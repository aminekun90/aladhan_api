
from src.adapters.base import SQLRepositoryBase
from src.domain import SettingsRepository
from typing import Optional
from src.domain.models import Setting
from src.adapters.models import SettingsTable

class SQLiteSettingsRepository(SQLRepositoryBase, SettingsRepository):
    """SQLite implementation of SettingsRepository. """
    def __init__(self, db_path="sqlite:///src/data/cities.db"):
        super().__init__(db_path)
        
    # Implement SettingsRepository methods here as needed
    
    def get_setting(self, key: str) -> Optional[Setting]:
        """Implementation for retrieving a setting by its key."""
        with self.session_maker() as session:
            setting = session.query(SettingsTable).filter(SettingsTable.key == key).first()
            if setting:
                return Setting(id=setting.id, key=setting.key, value=setting.value)
        return None
    
    def list_settings(self) -> list[Setting]:
        """Implementation for listing all settings in the database."""
        with self.session_maker() as session:
            settings = session.query(SettingsTable).all()
            return [Setting(id=s.id, key=s.key, value=s.value) for s in settings]
        
    def set_setting(self, key: str, value: str) -> None:
        """Implementation for adding a new setting to the database."""
        with self.session_maker() as session:
            setting = SettingsTable(key=key, value=value)
            session.add(setting)
            session.commit()
            
    def delete_setting(self, key: str) -> None:
        """Implementation for deleting a setting from the database."""
        with self.session_maker() as session:
            setting = session.query(SettingsTable).filter(SettingsTable.key == key).first()
            if setting:
                session.delete(setting)
                session.commit()
    
    def update_setting(self, key: str, value: str) -> None:
        """Implementation for updating a setting in the database."""
        with self.session_maker() as session:
            setting = session.query(SettingsTable).filter(SettingsTable.key == key).first()
            if setting:
                setting.value = value
                session.commit()
