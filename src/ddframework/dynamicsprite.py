import ddframework.cache as C
import pygame

from glm import vec2


class RSAP:
    def __init__(self,
                 angle: float = 0,
                 scale: float = 1,
                 alpha: int = 255,
                 pos: vec2|tuple[float, float] = (0, 0)) -> None:
        self.angle = angle
        self.scale = scale
        self.alpha = alpha
        self._pos = pos if isinstance(pos, vec2) else vec2(pos)

    def __iter__(self):
        yield self.angle
        yield self.scale
        yield self.alpha

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        self._pos = vec2(p)


class DynamicSprite(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface | str,
                 *groups: pygame.sprite.Group,
                 rsap: RSAP = None,
                 anchor: str = 'center') -> None:
        super().__init__(*groups)

        self.rsap = RSAP() if rsap is None else rsap
        self.anchor = anchor

        if isinstance(image, str):
            self.tag = image
            self.image = C.fetch(image, *self.rsap)
        else:
            self.image = image
            self.tag = None

        self.rect = self.image.get_rect()
        setattr(self.rect, self.anchor, self.rsap.pos)

    def update(self, dt):
        if self.tag is not None:
            self.image = C.fetch(self.tag, *self.rsap)
            self.rect = self.image.get_rect()
        setattr(self.rect, self.anchor, self.rsap.pos)

    def shutdown_(self):
        # This is for tinyecs
        self.kill()

def dynamic_sprite_system(self, dt, sprite):
    sprite.update(dt)
