from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime
from typing import Optional

from src.services.adhan_service import get_prayer_times
from src.schemas.prayer_times import PrayerTimesResponse

router = APIRouter()

def parse_date(s: Optional[str]) -> date:
    if not s:
        return date.today()
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")

@router.get("/prayer-times", response_model=PrayerTimesResponse)
def prayer_times(
    lat: float = Query(...),
    lon: float = Query(...),
    day: Optional[str] = Query(None),
    method: str = Query("MWL"),
    madhab: str = Query("Shafi"),
    tz: Optional[str] = Query("UTC")
):
    d = parse_date(day)
    return get_prayer_times(d, lat, lon, method, madhab, tz)
