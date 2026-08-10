# Tests from Molecular AI v4

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
    arr = [1, 2, 3]
    quicksort(arr)
    assert arr == [1, 2, 3]

def test_reverse():
    arr = [3, 2, 1]
    quicksort(arr)
    assert arr == [1, 2, 3]

def test_duplicates():
    arr = [2, 2, 1, 1, 3]
    quicksort(arr)
    assert arr == [1, 1, 2, 2, 3]