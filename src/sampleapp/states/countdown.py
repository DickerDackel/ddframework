import pygame

from pgcooldown import Cooldown
from ddframework.app import StateExit

import sampleapp.globals as G

from sampleapp.states.bannerstate import BannerState


class Countdown(BannerState):
    def __init__(self, app, *args, duration=3, **kwargs):

        styles = (G.BANNER_STYLE.copy(color=G.COLOR.secondary,
                                      font=G.FONT.huger,
                                      border_color=G.COLOR.default, border=10,
                                      margin=16, padding=(16, 32),
                                      bgcolor='black', border_radius=20), )
        super().__init__(app, '', styles=styles, pos=G.SCREEN.center)

        self.digits = None
        self.cooldown = Cooldown(1)

    def reset(self):
        super().reset()
        self.cooldown.reset()
        self.digits = iter(['3', '2', '1'])
        self.textbox.text = next(self.digits)

    def next_digit(self):
        self.cooldown.reset()
        try:
            digit = next(self.digits)
            self.textbox.text = digit
        except StopIteration:
            return None

        return digit

    def update(self, dt):
        if self.cooldown.cold():
            if self.next_digit() is None:
                raise StateExit(None)

        super().update(dt)

    def dispatch_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                if self.next_digit() is None:
                    raise StateExit(None)

        super().dispatch_event(e)

    # Needed because Bannerstate fills black
    def draw(self):
        self.app.renderer.clear()
        self.groups.text.draw()
