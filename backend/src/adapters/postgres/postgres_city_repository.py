from src.adapters.sqlite.sqlite_city_repository import SQLiteCityRepository

class PostgresCityRepository(SQLiteCityRepository):
    def __init__(self, dsn:str):
        super().__init__(dsn)