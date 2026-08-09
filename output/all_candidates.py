# All candidates from code generation v3.1

# ============================================================
# Agent 0: Generator (score=0.53)
# ============================================================

def quicksort(arr: list) -> None:
    """Sort list in-place via quicksort (not truly in-place, creates lists)."""
    if len(arr) <= 1:
        return
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    arr[:] = left + middle + right

# ============================================================
# Agent 1: Reviewer (score=0.93)
# ============================================================

Issues found:
- Not truly in-place (creates new lists left/middle/right)
- O(n) extra space instead of O(log n)
- Worst case O(n^2) if all elements equal
- No handling of empty list (works but not explicit)

# ============================================================
# Agent 2: Optimizer (score=1.03)
# ============================================================

def quicksort(arr: list, low: int = 0, high: int = None) -> None:
    """In-place quicksort with Lomuto partition."""
    if high is None:
        high = len(arr) - 1
    if low < high:
        p = _partition(arr, low, high)
        quicksort(arr, low, p - 1)
        quicksort(arr, p + 1, high)

def _partition(arr: list, low: int, high: int) -> int:
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# ============================================================
# Agent 3: Tester (score=1.03)
# ============================================================

import pytest
from generated_quicksort import quicksort

def test_empty():
    arr = []
    quicksort(arr)
    assert arr == []

def test_single():
    arr = [1]
    quicksort(arr)
    assert arr == [1]

def test_sorted():
    arr = [1, 2, 3, 4, 5]
    quicksort(arr)
    assert arr == [1, 2, 3, 4, 5]

def test_reverse():
    arr = [5, 4, 3, 2, 1]
    quicksort(arr)
    assert arr == [1, 2, 3, 4, 5]

def test_duplicates():
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    quicksort(arr)
    assert arr == [1, 1, 2, 3, 4, 5, 5, 6, 9]

def test_large_random():
    import random
    arr = [random.randint(0, 1000) for _ in range(100)]
    expected = sorted(arr)
    quicksort(arr)
    assert arr == expected

