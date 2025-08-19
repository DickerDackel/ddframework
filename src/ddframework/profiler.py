# Stolen from Lucy - https://github.com/kadir014/lucyframework

"""

    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from collections import defaultdict, deque, UserDict
from dataclasses import dataclass
from contextlib import contextmanager
from time import perf_counter

# Deque is faster but cannot be resized during runtime. So define it here.
ACCUMULATE_LIMIT = 60


@dataclass
class ProfiledStat:
    avg: float
    min: float
    max: float
    sma: float
    latest: float

    def __str__(self) -> str:
        return ' '.join(str(_) for _ in (self.avg, self.sma, self.min, self.max, self.latest))
        return f"err={abs(self.avg - self.sma): .10f}  avg={self.avg: .10f}  sma={self.sma: .10f}  min={self.min: .10f}  max={self.max: .10f}  latest={self.latest: .10f}"

    def __iter__(self):
        yield self.avg
        yield self.min
        yield self.max
        yield self.sma
        yield self.latest


class Profiler(UserDict):
    """
    Profiler and stat storage class.
    """

    def __init__(self) -> None:
        def factory() -> dict:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "sma": 0.0, "latest":
                    0.0, "acc": deque([], maxlen=ACCUMULATE_LIMIT)}

        self.data = defaultdict(factory)

    def __getitem__(self, key: str) -> ProfiledStat:
        """ Return a profiled stat. """
        return ProfiledStat(
            self.data[key]["avg"],
            self.data[key]["min"],
            self.data[key]["max"],
            self.data[key]["sma"],
            self.data[key]["latest"],
        )

    @contextmanager
    def profile(self, stat: str) -> None:
        """
        Profile piece of code.

        Parameters
        ----------
        stat
            Stat name to store the profiled code as.
        """

        start = perf_counter()

        try: yield None

        finally:
            elapsed = perf_counter() - start
            self.accumulate(stat, elapsed)

    def accumulate(self, stat: str, value: float) -> None:
        """
        Accumulate stat value.

        Parameters
        ----------
        stat
            Stat name to accumulate.
        value
            Stat value to accumulate.
        """

        t = self.data[stat]
        acc = t["acc"]
        acc.append(value)

        t["avg"] = sum(acc) / len(acc)
        t["min"] = min(acc)
        t["max"] = max(acc)
        t["sma"] += (value - acc[0]) / ACCUMULATE_LIMIT
        t["latest"] = value

profiler = Profiler()
