import pytest

from time import sleep

from ddframework.autosequence import AutoSequencer


class A:
    seq = AutoSequencer()

    def __init__(self) -> None: self.seq = ((1, 2, 3), 1)  # noqa: E301


class B:
    seq = AutoSequencer(repeat=0)
    def __init__(self) -> None: self.seq = ((1, 2, 3), 1)  # noqa: E301


class C:
    seq = AutoSequencer(repeat=1)
    def __init__(self) -> None: self.seq = ((1, 2, 3), 1)  # noqa: E301


class D:
    seq = AutoSequencer(repeat=1, loops=1)
    def __init__(self) -> None: self.seq = ((1, 2, 3), 1)  # noqa: E301


class E:
    seq = AutoSequencer(repeat=2, loops=2)
    def __init__(self) -> None: self.seq = ((1, 2, 3), 1)  # noqa: E301


def test_autosequencer_default() -> None:
    thing = A()
    assert thing.seq == 1
    sleep(1 / 3)
    assert thing.seq == 2
    sleep(1 / 3)
    assert thing.seq == 3
    sleep(1 / 3)
    assert thing.seq == 1


def test_autosequencer_repeat0() -> None:
    thing = B()
    assert thing.seq == 1
    sleep(1 / 3)
    assert thing.seq == 2
    sleep(1 / 3)
    assert thing.seq == 3
    sleep(1 / 3)
    assert thing.seq == None


def test_autosequencer_repeat1() -> None:
    thing = C()
    assert thing.seq == 1
    sleep(1 / 3)
    assert thing.seq == 2
    sleep(1 / 3)
    assert thing.seq == 3
    sleep(1 / 3)
    assert thing.seq == 1


def test_autosequencer_repeat1_loop1() -> None:
    thing = D()
    assert thing.seq == 1
    sleep(1 / 3)
    assert thing.seq == 2
    sleep(1 / 3)
    assert thing.seq == 3
    sleep(1 / 3)
    assert thing.seq == None


def test_autosequencer_repeat2_loop2() -> None:
    thing = E()
    assert thing.seq == 1
    sleep(1 / 3)
    assert thing.seq == 2
    sleep(1 / 3)
    assert thing.seq == 3
    sleep(1 / 3)
    assert thing.seq == 3
    sleep(1 / 3)
    assert thing.seq == 2
    sleep(1 / 3)
    assert thing.seq == 1
    sleep(1 / 3)
    assert thing.seq == None

def main():
    test_autosequencer_default()
    test_autosequencer_repeat0()
    test_autosequencer_repeat1()
    test_autosequencer_repeat1_loop1()
    test_autosequencer_repeat2_loop2()

if __name__ == '__main__':
    main()
