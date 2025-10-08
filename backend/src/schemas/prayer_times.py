from pydantic import BaseModel
from typing import Optional, Dict

class PrayerTimesResponse(BaseModel):
    date: str
    hijri_date: str
    latitude: float
    longitude: float
    method: str
    madhab: str
    times: Dict[str, Optional[str]]
