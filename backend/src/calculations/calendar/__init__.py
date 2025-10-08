"""Accurate Hijri-Gregorian dates converter based on the Umm al-Qura calendar.

https://github.com/dralshehri/hijridate
"""

from .hijri import Gregorian, Hijri

__all__ = ["Gregorian", "Hijri"]