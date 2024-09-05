import pygame

from glm import vec2


class _TotallyAVec2:
    def __set_name__(self, obj, name):
        self.attrib = f'__totally_a_vec2_{name}'

    def __set__(self, obj, val):
        if isinstance(val, vec2):
            obj.__setattr__(self.attrib, val)
        else:
            obj.__setattr__(self.attrib, vec2(val))

    def __get__(self, obj, parent):
        if obj is None: return self

        return obj.__getattribute__(self.attrib)


class RSAP:
    pos = _TotallyAVec2()

    """Rotation, Scale, Alpha, Position in one container"""
    def __init__(self,
                 angle: float = 0,
                 scale: float = 1,
                 alpha: int = 255,
                 pos: vec2|tuple[float, float] = (0, 0)) -> None:
        self.angle = angle
        self.scale = scale
        self.alpha = alpha
        self.pos = pos

    def __iter__(self):
        yield self.angle
        yield self.scale
        yield self.alpha
        yield self.pos


class DynamicSprite(pygame.sprite.Sprite):
    def __init__(self, texture, rsap, *groups, anchor='center'):
        super().__init__(*groups)

        self.image = texture
        self.rsap = rsap  # Camera needs access to this.  Can't be in a comp alone!
        self.anchor = anchor

        self.rect = self.image.get_rect(**{anchor: rsap.pos})

    def update(self, dt):
        setattr(self.rect, self.anchor, self.rsap.pos)

    # This is for tinyecs
    def shutdown_(self):
        self.kill()


class TGroup(pygame.sprite.Group):
    def draw(self):
        for s in self.sprites():
            args = {}

            if hasattr(s, 'scale'):
                args['dstrect'] = s.rect.scale_by(s.scale)
            else:
                args['dstrect'] = s.rect

            if hasattr(s, 'angle'):
                args['angle'] = s.angle

            preserve_alpha = None
            if hasattr(s, 'alpha'):
                preserve_alpha = s.image.alpha
                s.alpha = s.alpha

            s.image.draw(**args)

            if preserve_alpha is not None:
                s.image.alpha = preserve_alpha


def dynamic_sprite_system(self, dt, sprite):
    sprite.update(dt)
