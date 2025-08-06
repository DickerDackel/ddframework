from typing import NamedTuple, Optional, Type, TypeVar
from collections.abc import Sequence

from pgcooldown import LerpThing


T = TypeVar("T")


class SequenceConfig(NamedTuple):
    items: Sequence[object]
    duration: float


class AutoSequencer[T]:
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

    def __init__(self, repeat: int = 1) -> None:
        self.repeat = repeat

    def __set_name__(self, obj: object, name: str) -> None:
        self.attrib = f'__AutoSequencer_{name}'

    def __set__(self, obj: T, val: T | SequenceConfig) -> None:
        if isinstance(val, Sequence):
            items, duration = val
        else:
            items = (val,)
            duration = 1

        lt = LerpThing(0, len(items), duration, repeat=self.repeat)
        obj.__setattr__(self.attrib, (items, lt))

    def __get__(self, obj: T | None, objtype: Type[T]) -> SequenceConfig | T | None:
        if obj is None: return self

        sequence, lt = obj.__getattribute__(self.attrib)

        if lt.finished():
            return None
        else:
            return sequence[int(lt())]


class AutoSequence:
    item: object = AutoSequencer()

    def __init__(self, config: SequenceConfig | tuple[Sequence[object], float], repeat: int = 1) -> None:
        self.item = config
