from enum import IntEnum
from functools import partial
from random import random

import ddframework.cache as cache
import pygame
import pygame._sdl2 as sdl2
import glm

from ddframework import GameState, StateExit, StackPermissions
from ddframework.dynamicsprite import DynamicSprite, RSAP, TGroup, _TotallyAVec2
from pgcooldown import Cooldown
from glm import vec2

import sampleapp.globals as G

from .countdown import Countdown
from .gameover import Gameover
from .pause import Pause


class Particle(DynamicSprite):
    NAME = 'particle'
    momentum = _TotallyAVec2()

    def __init__(self, *, renderer, rsap, momentum, world, size, color):
        if (texture := cache.get(self.NAME)) is None:
            image = pygame.Surface((size, size))
            image.fill(color)
            texture = sdl2.Texture.from_surface(renderer, image)
            cache.add(texture, self.NAME)

        super().__init__(texture, rsap)

        self.image = cache.get(self.NAME)
        self.rect = self.image.get_rect(center=rsap.pos)

        self.momentum = momentum
        self.world = world.inflate(2 * size, 2 * size)

    def update(self, dt):
        self.rsap.pos += self.momentum * dt
        self.rect.center = self.rsap.pos

        if not self.world.contains(self.rect):
            self.kill()


def particle_factory(*, renderer, rsap, momentum=50, world=G.SCREEN,
                     size=16, color='white'):
    return Particle(renderer, rsap, momentum, world, size, color)


class PointEmitter(TGroup):
    def __init__(self, pos, density, speed, factory):
        super().__init__()

        self.pos = pos
        self.speed = speed
        self.factory = factory
        self.cooldown = Cooldown(1 / density)

    def update(self, dt):
        if self.cooldown.cold():
            self.cooldown.reset(wrap=True)
            momentum = glm.rotate(vec2(self.speed, 0), random() * 360)
            rsap = RSAP(pos=self.pos)
            particle = self.factory(rsap=rsap, momentum=momentum)
            self.add(particle)

        super().update(dt)

class Game(GameState):
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
        factory = partial(Particle, renderer=self.app.renderer, world=G.SCREEN,
                          size=16, color='lightgreen')
        self.emitter = PointEmitter(pos=G.SCREEN.center, density=5, speed=150,
                                    factory=factory)


    def reset(self, *args, **kwargs):
        super().reset(*args, **kwargs)
        self.state = self._States.PRE_LAUNCH
        self.prelaunch_frames = 2
        self.emitter.empty()
        self.running_cooldown = Cooldown(10)

    def restart(self, from_state, result):
        if self.prelaunch_frames >= 0:
            self.prelaunch_frames = 2

    def dispatch_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                raise StateExit(0)
            elif e.key == pygame.K_p:
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
            self.app.push(Countdown(self.app), StackPermissions.UPDATE | StackPermissions.DRAW)
            return

        if self.state == self._States.COUNTDOWN and not self.app.is_stacked(self):
            self.state = self._States.RUNNING
            self.running_cooldown.reset(10)
            # Fallthrough

        if self.state == self._States.RUNNING:
            if self.running_cooldown.cold():
                self.state = self._States.GAMEOVER

        if self.state == self._States.GAMEOVER:
            print('GAMEOVER')
            self.app.push(Gameover(self.app), StackPermissions.UPDATE | StackPermissions.DRAW)
            self.state = self._States.LINGERING
            return

        if self.state == self._States.LINGERING and not self.app.is_stacked(self):
            print('LINGERING AND NOT STACKED')
            raise StateExit(0)

    def draw(self):
        super().draw()
        self.emitter.draw()
