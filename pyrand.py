"""
Performant, short and easy random extention.
Extends random and uses wrapper to allow both threaded and none threaded 
randomizing, allowing full performance and new capabilities.

This extention also streamlines making randomized objects.
"""

from typing import Iterable, Optional, Union, TypeVar, Generic, Any
from dataclasses import dataclass
import wrapper
import random

T = TypeVar("T")
RandomOrX = Union["Random", "random.Random", int]

@dataclass
class ObjectDef(Generic[T]):
    value: T
    chance: float = 1.0

    def _get_random(self, random_or_x: Optional[RandomOrX] = None) -> random.Random:
        if isinstance(random_or_x, Random):
            _random = random_or_x.object
        elif isinstance(random_or_x, random.Random):
            _random = random_or_x
        else:
            _random = random.Random(random_or_x)
        return _random

    @wrapper.threaded
    def random(definition: "Object", random_or_x: Optional[RandomOrX] = None) -> Union[Any, float]:
        random = definition._get_random(random_or_x)
        value = definition.value
        if isinstance(value, Iterable):
            return random.choice(value)
        elif isinstance(value, (int, float)):
            return random.random() * value
    
    @wrapper.threaded
    def random_int(definition: "Object", random_or_x: Optional[RandomOrX] = None) -> int:
        if not isinstance(definition.value, int):
            raise TypeError("Wrong type when calculating random integer.")
        random = definition._get_random(random_or_x)
        return int(random.random() * definition.value)

class Object(ObjectDef[T]):
    def random(self, random_or_x: Optional[RandomOrX] = None) -> wrapper.Resolve[Union[Any, float]]:
        return ObjectDef.random(self, random_or_x)
    def random_int(self, random_or_x: Optional[RandomOrX] = None) -> wrapper.Resolve[int]:
        return ObjectDef.random_int(self, random_or_x)
    # Copy and conversion functions
    def to_absolute(self) -> "AbsoluteObject":
        return AbsoluteObject(self.value, self.chance)
    def to_threaded(self) -> "Object":
        return Object(self.value, self.chance)

class AbsoluteObject(Object[T]):
    def random(self, random_or_x: Optional[RandomOrX] = None) -> Union[Any, float]:
        return Object.random(self, random_or_x).result()
    def random_int(self, random_or_x: Optional[RandomOrX] = None) -> int:
        return Object.random_int(self, random_or_x).result()

class RandomWrapper(wrapper.Wrapper):
    def __init__(self) -> None:
        super().__init__()

@wrapper.wrap(wrapper=RandomWrapper)
class RandomDef:
    def __init__(self, x: Optional[int] = None) -> None:
        self._random = random.Random(x)
    
    @property
    def object(self) -> random.Random:
        return self._random
    
    @wrapper.threaded
    def random(definition: "Random") -> float:
        return definition._random.random()
    
    @wrapper.threaded
    def randint(definition: "Random", a: int, b: int) -> int:
        return definition._random.randint(a, b)
    
    @wrapper.threaded
    def randobj(definition: "Random", *args: Object, items: Optional[Iterable[Object]] = None) -> Any:
        real = []
        chance = []
        items = list(items or []) + list(args)
        for item in items:
            if item is None:
                continue
            real.append(item.value)
            chance.append(item.chance)
        return definition._random.choices(real, chance)[0]
    
    @wrapper.threaded
    def choice(definition: "Random", *args: Any, items: Optional[Iterable[Any]] = None) -> Any:
        return definition._random.choice(list(items or []) + list(args))

class Random(RandomDef):
    def random(self) -> wrapper.Resolve[float]:
        return RandomDef.random(self)
    
    def randint(self, a: int, b: int) -> wrapper.Resolve[int]:
        return RandomDef.randint(self, a, b)
    
    def randobj(self, *args: Object, items: Optional[Iterable[Object]] = None) -> wrapper.Resolve[Any]:
        return RandomDef.randobj(self, *args, items=items)
    
    def choice(self, *args: Any, items: Optional[Iterable[Any]] = None) -> wrapper.Resolve[Any]:
        return RandomDef.choice(self, *args, items=items)

    @staticmethod
    def prep(item: Any, chance: Optional[float] = None) -> Object:
        return Object(item, chance or 1.0)

    @staticmethod
    def cleanup() -> None:
        wrapper.cleanup()

class AbsoluteRandom(Random):
    def random(self) -> float:
        return Random.random(self).result()
    def randint(self, a: int, b: int) -> int:
        return Random.randint(self, a, b).result()
    def randobj(self, *args: Object, items: Optional[Iterable[Object]] = None) -> Any:
        return Random.randobj(self, *args, items=items).result()
    def choice(self, *args: Any, items: Optional[Iterable[Any]] = None) -> Any:
        return Random.choice(self, *args, items=items).result()