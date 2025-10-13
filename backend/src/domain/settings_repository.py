from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models import Setting

class SettingsRepository(ABC):
    
    @abstractmethod
    def get_setting(self, key: str) -> Optional[Setting]:
        ...
    
    @abstractmethod
    def list_settings(self) -> list[Setting]:
        ...
    @abstractmethod
    def set_setting(self, key: str, value: str) -> None:
        ...
    
    @abstractmethod
    def delete_setting(self, key: str) -> None:
        ...

    
    @abstractmethod
    def update_setting(self, key: str, value: str) -> None:
        ...
    