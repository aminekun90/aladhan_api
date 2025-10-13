from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
Base = declarative_base()

class CityTable(Base):
    __tablename__ = "cities"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String, nullable=False)
    lat:Mapped[float] = mapped_column(Float, nullable=False)
    lon:Mapped[float] = mapped_column(Float, nullable=False)
    country:Mapped[str] = mapped_column(String, nullable=False)  # ISO country code like "FR"


class SettingsTable(Base):
    __tablename__ = "settings"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    key:Mapped[str] = mapped_column(String, nullable=False)
    value:Mapped[str] = mapped_column(String, nullable=False)


class DeviceTable(Base):
    __tablename__ = "devices"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String,nullable=False)
    ip:Mapped[str] = mapped_column(String,nullable=False)
    raw_data:Mapped[str] = mapped_column(String,nullable=True)