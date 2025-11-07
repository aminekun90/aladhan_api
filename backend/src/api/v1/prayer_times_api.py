from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime
from typing import Optional, List

from src.services.adhan_service import (
    get_prayer_times,
    get_month_prayer_times,
    get_year_prayer_times,
    get_available_methods,
)

from src.core.repository_factory import RepositoryContainer

from src.schemas.prayer_times import PrayerTimesResponse
from src.utils.date_utils import get_tz

METHOD="France"
MADHAB="Shafi"
repository = RepositoryContainer()

TZ = get_tz()
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
    day: Optional[str] = Query(date.today().isoformat(), description="Date in YYYY-MM-DD format. Defaults to today if not provided."),
    method: str = Query(METHOD),
    madhab: str = Query(MADHAB),
    tz: Optional[str] = Query(TZ)
):
    d = parse_date(day)
    return get_prayer_times(d, lat, lon, method, madhab,tz if tz else get_tz())


@router.get("/prayer-times/month", response_model=List[PrayerTimesResponse])
def prayer_times_month(
    year: int = Query(date.today().year, ge=1900, le=2100),
    month: int = Query(date.today().month, ge=1, le=12),
    lat: float = Query(...),
    lon: float = Query(...),
    method: str = Query(METHOD),
    madhab: str = Query(MADHAB),
    tz: Optional[str] = Query(TZ)
):
    return get_month_prayer_times(year, month, lat, lon, method, madhab, tz)


@router.get("/prayer-times/year", response_model=List[PrayerTimesResponse])
def prayer_times_year(
    year: int = Query(date.today().year, ge=1900, le=2100),
    lat: float = Query(...),
    lon: float = Query(...),
    method: str = Query(METHOD),
    madhab: str = Query(MADHAB),
    tz: Optional[str] = Query(TZ)
):
    return get_year_prayer_times(year, lat, lon, method, madhab, tz)

@router.get("/available-methods", response_model=List[dict])
def available_methods():
    return get_available_methods()

@router.get("/to_hijri_date")
def to_hijri_date(
    day: Optional[str] = Query(date.today().isoformat(), description="Date in YYYY-MM-DD format. Defaults to today if not provided."),
):
    from src.calculations.calendar import Gregorian
    d = parse_date(day)
    hijri_date = Gregorian.fromdate(d).to_hijri()
    return {
        "date": d.isoformat(),
        "hijri_date": f"""{hijri_date.day_name(language="ar") } {hijri_date.day} {hijri_date.month_name(language="ar")} {hijri_date.year}"""
    }
