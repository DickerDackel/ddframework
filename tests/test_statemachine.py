import pdb
import pytest

from ddframework.statemachine import StateMachine, EmptyGraph, UnknownNode, OpenGraph

from pgcooldown import Cooldown
from time import sleep


@pytest.fixture
def machine():
    sm = StateMachine()
    sm.add('a', 'b', 'c', 'd')
    sm.add('b', 'c',)
    sm.add('c', None)
    return sm


def test_fixture(machine):
    assert isinstance(machine, StateMachine)


def test_empty():
    machine = StateMachine()
    walker = machine.walker()
    with pytest.raises(EmptyGraph):
        next(walker)


def test_unknown(machine):
    walker = machine.walker('xyzzy')
    with pytest.raises(UnknownNode):
        next(walker)


def test_open(machine):
    walker = machine.walker()
    next(walker)
    with pytest.raises(OpenGraph):
        walker.send(2)


def test_default_entry(machine):
    walker = machine.walker()
    assert next(walker) == 'a'


def test_chosen_entry(machine):
    walker = machine.walker('b')
    assert next(walker) == 'b'


def test_send(machine):
    walker = machine.walker()
    state = next(walker)
    assert walker.send(1) == 'c'


def test_exit(machine):
    walker = machine.walker()
    for state in walker:
        pass

    assert state == 'c'
