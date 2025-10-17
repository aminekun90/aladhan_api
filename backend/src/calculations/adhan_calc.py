# adhan_calc_class.py
import math
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import calendar

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None
# -----------------------------
# Prayer methods configuration
# -----------------------------
from .moonsight import Fajr as MSFajr, Isha as MSIsha
ORDERED_KEYS= [
            "Imsak","Fajr","Sunrise","Dhuhr","Asr",
            "Sunset","Maghrib","Isha","Midnight","Firstthird","Lastthird"
        ]
SCHEDULABLE_KEYS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
PRAYER_METHODS: dict = {
    "MWL": {"fajr": 18.0, "isha": 17.0,"description":"Muslim World League"},
    "ISNA": {"fajr": 15.0, "isha": 15.0 ,"description":"Islamic Society of North America"},
    "EGYPT": {"fajr": 19.5, "isha": 17.5 ,"description":"Egyptian General Authority of Survey"},
    "MAKKAH": {"fajr": 18.5, "isha": ("mins", 90),"description":"Umm al-Qura University"},  # 90 min after Maghrib
    "KARACHI": {"fajr": 18.0, "isha": 18.0, "description":"University of Islamic Sciences, Karachi"},
    "TEHRAN": {"fajr": 17.7, "isha": 14.0, "maghrib": 4.5, "midnight": "JAFARI", "description":"Institute of Geophysics, University of Tehran"},
    "JAFARI": {"fajr": 16.0, "isha": 14.0, "maghrib": 4.0, "midnight": "JAFARI", "description":"Shia Ithna-Ashari, Leva Institute, Qum"},
    "GULF": {"fajr": 19.5, "isha": ("mins", 90), "description":"Gulf Region"},
    "KUWAIT": {"fajr": 18.0, "isha": 17.5, "description":"Kuwait"},
    "QATAR": {"fajr": 18.0, "isha": ("mins", 90), "description":"Qatar"},
    "SINGAPORE": {"fajr": 20.0, "isha": 18.0, "description":"Singapore"},
    "FRANCE": {"fajr": 12.0, "isha": 12.0, "description":"French Government"},
    "TURKEY": {"fajr": 18.0, "isha": 17.0, "description":"Turkey"},
    "RUSSIA": {"fajr": 16.0, "isha": 15.0, "description":"Russia"},
    "MOONSIGHTING": {"fajr": MSFajr, "isha": MSIsha, "description":"Moonsighting Committee"},
    "DUBAI": {"fajr": 18.2, "isha": 18.2, "description":"Dubai"},
    "JAKIM": {"fajr": 20.0, "isha": 18.0, "description":"Malaysia"},
    "TUNISIA": {"fajr": 18.0, "isha": 18.0, "description":"Tunisia"},
    "ALGERIA": {"fajr": 18.0, "isha": 17.0, "description":"Algeria"},
    "KEMENAG": {"fajr": 20.0, "isha": 18.0, "description":"Indonesia"},
    "MOROCCO": {"fajr": 19.0, "isha": 17.0, "description":"Morocco"},
    "PORTUGAL": {"fajr": 18.0, "maghrib": ("mins", 3), "isha": ("mins", 77), "description":"Portugal"},
    "JORDAN": {"fajr": 18.0, "maghrib": ("mins", 5), "isha": 18.0, "description":"Jordan"},
    "CUSTOM": {"fajr": 18.0, "isha": 18.0, "description":"Custom method"}  # To be filled dynamically
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
    def get_available_methods() -> list[dict]:
        """Return a list of available prayer calculation methods keys and descriptions."""
        return [{"method": k, "description": v["description"]} for k, v in PRAYER_METHODS.items()]
    @staticmethod
    def sun_position(jd: float) -> tuple[float, float]:
        d = jd - 2451545.0
        g = math.radians((357.529 + 0.98560028 * d) % 360.0)
        q = (280.459 + 0.98564736 * d) % 360.0
        L = math.radians((q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360.0)
        e = math.radians(23.439 - 0.00000036 * d)
        ra_deg = math.degrees(math.atan2(math.cos(e) * math.sin(L), math.cos(L))) % 360.0
        ra_hours = ra_deg / 15.0
        dec_rad = math.asin(math.sin(e) * math.sin(L))
        eqt = q / 15.0 - ra_hours
        if eqt > 12: eqt -= 24
        if eqt < -12: eqt += 24
        return dec_rad, eqt * 60.0

    @staticmethod
    def _hour_angle_for_zenith(lat_rad: float, dec_rad: float, zenith_deg: float) -> Optional[float]:
        z_rad = math.radians(zenith_deg)
        denom = math.cos(lat_rad) * math.cos(dec_rad)
        if abs(denom) < 1e-15:
            return None
        cosh = (math.cos(z_rad) - math.sin(lat_rad) * math.sin(dec_rad)) / denom
        if cosh < -1.0 or cosh > 1.0:
            return None
        return math.degrees(math.acos(cosh))

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
    # Internal computation methods
    # -----------------------------
    def _compute_sunrise_sunset(self, lat_rad, jd0, dec0, noon_utc):
        """Compute sunrise and sunset times.

        Args:
            lat_rad (_type_): _description_
            jd0 (_type_): _description_
            dec0 (_type_): _description_
            noon_utc (_type_): _description_

        Returns:
            _type_: _description_
        """
        sunrise_utc = sunset_utc = None
        h_sun = self._hour_angle_for_zenith(lat_rad, dec0, 90.8333)
        if h_sun is not None:
            sunrise_utc = noon_utc - h_sun * 4.0
            sunset_utc = noon_utc + h_sun * 4.0
            for name, est in (("sunrise", sunrise_utc), ("sunset", sunset_utc)):
                jd_try = jd0 + est / 1440.0
                dec_try, _ = self.sun_position(jd_try)
                h_new = self._hour_angle_for_zenith(lat_rad, dec_try, 90.8333)
                if h_new is not None:
                    if name == "sunrise":
                        sunrise_utc = noon_utc - h_new * 4.0
                    else:
                        sunset_utc = noon_utc + h_new * 4.0
        return sunrise_utc, sunset_utc


    def _compute_asr(self, lat_rad, jd0, dhuhr_utc, noon_utc):
        """Compute Asr time.

        Args:
            lat_rad (_type_): _description_
            jd0 (_type_): _description_
            dhuhr_utc (_type_): _description_
            noon_utc (_type_): _description_

        Returns:
            _type_: _description_
        """ 
        asr_utc = None
        dec_for_asr, _ = self.sun_position(jd0 + dhuhr_utc / 1440.0)
        asr_alt = self._asr_altitude(lat_rad, dec_for_asr, self.asr_factor)
        cosh_asr_denom = math.cos(lat_rad) * math.cos(dec_for_asr)
        if abs(cosh_asr_denom) > 1e-15:
            cosh_asr = (math.sin(asr_alt) - math.sin(lat_rad) * math.sin(dec_for_asr)) / cosh_asr_denom
            if -1 <= cosh_asr <= 1:
                h_asr = math.degrees(math.acos(cosh_asr))
                asr_utc = noon_utc + h_asr * 4.0
                jd_try = jd0 + asr_utc / 1440.0
                dec_try, _ = self.sun_position(jd_try)
                cosh_asr = (math.sin(asr_alt) - math.sin(lat_rad) * math.sin(dec_try)) / (math.cos(lat_rad) * math.cos(dec_try))
                if -1 <= cosh_asr <= 1:
                    h_asr = math.degrees(math.acos(cosh_asr))
                    asr_utc = noon_utc + h_asr * 4.0
        return asr_utc


    def _compute_fajr_isha(self, base_date, lat_rad, jd0, dec0, noon_utc, sunrise_utc, sunset_utc):
        """Compute Fajr and Isha times using either standard or Moonsighting methods."""
        
        if self.method == "MOONSIGHTING":
            return self._compute_moonsighting_fajr_isha(base_date, lat_rad, sunrise_utc, sunset_utc)
        else:
            fajr_utc = self._compute_fajr_angle(lat_rad, jd0, dec0, noon_utc)
            isha_utc = self._compute_isha_angle(lat_rad, jd0, dec0, noon_utc, sunset_utc)
            return fajr_utc, isha_utc

    # -------------------------------------
    # Helper methods
    # -------------------------------------

    def _compute_moonsighting_fajr_isha(self, base_date, lat_rad, sunrise_utc, sunset_utc):
        """Compute Fajr/Isha using the Moonsighting Committee method."""
        fajr_obj = MSFajr(base_date, math.degrees(lat_rad))
        isha_obj = MSIsha(base_date, math.degrees(lat_rad), self.shafaq)
        fajr_utc = sunrise_utc - fajr_obj.minutes_before_sunrise()
        isha_utc = sunset_utc + isha_obj.minutes_after_sunset()
        return fajr_utc, isha_utc


    def _refine_angle(self, lat_rad, jd0, dec0, noon_utc, zenith, direction):
        """Generic refinement for angle-based times (used by Fajr/Isha)."""
        h_angle = self._hour_angle_for_zenith(lat_rad, dec0, zenith)
        if h_angle is None:
            return None

        time_utc = noon_utc + (h_angle * 4.0 * direction)
        jd_try = jd0 + time_utc / 1440.0
        dec_try, _ = self.sun_position(jd_try)

        h_new = self._hour_angle_for_zenith(lat_rad, dec_try, zenith)
        if h_new is not None:
            time_utc = noon_utc + (h_new * 4.0 * direction)

        return time_utc


    def _compute_fajr_angle(self, lat_rad, jd0, dec0, noon_utc):
        """Compute Fajr time using angle-based calculation."""
        fajr_zenith = 90.0 + float(self.fajr_cfg)
        return self._refine_angle(lat_rad, jd0, dec0, noon_utc, fajr_zenith, direction=-1)


    def _compute_isha_angle(self, lat_rad, jd0, dec0, noon_utc, sunset_utc):
        """Compute Isha time using either fixed minutes or angle-based method."""
        if isinstance(self.isha_cfg, tuple) and self.isha_cfg[0] == "mins":
            return sunset_utc + float(self.isha_cfg[1]) if sunset_utc else None

        # angle-based
        isha_angle = float(self.isha_cfg if isinstance(self.isha_cfg, (int, float)) else 18.0)
        isha_zenith = 90.0 + isha_angle
        return self._refine_angle(lat_rad, jd0, dec0, noon_utc, isha_zenith, direction=1)



    def _build_times(self, base_date, fajr_utc, sunrise_utc, dhuhr_utc, asr_utc, sunset_utc, maghrib_utc, isha_utc):
        """Build prayer times dictionary.

        Args:
            base_date (_type_): _description_
            fajr_utc (_type_): _description_
            sunrise_utc (_type_): _description_
            dhuhr_utc (_type_): _description_
            asr_utc (_type_): _description_
            sunset_utc (_type_): _description_
            maghrib_utc (_type_): _description_
            isha_utc (bool): _description_

        Returns:
            _type_: _description_
        """
        to_dt = lambda mins: self._to_local_datetime(base_date, mins, self.tz)
        return {
            "Fajr": to_dt(fajr_utc),
            "Sunrise": to_dt(sunrise_utc),
            "Dhuhr": to_dt(dhuhr_utc),
            "Asr": to_dt(asr_utc),
            "Sunset": to_dt(sunset_utc),
            "Maghrib": to_dt(maghrib_utc),
            "Isha": to_dt(isha_utc),
        }


    def _add_extras(self, times_dt):
        """Add extra times: Imsak, Midnight, Firstthird, Lastthird.
        Args:
            times_dt (_type_): _description_
        """
        if times_dt["Fajr"] and times_dt["Sunset"]:
            times_dt["Imsak"] = times_dt["Fajr"] - timedelta(minutes=10)
            times_dt["Midnight"] = times_dt["Sunset"] + (times_dt["Sunrise"] - times_dt["Sunset"]) / 2
            night_seconds = (times_dt["Fajr"] - times_dt["Sunset"]).total_seconds()
            times_dt["Firstthird"] = times_dt["Sunset"] + timedelta(seconds=night_seconds / 3.0)
            times_dt["Lastthird"] = times_dt["Sunset"] + timedelta(seconds=2.0 * night_seconds / 3.0)
        else:
            for k in ["Imsak", "Midnight", "Firstthird", "Lastthird"]:
                times_dt[k] = None
        return times_dt


    def _apply_offsets(self, times_dt):
        """Apply method-specific offsets to prayer times.

        Args:
            times_dt (_type_): _description_

        Returns:
            _type_: _description_
        """
        if self.method in METHOD_OFFSETS:
            for prayer, offset in METHOD_OFFSETS[self.method].items():
                dt = times_dt.get(prayer)
                if dt:
                    times_dt[prayer] = dt + timedelta(minutes=offset)
        return times_dt


    def _format_times(self, times_dt):
        """Format prayer times as strings.

        Args:
            times_dt (_type_): _description_

        Returns:
            _type_: _description_
        """
        times_formatted = {k: self._format(v) for k, v in times_dt.items()}
        
        return {k: times_formatted[k] for k in ORDERED_KEYS if k in times_formatted}

    # -----------------------------
    # Compute prayer times
    # -----------------------------
    def compute(self, base_date: date, latitude: float, longitude: float) -> dict:
        """Compute prayer times for a given date and location.

        Args:
            base_date (date): _description_
            latitude (float): _description_
            longitude (float): _description_

        Returns:
            _type_: _description_
        """
        lat_rad = math.radians(latitude)
        jd0 = self.julian_day(base_date.year, base_date.month, base_date.day)
        dec0, eqt_min = self.sun_position(jd0)
        noon_utc = 720.0 - 4.0 * longitude - eqt_min

        sunrise_utc, sunset_utc = self._compute_sunrise_sunset(lat_rad, jd0, dec0, noon_utc)
        dhuhr_utc = noon_utc
        asr_utc = self._compute_asr(lat_rad, jd0, dhuhr_utc, noon_utc)

        fajr_utc, isha_utc = self._compute_fajr_isha(base_date, lat_rad, jd0, dec0, noon_utc, sunrise_utc, sunset_utc)
        maghrib_utc = sunset_utc

        times_dt = self._build_times(base_date, fajr_utc, sunrise_utc, dhuhr_utc, asr_utc, sunset_utc, maghrib_utc, isha_utc)
        times_dt = self._add_extras(times_dt)
        times_dt = self._apply_offsets(times_dt)
        return self._format_times(times_dt)


    def compute_month(self, year: int, month: int, lat: float, lon: float):
        """Compute prayer times for a month.
        Args:
            year (_type_): _description_
            month (_type_): _description_
            lat (_type_): _description_
            lon (_type_): _description_
        Returns:
            _type_: _description_
        """
        from calendar import monthrange
        results = []
        for d in range(1, monthrange(year, month)[1] + 1):
            day = date(year, month, d)
            results.append((day.isoformat(), self.compute(day, lat, lon)))
        return results
    def compute_year(self, year, lat, lon):
        with ThreadPoolExecutor() as ex:
            futures = [ex.submit(self.compute, date(year, m, d), lat, lon)
                    for m in range(1, 13)
                    for d in range(1, calendar.monthrange(year, m)[1] + 1)]
            results = [f.result() for f in futures]
        return results