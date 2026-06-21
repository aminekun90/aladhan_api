"""Unit tests for FreeboxService: version-aware URLs + AirMedia fallback.

Network is fully mocked (the requests.Session is replaced), and session_token
is preset so login() is never triggered.
"""
from unittest.mock import MagicMock

import requests

from src.services.freebox_service import FreeboxService


class Resp:
    def __init__(self, data=None, status=200):
        self._data = data or {}
        self.status_code = status

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError("error")


def _service():
    s = FreeboxService(host="1.2.3.4")
    s.session_token = "tok"  # skip login()
    s.session = MagicMock()
    return s


def test_box_url_uses_discovered_version():
    s = _service()
    s.api_base, s.api_major = "/api/", "12"
    assert s._box_url("login/") == "http://1.2.3.4/api/v12/login/"


def test_player_url_uses_player_embedded_version():
    s = _service()
    s._player_api_major["7"] = "8"
    assert s._player_url("7", "control/open") == \
        "http://1.2.3.4/api/v8/player/7/api/v8/control/open"


def test_player_url_defaults_to_v6_when_unknown():
    s = _service()
    assert s._player_url("9", "player_status").endswith("/player/9/api/v6/player_status")


def test_downgrade_local_https():
    s = _service()
    assert s._downgrade_local_https("https://192.168.1.5/a.mp3") == "http://192.168.1.5/a.mp3"
    # public host keeps HTTPS
    assert s._downgrade_local_https("https://example.com/a.mp3") == "https://example.com/a.mp3"


def test_get_airmedia_receivers_parses_result():
    s = _service()
    s.session.get.return_value = Resp({"result": [
        {"name": "Salon", "password_protected": False, "capabilities": {"audio": True}},
    ]})
    receivers = s.get_airmedia_receivers()
    assert receivers[0]["name"] == "Salon"


def test_play_airmedia_builds_encoded_url_and_payload():
    s = _service()
    s.session.post.return_value = Resp({"success": True})

    assert s.play_airmedia("Salon TV", "http://192.168.1.5/a.mp3", password="1111") is True

    url = s.session.post.call_args.args[0]
    payload = s.session.post.call_args.kwargs["json"]
    assert url == "http://1.2.3.4/api/v8/airmedia/receivers/Salon%20TV/"
    assert payload == {
        "action": "start",
        "media_type": "video",  # AirMedia exposes only photo/video; audio -> video
        "media": "http://192.168.1.5/a.mp3",
        "password": "1111",
    }


def test_play_media_falls_back_to_airmedia_on_player_failure():
    s = _service()
    s._player_names["7"] = "Salon"
    s.session.put.return_value = Resp({"success": True})  # set_volume
    # First POST (player control/open) fails, second POST (AirMedia) succeeds.
    s.session.post.side_effect = [
        requests.exceptions.ConnectionError("player offline"),
        Resp({"success": True}),
    ]

    assert s.play_media(7, "http://192.168.1.5/a.mp3") is True
    last_url = s.session.post.call_args.args[0]
    assert last_url == "http://1.2.3.4/api/v8/airmedia/receivers/Salon/"
