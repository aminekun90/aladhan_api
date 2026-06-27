"""Thin client over the Keel admin API used to surface and approve OTA updates.

Keel (https://keel.sh) watches the cluster and, when ``keel.sh/approvals`` is
set, holds a new image in a *pending approval* instead of deploying it. This
service lets the Adhan app show that pending update and approve it from its own
UI — the browser never talks to Keel directly, the backend proxies it.
"""

import requests

from src.services.env_service import EnvService

VOTER = "adhan-app"
_TIMEOUT = 5


def _base_url() -> str:
    return EnvService.get("KEEL_URL", "http://keel.keel.svc.cluster.local:9300").rstrip("/")


def _auth() -> tuple[str, str] | None:
    user = EnvService.get("KEEL_USER", "")
    password = EnvService.get("KEEL_PASSWORD", "")
    return (user, password) if user else None


def _resource_name() -> str:
    return EnvService.get("KEEL_RESOURCE", "adhan-api")


def _list_approvals() -> list[dict]:
    response = requests.get(f"{_base_url()}/v1/approvals", auth=_auth(), timeout=_TIMEOUT)
    response.raise_for_status()
    return response.json() or []


def _is_pending(approval: dict) -> bool:
    return (
        not approval.get("archived")
        and not approval.get("rejected")
        and approval.get("votesReceived", 0) < approval.get("votesRequired", 1)
    )


def get_pending_update() -> dict | None:
    """Return the pending approval targeting our resource, or None."""
    resource = _resource_name()
    for approval in _list_approvals():
        if resource in approval.get("identifier", "") and _is_pending(approval):
            return {
                "identifier": approval["identifier"],
                "currentVersion": approval.get("currentVersion", ""),
                "newVersion": approval.get("newVersion", ""),
                "votesReceived": approval.get("votesReceived", 0),
                "votesRequired": approval.get("votesRequired", 1),
                "deadline": approval.get("deadline", ""),
                "message": approval.get("message", ""),
            }
    return None


def approve_update(identifier: str) -> None:
    """Cast an approval vote for the given Keel approval identifier."""
    response = requests.post(
        f"{_base_url()}/v1/approvals",
        json={"identifier": identifier, "action": "approve", "voter": VOTER},
        auth=_auth(),
        timeout=_TIMEOUT,
    )
    response.raise_for_status()
