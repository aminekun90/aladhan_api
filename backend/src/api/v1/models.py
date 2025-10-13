from pydantic import BaseModel

class CityResponse(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    country: str

    class Config:
        from_attributes = True