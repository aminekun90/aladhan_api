from datetime import date
from typing import Optional
from src.calculations.adhan_calc import PrayerTimes

def get_prayer_times(
    base_date: date,
    lat: float,
    lon: float,
    method: str,
    madhab: str,
    tz: Optional[str]
):
    # create an instance of PrayerTimes
    pt = PrayerTimes(method=method, madhab=madhab, tz=tz)
    times = pt.compute(base_date, lat, lon)

    return {
        "date": base_date.isoformat(),
        "latitude": lat,
        "longitude": lon,
        "method": method,
        "madhab": madhab,
        "times": {k: (v if v else None) for k, v in times.items()}
    }
