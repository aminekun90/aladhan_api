from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models import Settings

class SettingsRepository(ABC):
    
    @abstractmethod
    def get_setting(self, id: int) -> Optional[Settings]:
        ...
    
    @abstractmethod
    def list_settings(self) -> list[Settings]:
        ...
    
    @abstractmethod
    def delete_setting(self, id: int) -> None:
        ...

    
    @abstractmethod
    def update_setting(self, setting: Settings) -> None:
        ...
    
    @abstractmethod
    def update_settings_bulk(self, settings: list[Settings]) -> None:
        ...
    
    @abstractmethod
    def create_setting_of_device(self, device_id: int) -> Settings:
        ...
    
    @abstractmethod
    def get_setting_by_device_id(self, device_id: int) -> Optional[Settings]:
        ...