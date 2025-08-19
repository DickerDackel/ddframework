from typing import Hashable, Generator


__all__ = ['StateMachine']

StateWalker = Generator[Hashable, Hashable, None]


class EmptyGraph(Exception): pass
class OpenGraph(Exception): pass  # noqa: E302
class UnknownNode(Exception): pass  # noqa: E302


class StateMachine:
    """A very simple statemachine to consistently track... well, state.

    States are added to the state machine with a list of followup states.

        sm = StateMachine()
        sm.add(splashscreen, titlescreen)
        sm.add(titlescreen, demo, game)
        sm.add(demo, highscores, game)
        sm.add(highscores, title, game)
        sm.add(game, gameover)
        sm.add(gameover, highscores)

    will create the following state machine

                         +---------> game ----> gameover
                         |            ^            |
                         |            |            v
        splash ---> titlescreen ---> demo ---> highscores --+
                         ^                                  |
                         |                                  |
                         +----------------------------------+

    States are just python objects, so a state could be a string, but also a
    state-object to be called.

    Traversal of the state machine is done by requesting a state walker with a
    given start node.  Giving no start node will use the first state added.

        walker = sm.walker('splash')
        state = next(walker)  # --> `splash`

    The walker is a generator, and its next step can be controlled by
    `send`ing the number of the followup state to it.  Using `next` instead of
    `send` will always chose the first followup.

        state = next(walker)    # --> `titlescreen`
        state = walker.send(0)  # --> `demo`, same as next(walker)
        state = next(walker)    # --> `highscores`
        state = next(walker)    # --> `titlescreen`
        state = walker.send(1)  # --> `game`
        state = next(walker)    # --> `gameover`
        state = walker.send(-1) # --> raises StopIteration.

    Since walker is iterable, it can also be used for a linear workflow in a
    `for` loop:

        sm = StateMachine()
        sm.add('job1', 'job2')
        sm.add('job2', 'job3')
        sm.add('job3', None)
        batch = sm.walker()

        for task in batch:
            ...

    """
    def __init__(self, states: Hashable | None = None) -> None:
        """Create a state machine"""
        self.states = {}
        self.root = None

    def add(self, state: Hashable, *followups: Hashable) -> None:
        """Add a state to the state machine

            sm.add(state, followup_state1, followup_state2, ...)

        """
        if self.root is None:
            self.root = state

        self.states[state] = followups

    def walker(self, entry: Hashable = None) -> StateWalker:
        """Create a state walker.

            walker = sm.walker(initial_state)

        If `initial_state` is not given, start at the first state added.
        Use `state = next(walker)` or `walker.send(0)` to progress with the
        first followup.
        Use `state = walker.send(followup_index)` to progress with the nth followup.

        Use `walker = walker.send(-1)` to exit the state machine.  Sine
        `walker` is an iterable, this will raise `StopIteration`.

        Raises:
            EmptyGraph - when no states have been added
            UnknownNode - if the requested entry node is unknown
            OpenGraph - if a requested followup is an unknown state

        """
        if entry is not None and entry not in self.states:
            raise UnknownNode(f'{entry} not in {self.states}') from KeyError

        if self.root is None:
            raise EmptyGraph('Cannot create a walker for an empty graph')

        node = entry if entry is not None else self.root
        followup_idx = 0
        while True:
            # If the current node is None, terminate

            followup_idx = yield node
            # yield from a next returns None
            if followup_idx is None:
                followup_idx = 0
            elif followup_idx < 0:
                break

            try:
                next_node = self.states[node][followup_idx]
            except IndexError:
                raise OpenGraph(node, followup_idx, self.states[node]) from IndexError

            if next_node is not None and next_node not in self.states:
                raise OpenGraph((node, next_node))
            elif next_node is None:
                break

            node = next_node

    def __repr__(self) -> str:
        return ('\n'.join((f'StateMachine({id(self)}\n',
                           '\n'.join([f'    {k}: {v}' for k, v in self.states.items()]),
                           ')')))
