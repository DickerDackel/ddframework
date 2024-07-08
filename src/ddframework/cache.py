import logging

import pygame

chunk_angle = 10
chunk_alpha = 16
debug = False

_image = {}
_base = {}


class CachedRSAI(pygame.sprite.Sprite):
    """A cached rotated/scaled/alpha-blended image"""

    def __init__(self, img_id, pos, cache, angle=0, scale=1, alpha=255):
        super().__init__()
        self.id = img_id
        self.pos = pos
        self.cache = cache
        self._angle = angle
        self._scale = scale
        self._alpha = alpha

        self._image = self.cache.fetch(self.id, self.angle, self.scale, self.alpha)
        self.dirty = False

    @property
    def angle(self): return self._angle

    @angle.setter
    def angle(self, val):
        self.dirty = True
        self._angle = val
        return self._angle

    @property
    def scale(self): return self._scale

    @scale.setter
    def scale(self, val):
        self.dirty = True
        self._scale = val
        return self._scale

    @property
    def alpha(self): return self._alpha

    @alpha.setter
    def alpha(self, val):
        self.dirty = True
        self._alpha = val
        return self._alpha

    @property
    def image(self):
        if self.dirty:
            self._image = self.cache.fetch(self.id, self.angle, self.scale, self.alpha)
            self.dirty = False
        return self._image

    @property
    def rect(self):
        return self._image.get_rect(center=self.pos)

    @rect.setter
    def rect(self, r):
        self.pos = r.center


def chunk(v, size):
    return size * ((v + size // 2) // size)


def image_key(basename, *, angle=0, scale=1, alpha=255):
    if chunk_angle: angle = chunk(angle % 360, chunk_angle)
    if chunk_alpha: alpha = chunk(alpha, chunk_alpha)

    return f'{basename}-{scale}-{angle}-{alpha}'


def add_baseimage(name, img):
    key = image_key(name)
    if key not in _image:
        _image[key] = img
        _base[img] = _image[key]


def fetch(basename, angle=0, scale=1, alpha=255):
    key = image_key(basename, angle=angle, scale=scale, alpha=alpha)
    if key not in _image:
        logging.critical(f'generating {key}')
        base_key = image_key(basename)
        img = _image[base_key]
        if debug:
            pygame.draw.rect(img, 'yellow', img.get_rect(), width=1)

        if angle:
            img = pygame.transform.rotate(img, angle)
            if debug:
                pygame.draw.rect(img, 'cyan', img.get_rect(), width=1)

        if scale != 1:
            img = pygame.transform.scale_by(img, scale)
            if debug:
                pygame.draw.rect(img, 'magenta', img.get_rect(), width=1)

        if alpha != 255:
            img.set_alpha(alpha)

        _image[key] = img
        _base[_image[key]] = _image[base_key]
    return _image[key]


def base(image):
    return _base[image]


__all__ = [CachedRSAI, image_key, add_baseimage, fetch, base]
