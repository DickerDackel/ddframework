from typing import Hashable, Iterator


__all__ = ['StateMachine']

class EmptyGraph(Exception): pass
class OpenGraph(Exception): pass
class UnknownNode(Exception): pass
class UnknownFollowupIndex(Exception): pass

class StateMachine:
    def __init__(self, states=None) -> None:
        self.states = {}
        self.root = None

    def add(self, name, *followups) -> None:
        if self.root is None:
            self.root = name

        self.states[name] = followups

    def walker(self, entry: Hashable = None) -> Iterator[Hashable]:
        if entry is not None and entry not in self.states:
            raise UnknownNode(f'{entry} not in {self.states}') from KeyError

        if self.root is None:
            raise EmptyGraph(f'Cannot create a walker for an empty graph')

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
                raise UnknownFollowupIndex(node, followup_idx, self.states[node]) from IndexError

            if next_node is not None and next_node not in self.states:
                raise OpenGraph((node, next_node))
            elif next_node is None:
                break

            node = next_node


    def __repr__(self) -> str:
        return (f'StateMachine({id(self)}\n' +
                '\n'.join([f'    {k}: {v}' for k, v in self.states.items()]) +
                ')')
