from typing import Tuple
import calendar

def is_leap(year: int) -> bool:
    """Wheter the given year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def month_count(year: int, month: int) -> Tuple[int, int]:
    """Return (first_weekday, number_of_days) for the given month."""
    assert 1 <= month <= 12, month
    return calendar.monthrange(year, month)