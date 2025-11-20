"""
The `Schema` package provides features for scheduling 
plans. Wheter you want to create your own schema for 
an app, or for real-life occurances.

Be aware that this package provides features to store 
dates, times and a clock to call different methods under a 
regular period. But it doesn't provide the extensive 
features for handling different time operations, 
that, f.e, datetime provides. Thereby, we advice you 
overthink wheter to use this package or something else.

We recommend the calender and datetime for more extensive 
time operations and control.

For scanning your module (performance) or other threaded 
work, we provide extensive features that will make your 
work ten times easier!

Scanning can be imported as: 
>>> import Schema.scanner
>>> # or:
>>> from Schema import scanner

Copyright (C) 2025-2026 Neo Zetterberg
"""

from typing import Any
from ._internal import (
    Time, Date, DateTime, Clock, 
    is_leap, month_count
)
import sys
from . import scanner

#####################################################
# Module lets the user access any items as defined. #
# It also lets us create a much more comprehensive  #
#  structure and lets us use `__init__` f.e.        #
# ------------------------------------------------- #
# You may still import like normal:                 #
# from Schema import This              | Works      #
# import Schema                        |            #
# print(Schema.This)                   | Works      #
# import Schema as Schema              |            #
# print(Schema.This)                   | Also works #
#####################################################

class Module:
    def __getattribute__(self, name: str) -> Any:
        match name:
            case "Time":
                return Time
            case "Date":
                return Date
            case "DateTime":
                return DateTime
            case "Clock":
                return Clock
            case "Module":
                return Module
            case "This":
                return self
            case "is_leap":
                return is_leap
            case "month_count":
                return month_count
            case "scanner":
                return scanner
    def __setattr__(self, name: str, value: Any) -> None:
        raise PermissionError("You are not allowed to change any attribute of this package.")

sys.modules[__name__] = Module()