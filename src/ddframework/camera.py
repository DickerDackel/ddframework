import pygame
import ddframework.cache as C

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


class CameraGroup(pygame.sprite.Group):
    def __init__(self, camera, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = camera

        size = max(camera.viewport.size)
        self.bounding_box = pygame.Rect(0, 0, size, size).move_to(center=camera.viewport.center)

    def update(self, *args, **kwargs):
        self.bounding_box.center = self.camera.pos
        super().update(*args, **kwargs)

    def draw(self, screen):
        cam = self.camera

        def get_rotated_image(sprite, cam_angle):
            angle = -(cam_angle + sprite.rsap.angle)
            image = C.fetch(sprite.tag, angle=angle)
            return image

        self.bounding_box.center = cam.viewport.center
        pygame.draw.rect(pygame.display.get_surface(), 'red', self.bounding_box.move_to(topleft=(0, 0)), width=1)

        blits = []
        for sprite in self.sprites():
            pos = self.camera.world_to_viewport(sprite.rsap.pos)

            image = get_rotated_image(sprite, self.camera.angle) if sprite.tag else sprite.image
            rect = image.get_rect(center=pos)

            if not self.camera(rect):
                continue

            blits.append((image, rect))

        screen.fblits(blits)
