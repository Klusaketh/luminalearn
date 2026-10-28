---
lesson: sliding-window-two-pointers
title: Sliding Window and Two-Pointer Techniques
summary: Turn quadratic subarray and pair searches into single linear passes by moving two indices through an array.
minutes: 55
type: theory
objectives:
  - Recognise problems that can be solved with converging two pointers, fast and slow pointers on an array, or a sliding window
  - Implement fixed-size and variable-size sliding windows and explain why each element enters and leaves the window at most once
  - Prove that the two-pointer pair search on a sorted array never skips a valid answer
  - Analyse the time and space complexity of these techniques and compare them with brute force
---

## Introduction

Many array problems ask about **pairs** of elements or **contiguous subarrays**: does any pair sum to a target, what is the longest stretch without a repeated character, what is the largest sum of any $k$ consecutive values? The direct approach checks every pair or every subarray, which costs $\Theta(n^2)$ or worse. For an array of a million elements that is around $10^{12}$ steps.

Two closely related techniques reduce these problems to a single pass. **Two pointers** keep two indices into the array and move them according to a rule that safely discards candidates. A **sliding window** maintains a contiguous range `[left, right]` and updates a running summary as the range slides, instead of recomputing it from scratch. Both run in $\Theta(n)$ time because each index only ever moves forward.

**Before you start:** you need arrays, Big-O notation, and basic Python loops and dictionaries.

## Core theory

### Pattern 1: Converging pointers on a sorted array

Place one pointer at each end of a **sorted** array and move them toward each other. At each step, compare the current pair with the goal and move the pointer that can improve it.

For "find two numbers that sum to `target`" in sorted order:

- if `a[left] + a[right] == target`, you have found the pair;
- if the sum is **too small**, increase it by moving `left` right (every pair using the current `a[left]` with a smaller partner is even smaller);
- if the sum is **too large**, decrease it by moving `right` left.

**Why nothing is skipped.** When the sum is too small, `a[left]` paired with any element at or before `right` gives a sum no larger than the current one, because the array is sorted. So `a[left]` cannot be part of a solution with any remaining partner, and discarding it is safe. The symmetric argument justifies moving `right`. Each step discards one element, so the loop runs at most $n - 1$ times: $\Theta(n)$ time, $\Theta(1)$ extra space.

### Pattern 2: Same-direction pointers (read and write)

Two pointers can also move in the same direction: a **read** pointer scans every element, and a **write** pointer marks where the next kept element should go. This compacts an array in place, for example removing duplicates from a sorted array or removing all zeros, in $\Theta(n)$ time and $\Theta(1)$ space.

### Pattern 3: Fixed-size sliding window

To compute something over every window of exactly $k$ consecutive elements, compute the first window, then slide: add the element that enters on the right and remove the element that leaves on the left. Each slide costs $\Theta(1)$, so all $n - k + 1$ windows cost $\Theta(n)$ in total, instead of $\Theta(nk)$ for recomputing each window.

### Pattern 4: Variable-size sliding window

For "longest" or "shortest" subarray problems, the window grows and shrinks:

1. Extend `right` one step, adding `a[right]` to the window's state.
2. While the window violates the condition, remove `a[left]` from the state and advance `left`.
3. The window is now valid; record its length if it is the best so far.

This works when the condition is **monotone**: if a window is invalid, every larger window containing it is also invalid (for a longest-valid search), so it is safe to shrink from the left. Each element is added once when `right` passes it and removed at most once when `left` passes it, so the total work is $\Theta(n)$ even though there is a loop inside a loop.

### Choosing the pattern

| Problem shape | Technique |
| :--- | :--- |
| Pair or triplet with a target sum in a sorted array | Converging pointers |
| Remove or compact elements in place | Read and write pointers |
| Statistic over every window of size $k$ | Fixed sliding window |
| Longest or shortest subarray satisfying a monotone condition | Variable sliding window |

### When it does not apply

Sliding windows require a condition that behaves monotonically as the window grows. "Longest subarray with sum at most $S$" works when all numbers are non-negative, because adding elements can only increase the sum. With negative numbers allowed, a window that is too large can become valid again by including a negative value, so shrinking from the left can skip answers; prefix sums or other techniques are needed instead.

## Worked examples

### Example 1: Pair with a target sum

```python
def pair_with_sum(sorted_values, target):
    left, right = 0, len(sorted_values) - 1
    while left < right:
        total = sorted_values[left] + sorted_values[right]
        if total == target:
            return sorted_values[left], sorted_values[right]
        if total < target:
            left += 1
        else:
            right -= 1
    return None

data = [1, 3, 4, 6, 8, 11, 14]
print(pair_with_sum(data, 17))
print(pair_with_sum(data, 2))
```

Output:

```text
(3, 14)
None
```

Trace for target 17:

| left | right | pair | sum | action |
| :---: | :---: | :---: | :---: | :--- |
| 0 | 6 | 1, 14 | 15 | too small, move left |
| 1 | 6 | 3, 14 | 17 | found |

Seven elements, two comparisons. The brute-force approach would check up to 21 pairs.

### Example 2: Maximum sum of any $k$ consecutive values

```python
def max_window_sum(values, k):
    window = sum(values[:k])
    best = window
    for right in range(k, len(values)):
        window += values[right] - values[right - k]   # one in, one out
        best = max(best, window)
    return best

print(max_window_sum([4, 2, 12, 3, 8, 1, 7], 3))
```

Output:

```text
23
```

The windows of size 3 have sums 18, 17, 23, 12, 16. Each new sum is obtained from the previous one by adding the entering value and subtracting the leaving one, so the algorithm does one addition and one subtraction per element.

### Example 3: Longest substring without repeating characters

```python
def longest_unique(text):
    last_seen = {}
    left = best = 0
    for right, ch in enumerate(text):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1        # jump past the earlier copy
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best

for s in ("abcabcbb", "bbbb", "pwwkew", ""):
    print(repr(s), longest_unique(s))
```

Output:

```text
'abcabcbb' 3
'bbbb' 1
'pwwkew' 3
'' 0
```

The window `text[left:right+1]` always contains distinct characters. When `ch` already appears inside the window, the window cannot be extended without a repeat, so `left` jumps just past the earlier occurrence. Each index moves forward only, giving $\Theta(n)$ time and $O(\min(n, \sigma))$ space, where $\sigma$ is the alphabet size. For `"pwwkew"` the best windows are `"wke"` and `"kew"`.

### Example 4: Remove duplicates from a sorted array in place

```python
def dedupe_sorted(values):
    write = 0
    for read in range(len(values)):
        if read == 0 or values[read] != values[read - 1]:
            values[write] = values[read]
            write += 1
    del values[write:]          # trim the leftover tail
    return values

print(dedupe_sorted([1, 1, 2, 3, 3, 3, 7, 9, 9]))
```

Output:

```text
[1, 2, 3, 7, 9]
```

`read` visits every element; `write` advances only when a new value appears. Because the array is sorted, duplicates are adjacent, so comparing with the previous element is enough. Time $\Theta(n)$; the only extra memory is two integers.

## Applications

- **Network and systems monitoring.** Rate limiters and dashboards compute moving averages or request counts over the last $k$ seconds with a sliding window.
- **Signal and time-series processing.** Moving averages smooth sensor readings and stock prices using exactly the fixed-window update.
- **Text processing.** Finding the shortest snippet containing all query words, or the longest run of unique tokens, uses variable windows.
- **Data cleaning.** Compacting arrays and removing sentinel values in place uses read and write pointers.
- **Merging sorted data.** Two pointers walking two sorted lists merge them in linear time, which is the core of merge sort and of database merge joins.

## Common mistakes

- **Using converging pointers on an unsorted array.** The safety argument depends on sorted order; sort first ($\Theta(n \log n)$) or use a hash set.
- **Recomputing the window from scratch** on each step, which silently brings back $\Theta(nk)$ time.
- **Moving `left` backwards.** In Example 3, `left` must only increase; checking `last_seen[ch] >= left` prevents a stale earlier occurrence from dragging it back.
- **Applying a sliding window when the condition is not monotone,** such as sums with negative numbers.
- **Off-by-one errors in window length.** The window `[left, right]` inclusive has length `right - left + 1`.

## Revision notes

- Converging pointers on sorted data: move `left` when the value is too small, `right` when too large. $\Theta(n)$ time, $\Theta(1)$ space.
- Read/write pointers compact arrays in place in one pass.
- Fixed window of size $k$: update by adding the entering element and removing the leaving one.
- Variable window: expand right; shrink left while invalid; record the best valid window.
- Total work is linear because each pointer only moves forward and each element enters and leaves at most once.
- Requires sorted input (converging) or a monotone condition (variable window).

## Practice questions

:::question basic
Trace the two-pointer pair search on `[2, 5, 7, 9, 12, 15]` with target 21. List each pair checked and the action taken.
:::answer
(2, 15) sum 17, too small, move left. (5, 15) sum 20, too small, move left. (7, 15) sum 22, too large, move right. (7, 12) sum 19, too small, move left. (9, 12) sum 21, found. Five pairs were checked, compared with up to 15 for brute force.
:::

:::question basic
What is the time complexity of computing the sum of every window of size $k$ in an array of length $n$ (a) by summing each window separately and (b) with a sliding window?
:::answer
(a) There are $n - k + 1$ windows and each sum costs $k$ additions, so $\Theta((n - k + 1)k)$, which is $\Theta(nk)$ when $k$ is much smaller than $n$. (b) $\Theta(n)$: the first window costs $k$, and each of the remaining windows costs a constant number of operations.
:::

:::question intermediate
Find the length of the longest substring without repeating characters in `"abcbdeaf"` by tracing the variable window. Give the substring.
:::answer
The window grows to `abc` (length 3). At the second `b` (index 3), the earlier `b` is at index 1, so `left` jumps to 2, giving `cb`. Then it grows to `cbdea` and `cbdeaf`, length 6, with no repeats (`a` at index 0 is before `left`, so it does not force a jump). The answer is 6, the substring `"cbdeaf"`.
:::

:::question intermediate
Explain why the variable sliding window for "longest subarray with sum at most $S$" fails when the array contains negative numbers. Give a small counterexample.
:::answer
The window shrinks from the left whenever the sum exceeds $S$, assuming that any larger window would also exceed it. With negative numbers that is false. Take `[5, -10, 5]` and $S = 3$. The window `[5]` already exceeds 3, so the algorithm shrinks it and never considers subarrays that start with that first 5. But the whole array sums to $0 \le 3$ and has length 3, so the true answer is 3. The algorithm finds only length 2 (`[-10, 5]`). Prefix sums with a different search are needed when values can be negative.
:::

:::question intermediate
Write the core loop that moves all zeros in a list to the end while keeping the order of the non-zero elements, using $O(1)$ extra space.
:::answer
Use read and write pointers: for each `read` index, if `values[read] != 0`, swap `values[write]` and `values[read]` and increment `write`. After the loop, all non-zero elements occupy indices `0` to `write - 1` in their original order and the zeros fill the rest. One pass gives $\Theta(n)$ time and two integer variables give $O(1)$ space.
:::

:::question advanced
Given a sorted array, count the pairs `(i, j)` with `i < j` and `a[i] + a[j] <= T` in $\Theta(n)$ time. Explain the pointer movement and why it counts correctly.
:::answer
Start `left = 0`, `right = n - 1`, `count = 0`. While `left < right`: if `a[left] + a[right] <= T`, then `a[left]` pairs validly with every index from `left + 1` to `right` (all those partners are at most `a[right]`), so add `right - left` to the count and move `left` right. Otherwise `a[right]` is too large to pair with `a[left]` or anything after it, so move `right` left. Each step moves one pointer, giving $\Theta(n)$ steps, and every valid pair is counted exactly once, at the moment its left element is processed.
:::

## Further learning

- **Next:** *String Manipulation & Encodings* looks at strings as arrays of characters and how they are stored.
- **Related:** *Fast & Slow Pointer Techniques* applies the two-pointer idea to linked lists to detect cycles and find middles.
- **Related:** *Merge Sort & QuickSort* uses two pointers to merge sorted halves and to partition around a pivot.
