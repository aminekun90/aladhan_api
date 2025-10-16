from fastapi import APIRouter
from typing import List
from src.schemas.soco_device import SoCoDevice

from src.services.soco_service import SoCoService
from src.core.repository_factory import RepositoryContainer
from src.domain import DeviceRepository
from src.domain.models import Device

soco_service = SoCoService()
repos = RepositoryContainer()

device_repo: DeviceRepository = repos.device_repo

router = APIRouter()
@router.get("/soco/devices", response_model=List[SoCoDevice], description="List all Sonos devices on the local network upserting them into the database")
def list_soco_devices():
    devices = soco_service.get_soco()
    device_repo.upsert_devices_bulk(soco_service.from_list(devices))
    if not devices:
        return []
    return devices

@router.get("/devices", response_model=List[Device], description="List all devices from the database")
def list_devices_db():
    devices = soco_service.get_soco()
    device_repo.upsert_devices_bulk(soco_service.from_list(devices))
    return device_repo.list_devices()

