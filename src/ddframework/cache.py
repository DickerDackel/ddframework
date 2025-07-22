__all__ = ['add', 'get', 'get_all']

_cache = {}

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
