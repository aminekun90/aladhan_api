from pydantic import BaseModel
from typing import Optional, Any


class CityResponse(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    country: str

    class Config:
        from_attributes = True


class DeviceResponse(BaseModel):
    id: int
    name: str
    ip: str
    raw_data: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class AudioResponse(BaseModel):
    id: int
    name: str
    blob: bytes

    class Config:
        from_attributes = True


class CreateSettingOfDeviceRequest(BaseModel):
    device_id: int

    class Config:
        from_attributes = True


class SettingResponse(BaseModel):
    id: int
    volume: int
    enable_scheduler: bool
    selected_method: Optional[str] = None
    force_date: Optional[str] = None  # You could also use datetime.date if preferred
    city_id: Optional[int] = None
    device_id: Optional[int] = None
    audio_id: Optional[int] = None
    device: Optional[DeviceResponse] = None
    city: Optional[CityResponse] = None
    audio: Optional[AudioResponse] = None

    class Config:
        from_attributes = True


class SettingRequest(BaseModel):
    id: Optional[int] = None
    volume: int
    enable_scheduler: bool
    selected_method: Optional[str] = None
    force_date: Optional[str] = None
    city_id: Optional[int] = None
    device_id: Optional[int] = None
    audio_id: Optional[int] = None

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "volume": self.volume,
            "enable_scheduler": self.enable_scheduler,
            "selected_method": self.selected_method,
            "force_date": self.force_date,
            "city_id": self.city_id,
            "device_id": self.device_id,
            "audio_id": self.audio_id,
        }

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True
