from datetime import date
from src.calculations.adhan_calc import PrayerTimes

def test_basic_calc():
    d = date(2025, 10, 2)
    prayer_time = PrayerTimes(method="MWL", madhab="Shafi", tz="Europe/Paris")
    times = prayer_time.compute(d, 48.8566, 2.3522,)
    assert "Fajr" in times
    assert times["Dhuhr"] is not None
