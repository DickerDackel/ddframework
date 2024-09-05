import pygame._sdl2 as sdl2

from ddframework.textbox import TextBox
from ddframework.dynamicsprite import DynamicSprite
from pgcooldown import Cooldown


########################################################################
#                             _      
#   __ _  ___ _ __   ___ _ __(_) ___ 
#  / _` |/ _ \ '_ \ / _ \ '__| |/ __|
# | (_| |  __/ | | |  __/ |  | | (__ 
#  \__, |\___|_| |_|\___|_|  |_|\___|
#  |___/                             
#
########################################################################


########################################################################
#        _   _ _ _ _   _           
#  _   _| |_(_) (_) |_(_) ___  ___ 
# | | | | __| | | | __| |/ _ \/ __|
# | |_| | |_| | | | |_| |  __/\__ \
#  \__,_|\__|_|_|_|\__|_|\___||___/
#
########################################################################


class TextSprite(DynamicSprite):
    def __init__(self, renderer, textbox, rsap, *groups, **kwargs):
        self.renderer = renderer
        self.textbox = textbox
        self._surface = self.textbox()
        self._image = sdl2.Texture.from_surface(self.renderer, self._surface)
        super().__init__(self._image, rsap, *groups, **kwargs)

    @property
    def image(self):
        new_surf = self.textbox()
        if self._surface is not new_surf:
            pos = getattr(self.rect, self.anchor)
            self.rect = new_surf.get_rect(**{self.anchor: pos})
            self._surface = new_surf
            self._image = sdl2.Texture.from_surface(self.renderer, self._surface)

        return self._image

    @image.setter
    def image(self, _): pass


class CountdownSprite(TextSprite):
    def __init__(self, count, styles, *args, **kwargs):
        super().__init__(TextBox('', styles), *args, **kwargs)

        self.count = count + 1
        self.countdown = iter(reversed(range(self.count)))
        self.cooldown = Cooldown(1, cold=True)

    def reset(self):
        self.countdown = iter(reversed(range(self.count)))
        self.textbox.text = next(self.countdown)
        self.cooldown.reset()

    def update(self, dt):
        super().update(dt)
        if self.cooldown.cold():
            self.cooldown.reset()
            try:
                self.textbox.text = next(self.countdown)
            except StopIteration:
                self.kill()
                self.countdown = None

    def __bool__(self):
        return self.countdown is not None
