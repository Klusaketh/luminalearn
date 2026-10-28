---
lesson: elementary-linear-sorting
title: Elementary and Linear-Time Sorting
summary: Insertion, selection, and bubble sort, the Omega(n log n) lower bound for comparison sorting, and counting and radix sort, which beat it by not comparing keys.
minutes: 50
type: theory
objectives:
  - Implement insertion sort, selection sort, and bubble sort and trace each on a small array
  - Compare the elementary sorts by comparisons, swaps, adaptivity to nearly sorted input, and stability
  - Explain the Omega(n log n) lower bound for comparison sorting using decision trees
  - Implement counting sort and LSD radix sort and state when they outperform comparison sorts
---

## Introduction

Sorting is one of the most studied problems in computer science, because so much else depends on it: binary search needs sorted data, databases sort to answer `ORDER BY` and to join tables, and many algorithms begin with "first, sort the input". This lesson covers two families of sorting algorithms at opposite ends of the story.

The **elementary sorts**, insertion, selection, and bubble sort, are short, in place, and quadratic in the worst case. They are worth knowing well: insertion sort is genuinely fast on small or nearly sorted inputs, and production libraries use it inside their sophisticated hybrids. We then ask how fast *any* sort that works by comparing elements can possibly be, and prove that the answer is $\Omega(n \log n)$. Finally, **counting sort** and **radix sort** sidestep that bound by never comparing keys at all, sorting integers in linear time.

**Before you start:** you should know arrays, loops, and asymptotic notation.

## Core theory

### Vocabulary

- A sort is **in place** if it uses only $O(1)$ extra memory beyond the input.
- A sort is **stable** if elements with equal keys keep their original relative order. Stability matters when sorting records by one field after another, such as sorting by city and then stably by surname.
- A sort is **adaptive** if it runs faster on inputs that are already nearly sorted.
- An **inversion** is a pair of positions $i < j$ with $a[i] > a[j]$. A sorted array has no inversions; a reversed one has the maximum, $n(n-1)/2$. The number of inversions measures how unsorted an array is.

### Selection sort

For each position $i$ from left to right, find the smallest element in the unsorted part `a[i:]` and swap it into position $i$.

- Always makes exactly $n(n-1)/2$ comparisons, so it is $\Theta(n^2)$ even on sorted input.
- Makes at most $n - 1$ swaps, the fewest of any common sort, which helps when writes are expensive.
- Not stable: a long-distance swap can jump an element over an equal one.

### Insertion sort

Grow a sorted prefix. For each new element, shift the larger elements of the prefix one place right and drop the new element into the gap, like sorting a hand of playing cards.

- Each shift removes exactly one inversion, so the number of shifts equals the number of inversions. The running time is $\Theta(n + I)$, where $I$ is the number of inversions.
- Best case $\Theta(n)$ (already sorted), worst case $\Theta(n^2)$ (reversed), average $\Theta(n^2)$.
- Stable, in place, and adaptive. Because of this, Python's Timsort uses insertion sort to build short runs, and introsort implementations finish small partitions with it.

### Bubble sort

Sweep through the array, swapping each adjacent pair that is out of order; after the $k$-th sweep, the $k$ largest elements are in their final places. Stop early if a sweep makes no swaps.

- Stable and in place; with the early exit, $\Theta(n)$ on sorted input.
- Each swap removes one inversion, like insertion sort, but bubble sort makes far more comparisons on typical inputs. It is mainly of teaching value.

### The comparison lower bound

A **comparison sort** learns about its input only by comparing pairs of elements. Any such algorithm can be drawn as a **decision tree**: each internal node is a comparison "$a_i \le a_j$?", each branch is an outcome, and each leaf is a final ordering. To sort every input correctly, the tree must have a leaf for each of the $n!$ possible orderings of distinct keys. A binary tree of height $h$ has at most $2^h$ leaves, so

$$2^h \ge n! \quad \Longrightarrow \quad h \ge \log_2 n! = \Theta(n \log n).$$

The last step follows from $n! \ge (n/2)^{n/2}$, so $\log_2 n! \ge \tfrac{n}{2}\log_2 \tfrac{n}{2}$. The height is the worst-case number of comparisons, so **every comparison sort needs $\Omega(n \log n)$ comparisons in the worst case**. Merge sort and heapsort achieve this bound, so they are asymptotically optimal among comparison sorts.

### Counting sort

If the keys are integers in a small range $0$ to $k - 1$, we can sort without comparisons:

1. Count how many times each key occurs.
2. Turn the counts into prefix sums, so `count[v]` becomes the number of keys less than or equal to `v`, which tells each key where its group ends.
3. Scan the input **from right to left**, placing each element at the last free slot of its key's group. Scanning backwards keeps equal keys in their original order, making the sort stable.

Time and space are $\Theta(n + k)$, which is linear when $k = O(n)$. The lower bound does not apply because counting sort never compares two elements.

### Radix sort

Least-significant-digit (LSD) **radix sort** sorts $d$-digit numbers by applying a stable sort, usually counting sort, to one digit at a time, starting with the least significant digit. After the pass on digit $j$, the numbers are sorted by their last $j + 1$ digits; stability is what preserves the earlier passes' work when two numbers share the current digit. With base $b$, the time is $\Theta(d(n + b))$. For example, 32-bit integers can be sorted in 4 passes of base 256.

| Algorithm | Best | Worst | Extra space | Stable |
| :--- | :--- | :--- | :--- | :--- |
| Selection sort | $\Theta(n^2)$ | $\Theta(n^2)$ | $O(1)$ | no |
| Insertion sort | $\Theta(n)$ | $\Theta(n^2)$ | $O(1)$ | yes |
| Bubble sort (early exit) | $\Theta(n)$ | $\Theta(n^2)$ | $O(1)$ | yes |
| Counting sort | $\Theta(n + k)$ | $\Theta(n + k)$ | $\Theta(n + k)$ | yes |
| LSD radix sort | $\Theta(d(n + b))$ | $\Theta(d(n + b))$ | $\Theta(n + b)$ | yes |

## Worked examples

### Example 1: Tracing insertion sort

```python
def insertion_sort(a):
    a, shifts = a[:], 0
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:     # shift larger elements one place right
            a[j + 1] = a[j]
            j -= 1
            shifts += 1
        a[j + 1] = key
        print(f"i={i}: {a}")
    return a, shifts

result, shifts = insertion_sort([5, 2, 4, 6, 1, 3])
print("shifts:", shifts)
```

Output:

```text
i=1: [2, 5, 4, 6, 1, 3]
i=2: [2, 4, 5, 6, 1, 3]
i=3: [2, 4, 5, 6, 1, 3]
i=4: [1, 2, 4, 5, 6, 3]
i=5: [1, 2, 3, 4, 5, 6]
shifts: 9
```

After step $i$, the prefix `a[0..i]` is sorted. Inserting 6 at $i = 3$ shifts nothing, because 6 is larger than the whole prefix; inserting 1 at $i = 4$ shifts four elements. The total of 9 shifts equals the number of inversions in the input: (5,2), (5,4), (5,1), (5,3), (2,1), (4,1), (4,3), (6,1), and (6,3).

### Example 2: How the elementary sorts respond to their input

Each cell shows comparisons/swaps (or shifts, for insertion sort) when sorting 100 numbers.

```python
def selection_sort(a):
    a, comparisons, swaps = a[:], 0, 0
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            comparisons += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            swaps += 1
    return comparisons, swaps

def insertion_sort(a):
    a, comparisons, moves = a[:], 0, 0
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0:
            comparisons += 1
            if a[j] <= key:
                break
            a[j + 1] = a[j]
            j -= 1
            moves += 1
        a[j + 1] = key
    return comparisons, moves

def bubble_sort(a):
    a, comparisons, swaps = a[:], 0, 0
    for end in range(len(a) - 1, 0, -1):
        swapped = False
        for j in range(end):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break                           # a sweep without swaps: already sorted
    return comparisons, swaps

def scrambled(n, seed=12345):               # a Fisher-Yates shuffle driven by a fixed generator
    keys, state = list(range(1, n + 1)), seed
    for i in range(n - 1, 0, -1):
        state = (1103515245 * state + 12345) % 2**31
        j = state % (i + 1)
        keys[i], keys[j] = keys[j], keys[i]
    return keys

n = 100
inputs = {"sorted": list(range(n)), "reversed": list(range(n, 0, -1)), "scrambled": scrambled(n)}
print(f"{'input':10} {'selection':>13} {'insertion':>13} {'bubble':>13}")
for name, data in inputs.items():
    cells = [f"{c}/{s}" for c, s in (selection_sort(data), insertion_sort(data), bubble_sort(data))]
    print(f"{name:10} {cells[0]:>13} {cells[1]:>13} {cells[2]:>13}")
```

Output:

```text
input          selection     insertion        bubble
sorted            4950/0          99/0          99/0
reversed         4950/50     4950/4950     4950/4950
scrambled        4950/98     2446/2350     4935/2350
```

Selection sort makes $100 \cdot 99 / 2 = 4950$ comparisons whatever the input, but never more than 99 swaps. Insertion sort and bubble sort both finish a sorted array in a single pass of 99 comparisons. On the reversed array, every pair is an inversion, so both perform all 4950 swaps. On the scrambled array, insertion and bubble sort make exactly the same number of moves, 2350, because each move removes one inversion and the array has 2350 inversions; but insertion sort needs about half as many comparisons, which is why it is the elementary sort used in practice.

### Example 3: Stable counting sort

```python
def counting_sort(records, key, k):
    count = [0] * k
    for r in records:
        count[key(r)] += 1
    for v in range(1, k):                   # prefix sums: count[v] = number of keys <= v
        count[v] += count[v - 1]
    out = [None] * len(records)
    for r in reversed(records):             # right to left keeps equal keys in order
        count[key(r)] -= 1
        out[count[key(r)]] = r
    return out

students = [("Asha", 3), ("Ben", 1), ("Chen", 3), ("Dara", 0), ("Eli", 1), ("Fay", 2)]
print(counting_sort(students, key=lambda s: s[1], k=4))
```

Output:

```text
[('Dara', 0), ('Ben', 1), ('Eli', 1), ('Fay', 2), ('Asha', 3), ('Chen', 3)]
```

The counts are `[1, 2, 1, 2]`, and the prefix sums `[1, 3, 4, 6]` say that grade 0 occupies position 0, grade 1 positions 1 and 2, grade 2 position 3, and grade 3 positions 4 and 5. Scanning from the right places Fay, then Eli in position 2, then Dara, then Chen in position 5, Ben in position 1, and Asha in position 4. Ben still precedes Eli and Asha still precedes Chen: the sort is stable. No two records were ever compared.

### Example 4: LSD radix sort

```python
def radix_sort(nums, base=10):
    digits = len(str(max(nums)))
    for d in range(digits):
        buckets = [[] for _ in range(base)]
        for x in nums:                      # stable: equal digits keep the previous order
            buckets[(x // base**d) % base].append(x)
        nums = [x for bucket in buckets for x in bucket]
        print(f"after digit {d}: {nums}")
    return nums

radix_sort([170, 45, 75, 90, 802, 24, 2, 66])
```

Output:

```text
after digit 0: [170, 90, 802, 2, 24, 45, 75, 66]
after digit 1: [802, 2, 24, 45, 66, 170, 75, 90]
after digit 2: [2, 24, 45, 66, 75, 90, 170, 802]
```

After the first pass, the numbers are ordered by their last digit. In the second pass, 802 and 2 both have tens digit 0, and they stay in the order the first pass gave them. After the third pass, the list is sorted by all three digits. Appending to buckets in input order is a stable distribution, equivalent to counting sort on each digit.

## Applications

- **Small and nearly sorted inputs:** insertion sort finishes runs inside Timsort (Python, and Java's sort for objects) and small partitions inside introsort (common C++ `std::sort` implementations).
- **Minimising writes:** selection sort's $n - 1$ swaps suit memory where writes are slow or wear the hardware.
- **Integer keys in a bounded range:** counting sort for ages, grades, or byte values; it is also the inner step of radix sort.
- **Fixed-width keys:** radix sort for integers, dates, IP addresses, and fixed-length strings; suffix-array construction algorithms rely on it.
- **Theory:** the decision-tree argument is a standard technique for proving lower bounds on problems such as element uniqueness.

## Common mistakes

- **Calling selection sort adaptive.** It makes $n(n-1)/2$ comparisons even on sorted input.
- **Writing `a[j] >= key` in insertion sort,** which moves equal elements past each other and breaks stability.
- **Scanning left to right in the placement phase of counting sort** while filling groups from their end, which reverses the order of equal keys.
- **Using counting sort when the key range is huge,** such as 32-bit integers, which needs a count array with four billion entries; use radix sort instead.
- **Running radix sort with an unstable per-digit sort,** which destroys the ordering established by earlier passes.
- **Applying the $\Omega(n \log n)$ bound to every sort.** It covers comparison sorts only; counting and radix sort are faster because they use the keys' values directly.

## Revision notes

- Stable: equal keys keep their order. In place: $O(1)$ extra space. Adaptive: faster on nearly sorted input.
- Selection: $\Theta(n^2)$ comparisons always, at most $n - 1$ swaps, not stable.
- Insertion: $\Theta(n + I)$ for $I$ inversions; best $\Theta(n)$, worst $\Theta(n^2)$; stable; the elementary sort used in practice.
- Bubble: stable, $\Theta(n)$ best case with early exit, $\Theta(n^2)$ otherwise; mainly educational.
- Comparison sorts need $\log_2 n! = \Omega(n \log n)$ comparisons in the worst case (decision-tree argument).
- Counting sort: $\Theta(n + k)$, stable via prefix sums and a right-to-left scan. Radix sort: $\Theta(d(n + b))$ with a stable sort per digit.

## Practice questions

:::question basic
Which elementary sort performs the fewest swaps in the worst case, and how many?
:::answer
Selection sort, with at most $n - 1$ swaps: one per position, and none when the minimum is already in place. Insertion sort and bubble sort perform one move per inversion, which can be $n(n-1)/2$ for a reversed array.
:::

:::question basic
How many inversions does `[3, 1, 2]` have, and how many shifts will insertion sort perform on it?
:::answer
Two inversions: (3, 1) and (3, 2). Insertion sort performs exactly one shift per inversion, so 2 shifts: inserting 1 shifts 3, and inserting 2 shifts 3 again.
:::

:::question intermediate
Show that selection sort is not stable by sorting `[(2, 'a'), (2, 'b'), (1, 'c')]` by the numbers only.
:::answer
At position 0, the minimum is `(1, 'c')` at index 2, so it is swapped with `(2, 'a')`, giving `[(1, 'c'), (2, 'b'), (2, 'a')]`. At position 1, the minimum of the remaining two (comparing numbers only, with strict `<`) is `(2, 'b')`, already in place. The result has `'b'` before `'a'`, although `'a'` came first in the input, so the order of equal keys was not preserved.
:::

:::question intermediate
Use the decision-tree bound to find the minimum number of comparisons that any comparison sort needs in the worst case to sort 4 distinct elements.
:::answer
There are $4! = 24$ possible orderings, so the decision tree needs at least 24 leaves. A tree of height $h$ has at most $2^h$ leaves, and $2^4 = 16 < 24 \le 32 = 2^5$, so $h \ge 5$. Every comparison sort needs at least 5 comparisons in the worst case for 4 elements, and 5 is in fact achievable.
:::

:::question intermediate
You must sort one million 32-bit unsigned integers. Why is plain counting sort a poor choice, and what would you use instead?
:::answer
Counting sort needs a count array covering the whole key range, $2^{32} \approx 4.3$ billion entries, which is gigabytes of memory and $\Theta(n + k)$ time dominated by $k$. LSD radix sort with base 256 treats each integer as 4 digits of 8 bits and makes 4 stable counting-sort passes with 256 buckets each: $\Theta(4(n + 256))$, which is linear in $n$ with small memory overhead.
:::

:::question advanced
Prove that the number of shifts insertion sort performs equals the number of inversions in the input.
:::answer
When element $x = a[i]$ is inserted, it moves left past exactly the elements of the sorted prefix that are greater than it; each such move is one shift. Those elements are precisely the earlier elements that form an inversion with $x$. Shifting does not change the relative order of any other pair, so each shift removes exactly one inversion and creates none. The sorted output has no inversions, so the total number of shifts equals the number of inversions in the original array.
:::

:::question advanced
Why must LSD radix sort use a stable sort for each digit? Give a two-number example where an unstable digit sort produces the wrong answer.
:::answer
Each pass must preserve the order produced by the earlier passes among numbers that share the current digit; that is what stability guarantees. Take `[13, 12]`. After the ones-digit pass, the list is `[12, 13]`. In the tens-digit pass, both numbers have tens digit 1, so they tie. A stable sort keeps `[12, 13]`, which is correct, but an unstable sort may output `[13, 12]`, discarding the information from the ones digit and leaving the list unsorted.
:::

## Further learning

- **Next:** *Merge Sort & QuickSort* reaches the $O(n \log n)$ bound with divide and conquer.
- **Related:** *Min & Max Heap Implementation* gives heapsort, another optimal comparison sort.
- **Related:** *Binary Search & Invariants* is the main consumer of sorted arrays.
