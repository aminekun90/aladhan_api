from src.adapters.sqlite import SQLiteAudioRepository

class PostgresAudioRepository(SQLiteAudioRepository):
    """PostgreSQL implementation of AudioRepository."""
    def __init__(self, dsn:str):
        """Initialize with PostgreSQL connection string."""
        super().__init__(dsn)