"""Prayer-time engine tests.

These guard the alignment with the canonical Swift AstroEngine. The numeric
baseline locks the algorithm against accidental drift; the behavioural tests
cover Maghrib config, the 1/7-night high-latitude fallback, and Jafari midnight.
"""
from datetime import date, datetime

import pytest

from src.calculations.adhan_calc import ORDERED_KEYS, PRAYER_METHODS, PrayerTimes

PARIS = (48.8566, 2.3522)


def _hms(value: str) -> str:
    """'06:06:18 (CEST)' -> '06:06:18'."""
    return value.split()[0]


def _minutes(a: str, b: str) -> float:
    fmt = "%H:%M:%S"
    delta = datetime.strptime(_hms(b), fmt) - datetime.strptime(_hms(a), fmt)
    return delta.total_seconds() / 60.0


def test_all_keys_present():
    times = PrayerTimes("MWL", "Shafi", "Europe/Paris").compute(date(2025, 10, 2), *PARIS)
    assert list(times.keys()) == ORDERED_KEYS
    assert all(times[k] is not None for k in ORDERED_KEYS)


def test_paris_mwl_baseline():
    """Locked numeric baseline (Paris, MWL, 2025-10-02)."""
    times = PrayerTimes("MWL", "Shafi", "Europe/Paris").compute(date(2025, 10, 2), *PARIS)
    assert _hms(times["Fajr"]) == "06:06:18"
    assert _hms(times["Dhuhr"]) == "13:40:00"
    assert _hms(times["Maghrib"]) == "19:27:19"


def test_maghrib_fixed_offset_jordan():
    """JORDAN: Maghrib is Sunset + 5 minutes (was ignored before the fix)."""
    times = PrayerTimes("JORDAN", "Shafi", "Asia/Amman").compute(date(2025, 10, 2), 31.95, 35.93)
    assert _minutes(times["Sunset"], times["Maghrib"]) == pytest.approx(5.0, abs=0.05)


def test_maghrib_fixed_offset_portugal():
    """PORTUGAL: Maghrib is Sunset + 3 minutes."""
    times = PrayerTimes("PORTUGAL", "Shafi", "Europe/Lisbon").compute(date(2025, 10, 2), 38.72, -9.13)
    assert _minutes(times["Sunset"], times["Maghrib"]) == pytest.approx(3.0, abs=0.05)


def test_maghrib_angle_tehran_after_sunset():
    """TEHRAN: angle-based Maghrib must fall after Sunset, not equal it."""
    times = PrayerTimes("TEHRAN", "Shafi", "Asia/Tehran").compute(date(2025, 10, 2), 35.7, 51.4)
    assert _minutes(times["Sunset"], times["Maghrib"]) > 0


def test_default_maghrib_equals_sunset():
    """Methods without a Maghrib rule keep Maghrib == Sunset."""
    times = PrayerTimes("MWL", "Shafi", "Europe/Paris").compute(date(2025, 10, 2), *PARIS)
    assert _hms(times["Maghrib"]) == _hms(times["Sunset"])


def test_high_latitude_fallback():
    """Oslo in June: astronomical twilight is never reached, so the 1/7-night
    fallback must still yield a Fajr and Isha rather than None."""
    times = PrayerTimes("MWL", "Shafi", "Europe/Oslo").compute(date(2025, 6, 21), 59.91, 10.75)
    assert times["Fajr"] is not None
    assert times["Isha"] is not None


def test_polar_day_returns_none():
    """Tromso in June: the sun never sets — events gracefully resolve to None."""
    times = PrayerTimes("MWL", "Shafi", "Europe/Oslo").compute(date(2025, 6, 21), 69.65, 18.96)
    assert times["Sunset"] is None
    assert times["Maghrib"] is None
    assert times["Midnight"] is None


def test_jafari_vs_standard_midnight_differ():
    """Jafari midnight (Sunset->Fajr) differs from standard (Sunset->next Sunrise)."""
    jafari = PrayerTimes("JAFARI", "Shafi", "Asia/Tehran").compute(date(2025, 10, 2), 35.7, 51.4)
    standard = PrayerTimes("MWL", "Shafi", "Asia/Tehran").compute(date(2025, 10, 2), 35.7, 51.4)
    assert _hms(jafari["Midnight"]) != _hms(standard["Midnight"])


def test_hanafi_asr_later_than_shafi():
    shafi = PrayerTimes("MWL", "Shafi", "Europe/Paris").compute(date(2025, 10, 2), *PARIS)
    hanafi = PrayerTimes("MWL", "Hanafi", "Europe/Paris").compute(date(2025, 10, 2), *PARIS)
    assert _minutes(shafi["Asr"], hanafi["Asr"]) > 0


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        PrayerTimes("NOPE")


def test_available_methods_cover_registry():
    methods = {m["method"] for m in PrayerTimes.get_available_methods()}
    assert methods == set(PRAYER_METHODS)
