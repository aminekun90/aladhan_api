# src/services/cities_service.py
import sqlite3
from typing import List, Dict, Optional
from src.domain.models import City
from src.domain.city_repository import CityRepository

DB_PATH = "src/data/cities.db"


class CityService:
    def __init__(self,city_repo:CityRepository):
        self.city_repo = city_repo
    def search_cities(self, name: str, country: Optional[str] = None) -> List[City]:
        return self.city_repo.search_cities(name, country)

    def get_city(self, name: str) -> Optional[City]:
        return self.city_repo.get_city(name)
        

