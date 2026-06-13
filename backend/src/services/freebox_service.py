import hashlib
import hmac
import json
import os
import socket
import time
from typing import Any, Dict, Optional

import requests
from zeroconf import ServiceBrowser, Zeroconf

from src.domain.models import Device
from src.schemas.exceptions import AuthException
from src.schemas.log_config import LogConfig

logger = LogConfig.get_logger()

FBX_MDNS_SERVICE = "_fbx-api._tcp.local."
DEFAULT_HOST = "mafreebox.freebox.fr"
PRIVATE_PREFIXES = ("192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.",
                    "172.2", "172.30.", "172.31.", "127.")


def discover_freebox_base_url(timeout: float = 3.0) -> Optional[str]:
    """Locate the Freebox on the LAN via mDNS (`_fbx-api._tcp`).

    Returns an ``http://<ip>`` base URL, or None if no Freebox responds. This
    is the reliable fix for environments where ``mafreebox.freebox.fr`` does
    not resolve (the box's own DNS isn't being used).
    """
    found: dict = {}

    class _Listener:
        def add_service(self, zc, service_type, name):
            info = zc.get_service_info(service_type, name, timeout=int(timeout * 1000))
            if info and info.addresses:
                found["ip"] = socket.inet_ntoa(info.addresses[0])

        def update_service(self, *args):
            pass

        def remove_service(self, *args):
            pass

    zc = Zeroconf()
    try:
        ServiceBrowser(zc, FBX_MDNS_SERVICE, _Listener())
        deadline = time.time() + timeout
        while time.time() < deadline and "ip" not in found:
            time.sleep(0.1)
    except Exception as exc:
        logger.warning(f"Freebox mDNS discovery failed: {exc}")
    finally:
        zc.close()

    if "ip" in found:
        logger.info(f"Freebox discovered via mDNS at {found['ip']}")
        return f"http://{found['ip']}"
    return None


class FreeboxService:
    def __init__(self, host=DEFAULT_HOST, app_id="pi.aladhan.remote", app_name="Aladhan Pi Remote", device_name="Raspberry Pi"):
        self.base_url = f"http://{host}"
        self.app_id = app_id
        self.app_name = app_name
        self.app_version = "1.0.0"
        self.device_name = device_name

        # Token persistence: map this folder in docker-compose (- ./data:/app/data).
        self.token_dir = "src/data"
        os.makedirs(self.token_dir, exist_ok=True)
        self.token_file = os.path.join(self.token_dir, "fbx_token.json")

        self.session = requests.Session()
        self.app_token = None
        self.session_token = None
        self.track_id = None

    # ------------------------------
    # Host discovery
    # ------------------------------
    def ensure_reachable(self) -> bool:
        """Make sure base_url points at a reachable Freebox.

        Tries the current host first; if it fails, falls back to mDNS discovery.
        """
        if self._probe(self.base_url):
            return True
        logger.warning(f"Freebox not reachable at {self.base_url}; trying mDNS discovery")
        discovered = discover_freebox_base_url()
        if discovered and self._probe(discovered):
            self.base_url = discovered
            return True
        logger.warning("Freebox could not be reached via hostname or mDNS")
        return False

    def _probe(self, base_url: str) -> bool:
        try:
            r = self.session.get(f"{base_url}/api_version", timeout=2)
            return r.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # ------------------------------
    # Token persistence
    # ------------------------------
    def _load_token(self) -> bool:
        """Load the app_token from disk to avoid re-registering on every restart."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file) as f:
                    self.app_token = json.load(f).get("app_token")
                return bool(self.app_token)
            except Exception as exc:
                logger.warning(f"Error loading Freebox token: {exc}")
        return False

    def _save_token(self, app_token: str) -> None:
        try:
            with open(self.token_file, "w") as f:
                json.dump({"app_token": app_token}, f)
            self.app_token = app_token
        except Exception as exc:
            logger.error(f"Error saving Freebox token: {exc}")

    def _delete_token(self) -> None:
        """Delete an invalid token to force a clean registration."""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        self.app_token = None

    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.session_token:
            headers["X-Fbx-App-Auth"] = self.session_token
        return headers

    # ------------------------------
    # Non-blocking pairing
    # ------------------------------
    def start_registration(self) -> Dict[str, Any]:
        """Begin pairing and return immediately with a track_id to poll.

        The user must press the RIGHT ARROW on the Freebox display. Poll
        ``registration_status(track_id)`` instead of blocking the request.
        """
        self.ensure_reachable()
        payload = {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "device_name": self.device_name,
            "permissions": {"player": True, "settings": True, "tv": True},
        }
        try:
            r = self.session.post(f"{self.base_url}/api/v8/login/authorize/", json=payload, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise AuthException(f"Failed to contact Freebox for registration: {exc}")

        result = r.json().get("result", {})
        self.app_token = result.get("app_token")
        self.track_id = result.get("track_id")
        logger.info("Freebox pairing started - press the RIGHT ARROW on the Freebox display to authorize")
        return {"track_id": self.track_id, "status": "pending"}

    def registration_status(self, track_id: Optional[int] = None) -> Dict[str, Any]:
        """Poll the pairing status: pending | granted | denied | timeout | unknown.

        On 'granted' the app_token is persisted to disk.
        """
        track = track_id or self.track_id
        if track is None:
            raise AuthException("No pairing in progress; call start_registration first")
        try:
            r = self.session.get(f"{self.base_url}/api/v8/login/authorize/{track}", timeout=10)
            status = r.json().get("result", {}).get("status", "unknown")
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Freebox pairing poll failed: {exc}")
            return {"track_id": track, "status": "pending"}

        if status == "granted" and self.app_token:
            self._save_token(self.app_token)
            logger.info("Freebox pairing granted - token saved")
        return {"track_id": track, "status": status}

    # ------------------------------
    # Session login
    # ------------------------------
    def login(self) -> None:
        """Challenge-response authentication; auto-recovers on invalid token."""
        self.ensure_reachable()
        if not self.app_token and not self._load_token():
            raise AuthException("No Freebox token found; complete pairing via start_registration first")

        try:
            r = self.session.get(f"{self.base_url}/api/v8/login/", timeout=10)
            r.raise_for_status()
        except Exception as exc:
            raise AuthException(f"Failed to connect to Freebox for login: {exc}")

        challenge = r.json().get("result", {}).get("challenge")
        if not self.app_token or not challenge:
            raise AuthException("Login failed: missing token or challenge")

        password = hmac.new(self.app_token.encode("utf-8"), challenge.encode("utf-8"), hashlib.sha1).hexdigest()
        r = self.session.post(f"{self.base_url}/api/v8/login/session/",
                              json={"app_id": self.app_id, "password": password}, timeout=10)

        if r.status_code == 403:
            logger.warning("Freebox token invalid (403); deleting and re-pairing required")
            self._delete_token()
            raise AuthException("Freebox token revoked; re-pairing required")

        r.raise_for_status()
        result = r.json()
        if result.get("success"):
            self.session_token = result.get("result", {}).get("session_token")
            logger.info("Freebox login successful")
        else:
            raise AuthException(f"Login failed: {result.get('msg')}")

    def _ensure_session(self) -> None:
        if not self.session_token:
            self.login()

    # ------------------------------
    # Players
    # ------------------------------
    def get_players(self) -> Optional[list]:
        self._ensure_session()
        url = f"{self.base_url}/api/v8/player"
        r = self.session.get(url, headers=self._get_headers())
        if r.status_code in (401, 403):
            self.login()
            r = self.session.get(url, headers=self._get_headers())
        r.raise_for_status()
        return r.json().get("result") or None

    def set_volume(self, player_id, volume) -> bool:
        return self._player_request(player_id, "put", "control/volume", {"volume": volume})

    def play_media(self, player_id, media_url, content_type="audio/mpeg", volume=15) -> bool:
        self._ensure_session()
        safe_vol = volume if isinstance(volume, int) and 0 <= volume <= 100 else 15
        self.set_volume(player_id, safe_vol)

        # Players reject HTTPS on local IPs (self-signed certs). Downgrade for any private host.
        final_url = media_url
        if media_url.startswith("https://") and any(p in media_url for p in PRIVATE_PREFIXES):
            logger.info("Downgrading HTTPS to HTTP for Freebox local playback")
            final_url = "http://" + media_url[len("https://"):]

        logger.info(f"Freebox play command: {final_url}")
        return self._player_request(player_id, "post", "control/open", {
            "url": final_url,
            "content_type": content_type,
            "metadata": {"title": "Aladhan Prayer", "type": "audio"},
        })

    def control(self, player_id, action: str) -> bool:
        """Send a transport command (play, pause, stop, next, prev) to a player."""
        command = "prev" if action == "previous" else action
        return self._player_request(player_id, "post", f"control/{command}")

    def mute(self, player_id, muted: bool) -> bool:
        return self._player_request(player_id, "put", "control/mute", {"mute": muted})

    def get_status(self, player_id) -> Dict[str, Any]:
        """Return the raw player status payload (foreground app, player state)."""
        self._ensure_session()
        url = f"{self.base_url}/api/v8/player/{player_id}/api/v6/player_status"
        r = self.session.get(url, headers=self._get_headers())
        if r.status_code in (401, 403):
            self.login()
            r = self.session.get(url, headers=self._get_headers())
        r.raise_for_status()
        return r.json().get("result", {}) or {}

    def _player_request(self, player_id, method: str, path: str, payload: dict | None = None) -> bool:
        """Issue an authenticated player control request, retrying once on auth expiry."""
        self._ensure_session()
        url = f"{self.base_url}/api/v8/player/{player_id}/api/v6/{path}"
        send = lambda: getattr(self.session, method)(url, json=payload, headers=self._get_headers())
        r = send()
        if r.status_code in (401, 403):
            self.login()
            r = send()
        r.raise_for_status()
        return r.json().get("success", False)

    def from_list(self, players: list[dict] | None) -> list[Device]:
        if not players:
            return []
        return [Device(id=None, ip=str(p["id"]), name=p["device_name"], raw_data=p, type="freebox_player") for p in players]
