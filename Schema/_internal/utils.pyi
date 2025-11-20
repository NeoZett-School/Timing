from typing import Tuple

__all__ = (
    "is_leap",
    "days_in_month"
)

def is_leap(year: int) -> bool: ...
def month_count(year: int, month: int) -> Tuple[int, int]: ...