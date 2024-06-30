from types import SimpleNamespace

import pygame

from ddframework import GameState, StateExit, CountdownLabel

import sampleapp.globals as G


class Countdown(GameState):
    def __init__(self, *args, duration=3, **kwargs):
        super().__init__(*args, **kwargs)

        self.groups = SimpleNamespace(
            countdown = pygame.sprite.Group(),
        )

        style = G.LABEL_STYLE.copy(color='lightgreen',
                                   border_color='lightgreen', border=1,
                                   margin=16, padding=(16, 32), bgcolor='black',
                                   border_radius=20)
        self.countdown = CountdownLabel(duration, G.SCREEN.center, style)
        self.groups.countdown.add(self.countdown)

    def reset(self):
        super().reset()
        self.countdown.reset()
        self.groups.countdown.add(self.countdown)

    def update(self, dt):
        super().update(dt)
        self.groups.countdown.update(dt)
        if not self.groups.countdown:
            raise StateExit(None)

    def draw(self, screen):
        super().draw(screen)
        self.groups.countdown.draw(screen)
