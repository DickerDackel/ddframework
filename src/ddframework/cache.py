from collections import UserDict


__all__ = ['cache', 'Cache', 'add', 'get', 'get_all']

_cache = {}

class Cache(UserDict):
    def __setitem__(self, key, item):
        if key in self.data:
            raise RuntimeError('Overwriting an existing item is not allowed.  Use `replace()`')

        super().__setitem__(key, item)

    def replace(self, key, item):
        self.data[key] = item

    def get_all(self, *names):
        if len(names) == 1:
            return self.data[names[0]]
        else:
            return (self.data[key] for key in names)

    def has(self, *names):
        return all(key in self.data for key in names)

cache = Cache()


def add(obj, name):
    """Adds or overwrites a cache entry."""
    _cache[name] = obj


def rm(name):
    """Removes name from the cache."""
    try:
        del _cache[name]
    except KeyError:
        return False
    else:
        return True


def get(name):
    """Get name from the cache."""
    try:
        return _cache[name]
    except KeyError:
        return None


def get_all(names):
    """Get all names from cache in a list."""
    return (get(name) for name in names)


def has(*names):
    """Check if all names are in the cache."""
    return all(name in _cache for name in names)
