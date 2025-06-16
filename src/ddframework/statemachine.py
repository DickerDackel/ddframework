__all__ = ['StateMachine']

class NoRoot(Exception): pass
class OpenGraph(Exception): pass
class UnknownNode(Exception): pass
class UnknownFollowupIndex(Exception): pass

class StateMachine:
    def __init__(self, states=None):
        self.states = {}
        self.root = None

    def add(self, name, *followups):
        if self.root is None:
            self.root = name

        self.states[name] = followups

    def walker(self, entry = None):
        if entry is not None and entry not in self.states:
            raise UnknownNode(f'{entry} not in {self.states}') from KeyError

        node = entry if entry is not None else self.root
        followup_idx = 0
        while True:
            if node is None:
                break

            sent = yield node
            followup_idx = sent or 0

            try:
                next_node = self.states[node][followup_idx]
            except IndexError:
                raise UnknownFollowupIndex(node, followup_idx, self.states[node]) from IndexError

            if next_node is not None and next_node not in self.states:
                raise OpenGraph((node, next_node))

            node = next_node


    def __repr__(self):
        return (f'StateMachine({id(self)}\n' +
                '\n'.join([f'    {k}: {v}' for k, v in self.states.items()]) +
                ')')
