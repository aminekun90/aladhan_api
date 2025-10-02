# adhan_calc_class.py
import math
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Dict, Any, Union, Type

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None
# -----------------------------
# Prayer methods configuration
# -----------------------------
from .moonsight import Fajr as MSFajr, Isha as MSIsha

PRAYER_METHODS = {
    "MWL": {"fajr": 18.0, "isha": 17.0},
    "ISNA": {"fajr": 15.0, "isha": 15.0},
    "EGYPT": {"fajr": 19.5, "isha": 17.5},
    "MAKKAH": {"fajr": 18.5, "isha": ("mins", 90)},  # 90 min after Maghrib
    "KARACHI": {"fajr": 18.0, "isha": 18.0},
    "TEHRAN": {"fajr": 17.7, "isha": 14.0, "maghrib": 4.5, "midnight": "JAFARI"},
    "JAFARI": {"fajr": 16.0, "isha": 14.0, "maghrib": 4.0, "midnight": "JAFARI"},
    "GULF": {"fajr": 19.5, "isha": ("mins", 90)},
    "KUWAIT": {"fajr": 18.0, "isha": 17.5},
    "QATAR": {"fajr": 18.0, "isha": ("mins", 90)},
    "SINGAPORE": {"fajr": 20.0, "isha": 18.0},
    "FRANCE": {"fajr": 12.0, "isha": 12.0},
    "TURKEY": {"fajr": 18.0, "isha": 17.0},
    "RUSSIA": {"fajr": 16.0, "isha": 15.0},
    "MOONSIGHTING": {"fajr": MSFajr, "isha": MSIsha},
    "DUBAI": {"fajr": 18.2, "isha": 18.2},
    "JAKIM": {"fajr": 20.0, "isha": 18.0},
    "TUNISIA": {"fajr": 18.0, "isha": 18.0},
    "ALGERIA": {"fajr": 18.0, "isha": 17.0},
    "KEMENAG": {"fajr": 20.0, "isha": 18.0},
    "MOROCCO": {"fajr": 19.0, "isha": 17.0},
    "PORTUGAL": {"fajr": 18.0, "maghrib": ("mins", 3), "isha": ("mins", 77)},
    "JORDAN": {"fajr": 18.0, "maghrib": ("mins", 5), "isha": 18.0},
    "CUSTOM": {}  # To be filled dynamically
}



METHOD_OFFSETS = {
    "France": {"Fajr": 15, "Isha": 15},
}


# -----------------------------
# PrayerTimes Class
# -----------------------------
class PrayerTimes:
    def __init__(self, method="France", madhab="Shafi", tz="Europe/Paris", shafaq="general"):
        method = method.upper()
        if method not in PRAYER_METHODS:
            raise ValueError(f"Unknown method '{method}'")

        self.method = method
        self.madhab = madhab
        self.tz = tz
        self.shafaq = shafaq  # only used for moonsighting

        self.fajr_cfg = PRAYER_METHODS[method]["fajr"]
        self.isha_cfg = PRAYER_METHODS[method]["isha"]
        self.asr_factor = 1.0 if madhab.lower().startswith("sh") else 2.0

    # -----------------------------
    # Static helpers (unchanged)
    # -----------------------------
    @staticmethod
    def julian_day(y: int, m: int, d: int) -> float:
        yy, mm = y, m
        if mm <= 2:
            yy -= 1
            mm += 12
        A = yy // 100
        B = 2 - A + A // 4
        jd_day = int(365.25 * (yy + 4716)) + int(30.6001 * (mm + 1)) + d + B - 1524.5
        return jd_day

    @staticmethod
    def sun_position(jd: float) -> (float, float):
        d = jd - 2451545.0
        g = math.radians((357.529 + 0.98560028 * d) % 360.0)
        q = (280.459 + 0.98564736 * d) % 360.0
        L = math.radians((q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360.0)
        e = math.radians(23.439 - 0.00000036 * d)
        RA_deg = math.degrees(math.atan2(math.cos(e) * math.sin(L), math.cos(L))) % 360.0
        RA_hours = RA_deg / 15.0
        dec_rad = math.asin(math.sin(e) * math.sin(L))
        EqT = q / 15.0 - RA_hours
        if EqT > 12: EqT -= 24
        if EqT < -12: EqT += 24
        return dec_rad, EqT * 60.0

    @staticmethod
    def _hour_angle_for_zenith(lat_rad: float, dec_rad: float, zenith_deg: float) -> Optional[float]:
        z_rad = math.radians(zenith_deg)
        denom = math.cos(lat_rad) * math.cos(dec_rad)
        if abs(denom) < 1e-15:
            return None
        cosH = (math.cos(z_rad) - math.sin(lat_rad) * math.sin(dec_rad)) / denom
        if cosH < -1.0 or cosH > 1.0:
            return None
        return math.degrees(math.acos(cosH))

    @staticmethod
    def _asr_altitude(lat_rad: float, dec_rad: float, factor: float) -> float:
        return math.atan(1.0 / (factor + math.tan(abs(lat_rad - dec_rad))))

    @staticmethod
    def _to_local_datetime(base_date: date, minutes_utc: Optional[float], tz: Optional[str]) -> Optional[datetime]:
        if minutes_utc is None:
            return None
        dt_utc = datetime.combine(base_date, time(0, 0), tzinfo=timezone.utc) + timedelta(minutes=minutes_utc)
        if tz:
            if isinstance(tz, str):
                if ZoneInfo is None:
                    raise RuntimeError("zoneinfo required for tz-aware output; run Python 3.9+")
                return dt_utc.astimezone(ZoneInfo(tz))
            else:
                return dt_utc.astimezone(tz)
        return dt_utc

    @staticmethod
    def _format(dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.strftime("%H:%M:%S (%Z)")

    # -----------------------------
    # Compute prayer times
    # -----------------------------
    def compute(self, base_date: date, latitude: float, longitude: float) -> Dict[str, Optional[str]]:
        lat_rad = math.radians(latitude)
        jd0 = self.julian_day(base_date.year, base_date.month, base_date.day)
        dec0, eqt_min = self.sun_position(jd0)
        noon_utc = 720.0 - 4.0 * longitude - eqt_min

        # Sunrise/Sunset
        sunrise_utc = sunset_utc = None
        H_sun = self._hour_angle_for_zenith(lat_rad, dec0, 90.8333)
        if H_sun is not None:
            sunrise_utc = noon_utc - H_sun * 4.0
            sunset_utc = noon_utc + H_sun * 4.0
            # refine once
            for name, est in (("sunrise", sunrise_utc), ("sunset", sunset_utc)):
                jd_try = jd0 + est / 1440.0
                dec_try, _ = self.sun_position(jd_try)
                H_new = self._hour_angle_for_zenith(lat_rad, dec_try, 90.8333)
                if H_new is not None:
                    if name == "sunrise":
                        sunrise_utc = noon_utc - H_new * 4.0
                    else:
                        sunset_utc = noon_utc + H_new * 4.0

        # Dhuhr
        dhuhr_utc = noon_utc

        # Asr
        asr_utc = None
        dec_for_asr, _ = self.sun_position(jd0 + dhuhr_utc / 1440.0)
        asr_alt = self._asr_altitude(lat_rad, dec_for_asr, self.asr_factor)
        cosH_asr_denom = math.cos(lat_rad) * math.cos(dec_for_asr)
        if abs(cosH_asr_denom) > 1e-15:
            cosH_asr = (math.sin(asr_alt) - math.sin(lat_rad) * math.sin(dec_for_asr)) / cosH_asr_denom
            if -1 <= cosH_asr <= 1:
                H_asr = math.degrees(math.acos(cosH_asr))
                asr_utc = noon_utc + H_asr * 4.0
                # refine
                jd_try = jd0 + asr_utc / 1440.0
                dec_try, _ = self.sun_position(jd_try)
                cosH_asr = (math.sin(asr_alt) - math.sin(lat_rad) * math.sin(dec_try)) / (math.cos(lat_rad) * math.cos(dec_try))
                if -1 <= cosH_asr <= 1:
                    H_asr = math.degrees(math.acos(cosH_asr))
                    asr_utc = noon_utc + H_asr * 4.0

        # Fajr / Isha calculation
        if self.method == "MOONSIGHTING":
            fajr_obj = MSFajr(base_date, latitude)
            isha_obj = MSIsha(base_date, latitude, self.shafaq)
            fajr_utc = sunrise_utc - fajr_obj.getMinutesBeforeSunrise()
            isha_utc = sunset_utc + isha_obj.getMinutesAfterSunset()
        else:
            # Fajr
            fajr_utc = None
            fajr_zenith = 90.0 + float(self.fajr_cfg)
            H_fajr = self._hour_angle_for_zenith(lat_rad, dec0, fajr_zenith)
            if H_fajr is not None:
                fajr_utc = noon_utc - H_fajr * 4.0
                jd_try = jd0 + fajr_utc / 1440.0
                dec_try, _ = self.sun_position(jd_try)
                H_new = self._hour_angle_for_zenith(lat_rad, dec_try, fajr_zenith)
                if H_new is not None:
                    fajr_utc = noon_utc - H_new * 4.0

            # Isha
            isha_utc = None
            if isinstance(self.isha_cfg, tuple) and self.isha_cfg[0] == "mins":
                if sunset_utc is not None:
                    isha_utc = sunset_utc + float(self.isha_cfg[1])
            else:
                isha_angle = float(self.isha_cfg)
                isha_zenith = 90.0 + isha_angle
                H_isha = self._hour_angle_for_zenith(lat_rad, dec0, isha_zenith)
                if H_isha is not None:
                    isha_utc = noon_utc + H_isha * 4.0
                    jd_try = jd0 + isha_utc / 1440.0
                    dec_try, _ = self.sun_position(jd_try)
                    H_new = self._hour_angle_for_zenith(lat_rad, dec_try, isha_zenith)
                    if H_new is not None:
                        isha_utc = noon_utc + H_new * 4.0

        maghrib_utc = sunset_utc

        # Convert to datetime
        def to_dt(mins): return self._to_local_datetime(base_date, mins, self.tz)

        times_dt = {
            "Fajr": to_dt(fajr_utc),
            "Sunrise": to_dt(sunrise_utc),
            "Dhuhr": to_dt(dhuhr_utc),
            "Asr": to_dt(asr_utc),
            "Sunset": to_dt(sunset_utc),
            "Maghrib": to_dt(maghrib_utc),
            "Isha": to_dt(isha_utc),
        }

        # Extras
        if times_dt["Fajr"] and times_dt["Sunset"]:
            times_dt["Imsak"] = times_dt["Fajr"] - timedelta(minutes=10)
            times_dt["Midnight"] = times_dt["Sunset"] + (times_dt["Sunrise"] - times_dt["Sunset"]) / 2
            night_seconds = (times_dt["Fajr"] - times_dt["Sunset"]).total_seconds()
            times_dt["Firstthird"] = times_dt["Sunset"] + timedelta(seconds=night_seconds / 3.0)
            times_dt["Lastthird"] = times_dt["Sunset"] + timedelta(seconds=2.0 * night_seconds / 3.0)
        else:
            times_dt["Imsak"] = times_dt["Midnight"] = times_dt["Firstthird"] = times_dt["Lastthird"] = None

        # Apply method offsets
        if self.method in METHOD_OFFSETS:
            for prayer, offset in METHOD_OFFSETS[self.method].items():
                dt = times_dt.get(prayer)
                if dt: times_dt[prayer] = dt + timedelta(minutes=offset)

        # Format
        times_formatted = {k: self._format(v) for k, v in times_dt.items()}
        ordered_keys = [
            "Imsak",
            "Fajr",
            "Sunrise",
            "Dhuhr",
            "Asr",
            "Sunset",
            "Maghrib",
            "Isha",
            "Midnight",
            "Firstthird",
            "Lastthird"
            ]
        return {k: times_formatted[k] for k in ordered_keys if k in times_formatted}

