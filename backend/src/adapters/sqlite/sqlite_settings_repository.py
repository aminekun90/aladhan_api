from typing import Optional
from sqlalchemy.orm import joinedload
from src.adapters.base import SQLRepositoryBase
from src.domain import SettingsRepository
from src.domain.models import Settings
from src.adapters.models import SettingsTable


class SQLiteSettingsRepository(SQLRepositoryBase, SettingsRepository):
    """SQLite implementation of SettingsRepository."""

    def __init__(self, db_path="sqlite:///src/data/cities.db"):
        super().__init__(db_path)

    def get_setting(self, id: int) -> Optional[Settings]:
        """Retrieve a setting by ID with related objects."""
        with self.session_maker() as session:
            setting = (
                session.query(SettingsTable)
                .options(
                    joinedload(SettingsTable.device),
                    joinedload(SettingsTable.city),
                    joinedload(SettingsTable.audio),
                )
                .filter(SettingsTable.id == id)
                .first()
            )
            if setting:
                return Settings(
                    **setting.get_dict(),
                )
        return None

    def list_settings(self) -> list[Settings]:
        """List all settings with related foreign key objects."""
        with self.session_maker() as session:
            settings = (
                session.query(SettingsTable)
                .options(
                    joinedload(SettingsTable.device),
                    joinedload(SettingsTable.city),
                    joinedload(SettingsTable.audio),
                )
                .all()
            )

            return [
                Settings(
                    **s.get_dict(),
                )
                for s in settings
            ]

    def delete_setting(self, id: int) -> None:
        """Delete a setting by ID."""
        with self.session_maker() as session:
            setting = session.query(SettingsTable).filter(SettingsTable.id == id).first()
            if setting:
                session.delete(setting)
                session.commit()

    def update_setting(self, setting: Settings) -> None:
        """Update a single setting in the database."""
        with self.session_maker() as session:
            existing_setting = (
                session.query(SettingsTable)
                .filter(SettingsTable.id == setting.id)
                .first()
            )
            if existing_setting:
                for field, value in setting.get_dict().items():
                    setattr(existing_setting, field, value)
                session.commit()

    def update_settings_bulk(self, settings: list[Settings]) -> None:
        """Bulk update or insert settings safely (avoiding FK overwrite)."""
        with self.session_maker() as session:
            for setting in settings:
                existing_setting = (
                    session.query(SettingsTable)
                    .filter(SettingsTable.id == setting.id)
                    .first()
                )

                if existing_setting:
                    existing_setting.volume = setting.volume
                    existing_setting.enable_scheduler = setting.enable_scheduler
                    existing_setting.selected_method = setting.selected_method
                    existing_setting.force_date = setting.force_date
                    existing_setting.city_id = setting.city_id
                    existing_setting.device_id = setting.device_id if setting.device_id else existing_setting.device_id  # keep this!
                    existing_setting.audio_id = setting.audio_id
                else:
                    # Validate device FK presence on insert
                    # Note: Maybe I will remove it in the future to be able to have general default settings for all devices
                    if not setting.device_id:
                        raise ValueError(f"device_id required to create new setting: {setting.get_dict()}")
                    session.add(SettingsTable(
                        volume=setting.volume,
                        enable_scheduler=setting.enable_scheduler,
                        selected_method=setting.selected_method,
                        force_date=setting.force_date,
                        city_id=setting.city_id,
                        device_id=setting.device_id,
                        audio_id=setting.audio_id
                    ))

            session.commit()

    def create_setting_of_device(self, device_id: int) -> Settings:
        """Create a new setting in the database."""
        with self.session_maker() as session:
            found_settings = (
                session.query(SettingsTable)
                .filter(SettingsTable.device_id == device_id)
                .first()
            )
            if found_settings:
                return Settings(
                    **found_settings.get_dict(),
                )
            settings = SettingsTable(device_id=device_id)
            session.add(settings)
            session.commit()

            return Settings(
                **settings.get_dict(),
            )