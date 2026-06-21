"""AirMedia dispatch in the unified DeviceService layer (freebox service mocked)."""
from unittest.mock import MagicMock

from src.domain.models import Device
from src.schemas.player import PlayerAction
from src.services.device_service import FREEBOX_AIRMEDIA_TYPE, DeviceService


def _service() -> DeviceService:
    svc = DeviceService(MagicMock(), MagicMock())
    svc.freebox_service = MagicMock()  # override the real Freebox client
    return svc


def _airmedia_device() -> Device:
    return Device(id=1, ip="Salon", name="Salon", type=FREEBOX_AIRMEDIA_TYPE, raw_data={})


def test_play_on_device_routes_airmedia():
    svc = _service()
    svc._play_on_device(_airmedia_device(), "http://host/a.mp3", "a.mp3", 50)
    svc.freebox_service.play_airmedia.assert_called_once_with("Salon", "http://host/a.mp3")


def test_control_airmedia_stop():
    svc = _service()
    svc.freebox_service.stop_airmedia.return_value = True
    svc.get_device_by_id = MagicMock(return_value=_airmedia_device())
    result = svc.control_device(1, PlayerAction.STOP)
    assert result.status == "success"
    svc.freebox_service.stop_airmedia.assert_called_once_with("Salon")


def test_control_airmedia_play_is_unsupported():
    svc = _service()
    svc.get_device_by_id = MagicMock(return_value=_airmedia_device())
    assert svc.control_device(1, PlayerAction.PLAY).status == "error"


def test_airmedia_has_no_volume_control():
    svc = _service()
    svc.get_device_by_id = MagicMock(return_value=_airmedia_device())
    assert svc.set_device_volume(1, 30).status == "error"
