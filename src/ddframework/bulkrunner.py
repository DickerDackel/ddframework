from collections import UserList


class BulkRunner:
    # Make this private to avoid name conflicts with subclasses
    _bulkrunner_groups = []

    def __init__(self, *groups):
        for g in groups:
            g.append(self)
            self._bulkrunner_groups.append(g)

    def kill(self):
        for g in self._bulkrunner_groups:
            g.remove(self)
        self._bulkrunner_groups = None


class BulkRunnerGroup(UserList):
    def __init__(self, *runners):
        self.data = [_ for _ in runners]  # can't use copy on iterators

    def _remove_from_runner(self, runner):
        if runner is not None and hasattr(runner, '_bulkrunner_groups'):
            try:
                runner._bulkrunner_groups.remove(self)
            except ValueError:
                pass

    def _validate_runner(self, runner):
        if not isinstance(runner, BulkRunner):
            raise TypeError('Item is not subclassed from BulkRunner')

        if not (hasattr(runner, 'kill') and hasattr(runner, '_bulkrunner_groups')):
            raise RuntimeError('Item is not properly initialized.  Call init of BulkRunner')

    def _add_to_runner(self, runner):
        if self not in runner._bulkrunner_groups:
            runner._bulkrunner_groups.append(self)

    def __setitem__(self, i, item: BulkRunner):
        self._validate_runner(item)
        self._remove_from_runner(self.data[i])
        self._add_to_runner(item)
        self.data[i] = item

    def __delitem__(self, i):
        self._validate_runner(self.data[i])
        self._remove_from_runner(self.data[i])
        del self.data[i]

    def _call_runners(self, name):
        def inner(*args, **kwargs):
            for r in self.data:
                fn = getattr(r, name)
                fn(*args, **kwargs)
        return inner

    def __getattr__(self, attr):
        return self._call_runners(attr)

    def append(self, runner):
        self._validate_runner(runner)
        self._add_to_runner(runner)
        self.data.append(runner)

    def extend(self, runners):
        for r in runners:
            self._validate_runner(r)
            self._add_to_runner(r)
            self.data.append(r)

    def insert(self, i, item):
        self._validate_runner(item)
        self._add_to_runner(item)
        self.data.insert(i, item)

    def pop(self, i):
        item = self.data.pop(i)
        self._remove_from_runner(item)

    def remove(self, item):
        self._remove_from_runner(item)
        self.data.remove(item)

    def clear(self):
        for item in self.data:
            self._remove_from_runner(item)
        self.data.clear()
