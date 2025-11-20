from typing import (
    Set, List, Dict, ParamSpec, TypeVar, Type, Generic, Callable, Union, Optional, Any
)
import inspect as _inspect
import threading
import time
import sys

P = ParamSpec("P")
T = TypeVar("T")

class Environment:
    _Environment__start: float
    _Environment__methods: Set["Method"]
    _Environment__lock: threading.RLock
    __slots__ = ("_Environment__start", "_Environment__methods", "_Environment__lock")

    def __init__(self) -> None:
        object.__setattr__(self, "_Environment__start", time.perf_counter())
        object.__setattr__(self, "_Environment__methods", set())
        object.__setattr__(self, "_Environment__lock", threading.RLock())

    @property
    def start(self) -> float:
        return self._Environment__start
    
    @property
    def total_calls(self) -> int:
        with self._Environment__lock:
            return sum(method.total_calls for method in self._Environment__methods)
    
    @property
    def total_duration(self) -> float:
        with self._Environment__lock:
            with self._Environment__lock:
                vals = [m.min_duration for m in self._Environment__methods if m.min_duration is not None]
            return sum(vals) if vals else 0.0
        
    @property
    def min_duration(self) -> float:
        with self._Environment__lock:
            with self._Environment__lock:
                vals = [m.min_duration for m in self._Environment__methods if m.min_duration is not None]
            return min(vals) if vals else 0.0
    
    @property
    def max_duration(self) -> float:
        with self._Environment__lock:
            with self._Environment__lock:
                vals = [m.min_duration for m in self._Environment__methods if m.min_duration is not None]
            return min(vals) if vals else 0.0
    
    @property
    def avg_duration(self) -> float:
        with self._Environment__lock:
            with self._Environment__lock:
                vals = [m.min_duration for m in self._Environment__methods if m.min_duration is not None]
            return sum(vals) / len(vals) if vals else 0.0
    
    @property
    def history(self) -> List["Resolve"]:
        with self._Environment__lock:
            resolves = []
            for method in self._Environment__methods:
                resolves.extend(method.history)
            return sorted(resolves, key=lambda m: m.start)

    @property
    def methods(self) -> List["Method"]:
        with self._Environment__lock:
            return list(self._Environment__methods)
    
    def add(self, method: "Method") -> None:
        with self._Environment__lock:
            self._Environment__methods.add(method)
    
    def remove(self, method: "Method") -> None:
        with self._Environment__lock:
            self._Environment__methods.remove(method)
    
    def clear(self) -> None:
        with self._Environment__lock:
            self._Environment__methods.clear()
    
    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Environment objects are immutable")

_GLOBAL_ENVIRONMENT = Environment()

class Resolve:
    _Resolve__method: "Method"
    _Resolve__start: float
    _Resolve__end: float
    _Resolve__result: Any
    _Resolve__exception: Optional[Exception]
    __slots__ = ("_Resolve__method", "_Resolve__start", "_Resolve__end", "_Resolve__result", "_Resolve__exception")

    def __init__(self, method: "Method", start: float, end: float, result: Any, exception: Optional[Exception] = None) -> None:
        object.__setattr__(self, "_Resolve__method", method)
        object.__setattr__(self, "_Resolve__start", start)
        object.__setattr__(self, "_Resolve__end", end)
        object.__setattr__(self, "_Resolve__result", result)
        object.__setattr__(self, "_Resolve__exception", exception)
    
    @property
    def method(self) -> "Method":
        return self._Resolve__method
    
    @property
    def start(self) -> float:
        return self._Resolve__start
    
    @property
    def end(self) -> float:
        return self._Resolve__end

    @property
    def duration(self) -> float:
        return self._Resolve__end - self._Resolve__start
    
    @property
    def result(self) -> Any:
        return self._Resolve__result
    
    @property
    def exception(self) -> Optional[Exception]:
        return self._Resolve__exception
    
    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Resolve objects are immutable")
    
    def __repr__(self) -> str:
        return f"<Resolve func={self.method.name!r} duration={self.duration:.6f}s exception={bool(self.exception)}>"

class Method(Generic[P, T], Callable):
    """
    Wraps a callable and records timings / exceptions.

    - Merges default args/kwargs with call-time args in an intuitive way.
    - Thread-safe.
    - Preserves tracebacks on exceptions.
    - Supports async callables (returns a coroutine you can `await`).
    """

    _Method__method: Callable[P, T]
    _Method__created_at: float
    _Method__last_resolve: Optional[Resolve]
    _Method__history: List[Resolve]
    _Method__lock: threading.Lock
    _Method__total_duration: float
    _Method__total_calls: int
    _Method__default_args: List[Any]
    _Method__default_kwargs: Dict[str, Any]
    __slots__ = ("_Method__method", "_Method__created_at", "_Method__last_resolve", "_Method__history", "_Method__lock", "_Method__total_duration", "_Method__total_calls", "_Method__default_args", "_Method__default_kwargs")

    def __init__(self, method: Callable[P, T], *args: Any, **kwargs: Any) -> None:
        if not callable(method):
            raise TypeError("Function requires a callable")
        self._Method__method = method
        self._Method__created_at = time.perf_counter()
        self._Method__last_resolve = None
        self._Method__history = []
        self._Method__lock = threading.Lock()
        self._Method__total_calls = 0
        self._Method__total_duration = 0.0
        self._Method__default_args = list(args)
        self._Method__default_kwargs = dict(kwargs)
        _GLOBAL_ENVIRONMENT.add(self)
    
    @property
    def name(self) -> Optional[str]:
        return getattr(self._Method__method, "__name__", None)
    
    @property
    def doc(self) -> Optional[str]:
        return getattr(self._Method__method, "__doc__", None)
    
    @property
    def owner(self) -> Optional[Type]:
        obj = self._Method__method

        # Case 1: bound method
        if _inspect.ismethod(obj):
            return obj.__self__.__class__
        
        # Case 2: callable class instance
        if hasattr(obj, "__call__") and not _inspect.isfunction(obj):
            typ = obj.__class__
            # don't treat function objects as callable instances
            if typ is not type(lambda: None):
                return typ
        
        # Case 3: function defined inside a class (unbound method)
        if _inspect.isfunction(obj):
            qual = obj.__qualname__
            if "." in qual:
                cls_name = qual.split(".")[0]
                module = _inspect.getmodule(obj)
                if hasattr(module, cls_name):
                    cls = getattr(module, cls_name)
                    if isinstance(cls, type):
                        return cls
        
        return None
    
    @property
    def created_at(self) -> float:
        return self._Method__created_at
    
    @property
    def resolve(self) -> Optional[Resolve]:
        return self._Method__last_resolve
    
    @property
    def history(self) -> List[Resolve]:
        with self._Method__lock:
            return list(self._Method__history)
    
    @property
    def avg_duration(self) -> float:
        with self._Method__lock:
            if self._Method__total_calls == 0:
                return 0.0
            return self._Method__total_duration / self._Method__total_calls

    @property
    def min_duration(self) -> float:
        with self._Method__lock:
            if not self._Method__history:
                return 0.0
            return min(r.duration for r in self._Method__history)

    @property
    def max_duration(self) -> float:
        with self._Method__lock:
            if not self._Method__history:
                return 0.0
            return max(r.duration for r in self._Method__history)

    @property
    def calls_per_second(self) -> float:
        elapsed = time.perf_counter() - self._Method__created_at
        if elapsed <= 0:
            return float("inf") if self._Method__total_calls > 0 else 0.0
        with self._Method__lock:
            return self._Method__total_calls / elapsed
    
    @property
    def total_duration(self) -> float:
        with self._Method__lock:
            return self._Method__total_duration
    
    @property
    def total_calls(self) -> int:
        with self._Method__lock:
            return self._Method__total_calls
    
    def reset(self) -> None:
        with self._Method__lock:
            self._Method__last_resolve = None
            self._Method__total_duration = 0.0
            self._Method__total_calls = 0
            self._Method__history.clear()
            self._Method__created_at = time.perf_counter()
    
    def get_method(self) -> Callable[P, T]:
        return self._Method__method
    
    def _record(self, resolve: Resolve) -> None:
        with self._Method__lock:
            self._Method__last_resolve = resolve
            self._Method__total_duration += resolve.duration
            self._Method__total_calls += 1
            self._Method__history.append(resolve)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if not args and not kwargs:
            args = list(self._Method__default_args)
            kwargs = dict(self._Method__default_kwargs)
        owner = self.owner
        args = ([owner] if owner is not None else []) + list(args)
        kwargs = dict(kwargs)
        start = time.perf_counter()
        try:
            res = self._Method__method(*args, **kwargs)
            self._Method__method.__class__
        except Exception as e:
            res = None
            end = time.perf_counter()
            resolve = Resolve(self, start, end, res, sys.exc_info())
            self._record(resolve)
            raise
        end = time.perf_counter()
        resolve = Resolve(self, start, end, res, None)
        self._record(resolve)
        return res

class GlobalEnvironment:
    def reset(self) -> None: # _GLOBAL_ENVIRONMENT is safe, since this isn't provided in the .pyi
        global _GLOBAL_ENVIRONMENT
        del _GLOBAL_ENVIRONMENT
        _GLOBAL_ENVIRONMENT = Environment()
    def __call__(self) -> Environment:
        return _GLOBAL_ENVIRONMENT
GlobalEnvironment = GlobalEnvironment()

DecoratorLike = Callable[[Callable[P, T]], Method[P, T]]

def inspect(func: Optional[Callable[P, T]] = None, /, *args: Any, **kwargs: Any) -> Union[Method[P, T], DecoratorLike]:
    """
    Decorate either a function or a class, to get a 'Method' object.

    Usage:
      @inspect
      def f(...): ...

      or
      f = inspect(func, 1, 2, some_flag=True)

      you can then
      print(f.total_duration) -> "Some long number"

    Call the new, decorated object like normal. It will function just like normal. 
    To access feasable performance considerations and other metadata, you can access 
    the object by dot notation. You will find 'total_duration', 'resolve', 
    'history' and more. These will provide detailed information about that callable. 
    
    This inspection tool was built for functions, but applies to classes the same, as 
    efficiently.

    Provide arguments and keyword arguments, to parse as default. Default arguments 
    are arguments that will replace any parameter if there are none provided when 
    calling the method.

    Does not provide for async methods.

    This renders a class uninheritable and is thus unpractical. Only inspect a class 
    under strict circumstances, such as, if you want the class uninheritable by design. 
    Otherwise, you can inspect the '__init__' function directly. Note that functions 
    with 'self' will function like normal.
    """
    def decorator(func: Callable[P, T]) -> Method[P, T]:
        return Method(func, *args, **kwargs)
    if func: return decorator(func)
    return decorator