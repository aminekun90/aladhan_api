import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services import k8s_service, keel_service

router = APIRouter()


class UpdateStatus(BaseModel):
    pending: bool
    currentVersion: str = ""
    newVersion: str = ""
    votesReceived: int = 0
    votesRequired: int = 1


class ApproveResult(BaseModel):
    approved: bool
    newVersion: str = ""


class ForceResult(BaseModel):
    restarted: bool
    detail: str = ""


@router.get("/update/status", response_model=UpdateStatus)
def update_status():
    """Whether a new image is waiting for approval (via Keel)."""
    try:
        update = keel_service.get_pending_update()
    except requests.RequestException:
        # Keel unreachable / not deployed — treat as "nothing pending".
        return UpdateStatus(pending=False)
    if not update:
        return UpdateStatus(pending=False)
    return UpdateStatus(pending=True, **{k: update[k] for k in ("currentVersion", "newVersion", "votesReceived", "votesRequired")})


@router.post("/update/approve", response_model=ApproveResult)
def update_approve():
    """Approve the pending update so Keel rolls it out."""
    try:
        update = keel_service.get_pending_update()
        if not update:
            return ApproveResult(approved=False)
        keel_service.approve_update(update["identifier"])
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Keel unreachable: {exc}") from exc
    return ApproveResult(approved=True, newVersion=update["newVersion"])


@router.post("/update/force", response_model=ForceResult)
def update_force():
    """Force a rollout restart so the app re-pulls the latest image."""
    try:
        k8s_service.restart_self()
    except k8s_service.NotInClusterError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Kubernetes API error: {exc}") from exc
    return ForceResult(restarted=True, detail="Rollout restarted — pulling the latest image.")
