from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Hashable, Type

import pygame._sdl2 as sdl2

from pygame import Vector2 as vec2
from pygame.typing import Point

from ddframework.autosequencer import AutoSequence, AutoSequencer

import pygame


class _TotallyAVec2(vec2):
    """Makes sure the object is guaranteed to be a vec2, even after
    overwriting."""

    def __set_name__(self, obj: object, name: str) -> None:
        self.attrib = f'__totally_a_vec2_{name}'

    # type hint for val stolen from pygame-ce's math.pyi
    # def __set__(self, obj: vec2, val: str | float | Sequence[float] | vec2) -> None:
    def __set__(self, obj: vec2, val: vec2) -> None:
        if val is None:
            val = (0, 0)

        if isinstance(val, vec2):
            obj.__setattr__(self.attrib, val)
        else:
            obj.__setattr__(self.attrib, vec2(val))

    def __get__(self, obj: vec2 | None, objtype: Type[vec2]) -> vec2:
        if obj is None: return self

        return obj.__getattribute__(self.attrib)


class PRSA:
    """Rotation, Scale, Alpha, Position in one container"""

    pos: vec2 = _TotallyAVec2()

    def __init__(self, pos: vec2 | None = None,
                 rotation: float = 0, scale: float = 1, alpha: float = 255) -> None:
        self.pos = pos
        self.rotation = rotation
        self.scale = scale
        self.alpha = alpha

    def __iter__(self) -> Iterator[tuple[vec2, float, float, float]]:
        yield self.pos
        yield self.rotation
        yield self.scale
        yield self.alpha


class SDL2Group(pygame.sprite.Group):
    def draw(self, *args: tuple[object], **kwargs: dict[str, object]) -> None:
        for sprite in self.sprites():
            sprite.draw(*args, **kwargs)


class SDL2BaseSprite(pygame.sprite.Sprite):
    def __init__(self, prsa: PRSA, *groups: pygame.sprite.Group,
                 anchor: str = 'center') -> None:
        super().__init__(*groups)
        self.prsa = prsa
        self.anchor = anchor

    def __repr__(self) -> str:
        return f'{self.__class__}({self.prsa}, {self.image}, {self.rect})'

    def update(self, dt: float) -> None:
        if hasattr(self, 'rect'):
            setattr(self.rect, self.anchor, self.prsa.pos)

    def draw(self) -> None:
        bkp_alpha = self.image.alpha
        self.image.alpha = self.prsa.alpha
        self.image.draw(dstrect=self.rect.scale_by(self.prsa.scale),
                        angle=self.prsa.rotation)
        self.image.alpha = bkp_alpha


class SDL2Sprite(SDL2BaseSprite):
    def __init__(self, prsa: PRSA, texture: sdl2.Texture,
                 *groups: list[pygame.sprite.Group],
                 **kwargs: dict[Hashable, object]) -> None:
        super().__init__(prsa, *groups, **kwargs)
        self.image = texture
        self.rect = texture.get_rect(center=self.prsa.pos)


class SDL2AnimSprite(SDL2BaseSprite):
    image: sdl2.Texture | AutoSequence[sdl2.Texture] = AutoSequencer()
