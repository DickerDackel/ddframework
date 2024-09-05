from types import SimpleNamespace

import pygame

from ddframework import GameState, StateExit
from ddframework.textbox import TextBox
from ddframework.dynamicsprite import RSAP, TGroup

from pgcooldown import Cooldown

import sampleapp.compsys as cs
import sampleapp.globals as G


class BannerState(GameState):
    def __init__(self, app, banner, styles, pos, *args, blink=0,
                 followup=0, lifetime=None, **kwargs):
        super().__init__(app)

        self.banner = banner
        self.followup = followup
        self.lifetime = Cooldown(G.STATE_CYCLE_TIME) if lifetime else None

        self.groups = SimpleNamespace(
            text=TGroup(),
        )

        rsap = RSAP(pos=pos)
        self.textbox = TextBox(self.banner, styles, blink=blink)
        self.groups.text.add(cs.TextSprite(self.app.renderer, self.textbox, rsap))

    def reset(self):
        if self.lifetime is not None:
            self.lifetime.reset()

    def update(self, dt):
        if self.lifetime is not None and self.lifetime.cold():
            raise StateExit(self.followup)
        self.groups.text.update(dt)

    def draw(self):
        self.app.renderer.draw_color = G.COLOR.background
        self.app.renderer.clear()
        self.groups.text.draw()

    def dispatch_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                raise StateExit(self.followup)
        super().dispatch_event(e)
