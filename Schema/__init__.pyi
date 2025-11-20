from typing import Type, Callable
from ._internal import (
    Time, Date, DateTime, Clock,
    is_leap, month_count
)
from . import scanner

class Module:
    Time: Type[Time]
    Date: Type[Date]
    DateTime: Type[DateTime]
    Clock: Type[Clock]
    Module: Type[Module]
    This: Module

    is_leap: Callable
    month_count: Callable
    
    scanner: scanner

This: Module

__all__ = (
    "Time",
    "Date",
    "DateTime",
    "Clock",
    "Module",
    "This",
    "is_leap",
    "month_count",
    "scanner"
)