#!/bin/env python3

from types import SimpleNamespace

import pygame

from ddframework import App

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
    app.state_machine.add(states.splash, states.title)
    app.state_machine.add(states.title, states.demo, states.game)
    app.state_machine.add(states.demo, states.highscores, states.game)
    app.state_machine.add(states.highscores, states.title, states.game)
    app.state_machine.add(states.game, states.highscores)
    app.create_state_walker(states.splash)

    app.run()

if __name__ == "__main__":
    main()
