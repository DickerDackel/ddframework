from types import SimpleNamespace

import pygame

from ddframework import GameState, StateExit, TextLabel
from pgcooldown import Cooldown

import sampleapp.globals as G


class Gameover(GameState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.groups = SimpleNamespace(text=pygame.sprite.Group())
        style = G.LABEL_STYLE.copy(border=1, bgcolor='black', padding=(16, 32),
                                   border_radius=16, border_color='lightgreen')
        self.groups.text.add(TextLabel('Gameover', G.SCREEN.center, style))

        self.lifetime = Cooldown(3)

    def reset(self):
        self.lifetime.reset()

    def update(self, dt):
        super().update(dt)
        self.groups.text.update(dt)
        if self.lifetime.cold():
            raise StateExit(None)

    def draw(self, screen):
        super().draw(screen)
        self.groups.text.draw(screen)

    def dispatch_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            raise StateExit(None)

        super().dispatch_event(e)

