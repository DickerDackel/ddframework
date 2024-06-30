import pygame

from ddframework import LabelStyle


TITLE = 'ddframework test'
SCREEN = pygame.Rect(0, 0, 1024, 768)
FPS = 60
BGCOLOR = 'black'

pygame.font.init()
LABEL_STYLE = LabelStyle(font=pygame.font.SysFont(None, 64),
                         color='lightgreen',
                         anchor='center')

__all__ = [TITLE, SCREEN, FPS, BGCOLOR,
           LABEL_STYLE]
