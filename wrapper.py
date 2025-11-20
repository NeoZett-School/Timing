from typing import Optional, Union, Callable, Type, TypeVar, ParamSpec, Generic, Any
import threading
import functools
import time

class ThreadedException(BaseException):
    """Any exception that is threaded."""

T = TypeVar("T")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
P = ParamSpec("P")
P2 = ParamSpec("P2")

# single-instance sentinel (use instance, not class)
MISSING = object()

_threads: list[threading.Thread] = []

def _new_thread(target: Callable[..., Any], *args: Any, **kwargs: Any) -> threading.Thread:
    """Create a thread and register it; do not start it here (caller decides)."""
    thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    _threads.append(thread)
    return thread

class Resolve(Generic[T3]):
    __slots__ = ("_threaded_method", "_watch_thread", "_lock", "_event", "_value", "_exc")

    def __init__(self, threaded_method: "ThreadedMethod"):
        # use object.__setattr__ to bypass our __setattr__
        object.__setattr__(self, "_threaded_method", threaded_method)
        object.__setattr__(self, "_watch_thread", threading.Thread(target=self._watcher, daemon=threaded_method._daemon, kwargs={"capture": True}))
        object.__setattr__(self, "_lock", threading.Lock())
        object.__setattr__(self, "_event", threading.Event())
        object.__setattr__(self, "_value", MISSING)
        object.__setattr__(self, "_exc", None)

    # read-only accessors
    @property
    def method(self) -> "ThreadedMethod":
        return self._threaded_method

    @property
    def done(self) -> bool:
        return self._event.is_set()

    @property
    def value(self) -> Optional[T3]:
        with self._lock:
            return None if self._value is MISSING else self._value  # Optional[T3]

    # internal setters used by the worker
    def _set_value(self, value: T3) -> None:
        with self._lock:
            object.__setattr__(self, "_value", value)
            object.__setattr__(self, "_exc", None)
            self._event.set()

    def _set_exception(self, exc: BaseException) -> None:
        with self._lock:
            object.__setattr__(self, "_exc", exc)
            self._event.set()
    
    def _raise(self) -> None:
        if self._exc:
            raise self._exc from ThreadedException(f"Thread failed (ident: {self._threaded_method.thread.ident}), for method: '{self._threaded_method.__name__}'")

    # External API to start a watcher thread that will capture parent result when ready.
    def start_recording(self) -> None:
        """Start recording the result, whenever it occures. You can only call this once."""
        if not self._watch_thread.is_alive():
            self._watch_thread.start()

    # capture attempt (non-blocking) -- returns captured value or None
    def capture(self) -> Optional[T3]:
        """Capture the result in this very moment."""
        # If parent completed and parent _result isn't MISSING, capture it.
        parent = self._threaded_method
        parent_result = parent._result
        if parent.complete and parent_result is not MISSING and self._value is MISSING:
            # set parent's result into us if we don't have it yet
            self._set_value(parent_result)
            return parent_result
        return self.value

    # watcher thread function used by start_recording
    def _watcher(self, timeout: Optional[float] = None, capture: bool = False) -> Optional[T3]:
        start = time.monotonic()
        while (not self._threaded_method.complete) and (not self.done):
            if timeout is not None and (time.monotonic() - start) >= timeout:
                break
            time.sleep(0.05)
        if self._threaded_method.complete and capture:
            return self.capture()
        return self.value

    # wait-for-result API (blocks like concurrent.futures.Future.result)
    def result(self, timeout: Optional[float] = None) -> T3:
        """Wait for the result and return it."""
        finished = self._event.wait(timeout)
        if not finished:
            raise TimeoutError("Resolve.result() timed out")
        # if there was an exception in the worker, re-raise it
        if self._exc is not None:
            self._raise()
        # at this point _value must be set
        val = self.value
        # hinting: mypy won't deduce but runtime is fine
        return val  # type: ignore[return-value]
    
    def wait(self, timeout: Optional[float] = None) -> bool:
        """Wait for the method to complete."""
        finished = self._event.wait(timeout)
        if self._exc is not None:
            self._raise()
        return finished

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Resolve instances are immutable")

class ThreadedMethod(Generic[P2, T2]):
    def __init__(self, method: Callable[P2, T2], daemon: bool = True) -> None:
        self._method = method
        self._daemon = daemon
        self._thread: Optional[threading.Thread] = None
        self._resolve: Optional[Resolve[T2]] = None
        self._result: Union[T2, object] = MISSING
        self._complete = threading.Event()
        self._lock = threading.Lock()
        functools.update_wrapper(self, method) # We cannot supply slots for this object.

    @property
    def method(self) -> Callable[P2, T2]:
        return self._method

    @property
    def thread(self) -> Optional[threading.Thread]:
        return self._thread

    @property
    def complete(self) -> bool:
        return self._complete.is_set()

    @property
    def result(self) -> Optional[T2]:
        # None if not complete or value is the MISSING sentinel
        if self._result is MISSING or not self.complete:
            return None
        return self._result  # type: ignore[return-value]

    # internal runner invoked in the worker thread
    def _runner(self, resolve: Resolve[T2], *args: P2.args, **kwargs: P2.kwargs) -> None:
        self._complete.clear()
        try:
            val = self._method(*args, **kwargs)
            # publish to resolve first (so resolves waiting on parental capture will see it)
            resolve._set_value(val)
            with self._lock:
                object.__setattr__(self, "_result", val)
        except BaseException as e:
            resolve._set_exception(e)
            with self._lock:
                object.__setattr__(self, "_result", MISSING)
        finally:
            self._complete.set()

    # start a new background thread and return the Resolve handle
    def threaded_call(self, *args: P2.args, **kwargs: P2.kwargs) -> Resolve[T2]:
        # create the Resolve before starting thread and attach it to self
        res = Resolve[T2](self)
        object.__setattr__(self, "_resolve", res)
        # create thread configured with daemon flag
        self._thread = threading.Thread(target=self._runner, args=(res,)+args, kwargs=kwargs, daemon=self._daemon)
        self._thread.start()
        return res

    def __call__(self, *args: P2.args, **kwargs: P2.kwargs) -> Resolve[T2]:
        return self.threaded_call(*args, **kwargs)

def threaded(func: Optional[Callable[P2, T2]] = None, /, daemon: bool = True) -> Union[ThreadedMethod[P2, T2], Callable[[Callable[P2, T2]], ThreadedMethod[P2, T2]]]:
    """
    Create a new threaded method of the given function.
    """
    def decorator(f: Callable[P2, T2]) -> ThreadedMethod[P2, T2]:
        return ThreadedMethod(f, daemon=daemon)
    if func:
        return decorator(func)  # type: ignore[return-value]
    return decorator

def new_thread_resolve(func: ThreadedMethod[P2, T2]) -> Resolve[T2]:
    """
    Create a new thread resolve with the given parenting thread method.
    This will not automatically record the result, unless you call `start_recording`.
    """
    return Resolve[T2](func)

def is_threaded(func: Union[Callable[P2, T2], ThreadedMethod[P2, T2]]) -> bool:
    # handle either instances or types
    return isinstance(func, ThreadedMethod)

class Wrapper:
    __slots__ = ("_creation", "_frozen")

    def __init__(self):
        object.__setattr__(self, "_creation", time.monotonic())
        object.__setattr__(self, "_frozen", False)

    @property
    def creation(self) -> float:
        return self._creation

    @property
    def alive_time(self) -> float:
        return time.monotonic() - self._creation

    @property
    def frozen(self) -> bool:
        return self._frozen

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError(f"The '{type(self).__name__}' instance is frozen")
        super().__setattr__(name, value)

def wrap(cls: Optional[Type[T]] = None, /, wrapper: Type[Wrapper] = Wrapper, **kwargs: Any) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """
    Decorator that returns a subclass of the specified wrapper. The wrapper must be inheriting the wrapper
    """

    if not is_wrapped(wrapper):
        raise TypeError("The wrapper must be inheriting, or be the exact Wrapper.")

    def decorator(c: Type[T]) -> Type[T]:
        wrapped = type(c.__name__, (wrapper,) + c.__bases__, dict(c.__dict__), **kwargs)

        # the wrapper __init__: initialize the Wrapper base synchronously, then kick off background init
        def new_init(self, *a: Any, **k: Any) -> None:
            wrapper.__init__(self)
            c.__init__(self, *a, **k)

        wrapped.__init__ = new_init
        return wrapped

    if cls:
        return decorator(cls)
    return decorator

def is_wrapped(obj_or_cls: Union[Type[T], T]) -> bool:
    # handle either instances or types
    cls = obj_or_cls if isinstance(obj_or_cls, type) else type(obj_or_cls)
    return issubclass(cls, Wrapper)
