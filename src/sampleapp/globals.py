from types import SimpleNamespace

import pygame

from ddframework import LabelStyle

__all__ = ['TITLE', 'SCREEN', 'FPS', 'BGCOLOR',
           'STATE_CYCLE_TIME',
           'FONT', 'LABEL_STYLE',
           'BANNER_STYLES', 'BANNER_POS']


########################################################################
#  _____                              ___     _____                      
# | ____|_ __  _   _ _ __ ___  ___   ( _ )   |_   _|   _ _ __   ___  ___ 
# |  _| | '_ \| | | | '_ ` _ \/ __|  / _ \/\   | || | | | '_ \ / _ \/ __|
# | |___| | | | |_| | | | | | \__ \ | (_>  <   | || |_| | |_) |  __/\__ \
# |_____|_| |_|\__,_|_| |_| |_|___/  \___/\/   |_| \__, | .__/ \___||___/
#                                                |___/|_|
########################################################################

...

########################################################################
#     _                _ _           _   _
#    / \   _ __  _ __ | (_) ___ __ _| |_(_) ___  _ __ 
#   / _ \ | '_ \| '_ \| | |/ __/ _` | __| |/ _ \| '_ \ 
#  / ___ \| |_) | |_) | | | (_| (_| | |_| | (_) | | | |
# /_/   \_\ .__/| .__/|_|_|\___\__,_|\__|_|\___/|_| |_|
#         |_|   |_|
# 
########################################################################


TITLE = 'Sample App'
SCREEN = pygame.Rect(0, 0, 1024, 768)
FPS = 60

########################################################################
#   ____
#  / ___|___  _ __ ___  _ __ ___   ___  _ __ 
# | |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \ 
# | |__| (_) | | | | | | | | | | | (_) | | | |
#  \____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|
#
########################################################################

COLOR = SimpleNamespace(
    background='black',
    default='cyan',
    secondary='magenta',
)

STATE_CYCLE_TIME = 5

########################################################################
#  _____         _ 
# |_   _|____  _| |_ 
#   | |/ _ \ \/ / __|
#   | |  __/>  <| |_ 
#   |_|\___/_/\_\\__|
#
########################################################################

pygame.font.init()
FONT = SimpleNamespace(
    tiny=pygame.Font(None, 8),
    small=pygame.Font(None, 12),
    normal=pygame.Font(None, 24),
    large=pygame.Font(None, 32),
    larger=pygame.Font(None, 48),
    huge=pygame.Font(None, 64),
    huger=pygame.Font(None, 128),
    humongous=pygame.Font(None, 256),
)
for f in FONT.__dict__.values():
    f.align = pygame.FONT_CENTER

LABEL_STYLE = LabelStyle(font=pygame.font.SysFont(None, 64),
                         color='lightgreen')

BANNER_STYLE = LabelStyle(
    font=FONT.huge,
    color=COLOR.default,
)
BANNER_STYLES = (BANNER_STYLE, )
BANNER_POS = (SCREEN.centerx, SCREEN.height // 3)
