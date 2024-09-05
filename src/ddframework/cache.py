_cache = {}

def add(texture, name):
    if name not in _cache:
        _cache[name] = texture

def get(name):
    return _cache[name] if name in _cache else None


def get_all(names):
    return [get(name) for name in names]

__all__ = ['add', 'get', 'get_all']
