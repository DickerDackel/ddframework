import pygame

from dataclasses import dataclass


@dataclass
class GridLayout:
    """Split the screen into cells of fixed size

        GridLayout(canvas_rect, cells_x, cells_y, margin=0)

    Can return either cell positions as Rect, or grid positions as Vector2

    Parameters
    ----------
    canvas_rect: pygame.Rect
        A rect witht the canvas dimensions

    cells_x: int
    cells_y: int
        x and y steps to split the canvas into

    margin: int
        a margin around the whole canvas
    """

    canvas: pygame.Rect
    cells_x: int
    cells_y: int
    margin: int = 0

    def __post_init__(self):
        self.steps_x = (self.canvas.width - 2 * self.margin) / self.cells_x 
        self.steps_y = (self.canvas.height - 2 * self.margin) / self.cells_y

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
        if w == 0: return None
        if h == 0: return None
        if x + w > self.cells_x: return None
        if y + h > self.cells_y: return None

        return pygame.Rect(self.canvas.left + self.margin + x * self.steps_x,
                           self.canvas.top + self.margin + y * self.steps_y,
                           w * self.steps_x,
                           h * self.steps_y)


def debug_grid(screen, grid, color='grey20'):
    pygame.draw.rect(screen, color, screen.get_rect(), width=1)
    pygame.draw.rect(screen, color, grid(0, 0, grid.cells_x, grid.cells_y), width=1)
    for y in range(grid.cells_y):
        for x in range(grid.cells_x):
            pygame.draw.rect(screen, color, grid(x, y, 1, 1), width=1)
