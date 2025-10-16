from src.adapters.sqlite import SQLiteSettingsRepository
from src.domain import SettingsRepository

class PostgresSettingsRepository(SQLiteSettingsRepository):
    """PostgreSQL implementation of SettingsRepository."""
    def __init__(self, dsn:str):
        """Initialize with PostgreSQL connection string."""
        super().__init__(dsn)