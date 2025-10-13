from src.adapters.sqlite.sqlite_city_repository import SQLiteCityRepository

class PostgresCityRepository(SQLiteCityRepository):
    def __init__(self, host="localhost", db="cities", user="app", password="secret"):
        conn = f"postgresql+psycopg2://{user}:{password}@{host}/{db}"
        super().__init__(conn)