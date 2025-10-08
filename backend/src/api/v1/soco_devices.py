from fastapi import APIRouter
from typing import List
from src.schemas.soco_device import SoCoDevice

from src.services.soco_service import SoCoService

soco_service = SoCoService()
router = APIRouter(
    prefix="/soco",
    tags=["soco_devices"]
)
@router.get("/devices", response_model=List[SoCoDevice])
def list_soco_devices():
    devices = soco_service.get_soco()
    if not devices:
        return []
    return devices

