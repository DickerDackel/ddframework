"""Utilities for automatic traversal/looping over a list of objects.

The Sequencer class provides the core object.  Instantiate it with a list of
objects and a duration, and when `call`ed, it will return an item from that
list depending on the time since the instantiation.

The AutoSequencer is a descriptor class.  This will update a class attribute
without the need of an explicit `call`.
"""

from collections import UserList
from collections.abc import Sequence
from typing import Generator, Generic, Self, Type, TypeVar, overload

from pgcooldown import LerpThing


T = TypeVar("T")
SequenceConfig = tuple[Sequence[T], float]


class AutoSequence(UserList):
    """A class returning an automatically updating item.
    This is just a container for easy use of AutoSequencer
    """

    lt: LerpThing

    def __init__(self, items: Sequence[T],
                 duration: float = 1.0, repeat: int = 1, loops: int = -1) -> None:
        super().__init__(items)

        self.lt = LerpThing(0, len(items), duration, repeat=repeat, loops=loops)
        # Change vt1 on insert/remove

    def __call__(self) -> object:
        if self.lt.finished():
            return None
        else:
            return self.data[int(self.lt())] if self.data else ()

    def __iter__(self) -> Generator[object, None, None]:
        while not self.lt.finished():
            yield self.data[int(self.lt())] if self.data else ()

    def __next__(self) -> object:
        if not self.lt.finished():
            return self.data[int(self.lt())] if self.data else ()
        else:
            raise StopIteration

    def append(self, item: object) -> None:
        super().append(item)

    def insert(self, i: int, item: object) -> None:
        super().insert(item)

    def pop(self, i: int = -1) -> object:
        return self.data.pop(i)

    def remove(self, item: object) -> None:
        super().remove(item)

    def clear(self) -> None:
        self.data.clear()

    def extend(self, other: Sequence[object]) -> None:
        if isinstance(other, UserList):
            self.data.extend(other.data)
        else:
            self.data.extend(other)


class AutoSequencer(Generic[T]):
    """A descriptor class to run a sequence or a cycle over a list of objects.

    Can be used e.g. for sprite animations.::

        class Sprite(pygame.sprite.Sprite):
            image: pygame.surface.Surface = AutoSequence(repeat=True)
            def __init__(self,
                         image_list: list[pygame.surface.Surface,
                         duration: float = 1) -> None:
                super().__init__()
                self.image = (image_list, duration)

        sprite = Sprite(list_of_images, 3):
        current_image = sprite.image  # <-- will change over time

    """

    def __init__(self, repeat: int = 1, loops: int = -1) -> None:
        self.repeat = repeat
        self.loops = loops

    def __set_name__(self, obj: object, name: str) -> None:
        self.attrib = f'__AutoSequencer_{name}'

    def __set__(self, obj: T, val: SequenceConfig) -> None:
        seq = AutoSequence(val[0], val[1], repeat=self.repeat, loops=self.loops)
        obj.__setattr__(self.attrib, seq)

    @overload
    def __get__(self, obj: None, objtype: Type[T]) -> Self: ...

    @overload
    def __get__(self, obj: T, objtype: Type[T]) -> T: ...

    def __get__(self, obj, objtype):
        if obj is None: return self
        return obj.__getattribute__(self.attrib)()

