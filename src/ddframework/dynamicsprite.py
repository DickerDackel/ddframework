from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Hashable, Type

import pygame._sdl2 as sdl2

from pygame import Vector2 as vec2
from pygame.typing import Point

import pygame


class PRSA:
    """Rotation, Scale, Alpha, Position in one container"""
    pos: vec2
    rotation: float
    scale: float
    alpha: float

    def __init__(self, pos: vec2 | None = None,
                 rotation: float = 0, scale: Sequence[float] | float = 1, alpha: float = 255) -> None:
        self.pos = pos
        self.rotation = rotation
        self.scale = scale
        self.alpha = alpha

    def __iter__(self) -> Iterator[tuple[vec2, float, float, float]]:
        yield self.pos
        yield self.rotation
        yield self.scale
        yield self.alpha

    def __repr__(self) -> str:
        return f'PRSA(pos={self.pos}, rotation={self.rotation}, scale={self.scale}, alpha={self.alpha})'


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
