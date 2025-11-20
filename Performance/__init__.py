"""
The `Performance` package provides features for inspecting 
functions. Wheter you want to introspect or extend custom 
callables.

Copyright (C) 2025-2026 Neo Zetterberg
"""

from typing import Any
from ._internal import (
    GlobalEnvironment, inspect, print_total_log, print_overview_log
)
import sys

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
    __name__, __file__, __spec__ = __name__, __file__, __spec__
    def __getattribute__(self, name: str) -> Any:
        match name:
            case "GlobalEnvironment":
                return GlobalEnvironment()
            case "Module":
                return Module
            case "This":
                return self
            case "inspect":
                return inspect
            case "print_total_log":
                return print_total_log
            case "print_overview_log":
                return print_overview_log
            case "reset":
                return GlobalEnvironment.reset
    def __setattr__(self, name: str, value: Any) -> None:
        raise PermissionError("You are not allowed to change any attribute of this package.")

sys.modules[__name__] = Module()