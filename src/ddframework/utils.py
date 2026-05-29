from random import random

import glm


def random_vector(length: float = 1) -> glm.vec2:
    """Return a random vec2 with the given length"""

    angle = random() * glm.two_pi()
    v = glm.vec2(1, 0) * length

    return glm.rotate(v, angle)


def xpath(dict_: dict, path: str):
    """Return the value in dict_ described by path (separated by `.`)"""

    res = dict_
    for k in path.split('.'):
        res = res[k]

    return res
