from dataclasses import dataclass

import pygame._sdl2 as sdl2

from pygame import Vector2 as vec2
from pygame.typing import Point

from ddframework.autosequencer import AutoSequence, AutoSequencer

import pygame


class _TotallyAVec2(vec2):
    """Makes sure the object is guaranteed to be a vec2, even after
    overwriting."""

    def __set_name__(self, obj, name):
        self.attrib = f'__totally_a_vec2_{name}'

    def __set__(self, obj, val):
        if val is None:
            val = (0, 0)

        if isinstance(val, vec2):
            obj.__setattr__(self.attrib, val)
        else:
            obj.__setattr__(self.attrib, vec2(val))

    def __get__(self, obj, parent):
        if obj is None: return self

        return obj.__getattribute__(self.attrib)


@dataclass
class PRSA:
    """Rotation, Scale, Alpha, Position in one container"""

    pos: Point = _TotallyAVec2()
    rotation: float = 0
    scale: float | tuple[float, float] = 1
    alpha: float = 255

    def __iter__(self):
        yield self.pos
        yield self.rotation
        yield self.scale
        yield self.alpha


class SDL2Group(pygame.sprite.Group):
    def draw(self, *args, **kwargs) -> None:
        for sprite in self.sprites():
            sprite.draw()


class SDL2BaseSprite(pygame.sprite.Sprite):
    def __init__(self, prsa, *groups, anchor='center'):
        super().__init__(*groups)
        self.prsa = prsa
        self.anchor = anchor

    def __repr__(self):
        return f'{self.__class__}({self.prsa}, {self.image}, {self.rect})'

    def update(self, dt):
        if hasattr(self, 'rect'):
            setattr(self.rect, self.anchor, self.prsa.pos)

    def draw(self):
        bkp_alpha = self.image.alpha
        self.image.alpha = self.prsa.alpha
        self.image.draw(dstrect=self.rect.scale_by(self.prsa.scale),
                        angle=self.prsa.rotation)
        self.image.alpha = bkp_alpha


class SDL2Sprite(SDL2BaseSprite):
    def __init__(self, prsa, texture, *groups, **kwargs):
        super().__init__(prsa, *groups, **kwargs)
        self.image = texture
        self.rect = texture.get_rect(center=self.prsa.pos)


class SDL2AnimSprite(SDL2BaseSprite):
    image: sdl2.Texture | AutoSequence[sdl2.Texture] = AutoSequencer()
