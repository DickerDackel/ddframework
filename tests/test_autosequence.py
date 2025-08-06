import pytest

from time import sleep

from ddframework.autosequence import AutoSequence


def test_autosequence_default() -> None:
    thing = AutoSequence((1, 2, 3), 1)
    assert thing() == 1
    sleep(1 / 3)
    assert thing() == 2
    sleep(1 / 3)
    assert thing() == 3
    sleep(1 / 3)
    assert thing() == 1


def test_autosequence_repeat0() -> None:
    thing = AutoSequence((1, 2, 3), 1, repeat=0)
    assert thing() == 1
    sleep(1 / 3)
    assert thing() == 2
    sleep(1 / 3)
    assert thing() == 3
    sleep(1 / 3)
    assert thing() == None


def test_autosequence_repeat1() -> None:
    thing = AutoSequence((1, 2, 3), 1, repeat=1)
    assert thing() == 1
    sleep(1 / 3)
    assert thing() == 2
    sleep(1 / 3)
    assert thing() == 3
    sleep(1 / 3)
    assert thing() == 1


def test_autosequence_repeat1_loop1() -> None:
    thing = AutoSequence((1, 2, 3), 1, repeat=1, loops=1)
    assert thing() == 1
    sleep(1 / 3)
    assert thing() == 2
    sleep(1 / 3)
    assert thing() == 3
    sleep(1 / 3)
    assert thing() == None


def test_autosequence_repeat2_loop2() -> None:
    thing = AutoSequence((1, 2, 3), 1, repeat=2, loops=2)
    assert thing() == 1
    sleep(1 / 3)
    assert thing() == 2
    sleep(1 / 3)
    assert thing() == 3
    sleep(1 / 3)
    assert thing() == 3
    sleep(1 / 3)
    assert thing() == 2
    sleep(1 / 3)
    assert thing() == 1
    sleep(1 / 3)
    assert thing() == None
