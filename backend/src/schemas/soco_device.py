from typing import Optional, List, Dict
from pydantic import BaseModel

class TrackInfo(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    album_art: Optional[str] = None
    position: Optional[str] = None
    playlist_position: Optional[str] = None
    duration: Optional[str] = None
    uri: Optional[str] = None
    metadata: Optional[str] = None

class SoCoDevice(BaseModel):
    name: str
    track_info: TrackInfo
    current_transport_state: Optional[str]
    ip_address: Optional[str]
    volume: Optional[int]
    uid: Optional[str]
    household_id: Optional[str]
    is_visible: Optional[bool]
    is_bridge: Optional[bool]
    is_coordinator: Optional[bool]
    is_soundbar: Optional[bool]
    is_satellite: Optional[bool]
    has_satellites: Optional[bool]
    sub_enabled: Optional[bool]
    sub_gain: Optional[int]
    is_subwoofer: Optional[bool]
    has_subwoofer: Optional[bool]
    channel: Optional[str]
    bass: Optional[int]
    treble: Optional[int]
    loudness: Optional[bool]
    balance: Optional[List[int]]
    audio_delay: Optional[int]
    night_mode: Optional[bool]
    dialog_mode: Optional[bool]
    surround_enabled: Optional[bool]
    surround_full_volume_enabled: Optional[bool]
    surround_volume_tv: Optional[int]
    surround_volume_music: Optional[int]
    supports_fixed_volume: Optional[bool]
    fixed_volume: Optional[bool]
    soundbar_audio_input_format: Optional[str]
    soundbar_audio_input_format_code: Optional[str]
    trueplay: Optional[str]
    status_light: Optional[bool]
    buttons_enabled: Optional[bool]
    voice_service_configured: Optional[bool]
    mic_enabled: Optional[bool]
