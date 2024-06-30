from dataclasses import dataclass
from typing import NamedTuple, Sequence

import pygame

from pgcooldown import Cooldown


class Framing(NamedTuple):
    top: float
    right: float
    bottom: float
    left: float

def cleanup_framing(framing):
    # Rules stolen from CSS
    if framing is None or framing == 0:
        top = right = bottom = left = 0
    elif isinstance(framing, Sequence):
        l = len(framing)
        assert 2 <= l <= 4, "Margin must be number, or a 2-4 element sequence"

        if l == 2:
            top = bottom = framing[0]
            left = right = framing[1]
        elif l == 3:
            top = framing[0]
            left = right = framing[1]
            bottom = framing[2]
        elif l == 4:
            top, right, bottom, left = framing
    else:
        top = right = bottom = left = framing

    return Framing(top, right, bottom, left)


def mkembed(surface, framing):
    rect = surface.get_rect().inflate(framing.left + framing.right,
                                      framing.top + framing.bottom)
    canvas = pygame.Surface(rect.size, flags=surface.get_flags())
    canvas.set_colorkey(surface.get_colorkey())

    return canvas


def mklabel(s, style):
    text = style.font.render(s, True, style.color)

    padding = mkembed(text, cleanup_framing(style.padding))
    border = mkembed(padding, cleanup_framing(style.border))
    canvas = mkembed(border, cleanup_framing(style.margin))

    if style.bgcolor is not None:
        brect = border.get_rect()
        pygame.draw.rect(border, style.bgcolor, brect,
                         width=0, border_radius=style.border_radius)
        pygame.draw.rect(border, style.border_color, brect,
                         width=style.border, border_radius=style.border_radius)

    rect = canvas.get_rect()
    canvas.blit(border, border.get_rect(center=rect.center))
    canvas.blit(padding, padding.get_rect(center=rect.center))
    canvas.blit(text, text.get_rect(center=rect.center))

    return canvas

@dataclass
class LabelStyle:
    """A class to configure look and behaviour of a TextLabel

    The following fields are available in both the `init` and as attributes.

        Attribute       Type                        Default
        ---------------------------------------------------
        font:           pygame.Font
        color:          pygame.Color                'white'
        bgcolor:        pygame.Color                None
        margin:         float | Sequence | None     0
        padding:        float | Sequence | None     0
        border:         float | None                0
        border_color:   pygame.Color                'white'
        border_radius:  float                       0
        blink:          int                         0
        blink_color:    pygame.Color                transparent
        anchor:         str                         'center'
    """
    font: pygame.Font
    color: pygame.Color = 'white'
    bgcolor: pygame.Color | None = None
    margin: Sequence | float = 0
    padding: Sequence | float = 0
    border: float = 0
    border_color: pygame.Color = 'white'
    border_radius: float = 0
    blink: int = 0
    blink_color: pygame.Color = (0, 0, 0, 0)
    anchor: str = 'center'

    def __post_init__(self):
        self.margin = cleanup_framing(self.margin)
        self.padding = cleanup_framing(self.padding)


    def copy(self, **kwargs):
        """Create a copy of a style

            clone = style.copy(blink=0.5)

        All attributes from the `init` can be overwritten as well.
        """

        definitions = {
            'font': self.font,
            'color': self.color,
            'bgcolor': self.bgcolor,
            'margin': self.margin,
            'padding': self.padding,
            'border': self.border,
            'border_color': self.border_color,
            'border_radius': self.border_radius,
            'blink': self.blink,
            'blink_color': self.blink_color,
            'anchor': self.anchor,
        }
        definitions.update(kwargs)
        clone = LabelStyle(**definitions)

        return clone


class TextLabel(pygame.sprite.Sprite):
    def __init__(self, text, pos, style, *groups):
        super().__init__(*groups)

        self._text = text
        self.style = style
        self.pos = pos

        self.blink_state = 0
        self.blinks = []
        self.blink_cooldown = Cooldown(style.blink) if style.blink else None

        self._update_images()
        setattr(self.rect, self.style.anchor, self.pos)

    def __repr__(self):
        return f"""
{type(self)}({self._text=},
          {self.style=},
          {self.pos=},
          {self.image=},
          {self.rect=}
)
"""

    def _update_images(self):
        self.blinks = []
        self.image = mklabel(self._text, self.style)
        self.rect = self.image.get_rect(center=self.pos)
        self.blinks.append(self.image)

        if self.style.blink:
            blink = mklabel(self._text, self.style.copy(color=self.style.blink_color))
            self.blinks.append(blink)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = str(text)
        self._update_images()

    def reset(self):
        self.blink_cooldown.reset()

    def update(self, dt):
        setattr(self.rect, self.style.anchor, self.pos)

        if self.style.blink and self.blink_cooldown.cold():
            self.blink_cooldown.reset(wrap=True)
            self.blink_state = 1 - self.blink_state

        self.image = self.blinks[self.blink_state]
