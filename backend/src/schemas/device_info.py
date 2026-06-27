"""Schema for the device info modal: network details + identity per device.

Aggregates everything we can surface about a device (Sonos / Freebox / local
host / Bluetooth) so the UI can show IPv4/IPv6, MAC/hardware address, model and
reachability in a single dialog.
"""
from typing import List, Optional

from pydantic import BaseModel


class NetAddress(BaseModel):
    """One network address bound to an interface."""
    family: str  # "ipv4" | "ipv6" | "mac"
    address: str
    interface: Optional[str] = None


class DeviceInfo(BaseModel):
    """Detailed, normalized info for a single device."""
    device_id: Optional[int] = None
    name: str = ""
    type: Optional[str] = None
    uid: Optional[str] = None
    model: Optional[str] = None
    vendor: Optional[str] = None

    # Network
    hostname: Optional[str] = None
    ipv4: List[str] = []
    ipv6: List[str] = []
    mac: Optional[str] = None
    addresses: List[NetAddress] = []  # full per-interface breakdown (local host)

    # Reachability / playback
    online: bool = True
    standby: Optional[bool] = None
    volume: Optional[int] = None

    # How transport control is routed ("box_api" for Freebox, "direct" otherwise)
    control_channel: Optional[str] = None
    note: Optional[str] = None
