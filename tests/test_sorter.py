from __future__ import annotations

import random

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
    # Large enough to stress the algorithm while keeping runtime practical
    for n in [610, 987, 1597, 2584, 4181]:
        comparisons, gt, out = _run_simulated_sort(n, seed=0xBABABABABABABABA)
        assert out == gt
        assert comparisons <= expected_max_comparisons(n)


def test_empty_list() -> None:
    """Test that empty list is handled correctly."""
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting([])
    assert sorter.is_done()
    assert sorter.current_pair() is None
    result = sorter.finish_sorting()
    assert result == []


def test_single_element() -> None:
    """Test that single element list is handled correctly."""
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting([42])
    assert sorter.is_done()
    assert sorter.current_pair() is None
    result = sorter.finish_sorting()
    assert result == [42]


def test_already_sorted_ascending() -> None:
    """Test list that is already sorted in ascending order (should be reversed)."""
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
    """Test list that is already sorted in descending order."""
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
    """Test list with all identical values."""
    items = [5, 5, 5, 5, 5, 5, 5]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    comparisons = 0
    while True:
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        # When equal, choose RIGHT (current <= pivot)
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
        comparisons += 1

    result = sorter.finish_sorting()
    expected = sorted(items, reverse=True)
    assert result == expected
    assert comparisons <= expected_max_comparisons(len(items))


def test_duplicate_values() -> None:
    """Test list with some duplicate values."""
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
    """Test list with negative numbers."""
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
    """Test list with both positive and negative numbers."""
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
    """Test calling finish_sorting before completing all comparisons."""
    items = [5, 2, 8, 1, 9, 3, 7, 4, 6]
    sorter: PairwiseSorter[int] = PairwiseSorter()
    sorter.start_sorting(items)

    # Make a few comparisons
    for _ in range(3):
        pair = sorter.current_pair()
        if pair is None:
            break
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)

    # Finish early - should return partially sorted + unsorted
    result = sorter.finish_sorting()
    # Result should contain all items, just potentially in different order
    assert len(result) == len(items)
    assert set(result) == set(items)


def test_multiple_start_sorting_calls() -> None:
    """Test that multiple start_sorting calls reset the state correctly."""
    sorter: PairwiseSorter[int] = PairwiseSorter()

    # First sort
    items1 = [3, 1, 4, 1, 5]
    sorter.start_sorting(items1)
    while sorter.current_pair() is not None:
        pair = sorter.current_pair()
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
    result1 = sorter.finish_sorting()
    assert result1 == sorted(items1, reverse=True)

    # Second sort (should reset state)
    items2 = [9, 2, 6, 5, 3]
    sorter.start_sorting(items2)
    while sorter.current_pair() is not None:
        pair = sorter.current_pair()
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
    result2 = sorter.finish_sorting()
    assert result2 == sorted(items2, reverse=True)


def test_make_choice_when_not_comparing() -> None:
    """Test that make_choice is safe to call when not in CompareState."""
    sorter: PairwiseSorter[int] = PairwiseSorter()

    # Call make_choice before start_sorting (should be safe)
    sorter.make_choice(Choice.LEFT)
    sorter.make_choice(Choice.RIGHT)

    # Start with empty list (DoneState immediately)
    sorter.start_sorting([])
    assert sorter.is_done()

    # Call make_choice when done (should be safe)
    sorter.make_choice(Choice.LEFT)
    sorter.make_choice(Choice.RIGHT)

    result = sorter.finish_sorting()
    assert result == []


def test_current_pair_when_not_comparing() -> None:
    """Test that current_pair returns None when not in CompareState."""
    sorter: PairwiseSorter[int] = PairwiseSorter()

    # Before start_sorting
    assert sorter.current_pair() is None

    # After empty list
    sorter.start_sorting([])
    assert sorter.current_pair() is None

    # After single element
    sorter.start_sorting([42])
    assert sorter.current_pair() is None

    # After completing sort
    sorter.start_sorting([3, 1, 4])
    while sorter.current_pair() is not None:
        pair = sorter.current_pair()
        current, pivot = pair
        choice = Choice.LEFT if current > pivot else Choice.RIGHT
        sorter.make_choice(choice)
    assert sorter.current_pair() is None
