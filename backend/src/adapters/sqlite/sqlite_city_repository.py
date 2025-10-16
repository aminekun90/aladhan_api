from typing import List, Optional
from src.adapters.base import SQLRepositoryBase
from src.domain.models import City
from src.domain import CityRepository
from src.adapters.models import CityTable


class SQLiteCityRepository(SQLRepositoryBase, CityRepository):
    """SQLite implementation of CityRepository."""

    def __init__(self, db_path: str = "sqlite:///src/data/cities.db"):
        super().__init__(db_path)

    def search_cities(self, name: str, country: Optional[str] = None) -> List[City]:
        """Fast prefix search for autocomplete."""
        with self.session_maker() as session:
            # Normalize input
            name = name.strip().upper()

            # Query only necessary columns
            query = session.query(
                CityTable.id, CityTable.name, CityTable.lat, CityTable.lon, CityTable.country
            ).filter(CityTable.name.ilike(f"{name}%"))

            if country:
                query = query.filter(CityTable.country == country.upper())

            # Limit results to 50 for autocomplete
            results = query.limit(50).all()

            # Build City objects
            return [City(id=r.id, name=r.name, lat=r.lat, lon=r.lon, country=r.country) for r in results]

    def get_city(self, name: str) -> Optional[City]:
        """Retrieve a city by exact name."""
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.name == name).first()
            if city:
                return City(**city.get_dict())
        return None

    def get_city_by_id(self, city_id: int) -> Optional[City]:
        """Retrieve a city by ID."""
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.id == city_id).first()
            if city:
                return City(**city.get_dict())
        return None

    def add_city(self, city: City) -> None:
        """Add a new city record."""
        with self.session_maker() as session:
            session.add(CityTable(**city.get_dict()))
            session.commit()

    def add_cities_bulk(self, cities: List[City]) -> None:
        """Add multiple cities in a single transaction."""
        with self.session_maker() as session:
            session.add_all([CityTable(**city.get_dict()) for city in cities])
            session.commit()

    def update_city(self, name: str, new_data: dict) -> None:
        """Update a city by name."""
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.name == name).first()
            if city:
                for key, value in new_data.items():
                    if hasattr(city, key):
                        setattr(city, key, value)
                session.commit()

    def update_cities_bulk(self, cities: List[City]) -> None:
        """Update or insert multiple cities (bulk upsert)."""
        with self.session_maker() as session:
            for city in cities:
                existing_city = (
                    session.query(CityTable)
                    .filter(CityTable.id == city.id)
                    .first()
                )
                if existing_city:
                    for key, value in city.get_dict().items():
                        setattr(existing_city, key, value)
                else:
                    session.add(CityTable(**city.get_dict()))
            session.commit()

    def delete_city(self, name: str) -> None:
        """Delete a city by name."""
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.name == name).first()
            if city:
                session.delete(city)
                session.commit()

    def delete_city_by_id(self, city_id: int) -> None:
        """Delete a city by ID."""
        with self.session_maker() as session:
            city = session.query(CityTable).filter(CityTable.id == city_id).first()
            if city:
                session.delete(city)
                session.commit()

    def list_cities(self) -> List[City]:
        """List all cities."""
        with self.session_maker() as session:
            cities = session.query(CityTable).all()
            return [City(**c.get_dict()) for c in cities]
