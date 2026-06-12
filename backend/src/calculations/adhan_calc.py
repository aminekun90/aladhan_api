"""Islamic prayer-time calculations.

Astronomical engine ported 1:1 from the canonical Swift implementation
(`qibla/Data/Services/AstroEngine.swift`). Keep the two in sync: any change to
the algorithm here should be mirrored there, and the golden vectors in
`tests/unit/test_calc.py` guard against drift.
"""

import calendar
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Union

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9
    ZoneInfo = None

from .moonsight import Fajr as MSFajr
from .moonsight import Isha as MSIsha

ORDERED_KEYS = [
    "Imsak", "Fajr", "Sunrise", "Dhuhr", "Asr",
    "Sunset", "Maghrib", "Isha", "Midnight", "Firstthird", "Lastthird",
]
SCHEDULABLE_KEYS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

SUN_ZENITH = 90.8333  # standard sunrise/sunset zenith (refraction + solar radius)

# -----------------------------
# Method configuration types
# -----------------------------
# Isha / Maghrib are either angle-based ("angle", degrees) or a fixed offset
# after sunset ("mins", minutes). Maghrib additionally supports "sunset".


@dataclass(frozen=True)
class MethodConfig:
    """Resolved configuration for a calculation method.

    fajr     : twilight angle below horizon, or a Moonsighting Fajr class.
    isha     : ("angle", deg) | ("mins", minutes) | a Moonsighting Isha class.
    maghrib  : ("sunset",) | ("angle", deg) | ("mins", minutes).
    midnight : "standard" (Sunset -> next Sunrise) | "jafari" (Sunset -> Fajr).
    """

    description: str
    fajr: Union[float, type]
    isha: Union[tuple, type]
    maghrib: tuple = ("sunset",)
    midnight: str = "standard"
    moonsighting: bool = False


def _angle(deg: float) -> tuple:
    return ("angle", float(deg))


def _mins(minutes: float) -> tuple:
    return ("mins", float(minutes))


PRAYER_METHODS: dict[str, MethodConfig] = {
    "MWL":      MethodConfig("Muslim World League", 18.0, _angle(17.0)),
    "ISNA":     MethodConfig("Islamic Society of North America", 15.0, _angle(15.0)),
    "EGYPT":    MethodConfig("Egyptian General Authority of Survey", 19.5, _angle(17.5)),
    "MAKKAH":   MethodConfig("Umm al-Qura University", 18.5, _mins(90)),
    "KARACHI":  MethodConfig("University of Islamic Sciences, Karachi", 18.0, _angle(18.0)),
    "TEHRAN":   MethodConfig("Institute of Geophysics, University of Tehran", 17.7,
                             _angle(14.0), maghrib=_angle(4.5), midnight="jafari"),
    "JAFARI":   MethodConfig("Shia Ithna-Ashari, Leva Institute, Qum", 16.0,
                             _angle(14.0), maghrib=_angle(4.0), midnight="jafari"),
    "GULF":     MethodConfig("Gulf Region", 19.5, _mins(90)),
    "KUWAIT":   MethodConfig("Kuwait", 18.0, _angle(17.5)),
    "QATAR":    MethodConfig("Qatar", 18.0, _mins(90)),
    "SINGAPORE": MethodConfig("Singapore", 20.0, _angle(18.0)),
    "FRANCE":   MethodConfig("French Government", 12.0, _angle(12.0)),
    "TURKEY":   MethodConfig("Turkey", 18.0, _angle(17.0)),
    "RUSSIA":   MethodConfig("Russia", 16.0, _angle(15.0)),
    "MOONSIGHTING": MethodConfig("Moonsighting Committee", MSFajr, MSIsha, moonsighting=True),
    "DUBAI":    MethodConfig("Dubai", 18.2, _angle(18.2)),
    "JAKIM":    MethodConfig("Malaysia", 20.0, _angle(18.0)),
    "TUNISIA":  MethodConfig("Tunisia", 18.0, _angle(18.0)),
    "ALGERIA":  MethodConfig("Algeria", 18.0, _angle(17.0)),
    "KEMENAG":  MethodConfig("Indonesia", 20.0, _angle(18.0)),
    "MOROCCO":  MethodConfig("Morocco", 19.0, _angle(17.0)),
    "PORTUGAL": MethodConfig("Portugal", 18.0, _mins(77), maghrib=_mins(3)),
    "JORDAN":   MethodConfig("Jordan", 18.0, _angle(18.0), maghrib=_mins(5)),
    "CUSTOM":   MethodConfig("Custom method", 18.0, _angle(18.0)),
}


# -----------------------------
# PrayerTimes
# -----------------------------
class PrayerTimes:
    def __init__(self, method: str = "France", madhab: str = "Shafi",
                 tz: str = "Europe/Paris", shafaq: str = "general"):
        method = method.upper()
        if method not in PRAYER_METHODS:
            raise ValueError(f"Unknown method '{method}'")

        self.method = method
        self.cfg = PRAYER_METHODS[method]
        self.madhab = madhab
        self.tz = tz
        self.shafaq = shafaq  # only used for moonsighting
        # Shafi: shadow factor 1, Hanafi: 2.
        self.asr_factor = 1.0 if madhab.lower().startswith("sh") else 2.0

    # -----------------------------
    # Astronomy primitives
    # -----------------------------
    @staticmethod
    def julian_day(y: int, m: int, d: int) -> float:
        yy, mm = y, m
        if mm <= 2:
            yy -= 1
            mm += 12
        a = yy // 100
        b = 2 - a + a // 4
        return int(365.25 * (yy + 4716)) + int(30.6001 * (mm + 1)) + d + b - 1524.5

    @staticmethod
    def sun_position(jd: float) -> tuple[float, float]:
        """Return (declination_rad, equation_of_time_minutes) for a Julian Day."""
        d = jd - 2451545.0
        g = math.radians((357.529 + 0.98560028 * d) % 360.0)
        q = (280.459 + 0.98564736 * d) % 360.0
        L = math.radians((q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360.0)
        e = math.radians(23.439 - 0.00000036 * d)
        ra_deg = math.degrees(math.atan2(math.cos(e) * math.sin(L), math.cos(L))) % 360.0
        ra_hours = ra_deg / 15.0
        dec_rad = math.asin(math.sin(e) * math.sin(L))
        eqt = q / 15.0 - ra_hours
        if eqt > 12:
            eqt -= 24
        if eqt < -12:
            eqt += 24
        return dec_rad, eqt * 60.0

    @staticmethod
    def _hour_angle(lat_rad: float, dec_rad: float, zenith_deg: float) -> Optional[float]:
        z_rad = math.radians(zenith_deg)
        denom = math.cos(lat_rad) * math.cos(dec_rad)
        if abs(denom) < 1e-15:
            return None
        cosh = (math.cos(z_rad) - math.sin(lat_rad) * math.sin(dec_rad)) / denom
        if cosh < -1.0 or cosh > 1.0:
            return None
        return math.degrees(math.acos(cosh))

    def _refine_angle(self, lat_rad: float, jd0: float, noon_utc: float,
                      zenith: float, direction: int) -> Optional[float]:
        """One-iteration solar-time solver for a given zenith.

        direction: -1 for morning events (before noon), +1 for evening events.
        Returns UTC minutes from midnight, or None when the sun never reaches
        the zenith (high latitude / polar day or night).
        """
        dec0, _ = self.sun_position(jd0)
        h0 = self._hour_angle(lat_rad, dec0, zenith)
        if h0 is None:
            return None
        t = noon_utc + h0 * 4.0 * direction
        dec_try, _ = self.sun_position(jd0 + t / 1440.0)
        h1 = self._hour_angle(lat_rad, dec_try, zenith)
        if h1 is not None:
            t = noon_utc + h1 * 4.0 * direction
        return t

    def _compute_asr(self, lat_rad: float, jd0: float, noon_utc: float) -> Optional[float]:
        dec, _ = self.sun_position(jd0 + noon_utc / 1440.0)
        alt = math.atan(1.0 / (self.asr_factor + math.tan(abs(lat_rad - dec))))
        cosh = self._asr_cosh(lat_rad, dec, alt)
        if cosh is None:
            return None
        asr_utc = noon_utc + math.degrees(math.acos(cosh)) * 4.0

        dec_try, _ = self.sun_position(jd0 + asr_utc / 1440.0)
        alt_try = math.atan(1.0 / (self.asr_factor + math.tan(abs(lat_rad - dec_try))))
        cosh_try = self._asr_cosh(lat_rad, dec_try, alt_try)
        if cosh_try is not None:
            asr_utc = noon_utc + math.degrees(math.acos(cosh_try)) * 4.0
        return asr_utc

    @staticmethod
    def _asr_cosh(lat_rad: float, dec: float, alt: float) -> Optional[float]:
        denom = math.cos(lat_rad) * math.cos(dec)
        if abs(denom) < 1e-15:
            return None
        cosh = (math.sin(alt) - math.sin(lat_rad) * math.sin(dec)) / denom
        return cosh if -1.0 <= cosh <= 1.0 else None

    # -----------------------------
    # Fajr / Isha / Maghrib
    # -----------------------------
    def _compute_fajr_isha(self, base_date, lat_rad, jd0, noon_utc,
                           sunrise_utc, sunset_utc, night_fallback):
        if self.cfg.moonsighting:
            lat_deg = math.degrees(lat_rad)
            fajr_utc = sunrise_utc - MSFajr(base_date, lat_deg).minutes_before_sunrise()
            isha_utc = sunset_utc + MSIsha(base_date, lat_deg, self.shafaq).minutes_after_sunset()
            return fajr_utc, isha_utc

        fajr_utc = self._refine_angle(lat_rad, jd0, noon_utc, 90.0 + float(self.cfg.fajr), -1)
        if fajr_utc is None and sunrise_utc is not None:
            fajr_utc = sunrise_utc - night_fallback / 7.0  # 1/7-of-night high-latitude rule

        kind, value = self.cfg.isha
        if kind == "mins":
            isha_utc = sunset_utc + value if sunset_utc is not None else None
        else:
            isha_utc = self._refine_angle(lat_rad, jd0, noon_utc, 90.0 + value, 1)
            if isha_utc is None and sunset_utc is not None:
                isha_utc = sunset_utc + night_fallback / 7.0
        return fajr_utc, isha_utc

    def _compute_maghrib(self, lat_rad, jd0, noon_utc, sunset_utc) -> float:
        kind = self.cfg.maghrib[0]
        if kind == "sunset":
            return sunset_utc
        if kind == "mins":
            return sunset_utc + self.cfg.maghrib[1]
        # angle
        maghrib_utc = self._refine_angle(lat_rad, jd0, noon_utc, 90.0 + self.cfg.maghrib[1], 1)
        return maghrib_utc if maghrib_utc is not None else sunset_utc

    # -----------------------------
    # Output helpers
    # -----------------------------
    def _to_local_datetime(self, base_date: date, minutes_utc: Optional[float]) -> Optional[datetime]:
        if minutes_utc is None:
            return None
        dt_utc = datetime.combine(base_date, time(0, 0), tzinfo=timezone.utc) + timedelta(minutes=minutes_utc)
        if not self.tz:
            return dt_utc
        if ZoneInfo is None:
            raise RuntimeError("zoneinfo required for tz-aware output; run Python 3.9+")
        tz = ZoneInfo(self.tz) if isinstance(self.tz, str) else self.tz
        return dt_utc.astimezone(tz)

    @staticmethod
    def _format(dt: Optional[datetime]) -> Optional[str]:
        return dt.strftime("%H:%M:%S (%Z)") if dt else None

    @staticmethod
    def get_available_methods() -> list[dict]:
        """Return available calculation methods with their descriptions."""
        return [{"method": k, "description": v.description} for k, v in PRAYER_METHODS.items()]

    # -----------------------------
    # Compute
    # -----------------------------
    def compute(self, base_date: date, latitude: float, longitude: float) -> dict:
        """Compute prayer times for one date and location.

        Returns a dict keyed by ORDERED_KEYS with formatted local-time strings
        (or None when an event does not occur, e.g. polar conditions).
        """
        lat_rad = math.radians(latitude)
        jd0 = self.julian_day(base_date.year, base_date.month, base_date.day)
        _, eqt_min = self.sun_position(jd0)
        noon_utc = 720.0 - 4.0 * longitude - eqt_min

        sunrise_utc = self._refine_angle(lat_rad, jd0, noon_utc, SUN_ZENITH, -1)
        sunset_utc = self._refine_angle(lat_rad, jd0, noon_utc, SUN_ZENITH, 1)

        # Night length used for high-latitude Fajr/Isha fallback (uses same-day sunrise).
        if sunrise_utc is not None and sunset_utc is not None:
            night_fallback = sunrise_utc + (1440.0 - sunset_utc)
        else:
            night_fallback = 0.0

        dhuhr_utc = noon_utc
        asr_utc = self._compute_asr(lat_rad, jd0, noon_utc)
        if asr_utc is None:
            asr_utc = noon_utc + 150.0

        fajr_utc, isha_utc = self._compute_fajr_isha(
            base_date, lat_rad, jd0, noon_utc, sunrise_utc, sunset_utc, night_fallback
        )
        maghrib_utc = self._compute_maghrib(lat_rad, jd0, noon_utc, sunset_utc)

        times_utc = {
            "Imsak": fajr_utc - 10.0 if fajr_utc is not None else None,
            "Fajr": fajr_utc,
            "Sunrise": sunrise_utc,
            "Dhuhr": dhuhr_utc,
            "Asr": asr_utc,
            "Sunset": sunset_utc,
            "Maghrib": maghrib_utc,
            "Isha": isha_utc,
        }
        times_utc.update(self._night_marks(lat_rad, jd0, longitude, fajr_utc, sunset_utc))

        return {
            k: self._format(self._to_local_datetime(base_date, times_utc.get(k)))
            for k in ORDERED_KEYS
        }

    def _night_marks(self, lat_rad, jd0, longitude, fajr_utc, sunset_utc) -> dict:
        """Midnight and the night thirds, in UTC minutes.

        Night spans Sunset to the next day's Sunrise (standard) or to Fajr
        (jafari). Using the next day's recomputed sunrise — not today's + 24h —
        keeps the midpoint accurate as day length changes.
        """
        if sunset_utc is None:
            return {"Midnight": None, "Firstthird": None, "Lastthird": None}

        if self.cfg.midnight == "jafari" and fajr_utc is not None:
            night = (fajr_utc + 1440.0) - sunset_utc
        else:
            _, eqt_next = self.sun_position(jd0 + 1.0)
            noon_next = 720.0 - 4.0 * longitude - eqt_next
            sunrise_next = self._refine_angle(lat_rad, jd0 + 1.0, noon_next, SUN_ZENITH, -1)
            if sunrise_next is None:
                return {"Midnight": None, "Firstthird": None, "Lastthird": None}
            night = (sunrise_next + 1440.0) - sunset_utc

        return {
            "Midnight": sunset_utc + night / 2.0,
            "Firstthird": sunset_utc + night / 3.0,
            "Lastthird": sunset_utc + 2.0 * night / 3.0,
        }

    def compute_month(self, year: int, month: int, lat: float, lon: float):
        """Compute prayer times for every day of a month (list of (iso_date, times))."""
        return [
            (date(year, month, d).isoformat(), self.compute(date(year, month, d), lat, lon))
            for d in range(1, calendar.monthrange(year, month)[1] + 1)
        ]

    def compute_year(self, year: int, lat: float, lon: float):
        """Compute prayer times for a whole year, in parallel."""
        with ThreadPoolExecutor() as ex:
            futures = [
                ex.submit(self.compute, date(year, m, d), lat, lon)
                for m in range(1, 13)
                for d in range(1, calendar.monthrange(year, m)[1] + 1)
            ]
            return [f.result() for f in futures]
