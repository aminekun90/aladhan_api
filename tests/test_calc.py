from datetime import date
from src.calculations.adhan_calc import get_prayer_times_for_date

def test_basic_calc():
    d = date(2025, 10, 2)
    times = get_prayer_times_for_date(d, 48.8566, 2.3522, method="MWL", tz="Europe/Paris")
    assert "fajr" in times
    assert times["dhuhr"] is not None
