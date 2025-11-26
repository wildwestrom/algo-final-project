from __future__ import annotations

import random
import traceback
from collections.abc import Callable

from priority_sorter.sorter import Choice, PairwiseSorter, expected_max_comparisons


def _run_simulated_sort(n: int, seed: int) -> tuple[int, list[int], list[int]]:
    rng = random.Random(seed)
    items = list(range(n))
    rng.shuffle(items)

    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0

    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    sorted_items = sorter.finish_sorting(items)
    ground_truth = sorted(items, reverse=True)
    return comparisons, ground_truth, sorted_items


def test_sorts_matches_ground_truth_small_sizes() -> None:
    for n in [0, 1, 2, 3, 5, 8, 13]:
        comparisons, gt, out = _run_simulated_sort(n, seed=0xDEADBEEFCAFEBABE)
        assert out == gt
        assert comparisons <= expected_max_comparisons(n)


def test_sorts_matches_ground_truth_medium_sizes() -> None:
    for n in [21, 34, 55, 89, 144, 233, 377]:
        comparisons, gt, out = _run_simulated_sort(n, seed=0x1234_5678_9ABC_DEF0)
        assert out == gt
        assert comparisons <= expected_max_comparisons(n)


def test_sorts_matches_ground_truth_large_sizes() -> None:
    for n in [610, 987, 1597, 2584, 4181]:
        comparisons, gt, out = _run_simulated_sort(n, seed=0xBABABABABABABABA)
        assert out == gt
        assert comparisons <= expected_max_comparisons(n)


def test_empty_list() -> None:
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting([])
    assert sorter.is_done()
    assert sorter.current_pair() is None
    result = sorter.finish_sorting()
    assert result == []


def test_single_element() -> None:
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting([42])
    assert sorter.is_done()
    assert sorter.current_pair() is None
    result = sorter.finish_sorting()
    assert result == [42]


def test_already_sorted_ascending() -> None:
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0
    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    result = sorter.finish_sorting()
    expected = sorted(items, reverse=True)
    assert result == expected
    assert comparisons <= expected_max_comparisons(len(items))


def test_already_sorted_descending() -> None:
    items = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0
    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    result = sorter.finish_sorting()
    expected = sorted(items, reverse=True)
    assert result == expected
    assert comparisons <= expected_max_comparisons(len(items))


def test_all_same_values() -> None:
    items = [5, 5, 5, 5, 5, 5, 5]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0
    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    result = sorter.finish_sorting()
    expected = sorted(items, reverse=True)
    assert result == expected
    assert comparisons <= expected_max_comparisons(len(items))


def test_duplicate_values() -> None:
    items = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0
    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    result = sorter.finish_sorting()
    expected = sorted(items, reverse=True)
    assert result == expected
    assert comparisons <= expected_max_comparisons(len(items))


def test_negative_numbers() -> None:
    items = [-5, -2, -8, -1, -9, -3, -7, -4, -6]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0
    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    result = sorter.finish_sorting()
    expected = sorted(items, reverse=True)
    assert result == expected
    assert comparisons <= expected_max_comparisons(len(items))


def test_mixed_positive_negative() -> None:
    items = [-3, 5, -1, 0, 4, -2, 1, -5, 2, -4, 3]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0
    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    result = sorter.finish_sorting()
    expected = sorted(items, reverse=True)
    assert result == expected
    assert comparisons <= expected_max_comparisons(len(items))


def test_finish_sorting_mid_sort() -> None:
    items = [5, 2, 8, 1, 9, 3, 7, 4, 6]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    for _ in range(3):
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)

    result = sorter.finish_sorting()
    assert len(result) == len(items)
    assert set(result) == set(items)


def test_multiple_start_sorting_calls() -> None:
    sorter: PairwiseSorter[int] = PairwiseSorter()

    items1 = [3, 1, 4, 1, 5]
    sorter.start_sorting(items1)
    while sorter.current_pair() is not None:
        current, pivot = sorter.current_pair()
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
    result1 = sorter.finish_sorting()
    assert result1 == sorted(items1, reverse=True)

    items2 = [9, 2, 6, 5, 3]
    sorter.start_sorting(items2)
    while sorter.current_pair() is not None:
        current, pivot = sorter.current_pair()
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
    result2 = sorter.finish_sorting()
    assert result2 == sorted(items2, reverse=True)


def test_make_choice_when_not_comparing() -> None:
    sorter: PairwiseSorter[int] = PairwiseSorter()

    sorter.make_choice(Choice.LEFT)
    sorter.make_choice(Choice.RIGHT)

    sorter.start_sorting([])
    assert sorter.is_done()

    sorter.make_choice(Choice.LEFT)
    sorter.make_choice(Choice.RIGHT)

    result = sorter.finish_sorting()
    assert result == []


def test_current_pair_when_not_comparing() -> None:
    sorter: PairwiseSorter[int] = PairwiseSorter()

    assert sorter.current_pair() is None

    sorter.start_sorting([])
    assert sorter.current_pair() is None

    sorter.start_sorting([42])
    assert sorter.current_pair() is None

    sorter.start_sorting([3, 1, 4])
    while sorter.current_pair() is not None:
        current, pivot = sorter.current_pair()
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
    assert sorter.current_pair() is None


def _collect_tests() -> list[tuple[str, Callable[[], None]]]:
    tests: list[tuple[str, Callable[[], None]]] = []
    for name, obj in globals().items():
        if name.startswith("test_") and callable(obj):
            tests.append((name, obj))  # type: ignore[arg-type]
    tests.sort(key=lambda pair: pair[0])
    return tests


def _run_tests(tests: list[tuple[str, Callable[[], None]]]) -> int:
    failures = 0
    for name, func in tests:
        try:
            func()
        except AssertionError:
            failures += 1
            print(f"FAIL: {name}")
            traceback.print_exc()
        except Exception:
            failures += 1
            print(f"ERROR: {name}")
            traceback.print_exc()
        else:
            print(f"PASS: {name}")
    total = len(tests)
    print(f"Ran {total} test{'s' if total != 1 else ''}.")
    if failures:
        print(f"{failures} failure{'s' if failures != 1 else ''}.")
    else:
        print("All tests passed.")
    return failures


def main() -> int:
    tests = _collect_tests()
    if not tests:
        print("No tests discovered.")
        return 1
    return 1 if _run_tests(tests) else 0


if __name__ == "__main__":
    raise SystemExit(main())
