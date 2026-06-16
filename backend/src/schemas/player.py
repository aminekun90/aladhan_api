"""Shared types for cross-backend player transport control (Sonos / Freebox / BT)."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PlayerAction(str, Enum):
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"
    MUTE = "mute"
    UNMUTE = "unmute"


class PlayerState(BaseModel):
    """Normalized playback state, returned by every device backend."""
    device_id: Optional[int] = None
    name: str = ""
    ip: str = ""
    type: Optional[str] = None
    transport_state: str = "UNKNOWN"  # PLAYING | PAUSED_PLAYBACK | STOPPED | UNKNOWN
    volume: Optional[int] = None
    muted: Optional[bool] = None
    track_title: Optional[str] = None
    online: bool = True


class ControlResult(BaseModel):
    status: str
    message: str
    state: Optional[PlayerState] = None
