"""Bluetooth A2DP speaker support via BlueZ (Linux / Raspberry Pi).

Unlike Sonos/Freebox (network players that fetch a URL), Bluetooth speakers are
controlled at the OS level: pair/connect through BlueZ, then play audio to the
host's default sink. This service shells out to `bluetoothctl` and a local audio
player. It degrades gracefully (returns unavailable) on non-Linux hosts or when
the required binaries are missing, so the rest of the API keeps working.
"""
import platform
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from src.domain.models import Device
from src.schemas.log_config import LogConfig

logger = LogConfig.get_logger()

# bluetoothctl line: "Device AA:BB:CC:DD:EE:FF Speaker Name"
_DEVICE_LINE = re.compile(r"Device\s+([0-9A-Fa-f:]{17})\s+(.+)")
# Players tried in order; first one found is used.
_PLAYERS = ("mpg123", "ffplay", "cvlc", "paplay", "aplay")


class BluetoothService:
    def __init__(self):
        self._player = next((p for p in _PLAYERS if shutil.which(p)), None)

    # ------------------------------
    # Capability detection
    # ------------------------------
    def available(self) -> bool:
        """True only on Linux with bluetoothctl present."""
        return platform.system() == "Linux" and shutil.which("bluetoothctl") is not None

    def status(self) -> Dict[str, Any]:
        return {
            "available": self.available(),
            "platform": platform.system(),
            "bluetoothctl": shutil.which("bluetoothctl") is not None,
            "player": self._player,
        }

    # ------------------------------
    # Discovery & pairing
    # ------------------------------
    def scan(self, timeout: int = 8) -> List[Device]:
        """Scan for nearby Bluetooth devices and return them as domain Devices."""
        if not self.available():
            logger.warning("Bluetooth scan requested on a host without BlueZ; returning empty")
            return []
        # Run a timed discovery, then read the known-devices list.
        self._ctl(["--timeout", str(timeout), "scan", "on"], timeout=timeout + 5)
        out = self._ctl(["devices"])
        return self._parse_devices(out)

    def pair(self, mac: str) -> bool:
        return self._connect_step(mac, "pair") and self._connect_step(mac, "trust")

    def connect(self, mac: str) -> bool:
        return self._connect_step(mac, "connect")

    def disconnect(self, mac: str) -> bool:
        return self._connect_step(mac, "disconnect")

    def is_connected(self, mac: str) -> bool:
        info = self._ctl(["info", mac])
        return "Connected: yes" in info

    # ------------------------------
    # Playback
    # ------------------------------
    def play_file(self, file_path: str, mac: Optional[str] = None) -> bool:
        """Play a local audio file to the default sink (the connected speaker).

        If `mac` is given and not connected, attempt to connect first.
        """
        if not self.available():
            logger.warning("Bluetooth playback requested without BlueZ; skipping")
            return False
        if not self._player:
            logger.error(f"No audio player found (need one of {_PLAYERS})")
            return False
        if mac and not self.is_connected(mac):
            self.connect(mac)

        cmd = self._play_command(file_path)
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Bluetooth playback started: {' '.join(cmd)}")
            return True
        except Exception as exc:
            logger.error(f"Bluetooth playback failed: {exc}")
            return False

    def from_list(self, devices: List[Device]) -> List[Device]:
        """Identity helper for API symmetry with the other services."""
        return devices or []

    # ------------------------------
    # Internals
    # ------------------------------
    def _play_command(self, file_path: str) -> List[str]:
        if self._player == "ffplay":
            return ["ffplay", "-nodisp", "-autoexit", file_path]
        if self._player == "cvlc":
            return ["cvlc", "--play-and-exit", file_path]
        return [self._player, file_path]

    def _connect_step(self, mac: str, action: str) -> bool:
        if not self.available():
            return False
        out = self._ctl([action, mac], timeout=20)
        ok = "successful" in out.lower() or "changing" in out.lower()
        if not ok:
            logger.warning(f"Bluetooth {action} {mac} did not confirm success: {out.strip()[:120]}")
        return ok

    def _parse_devices(self, output: str) -> List[Device]:
        devices = []
        for line in output.splitlines():
            match = _DEVICE_LINE.search(line)
            if match:
                mac, name = match.group(1), match.group(2).strip()
                devices.append(Device(id=None, ip=mac, name=name,
                                      raw_data={"mac": mac}, type="bluetooth_speaker"))
        return devices

    def _ctl(self, args: List[str], timeout: int = 15) -> str:
        try:
            result = subprocess.run(["bluetoothctl", *args], capture_output=True,
                                    text=True, timeout=timeout, check=False)
            return result.stdout + result.stderr
        except Exception as exc:
            logger.warning(f"bluetoothctl {' '.join(args)} failed: {exc}")
            return ""
