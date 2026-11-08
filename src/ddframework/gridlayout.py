import pygame
import pygame._sdl2 as sdl2

from pygame.typing import ColorLike

from dataclasses import dataclass


@dataclass
class GridLayout:
    """Access cells in a grid.

    :param canvas: The dimensions of the canvas.
    :param cells_x: Number of horizontal cells
    :param cells_y: Number of vertical cells
    :param margin_x: Left and right margin of the grid on the canvas
    :param margin_y: Top and bottom margin of the grid on the canvas
    :param cell_margin_x: Left and right margin of individual cells
    :param cell_margin_y: Top and bottom margin of individual cells

    The ``GridLayout`` supports assignment and reading of the same attributes
    like a pygame.rect.Rect.

    """

    canvas: pygame.Rect
    cells_x: int
    cells_y: int
    margin_x: int = 0
    margin_y: int = 0
    cell_margin_x: int = 0
    cell_margin_y: int = 0

    @classmethod
    def from_cells(cls, width, height, cell_size, *args, **kwargs):
        print(f'{width=}  {height=}  {cell_size=}  {args=}  {kwargs=}')
        rect = pygame.Rect(0, 0, width * cell_size, height * cell_size)
        print(rect)
        return cls(rect, width, height, *args, **kwargs)

    def __post_init__(self):
        self.steps_x = (self.canvas.width - 2 * self.margin_x) / self.cells_x
        self.steps_y = (self.canvas.height - 2 * self.margin_y) / self.cells_y
        self.grid = self.canvas.inflate(-2 * self.margin_x, -2 * self.margin_y)

    def __getattr__(self, name):
        if name in {'x', 'y', 'top', 'left', 'bottom', 'right', 'topleft',
                    'bottomleft', 'topright', 'bottomright', 'midtop',
                    'midleft', 'midbottom', 'midright', 'center', 'centerx',
                    'centery', 'size', 'width', 'height', 'w', 'h'}:
            return getattr(self.canvas, name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(f"'GridLayout' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in {'x', 'y', 'top', 'left', 'bottom', 'right', 'topleft',
                    'bottomleft', 'topright', 'bottomright', 'midtop',
                    'midleft', 'midbottom', 'midright', 'center', 'centerx',
                    'centery', 'size', 'width', 'height', 'w', 'h'}:
            setattr(self.canvas, name, value)
        else:
            self.__dict__[name] = value

    def __call__(self, x, y, w=1, h=1):
        """Return a rectangle starting at the x, y cell coordinates, spanning over w, h cells

        :param x: left most cell of the requested area
        :param y: top most cell of the requested area
        :param w: width of the requested area in cells
        :param h: height of the requested area in cells
        :return: pygame.Rect | None

        .. code:: python

            grid = GridLayout(canvas, 10, 5)
            rect = grid(3, 3, 2, 1)

        if the requested segment doesn't completely fit on the canvas, None
        is returned.

        """
        res_x = self.canvas.left + self.margin_x + x * self.steps_x
        res_y = self.canvas.top + self.margin_y + y * self.steps_y
        rect = pygame.Rect(res_x, res_y, w * self.steps_x, h * self.steps_y).inflate(-2 * self.cell_margin_x, -2 * self.cell_margin_y)

        return rect

    def offset(self, x, y, w=1, h=1):
        """Return the fragment offset within a requested cell


        :param x: Horizontal cell number
        :param y: Vertical cell number
        :param w: Number of cells horizontally
        :param h: Number of cells vertically
        :returns: top-left coordinates of the given cell, or None if the cells
            won't fit the canvas.

        .. code:: python

            grid = GridLayout(canvas, 10, 5)
            rect = grid(3, 3, 2, 1)
            offset = grid.offset(3, 3, 2, 1)

        """
        frac_x = (x - int(x)) * self.steps_x
        frac_y = (y - int(y)) * self.steps_y

        return frac_x, frac_y

    position = __call__

    def cell(self, world_x, world_y):
        """Return the cell position for the given world coordinates.

        :param world_x: Horizontal screen position
        :param world_y: Vertical screen position
        :returns: cell coordinates as floats

        .. note:: The result will be a float that includes the position within
           the cell in the decimal places.

        .. code:: python

            grid = GridLayout(canvas, 10, 5)
            mouse = pygame.mouse.get_pos()
            cell = grid.cell(mouse.x, mouse.y)

        """

        span_x = world_x - self.margin_x
        span_y = world_y - self.margin_y

        x = span_x / self.steps_x
        y = span_y / self.steps_y

        return x, y


def debug_grid(screen: pygame.Surface | sdl2.Renderer, grid: GridLayout, color: ColorLike = 'grey20'):
    """Draw a grid covering all defined cells in the GridLayout."""

    if isinstance(screen, pygame.Surface):
        pygame.draw.rect(screen, color, screen.get_rect(), width=1)
        pygame.draw.rect(screen, color, grid(0, 0, grid.cells_x, grid.cells_y), width=1)
        for y in range(grid.cells_y):
            for x in range(grid.cells_x):
                pygame.draw.rect(screen, color, grid(x, y, 1, 1), width=1)
    elif isinstance(screen, sdl2.Renderer):
        preserve_color = screen.draw_color
        screen.draw_color = color

        screen.draw_rect(screen.get_viewport().move_to(topleft=(0, 0)))
        screen.draw_rect(grid(0, 0, grid.cells_x, grid.cells_y))
        for y in range(grid.cells_y):
            for x in range(grid.cells_x):
                screen.draw_rect(grid(x, y, 1, 1))

        screen.draw_color = preserve_color
