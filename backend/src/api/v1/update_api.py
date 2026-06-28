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
    updated: bool
    detail: str = ""


@router.get("/update/status", response_model=UpdateStatus)
def update_status():
    """Whether a new version is available — via a Keel approval or a newer image."""
    # 1) Keel pending approval (only if Keel is installed).
    try:
        update = keel_service.get_pending_update()
        if update:
            return UpdateStatus(pending=True, **{k: update[k] for k in ("currentVersion", "newVersion", "votesReceived", "votesRequired")})
    except requests.RequestException:
        pass

    # 2) Registry check: is a newer :latest image available than the one we run?
    try:
        check = k8s_service.check_update_available()
        if check["available"]:
            return UpdateStatus(pending=True, newVersion=check["newVersion"])
    except (requests.RequestException, k8s_service.NotInClusterError, KeyError):
        pass

    return UpdateStatus(pending=False)


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
    """Pin the Deployment to the current :latest digest so the app pulls it."""
    try:
        result = k8s_service.force_pull_latest()
    except k8s_service.NotInClusterError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Update failed: {exc}") from exc
    if not result["updated"]:
        return ForceResult(updated=False, detail="Already on the latest image.")
    return ForceResult(updated=True, detail="Pulling the latest image and restarting.")
