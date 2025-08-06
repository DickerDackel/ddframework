from collections import UserList
from typing import Any, Callable, Sequence


class BulkRunner:
    # Make this private to avoid name conflicts with subclasses
    _bulkrunner_groups: set['BulkRunnerGroup'] = set()

    def __init__(self, *groups: 'BulkRunnerGroup') -> None:
        for g in groups:
            g.append(self)
            self._bulkrunner_groups.append(g)

    def kill(self) -> None:
        for g in self._bulkrunner_groups:
            g.remove(self)
        self._bulkrunner_groups = None


class BulkRunnerGroup(UserList):
    def __init__(self, *runners: BulkRunner) -> None:
        self.data = [_ for _ in runners]  # can't use copy on iterators

    def _remove_from_runner(self, runner: BulkRunner) -> None:
        if runner is not None and hasattr(runner, '_bulkrunner_groups'):
            try:
                runner._bulkrunner_groups.remove(self)
            except ValueError:
                pass

    def _add_to_runner(self, runner: BulkRunner) -> None:
        if self not in runner._bulkrunner_groups:
            runner._bulkrunner_groups.add(self)

    def __setitem__(self, i: int, item: BulkRunner) -> None:
        self._validate_runner(item)
        self._remove_from_runner(self.data[i])
        self._add_to_runner(item)
        self.data[i] = item

    def __delitem__(self, i: int) -> None:
        self._validate_runner(self.data[i])
        self._remove_from_runner(self.data[i])
        del self.data[i]

    def _call_runners(self, name: str) -> Callable:
        def inner(*args: Any, **kwargs: Any) -> object | None:
            for r in self.data:
                fn = getattr(r, name)
                return fn(*args, **kwargs)
        return inner

    def __getattr__(self, attr: str) -> object:
        return self._call_runners(attr)

    def append(self, runner: BulkRunner) -> None:
        self._validate_runner(runner)
        self._add_to_runner(runner)
        self.data.append(runner)

    def extend(self, runners: Sequence[BulkRunner]) -> None:
        for r in runners:
            self._validate_runner(r)
            self._add_to_runner(r)
            self.data.append(r)

    def insert(self, i: int, item: BulkRunner) -> None:
        self._validate_runner(item)
        self._add_to_runner(item)
        self.data.insert(i, item)

    def pop(self, i: int) -> BulkRunner:
        item = self.data.pop(i)
        self._remove_from_runner(item)
        return item

    def remove(self, item: BulkRunner) -> None:
        self._remove_from_runner(item)
        self.data.remove(item)

    def clear(self) -> None:
        for item in self.data:
            self._remove_from_runner(item)
        self.data.clear()


def _validate_runner(runner: BulkRunner) -> None:
    if not isinstance(runner, BulkRunner):
        raise TypeError('Item is not subclassed from BulkRunner')

    if not (hasattr(runner, 'kill') and hasattr(runner, '_bulkrunner_groups')):
        raise RuntimeError('Item is not properly initialized.  Call init of BulkRunner')
