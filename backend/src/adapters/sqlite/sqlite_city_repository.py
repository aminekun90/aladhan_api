from typing import List, Optional
from src.adapters.base import SQLRepositoryBase
from src.domain.models import City
from src.domain import CityRepository
from src.adapters.models import CityTable

class SQLiteCityRepository(SQLRepositoryBase, CityRepository):
    """SQLite implementation of CityRepository."""

    def __init__(self, db_path="sqlite:///src/data/cities.db"):
        super().__init__(db_path)

    def search_cities(self, name: str, country: Optional[str] = None) -> List[City]:
        with self.session_maker() as session:
            query = session.query(CityTable).filter(CityTable.name.like(f"%{name}%"))
            if country:
                query = query.filter(CityTable.country == country.upper())
            results = query.all()
            if not results:
                return []
            return [City(id=r.id, name=r.name, lat=r.lat, lon=r.lon, country=r.country) for r in results]

    def get_city(self, name: str) -> Optional[City]:
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.name == name).first()
            if city:
                return City(id=city.id, name=city.name, lat=city.lat, lon=city.lon, country=city.country)
        return None

    def add_city(self, city: City) -> None:
        with self.session_maker() as session:
            city_table = CityTable(name=city.name, lat=city.lat, lon=city.lon, country=city.country)
            session.add(city_table)
            session.commit()

    def delete_city(self, name: str) -> None:
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.name == name).first()
            if city:
                session.delete(city)
                session.commit()

    def update_city(self, name: str, new_data: dict) -> None:
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.name == name).first()
            if city:
                for key, value in new_data.items():
                    setattr(city, key, value)
                session.commit()

    def list_cities(self) -> List[City]:
        with self.session_maker() as session:
            cities = session.query(CityTable).all()
            return [City(id=c.id, name=c.name, lat=c.lat, lon=c.lon, country=c.country) for c in cities]
