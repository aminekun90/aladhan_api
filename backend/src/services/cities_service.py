from typing import List, Optional

from src.domain.city_repository import CityRepository
from src.domain.models import City

DB_PATH = "src/data/cities.db"


class CityService:
    def __init__(self,city_repo:CityRepository):
        self.city_repo = city_repo
    def search_cities(self, name: str, country: Optional[str] = None) -> List[City]:
        """Search cities by name and optionally filter by country."""
        return self.city_repo.search_cities(name, country)

    def get_city(self, name: str) -> Optional[City]:
        return self.city_repo.get_city(name)
        

