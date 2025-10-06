from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime
from typing import Optional, List

from src.services.adhan_service import (
    get_prayer_times,
    get_month_prayer_times,
    get_year_prayer_times
)
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


@router.get("/prayer-times/month")
def prayer_times_month(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    lat: float = Query(...),
    lon: float = Query(...),
    method: str = Query("MWL"),
    madhab: str = Query("Shafi"),
    tz: Optional[str] = Query("UTC")
):
    return get_month_prayer_times(year, month, lat, lon, method, madhab, tz)


@router.get("/prayer-times/year")
def prayer_times_year(
    year: int = Query(..., ge=1900, le=2100),
    lat: float = Query(...),
    lon: float = Query(...),
    method: str = Query("MWL"),
    madhab: str = Query("Shafi"),
    tz: Optional[str] = Query("UTC")
):
    return get_year_prayer_times(year, lat, lon, method, madhab, tz)
