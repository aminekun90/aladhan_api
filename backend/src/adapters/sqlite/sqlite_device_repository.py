
from src.adapters.base import SQLRepositoryBase
class SQLiteDeviceRepository(SQLRepositoryBase):
    """Interface for device repository."""
    def __init__(self, db_path="sqlite:///src/data/cities.db"):
        super().__init__(db_path)