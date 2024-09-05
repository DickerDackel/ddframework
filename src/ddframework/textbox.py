from dataclasses import dataclass
from typing import NamedTuple, Sequence

import pygame

from pgcooldown import LerpThing


class Frame(NamedTuple):
    top: float
    right: float
    bottom: float
    left: float


def frame(*framing):
    # Rules stolen from CSS
    l = len(framing)
    assert 0 <= l <= 4, 'Framing must be within 0 to 4 elements'

    if l == 0:
        top = right = bottom = left = 0
    elif l == 1:
        top = right = bottom = left = framing[0]
    elif l == 2:
        top = bottom = framing[0]
        left = right = framing[1]
    elif l == 3:
        top = framing[0]
        left = right = framing[1]
        bottom = framing[2]
    elif l == 4:
        top, right, bottom, left = framing

    return Frame(top, right, bottom, left)


def mklabel(s, style, alpha=True):
    flags = pygame.SRCALPHA if alpha else 0

    padding = style.padding
    border = style.border
    margin = style.margin

    text = style.font.render(s, True, style.color)
    trect = text.get_rect(topleft=(margin.left + border + padding.left,
                                   margin.top + border + padding.top))

    width = (trect.width + padding.left + padding.right + 2 * border + margin.left + margin.right)
    height = (trect.height + padding.top + padding.bottom + 2 * border + margin.top + margin.bottom)
    canvas = pygame.Surface((width, height), flags=flags)

    if style.border:
        brect = trect.inflate(
            (padding.left + padding.right + 2 * border,
             padding.top + padding.bottom + 2 * border)
        ).move_to(
            topleft=(margin.left, margin.top)
        )

        if style.bgcolor:
            pygame.draw.rect(canvas, style.bgcolor, brect,
                             width=0, border_radius=style.border_radius)

        pygame.draw.rect(canvas, style.border_color, brect,
                         width=style.border, border_radius=style.border_radius)

    canvas.blit(text, trect)

    return canvas


@dataclass
class LabelStyle:
    """A class to configure look and behaviour of a TextBox

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
    """
    font: pygame.Font
    color: pygame.Color = 'white'
    bgcolor: pygame.Color | None = None
    margin: Sequence | float = 0
    padding: Sequence | float = 0
    border: float = 0
    border_color: pygame.Color = 'white'
    border_radius: float = 0

    def __post_init__(self):
        if not isinstance(self.margin, Frame):
            m = self.margin
            self.margin = frame(*m) if isinstance(m, Sequence) else frame(m)
        if not isinstance(self.padding, Frame):
            p = self.padding
            self.padding = frame(*p) if isinstance(p, Sequence) else frame(p)

    def copy(self, **kwargs):
        """Create a copy of a style

            clone = style.copy(color='yellow')

        All attributes from the `init` can be overwritten as well.
        """

        definitions = self.__dict__.copy()
        definitions.update(kwargs)
        clone = LabelStyle(**definitions)

        return clone


class TextBox:
    """Create a text surface in a prefined style

    Given a text and one or two styles (See LabelStyle), this class provides a
    surface of the rendered text.

    Changing the text will automatically update the surface.

    If multiple styles are passed, the text will cycle through them in the
    `blink` interval (given in seconds).  E.g. one style with text color white
    and one with text color black will let the text blink.  Another example
    would be cycling through rainbow colors.

    Methods:
    --------
    To access the current surface, just call the instance like a function.

        tb = TextBox('Hello, world', label_style)
        surface = tb()

    Note:
    -----
    All parameters are also available as attributes.

    Parameters / Attributes
    ----------
    text: str
        The initial text to render

    *styles: list[ddframework.textbox.LabelStyle]
        One or more styles to cycle through.

    blink: float = 0
        The delay in seconds between style switches.

    """

    def __init__(self, text, styles, blink=0):
        self._text = text
        self._styles = styles

        self.blinks = []
        self.blink_idx = LerpThing(0, len(styles), blink, repeat=True)

        self._update_images()

    def _update_images(self):
        self.blinks = []
        for style in self._styles:
            image = mklabel(self._text, style)
            self.blinks.append(image)

    def __call__(self):
        return self.blinks[int(self.blink_idx())]

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = str(text)
        self._update_images()

    @property
    def styles(self):
        return self._styles

    @styles.setter
    def styles(self, *styles):
        self._styles = styles
        self._update_images()

    @property
    def blink(self):
        return self.blink_idx.cooldown.duration

    @blink.setter
    def blink(self, blink):
        self.blink_idx.cooldown.reset(blink)
