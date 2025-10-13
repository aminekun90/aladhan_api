from src.adapters.sqlite import SQLiteDeviceRepository
from src.domain import DeviceRepository

class PostgresDeviceRepository(SQLiteDeviceRepository,DeviceRepository):
    """PostgreSQL implementation of DeviceRepository."""
    def __init__(self, host="localhost", db="cities", user="app", password="secret"):
        """Initialize with PostgreSQL connection string."""
        conn = f"postgresql+psycopg2://{user}:{password}@{host}/{db}"
        super().__init__(conn)