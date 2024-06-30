from enum import IntEnum
from functools import partial
from random import random

import pygame

from pygame import Vector2 as V2

from ddframework import StateExit, StackPermissions
from pgcooldown import Cooldown

import sampleapp.globals as G

from .bannerstate import BannerState
from .countdown import Countdown
from .gameover import Gameover
from .pause import Pause


class Particle(pygame.sprite.Sprite):
    def __init__(self, *groups, pos, momentum, world, size, color):
        super().__init__(*groups)
        self.pos = pos
        self.momentum = momentum
        self.world = world.inflate(2 * size, 2 * size)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        self.pos += self.momentum * dt
        self.rect.center = self.pos

        if not self.world.contains(self.rect):
            self.kill()


def particle_factory(pos=G.SCREEN.center, momentum=50, world=G.SCREEN,
                     size=16, color='white'):
    return Particle(pos=pos, momentum=momentum, world=world, size=size, color=color)


class PointEmitter(pygame.sprite.Group):
    def __init__(self, pos, density, speed, factory):
        super().__init__()

        self.pos = pos
        self.speed = speed
        self.factory = factory
        self.cooldown = Cooldown(1 / density)

    def update(self, dt):
        if self.cooldown.cold():
            self.cooldown.reset(wrap=True)
            momentum = V2(self.speed, 0).rotate(random() * 360)
            particle = self.factory(pos=self.pos, momentum=momentum)
            self.add(particle)

        super().update(dt)

class Game(BannerState):
    class _States(IntEnum):
        PRE_LAUNCH = 0
        STARTED = 1
        COUNTDOWN = 2
        RUNNING = 3
        GAMEOVER = 4
        LINGERING = 5
        FINISHED = 6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = None
        self.prelaunch_frames = None
        factory = partial(particle_factory, world=G.SCREEN, size=16,
                          color='lightgreen')
        self.emitter = PointEmitter(pos=G.SCREEN.center, density=5, speed=150,
                                    factory=factory)


    def reset(self):
        super().reset()
        self.state = self._States.PRE_LAUNCH
        self.prelaunch_frames = 2
        self.emitter.empty()

    def restart(self, result):
        self.lifetime.start()
        if self.prelaunch_frames >= 0:
            self.prelaunch_frames = 2

    def dispatch_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.state = self._States.GAMEOVER
            elif e.key == pygame.K_p:
                self.lifetime.pause()
                self.app.push(Pause(self.app), StackPermissions.DRAW)

    def update(self, dt):
        self.emitter.update(dt)
        if self.state == self._States.PRE_LAUNCH:
            # run for 2 frames before the countdown
            self.prelaunch_frames -= 1
            if self.prelaunch_frames < 0:
                self.state = self._States.STARTED
            return

        if self.state == self._States.STARTED:
            self.state = self._States.COUNTDOWN
            self.lifetime.pause()
            self.app.push(Countdown(self.app), StackPermissions.UPDATE | StackPermissions.DRAW)
            return

        if self.state == self._States.COUNTDOWN and not self.app.is_stacked(self):
            self.state = self._States.RUNNING
            # Fallthrough

        if self.state == self._States.RUNNING:
            if self.lifetime.cold():
                self.state = self._States.GAMEOVER
                return

        if self.state == self._States.GAMEOVER:
            self.app.push(Gameover(self.app), StackPermissions.UPDATE | StackPermissions.DRAW)
            self.state = self._States.LINGERING
            return

        if self.state == self._States.LINGERING and not self.app.is_stacked(self):
            raise StateExit(0)

    def draw(self, screen):
        super().draw(screen)
        self.emitter.draw(screen)
