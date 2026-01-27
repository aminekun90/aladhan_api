import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict

import requests

from src.domain.models import Device
from src.schemas.exceptions import AuthException


class FreeboxService:
    def __init__(self, host="mafreebox.freebox.fr", app_id="pi.aladhan.remote", app_name="Aladhan Pi Remote", device_name="Raspberry Pi"):
        self.base_url = f"http://{host}"
        self.app_id = app_id
        self.app_name = app_name
        self.app_version = "1.0.0"
        self.device_name = device_name
        
        # PERSISTENCE FIX: 
        # We store the token in a 'data' folder. 
        # You MUST map this folder in docker-compose: - ./data:/app/data
        self.token_dir = "src/data"
        if not os.path.exists(self.token_dir):
            os.makedirs(self.token_dir, exist_ok=True)
            
        self.token_file = os.path.join(self.token_dir, "fbx_token.json")
        
        self.session = requests.Session()
        self.app_token = None
        self.session_token = None
        self.track_id = None

    def _load_token(self):
        """Load the app_token from disk to avoid re-registering on every restart."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.app_token = data.get('app_token')
                    if self.app_token:
                        return True
            except Exception as e:
                print(f"Error loading token: {e}")
                return False
        return False

    def _save_token(self, app_token):
        """Save the app_token to disk."""
        try:
            with open(self.token_file, 'w') as f:
                json.dump({'app_token': app_token}, f)
            self.app_token = app_token
        except Exception as e:
            print(f"Error saving token: {e}")

    def _delete_token(self):
        """Delete invalid token to force a clean registration."""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        self.app_token = None

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.session_token:
            headers['X-Fbx-App-Auth'] = self.session_token
        return headers

    def register(self):
        """
        Registers the app with the Freebox.
        This will print a message asking you to physically press the arrow on the Freebox.
        """
        print("Starting registration sequence...")
        payload = {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "device_name": self.device_name,
            "permissions": {
                "player": True,
                "settings": True,
                "tv": True
            }
        }
        
        try:
            r = self.session.post(f"{self.base_url}/api/v8/login/authorize/", json=payload)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
             raise AuthException(f"Failed to contact Freebox for registration: {e}")

        result = r.json().get('result')
        
        self.app_token = result.get('app_token')
        self.track_id = result.get('track_id')
        
        print(">>> ACTION REQUIRED: Please press the RIGHT ARROW on the Freebox Server display to authorize access.")
        
        # Wait loop (inspired by hacf-fr logic)
        start_time = time.time()
        while True:
            if time.time() - start_time > 60:
                raise AuthException("Authorization timed out. You didn't press the button in time.")

            try:
                r = self.session.get(f"{self.base_url}/api/v8/login/authorize/{self.track_id}")
                status = r.json().get('result', {}).get('status')
                
                if status == 'granted':
                    self._save_token(self.app_token)
                    print("Authorization granted! Token saved.")
                    break
                elif status == 'denied':
                    raise AuthException("Authorization denied by user.")
                elif status == 'timeout':
                    raise AuthException("Authorization timed out.")
            except requests.exceptions.RequestException:
                pass # Retry on transient network errors
            
            time.sleep(1)

    def login(self):
        """
        Performs the Challenge-Response authentication.
        Auto-recovers if the token is invalid.
        """
        # 1. Try to load token if missing
        if not self.app_token:
            if not self._load_token():
                print("No token found. Triggering registration...")
                self.register()

        # 2. Request Challenge
        try:
            r = self.session.get(f"{self.base_url}/api/v8/login/")
            r.raise_for_status()
        except Exception as e:
            print(f"Connection error: {e}")
            raise AuthException("Failed to connect to Freebox for login.")

        challenge = r.json().get('result', {}).get('challenge')
        
        if not self.app_token or not challenge:
            raise AuthException("Login failed: Missing token or challenge.")

        # 3. Create Password (HMAC SHA1)
        # Note: The 'hacf-fr' repo and official docs confirm this order: hmac(key=app_token, msg=challenge)
        password = hmac.new(
            self.app_token.encode('utf-8'),
            challenge.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()

        payload = {
            "app_id": self.app_id,
            "password": password
        }

        # 4. Open Session
        r = self.session.post(f"{self.base_url}/api/v8/login/session/", json=payload)
        
        # If 403, our token is likely revoked or invalid -> Delete and Register again
        if r.status_code == 403:
            print("Token invalid (403). Deleting and re-registering...")
            self._delete_token()
            self.register()
            return self.login() # Recursive retry

        r.raise_for_status()
        result = r.json()
        
        if result.get('success'):
            self.session_token = result.get('result', {}).get('session_token')
            print("Freebox Login Successful.")
        else:
            raise AuthException(f"Login failed: {result.get('msg')}")

    def _ensure_session(self):
        """Helper to ensure we are logged in before making requests."""
        if not self.session_token:
            self.login()

    def get_players(self) -> list[Dict[str, Any]] | None:
        self._ensure_session()
        url = f"{self.base_url}/api/v8/player"
        r = self.session.get(url, headers=self._get_headers())
        
        # If session expired, login and retry
        if r.status_code == 403 or r.status_code == 401:
            self.login()
            r = self.session.get(url, headers=self._get_headers())
            
        r.raise_for_status()
        result = r.json().get('result', [])
        return result if result else None

    def set_volume(self, player_id, volume):
        self._ensure_session()
        url = f"{self.base_url}/api/v8/player/{player_id}/api/v6/control/volume/"
        payload = {"volume": volume}
        
        r = self.session.put(url, json=payload, headers=self._get_headers())
        
        if r.status_code == 403 or r.status_code == 401:
            self.login()
            r = self.session.put(url, json=payload, headers=self._get_headers())
            
        r.raise_for_status()
        return r.json().get('success', False)

    def play_media(self, player_id, media_url, content_type="audio/mp3", volume=15):
        self._ensure_session()
        
        # 1. Set Volume
        safe_vol = volume if isinstance(volume, int) and 0 <= volume <= 100 else 15
        self.set_volume(player_id, safe_vol)
        
        # 2. Fix URL for Player Compatibility
        # The Player often fails with HTTPS on local IPs due to self-signed certs.
        # We downgrade to HTTP for local playback.
        final_url = media_url
        if "https://" in media_url and "192.168." in media_url:
            print("Converting HTTPS to HTTP for Freebox Player compatibility...")
            final_url = media_url.replace("https://", "http://")

        url = f"{self.base_url}/api/v8/player/{player_id}/api/v6/control/open"
        payload = {
            "url": final_url,
            "content_type": content_type,
            "metadata": {
                "title": "Aladhan Prayer",
                "type": "audio"
            }
        }
        
        print(f"Sending play command: {final_url}")
        r = self.session.post(url, json=payload, headers=self._get_headers())
        
        if r.status_code == 403 or r.status_code == 401:
            self.login()
            r = self.session.post(url, json=payload, headers=self._get_headers())

        r.raise_for_status()
        return r.json().get('success', False)

    def from_list(self, players: list[dict] | None) -> list[Device]:
        if not players:
            return []
        return [Device(id=None, ip=str(p["id"]), name=p["device_name"], raw_data=p, type="freebox_player") for p in players]