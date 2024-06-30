from types import SimpleNamespace

import pygame

from ddframework import GameState, StateExit, TextLabel

import sampleapp.globals as G


class Pause(GameState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.groups = SimpleNamespace(text=pygame.sprite.Group())

        style = G.LABEL_STYLE.copy(bgcolor='black', padding=10, border=1,
                                   border_color='lightgreen', border_radius=10)
        self.groups.text.add(TextLabel('Pause', G.SCREEN.center, style))

    def dispatch_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            raise StateExit(None)

        super().dispatch_event(e)

    def update(self, dt):
        super().update(dt)
        self.groups.text.update(dt)

    def draw(self, screen):
        super().draw(screen)
        self.groups.text.draw(screen)
