
from src.adapters.base import SQLRepositoryBase
from src.domain import DeviceRepository
from src.domain.models import Device
from typing import Optional
from src.adapters.models import DeviceTable
class SQLiteDeviceRepository(SQLRepositoryBase, DeviceRepository):
    """Interface for device repository."""
    def __init__(self, db_path="sqlite:///src/data/cities.db"):
        super().__init__(db_path)
    
    
    def add_device(self, name: str, ip: str, raw_data: str) -> None:
        """Implementation for adding a device to the database."""
        with self.session_maker() as session:
            
            device = DeviceTable(name=name, ip=ip, raw_data=raw_data)
            session.add(device)
            session.commit()
    def delete_device(self, device_id: str) -> None:
        """Implementation for deleting a device from the database."""
        with self.session_maker() as session:
            
            device = session.query(DeviceTable).filter(DeviceTable.id == device_id).first()
            if device:
                session.delete(device)
                session.commit()
    def delete_devices(self, ids: list) -> None:
        """Implementation for deleting multiple devices from the database."""
        with self.session_maker() as session:
            
            session.query(DeviceTable).filter(DeviceTable.id.in_(ids)).delete(synchronize_session=False)
            session.commit()
    def list_devices(self) -> list[Device]:
        """Implementation for listing all devices in the database."""
        with self.session_maker() as session:
            
            devices = session.query(DeviceTable).all()
            return [Device(id=d.id, name=d.name, ip=d.ip, raw_data=d.raw_data) for d in devices]
    
    def update_device(self, device_id: str, new_data: dict) -> None:
        """Implementation for updating a device in the database."""
        with self.session_maker() as session:
            
            device = session.query(DeviceTable).filter(DeviceTable.id == device_id).first()
            if device:
                for key, value in new_data.items():
                    setattr(device, key, value)
                session.commit()
    
    def search_devices(self, name: str) -> list[Device]:
        """Implementation for searching devices by name in the database."""
        with self.session_maker() as session:
            
            devices = session.query(DeviceTable).filter(DeviceTable.name.like(f"%{name}%")).all()
            return [Device(id=d.id, name=d.name, ip=d.ip, raw_data=d.raw_data) for d in devices]
    
    def get_device_by_ip(self, ip: str) -> Optional[Device]:
        """Implementation for retrieving a device by its IP address."""
        with self.session_maker() as session:
            
            device = session.query(DeviceTable).filter(DeviceTable.ip == ip).first()
            if device:
                return Device(id=device.id, name=device.name, ip=device.ip, raw_data=device.raw_data)
        return None
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """Implementation for retrieving a device by its ID."""
        with self.session_maker() as session:
            
            device = session.query(DeviceTable).filter(DeviceTable.id == device_id).first()
            if device:
                return Device(id=device.id, name=device.name, ip=device.ip, raw_data=device.raw_data)
        return None
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Implementation for retrieving a device by its ID."""
        return self.get_device_by_id(device_id)