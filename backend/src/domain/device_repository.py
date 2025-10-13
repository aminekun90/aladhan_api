from abc import ABC, abstractmethod
from .models import Device
from typing import Optional

class DeviceRepository(ABC):
    """Abstract interface for Device repository."""
    
    @abstractmethod
    def add_device(self, name: str,ip: str,raw_data: str) -> None:
        ...
    
    @abstractmethod
    def delete_device(self, device_id: str) -> None:
        ...
    
    @abstractmethod
    def delete_devices(self,ids: list) -> None:
        ...
    
    @abstractmethod
    def list_devices(self) -> list[Device]:
        ...
    
    @abstractmethod
    def update_device(self, device_id: str, new_data: dict) -> None:
        ...
    
    @abstractmethod
    def search_devices(self, name: str) -> list[Device]:
        ...
    @abstractmethod
    def get_device_by_ip(self, ip: str) -> dict:
        ...
    
    @abstractmethod
    def get_device_by_id(self, device_id: str) -> dict:
        ...
    
    @abstractmethod
    def get_device(self, device_id: str) -> Optional[Device]:
        ...