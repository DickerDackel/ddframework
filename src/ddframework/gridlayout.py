import pygame

from dataclasses import dataclass


@dataclass
class GridLayout:
    """Split the screen into cells of fixed size

        GridLayout(canvas_rect, cells_x, cells_y, margin_x=0, margin_y=0)

    Can return either cell positions as Rect, or grid positions as Vector2

    Parameters
    ----------
    canvas_rect: pygame.Rect
        A rect witht the canvas dimensions

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

    def __post_init__(self):
        self.steps_x = (self.canvas.width - 2 * self.margin_x) / self.cells_x 
        self.steps_y = (self.canvas.height - 2 * self.margin_y) / self.cells_y

    def _validate(x, y, w, h):
        return (w > 0 and h > 0 and x + w <= self.cells_x and y + h < self.cells_y)

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
        Tuple[pygame.Rect, tuple[int, int]] | None

            if the requested segment doesn't completely fits on the canvas,
            None is returned.

        """
        if not self._validate(x, y, w, h): return None

        int_x = int(x)
        int_y = int(y)
        frac_x = (x - int_x) * self.steps_x
        frac_y = (y - int_y) * self.steps_y
        res_x = self.canvas.left + self.margin_x + int(x) * self.steps_x
        res_y = self.canvas.left + self.margin_y + int(y) * self.steps_y

        return (pygame.Rect(res_x, res_y, w * self.steps_x, h * self.steps_y),
                (frac_x, frac_y))

    def position(self, x, y):
        if not self._validate(x, y, w, h): return None

        res_x = self.canvas.left + self.margin_x + x * self.steps_x
        res_y = self.canvas.left + self.margin_y + y * self.steps_y

        return res_x, res_y

    def divmod(self, world_x, world_y):
        span_x = world_x - self.margin_x
        span_y = world_y - self.margin_y

        x, frac_x = divmod(span_x, self.steps_x)
        y, frac_y = divmod(span_y, self.steps_y)

        return x, y, frac_x, frac_y


def debug_grid(screen, grid, color='grey20'):
    pygame.draw.rect(screen, color, screen.get_rect(), width=1)
    pygame.draw.rect(screen, color, grid(0, 0, grid.cells_x, grid.cells_y), width=1)
    for y in range(grid.cells_y):
        for x in range(grid.cells_x):
            pygame.draw.rect(screen, color, grid(x, y, 1, 1), width=1)
