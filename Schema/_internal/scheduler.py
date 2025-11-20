from typing import Tuple, Dict, Callable, Optional, Any
from .core import Time, Clock as _Clock
import threading
import time as _time

class Callback:
    _Callback__target: Callable
    _Callback__args: Tuple
    _Callback__kwargs: Dict[str, Any]
    __slots__ = ("_Callback__target", "_Callback__args", "_Callback__kwargs")

    def __init__(self, target: Callable, args: Optional[Tuple] = None, kwargs: Optional[Dict[str, Any]] = None) -> None:
        self._Callback__target = target
        self._Callback__args = args or ()
        self._Callback__kwargs = kwargs or {}
    
    def __call__(self) -> Any:
        return self._Callback__target(*self._Callback__args, **self._Callback__kwargs)

class Clock(_Clock):
    """
    A clock provides all key features to creating your own schema or other time-dependent systems.

    Decide the interval for schedules. It will check wheter any callback has been reached for every 
    interval of seconds.

    Setting a callback, you will find that every callback has a identifier, counted as a Time object. 
    This means, that you can only have one object at any given moment with that object. You remove the 
    object, or update it with that same time object. But, as the time is the object, you can also have 
    multiple time objects for the same given time.

    Note! You must save the Time object to remove or update the callback.

    The thread will not join, since it will be stopped before we even reach it. If you want to be sure 
    that it is joined, try stop_thread.
    """

    interval: int = 1

    _Clock__callbacks: Dict[Time, Callback]
    _Clock__active: threading.Event
    _Clock__thread: Optional[threading.Thread]
    _Clock__last_tick: int
    __slots__ = _Clock.__slots__ + ("_Clock__callbacks", "_Clock__active", "_Clock__thread", "_Clock__last_tick")

    def __init__(self, start: Optional[float] = None) -> None:
        super().__init__(start)
        self._Clock__callbacks = {}
        self._Clock__active = threading.Event()
        self._Clock__thread = None
        self._Clock__last_tick = -1
    
    @property
    def callbacks_active(self) -> bool:
        return self._Clock__active.is_set()
    
    def __loop(self) -> None:
        while self._Clock__active.is_set():
            try:
                self.update_schedule()
            except Exception:
                # swallow to avoid killing the thread; consider logging
                pass
            _time.sleep(0.1)
    
    def set_callback(self, time: Time, callback: Callback) -> None:
        self._Clock__callbacks[time] = callback
    
    def remove_callback(self, time: Time) -> None:
        self._Clock__callbacks.pop(time, None)
    
    def has_callback(self, time: Time) -> bool:
        return time in self._Clock__callbacks
    
    def clear_callbacks(self) -> None:
        self._Clock__callbacks.clear()
    
    def start_schedule(self, daemon: bool = False) -> None:
        if self._Clock__active.is_set(): return
        self._Clock__active.set()
        self._Clock__thread = threading.Thread(target=self.__loop, daemon=daemon)
        self._Clock__thread.start()
    
    def update_schedule(self) -> None:
        now = self.now()

        # compute tick index: how many full 'interval' seconds have passed
        tick = int(now) // int(self.interval)
        # process each tick once only
        if tick == self._Clock__last_tick:
            return
        self._Clock__last_tick = tick

        for t, callback in self._Clock__callbacks.copy().items():
            if now >= t.seconds: 
                try:
                    callback()
                finally:
                    self.remove_callback(t)
    
    def stop_schedule(self) -> None:
        self._Clock__active.clear()
        # We should not join the thread since the exit is so fast to even bother!
    
    def stop_thread(self, join_timeout: Optional[float] = None) -> None:
        if self._Clock__thread is not None:
            self._Clock__thread.join(timeout=join_timeout)
            self._Clock__thread = None
    
    def wait_for_scheduler(self) -> None:
        """Block the current thread until the sheduler has stopped."""
        while self._Clock__active.is_set():
            _time.sleep(0.1)
    
    @staticmethod
    def new_callback(target: Callable, args: Optional[Tuple] = None, kwargs: Optional[Dict[str, Any]] = None) -> Callback:
        return Callback(target, args, kwargs)