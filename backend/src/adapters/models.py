from sqlalchemy import Integer, Float, String, LargeBinary, ForeignKey, Date, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.adapters.base.sql_repository_base import Base
from datetime import date


class CityTable(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship back to settings
    settings = relationship("SettingsTable", back_populates="city", cascade="all, delete-orphan")

    def get_dict(self, include_settings: bool = False):
        data = {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "country": self.country,
        }
        if include_settings:
            data["settings"] = [s.id for s in self.settings]
        return data

    def __repr__(self):
        return f"<City(name={self.name}, country={self.country})>"


class DeviceTable(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ip: Mapped[str] = mapped_column(String, nullable=False)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationship back to settings
    settings = relationship("SettingsTable", back_populates="device", cascade="all, delete-orphan")

    def get_dict(self, include_settings: bool = False):
        data = {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "raw_data": self.raw_data,
        }
        if include_settings:
            data["settings"] = [s.id for s in self.settings]
        return data

    def __repr__(self):
        return f"<Device(name={self.name}, ip={self.ip})>"


class AudioTable(Base):
    __tablename__ = "audio_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    blob: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # Relationship back to settings
    settings = relationship("SettingsTable", back_populates="audio", cascade="all, delete-orphan")

    def get_dict(self, include_settings: bool = False):
        data = {
            "id": self.id,
            "name": self.name,
        }
        if include_settings:
            data["settings"] = [s.id for s in self.settings]
        return data

    def __repr__(self):
        return f"<Audio(name={self.name})>"


class SettingsTable(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core app settings
    volume: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    enable_scheduler: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    selected_method: Mapped[str | None] = mapped_column(String, nullable=True)
    force_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Foreign keys
    city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"))
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"),nullable=False)
    audio_id: Mapped[int | None] = mapped_column(ForeignKey("audio_files.id"))

    # Relationships
    city = relationship("CityTable", back_populates="settings")
    device = relationship("DeviceTable", back_populates="settings")
    audio = relationship("AudioTable", back_populates="settings")

    def get_dict(self, include_relations: bool = True) -> dict:
        """Return dict representation without infinite recursion and handle dict objects safely."""
        def safe_get(obj):
            if obj is None:
                return None
            if hasattr(obj, "get_dict"):
                return obj.get_dict()
            if isinstance(obj, dict):
                return obj
            return {"id": getattr(obj, "id", None)}

        data = {
            "id": self.id,
            "volume": self.volume,
            "enable_scheduler": self.enable_scheduler,
            "selected_method": self.selected_method,
            "force_date": self.force_date,
            "city_id": self.city_id,
            "device_id": self.device_id,
            "audio_id": self.audio_id,
        }

        if include_relations:
            data["city"] = safe_get(self.city)
            data["device"] = safe_get(self.device)
            data["audio"] = safe_get(self.audio)

        return data

    def __repr__(self):
        return f"<Settings(id={self.id}, volume={self.volume}, scheduler={self.enable_scheduler})>"
