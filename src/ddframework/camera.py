import pygame

from ddframework.dynamicsprite import DynamicSprite

from glm import vec2, rotate, radians


def rotate_around_pivot(point, pivot, angle):
    shifted = vec2(point) - vec2(pivot)
    rotated = rotate(shifted, -radians(angle))
    return rotated + pivot


class Camera:
    def __init__(self, pos, viewport, anchor):
        self.pos = pos
        self.viewport = pygame.Rect(viewport)
        self.anchor = vec2(anchor)

        self.angle = 0

    def __call__(self, item):
        if isinstance(item, (pygame.Rect, pygame.FRect)):
            return self.viewport.colliderect(item)
        else:
            return self.viewport.collidepoint(item)

    def world_to_viewport(self, point):
        rotated = rotate_around_pivot(point, self.pos, self.angle) if self.angle else point
        shifted = rotated - self.pos + self.anchor
        shifted.y = self.viewport.height - shifted.y
        return shifted

    def viewport_to_world(self, point):
        mirrored = vec2(point)
        mirrored.y = self.viewport.height - mirrored.y
        shifted = mirrored - self.anchor + self.pos
        rotated = rotate_around_pivot(shifted, self.pos, -self.angle) if self.angle else shifted
        return rotated

    def world_to_camera_angle(self, angle):
        return -(self.angle + angle)


class CameraGroup(pygame.sprite.Group):
    def __init__(self, camera, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = camera

        size = max(camera.viewport.size)
        self.bounding_box = pygame.Rect(0, 0, size, size).move_to(center=camera.viewport.center)

    def update(self, *args, **kwargs):
        self.bounding_box.center = self.camera.pos
        super().update(*args, **kwargs)


    def add(self, *sprites):
        for s in sprites:
            if not isinstance(s, DynamicSprite):
                raise TypeError('CameraGroup requires sprite to be of class DynamicSprite')

        super().add(*sprites)

    def draw(self):
        cam = self.camera

        self.bounding_box.center = cam.viewport.center

        for s in self.sprites():
            pos = self.camera.world_to_viewport(s.rsap.pos)

            rect = s.image.get_rect(center=pos)
            if not self.camera(rect):
                continue

            args = {}

            if s.rsap.scale != 1:
                args['dstrect'] = s.rect.scale_by(s.rsap.scale)
            else:
                args['dstrect'] = s.rect

            if s.rsap.angle != 0:
                args['angle'] = self.camera.world_to_camera_angle(s.rsap.angle)

            preserve_alpha = None
            if hasattr(s, 'alpha'):
                preserve_alpha = s.texture.alpha
                s.texture.alpha = s.rsap.alpha

            s.texture.draw(**args)

            if preserve_alpha is not None:
                s.texture.alpha = preserve_alpha
