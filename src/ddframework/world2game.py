from pygame.math import remap
from pygame.math import Vector2 as vec2
from pygame.rect import FRect
from pygame.typing import Point, RectLike


class World2Game:
    def __init__(self, wrect: RectLike, grect: RectLike) -> None:
        self.wrect = FRect(wrect)
        self.grect = FRect(grect)

    def w2g(self, p: Point) -> vec2:
        return vec2(remap(self.wrect.left, self.wrect.right, self.grect.left, self.grect.right, p[0]),
                    remap(self.wrect.top, self.wrect.bottom, self.grect.top, self.grect.bottom, p[1]))

    def g2w(self, p: Point) -> vec2:
        return vec2(remap(self.grect.left, self.grect.right, self.wrect.left, self.wrect.right, p[0]),
                    remap(self.grect.top, self.grect.bottom, self.wrect.top, self.wrect.bottom, p[1]))
