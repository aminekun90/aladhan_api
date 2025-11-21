import soco
from soco import SoCo, discover
from typing import List, Dict, Any
from fastapi.encoders import jsonable_encoder

from src.domain.models import Device
from src.schemas.log_config import LogConfig
logger = LogConfig.get_logger()

class SoCoService:
    def _serialize_device(self, device: SoCo) -> Dict[str, Any]:
        """Convert SoCo device object into a fully JSON-serializable dict."""
        def safe(value):
            if isinstance(value, tuple):
                return list(value)
            if isinstance(value, (bytes, bytearray)):
                return value.decode(errors="ignore")
            return value

        track_info = device.get_current_track_info() or {}
        transport_info = device.get_current_transport_info() or {}

        return {
            "name": device.player_name,
            "track_info": {k: safe(v) for k, v in track_info.items()},
            "current_transport_state": transport_info.get("current_transport_state", ""),
            "ip_address": safe(device.ip_address),
            "volume": safe(device.volume),
            "uid": safe(device.uid),
            "household_id": safe(device.household_id),
            "is_visible": safe(device.is_visible),
            "is_bridge": safe(device.is_bridge),
            "is_coordinator": safe(device.is_coordinator),
            "is_soundbar": safe(device.is_soundbar),
            "is_satellite": safe(device.is_satellite),
            "has_satellites": safe(device.has_satellites),
            "sub_enabled": safe(device.sub_enabled),
            "sub_gain": safe(device.sub_gain),
            "is_subwoofer": safe(device.is_subwoofer),
            "has_subwoofer": safe(device.has_subwoofer),
            "channel": safe(device.channel),
            "bass": safe(device.bass),
            "treble": safe(device.treble),
            "loudness": safe(device.loudness),
            "balance": safe(device.balance),
            "audio_delay": safe(device.audio_delay),
            "night_mode": safe(device.night_mode),
            "dialog_mode": safe(device.dialog_mode),
            "surround_enabled": safe(device.surround_enabled),
            "surround_full_volume_enabled": safe(device.surround_full_volume_enabled),
            "surround_volume_tv": safe(device.surround_volume_tv),
            "surround_volume_music": safe(device.surround_volume_music),
            "supports_fixed_volume": safe(device.supports_fixed_volume),
            "fixed_volume": safe(device.fixed_volume),
            "soundbar_audio_input_format": safe(device.soundbar_audio_input_format),
            "soundbar_audio_input_format_code": safe(device.soundbar_audio_input_format_code),
            "trueplay": safe(device.trueplay),
            "status_light": safe(device.status_light),
            "buttons_enabled": safe(device.buttons_enabled),
            "voice_service_configured": safe(device.voice_service_configured),
            "mic_enabled": safe(device.mic_enabled),
        }

    def get_soco(self) -> List[Dict[str, Any]] | None:
        """Discover Sonos devices and return serializable data."""
        devices = soco.discover() or discover()
        if not devices:
            return None
        devices = iter(devices) if isinstance(devices, set) else devices
        data = [self._serialize_device(device) for device in devices]
        return jsonable_encoder(data)  # ensures final serialization safety
    
    def from_list(self, devices: List[Dict[str, Any]] | None) -> List[Device]:
        if not devices:
            return []
        """Convert list of device dicts to list of Device domain models."""
        return [Device(id=None,ip=d["ip_address"], name=d["name"], raw_data=d, type="sonos_player") for d in devices] if devices else []

    def play_audio(self, device: Device, url: str,volume: int) -> None:
        soco_device = SoCo(device.ip)
        if not soco_device:
            logger.info(f"🔇 Device with ip {device.ip} not available in network")
            return
        soco_device.volume = volume
        soco_device.play_uri(url)