from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import City

class CityRepository(ABC):
    """Abstract interface for City repository."""

    @abstractmethod
    def search_cities(self, name: str, country: Optional[str] = None) -> List[City]:
        ...

    @abstractmethod
    def get_city(self, name: str) -> Optional[City]:
        ...

    @abstractmethod
    def add_city(self, city: City) -> None:
        ...

    @abstractmethod
    def delete_city(self, name: str) -> None:
        ...

    @abstractmethod
    def update_city(self, name: str, new_data: dict) -> None:
        ...

    @abstractmethod
    def list_cities(self) -> List[City]:
        ...
