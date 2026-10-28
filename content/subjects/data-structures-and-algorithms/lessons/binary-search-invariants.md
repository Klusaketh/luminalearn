---
lesson: binary-search-invariants
title: Binary Search and Loop Invariants
summary: Halve a sorted search space at every step, use a loop invariant to get the boundaries right, and apply the same idea to any monotonic yes-or-no question.
minutes: 45
type: theory
objectives:
  - Implement binary search on a sorted array and state the loop invariant that makes it correct
  - Write lower-bound and upper-bound variants that find first and last positions and insertion points
  - Prevent off-by-one errors and infinite loops by choosing an interval convention and keeping to it
  - Apply binary search to monotonic predicates, such as searching for the smallest feasible answer, and analyse its O(log n) cost
---

## Introduction

To find a word in a printed dictionary, nobody starts at page one. You open the book near the middle, see whether the word comes before or after that page, and discard half of the book in one move. Repeating this, a 1,000-page dictionary takes about ten looks. That is **binary search**, and it turns a linear scan into a logarithmic one: searching a sorted list of a billion items takes about 30 comparisons.

The idea is simple, but the details are notoriously easy to get wrong. Jon Bentley reported in *Programming Pearls* that most professional programmers he tested could not write a correct binary search, and in 2006 Joshua Bloch described an integer-overflow bug that had sat for years in the binary search of Java's standard library. The reliable way to get it right is to state a **loop invariant**, a fact that is true before and after every iteration, and to write each line so that it preserves that invariant.

**Before you start:** you should know arrays, logarithms, and asymptotic notation.

## Core theory

### The invariant

Binary search needs a sorted array `a` and a target `x`. Keep a search interval and maintain this invariant:

> If `x` occurs in `a`, then it occurs at an index in the current interval.

This lesson uses **half-open intervals** `[lo, hi)`: `lo` is included and `hi` is excluded, so the interval holds `hi - lo` elements and is empty when `lo == hi`. Initially `lo = 0` and `hi = len(a)`, which covers the whole array, so the invariant holds.

Each iteration inspects the middle element, `mid = (lo + hi) // 2`:

- If `a[mid] == x`, return `mid`.
- If `a[mid] < x`, then because the array is sorted, every element at or before `mid` is less than `x`. Set `lo = mid + 1`.
- If `a[mid] > x`, every element at or after `mid` is greater than `x`. Set `hi = mid`.

Both updates discard only positions where `x` cannot be, so the invariant still holds. Both also make the interval strictly smaller (`mid` itself is always excluded), so the loop terminates. When the interval is empty, the invariant says `x` is not in the array.

### Cost

Each iteration at least halves the interval, so a search of $n$ elements makes at most $\lfloor \log_2 n \rfloor + 1$ comparisons with the middle element. That is 10 for $n = 1000$, 20 for a million, and 30 for a billion. The cost is $O(\log n)$ time and $O(1)$ extra space for the iterative version.

### Lower and upper bounds

With duplicates, "find any index of `x`" is often the wrong question. Two variants are more useful:

- **lower bound**: the first index `i` with `a[i] >= x`. It is also the position where `x` would be inserted to keep the array sorted, before any equal elements.
- **upper bound**: the first index `i` with `a[i] > x`, the insertion point after any equal elements.

The number of occurrences of `x` is `upper_bound - lower_bound`, computed in $O(\log n)$. For the lower bound, the invariant is: every element in `a[:lo]` is less than `x`, and every element in `a[hi:]` is at least `x`. The loop narrows the gap until `lo == hi`, and that position is the answer. Python's `bisect.bisect_left` and `bisect.bisect_right` implement exactly these two functions.

### Searching on a predicate

Binary search does not really need an array. It needs a **monotonic predicate**: a yes-or-no test $p(k)$ over a range of integers that is false up to some point and true from then on:

```text
k:     1  2  3  4  5  6  7  8
p(k):  F  F  F  F  T  T  T  T
                    ^ find the first T
```

Binary search finds the boundary with $O(\log(\text{range}))$ evaluations of $p$. Problems of the form "find the smallest capacity, speed, or time that is enough" often have this shape, because anything larger than enough is also enough. This technique is called **binary search on the answer**. The lower bound is the special case $p(i) = (a[i] \ge x)$.

### Choosing a convention

Many bugs come from mixing conventions. Two consistent templates are:

| Template | Loop condition | Updates | Use it for |
| :--- | :--- | :--- | :--- |
| Half-open `[lo, hi)` | `while lo < hi` | `lo = mid + 1` or `hi = mid` | lower and upper bounds, first true |
| Keep a known-good `lo` and a known-bad `hi` | `while hi - lo > 1` | `lo = mid` or `hi = mid` | last true, such as an integer square root |

In the second template, `lo` always satisfies the condition and `hi` never does. Because the loop runs only while there is a strict gap, `mid` is strictly between them, and each update makes progress.

In languages with fixed-width integers, computing `(lo + hi) / 2` can overflow when `lo + hi` exceeds the largest integer, which is the bug Bloch described. Use `lo + (hi - lo) / 2`. Python integers do not overflow, so the simpler form is safe there.

## Worked examples

### Example 1: Tracing a search

```python
def binary_search(a, x):
    lo, hi = 0, len(a)            # invariant: if x is in a, its index is in [lo, hi)
    steps = []
    while lo < hi:
        mid = (lo + hi) // 2
        steps.append((lo, hi, mid, a[mid]))
        if a[mid] == x:
            return mid, steps
        if a[mid] < x:
            lo = mid + 1          # x cannot be at mid or to its left
        else:
            hi = mid              # x cannot be at mid or to its right
    return -1, steps

a = [3, 8, 15, 21, 27, 34, 42, 56, 63, 71]
for x in (42, 4):
    index, steps = binary_search(a, x)
    print(f"search {x}: index {index}")
    for lo, hi, mid, value in steps:
        print(f"  lo={lo} hi={hi} mid={mid} a[mid]={value}")
```

Output:

```text
search 42: index 6
  lo=0 hi=10 mid=5 a[mid]=34
  lo=6 hi=10 mid=8 a[mid]=63
  lo=6 hi=8 mid=7 a[mid]=56
  lo=6 hi=7 mid=6 a[mid]=42
search 4: index -1
  lo=0 hi=10 mid=5 a[mid]=34
  lo=0 hi=5 mid=2 a[mid]=15
  lo=0 hi=2 mid=1 a[mid]=8
  lo=0 hi=1 mid=0 a[mid]=3
```

The search for 42 shrinks the interval from 10 elements to 4, 2, and 1. The unsuccessful search for 4 ends with `lo = hi = 1`, an empty interval. That final position is not wasted information: it is exactly where 4 would be inserted to keep the array sorted.

### Example 2: First and last positions with duplicates

```python
from bisect import bisect_left, bisect_right

def lower_bound(a, x):
    lo, hi = 0, len(a)            # invariant: a[:lo] < x and a[hi:] >= x
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(a, x):
    lo, hi = 0, len(a)            # invariant: a[:lo] <= x and a[hi:] > x
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo

a = [1, 2, 4, 4, 4, 7, 9]
for x in (4, 5, 0, 10):
    first, after = lower_bound(a, x), upper_bound(a, x)
    assert (first, after) == (bisect_left(a, x), bisect_right(a, x))
    print(f"x={x}: first >= x at {first}, first > x at {after}, count {after - first}")
```

Output:

```text
x=4: first >= x at 2, first > x at 5, count 3
x=5: first >= x at 5, first > x at 5, count 0
x=0: first >= x at 0, first > x at 0, count 0
x=10: first >= x at 7, first > x at 7, count 0
```

The two functions differ in a single character, `<` against `<=`, and the invariant comments say precisely what each one means. For the absent value 5, both return 5, the insertion point; for 10, both return 7, one past the end, which is a valid insertion point too. The `assert` confirms that the hand-written versions agree with the standard library.

### Example 3: Binary search on the answer

A conveyor must ship packages in the given order within a number of days. Each day the ship carries consecutive packages until the next one would exceed its capacity. What is the smallest capacity that finishes in 5 days?

```python
def days_needed(weights, capacity):
    days, load = 1, 0
    for w in weights:
        if load + w > capacity:   # start a new day
            days, load = days + 1, 0
        load += w
    return days

def min_capacity(weights, days):
    lo, hi = max(weights), sum(weights)   # the answer lies in [lo, hi]
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(weights, mid) <= days:
            hi = mid              # mid is enough; a smaller capacity might be too
        else:
            lo = mid + 1          # mid is too small, and so is everything below it
    return lo

weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(min_capacity(weights, 5), days_needed(weights, 15), days_needed(weights, 14))
```

Output:

```text
15 5 6
```

The predicate "capacity $c$ finishes within 5 days" is monotonic: a larger ship never needs more days. The capacity must be at least the heaviest package (10) and never needs to exceed the total (55), so binary search over $[10, 55]$ needs about $\log_2 46 \approx 6$ evaluations, each costing $O(n)$. The output confirms the boundary: capacity 15 takes 5 days, while 14 takes 6.

### Example 4: The last value that passes a test

The integer square root of $n$ is the largest $r$ with $r^2 \le n$. Here the predicate is true and then false, so the second template fits: `lo` is always a valid root and `hi` never is.

```python
from math import isqrt

def integer_sqrt(n):
    lo, hi = 0, n + 1             # invariant: lo * lo <= n < hi * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
    return lo

for n in (99, 100, 10**18 + 12345):
    print(n, integer_sqrt(n), integer_sqrt(n) == isqrt(n))
```

Output:

```text
99 9 True
100 10 True
1000000000000012345 1000000000 True
```

Because `hi - lo > 1` holds inside the loop, `mid` lies strictly between `lo` and `hi`, so setting `lo = mid` cannot stall. Even for $n$ above $10^{18}$, the loop runs only about 60 times, and exact integer arithmetic avoids the rounding errors that `int(n ** 0.5)` can suffer for large numbers.

## Applications

- **Searching sorted data:** lookups in sorted arrays and files, timestamps in logs, and the keys inside each node of a B-tree index.
- **Finding a regression with `git bisect`:** given a known good commit and a known bad one, Git checks out the midpoint and asks whether the bug is present, finding the first bad commit in about $\log_2(\text{commits})$ tests.
- **Numerical root finding:** the bisection method halves an interval in which a continuous function changes sign.
- **Capacity and parameter tuning:** the smallest server count, buffer size, or speed that meets a requirement, whenever more is never worse.
- **Library functions:** Python's `bisect` module, C++'s `std::lower_bound` and `std::upper_bound`, and Java's `Arrays.binarySearch`.

## Common mistakes

- **Mixing conventions,** for example initialising `hi = len(a) - 1` (closed interval) but looping `while lo < hi` and setting `hi = mid` (half-open updates), which skips the last element.
- **Writing `lo = mid` in a `while lo < hi` loop.** When `hi = lo + 1`, `mid` equals `lo` and the loop never ends. Use `lo = mid + 1`, or switch to the `hi - lo > 1` template.
- **Overflow in `(lo + hi) / 2`** with fixed-width integers; compute `lo + (hi - lo) / 2`.
- **Searching unsorted data** or applying binary search on the answer to a predicate that is not monotonic; the halving step is only valid when one side can be ruled out.
- **Assuming the index returned for a duplicated value is the first one.** Plain binary search returns some matching index; use the lower bound for the first.

## Revision notes

- Requirement: a sorted array or a monotonic predicate.
- Invariant (half-open): if `x` is present, it is in `[lo, hi)`. Each step keeps the invariant and shrinks the interval.
- At most $\lfloor \log_2 n \rfloor + 1$ probes: $O(\log n)$ time, $O(1)$ space.
- Lower bound: first `a[i] >= x`. Upper bound: first `a[i] > x`. Count = upper − lower.
- Binary search on the answer: find the first value for which a monotonic test becomes true.
- Two safe templates: `while lo < hi` with `lo = mid + 1` / `hi = mid`, or `while hi - lo > 1` with `lo = mid` / `hi = mid`.

## Practice questions

:::question basic
What is the maximum number of probes binary search makes on a sorted array of 1000 elements? Of one million?
:::answer
At most $\lfloor \log_2 n \rfloor + 1$. For $n = 1000$, $\log_2 1000 \approx 9.97$, so at most $9 + 1 = 10$ probes. For one million, $\log_2 10^6 \approx 19.9$, so at most 20. Multiplying the input by 1000 adds only about 10 probes.
:::

:::question basic
Trace the search for 27 in the array from Example 1. List `lo`, `hi`, and `mid` at each step.
:::answer
Step 1: `lo=0, hi=10, mid=5`; `a[5] = 34 > 27`, so `hi = 5`. Step 2: `lo=0, hi=5, mid=2`; `a[2] = 15 < 27`, so `lo = 3`. Step 3: `lo=3, hi=5, mid=4`; `a[4] = 27`, found at index 4 after three probes.
:::

:::question intermediate
A programmer writes `while lo < hi: mid = (lo + hi) // 2; if a[mid] <= x: lo = mid else: hi = mid - 1`. Show an input where this loops forever.
:::answer
Take `a = [5, 7]` and `x = 5`, starting from `lo = 0`, `hi = 1` (both meant as inclusive bounds). Then `mid = (0 + 1) // 2 = 0` and `a[0] = 5 <= 5`, so `lo = mid = 0`. Nothing changes, and the loop repeats forever. Whenever `hi = lo + 1`, floor division gives `mid = lo`, so the update `lo = mid` makes no progress. Fix it with `mid = (lo + hi + 1) // 2` or by using a template whose updates always shrink the interval.
:::

:::question intermediate
Explain how to count how many times a value occurs in a sorted array of $n$ elements in $O(\log n)$ time.
:::answer
Compute the lower bound (first index with `a[i] >= x`) and the upper bound (first index with `a[i] > x`) with two binary searches. The occurrences of `x` occupy exactly the indices from the lower bound up to, but not including, the upper bound, so the count is their difference. Each search is $O(\log n)$, so the total is $O(\log n)$, however many copies there are.
:::

:::question intermediate
Versions 1 to 1000 of a program were released in order. Some version introduced a bug, and every later version also has it. With a function `is_bad(v)`, how many calls do you need to find the first bad version, and why?
:::answer
About 10. The predicate `is_bad` is false and then true, so it is monotonic, and binary search finds the first true value. Each call halves the range of candidates: $1000 \to 500 \to 250 \to \dots$, which needs $\lceil \log_2 1000 \rceil = 10$ calls. This is the procedure `git bisect` automates.
:::

:::question advanced
A sorted array of distinct numbers has been rotated, for example `[15, 18, 2, 3, 6, 12]`. Find the minimum in $O(\log n)$ time and justify each step.
:::answer
Use `lo = 0`, `hi = n - 1` and loop while `lo < hi`. Compare `a[mid]` with `a[hi]`. If `a[mid] > a[hi]`, the rotation point (the minimum) lies strictly to the right of `mid`, so set `lo = mid + 1`. Otherwise the segment from `mid` to `hi` is sorted and the minimum is at `mid` or to its left, so set `hi = mid`. The invariant is that the minimum's index lies in `[lo, hi]`, and each step keeps it and shrinks the interval. For the example: `lo=0, hi=5, mid=2`, `2 < 12`, so `hi = 2`; `lo=0, hi=2, mid=1`, `18 > 2`, so `lo = 2`. The loop ends with index 2, value 2.
:::

:::question advanced
Prove that `lower_bound` in Example 2 returns the first index whose element is at least `x`.
:::answer
Invariant: every element of `a[:lo]` is less than `x`, and every element of `a[hi:]` is at least `x`. Initially both slices are empty, so it holds. If `a[mid] < x`, then by sortedness everything up to `mid` is less than `x`, so setting `lo = mid + 1` preserves the first part. Otherwise `a[mid] >= x`, so everything from `mid` onwards is at least `x`, and setting `hi = mid` preserves the second part. Each step shrinks `hi - lo`, so the loop ends with `lo == hi`. Then everything before `lo` is less than `x` and everything from `lo` onwards is at least `x`, so `lo` is the first index with `a[i] >= x` (or `len(a)` if there is none).
:::

## Further learning

- **Next:** *Elementary & Linear-Time Sorting* covers how to produce the sorted arrays that binary search relies on.
- **Related:** *Binary Search Trees (BST)* applies the same halving idea to a dynamic, pointer-based structure.
- **Related:** *Asymptotic Notations* explains why $O(\log n)$ grows so slowly.
