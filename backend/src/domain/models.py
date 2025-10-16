from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional


@dataclass
class City:
    id: Optional[int] = None
    name: str = ""
    lat: float = 0.0
    lon: float = 0.0
    country: str = ""

    def get_dict(self) -> dict:
        return asdict(self)


@dataclass
class Device:
    id: Optional[int] = None
    name: str = ""
    ip: str = ""
    raw_data: Optional[dict] = None

    def get_dict(self) -> dict:
        return asdict(self)


@dataclass
class Audio:
    id: Optional[int] = None
    name: str = ""
    blob: Optional[bytes] = None  # can be None if not loaded

    def get_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "blob": self.blob}


@dataclass
class Settings:
    id: Optional[int] = None
    volume: int = 50
    enable_scheduler: bool = False
    selected_method: Optional[str] = None
    force_date: Optional[date] = None
    city_id: Optional[int] = None
    device_id: Optional[int] = None
    audio_id: Optional[int] = None

    city: Optional[City] = None
    device: Optional[Device] = None
    audio: Optional[Audio] = None

    def get_dict(self) -> dict:
        if isinstance(self.city, City) and self.city:
            city_dict = self.city.get_dict()
        elif self.city:
            city_dict = self.city
        else:
            city_dict = None

        if isinstance(self.device, Device) and self.device:
            device_dict = self.device.get_dict()
        elif self.device:
            device_dict = self.device
        else:
            device_dict = None

        if isinstance(self.audio, Audio) and self.audio:
            audio_dict = self.audio.get_dict()
        elif self.audio:
            audio_dict = self.audio
        else:
            audio_dict = None

        return {
            "id": self.id,
            "volume": self.volume,
            "enable_scheduler": self.enable_scheduler,
            "selected_method": self.selected_method,
            "force_date": self.force_date.isoformat() if self.force_date else None,
            "city_id": self.city_id,
            "device_id": self.device_id,
            "audio_id": self.audio_id,
            "city": city_dict,
            "device": device_dict,
            "audio": audio_dict,
        }
