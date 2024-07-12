import logging

import pygame

chunk_angle = 10
chunk_alpha = 16
debug = False

_image = {}
_base = {}


def chunk(v, size):
    return size * ((v + size // 2) // size)


def image_key(basename, *, angle=0, scale=1, alpha=255):
    if chunk_angle: angle = chunk(angle % 360, chunk_angle)
    if chunk_alpha: alpha = chunk(alpha, chunk_alpha)

    return f'{basename}-{scale}-{angle}-{alpha}'


def add_baseimage(img, name):
    key = image_key(name)
    if key not in _image:
        _image[key] = img
        _base[img] = _image[key]


def fetch(basename, angle=0, scale=1, alpha=255):
    key = image_key(basename, angle=angle, scale=scale, alpha=alpha)
    if key not in _image:
        logging.debug(f'generating {key}')
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


__all__ = [image_key, add_baseimage, fetch, base]
