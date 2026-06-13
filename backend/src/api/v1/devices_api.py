from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from src.core.repository_factory import RepositoryContainer
from src.domain.models import Device
from src.schemas.player import ControlResult, PlayerAction, PlayerState

# Import your services and models
from src.services.bluetooth_service import BluetoothService
from src.services.device_service import DeviceService
from src.services.freebox_service import FreeboxService
from src.services.soco_service import SoCoService

# Initialize Services
repos = RepositoryContainer()
soco_service = SoCoService()
freebox_service = FreeboxService()
bluetooth_service = BluetoothService()
device_service = DeviceService(repos.device_repo, repos.setting_repo)

router = APIRouter()

@router.post("/freebox/auth/start", description="Begin Freebox pairing (non-blocking). Returns a track_id to poll.")
def freebox_auth_start():
    """Start pairing, then press the RIGHT ARROW on the Freebox display.

    Returns immediately with a track_id; poll /freebox/auth/status to know when
    the user has authorized the app.
    """
    try:
        return freebox_service.start_registration()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to start pairing: {str(e)}")


@router.get("/freebox/auth/status", description="Poll Freebox pairing status: pending | granted | denied | timeout.")
def freebox_auth_status(track_id: int | None = None):
    try:
        return freebox_service.registration_status(track_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/freebox/auth", description="Verify Freebox session (logs in with the saved token).")
def freebox_authenticate():
    """Open a session using the token saved during pairing."""
    try:
        freebox_service.login()
        return {"status": "success", "message": "Authenticated with Freebox successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/soco/devices", response_model=List[Dict[str, Any]], description="List all devices (Sonos + Freebox) and upsert them into the DB")
def list_soco_devices():
    """
    Scans for both Sonos and Freebox devices.
    If Freebox is not authenticated yet, it will skip it (check logs) instead of crashing.
    """
    # 1. Get Sonos Devices (returns list of dicts)
    devices = soco_service.get_soco()
    
    # 2. Get Freebox Devices (Safely)
    freebox_devices_objs = []
    try:
        # Only try to get players if we have a token or can login silently.
        # We assume explicit auth is done via /freebox/auth first to avoid hanging this request.
        if freebox_service._load_token(): 
            freebox_service.login()
            players = freebox_service.get_players()
            if players:
                # Returns list of Device objects
                freebox_devices_objs = freebox_service.from_list(players)
            else:
                print("Warning: No Freebox players found.")
        else:
            print("Warning: Freebox token not found. Skipping Freebox device scan.")
    except Exception as e:
        print(f"Warning: Could not fetch Freebox devices (Auth required?): {e}")

    # 3. Save to Database
    all_devices_to_save = []
    
    if devices:
        soco_converted = soco_service.from_list(devices)
        all_devices_to_save.extend(soco_converted)
        
    if freebox_devices_objs:
        all_devices_to_save.extend(freebox_devices_objs)
    
    if all_devices_to_save:
        device_service.upsert_devices_bulk(all_devices_to_save)

    # 4. Return combined list for the API response
    # 'devices' is already a list of dicts (from soco)
    combined_list = devices if devices else []
    # Append Freebox devices as dicts
    return combined_list + freebox_devices_objs

@router.post("/freebox/device/{device_id}/volume/{volume}", description="Set volume for a Freebox device")
def set_freebox_device_volume(device_id: str, volume: int):
    try:
        # Ensure device_id is handled as int for Freebox API
        success = freebox_service.set_volume(int(device_id), volume)
        if success:
            return {"status": "success", "message": f"Volume set to {volume} for device {device_id}"}
        else:
            raise HTTPException(status_code=500, detail="Freebox returned failure status")
    except ValueError:
         raise HTTPException(status_code=400, detail="Device ID must be an integer for Freebox")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/freebox/device/{device_id}/play", description="Play media on a Freebox device")
def play_media_on_freebox_device(device_id: str, media_url: str, volume: int = 15):
    try:
        # The service now handles HTTPS->HTTP conversion automatically
        success = freebox_service.play_media(int(device_id), media_url, volume=volume)
        if success:
            return {"status": "success", "message": f"Playing media on device {device_id}"}
        else:
            raise HTTPException(status_code=500, detail="Freebox returned failure (Check if Player is ON)")
    except ValueError:
         raise HTTPException(status_code=400, detail="Device ID must be an integer for Freebox")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices", response_model=List[Device], description="List all devices stored in the database")
def list_devices_db():
    # This just reads from DB, no scanning
    return device_service.list_devices()

@router.get("/device/schedule/{device_id}", description="Schedule prayers for a specific device id")
def schedule_prayers(device_id: int) -> dict:
    device = device_service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device_service.schedule_prayers_for_device(device=device)

@router.get("/devices/schedule", description="Schedule prayers for all devices")
def schedule_prayers_all() -> list[dict]:
    return device_service.schedule_prayers_for_all_devices()

@router.post("/device/play/{device_id}", description="Play the audio for a specific device id")
def play_prayer(device_id: int) -> dict:
    device = device_service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device_service.play_audio_in_device(device_id= device_id)


# ------------------------------
# Unified transport controls (Sonos + Freebox)
# ------------------------------
@router.post("/device/{device_id}/control/{action}", response_model=ControlResult,
             description="Transport control: play | pause | stop | next | previous | mute | unmute")
def control_device(device_id: int, action: PlayerAction) -> ControlResult:
    result = device_service.control_device(device_id, action)
    if result.status == "error" and result.message == "Device not found":
        raise HTTPException(status_code=404, detail=result.message)
    return result


@router.post("/device/{device_id}/volume/{volume}", response_model=ControlResult,
             description="Set volume (0-100) for a device, regardless of backend")
def set_device_volume(device_id: int, volume: int) -> ControlResult:
    result = device_service.set_device_volume(device_id, volume)
    if result.status == "error" and result.message == "Device not found":
        raise HTTPException(status_code=404, detail=result.message)
    return result


@router.get("/device/{device_id}/state", response_model=PlayerState,
            description="Current normalized playback state of a device")
def get_device_state(device_id: int) -> PlayerState:
    state = device_service.get_device_state(device_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return state


# ------------------------------
# Bluetooth (BlueZ — Linux/Raspberry Pi)
# ------------------------------
@router.get("/bluetooth/status", description="Bluetooth capability of the host (Linux/BlueZ required)")
def bluetooth_status() -> Dict[str, Any]:
    return bluetooth_service.status()


@router.get("/bluetooth/scan", response_model=List[Device],
            description="Scan for nearby Bluetooth speakers and persist them")
def bluetooth_scan(timeout: int = 8) -> List[Device]:
    devices = bluetooth_service.scan(timeout=timeout)
    if devices:
        device_service.upsert_devices_bulk(devices)
    return devices


@router.post("/bluetooth/{mac}/pair", description="Pair and trust a Bluetooth speaker")
def bluetooth_pair(mac: str) -> dict:
    ok = bluetooth_service.pair(mac)
    return {"status": "success" if ok else "error", "mac": mac}


@router.post("/bluetooth/{mac}/connect", description="Connect a paired Bluetooth speaker")
def bluetooth_connect(mac: str) -> dict:
    ok = bluetooth_service.connect(mac)
    return {"status": "success" if ok else "error", "mac": mac}


@router.post("/bluetooth/{mac}/disconnect", description="Disconnect a Bluetooth speaker")
def bluetooth_disconnect(mac: str) -> dict:
    ok = bluetooth_service.disconnect(mac)
    return {"status": "success" if ok else "error", "mac": mac}