
from src.adapters.sqlite import SQLiteCityRepository, SQLiteDeviceRepository, SQLiteSettingsRepository, SQLiteAudioRepository
from src.adapters.postgres import PostgresCityRepository, PostgresDeviceRepository, PostgresSettingsRepository, PostgresAudioRepository

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
            self.audio_repo = PostgresAudioRepository(dsn)
            
        else:
            db_path = EnvService.get("DB_PATH", "src/data/cities.db") 
            dbs = f"sqlite:///{db_path}"
            self.city_repo = SQLiteCityRepository(db_path=dbs)
            self.device_repo = SQLiteDeviceRepository(db_path=dbs)
            self.setting_repo = SQLiteSettingsRepository(db_path=dbs)
            self.audio_repo = SQLiteAudioRepository(db_path=dbs)
    
    def get_db_engine(self):
        return self.city_repo.engine  # Assuming all repos share the same engine

    def get_repos_health(self):
        return {
            "status": "ok",
            "city_repo": self.city_repo.get_health(),
            "device_repo": self.device_repo.get_health(),
            "setting_repo": self.setting_repo.get_health(),
            "audio_repo": self.audio_repo.get_health(),
        }