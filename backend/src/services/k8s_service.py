"""In-cluster Kubernetes client to force this app onto the newest image.

Used by the "force update" button. `imagePullPolicy: Always` + a rollout restart
does NOT reliably re-pull a moving `:latest` tag on k3s/containerd (the local
`:latest` digest is reused). So instead we resolve the current `:latest` digest
from the registry and patch the Deployment to `repo@sha256:<digest>` — the image
ref changes, so the kubelet pulls the new image and rolls out. Same trick Keel
uses. Argo CD ignores this image field (see the adhan Application).
"""

import platform
from pathlib import Path

import requests

from src.services.env_service import EnvService

_SA_DIR = Path("/var/run/secrets/kubernetes.io/serviceaccount")
_TIMEOUT = 8


class NotInClusterError(RuntimeError):
    """Raised when there is no in-cluster ServiceAccount (e.g. local dev)."""


def is_in_cluster() -> bool:
    return (_SA_DIR / "token").exists()


def _node_arch() -> str:
    machine = platform.machine().lower()
    return {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64", "amd64": "amd64"}.get(machine, "amd64")


def _latest_digest(repo: str) -> str:
    """Resolve the current :latest image digest for this node's architecture."""
    response = requests.get(f"https://hub.docker.com/v2/repositories/{repo}/tags/latest", timeout=_TIMEOUT)
    response.raise_for_status()
    arch = _node_arch()
    for image in response.json().get("images", []):
        if image.get("architecture") == arch and image.get("digest"):
            return image["digest"]
    raise RuntimeError(f"No {arch} image found for {repo}:latest")


def _k8s(method: str, path: str, json: dict | None = None, content_type: str | None = None) -> requests.Response:
    namespace = (_SA_DIR / "namespace").read_text().strip()
    token = (_SA_DIR / "token").read_text().strip()
    host = EnvService.get("KUBERNETES_SERVICE_HOST", "kubernetes.default.svc")
    port = EnvService.get("KUBERNETES_SERVICE_PORT", "443")
    headers = {"Authorization": f"Bearer {token}"}
    if content_type:
        headers["Content-Type"] = content_type
    url = f"https://{host}:{port}/apis/apps/v1/namespaces/{namespace}{path}"
    response = requests.request(method, url, json=json, headers=headers, verify=str(_SA_DIR / "ca.crt"), timeout=_TIMEOUT)
    response.raise_for_status()
    return response


def force_pull_latest() -> dict:
    """Pin the Deployment to the current :latest digest so the kubelet pulls it.

    Returns {"updated": bool, "image": str} — updated is False if already current.
    """
    if not is_in_cluster():
        raise NotInClusterError("No in-cluster ServiceAccount — cannot trigger an update.")

    deployment = EnvService.get("KUBE_DEPLOYMENT", "adhan-api")
    container = EnvService.get("KUBE_CONTAINER", "adhan-api")
    repo = EnvService.get("KUBE_IMAGE_REPO", "aminekun90/adhan-api")

    digest = _latest_digest(repo)
    target = f"{repo}@{digest}"

    current = _k8s("GET", f"/deployments/{deployment}").json()
    running = current["spec"]["template"]["spec"]["containers"][0].get("image", "")
    if running == target:
        return {"updated": False, "image": target}

    patch = {"spec": {"template": {"spec": {"containers": [{"name": container, "image": target}]}}}}
    _k8s("PATCH", f"/deployments/{deployment}", json=patch,
         content_type="application/strategic-merge-patch+json")
    return {"updated": True, "image": target}
