from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Iterable, List, Sequence, Tuple, TypeVar


T = TypeVar("T")


class Choice(Enum):
    """Represents which option the user picked during a comparison."""

    LEFT = "left"
    RIGHT = "right"


@dataclass
class EmptyState(Generic[T]):
    """Represents an idle sorter with no work to do."""

    items: List[T] = field(default_factory=list)


@dataclass
class CompareState(Generic[T]):
    """Represents an ongoing binary-search insertion."""

    unsorted: List[T]
    sorted: List[T]
    lo: int
    hi: int


@dataclass
class DoneState(Generic[T]):
    """Represents a finished sort."""

    sorted: List[T]


SortState = EmptyState[T] | CompareState[T] | DoneState[T]


class PairwiseSorter(Generic[T]):
    """Interactive priority sorter using safe pairwise comparisons."""

    def __init__(self) -> None:
        self.state: SortState[T] = EmptyState([])

    def start_sorting(self, items: Sequence[T]) -> None:
        """
        Initialize the sorter with a fresh batch of items.

        Mirrors the Rust logic by seeding the ordered list with the first entry
        and treating the rest as a stack processed from the tail backwards.
        """
        data = list(items)
        if not data:
            self.state = EmptyState([])
            return

        if len(data) == 1:
            self.state = DoneState([data[0]])
            return

        sorted_block = [data[0]]
        # Treat the remainder as a stack where the current item is last().
        unsorted_block = data[1:]
        self.state = CompareState(
            unsorted=unsorted_block,
            sorted=sorted_block,
            lo=0,
            hi=len(sorted_block),
        )

    def make_choice(self, choice: Choice) -> None:
        """Apply the user's decision and advance the binary-search insertion."""
        if not isinstance(self.state, CompareState):
            return

        state = self.state
        if not state.unsorted:
            self.state = DoneState(state.sorted.copy())
            return

        mid = (state.lo + state.hi) // 2

        if choice == Choice.LEFT:
            state.hi = mid
        else:
            state.lo = mid + 1

        if state.lo < state.hi:
            return

        insert_pos = state.lo
        current = state.unsorted.pop()
        state.sorted.insert(insert_pos, current)

        if not state.unsorted:
            self.state = DoneState(state.sorted.copy())
            return

        state.lo = 0
        state.hi = len(state.sorted)

    def finish_sorting(self, fallback: Iterable[T] | None = None) -> List[T]:
        """
        Return the best-known ordering and reset transient comparison state.

        If invoked mid-session, the partially sorted prefix is concatenated with
        the untouched suffix to mirror the Rust behavior.
        """
        if isinstance(self.state, DoneState):
            return list(self.state.sorted)
        if isinstance(self.state, CompareState):
            stitched = list(self.state.sorted)
            stitched.extend(self.state.unsorted)
            return stitched
        if fallback is None:
            return list(self.state.items)
        return list(fallback)

    def current_pair(self) -> Tuple[T, T] | None:
        """Return the active comparison pair (current item, pivot)."""
        if not isinstance(self.state, CompareState):
            return None
        if not self.state.unsorted:
            return None
        mid = (self.state.lo + self.state.hi) // 2
        current = self.state.unsorted[-1]
        pivot = self.state.sorted[mid]
        return current, pivot

    def is_done(self) -> bool:
        return isinstance(self.state, DoneState)


def expected_max_comparisons(n: int) -> int:
    """Upper-bound used by the Rust tests, ported verbatim."""
    if n <= 1:
        return 0
    total = 0
    for k in range(1, n):
        x = k + 1
        ceil_log2 = (x - 1).bit_length()
        total += ceil_log2
    return total
