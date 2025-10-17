from fastapi import APIRouter
from typing import List
from src.schemas.soco_device import SoCoDevice

from src.services.soco_service import SoCoService
from src.core.repository_factory import RepositoryContainer
from src.services.device_service import DeviceService
from src.domain.models import Device

repos = RepositoryContainer()
soco_service = SoCoService()
device_service = DeviceService(repos.device_repo, repos.setting_repo)



router = APIRouter()
@router.get("/soco/devices", response_model=List[SoCoDevice], description="List all Sonos devices on the local network upserting them into the database")
def list_soco_devices():
    devices = soco_service.get_soco()
    device_service.upsert_devices_bulk(soco_service.from_list(devices))
    if not devices:
        return []
    return devices

@router.get("/devices", response_model=List[Device], description="List all devices from the database")
def list_devices_db():
    devices = soco_service.get_soco()
    device_service.upsert_devices_bulk(soco_service.from_list(devices))
    return device_service.list_devices()

@router.get("/device/{device_id}", description="Schedule prayers for a specific device id")
def schedule_prayers(device_id: int)-> dict:
    device =device_service.get_device_by_id(device_id)
    if not device:
        return {"status": "error", "message": "Device not found"}
    return device_service.schedule_prayers_for_device(device=device)

@router.get("/devices/schedule", description="Schedule prayers for all devices")
def schedule_prayers_all()-> list[dict]:
    return device_service.schedule_prayers_for_all_devices()