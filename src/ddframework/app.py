import logging

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from enum import IntEnum
from functools import partial
from typing import Any

import pygame
import pygame._sdl2 as sdl2

from pygame.typing import ColorLike, Point

from ddframework.msgbroker import broker
from ddframework.profiler import Profiler
from ddframework.statemachine import StateMachine, StateWalker

__all__ = ['App', 'GameState', 'StackPermissions', 'StateExit']


logging.basicConfig(format='%(asctime)s %(levelname)-12s  %(message)s',
                    datefmt='%F %T')


def _size_to_window(scale, p):
    return (p[0] * scale[0],
            p[1] * scale[1])


def _size_from_window(scale, p):
    return (p[0] / scale[0],
            p[1] / scale[1])


def _coordinates_to_window(viewport, scale, p):
    return ((p[0] + viewport.left) * scale[0],
            (p[1] + viewport.top) * scale[1])


def _coordinates_from_window(viewport, scale, p):
    return (p[0] / scale[0] - viewport.left,
            p[1] / scale[1] - viewport.top)


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
    def __init__(self, app: 'App') -> None:
        self.app: 'App' = app

    def reset(self, *args: Any, **kwargs: Any) -> None:
        pass

    def restart(self, from_state: 'GameState', result: Any) -> None:
        pass

    def dispatch_event(self, e: pygame.event.Event) -> None:
        if (e.type == pygame.QUIT
                or e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            raise StateExit(None)

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass


@dataclass
class StackEntry:
    state: GameState | None
    passthrough: int
    walker: Iterator


class App:
    def __init__(self, title: str,
                 *,
                 resolution: Point | None = None,
                 window: pygame.Window | None = None,
                 renderer: sdl2.Renderer | None = None,
                 fps: int,
                 bgcolor: ColorLike,
                 do_clear: bool = True) -> None:
        self.title = title
        self.fps = fps
        self.bgcolor = bgcolor
        self.do_clear = do_clear

        if window is None:
            window = pygame.Window(
                title=title,
                fullscreen_desktop=True,
                fullscreen=True,
                input_focus=True,
                mouse_focus=True,
            )
        if title is not None:
            window.title = title

        self.window = window

        if renderer is None:
            self.renderer = sdl2.Renderer(window)

        # renderer.logical_size returns (0, 0) if unset
        self.renderer.logical_size = resolution if resolution is not None else window.size

        self.window_rect = pygame.Rect((0, 0), window.size)
        self.logical_rect = pygame.Rect((0, 0), self.renderer.logical_size)
        self.viewport = self.renderer.get_viewport()

        self.coordinates_from_window = partial(_coordinates_from_window, self.viewport, self.renderer.scale)
        self.coordinates_to_window = partial(_coordinates_to_window, self.viewport, self.renderer.scale)
        self.size_to_window = partial(_size_to_window, self.renderer.scale)
        self.size_from_window = partial(_size_from_window, self.renderer.scale)

        self.clock = pygame.time.Clock()
        self.dt_max = 3 / fps
        self.running = True

        self.broker = broker
        self.profiler = Profiler()

        self.state_stack = []

    def run(self, walker: StateWalker, perftrace: bool = False, stats: bool = False) -> None:
        self.push(walker, StackPermissions.NONE)

        with self.profiler.profile('total'):
            while self.state_stack:
                dt = min(self.clock.tick(self.fps) / 1000.0, self.dt_max)

                # This must happen here and not in the states due state stacking
                with self.profiler.profile('cls'):
                    if self.do_clear:
                        self.renderer.draw_color = self.bgcolor
                        self.renderer.clear()

                try:
                    with self.profiler.profile('events'): self.dispatch_events()
                    with self.profiler.profile('update'): self.update(dt)
                    with self.profiler.profile('draw'):   self.draw()
                except StateExit as e:
                    self.transition(e.args if len(e.args) else None)

                self.renderer.present()

                if perftrace:
                    print('events', self.profiler['events'])
                    print('update', self.profiler['update'])
                    print('draw', self.profiler['draw'], flush=True)

        if stats:
            for _, prof_data in self.profiler.items():
                print(prof_data, flush=True)

    def dispatch_events(self) -> None:
        for e in pygame.event.get():
            states = (entry.state
                      for i, entry in enumerate(self.state_stack[:-1])
                      if self.state_stack[i + 1].passthrough & StackPermissions.EVENTS)
            for state in states:
                state.dispatch_event(e)

            self.state_stack[-1].state.dispatch_event(e)

        self.broker.tick()

    def update(self, dt: float = 0) -> None:
        states = (entry.state
                  for i, entry in enumerate(self.state_stack[:-1])
                  if self.state_stack[i + 1].passthrough & StackPermissions.UPDATE)
        for state in states:
            state.update(dt)

        self.state_stack[-1].state.update(dt)

    def draw(self) -> None:
        states = (entry.state
                  for i, entry in enumerate(self.state_stack[:-1])
                  if self.state_stack[i + 1].passthrough & StackPermissions.DRAW)
        for state in states:
            state.draw()

        self.state_stack[-1].state.draw()

    def push(self,
             state_or_walker: GameState | Iterator,
             passthrough: StackPermissions = StackPermissions.NONE) -> None:

        if isinstance(state_or_walker, GameState):
            statemachine = StateMachine()
            statemachine.add(state_or_walker, None)
            walker = statemachine.walker()
        else:
            walker = state_or_walker

        stackentry = StackEntry(next(walker), passthrough, walker)
        self.state_stack.append(stackentry)
        self.state_stack[-1].state.reset(None)

    def is_stacked(self, state: GameState) -> None:
        return state in [_.state for _ in self.state_stack[:-1]]

    def transition(self, result: tuple[Any] | int | None) -> None:
        # If the GameState raises StateExit(nn < 0):
        #   Pop
        #   If stack is empty, return
        # If the Gamestate raises StateExit(None), it's the same as using
        #   `next(walker).  --> Set nn to 0
        # If the GameState raises StateExit(nn):
        #   Transition to nn
        #   On StopIteration (walker is exhausted):
        #     Pop
        #     if stack is empty, return
        # If the GameState raises StateExit(tuple): Transition to tuple[0]
        #    if tuple[0] is < 0: Terminate
        #    else transition to tuple[0]
        # If Transition destination is None: Terminate
        # If stack is empty: return

        if isinstance(result, tuple):
            index = result[0]
        else:
            index = result

        try:
            followup = self.state_stack[-1].walker.send(index)
        except StopIteration:
            from_state = self.state_stack.pop(-1).state
            if not self.state_stack:
                return

            self.state_stack[-1].state.restart(from_state, result)
            return

        self.state_stack[-1].state = followup
        self.state_stack[-1].state.reset(result)
