from typing import (
    List, Dict, Callable, ParamSpec, TypeVar, 
    Union, Optional, Any
)
from dataclasses import dataclass
import Schema

P = ParamSpec("P")
T = TypeVar("T")

__all__ = ("scan", "quick_scan")

@dataclass(frozen=True)
class Resolve:
    """Immutable record of a single resolved scheduled call."""
    time: Schema.Time
    start: Schema.Time
    end: Schema.Time
    function: Callable[..., Any]
    resolution: Any
    exception: Optional[BaseException]
    @property
    def error(self) -> float: ...
    @property
    def duration(self) -> float: ...


class PendingResolve:
    """
    Holds a Resolve once the scheduled function has executed.
    Uses threading.Event to provide an efficient wait() implementation.
    """
    resolve: Resolve
    args: List[Any]
    kwargs: Dict[str, Any]
    total_duration: float
    called_count: int
    def __init__(self) -> None: ...
    def set_resolve(self, resolve: Resolve) -> None: ...
    def wait(self, timeout: Optional[float] = None) -> Optional[Resolve]: ...
    def is_set(self) -> bool: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class Overview:
    clock: Schema.Clock
    def __init__(self, clock: Schema.Clock) -> None: ...
    def load(self, when: Union[float, Schema.Time] = -1, *args: P.args, **kwargs: P.kwargs) \
            -> Callable[[Callable[P, T]], PendingResolve]: ...
    def keep(self, *pending: PendingResolve) -> None: ...
    def end(self) -> None: ...
    def wait_all(self, timeout: Optional[float] = None) -> List[Optional[Resolve]]: ...


class Result: 
    def __init__(self, overview: Overview) -> None: ...
    @property
    def resolves(self) -> List[PendingResolve]: ...
    def wait(self, timeout: Optional[float] = None) -> List[Optional[Resolve]]: ...
    def conclude(self) -> None: ...


# Convenience type annotations for the initialization callback used by scan()
LoadType = Callable[[Union[float, Schema.Time], Any], PendingResolve]
KeepType = Callable[..., None]


def scan(init: Callable[[LoadType, KeepType], None]) -> Callable[[], Result]: ...
def quick_scan(objects: Callable[[LoadType], List[PendingResolve]]) -> Result: ...