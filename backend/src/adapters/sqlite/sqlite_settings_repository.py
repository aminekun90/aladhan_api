
from src.adapters.base import SQLRepositoryBase

class SQLiteSettingsRepository(SQLRepositoryBase):
    """SQLite implementation of SettingsRepository. """
    def __init__(self, db_path="sqlite:///src/data/cities.db"):
        super().__init__(db_path)