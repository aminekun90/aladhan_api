"""Minimal in-cluster Kubernetes client to force a redeploy of this app.

Used by the "force update" button: with the image on a mutable tag (`:latest`,
`pullPolicy: Always`), a rollout restart re-pulls the newest image. We patch the
Deployment's pod template `restartedAt` annotation — the same thing
`kubectl rollout restart` does — using the pod's own ServiceAccount.
"""

from datetime import datetime, timezone
from pathlib import Path

import requests

from src.services.env_service import EnvService

_SA_DIR = Path("/var/run/secrets/kubernetes.io/serviceaccount")
_TIMEOUT = 5


class NotInClusterError(RuntimeError):
    """Raised when there is no in-cluster ServiceAccount (e.g. local dev)."""


def is_in_cluster() -> bool:
    return (_SA_DIR / "token").exists()


def restart_self() -> str:
    """Trigger a rollout restart of this app's Deployment. Returns the new image tag note."""
    if not is_in_cluster():
        raise NotInClusterError("No in-cluster ServiceAccount — cannot trigger a restart.")

    namespace = (_SA_DIR / "namespace").read_text().strip()
    token = (_SA_DIR / "token").read_text().strip()
    deployment = EnvService.get("KUBE_DEPLOYMENT", "adhan-api")
    host = EnvService.get("KUBERNETES_SERVICE_HOST", "kubernetes.default.svc")
    port = EnvService.get("KUBERNETES_SERVICE_PORT", "443")

    url = f"https://{host}:{port}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}"
    now = datetime.now(timezone.utc).isoformat()
    patch = {"spec": {"template": {"metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": now}}}}}

    response = requests.patch(
        url,
        json=patch,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/strategic-merge-patch+json",
        },
        verify=str(_SA_DIR / "ca.crt"),
        timeout=_TIMEOUT,
    )
    response.raise_for_status()
    return now
