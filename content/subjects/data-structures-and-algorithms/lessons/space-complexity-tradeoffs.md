---
lesson: space-complexity-tradeoffs
title: Space Complexity and Memory Trade-offs
summary: Measure how much memory an algorithm needs as its input grows, and learn when spending memory buys time.
minutes: 35
type: theory
objectives:
  - Distinguish input space, auxiliary space, and total space, and state which one an analysis reports
  - Determine the auxiliary space of iterative and recursive functions, including call-stack usage
  - Explain classic time-space trade-offs such as caching, lookup tables, and in-place versus out-of-place algorithms
  - Choose between memory-hungry and memory-frugal solutions for a stated constraint
---

## Introduction

Time is not the only resource an algorithm consumes. Every variable, array, hash table, and pending function call occupies memory, and memory is finite. A program that is fast but needs more memory than the machine has will crash, swap to disk (and slow down by orders of magnitude), or simply be impossible to run on a phone or a small embedded device.

**Space complexity** applies the same asymptotic language you used for time to memory: it describes how the amount of memory an algorithm needs grows with the input size $n$. This lesson shows how to measure it, how recursion hides a memory cost in the call stack, and how to reason about the frequent choice between spending memory to save time and spending time to save memory.

**Before you start:** you should know Big-O, Big-Omega, and Big-Theta notation from the previous lesson.

## Core theory

### What counts as space

The memory an algorithm uses splits into two parts:

- **Input space**: the memory that holds the input itself, such as the list you were given.
- **Auxiliary space**: any extra memory the algorithm allocates while it runs: temporary variables, new arrays, hash tables, and the call stack used by recursion.

**Total space** is input space plus auxiliary space. Because every algorithm that reads an input of size $n$ needs at least $\Theta(n)$ total space, comparing algorithms by total space hides the differences between them. So when people say an algorithm "uses $O(1)$ space", they almost always mean $O(1)$ **auxiliary** space. State which one you mean when it matters.

### Measuring auxiliary space

Count the memory allocated as a function of $n$, then simplify exactly as you would for time:

- A fixed number of scalar variables (counters, indices, a running sum) is $O(1)$.
- A new list, set, or dictionary that can hold up to $n$ items is $O(n)$.
- An $n \times n$ table is $O(n^2)$.
- Memory that is allocated and freed inside a loop is counted once at its peak, not once per iteration, because it is reused.

Space complexity reports the **peak** memory in use at any moment, not the total amount ever allocated.

### The hidden cost of recursion

Each call to a function creates a **stack frame** that stores its parameters, local variables, and the place to return to. The frame stays on the call stack until the call returns. So a recursive function uses auxiliary space proportional to its **maximum recursion depth**, even if each frame holds only a few variables.

```python
def sum_recursive(values: list[int], i: int = 0) -> int:
    if i == len(values):
        return 0
    return values[i] + sum_recursive(values, i + 1)
```

This function makes a chain of $n + 1$ calls before any of them returns, so $n + 1$ frames are on the stack at the deepest point: $\Theta(n)$ auxiliary space. An iterative loop that computes the same sum with one accumulator uses $\Theta(1)$. Python also limits recursion depth (by default to about 1000 frames), so deep recursion can fail outright with a `RecursionError`.

Recursion that halves the problem, such as recursive binary search, has depth $\log_2 n$ and therefore uses $\Theta(\log n)$ stack space.

### In-place and out-of-place algorithms

An algorithm is **in-place** if it transforms its input using only $O(1)$ (or, by a looser convention, $O(\log n)$) auxiliary space, overwriting the input as it goes. Reversing a list by swapping from both ends is in-place. Building a reversed copy is out-of-place and uses $\Theta(n)$ auxiliary space.

| Algorithm | Auxiliary space | In-place? |
| :--- | :--- | :--- |
| Reverse by swapping ends | $\Theta(1)$ | Yes |
| Insertion sort | $\Theta(1)$ | Yes |
| Heap sort | $\Theta(1)$ | Yes |
| Quicksort (typical implementation) | $\Theta(\log n)$ expected for the stack | Yes, by the looser convention |
| Merge sort on arrays | $\Theta(n)$ for the merge buffer | No |
| Building a hash set of the input | $\Theta(n)$ | No |

In-place algorithms are valuable when memory is tight, but they destroy the original order of the input, which the caller may still need.

### Time-space trade-offs

Many problems let you trade one resource for the other:

- **Caching (memoisation)** stores results you have already computed so you never recompute them. Memory goes up, time goes down. The naive recursive Fibonacci function takes exponential time; caching each result makes it linear time with linear space.
- **Lookup tables** precompute answers. Counting the set bits of every byte value in a 256-entry table lets you count bits in a large file with one table lookup per byte.
- **Indexes** in databases are extra data structures (often B+ trees) that make searches logarithmic instead of linear, at the cost of storage and slower writes.
- **Hashing for membership.** Checking whether any pair in a list sums to a target takes $O(n^2)$ time with $O(1)$ space using nested loops, or $O(n)$ expected time with $O(n)$ space using a set.

Going the other way, you can **recompute instead of storing** when memory is scarce. Streaming algorithms process data in one pass with tiny memory, accepting approximate answers or extra passes.

### Bits, not just counts

Asymptotic space hides constant factors, but real memory is measured in bytes. A Python `int` object takes 28 bytes on a typical 64-bit build, while a C `int` takes 4. A Python list of a million small integers therefore uses tens of megabytes, while the same values in an `array.array("i")` take about 4 megabytes. Asymptotics tell you how memory grows; the representation decides the constant.

## Worked examples

### Example 1: Auxiliary space of three functions

```python
def maximum(values):          # (a)
    best = values[0]
    for v in values:
        if v > best:
            best = v
    return best

def squares(values):          # (b)
    return [v * v for v in values]

def pair_table(values):       # (c)
    return [[a * b for b in values] for a in values]
```

- (a) stores one variable `best` regardless of $n$: $\Theta(1)$ auxiliary space.
- (b) builds a new list of $n$ squares: $\Theta(n)$ auxiliary space.
- (c) builds $n$ lists of $n$ products: $\Theta(n^2)$ auxiliary space. For $n = 10{,}000$ that is $10^8$ entries, far more memory than most programs should use, even though the time ($\Theta(n^2)$) might be acceptable.

### Example 2: Two-sum with and without extra memory

Given a list and a target, decide whether two different elements sum to the target.

```python
def two_sum_quadratic(values, target):
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            if values[i] + values[j] == target:
                return True
    return False

def two_sum_linear(values, target):
    seen = set()
    for v in values:
        if target - v in seen:
            return True
        seen.add(v)
    return False

data = [8, 3, 11, 5, 2]
print(two_sum_quadratic(data, 13), two_sum_linear(data, 13))
print(two_sum_quadratic(data, 30), two_sum_linear(data, 30))
```

Output:

```text
True True
False False
```

| Version | Time | Auxiliary space |
| :--- | :--- | :--- |
| Nested loops | $\Theta(n^2)$ | $\Theta(1)$ |
| Hash set | $\Theta(n)$ expected | $\Theta(n)$ |

Both are correct. The set version spends linear memory to remove a factor of $n$ from the running time. For a million elements the quadratic version needs about $5 \times 10^{11}$ comparisons in the worst case; the linear one needs about a million set operations. If memory were severely limited, a third option is to sort the list in place ($O(n \log n)$ time) and scan with two pointers ($O(1)$ extra space).

### Example 3: Recursion depth as memory

```python
import sys

def depth_of_halving(n):
    if n <= 1:
        return 1
    return 1 + depth_of_halving(n // 2)

def depth_of_counting(n):
    if n == 0:
        return 1
    return 1 + depth_of_counting(n - 1)

print(depth_of_halving(1_000_000))
print(depth_of_counting(500))
print(sys.getrecursionlimit() >= 500)
```

Output:

```text
20
501
True
```

Halving reaches the base case after about $\log_2 n$ calls, so only 20 frames are ever live for a million. Counting down by one keeps $n + 1$ frames live, which is why `depth_of_counting(1_000_000)` would raise `RecursionError` in standard Python. The two functions do similar work per call, but their space complexities are $\Theta(\log n)$ and $\Theta(n)$.

### Example 4: Memoisation trades memory for time

```python
from functools import lru_cache

calls = 0

def fib_naive(n):
    global calls
    calls += 1
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)

@lru_cache(maxsize=None)
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)

print(fib_naive(20), calls)
print(fib_cached(20), fib_cached.cache_info().currsize)
```

Output:

```text
6765 21891
6765 21
```

The naive version makes 21,891 calls to compute $F_{20}$, and the count grows exponentially with $n$. The cached version computes each value from $F_0$ to $F_{20}$ once and stores 21 results. Time drops from exponential to linear in exchange for $\Theta(n)$ memory for the cache (plus $\Theta(n)$ stack depth).

## Applications

- **Mobile and embedded software**, where memory is measured in kilobytes or a few megabytes, favours in-place algorithms and streaming designs.
- **Big data processing** often cannot hold the whole data set in memory, so algorithms are designed to stream through data in passes (external sorting, counting sketches).
- **Web caches and content delivery networks** spend large amounts of memory and storage to answer repeated requests without recomputation or long network trips.
- **Database indexes** deliberately duplicate data in tree structures to make reads fast; administrators weigh that storage against query speed and write cost.
- **Compilers and runtimes** decide whether to cache computed values or recompute them depending on register and memory pressure.

## Common mistakes

- **Counting the input as auxiliary space.** Reading a list of $n$ items does not make an algorithm $O(n)$ auxiliary space; allocating a copy does.
- **Forgetting the call stack.** A recursive function with no visible arrays still uses memory proportional to its recursion depth.
- **Summing memory across loop iterations.** If a temporary list of size $k$ is rebuilt in each of $n$ iterations, peak space is $O(k)$, not $O(nk)$, because the old list is released.
- **Assuming in-place means no memory at all.** In-place algorithms may still use $O(\log n)$ stack space, as quicksort does.
- **Ignoring constant factors when memory is tight.** Two $\Theta(n)$ structures can differ by a factor of seven or more in bytes per element.

## Revision notes

- Space complexity = growth of memory with $n$. Usually report **auxiliary** space.
- Scalars: $O(1)$. A size-$n$ collection: $O(n)$. An $n \times n$ table: $O(n^2)$.
- Recursion costs stack space equal to the maximum depth: $\Theta(n)$ for linear recursion, $\Theta(\log n)$ for halving recursion.
- Report **peak** memory, not total allocations.
- In-place: $O(1)$ (sometimes $O(\log n)$) auxiliary space, overwriting the input.
- Trade-offs: caching, lookup tables, indexes, and hash sets buy time with memory; recomputation and streaming buy memory with time.

## Practice questions

:::question basic
What is the auxiliary space complexity of a function that counts how many times each distinct word appears in a list of $n$ words using a dictionary? Justify your answer.
:::answer
$O(d)$, where $d$ is the number of distinct words, which is at most $n$, so the worst case is $\Theta(n)$. The dictionary holds one entry per distinct word; scalar counters add only $O(1)$. If every word is different, the dictionary grows to $n$ entries.
:::

:::question basic
Explain why the following function uses $\Theta(n)$ auxiliary space even though it creates no lists.

```python
def countdown(n):
    if n > 0:
        countdown(n - 1)
```
:::answer
Each call waits for the next one to return, so at the deepest point there are $n + 1$ active calls, each with its own stack frame holding `n` and a return address. Memory used by the call stack therefore grows linearly with $n$. An equivalent `while` loop would use $\Theta(1)$ auxiliary space.
:::

:::question intermediate
A function receives a list of length $n$ and, inside a loop that runs $n$ times, builds a temporary list of 50 elements, uses it, and discards it. What is its auxiliary space complexity?
:::answer
$\Theta(1)$. The temporary list has a fixed size (50) that does not depend on $n$, and it is released before the next iteration builds a new one, so the peak extra memory is bounded by a constant. Total allocations grow with $n$, but space complexity measures peak memory in use, not the sum of all allocations.
:::

:::question intermediate
You must find whether a list of $n$ integers contains a duplicate, and you may use only $O(1)$ auxiliary space. You are allowed to modify the list. Describe an approach and give its time complexity.
:::answer
Sort the list in place with an in-place sort such as heap sort ($O(n \log n)$ time, $O(1)$ auxiliary space), then scan once and compare each element with its neighbour; any duplicate values become adjacent after sorting. Total time is $O(n \log n)$ with $O(1)$ extra space. (Using a hash set would give $O(n)$ expected time but $O(n)$ space, which breaks the constraint. If you use quicksort instead, the recursion uses $O(\log n)$ expected stack space.)
:::

:::question intermediate
State the time and auxiliary space of computing the $n$-th Fibonacci number in each way: (a) naive recursion, (b) recursion with a cache, (c) a loop keeping only the last two values.
:::answer
(a) Exponential time, about $\Theta(\varphi^n)$ with $\varphi \approx 1.618$, and $\Theta(n)$ space for the recursion depth. (b) $\Theta(n)$ time and $\Theta(n)$ space for the cache plus the stack. (c) $\Theta(n)$ time and $\Theta(1)$ space, because only two numbers are kept at a time. Version (c) shows that the cache in (b) stores more than the computation needs.
:::

:::question advanced
Merge sort on an array uses $\Theta(n)$ auxiliary space. Explain where that space goes, and why the recursion depth alone ($\Theta(\log n)$) does not determine its space complexity.
:::answer
Each merge step combines two sorted halves into a temporary buffer before copying back, and the top-level merge needs a buffer the size of the whole array, $\Theta(n)$. With a careful implementation, one shared buffer of size $n$ is allocated once and reused, so total auxiliary space is $\Theta(n)$ for the buffer plus $\Theta(\log n)$ for the stack. The space complexity is the larger term, $\Theta(n)$. The depth bounds only the stack, not the data buffers.
:::

## Further learning

- **Next:** *Amortized Analysis* shows how a dynamic array can waste some memory on spare capacity in exchange for fast appends.
- **Related:** *Memoization vs Tabulation* develops the caching trade-off from Example 4 into a general technique.
- **Related:** *Merge Sort & QuickSort* compares an out-of-place and an in-place sort in detail.
