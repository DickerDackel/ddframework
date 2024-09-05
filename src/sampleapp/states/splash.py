import pygame

from ddframework.app import StateExit
import sampleapp.globals as G

from sampleapp.states.bannerstate import BannerState


class Splash(BannerState):
    def __init__(self, app):
        super().__init__(app, 'Splash Screen', pos=G.BANNER_POS,
                         styles=G.BANNER_STYLES, lifetime=G.STATE_CYCLE_TIME)
