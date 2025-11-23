import requests
import hmac
import hashlib
import json
import time
import os
from src.domain.models import Device
from typing import List, Dict, Any
class FreeboxService:
    def __init__(self, host="mafreebox.freebox.fr", app_id="pi.aladhan.remote", app_name="Aladhan Pi Remote", device_name="Raspberry Pi"):
        self.base_url = f"http://{host}"
        self.app_id = app_id
        self.app_name = app_name
        self.app_version = "1.0.0"
        self.device_name = device_name
        self.token_file = "fbx_token.json"
        self.session = requests.Session()
        self.app_token = None
        self.session_token = None
        self.track_id = None

    def _load_token(self):
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.app_token = data.get('app_token')
                    return True
            except:
                return False
        return False

    def _save_token(self, app_token):
        with open(self.token_file, 'w') as f:
            json.dump({'app_token': app_token}, f)
        self.app_token = app_token

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.session_token:
            headers['X-Fbx-App-Auth'] = self.session_token
        return headers

    def register(self):
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
        
        r = self.session.post(f"{self.base_url}/api/v8/login/authorize/", json=payload)
        r.raise_for_status()
        result = r.json().get('result')
        
        self.app_token = result.get('app_token')
        self.track_id = result.get('track_id')
        
        print("Veuillez appuyer sur la flèche DROITE de la Freebox pour autoriser l'application...")
        
        while True:
            r = self.session.get(f"{self.base_url}/api/v8/login/authorize/{self.track_id}")
            status = r.json().get('result', {}).get('status')
            
            if status == 'granted':
                self._save_token(self.app_token)
                print("Autorisation accordée.")
                break
            elif status == 'denied':
                raise Exception("Autorisation refusée par l'utilisateur.")
            elif status == 'timeout':
                raise Exception("Délai d'attente dépassé.")
            
            time.sleep(1)

    def login(self):
        if not self.app_token:
            if not self._load_token():
                self.register()

        r = self.session.get(f"{self.base_url}/api/v8/login/")
        r.raise_for_status()
        challenge = r.json().get('result', {}).get('challenge')
        
        if self.app_token is None or challenge is None:
            raise Exception("Impossible de récupérer le token ou le challenge.")

        password = hmac.new(
            self.app_token.encode('utf-8'),
            challenge.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()

        payload = {
            "app_id": self.app_id,
            "password": password
        }

        r = self.session.post(f"{self.base_url}/api/v8/login/session/", json=payload)
        r.raise_for_status()
        result = r.json()
        
        if result.get('success'):
            self.session_token = result.get('result', {}).get('session_token')
            print("Connexion réussie. Session active.")
        else:
            raise Exception(f"Echec connexion: {result.get('msg')}")

    def get_players(self) -> list[Dict[str, Any]] | None:
        url = f"{self.base_url}/api/v8/player"
        r = self.session.get(url, headers=self._get_headers())
        r.raise_for_status()
        result = r.json().get('result', [])
        return result if result else None
    def set_volume(self, player_id, volume):
        #/api/v8/player/{id_player}/api/v6/control/volume/
        url = f"{self.base_url}/api/v8/player/{player_id}/api/v6/control/volume/"
        payload = {
            "volume": volume
        }
        r = self.session.put(url, json=payload, headers=self._get_headers())
        r.raise_for_status()
        return r.json().get('success', False)
    def play_media(self, player_id, media_url, content_type="audio/mp3",volume=15):
        self.set_volume(player_id, volume = volume if isinstance(volume,int) and volume >=0 and volume <=100 else 15)
        url = f"{self.base_url}/api/v8/player/{player_id}/api/v6/control/open"
        payload = {
            "url": media_url,
            "content_type": content_type,
            "metadata": {
                "title": "Aladhan Prayer",
                "type": "audio"
            }
        }
        r = self.session.post(url, json=payload, headers=self._get_headers())
        r.raise_for_status()
        return r.json().get('success', False)

    def from_list(self, players: list[dict] | None) -> list[Device]:
        if not players:
            return []
        return [Device(id=None, ip=p["id"], name=p["device_name"], raw_data=p, type="freebox_player") for p in players]