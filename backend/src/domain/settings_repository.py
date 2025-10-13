from abc import ABC, abstractmethod

class SettingsRepository(ABC):
    
    @abstractmethod
    def get_setting(self, key: str) -> str:
        ...
    
    @abstractmethod
    def set_setting(self, key: str, value: str) -> None:
        ...
    
    @abstractmethod
    def delete_setting(self, key: str) -> None:
        ...
    
    @abstractmethod
    def list_settings(self) -> dict:
        ...
    
    @abstractmethod
    def update_setting(self, key: str, value: str) -> None:
        ...
    