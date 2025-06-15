__all__ = ['StateMachine']

class NoRoot(Exception): pass
class OpenGraph(Exception): pass
class UnknownNode(Exception): pass
class UnknownFollowupIndex(Exception): pass

class StateMachine:
    def __init__(self, states=None):
        self.states = {} if states is None else {s[0]: s[1:] for s in states}

    def add(self, name, *followups):
        self.states[name] = followups

    def walker(self, entry):
        if entry not in self.states:
            raise UnknownNode(f'{entry} not in {self.states}') from KeyError

        node = entry
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
