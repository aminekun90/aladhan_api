from datetime import date, datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.calculations.calendar import Gregorian
from src.core.repository_factory import RepositoryContainer
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
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD",)


@router.get("/prayer-times", response_model=PrayerTimesResponse)
def prayer_times(
    lat: Annotated[float, Query(...)],
    lon: Annotated[float, Query(...)],
    # On met None par défaut ici
    day: Annotated[Optional[str], Query(None, description="Date in YYYY-MM-DD format. Defaults to today.")] = None,
    method: Annotated[str, Query(METHOD)] = METHOD,
    madhab: Annotated[str, Query(MADHAB)] = MADHAB,
    tz: Annotated[Optional[str], Query(TZ)] = None,
):
    # C'est ici que l'on calcule la date du jour si 'day' est absent
    d = parse_date(day) 
    
    logger.info(f"prayer_times request for date: {d}")
    return get_prayer_times(d, lat, lon, method, madhab, tz if tz else get_tz())


@router.get("/prayer-times/month", response_model=List[PrayerTimesResponse])
def prayer_times_month(
    year: Annotated[int, Query(ge=1900, le=2100)] = Query(date.today().year),
    month: Annotated[int, Query(ge=1, le=12)] = Query(date.today().month),
    lat: Annotated[float, Query(...)] = Query(...),
    lon: Annotated[float, Query(...)] = Query(...),
    method: Annotated[str, Query(METHOD)] = Query(METHOD),
    madhab: Annotated[str, Query(MADHAB)] = Query(MADHAB),
    tz: Annotated[Optional[str], Query(TZ)] = Query(TZ)
):
    return get_month_prayer_times(year, month, lat, lon, method, madhab, tz)


@router.get("/prayer-times/year", response_model=List[PrayerTimesResponse])
def prayer_times_year(
    year: Annotated[int, Query(ge=1900, le=2100)] = Query(date.today().year, ge=1900, le=2100),
    lat: Annotated[float, Query(...)] = Query(...),
    lon: Annotated[float, Query(...)] = Query(...),
    method: Annotated[str, Query(METHOD)] = Query(METHOD),
    madhab: Annotated[str, Query(MADHAB)] = Query(MADHAB),
    tz: Annotated[Optional[str], Query(TZ)] = Query(TZ)
):
    return get_year_prayer_times(year, lat, lon, method, madhab, tz)

@router.get("/available-methods", response_model=List[dict])
def available_methods():
    return get_available_methods()

@router.get("/to_hijri_date")
def to_hijri_date(
    day: Annotated[Optional[str], Query(None, description="Date in YYYY-MM-DD format. Defaults to today.")] = None,
):
    # Même correction ici
    d = parse_date(day)
    hijri_date = Gregorian.fromdate(d).to_hijri()
    return {
        "date": d.isoformat(),
        "hijri_date": f"{hijri_date.day_name(language='ar')} {hijri_date.day} {hijri_date.month_name(language='ar')} {hijri_date.year}"
    }
