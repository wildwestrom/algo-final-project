from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Item:
    """Simple mutable representation of a priority item."""

    description: str
    is_editing: bool = False

    def clone(self) -> "Item":
        return Item(self.description, self.is_editing)


DEFAULT_ITEM_LABELS: List[str] = [
    "Study for algorithms class",
    "Study for other classes",
    "Buy my mom flowers",
    "Finish reading my book",
    "Fix the button on my jacket",
    "Buy groceries",
    "Call my friend",
    "Go to the gym",
]

DEFAULT_ITEMS: List[Item] = [Item(label) for label in DEFAULT_ITEM_LABELS]


def seeded_items() -> List[Item]:
    """Return a fresh, independent copy of the default items."""
    return [item.clone() for item in DEFAULT_ITEMS]
