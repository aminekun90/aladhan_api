from datetime import date

class MoonSightingBase:
    DYY_NORTH_0 = (12, 21)
    DYY_SOUTH_0 = (6, 21)

    def __init__(self, dt: date, latitude: float):
        self.date = dt
        self.latitude = latitude
        self.dyy = self.get_dyy()
        self.a = self.b = self.c = self.d = 0

    def get_dyy(self) -> int:
        year = self.date.year
        if self.latitude >= 0:
            month, day = self.DYY_NORTH_0
        else:
            month, day = self.DYY_SOUTH_0
        dyy_zero = date(year, month, day)
        diff = (self.date - dyy_zero).days
        return diff if diff > 0 else 365 + diff

    def get_minutes(self) -> float:
        d = self.dyy
        if d < 91:
            return self.a + (self.b - self.a) / 91 * d
        elif d < 137:
            return self.b + (self.c - self.b) / 46 * (d - 91)
        elif d < 183:
            return self.c + (self.d - self.c) / 46 * (d - 137)
        elif d < 229:
            return self.d + (self.c - self.d) / 46 * (d - 183)
        elif d < 275:
            return self.c + (self.b - self.c) / 46 * (d - 229)
        else:
            return self.b + (self.a - self.b) / 91 * (d - 275)


class Fajr(MoonSightingBase):
    def __init__(self, dt: date, latitude: float):
        super().__init__(dt, latitude)
        self.a = 75 + 28.65 / 55 * abs(latitude)
        self.b = 75 + 19.44 / 55 * abs(latitude)
        self.c = 75 + 32.74 / 55 * abs(latitude)
        self.d = 75 + 48.1 / 55 * abs(latitude)

    def minutes_before_sunrise(self) -> float:
        return round(self.get_minutes())


class Isha(MoonSightingBase):
    SHAFAQ_AHMER = "ahmer"
    SHAFAQ_ABYAD = "abyad"
    SHAFAQ_GENERAL = "general"

    def __init__(self, dt: date, latitude: float, shafaq: str = SHAFAQ_GENERAL):
        super().__init__(dt, latitude)
        self.shafaq = shafaq
        self.set_shafaq(shafaq)

    def set_shafaq(self, shafaq: str):
        self.shafaq = shafaq
        lat = abs(self.latitude)
        if shafaq == self.SHAFAQ_AHMER:
            self.a = 62 + 17.4 / 55.0 * lat
            self.b = 62 - 7.16 / 55.0 * lat
            self.c = 62 + 5.12 / 55.0 * lat
            self.d = 62 + 19.44 / 55.0 * lat
        elif shafaq == self.SHAFAQ_ABYAD:
            self.a = 75 + 25.6 / 55.0 * lat
            self.b = 75 + 7.16 / 55.0 * lat
            self.c = 75 + 36.84 / 55.0 * lat
            self.d = 75 + 81.84 / 55.0 * lat
        else:  # general
            self.a = 75 + 25.6 / 55.0 * lat
            self.b = 75 + 2.05 / 55.0 * lat
            self.c = 75 - 9.21 / 55.0 * lat
            self.d = 75 + 6.14 / 55.0 * lat

    def minutes_after_sunset(self) -> float:
        return round(self.get_minutes())
