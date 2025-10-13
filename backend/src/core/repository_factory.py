import os
from src.adapters.sqlite.sqlite_city_repository import SQLiteCityRepository
from src.adapters.postgres.postgres_city_repository import PostgresCityRepository
from src.domain import CityRepository

import os
from src.domain import CityRepository, DeviceRepository, SettingsRepository
from src.adapters.sqlite import SQLiteCityRepository, SQLiteDeviceRepository, SQLiteSettingsRepository
from src.adapters.postgres import PostgresCityRepository, PostgresDeviceRepository, PostgresSettingsRepository

class RepositoryContainer:
    _instance = None  # class-level instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_repositories()
        return cls._instance

    def _init_repositories(self):
        db_type = os.environ.get("DB_TYPE", "sqlite").lower()
        if db_type not in ["sqlite", "postgres"]:
            print(f"Warning: Unsupported DB_TYPE '{db_type}'. Falling back to 'sqlite'.")
            db_type = "sqlite"

        if db_type == "postgres":
            self.city_repo: CityRepository = PostgresCityRepository()
            self.device_repo: DeviceRepository = PostgresDeviceRepository()
            self.setting_repo: SettingsRepository = PostgresSettingsRepository()
        else:
            self.city_repo: CityRepository = SQLiteCityRepository()
            self.device_repo: DeviceRepository = SQLiteDeviceRepository()
            self.setting_repo: SettingsRepository = SQLiteSettingsRepository()

