from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from ddframework.cache import cache


class SlurpConfig(NamedTuple):
    handler: Callable
    hierarchy: str | None = None


def default_slurp_handler(fname: Path):
    with open(fname) as f:
        return f.read()


def null_slurp_handler(fname: Path):
    pass


def slurp_assets(assets: Path, suffix_slurpconfig_map: dict[str, Callable]):
    def default_slurp_handler(p: Path) -> object:
        with open(p) as f:
            return f.read()

    for root, dirs, files in assets.walk():
        for f in files:
            p = root / f
            suffix = p.suffix

            cfg = suffix_slurpconfig_map.get(suffix, None)
            if cfg is None:
                continue

            item = cfg.handler(p)

            p = p.relative_to(assets).with_suffix('')
            if cfg.hierarchy:
                p = cfg.hierarchy / p

            xpath = str(p).replace('/', '.')
            print(f'{xpath=}')
            cache.xpath_put(str(xpath), item)
