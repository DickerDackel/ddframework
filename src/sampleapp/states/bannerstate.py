from types import SimpleNamespace

import pygame

from ddframework import GameState, StateExit, TextLabel
from pgcooldown import Cooldown

import sampleapp.globals as G


class BannerState(GameState):
    def __init__(self, title, *args, lifetime=5, **kwargs):
        super().__init__(*args, **kwargs)

        self.lifetime = Cooldown(lifetime)

        self.groups = SimpleNamespace(
            text=pygame.sprite.Group(),
        )
        self.label = TextLabel(title, (G.SCREEN.centerx, G.SCREEN.centery / 2), G.LABEL_STYLE)
        self.groups.text.add()

    def reset(self):
        if self.lifetime is not None:
            self.lifetime.reset()

        self.groups.text.empty()
        self.groups.text.add(self.label)

    def dispatch_event(self, e):
        super().dispatch_event(e)
        if e.type == pygame.KEYDOWN:
            if pygame.K_0 <= e.key <= pygame.K_9:
                raise StateExit(e.key - pygame.K_0)
            elif e.key == pygame.K_SPACE:
                raise StateExit(0)

    def update(self, dt):
        if self.lifetime is not None and self.lifetime.cold():
            raise StateExit(0)

        self.groups.text.update(dt)

    def draw(self, screen):
        screen.fill(G.BGCOLOR)
        self.groups.text.draw(screen)

