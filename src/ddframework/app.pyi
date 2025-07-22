import abc
import pygame
import pygame._sdl2 as sdl2
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from enum import IntEnum
from pygame.typing import Point
from typing import Any, Hashable, Iterator, NamedTuple

from ddframework.statemachine import StateMachine, StateMachineState

__all__ = ['App', 'GameState', 'StackPermissions', 'StateExit']

class StackPermissions(IntEnum):
    NONE = 0
    UPDATE = 1
    DRAW = 2
    EVENTS = 4
    DRUPDATE = 3
    ALL = 7

class StateExit(Exception): ...

class GameState(ABC, metaclass=abc.ABCMeta):
    app: App
    def __init__(self, app: App) -> None: ...
    def reset(self) -> None: ...
    def restart(self, from_state: GameState, result: Any) -> None: ...
    def dispatch_event(self, e: pygame.event.Event) -> None: ...
    @abstractmethod
    def update(self, dt: float) -> None: ...
    @abstractmethod
    def draw(self) -> None: ...

class StackEntry(NamedTuple):
    state: GameState
    passthrough: int

class App:
    title: str
    fps: float
    bgcolor: pygame.Color
    window: pygame.Window
    renderer: sdl2.Renderer
    window_rect: pygame.Rect
    logical_rect: pygame.Rect
    window_to_logical: pygame.Point
    logical_to_window: pygame.Point
    clock: pygame.time.Clock
    dt_max: float
    running: bool
    state_stack: list[GameState]
    state_machine: StateMachine
    state_walker: Iterator[StateMachineState]
    def __init__(self, title: str, *, resolution: Point = None, window: pygame.Window = None, renderer: sdl2.Renderer = None, fps: int, bgcolor: pygame.Color) -> None: ...
    def run(self) -> None: ...
    def dispatch_events(self) -> None: ...
    def update(self, dt: float = 0) -> None: ...
    def draw(self) -> None: ...
    def push(self, substate: GameState, passthrough: StackPermissions = ...) -> None: ...
    def is_stacked(self, state: GameState) -> None: ...
    def create_state_walker(self, node: Hashable) -> Iterator[Hashable]: ...
    def transition(self, index: int | None) -> None: ...
