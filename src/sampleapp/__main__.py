#!/bin/env python3

from types import SimpleNamespace

import pygame

from ddframework.app import App
from ddframework.statemachine import StateMachine

import sampleapp.globals as G

from .states import Splash, Title, Demo, Highscores, Game


def main():
    w = pygame.Window(size=(1024, 960))
    app = App(G.TITLE, window=w, resolution=G.SCREEN.size, fps=G.FPS,
              bgcolor=G.COLOR.background)

    pygame.mouse.set_visible(False)
    pygame.mouse.set_relative_mode(True)

    states = SimpleNamespace(
        splash=Splash(app),
        title=Title(app),
        demo=Demo(app),
        highscores=Highscores(app),
        game=Game(app),
    )
    statemachine = StateMachine()
    statemachine.add(states.splash, states.title)
    statemachine.add(states.title, states.demo, states.game)
    statemachine.add(states.demo, states.highscores, states.game)
    statemachine.add(states.highscores, states.title, states.game)
    statemachine.add(states.game, states.highscores)
    walker = statemachine.walker(states.splash)

    app.run(walker)

if __name__ == "__main__":
    main()
