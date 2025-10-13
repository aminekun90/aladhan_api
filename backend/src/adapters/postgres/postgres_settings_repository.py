from src.adapters.sqlite import SQLiteSettingsRepository
from src.domain import SettingsRepository

class PostgresSettingsRepository(SQLiteSettingsRepository):
    """PostgreSQL implementation of SettingsRepository."""
    def __init__(self, host="localhost", db="adhan_db", user="app", password="secret"):
        """Initialize with PostgreSQL connection string."""
        conn = f"postgresql+psycopg2://{user}:{password}@{host}/{db}"
        super().__init__(conn)