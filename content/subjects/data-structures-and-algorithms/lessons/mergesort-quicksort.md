---
lesson: mergesort-quicksort
title: Merge Sort and QuickSort
summary: Two divide-and-conquer sorts that reach O(n log n) - merge sort by splitting and merging, quicksort by partitioning around a pivot - and how their trade-offs shape real sorting libraries.
minutes: 60
type: theory
objectives:
  - Implement merge sort, trace its splitting and merging, and derive its Theta(n log n) running time
  - Implement quicksort with Lomuto partitioning and explain how pivot choice decides its performance
  - Compare merge sort and quicksort by worst case, average case, memory, stability, and practical speed
  - Explain how production algorithms such as Timsort and introsort combine these ideas
---

## Introduction

The elementary sorts take $\Theta(n^2)$ time, which is hopeless for a million items: about $5 \times 10^{11}$ steps. The decision-tree argument shows that comparison sorting cannot beat $\Theta(n \log n)$, about $2 \times 10^7$ steps for a million items, so there is a lot of room to improve. The two most important algorithms that close the gap both use **divide and conquer**: split the problem into smaller pieces, solve them recursively, and combine the results.

They split the work in opposite ways. **Merge sort** (described by John von Neumann in 1945) divides the array blindly in half and does its real work while combining, merging two sorted halves. **Quicksort** (Tony Hoare, published in 1961) does its real work while dividing, partitioning the elements around a pivot so that combining is trivial. Merge sort is predictable and stable but needs extra memory; quicksort works in place and is usually faster in practice, but a bad pivot can make it quadratic. Understanding why explains the design of every serious sorting library.

**Before you start:** you should know recursion, the elementary sorts, and the idea of a recurrence.

## Core theory

### Merge sort

```text
merge_sort(a):
    if len(a) <= 1: return a
    left  = merge_sort(first half of a)
    right = merge_sort(second half of a)
    return merge(left, right)
```

**Merging** two sorted lists takes linear time with two pointers: repeatedly compare the front elements, move the smaller one to the output, and copy whatever remains when one list runs out. Merging lists of total length $n$ makes at most $n - 1$ comparisons. Taking from the left list when the fronts are equal keeps the sort **stable**.

**Running time.** Let $T(n)$ be the time to sort $n$ elements:

$$T(n) = 2T(n/2) + \Theta(n).$$

Draw the recursion tree: the top level merges $n$ elements; the next level has two merges of $n/2$, also $n$ in total; and so on. There are $\log_2 n$ levels, each costing $\Theta(n)$, so $T(n) = \Theta(n \log n)$. The split does not depend on the data, so this holds in the best, average, and worst case.

**Memory.** Merging arrays needs a $\Theta(n)$ buffer. Merge sort is therefore not in place for arrays, but it is ideal for **linked lists** (merging relinks nodes, needing no buffer) and for **external sorting** of data too large for memory, where sorted runs on disk are merged sequentially.

### Quicksort

```text
quicksort(a, lo, hi):
    if lo < hi:
        p = partition(a, lo, hi)     # pivot ends at index p
        quicksort(a, lo, p - 1)
        quicksort(a, p + 1, hi)
```

**Partitioning** rearranges `a[lo..hi]` around a pivot value so that smaller elements come before it and the others after it, and the pivot lands in its final sorted position. The **Lomuto scheme** takes the last element as the pivot and scans left to right, keeping the invariant that `a[lo:i]` holds the elements smaller than the pivot; at the end, it swaps the pivot into position `i`. Hoare's original scheme scans inward from both ends and performs fewer swaps on average.

**Running time.** Partitioning $k$ elements costs $\Theta(k)$. The total depends on how evenly the pivot splits the array:

- **Best and average case:** balanced or reasonably balanced splits give $T(n) = 2T(n/2) + \Theta(n) = \Theta(n \log n)$. Even a consistent 1-to-9 split gives $\Theta(n \log n)$, with a larger constant. For a random input, quicksort makes about $2n \ln n \approx 1.39\, n \log_2 n$ comparisons on average.
- **Worst case:** if the pivot is always the smallest or largest element, one side is empty and $T(n) = T(n-1) + \Theta(n) = \Theta(n^2)$. With "last element" pivots, this happens on **already sorted input**, a very common case in practice.

**Choosing a pivot.** A **random** pivot makes the expected time $\Theta(n \log n)$ for every input, because no fixed input is consistently bad. **Median-of-three** (the median of the first, middle, and last elements) defends against sorted and reversed inputs cheaply. Inputs with **many duplicate keys** need **three-way partitioning** into less-than, equal, and greater-than parts; otherwise equal elements all fall on one side and the running time degrades towards quadratic.

**Memory.** Quicksort partitions in place. Its only extra memory is the recursion stack. If the implementation recurses into the **smaller** part and loops on the larger one, each recursive call handles at most half the elements, so the stack depth is $O(\log n)$ even in the worst case.

**Stability.** Partitioning swaps elements over long distances, so quicksort is not stable.

### Comparison

| | Merge sort | Quicksort |
| :--- | :--- | :--- |
| Worst case | $\Theta(n \log n)$ | $\Theta(n^2)$ (rare with good pivots) |
| Average case | $\Theta(n \log n)$ | $\Theta(n \log n)$, about $1.39 n \log_2 n$ comparisons |
| Extra memory (arrays) | $\Theta(n)$ | $O(\log n)$ stack |
| Stable | yes | no |
| Where the work happens | combining (merge) | dividing (partition) |
| Practical speed | good; sequential access | usually fastest in memory; cache-friendly, few moves |

### Sorting in practice

- **Timsort** (Tim Peters, 2002) is the sort behind Python's `sorted` and `list.sort`, and Java uses it for sorting objects. It is a merge sort that first detects already sorted **runs** in the data, extends short runs with insertion sort, and merges runs with careful balancing rules. It is stable and runs in $O(n)$ on already sorted input.
- **Introsort** (David Musser, 1997) is the design used by common C++ `std::sort` implementations. It runs quicksort, switches to heapsort if the recursion gets deeper than about $2 \log_2 n$ (guaranteeing $O(n \log n)$), and finishes small partitions with insertion sort.
- Java sorts arrays of primitive values with a **dual-pivot quicksort**, which partitions around two pivots at once; stability does not matter for primitives, because equal values are indistinguishable.

## Worked examples

### Example 1: Merge sort, level by level

```python
def merge(left, right):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:              # <= takes from the left on ties: stable
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])                     # at most one of these is non-empty
    out.extend(right[j:])
    return out

def merge_sort(a, depth=0):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid], depth + 1)
    right = merge_sort(a[mid:], depth + 1)
    merged = merge(left, right)
    print("  " * depth + f"merge {left} + {right} -> {merged}")
    return merged

merge_sort([38, 27, 43, 3, 9, 82, 10])
```

Output:

```text
    merge [27] + [43] -> [27, 43]
  merge [38] + [27, 43] -> [27, 38, 43]
    merge [3] + [9] -> [3, 9]
    merge [82] + [10] -> [10, 82]
  merge [3, 9] + [10, 82] -> [3, 9, 10, 82]
merge [27, 38, 43] + [3, 9, 10, 82] -> [3, 9, 10, 27, 38, 43, 82]
```

Indentation shows recursion depth. The merges happen bottom-up, in post-order: a merge can run only after both halves are sorted. The final merge interleaves `[27, 38, 43]` with `[3, 9, 10, 82]`, taking 3, 9, and 10 from the right before anything from the left, and finishes by copying the leftover 82. There are $\lceil \log_2 7 \rceil = 3$ levels of merging.

### Example 2: Partitioning, and why the pivot matters

```python
def partition(a, lo, hi, counter):           # Lomuto scheme: the pivot is a[hi]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        counter[0] += 1
        if a[j] < pivot:                     # invariant: a[lo:i] < pivot
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]                # place the pivot between the parts
    return i

def quicksort(a, lo, hi, counter, middle_pivot=False):
    while lo < hi:
        if middle_pivot:                     # move the middle element into the pivot slot
            mid = (lo + hi) // 2
            a[mid], a[hi] = a[hi], a[mid]
        p = partition(a, lo, hi, counter)
        if p - lo < hi - p:                  # recurse on the smaller part, loop on the larger
            quicksort(a, lo, p - 1, counter, middle_pivot)
            lo = p + 1
        else:
            quicksort(a, p + 1, hi, counter, middle_pivot)
            hi = p - 1

def comparisons(data, middle_pivot=False):
    a, counter = data[:], [0]
    quicksort(a, 0, len(a) - 1, counter, middle_pivot)
    assert a == sorted(data)
    return counter[0]

def scrambled(n, seed=12345):                # a Fisher-Yates shuffle driven by a fixed generator
    keys, state = list(range(1, n + 1)), seed
    for i in range(n - 1, 0, -1):
        state = (1103515245 * state + 12345) % 2**31
        j = state % (i + 1)
        keys[i], keys[j] = keys[j], keys[i]
    return keys

a = [7, 2, 1, 8, 6, 3, 5, 4]
p = partition(a, 0, len(a) - 1, [0])
print("pivot 4 lands at index", p, "->", a)

n = 2000
print("last pivot, sorted input:   ", comparisons(list(range(n))))
print("last pivot, scrambled input:", comparisons(scrambled(n)))
print("middle pivot, sorted input: ", comparisons(list(range(n)), middle_pivot=True))
```

Output:

```text
pivot 4 lands at index 3 -> [2, 1, 3, 4, 6, 7, 5, 8]
last pivot, sorted input:    1999000
last pivot, scrambled input: 25990
middle pivot, sorted input:  17964
```

After partitioning, 4 sits at index 3, its final sorted position, with 2, 1, and 3 to its left and the larger values to its right; neither side is sorted yet. The counts show the pivot's influence. On sorted input, the last element is always the maximum, so every partition peels off a single element: $n(n-1)/2 = 1{,}999{,}000$ comparisons. On scrambled input, the same code makes 25,990 comparisons, below the average-case estimate $2n \ln n \approx 30{,}400$. Choosing the middle element as the pivot turns the sorted input into the best case, 17,964 comparisons. Because the code recurses only into the smaller part, even the quadratic case never builds a deep call stack.

## Applications

- **General-purpose library sorts:** Timsort in Python and for Java objects, introsort in C++ standard libraries, and dual-pivot quicksort for Java primitives.
- **External sorting:** databases and tools such as the Unix `sort` command sort data larger than memory by sorting chunks and then merging the sorted runs, which is merge sort's merging step at scale.
- **Linked lists:** merge sort sorts linked lists in $O(n \log n)$ time with no extra buffer, which is why it is the usual choice there.
- **Selection:** quickselect uses quicksort's partition to find the $k$-th smallest element, such as a median, in expected linear time, recursing into only one side.
- **Counting inversions:** a modified merge sort counts the inversions in an array in $O(n \log n)$, which is used to compare rankings.

## Common mistakes

- **Using `<` instead of `<=` when merging,** which takes equal elements from the right first and makes merge sort unstable.
- **Picking the first or last element as the pivot on data that may be sorted,** which triggers the $\Theta(n^2)$ worst case on one of the most common kinds of input.
- **Ignoring duplicates in quicksort.** With many equal keys, a two-way partition puts them all on one side; use three-way partitioning.
- **Recursing on both sides naively,** which can reach a recursion depth of $n$ in the worst case; recurse on the smaller side first.
- **Forgetting the leftover elements** at the end of a merge, which silently drops data.
- **Assuming quicksort is always faster.** When a worst-case guarantee or stability is required, merge sort, heapsort, or a hybrid is the right choice.

## Revision notes

- Merge sort: split in half, sort both halves, merge in linear time. $T(n) = 2T(n/2) + \Theta(n) = \Theta(n \log n)$ in all cases. Stable; $\Theta(n)$ extra space for arrays.
- Quicksort: partition around a pivot, then sort both sides. Average $\Theta(n \log n)$ (about $1.39 n \log_2 n$ comparisons), worst $\Theta(n^2)$. In place, not stable.
- Lomuto partition: pivot = last element; invariant `a[lo:i] < pivot`; finally swap the pivot to index `i`.
- Good pivots: random or median-of-three; three-way partitioning for duplicates; recurse on the smaller side for $O(\log n)$ stack depth.
- Timsort = run detection + insertion sort + merging (stable, adaptive). Introsort = quicksort + heapsort fallback + insertion sort.

## Practice questions

:::question basic
Merge `[1, 4, 9]` and `[2, 3, 10]`. How many comparisons are made?
:::answer
Compare 1 and 2: output 1. Compare 4 and 2: output 2. Compare 4 and 3: output 3. Compare 4 and 10: output 4. Compare 9 and 10: output 9. The left list is now empty, so 10 is copied without a comparison. Result: `[1, 2, 3, 4, 9, 10]` after 5 comparisons, which is $n - 1$ for $n = 6$ elements.
:::

:::question basic
Why does merge sort take $\Theta(n \log n)$ time even on an already sorted array?
:::answer
Merge sort always splits in the middle, whatever the data, so its recursion tree always has $\log_2 n$ levels. Every level merges all $n$ elements, costing $\Theta(n)$ per level even when no element needs to move. So the total is $\Theta(n \log n)$ for every input. (Timsort avoids this by detecting existing runs.)
:::

:::question intermediate
Partition `[3, 8, 2, 5, 1, 4, 7, 6]` with the Lomuto scheme, using the last element as the pivot. Give the final array and the pivot's index.
:::answer
The pivot is 6. Scanning left to right, the elements smaller than 6 (3, 2, 5, 1, 4) are swapped, in order, into the front: after the scan the array is `[3, 2, 5, 1, 4, 8, 7, 6]` with `i = 5`. The final swap exchanges `a[5]` and the pivot, giving `[3, 2, 5, 1, 4, 6, 7, 8]`. The pivot 6 is at index 5, which is its position in sorted order.
:::

:::question intermediate
Quicksort always chooses the last element as its pivot. Describe an input of size $n$ that causes $\Theta(n^2)$ time, and two ways to prevent it.
:::answer
An already sorted array: the last element is always the maximum, so each partition leaves $n - 1$ elements on one side and none on the other, giving $(n-1) + (n-2) + \dots + 1 = \Theta(n^2)$ comparisons. A reversed array is equally bad. Prevent it by choosing the pivot at random, which makes the expected time $\Theta(n \log n)$ for every input, or by using median-of-three, which picks a good pivot for sorted and reversed inputs.
:::

:::question intermediate
Which algorithm would you choose for each case: (a) sorting a singly linked list, (b) sorting records that are already sorted by date, by name, while keeping the date order for equal names, (c) sorting a large array of integers in memory where speed matters most?
:::answer
(a) Merge sort: merging relinks nodes with no extra buffer, while quicksort needs random access to partition efficiently. (b) A stable sort, such as merge sort or Timsort, so that records with equal names stay in date order. (c) Quicksort with a good pivot strategy (or introsort), which is usually the fastest in-memory comparison sort; for integers with a small key range or fixed width, radix sort is also worth considering.
:::

:::question advanced
Explain why recursing into the smaller part first limits quicksort's stack depth to $O(\log n)$, even when the running time is $\Theta(n^2)$.
:::answer
Each recursive call is made on the smaller of the two parts, which holds at most half of the current elements. The larger part is handled by the loop in the same stack frame, without a new call. So along any chain of nested calls, the subarray size at least halves at every level, and after $\log_2 n$ levels it is down to one element. The depth is therefore at most about $\log_2 n$, whatever the pivots are. The total work can still be quadratic, but the call stack cannot overflow.
:::

:::question advanced
What happens when Lomuto quicksort sorts an array in which every element is equal? How does three-way partitioning fix it?
:::answer
The test `a[j] < pivot` is never true, so every partition puts all the other elements on the right and the pivot at the far left. Each step removes one element, giving $\Theta(n^2)$ comparisons. Three-way partitioning (the Dutch national flag scheme) divides the range into elements less than, equal to, and greater than the pivot, and recurses only on the less-than and greater-than parts. For an all-equal array, a single partition places everything in the equal part, so the sort finishes in $\Theta(n)$ time.
:::

## Further learning

- **Next:** *Call Stack & Recurrence Trees* solves recurrences such as $T(n) = 2T(n/2) + n$ in general, including with the Master Theorem.
- **Related:** *Elementary & Linear-Time Sorting* explains the $\Omega(n \log n)$ lower bound that both algorithms meet.
- **Related:** *Min & Max Heap Implementation* covers heapsort, introsort's fallback.
