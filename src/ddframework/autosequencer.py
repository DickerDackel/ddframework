from typing import NamedTuple, Optional, Type, TypeVar
from collections.abc import Sequence

from pgcooldown import LerpThing


T = TypeVar("T")


class AutoSequence(NamedTuple):
    items: Sequence[object]
    delay: float


class AutoSequencer[T]:
    """A descriptor class to run a sequence or a cycle over a list of objects.

    Can be used e.g. for sprite animations.::

        class Sprite(pygame.sprite.Sprite):
            image: pygame.surface.Surface = AutoSequence(repeat=True)
            def __init__(self,
                         image_list: list[pygame.surface.Surface,
                         delay: float = 1) -> None:
                super().__init__()
                self.image = (image_list, delay)

        sprite = Sprite(list_of_images, 3):
        current_image = sprite.image  # <-- will change over time

    """

    def __init__(self, repeat=1):
        self.repeat = repeat

    def __set_name__(self, obj: object, name: str):
        self.attrib = f'__AutoSequencer_{name}'

    def __set__(self, obj: T, val: T | AutoSequence):
        if isinstance(val, Sequence):
            items, delay = val
        else:
            items = (val,)
            delay = 1

        lt = LerpThing(0, len(items), delay, repeat=self.repeat)
        obj.__setattr__(self.attrib, (items, lt))

    def __get__(self, obj: Optional[T], objtype: Type[T]) -> AutoSequence | T | None:
        if obj is None: return self

        sequence, lt = obj.__getattribute__(self.attrib)

        if lt.finished():
            return None
        else:
            return sequence[int(lt())]
