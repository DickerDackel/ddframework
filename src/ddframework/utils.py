from collections.abc import Iterator
from random import random

import glm


def angle_of(v: glm.vec2) -> float:
    """Return the angle of ``v`` in degrees, since glm lacks that.

    :param v: The vector in question
    :return: Angle of ``v`` in degrees

    """

    return glm.degrees(glm.atan2(v.y, v.x))


def chunks(start: float, end: float, steps: int) -> Iterator[float]:
    """Loop over the float range ``start`` - ``end`` in steps.

    :param start: First step of the interval
    :param end: Final step of the interval
    :param steps: The number of steps in total

    .. important:: This is an active fencepost problem.  This function gives
        you the number of posts, **not** the number of segments between them.

        So ``list(frange(0, 10, 4))`` will result in ``[0.0, 3.333..., 6.666..., 10]```
        instead of the probably expected ``[0, 2.5, 5, 7.5]``

    """
    steps -= 1
    step = (end - start) / steps
    for i in range(steps):
        yield start + step * i

    yield end


def random_vector(length: float = 1) -> glm.vec2:
    """Return a random vec2 with the given length"""

    angle = random() * glm.two_pi()
    v = glm.vec2(1, 0) * length

    return glm.rotate(v, angle)


def xpath(dict_: dict, path: str, early=False):
    """Return the value in dict_ described by path (separated by `.`)"""

    res = dict_
    for k in path.split('.'):
        try:
            res = res[k]
        except TypeError, KeyError:
            if early: return res
            raise

    return res
