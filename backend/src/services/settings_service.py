from src.domain import SettingsRepository
from typing import List, Optional
from src.domain.models import Settings

class SettingsService:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo
    def get_setting(self, id: int)->Optional[Settings]:
        return self.settings_repo.get_setting(id)
    
    def list_settings(self)->List[Settings]:
        return self.settings_repo.list_settings()
    
    def update_setting(self,setting: Settings)->None:
        self.settings_repo.update_setting(setting)
        
    
    def update_settings_bulk(self, settings: List[Settings])->None:
        self.settings_repo.update_settings_bulk(settings)
        
    def create_setting_of_device(self, device_id: int)->Settings:
        return self.settings_repo.create_setting_of_device(device_id)