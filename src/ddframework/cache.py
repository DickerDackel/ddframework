from collections import UserDict

_cache = {}


class Cache(UserDict):
    def __missing__(self, key):
        self.data[key] = self.__class__()
        return self.data[key]

    # ?!? WHY ?!?
    #
    # def __setitem__(self, key, item):
    #     if key in self.data:
    #         raise RuntimeError('Overwriting an existing item is not allowed.  Use `replace()`')
    #
    #     super().__setitem__(key, item)
    #
    # def replace(self, key, item):
    #     self.data[key] = item

    def get_all(self, *names):
        if len(names) == 1:
            return self.data[names[0]]
        else:
            return (self.data[key] for key in names)

    def has(self, *names):
        return all(key in self.data for key in names)

    def xpath(self, path: str, early=False) -> object:
        """Return the value in dict_ described by path (separated by `.`)

        :param path: Inspired by xpath, the path into the dictionary
        :param early: If the path can't be followed up to the end, still return what already matched
        :return: The cached object

        """

        res = self.data
        for k in path.split('.'):
            try:
                res = res[k]
            except TypeError, KeyError:
                if early: return res
                raise

        return res

    def xpath_put(self, path: str, value: object) -> None:
        """Insert values into the nested dict addressed by the xpath.

        :param path: The dotted path into the dict
        :param value: The value to insert

        """

        node = self.data
        steps = path.split('.')
        for k in steps[:-1]:
            if k not in node:
                node[k] = self.__class__()
            node = node[k]

        node[steps[-1]] = value


cache = Cache()
