from fastapi import APIRouter, Query
from typing import List, Optional
from src.core.repository_factory import RepositoryContainer
from src.services.cities_service import CityService
from src.api.v1.models import CityResponse
router = APIRouter()

repos = RepositoryContainer()
city_service = CityService(repos.city_repo)

@router.get("/cities", response_model=List[CityResponse])
def get_cities(
    name: str = Query(..., min_length=1),
    country: Optional[str] = None
) -> List[CityResponse]:
    """
    Search cities by name and optionally filter by country.
    Returns: list of {name, lat, lon, country}
    """
    return [CityResponse(**city.get_dict()) for city in city_service.search_cities(name, country)]
