
from fastapi import APIRouter, Query
from typing import List, Optional
from src.services.cities_service import search_cities

router = APIRouter()

@router.get("/api/v1/cities", response_model=List[dict])
def get_cities(
    name: str = Query(..., min_length=1),
    country: Optional[str] = None
) -> List[dict]:
    """
    Search cities by name and optionally filter by country.
    Returns: list of {name, lat, lon, country}
    """
    return search_cities(name, country)