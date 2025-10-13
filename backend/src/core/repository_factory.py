import os
from src.adapters.sqlite.sqlite_city_repository import SQLiteCityRepository
from src.adapters.postgres.postgres_city_repository import PostgresCityRepository
from src.domain import CityRepository

import os
from src.domain import CityRepository, DeviceRepository, SettingsRepository
from src.adapters.sqlite import SQLiteCityRepository, SQLiteDeviceRepository, SQLiteSettingsRepository
from src.adapters.postgres import PostgresCityRepository, PostgresDeviceRepository, PostgresSettingsRepository

from src.services.env_service import EnvService

class RepositoryContainer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_repositories()
        return cls._instance

    def _init_repositories(self):
        EnvService.load_env()  # Load .env once
        db_type = EnvService.get("DB_TYPE", "sqlite").lower()

        if db_type == "postgres":
            host = EnvService.get("DB_HOST", "localhost")
            port = EnvService.get("DB_PORT", "5432")
            db_name = EnvService.get("DB_NAME", "adhan_db")
            user = EnvService.get("DB_USER", "app")
            password = EnvService.get("DB_PASSWORD", "")
            dsn = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

            self.city_repo = PostgresCityRepository(dsn)
            self.device_repo = PostgresDeviceRepository(dsn)
            self.setting_repo = PostgresSettingsRepository(dsn)
        else:
            self.city_repo = SQLiteCityRepository()
            self.device_repo = SQLiteDeviceRepository()
            self.setting_repo = SQLiteSettingsRepository()

