from src.adapters.sqlite import SQLiteDeviceRepository


class PostgresDeviceRepository(SQLiteDeviceRepository):
    """PostgreSQL implementation of DeviceRepository."""
    def __init__(self, dsn:str):
        """Initialize with PostgreSQL connection string."""
        super().__init__(dsn)
        
    