"""Local (virtual) player — plays the adhan on the host running the app.

This is the always-available fallback device: when no Sonos/Freebox/Bluetooth
speaker is found, the adhan still plays through the machine's own default audio
output. It shells out to whatever audio player is present (afplay on macOS,
mpg123/ffplay/paplay/aplay on Linux).
"""
import platform
import shutil
import subprocess
from typing import List, Optional

from src.schemas.log_config import LogConfig

logger = LogConfig.get_logger()

# Player binaries tried in order, per platform.
_PLAYERS_DARWIN = ("afplay",)
_PLAYERS_LINUX = ("mpg123", "ffplay", "cvlc", "paplay", "aplay")


class LocalPlayerService:
    def __init__(self):
        candidates = _PLAYERS_DARWIN if platform.system() == "Darwin" else _PLAYERS_LINUX
        self._player = next((p for p in candidates if shutil.which(p)), None)

    def available(self) -> bool:
        return self._player is not None

    def play_file(self, file_path: str) -> bool:
        """Play a local audio file on the host's default output (non-blocking)."""
        if not self._player:
            logger.error("No local audio player found (need afplay / mpg123 / ffplay / paplay / aplay)")
            return False
        try:
            subprocess.Popen(self._command(file_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Local playback started via {self._player}: {file_path}")
            return True
        except Exception as exc:
            logger.error(f"Local playback failed: {exc}")
            return False

    def _command(self, file_path: str) -> List[str]:
        if self._player == "ffplay":
            return ["ffplay", "-nodisp", "-autoexit", file_path]
        if self._player == "cvlc":
            return ["cvlc", "--play-and-exit", file_path]
        return [self._player, file_path]

    @property
    def player(self) -> Optional[str]:
        return self._player
