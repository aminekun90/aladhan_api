from fastapi import APIRouter
from typing import List
from src.schemas.soco_device import SoCoDevice

from src.services.soco_service import SoCoService
from src.services.freebox_service import FreeboxService
from src.core.repository_factory import RepositoryContainer
from src.services.device_service import DeviceService
from src.domain.models import Device

from typing import Any, Dict


repos = RepositoryContainer()
soco_service = SoCoService()
freebox_service = FreeboxService()
device_service = DeviceService(repos.device_repo, repos.setting_repo)



router = APIRouter()
@router.get("/soco/devices", response_model=List[Dict[str, Any]], description="List all Sonos devices on the local network upserting them into the database")
def list_soco_devices():
    devices = soco_service.get_soco()
    freebox_devices = []
    try:
        freebox_service.login()
        freebox_devices = freebox_service.get_players()
        
    
        device_service.upsert_devices_bulk(freebox_service.from_list(freebox_devices))
    except Exception as e:
        print(f"Error fetching Freebox devices: {e}")
    
    device_service.upsert_devices_bulk(soco_service.from_list(devices))
    
    if not devices and not freebox_devices:
        return []
    
    if devices and freebox_devices:
        return devices + freebox_devices
    elif freebox_devices:
        return freebox_devices
    
    return devices
@router.get("freebox/auth", description="Authenticate with Freebox to access its devices")
def freebox_authenticate():
    try:
        freebox_service.login()
        return {"status": "success", "message": "Authenticated with Freebox successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
@router.get("/devices", response_model=List[Device], description="List all devices from the database")
def list_devices_db():
    devices = soco_service.get_soco()
    device_service.upsert_devices_bulk(soco_service.from_list(devices))
    return device_service.list_devices()

@router.get("/device/schedule/{device_id}", description="Schedule prayers for a specific device id")
def schedule_prayers(device_id: int)-> dict:
    device =device_service.get_device_by_id(device_id)
    if not device:
        return {"status": "error", "message": "Device not found"}
    return device_service.schedule_prayers_for_device(device=device)

@router.get("/devices/schedule", description="Schedule prayers for all devices")
def schedule_prayers_all()-> list[dict]:
    return device_service.schedule_prayers_for_all_devices()