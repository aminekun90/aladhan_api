import math
from datetime import date

def julian_day(y: int, m: int, d: int) -> float:
    """Return Julian Day (simplified, 0h UTC)."""
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + B - 1524.5
    return jd

def sun_position(jd: float) -> tuple[float, float]:
    """Return declination (rad) and equation of time (minutes)."""
    d = jd - 2451545.0
    g = math.radians((357.529 + 0.98560028 * d) % 360)
    q = (280.459 + 0.98564736 * d) % 360
    L = math.radians((q + 1.915 * math.sin(g) + 0.02 * math.sin(2*g)) % 360)
    e = math.radians(23.439 - 0.00000036 * d)
    RA = math.degrees(math.atan2(math.cos(e) * math.sin(L), math.cos(L)))
    RA = (RA + 360) % 360
    ra_hours = RA / 15
    dec = math.radians(math.asin(math.sin(e) * math.sin(L)))
    eqt = q / 15 - ra_hours
    if eqt > 12: eqt -= 24
    if eqt < -12: eqt += 24
    return dec, eqt * 60
