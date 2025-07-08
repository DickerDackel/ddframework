import logging

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import NamedTuple

import pygame
import pygame._sdl2 as sdl2

from .statemachine import StateMachine

__all__ = ['App', 'GameState', 'StackPermissions', 'StateExit']


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-12s  %(message)s',
                    datefmt='%F %T')


class StackPermissions(IntEnum):
    NONE = 0
    UPDATE = 1
    DRAW = 2
    EVENTS = 4
    DRUPDATE = 3
    ALL = 7


class StateExit(Exception):
    pass


class GameState(ABC):
    def __init__(self, app):
        self.app = app

    def reset(self):
        pass

    def restart(self, from_state, result):
        pass

    def dispatch_event(self, e):
        if (e.type == pygame.QUIT
                or e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            raise StateExit(-999)

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self):
        pass


class StackEntry(NamedTuple):
    state: GameState
    passthrough: int


class App:
    def __init__(self, title, *, resolution=None, window=None, renderer=None, fps=60, bgcolor='black'):
        self.title = title
        self.fps = fps
        self.bgcolor = bgcolor

        if window is None:
            window = pygame.Window(
                title=title,
                fullscreen_desktop=True,
                fullscreen=True,
                input_focus=True,
                mouse_focus=True,
            )

        self.window = window

        if renderer is None:
            self.renderer = sdl2.Renderer(window)

        # renderer.logical_size returns (0, 0) if unset
        self.renderer.logical_size = resolution if resolution is not None else window.size

        self.window_rect = pygame.Rect((0, 0), window.size)
        self.logical_rect = pygame.Rect((0, 0), self.renderer.logical_size)

        self.clock = pygame.time.Clock()
        self.dt_max = 3 / fps
        self.running = True

        self.state_stack = []
        self.state_machine = StateMachine()
        self.state_walker = None

    def run(self):
        assert self.state_walker is not None

        self.state_stack.append(StackEntry(next(self.state_walker), 0))
        self.state_stack[-1].state.reset()

        while self.state_stack:
            # dt = min(self.clock.tick(self.fps) / 1000.0, self.dt_max)
            dt = min(self.clock.tick(self.fps) / 1000.0, self.dt_max)

            # This must happen here and not in the states due state stacking
            self.renderer.draw_color = self.bgcolor
            self.renderer.clear()

            try:
                self.dispatch_events()
                self.update(dt)
                self.draw()
            except StateExit as e:
                self.transition(e.args[0] if e.args else 0)

            self.renderer.present()

    def dispatch_events(self):
        for e in pygame.event.get():
            states = (entry.state
                      for i, entry in enumerate(self.state_stack[:-1])
                      if self.state_stack[i + 1].passthrough & StackPermissions.EVENTS)
            for state in states:
                state.dispatch_event(e)

            self.state_stack[-1].state.dispatch_event(e)

    def update(self, dt):
        states = (entry.state
                  for i, entry in enumerate(self.state_stack[:-1])
                  if self.state_stack[i + 1].passthrough & StackPermissions.UPDATE)
        for state in states:
            state.update(dt)

        self.state_stack[-1].state.update(dt)

    def draw(self):
        states = (entry.state
                  for i, entry in enumerate(self.state_stack[:-1])
                  if self.state_stack[i + 1].passthrough & StackPermissions.DRAW)
        for state in states:
            state.draw()

        self.state_stack[-1].state.draw()

    def push(self, substate, passthrough=StackPermissions.NONE):
        self.state_stack.append(StackEntry(substate, passthrough))
        self.state_stack[-1].state.reset()

    def is_stacked(self, state):
        return state in [_.state for _ in self.state_stack[:-1]]

    def create_state_walker(self, node):
        self.state_walker = self.state_machine.walker(node)

    def transition(self, index):
        if index is None or index < 0:
            from_state = self.state_stack.pop(-1)
            if not self.state_stack:
                return
            self.state_stack[-1].state.restart(from_state.state, index)
        else:
            # preserve passthrough if we're on a stacked state that has a
            # transition
            passthrough = self.state_stack[-1].passthrough
            followup = StackEntry(self.state_walker.send(index), passthrough)

            self.state_stack[-1] = followup
            self.state_stack[-1].state.reset()
