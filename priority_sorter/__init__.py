"""Priority Sorter Python package."""

from .items import Item, DEFAULT_ITEM_LABELS, DEFAULT_ITEMS, seeded_items
from .sorter import Choice, PairwiseSorter, expected_max_comparisons

__all__ = [
    "run_app",
    "Item",
    "DEFAULT_ITEM_LABELS",
    "DEFAULT_ITEMS",
    "seeded_items",
    "Choice",
    "PairwiseSorter",
    "expected_max_comparisons",
]


def run_app() -> None:
    """
    Lazy entrypoint for the Tkinter GUI.

    Importing tkinter eagerly breaks environments (like headless CI) that only
    need the algorithm, so we defer the heavy import.
    """
    from .gui import run_app as _run_app

    _run_app()
