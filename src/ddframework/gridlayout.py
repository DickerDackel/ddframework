import pygame
import pygame._sdl2 as sdl2

from pygame.typing import ColorLike

from dataclasses import dataclass


@dataclass
class GridLayout:
    """Split the screen into cells of fixed size

        GridLayout(canvas_rect, cells_x, cells_y, margin_x=0, margin_y=0)

    Can return either cell positions as Rect, or grid positions as Vector2

    Parameters
    ----------
    canvas_rect: pygame.Rect
        A rect like with the canvas dimensions

    cells_x: int
    cells_y: int
        x and y steps to split the canvas into

    margin_x: int
    margin_y: int
        a margin around the whole canvas
    """

    canvas: pygame.Rect
    cells_x: int
    cells_y: int
    margin_x: int = 0
    margin_y: int = 0
    cell_margin_x: int = 0
    cell_margin_y: int = 0

    def __post_init__(self):
        self.steps_x = (self.canvas.width - 2 * self.margin_x) / self.cells_x 
        self.steps_y = (self.canvas.height - 2 * self.margin_y) / self.cells_y

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

            grid = GridLayout(canvas, 10, 5)
            rect = grid.cell(3, 3, 2, 1)


        Parameters
        ----------
        x, y: int
            cell position

        w, h: int
            width and height in cell steps

        Returns
        -------
        pygame.Rect | None

            if the requested segment doesn't completely fits on the canvas,
            None is returned.

        """
        res_x = self.canvas.left + self.margin_x + x * self.steps_x
        res_y = self.canvas.left + self.margin_y + y * self.steps_y
        rect = pygame.Rect(res_x, res_y, w * self.steps_x, h * self.steps_y).inflate(-self.cell_margin_x, -self.cell_margin_y)

        return rect

    def offset(self, x, y, w=1, h=1):
        """Return the fragment offset within a requested cell

            grid = GridLayout(canvas, 10, 5)
            rect = grid(3, 3, 2, 1)
            offset = grid.offset(3, 3, 2, 1)


        Parameters
        ----------
        x, y: int
            cell position

        w, h: int
            width and height in cell steps

        Returns
        -------
        Tuple[float, float] | None

            if the requested segment doesn't completely fits on the canvas,
            None is returned.

        """
        frac_x = (x - int(x)) * self.steps_x
        frac_y = (y - int(x)) * self.steps_y

        return frac_x, frac_y

    position = __call__

    def cell(self, world_x, world_y):
        """Return the cell position for the given world coordinates.

            grid = GridLayout(canvas, 10, 5)
            mouse = pygame.mouse.get_pos()
            cell = grid.cell(mouse.x, mouse.y)

        Note:

            The result will be a float that includes the position within the
            cell in the decimal places.

        Parameters
        ----------
        world_x, world_y: int
            screen position

        Returns
        -------
        x, y: float
            cell coordinates as float
        """

        span_x = world_x - self.margin_x
        span_y = world_y - self.margin_y

        x = span_x / self.steps_x
        y = span_y / self.steps_y

        return x, y


def debug_grid(screen: pygame.Surface | sdl2.Renderer, grid: GridLayout, color: ColorLike = 'grey20'):
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
