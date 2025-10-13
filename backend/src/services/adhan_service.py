from datetime import date, timedelta
from typing import Optional, List, Dict
from calendar import monthrange
from src.calculations.calendar import Gregorian
from src.calculations.adhan_calc import PrayerTimes


def get_prayer_times(
    base_date: date,
    lat: float,
    lon: float,
    method: str,
    madhab: str,
    tz: Optional[str]
) -> Dict:
    pt = PrayerTimes(method=method, madhab=madhab, tz=tz if tz else "UTC")
    times = pt.compute(base_date, lat, lon)
    hijri_date = Gregorian.fromdate(base_date).to_hijri()
    return {
        "date": base_date.isoformat(),
        "hijri_date": f"""{hijri_date.day_name(language="ar") } {hijri_date.day} {hijri_date.month_name(language="ar")} {hijri_date.year}""",
        "latitude": lat,
        "longitude": lon,
        "method": method,
        "madhab": madhab,
        "times": {k: (v if v else None) for k, v in times.items()},
    }


def get_month_prayer_times(
    year: int,
    month: int,
    lat: float,
    lon: float,
    method: str,
    madhab: str,
    tz: Optional[str]
) -> List[Dict]:
    num_days = monthrange(year, month)[1]
    results = []
    for day in range(1, num_days + 1):
        base_date = date(year, month, day)
        results.append(get_prayer_times(base_date, lat, lon, method, madhab, tz))
    return results


def get_year_prayer_times(
    year: int,
    lat: float,
    lon: float,
    method: str,
    madhab: str,
    tz: Optional[str]
) -> List[Dict]:
    results = []
    for month in range(1, 13):
        results.extend(get_month_prayer_times(year, month, lat, lon, method, madhab, tz))
    return results
