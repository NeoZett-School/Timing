from typing import Type, Callable
from ._internal import (
    Environment, inspect, print_total_log, print_overview_log
)

class Module:
    GlobalEnvironment: Environment
    Module: Type[Module]
    This: Module

    inspect: Callable
    print_total_log: Callable
    print_overview_log: Callable

GlobalEnvironment: Environment
This: Module

__all__ = (
    "GlobalEnvironment",
    "Module",
    "This",
    "inspect",
    "print_total_log",
    "print_overview_log"
)