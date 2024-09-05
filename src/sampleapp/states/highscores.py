import pygame

from ddframework import StateExit

import sampleapp.globals as G

from sampleapp.states.bannerstate import BannerState


class Highscores(BannerState):
    def __init__(self, app):
        super().__init__(app, 'Highscores', pos=G.BANNER_POS,
                         styles=G.BANNER_STYLES, lifetime=G.STATE_CYCLE_TIME)

    def dispatch_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                raise StateExit(1)
        super().dispatch_event(e)
