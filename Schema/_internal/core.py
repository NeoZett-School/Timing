from typing import Iterable, Set, Tuple, List, Dict, Optional, Generator, Any
from .utils import is_leap, month_count
import time as _time

###########################
# Exports:                #
# ----------------------- #
# Time, Date, DateTime,  #
# Clock                   #
###########################

# You can create a time object, or date for specific timing.
# Otherwise, you can use the clock for real-time scheduling.

# Quick reminder. This library isn't built around calculations and time schematics, 
# but rather around saving time aspects simply as a cache or storage. For real applications, 
# we would suggest overthinking if they should use a library for extensive time 
# operations (like datetime), or simply store a point in time. Becaue, then this library becomes 
# useful.

# We use the pyi for the public interface. Since this system is centered around clean and 
# powerful code, rather than plain practiality during coding, we use dubble underscore, 
# which also provides extensibility if someone were to extend onto this system later on. 
# In fact, this scenario is one of the highest priorised implementations: to keep it extensive 
# for continuation and a clean workspace to build another powerful time protocol, or 
# something alike.

class Time:
    """
    The time lets you easily keep track of time.
    """
    _Time__seconds: float
    _Time__frozen: bool
    __slots__ = ("_Time__seconds", "_Time__frozen")

    def __init__(self, seconds: float) -> None:
        self._Time__frozen = False
        self._Time__seconds = seconds
    
    @classmethod
    def from_units(cls, hours: int = 0, minutes: int = 0, seconds: float = 0.0) -> "Time":
        return cls(hours * 3600 + minutes * 60 + seconds)
    
    @classmethod
    def from_timestamp(cls, time: float) -> "Time":
        y, m, d, hh, mm, ss, weekday, jday, dst = _time.localtime(time)
        return cls(hh * 3600 + mm * 60 + ss)
    
    @classmethod
    def now(cls) -> "Time":
        return Time.from_timestamp(_time.time())
    
    @property
    def days(self) -> float:
        return self._Time__seconds / 86400
    
    @days.setter
    def days(self, value: float) -> None:
        if not self._Time__frozen:
            self._Time__seconds = value * 86400
    
    @property
    def hours(self) -> float:
        return self._Time__seconds / 3600
    
    @hours.setter
    def hours(self, value: float) -> None:
        if not self._Time__frozen:
            self._Time__seconds = value * 3600
    
    @property
    def minutes(self) -> float:
        return self._Time__seconds / 60
    
    @minutes.setter
    def minutes(self, value: float) -> None:
        if not self._Time__frozen:
            self._Time__seconds = value * 60
    
    @property
    def seconds(self) -> float:
        return self._Time__seconds
    
    @seconds.setter
    def seconds(self, value: float) -> None:
        if not self._Time__frozen:
            self._Time__seconds = value
    
    @property
    def milliseconds(self) -> float:
        return self._Time__seconds * 1000
    
    @milliseconds.setter
    def milliseconds(self, value: float) -> None:
        if not self._Time__frozen:
            self._Time__seconds = value / 1000
    
    @property
    def microseconds(self) -> float:
        return self._Time__seconds * 1000_000
    
    @microseconds.setter
    def microseconds(self, value: float) -> None:
        if not self._Time__frozen:
            self._Time__seconds = value / 1000_000
    
    @property
    def nanoseconds(self) -> float:
        return self._Time__seconds * 1000_000_000
    
    @nanoseconds.setter
    def nanoseconds(self, value: float) -> None:
        if not self._Time__frozen:
            self._Time__seconds = value / 1000_000_000
    
    @property
    def frozen(self) -> bool:
        return self._Time__frozen
    
    def to_units(self) -> Tuple[int, int, float]:
        """
        Get hours, minutes and seconds in that order.
        """
        minutes, seconds = divmod(self._Time__seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return int(hours), int(minutes), seconds
    
    def freeze(self) -> None:
        self._Time__frozen = True
    
    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_Time__frozen") and self._Time__frozen:
            raise AttributeError("Cannot set attribute to a Time object that is frozen.")
        super().__setattr__(name, value)
    
    def __repr__(self) -> str:
        return f"Time({self._Time__seconds})"
    
    def __str__(self) -> str:
        return f"{self._Time__seconds}"
    
    def __round__(self, ndigits: Optional[int] = None) -> float: 
        return round(self._Time__seconds, ndigits)
    
    def __int__(self) -> int:
        return int(self._Time__seconds)
    
    def __float__(self) -> float:
        return float(self._Time__seconds)
    
    def __hash__(self) -> int:
        return id(self)


class Date:
    """
    The date lets you keep track of different days.
    It is optimal for simple task and recognition of time, not heavy time operations like datetime.date.
    """
    _Date__year: int
    _Date__month: int
    _Date__day: int
    _Date__frozen: bool
    __slots__ = ("_Date__year", "_Date__month", "_Date__day", "_Date__frozen")

    def __init__(self, year: int, month: int, day: int) -> None:
        # We trust the user with arbitrary inputs.
        self._Date__frozen = False
        self._Date__year = year
        self._Date__month = month
        self._Date__day = day
    
    @classmethod
    def from_timestamp(cls, time: float) -> "Date":
        y, m, d, hh, mm, ss, weekday, jday, dst = _time.localtime(time)
        return cls(y, m, d)
    
    @classmethod
    def today(cls) -> "Date":
        return cls.from_timestamp(_time.time())

    @property
    def year(self) -> int:
        return self._Date__year
    
    @year.setter
    def year(self, value: int) -> None:
        if not self._Date__frozen:
            self._Date__year = value
    
    @property
    def month(self) -> int:
        return self._Date__month
    
    @month.setter
    def month(self, value: int) -> None:
        if not self._Date__frozen:
            self._Date__month = value
    
    @property
    def day(self) -> int:
        return self._Date__day
    
    @day.setter
    def day(self, value: int) -> None:
        if not self._Date__frozen:
            self._Date__day = value
    
    @property
    def frozen(self) -> bool:
        return self._Date__frozen
    
    def freeze(self) -> None:
        self._Date__frozen = True
    
    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_Date__frozen") and self._Date__frozen:
            raise AttributeError("Cannot set attribute to a Date object that is frozen.")
        super().__setattr__(name, value)
    
    def __repr__(self) -> str:
        return f"Date(year={self.year} month={self.month} day={self.day})"
    
    __str__ = __repr__
    
    def __hash__(self) -> int:
        return id(self)


class DateTime:
    _DateTime__date: Date
    _DateTime__time: Time
    __slots__ = ("_DateTime__date", "_DateTime__time")

    def __init__(self, date: Date, time: Time) -> None:
        self._DateTime__date = date
        self._DateTime__time = time
    
    @classmethod
    def now(cls) -> "DateTime":
        return DateTime(Date.today(), Time.now())
    
    @property
    def date(self) -> Date:
        return self._DateTime__date
    
    @property
    def time(self) -> Time:
        return self._DateTime__time
    
    def __repr__(self) -> str:
        return f"DateTime(date={repr(self.date)} time={repr(self.time)})"
    
    __str__ = __repr__
    
    def __hash__(self) -> int:
        return id(self)


class Event:
    """
    An event will have a date and time for when it will be variable.
    """
    _Event__name: str
    _Event__date: "Day.Date"
    _Event__time: Time
    _Event__due: "Event.Due"
    __slots__ = ("_Event__name", "_Event__date", "_Event__time", "_Event__due")

    class Due:
        _Due__date: Date
        _Due__time: Time
        __slots__ = ("_Due__date", "_Due__time")

        def __init__(self, date: Date, time: Time) -> None:
            self._Due__date = date
            self._Due__time = time
        
        @property
        def date(self) -> Date:
            return self._Due__date
        
        @property
        def time(self) -> Time:
            return self._Due__time
        
        def __repr__(self) -> str:
            return f"Event.Due(date={repr(self.date)} time={repr(self.time)})"
        
        __str__ = __repr__
        
        def __hash__(self) -> int:
            return id(self)

    def __init__(self, name: str, date: "Day.Date", time: Time, due: Optional["Event.Due"] = None) -> None:
        self._Event__name = name
        self._Event__date = date
        self._Event__time = time
        self._Event__due = due
    
    @property
    def name(self) -> str:
        return self._Event__name
    
    @property
    def date(self) -> "Day.Date":
        return self._Event__date
    
    @property
    def time(self) -> Time:
        return self._Event__time
    
    @property
    def due(self) -> Optional["Event.Due"]:
        return self._Event__due
    
    @property
    def duration(self) -> float:
        """The duration in seconds."""
        return self.due.time.seconds - self.time.seconds if self.due else 0
    
    def __repr__(self) -> str:
        return f"Event(name={self.name} date={repr(self.date)} time={repr(self.time)} due={repr(self.due)})"
    
    __str__ = __repr__
    
    def __hash__(self) -> int:
        return id(self)


class Day:
    """
    Name your day. The day will be filled with events.
    """
    _Day__name: str
    _Day__year: int
    _Day__month: int
    _Day__day: int
    _Day__week: Optional["Week"]
    _Day__date: "Day.Date"
    _Day__events: Set[Event]
    __slots__ = ("_Day__name", "_Day__year", "_Day__month", "_Day__day", "_Day__week", "_Day__date", "_Day__events")

    class Date(Date):
        _Date__day_object: "Day"
        __slots__ = ("_Date__day_object", "_Date__year", "_Date__month", "_Date__day", "_Date__frozen")

        def __init__(self, year: int, month: int, day: int, day_object: "Day") -> None:
            super().__init__(year, month, day)
            self._Date__day_object = day_object
        
        def new_event(self, name: str, time: Time, due: Optional[Event.Due] = None) -> Event:
            return Event(name, self, time, due)
        
        def to_date(self) -> Date:
            """Translate the Day.Date object into a clean Date object instead."""
            return Date(self.year, self.month, self.day)
        
        @property
        def day_object(self) -> "Day":
            return self._Date__day_object
        
        def __hash__(self) -> int:
            return id(self)

    def __init__(self, name: str, year: int, month: int, day: int, week: Optional["Week"]) -> None:
        self._Day__name = name
        self._Day__year = year
        self._Day__month = month
        self._Day__day = day
        self._Day__week = week
        self._Day__date = Day.Date(year, month, day, self)
        self._Day__events = set()
    
    @property
    def name(self) -> str:
        return self._Day__name
    
    @property
    def year(self) -> int:
        return self._Day__year
    
    @property
    def month(self) -> int:
        return self._Day__month
    
    @property
    def day(self) -> int:
        return self._Day__day
    
    @property
    def week(self) -> Optional["Week"]:
        return self._Day__week
    
    @property
    def date(self) -> "Day.Date":
        return self._Day__date
    
    @property
    def events(self) -> List[Event]:
        return list(self._Day__events)
    
    def add(self, event: Event) -> None:
        self._Day__events.add(event)
    
    def remove(self, event: Event) -> None:
        self._Day__events.remove(event)
    
    def clear(self) -> None:
        self._Day__events.clear()
    
    def new_event(self, name: str, date: "Day.Date", time: Time, due: Optional[Event.Due] = None) -> Event:
        event = date.new_event(name, time, due)
        self.add(event)
        return event
    
    def iterate(self) -> Generator[Event, Any, None]:
        yield from self._Day__events
    
    def __iter__(self) -> Iterable[Event]:
        return iter(self._Day__events)
    
    def __repr__(self) -> str:
        return f"Day(year={self.year} month={self.month} day={self.day})"
    
    __str__ = __repr__
    
    def __hash__(self) -> int:
        return id(self)


class Week:
    """
    Give the week a number. A week will be filled of days.
    """
    _Week__number: int
    _Week__year: int
    _Week__month: int
    _Week__days: Set[Day]
    _Week__month_object: Optional["Month"]
    __slots__ = ("_Week__number", "_Week__year", "_Week__month", "_Week__days", "_Week__month_object")

    def __init__(self, number: int, year: int, month: int, days: Optional[List[Day]] = None, month_object: Optional["Month"] = None) -> None:
        self._Week__number = number
        self._Week__year = year
        self._Week__month = month
        self._Week__days = set(days or [])
        self._Week__month_object = month_object
    
    @property
    def month_object(self) -> Optional["Month"]:
        return self._Week__month_object
    
    @property
    def number(self) -> int:
        return self._Week__number

    @property
    def year(self) -> int:
        return self._Week__year
    
    @property
    def month(self) -> int:
        return self._Week__month
    
    @property
    def days(self) -> List[Day]:
        return list(self._Week__days)
    
    def add(self, day: Day) -> None:
        self._Week__days.add(day)
    
    def remove(self, day: Day) -> None:
        self._Week__days.remove(day)
    
    def clear(self) -> None:
        self._Week__days.clear()
    
    def new_day(self, name: str, day: int) -> Day:
        day = Day(name, self._Week__year, self._Week__month, day, self)
        self.add(day)
        return day
    
    def iterate(self) -> Generator[Day, Any, None]:
        yield from self._Week__days
    
    def to_dict_name(self) -> Dict[str, Day]:
        return {day.name: day for day in self._Week__days}
    
    def to_dict_day(self) -> Dict[int, Day]:
        return {day.day: day for day in self._Week__days}
    
    def __iter__(self) -> Iterable[Day]:
        return iter(self._Week__days)
    
    def __hash__(self) -> int:
        return id(self)


class Month:
    """
    Name your month. The month will contain weeks.
    """
    _Month__name: str
    _Month__year: int
    _Month__month: int
    _Month__weeks: Set[Week]
    _Month__year_object: Optional["Year"]
    __slots__ = ("_Month__name", "_Month__year", "_Month__month", "_Month__weeks", "_Month__year_object")
    
    def __init__(self, name: str, year: int, month: int, year_object: Optional["Year"] = None) -> None:
        self._Month__name = name
        self._Month__year = year
        self._Month__month = month
        self._Month__weeks = set()
        self._Month__year_object = year_object
    
    @property
    def supposed_count(self) -> Tuple[int, int]:
        """Return (first_weekday, number_of_days) for the given month."""
        return month_count(self._Month__year, self._Month__month)
    
    @property
    def year_object(self) -> Optional["Year"]:
        return self._Month__year_object
    
    @property
    def name(self) -> str:
        return self._Month__name

    @property
    def year(self) -> int:
        return self._Month__year
    
    @property
    def month(self) -> int:
        return self._Month__month
    
    @property
    def weeks(self) -> List[Week]:
        return list(self._Month__weeks)
    
    def add(self, week: Week) -> None:
        self._Month__weeks.add(week)
    
    def remove(self, week: Week) -> None:
        self._Month__weeks.remove(week)
    
    def clear(self) -> None:
        self._Month__weeks.clear()
    
    def new_week(self, number: int, days: Optional[List[Day]] = None) -> Week:
        week = Week(number, self._Month__year, self._Month__month, days, self)
        self.add(week)
        return week
    
    def iterate(self) -> Generator[Week, Any, None]:
        yield from self._Month__weeks
    
    def __iter__(self) -> Iterable[Week]:
        return iter(self._Month__weeks)
    
    def __hash__(self) -> int:
        return id(self)


class Year:
    """
    A year will contain different months.
    """
    _Year__year: int
    _Year__months: Set[Month]
    __slots__ = ("_Year__year", "_Year__months")

    def __init__(self, year: int, months: Optional[List[Month]] = None) -> None:
        self._Year__year = year
        self._Year__months = set(months or [])
    
    @property
    def is_leap(self) -> bool:
        return is_leap(self._Year__year)
    
    @property
    def year(self) -> int:
        return self._Year__year
    
    @property
    def months(self) -> List[Month]:
        return list(self._Year__months)
    
    def add(self, month: Month) -> None:
        self._Year__months.add(month)
    
    def remove(self, month: Month) -> None:
        self._Year__months.remove(month)
    
    def clear(self) -> None:
        self._Year__months.clear()
    
    def new_month(self, name: str, month: int) -> Month:
        month = Month(name, self._Year__year, month, self)
        self.add(month)
        return month
    
    def iterate(self) -> Generator[Month, Any, None]:
        yield from self._Year__months
    
    def to_dict_name(self) -> Dict[str, Month]:
        return {month.name: month for month in self._Year__months}
    
    def to_dict_month(self) -> Dict[int, Month]:
        return {month.month: month for month in self._Year__months}
    
    def __iter__(self) -> Iterable[Month]:
        return iter(self._Year__months)
    
    def __hash__(self) -> int:
        return id(self)


class Clock:
    """
    A clock provides all key features to creating your own schema or other time-dependent systems.
    """

    _Clock__start: float
    __slots__ = ("_Clock__start",)

    def __init__(self, start: Optional[float] = None) -> None:
        self._Clock__start = start or _time.monotonic()
    
    @property
    def start_time(self) -> float:
        """The start time used."""
        return self._Clock__start
    
    @property
    def day(self) -> int:
        """Day counter."""
        now = self.now()
        return int(now / 86400)

    @property
    def seconds(self) -> float:
        """Seconds into the day."""
        now = self.now()
        return now - int(now / 86400)
    
    def now(self) -> float:
        """
        Monotonic current time. Since this object was created, or the start time specified.
        """
        return _time.monotonic() - self._Clock__start
    
    @staticmethod
    def today() -> Date:
        return Date.today()
    
    @staticmethod
    def real_time() -> float:
        """
        Return the current time in seconds since the Epoch. 
        Fractions of a second may be present if the system clock provides them.
        """
        return _time.time()

    @staticmethod
    def new_time(seconds: float) -> Time:
        """
        Create new time object.
        """
        return Time(seconds)
        
    @staticmethod
    def due_date(date: Date, time: Time) -> Event.Due:
        """
        Create a new due time.
        """
        return Event.Due(date, time)
    
    @staticmethod
    def create_year(year: int, months: Optional[List[Month]] = None) -> Year:
        """
        Start creating your schedule.
        Begin at the year, and build your way up to your prefered scheduling.
        """
        return Year(year, months)
    
    def __hash__(self) -> int:
        return id(self)