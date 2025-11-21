import json
from typing import Optional
from sqlalchemy.orm import joinedload
from src.adapters.base import SQLRepositoryBase
from src.domain import DeviceRepository
from src.domain.models import Device
from src.adapters.models import DeviceTable


class SQLiteDeviceRepository(SQLRepositoryBase, DeviceRepository):
    """SQLite implementation of the DeviceRepository."""

    def __init__(self, db_path: str = "sqlite:///src/data/cities.db"):
        super().__init__(db_path)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    def add_device(self, name: str, ip: str, raw_data: dict | str | None = None,type: Optional[str] = None) -> None:
        """Add a new device to the database."""
        with self.session_maker() as session:
            raw_json = (
                json.dumps(raw_data) if isinstance(raw_data, dict) else raw_data or "{}"
            )
            device = DeviceTable(name=name, ip=ip, raw_data=raw_json,type=type)
            session.add(device)
            session.commit()

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------
    def list_devices(self) -> list[Device]:
        """List all devices."""
        with self.session_maker() as session:
            devices = session.query(DeviceTable).all()
            return [
                Device(
                    id=d.id,
                    name=d.name,
                    ip=d.ip,
                    raw_data=json.loads(d.raw_data) if isinstance(d.raw_data, str) else d.raw_data,
                    type=d.type
                )
                for d in devices
            ]

    def search_devices(self, name: str) -> list[Device]:
        """Search for devices by name."""
        with self.session_maker() as session:
            devices = (
                session.query(DeviceTable)
                .filter(DeviceTable.name.ilike(f"%{name}%"))
                .all()
            )
            return [
                Device(
                    id=d.id,
                    name=d.name,
                    ip=d.ip,
                    raw_data=json.loads(d.raw_data) if isinstance(d.raw_data, str) else d.raw_data,
                )
                for d in devices
            ]

    def get_device_by_ip(self, ip: str) -> Optional[Device]:
        """Get a device by its IP."""
        with self.session_maker() as session:
            device = session.query(DeviceTable).filter(DeviceTable.ip == ip).first()
            if device:
                return Device(
                    id=device.id,
                    name=device.name,
                    ip=device.ip,
                    raw_data=json.loads(device.raw_data) if isinstance(device.raw_data, str) else device.raw_data,
                )
        return None

    def get_device_by_id(self, device_id: int) -> Optional[Device]:
        """Get a device by its ID."""
        with self.session_maker() as session:
            device = session.query(DeviceTable).filter(DeviceTable.id == device_id).first()
            if device:
                return Device(
                    id=device.id,
                    name=device.name,
                    ip=device.ip,
                    raw_data=json.loads(device.raw_data) if isinstance(device.raw_data, str) else device.raw_data,
                )
        return None

    def get_device(self, device_id: int) -> Optional[Device]:
        """Alias for get_device_by_id."""
        return self.get_device_by_id(device_id)

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update_device(self, device_id: int, new_data: dict) -> None:
        """Update a device's attributes."""
        with self.session_maker() as session:
            device = session.query(DeviceTable).filter(DeviceTable.id == device_id).first()
            if device:
                for key, value in new_data.items():
                    if key == "raw_data" and isinstance(value, dict):
                        value = json.dumps(value)
                    setattr(device, key, value)
                session.commit()

    def upsert_devices_bulk(self, devices: list[Device]) -> None:
        """
        Insert or update multiple devices.
        - If IP already exists → update
        - Otherwise → create new entry
        """
        with self.session_maker() as session:
            for device in devices:
                existing_device = session.query(DeviceTable).filter(DeviceTable.ip == device.ip).first()
                if existing_device:
                    existing_device.name = device.name
                    existing_device.raw_data = device.raw_data
                    existing_device.type = device.type
                    print(f"Update existing device: {device.name} ({device.ip}:{device.type})")
                    
                else:
                    print(f"Adding new device: {device.name} ({device.ip}:{device.type})")
                    session.add(
                        DeviceTable(
                            name=device.name,
                            ip=device.ip,
                            raw_data=json.dumps(device.raw_data)
                            if isinstance(device.raw_data, dict)
                            else device.raw_data,
                            type=device.type
                        )
                    )
            session.commit()

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    def delete_device(self, device_id: int) -> None:
        """Delete a single device."""
        with self.session_maker() as session:
            device = session.query(DeviceTable).filter(DeviceTable.id == device_id).first()
            if device:
                session.delete(device)
                session.commit()

    def delete_devices(self, ids: list[int]) -> None:
        """Delete multiple devices by their IDs."""
        with self.session_maker() as session:
            session.query(DeviceTable).filter(DeviceTable.id.in_(ids)).delete(synchronize_session=False)
            session.commit()
