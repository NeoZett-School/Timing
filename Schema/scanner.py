"""
The scanner module provides extensive features for 
scanning your program for any weak points in performance.

This module is more centered around performance reduction 
on certain specified parts of your code. It is not built 
to replace other, more efficient performance checkers 
in that apartment. 

But it does provide features that lets your code 
dynamically adjust dependently on performance in 
certain parts of your code.
"""

from typing import (
    Set, List, Dict, Callable, ParamSpec, TypeVar, 
    Union, Optional, Any
)
from dataclasses import dataclass
import threading
import Schema

P = ParamSpec("P")
T = TypeVar("T")


@dataclass(frozen=True)
class Resolve:
    """Immutable record of a single resolved scheduled call."""
    time: Schema.Time
    start: Schema.Time
    end: Schema.Time
    function: Callable[..., Any]
    resolution: Any
    exception: Optional[BaseException] = None

    @property
    def error(self) -> float:
        return self.start.seconds - self.time.seconds

    @property
    def duration(self) -> float:
        return self.end.seconds - self.start.seconds


class PendingResolve:
    """
    Holds a Resolve once the scheduled function has executed.
    Uses threading.Event to provide an efficient wait() implementation.
    """
    def __init__(self) -> None:
        self._event = threading.Event()
        self.resolve: Optional[Resolve] = None
        self.function: Optional[Callable] = None
        self.args: Optional[List[Any]] = None
        self.kwargs: Optional[Dict[str, Any]] = None
        self.expected: bool = True
        self.total_duration: float = 0
        self.called_count: int = 0

    def set_resolve(self, resolve: Resolve) -> None:
        self.resolve = resolve
        self.total_duration += resolve.duration
        self.called_count += 1
        self._event.set()

    def wait(self, timeout: Optional[float] = None) -> Optional[Resolve]:
        """
        Wait until resolved. If timeout is None, wait indefinitely.
        If `expected` is False this returns None immediately (never scheduled).
        """
        if not self.expected: return 
        finished = self._event.wait(timeout)
        return self.resolve if finished else None

    def is_set(self) -> bool:
        return self._event.is_set()
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.function is None:
            raise RuntimeError("PendingResolve called before function assigned.")
        return self.function(*args, **kwargs)


class Overview:
    """
    Manages scheduled callbacks on a Schema.Clock and tracks PendingResolve objects.
    """
    def __init__(self, clock: Schema.Clock) -> None:
        self._ids: Set[Schema.Time] = set()
        self.clock = clock
        self.resolves: List[PendingResolve] = []
        self.active = True
        self._lock = threading.Lock()

    def load(self, when: Union[float, Schema.Time] = -1, *args: P.args, **kwargs: P.kwargs) \
            -> Callable[[Callable[P, T]], PendingResolve]:
        """
        Schedule decorated function at `when` (float seconds) or -1 to never auto-run.
        Returns a PendingResolve immediately so callers can wait on the result later.
        """
        # normalize time
        when_time = when if isinstance(when, Schema.Time) else Schema.Time(when)

        def decorator(func: Callable[P, T]) -> PendingResolve:
            pending = PendingResolve()

            def method(*a: P.args, **kw: P.kwargs) -> T:
                # record start and end around the actual call
                start = Schema.Time(self.clock.seconds)
                exc = None
                try:
                    result = func(*a, **kw)
                except Exception as e:
                    exc = e
                    result = None
                end = Schema.Time(self.clock.seconds)
                pending.set_resolve(Resolve(when_time, start, end, func, result, exc))
                if exc:
                    raise exc
                return result
            
            # Make the PendingResolve call the wrapper that sets the Resolve
            pending.function = method
            pending.args = list(args)
            pending.kwargs = dict(kwargs)

            # register id and schedule callback
            with self._lock:
                self._ids.add(when_time)

            if not when_time.seconds == -1.0:
                callback = self.clock.new_callback(
                    target=method,
                    args=args,
                    kwargs=kwargs,
                )
                self.clock.set_callback(when_time, callback)
            else: pending.expected = False
            return pending

        return decorator

    def keep(self, *pending: PendingResolve) -> None:
        """Attach additional PendingResolve objects to this overview (idempotent)."""
        with self._lock:
            self.resolves.extend(pending)

    def end(self) -> None:
        """Stop scheduled callbacks and try to stop the clock thread."""
        with self._lock:
            for t in list(self._ids):
                if self.clock.has_callback(t):
                    self.clock.remove_callback(t)
            self._ids.clear()

        # stop scheduling machinery on the clock (best-effort)
        try:
            self.clock.stop_schedule()
        except Exception:
            pass

        try:
            self.clock.stop_thread(1.0)
        except Exception:
            pass

        self.active = False

    def wait_all(self, timeout: Optional[float] = None) -> List[Optional[Resolve]]:
        """
        Wait for all tracked resolves to finish. If timeout is provided, wait up
        to that many seconds for each item (not total).
        """
        results: List[Optional[Resolve]] = []
        for p in list(self.resolves):
            results.append(p.wait(timeout))
        return results


class Result:
    """
    Lightweight wrapper exposing the Overview and convenience wait method.
    """
    def __init__(self, overview: Overview) -> None:
        self.overview = overview

    @property
    def resolves(self) -> List[PendingResolve]:
        return self.overview.resolves

    def wait(self, timeout: Optional[float] = None) -> List[Optional[Resolve]]:
        resolves = self.overview.wait_all(timeout)
        self.conclude()
        return resolves
    
    def conclude(self) -> None:
        "Conclude this result, and unload the clock and other features."
        if self.overview.active:
            self.overview.end()


# Convenience type annotations for the initialization callback used by scan()
LoadType = Callable[[Union[float, Schema.Time], Any], PendingResolve]
KeepType = Callable[..., None]


def scan(init: Callable[[LoadType, KeepType], None]) -> Callable[[], Result]:
    """
    Create a runner that starts a clock, calls `init(load, keep)` to register callbacks,
    and returns a Result (caller must call result.wait() or result.conclude()).
    """
    def execute() -> Result:
        clock = Schema.Clock()
        overview = Overview(clock)
        # start the clock's scheduling thread; allow the clock to run in background
        clock.start_schedule(daemon=True)
        # call user-provided init to register scheduled jobs
        init(overview.load, overview.keep)
        return Result(overview)

    return execute

def quick_scan(objects: Callable[[LoadType], List[PendingResolve]]) -> Result:
    """
    Helper: given a function that accepts `load` and returns an iterable of PendingResolves,
    register them with `keep` and return a running Result immediately.
    """
    scanner = scan(lambda load, keep: keep(*objects(load)))
    return scanner()