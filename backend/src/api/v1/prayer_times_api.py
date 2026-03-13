from datetime import date, datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.calculations.calendar import Gregorian
from src.schemas.log_config import LogConfig
from src.schemas.prayer_times import PrayerTimesResponse
from src.services.adhan_service import (
    get_available_methods,
    get_month_prayer_times,
    get_prayer_times,
    get_year_prayer_times,
)
from src.utils.date_utils import get_tz

logger = LogConfig.get_logger()
METHOD = "France"
MADHAB = "Shafi"
TZ = get_tz()
router = APIRouter()


def parse_date(s: Optional[str]) -> date:
    """Parse une date ou retourne aujourd'hui si None."""
    if not s:
        return date.today()
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")


@router.get("/prayer-times", response_model=PrayerTimesResponse)
def prayer_times(
    lat: Annotated[float, Query(...)],
    lon: Annotated[float, Query(...)],
    day: Annotated[
        Optional[str],
        Query(description="Date in YYYY-MM-DD format. Defaults to today."),
    ] = None,
    method: Annotated[str, Query()] = METHOD,
    madhab: Annotated[str, Query()] = MADHAB,
    tz: Annotated[Optional[str], Query()] = None,
):
    # Utilisation de la constante TZ par défaut si tz est None
    effective_tz = tz if tz else TZ
    d = parse_date(day)
    return get_prayer_times(d, lat, lon, method, madhab, effective_tz)


@router.get("/prayer-times/month", response_model=List[PrayerTimesResponse])
def prayer_times_month(
    lat: Annotated[float, Query(...)],
    lon: Annotated[float, Query(...)],
    year: Annotated[Optional[int], Query(ge=1900, le=2100)] = None,
    month: Annotated[Optional[int], Query(ge=1, le=12)] = None,
    method: Annotated[str, Query()] = METHOD,
    madhab: Annotated[str, Query()] = MADHAB,
    tz: Annotated[Optional[str], Query()] = None,
):
    now = date.today()
    y = year if year is not None else now.year
    m = month if month is not None else now.month
    effective_tz = tz if tz else TZ

    return get_month_prayer_times(y, m, lat, lon, method, madhab, effective_tz)


@router.get("/prayer-times/year", response_model=List[PrayerTimesResponse])
def prayer_times_year(
    lat: Annotated[float, Query(...)],
    lon: Annotated[float, Query(...)],
    year: Annotated[Optional[int], Query(ge=1900, le=2100)] = None,
    method: Annotated[str, Query()] = METHOD,
    madhab: Annotated[str, Query()] = MADHAB,
    tz: Annotated[Optional[str], Query()] = None,
):
    y = year if year is not None else date.today().year
    effective_tz = tz if tz else TZ

    return get_year_prayer_times(y, lat, lon, method, madhab, effective_tz)


@router.get("/available-methods", response_model=List[dict])
def available_methods():
    return get_available_methods()


@router.get("/to_hijri_date")
def to_hijri_date(
    day: Annotated[
        Optional[str],
        Query(description="Date in YYYY-MM-DD format. Defaults to today."),
    ] = None,
):
    d = parse_date(day)
    hijri_date = Gregorian.fromdate(d).to_hijri()
    return {
        "date": d.isoformat(),
        "hijri_date": f"{hijri_date.day_name(language='ar')} {hijri_date.day} {hijri_date.month_name(language='ar')} {hijri_date.year}",
    }
