"""
Sorting algorithms implemented as generators that yield snapshots for visualization.
Each yield is a tuple: (array_copy, info_dict)
info_dict can include keys:
 - 'active': list of active/compared indices
 - 'sorted': list of indices considered sorted
 - 'label': optional text label

Supported algorithms: bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort
"""
from typing import Generator, List, Tuple, Dict
import random

Snapshot = Tuple[List[int], Dict]


def bubble_sort(arr: List[int]) -> Generator[Snapshot, None, None]:
    a = arr.copy()
    n = len(a)
    if n == 0:
        yield a, {'active': [], 'sorted': []}
        return
    yield a.copy(), {'active': [], 'sorted': []}
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            yield a.copy(), {'active': [j, j + 1], 'sorted': list(range(n - i, n))}
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                yield a.copy(), {'active': [j, j + 1], 'sorted': list(range(n - i, n))}
        if not swapped:
            break
    yield a.copy(), {'active': [], 'sorted': list(range(n))}


def selection_sort(arr: List[int]) -> Generator[Snapshot, None, None]:
    a = arr.copy()
    n = len(a)
    yield a.copy(), {'active': [], 'sorted': []}
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield a.copy(), {'active': [min_idx, j], 'sorted': list(range(i))}
            if a[j] < a[min_idx]:
                min_idx = j
                yield a.copy(), {'active': [min_idx], 'sorted': list(range(i))}
        if i != min_idx:
            a[i], a[min_idx] = a[min_idx], a[i]
            yield a.copy(), {'active': [i, min_idx], 'sorted': list(range(i + 1))}
    yield a.copy(), {'active': [], 'sorted': list(range(n))}


def insertion_sort(arr: List[int]) -> Generator[Snapshot, None, None]:
    a = arr.copy()
    n = len(a)
    yield a.copy(), {'active': [], 'sorted': []}
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            yield a.copy(), {'active': [j, j + 1], 'sorted': list(range(i + 1, n))}
            a[j + 1] = a[j]
            j -= 1
            yield a.copy(), {'active': [j + 1], 'sorted': list(range(i + 1, n))}
        a[j + 1] = key
        yield a.copy(), {'active': [j + 1], 'sorted': list(range(i + 1, n))}
    yield a.copy(), {'active': [], 'sorted': list(range(n))}


# Merge sort with yield-from for visualization

def merge_sort(arr: List[int]) -> Generator[Snapshot, None, None]:
    a = arr.copy()
    n = len(a)
    if n == 0:
        yield a, {'active': [], 'sorted': []}
        return

    yield a.copy(), {'active': [], 'sorted': []}

    def merge(left: int, mid: int, right: int):
        L = a[left:mid]
        R = a[mid:right]
        i = j = 0
        k = left
        while i < len(L) and j < len(R):
            yield a.copy(), {'active': [k], 'label': f'merging {left}:{mid} + {mid}:{right}'}
            if L[i] <= R[j]:
                a[k] = L[i]
                i += 1
            else:
                a[k] = R[j]
                j += 1
            k += 1
            yield a.copy(), {'active': [k - 1], 'label': 'after write'}
        while i < len(L):
            a[k] = L[i]
            i += 1
            k += 1
            yield a.copy(), {'active': [k - 1]}
        while j < len(R):
            a[k] = R[j]
            j += 1
            k += 1
            yield a.copy(), {'active': [k - 1]}

    def sort_rec(left: int, right: int):
        if right - left <= 1:
            return
        mid = (left + right) // 2
        yield from sort_rec(left, mid)
        yield from sort_rec(mid, right)
        yield from merge(left, mid, right)

    yield from sort_rec(0, n)
    yield a.copy(), {'active': [], 'sorted': list(range(n))}


# Quick sort with Lomuto partition scheme

def quick_sort(arr: List[int]) -> Generator[Snapshot, None, None]:
    a = arr.copy()
    n = len(a)
    if n == 0:
        yield a, {'active': [], 'sorted': []}
        return
    yield a.copy(), {'active': [], 'sorted': []}

    def partition(low: int, high: int) -> Generator[Snapshot, None, int]:
        pivot = a[high]
        i = low
        for j in range(low, high):
            yield a.copy(), {'active': [j, high], 'label': 'compare to pivot'}
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                yield a.copy(), {'active': [i, j], 'label': 'swap smaller'}
                i += 1
        a[i], a[high] = a[high], a[i]
        yield a.copy(), {'active': [i, high], 'label': 'pivot swap'}
        return i

    def quick_rec(low: int, high: int):
        if low < high:
            # partition yields many snapshots; we need to capture them and get pivot index
            gen = partition(low, high)
            pivot_index = None
            for item in gen:
                # partition yields snapshots as (array, info) until it returns the pivot index
                yield item
            # After generator finishes partition, we still need pivot index -- recompute
            # (since generator can't return via yield easily here), find pivot position
            # The Lomuto partition places pivot at the correct position i; find index of pivot value
            pivot_val = a[low:high + 1][-(1)]  # not reliable; instead locate correctly
            # find pivot by scanning -- pivot is at position where left <= pivot < right
            # Simpler: find index where a[k] was originally pivot value; we'll search for the value that was at high
            # But the value may be duplicated; fallback is to use last swap logic: find first index p in [low,high] such that all left < pivot and all right >= pivot
            # Simpler approach: choose pivot index by scanning where element equals pivot and either low==index or a[index-1] <= a[index]
            # For robustness, recompute pivot index by finding smallest index where elements to left <= elements to right
            # Instead, use standard partition implementation inline to get pivot index deterministically.
            # We'll re-implement partition inline to get pivot index and avoid complexity.
            pass

    # Because returning a pivot from a generator is awkward above, we'll implement quicksort iteratively using an explicit stack
    stack = [(0, n - 1)]
    while stack:
        low, high = stack.pop()
        if low >= high:
            continue
        pivot = a[high]
        i = low
        for j in range(low, high):
            yield a.copy(), {'active': [j, high], 'label': 'compare to pivot'}
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                yield a.copy(), {'active': [i, j], 'label': 'swap smaller'}
                i += 1
        a[i], a[high] = a[high], a[i]
        yield a.copy(), {'active': [i, high], 'label': 'pivot placed'}
        # push subarrays
        stack.append((low, i - 1))
        stack.append((i + 1, high))

    yield a.copy(), {'active': [], 'sorted': list(range(n))}


# Utility to create a random array

def random_array(n: int, low: int = 1, high: int = 100) -> List[int]:
    return [random.randint(low, high) for _ in range(n)]
