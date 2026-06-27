import hashlib
import hmac
import json
import os
import socket
import time
from typing import Any, Dict, Optional
from urllib.parse import quote

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

        # Box API version, discovered from /api_version (don't hardcode v8 —
        # it changes across Freebox OS releases). Defaults are a safe fallback.
        self.api_base = "/api/"
        self.api_major = "8"
        # Per-player embedded API version (the inner /api/v6/ path), cached from
        # the player list, and player_id -> device_name for the AirMedia fallback.
        self._player_api_major: Dict[str, str] = {}
        self._player_names: Dict[str, str] = {}

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
            if r.status_code != 200:
                return False
            data = r.json()
            # e.g. api_base_url="/api/", api_version="8.0" -> /api/v8/
            self.api_base = data.get("api_base_url", self.api_base)
            self.api_major = str(data.get("api_version", f"{self.api_major}.0")).split(".")[0]
            return True
        except requests.exceptions.RequestException:
            return False

    # ------------------------------
    # URL builders (version-aware)
    # ------------------------------
    def _box_url(self, path: str) -> str:
        """Build a box API URL from the discovered api_base_url + major version."""
        base = self.api_base if self.api_base.endswith("/") else self.api_base + "/"
        return f"{self.base_url}{base}v{self.api_major}/{path.lstrip('/')}"

    def _player_url(self, player_id, path: str) -> str:
        """Build a player media-API URL using the player's own embedded version."""
        major = self._player_api_major.get(str(player_id), "6")
        return self._box_url(f"player/{player_id}/api/v{major}/{path.lstrip('/')}")

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
            r = self.session.post(self._box_url("login/authorize/"), json=payload, timeout=10)
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
            r = self.session.get(self._box_url(f"login/authorize/{track}"), timeout=10)
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
            r = self.session.get(self._box_url("login/"), timeout=10)
            r.raise_for_status()
        except Exception as exc:
            raise AuthException(f"Failed to connect to Freebox for login: {exc}")

        challenge = r.json().get("result", {}).get("challenge")
        if not self.app_token or not challenge:
            raise AuthException("Login failed: missing token or challenge")

        password = hmac.new(self.app_token.encode("utf-8"), challenge.encode("utf-8"), hashlib.sha1).hexdigest()
        r = self.session.post(self._box_url("login/session/"),
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
        url = self._box_url("player")
        r = self.session.get(url, headers=self._get_headers())
        if r.status_code in (401, 403):
            self.login()
            r = self.session.get(url, headers=self._get_headers())
        r.raise_for_status()
        players = r.json().get("result") or None
        # Cache each player's embedded API version and display name (used by the
        # version-aware URL builder and the AirMedia fallback).
        for p in players or []:
            pid = str(p.get("id"))
            if "api_version" in p:
                self._player_api_major[pid] = str(p["api_version"]).split(".")[0]
            if p.get("device_name"):
                self._player_names[pid] = p["device_name"]
        return players

    def set_volume(self, player_id, volume) -> bool:
        return self._player_request(player_id, "put", "control/volume", {"volume": volume})

    def play_media(self, player_id, media_url, content_type="audio/mpeg", volume=15) -> bool:
        """Play a media on a Freebox Player, falling back to AirMedia on failure.

        Primary path is the Player media API (control/open). If the player is
        unreachable or rejects the command (e.g. the Player app isn't in the
        foreground), we push the same URL via AirMedia instead.
        """
        self._ensure_session()
        safe_vol = volume if isinstance(volume, int) and 0 <= volume <= 100 else 15
        final_url = self._downgrade_local_https(media_url)

        try:
            self.set_volume(player_id, safe_vol)
            logger.info(f"Freebox player play: {final_url}")
            if self._player_request(player_id, "post", "control/open", {
                "url": final_url,
                "content_type": content_type,
                "metadata": {"title": "Aladhan Prayer", "type": "audio"},
            }):
                return True
            logger.warning("Freebox player control/open returned no success; trying AirMedia")
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Freebox player play failed ({exc}); trying AirMedia")

        receiver = self._receiver_name_for(player_id)
        if receiver:
            return self.play_airmedia(receiver, final_url)
        logger.error("Freebox playback failed and no AirMedia receiver resolved")
        return False

    def _downgrade_local_https(self, media_url: str) -> str:
        """Players reject HTTPS on local IPs (self-signed certs) — use HTTP there."""
        if media_url.startswith("https://") and any(p in media_url for p in PRIVATE_PREFIXES):
            logger.info("Downgrading HTTPS to HTTP for Freebox local playback")
            return "http://" + media_url[len("https://"):]
        return media_url

    def _receiver_name_for(self, player_id) -> Optional[str]:
        """Resolve the AirMedia receiver name (= player device_name) for a player."""
        name = self._player_names.get(str(player_id))
        if name:
            return name
        try:
            self.get_players()  # populate the cache if play came before listing
        except requests.exceptions.RequestException:
            return None
        return self._player_names.get(str(player_id))

    # ------------------------------
    # AirMedia (AirPlay-like push)
    # ------------------------------
    def get_lan_host(self, mac: Optional[str]) -> Dict[str, Any]:
        """Best-effort LAN lookup of a host by MAC via the Freebox LAN browser.

        Returns {"ipv4": [...], "ipv6": [...], "hostname": str|None, "reachable": bool|None}.
        Used only to enrich the device-info modal; never required for control.
        """
        empty: Dict[str, Any] = {"ipv4": [], "ipv6": [], "hostname": None, "reachable": None}
        if not mac:
            return empty
        try:
            self._ensure_session()
            url = self._box_url("lan/browser/pub/")
            r = self.session.get(url, headers=self._get_headers(), timeout=8)
            if r.status_code in (401, 403):
                self.login()
                r = self.session.get(url, headers=self._get_headers(), timeout=8)
            r.raise_for_status()
            hosts = r.json().get("result") or []
        except Exception as e:
            logger.warning(f"Freebox LAN browse failed: {e}")
            return empty

        target = mac.lower()
        for host in hosts:
            l2 = (host.get("l2ident") or {}).get("id", "")
            if str(l2).lower() != target:
                continue
            ipv4, ipv6 = [], []
            for c in host.get("l3connectivities") or []:
                if not c.get("active", False):
                    continue
                af, addr = c.get("af"), c.get("addr")
                if af == "ipv4" and addr:
                    ipv4.append(addr)
                elif af == "ipv6" and addr:
                    ipv6.append(addr)
            return {
                "ipv4": ipv4,
                "ipv6": ipv6,
                "hostname": host.get("primary_name") or None,
                "reachable": bool(host.get("active", False)),
            }
        return empty

    def get_airmedia_receivers(self) -> list:
        """List AirMedia receivers (name, password_protected, capabilities)."""
        self._ensure_session()
        url = self._box_url("airmedia/receivers/")
        r = self.session.get(url, headers=self._get_headers())
        if r.status_code in (401, 403):
            self.login()
            r = self.session.get(url, headers=self._get_headers())
        r.raise_for_status()
        return r.json().get("result") or []

    def play_airmedia(self, receiver_name: str, media_url: str, password: Optional[str] = None) -> bool:
        """Push a media to an AirMedia receiver. AirMedia exposes only photo/video
        media types, so audio streams are sent as 'video'."""
        logger.info(f"Freebox AirMedia play on '{receiver_name}': {media_url}")
        return self._airmedia(receiver_name, "start",
                              media_url=self._downgrade_local_https(media_url), password=password)

    def stop_airmedia(self, receiver_name: str, password: Optional[str] = None) -> bool:
        return self._airmedia(receiver_name, "stop", password=password)

    def _airmedia(self, receiver_name: str, action: str, media_url: Optional[str] = None,
                  password: Optional[str] = None, media_type: str = "video") -> bool:
        self._ensure_session()
        payload: Dict[str, Any] = {"action": action, "media_type": media_type}
        if media_url:
            payload["media"] = media_url
        if password:
            payload["password"] = password
        url = self._box_url(f"airmedia/receivers/{quote(receiver_name, safe='')}/")
        send = lambda: self.session.post(url, json=payload, headers=self._get_headers())
        r = send()
        if r.status_code in (401, 403):
            self.login()
            r = send()
        r.raise_for_status()
        return r.json().get("success", False)

    def control(self, player_id, action: str) -> bool:
        """Send a transport command (play, pause, stop, next, prev) to a player."""
        command = "prev" if action == "previous" else action
        return self._player_request(player_id, "post", f"control/{command}")

    def mute(self, player_id, muted: bool) -> bool:
        return self._player_request(player_id, "put", "control/mute", {"mute": muted})

    def get_status(self, player_id) -> Dict[str, Any]:
        """Return the raw player status payload (foreground app, player state)."""
        self._ensure_session()
        url = self._player_url(player_id, "player_status")
        r = self.session.get(url, headers=self._get_headers())
        if r.status_code in (401, 403):
            self.login()
            r = self.session.get(url, headers=self._get_headers())
        r.raise_for_status()
        return r.json().get("result", {}) or {}

    def _player_request(self, player_id, method: str, path: str, payload: dict | None = None) -> bool:
        """Issue an authenticated player control request, retrying once on auth expiry."""
        self._ensure_session()
        url = self._player_url(player_id, path)
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
        # device.ip holds the player id: control/playback are routed through the
        # box API (/player/<id>/...), never the player's LAN IP — so a player IP
        # change has no effect. uid keys on the player's MAC (physically attached
        # to the hardware) when present, falling back to the box-assigned id.
        return [Device(id=None, ip=str(p["id"]), uid=self._player_uid(p),
                       name=p["device_name"], raw_data=p, type="freebox_player") for p in players]

    @staticmethod
    def _player_uid(player: dict) -> str:
        mac = player.get("mac")
        return f"freebox-player-mac-{mac.lower()}" if mac else f"freebox-player-{player['id']}"

    def airmedia_from_list(self, receivers: list[dict] | None) -> list[Device]:
        """Map AirMedia receivers to Device objects (identified by their name)."""
        if not receivers:
            return []
        return [Device(id=None, ip=r["name"], uid=f"freebox-airmedia-{r['name']}",
                       name=r["name"], raw_data=r, type="freebox_airmedia")
                for r in receivers]
