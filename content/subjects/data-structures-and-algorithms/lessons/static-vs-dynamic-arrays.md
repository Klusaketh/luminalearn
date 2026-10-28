---
lesson: array-memory-layout-and-operations
title: Static and Dynamic Arrays
summary: How arrays are laid out in contiguous memory, why indexing is constant time, and what insertion, deletion, and resizing really cost.
minutes: 45
type: theory
objectives:
  - Compute the address of an array element from the base address, element size, and index, including for two-dimensional arrays
  - State and justify the time complexity of access, search, insertion, and deletion in an array
  - Explain how a dynamic array grows and why appending is amortized constant time
  - Choose between an array and other structures based on the operations a program performs
---

## Introduction

The array is the most fundamental data structure: a sequence of elements stored side by side in one block of memory. Almost every other structure is built on top of arrays, from hash tables and heaps to the dynamic lists of Python, Java, and C++. Understanding exactly how an array sits in memory explains both its great strength (instant access to any element by position) and its weaknesses (expensive insertion in the middle and a fixed capacity).

This lesson covers **static arrays**, whose size is fixed when they are created, and **dynamic arrays**, which grow automatically by allocating a larger block and copying.

**Before you start:** you should know Big-O notation and have met amortized analysis.

## Core theory

### Contiguous storage and address arithmetic

A static array of $n$ elements occupies one contiguous block of memory. If every element has the same size $s$ bytes and the block starts at the **base address** $B$, then element $i$ (counting from 0) lives at

$$\text{address}(i) = B + i \cdot s.$$

Computing this address takes one multiplication and one addition, no matter how large $n$ or $i$ is. That is why **indexing an array is $\Theta(1)$**, and it is why most languages count indices from 0: the index is the offset from the start.

The same idea extends to two dimensions. A matrix with $R$ rows and $C$ columns stored in **row-major order** (rows one after another, as in C and in NumPy by default) places element $(r, c)$ at

$$B + (r \cdot C + c) \cdot s.$$

In **column-major order** (Fortran, MATLAB, R) the columns are laid out one after another instead, and the formula becomes $B + (c \cdot R + r) \cdot s$.

### Cache friendliness

Processors fetch memory in blocks called **cache lines**, typically 64 bytes. Reading `a[0]` brings its neighbours into the cache as well, so scanning an array from left to right is extremely fast in practice. The same scan over a linked list jumps around memory and is often several times slower, even though both are $\Theta(n)$. Traversing a row-major matrix row by row is similarly much faster than traversing it column by column.

### Operation costs

| Operation | Static array | Why |
| :--- | :--- | :--- |
| Read or write `a[i]` | $\Theta(1)$ | address arithmetic |
| Search for a value (unsorted) | $\Theta(n)$ worst case | must inspect each element |
| Search (sorted, binary search) | $\Theta(\log n)$ | halves the range each step |
| Insert at position $i$ | $\Theta(n - i)$ | shift later elements right by one |
| Delete at position $i$ | $\Theta(n - i)$ | shift later elements left by one |
| Insert or delete at the end | $\Theta(1)$ if there is space | no shifting |

Inserting at the front is the worst case: all $n$ elements must move. Deleting from the middle without preserving order can be done in $\Theta(1)$ by moving the last element into the gap, a trick worth remembering when order does not matter.

### Static arrays

A **static array** has a capacity fixed at creation. In C, `int scores[100];` reserves room for exactly 100 integers. Static arrays are simple and have no resizing overhead, but you must know the maximum size in advance; writing past the end is a serious bug (in C it is undefined behaviour and a classic security hole).

### Dynamic arrays

A **dynamic array** keeps two numbers: its **size** (elements in use) and its **capacity** (slots allocated). Appending writes into the next free slot. When size reaches capacity, it:

1. allocates a new block with larger capacity, usually a constant factor such as 1.5 or 2 times the old one,
2. copies every existing element into the new block,
3. frees the old block and appends the new element.

A single resizing append costs $\Theta(n)$, but because capacity grows geometrically, the total copying over $n$ appends is $O(n)$. Appending is therefore **amortized $\Theta(1)$**. Python's `list`, Java's `ArrayList`, and C++'s `std::vector` are all dynamic arrays.

The price is wasted memory: right after a resize, up to half the capacity (with doubling) is empty. Some implementations also shrink the block when the size drops below a quarter of the capacity, so memory is returned without risking repeated grow-shrink cycles.

### What a Python list actually stores

A Python list is a dynamic array of **references**: each slot holds a pointer to an object stored elsewhere. Indexing is still $\Theta(1)$, but the objects themselves are scattered in memory, so a list of numbers is less cache friendly than a C array of the same numbers. The `array` module and NumPy arrays store the raw values contiguously instead.

## Worked examples

### Example 1: Address calculation

An array of 4-byte integers starts at address 1000. Where is `a[25]`?

$$1000 + 25 \times 4 = 1100.$$

A 2D array `m` of 8-byte doubles has 6 rows and 10 columns, stored row-major from address 2000. Where is `m[3][7]`?

$$2000 + (3 \times 10 + 7) \times 8 = 2000 + 37 \times 8 = 2296.$$

If the same matrix were column-major, `m[3][7]` would be at $2000 + (7 \times 6 + 3) \times 8 = 2000 + 45 \times 8 = 2360$.

### Example 2: Watching a Python list grow

`sys.getsizeof` reports the bytes a list object occupies, which changes only when its capacity changes.

```python
import sys

values = []
last = sys.getsizeof(values)
growth_points = []
for i in range(64):
    values.append(i)
    size = sys.getsizeof(values)
    if size != last:
        growth_points.append(len(values))
        last = size
print(growth_points)
```

On CPython 3.13 this prints `[1, 5, 9, 17, 25, 33, 41, 53]`: the capacity changes only when the list reaches sizes 1, 5, 9, 17, and so on, not on every append. Each jump allocates spare room for several future appends. The exact growth pattern is an implementation detail of CPython (it grows by roughly an eighth plus a small constant) and can differ between versions, but the principle, geometric growth with occasional copies, is what makes appends amortized constant time.

### Example 3: The cost of inserting at the front

```python
def shifts_for_inserts(n, at_front):
    arr, moved = [], 0
    for x in range(n):
        if at_front:
            moved += len(arr)       # every existing element shifts right
            arr.insert(0, x)
        else:
            arr.append(x)           # nothing shifts
    return moved

for n in (10, 100, 1000):
    print(n, shifts_for_inserts(n, True), shifts_for_inserts(n, False))
```

Output:

```text
10 45 0
100 4950 0
1000 499500 0
```

Inserting $n$ elements at the front shifts $0 + 1 + \dots + (n-1) = n(n-1)/2$ elements, which is $\Theta(n^2)$ in total. Appending shifts nothing. If a program needs fast insertion at both ends, a double-ended queue (`collections.deque`) is the right structure.

### Example 4: Deleting without preserving order

```python
def remove_unordered(arr, i):
    arr[i] = arr[-1]   # overwrite the target with the last element
    arr.pop()          # drop the duplicate at the end: O(1)

tasks = ["build", "test", "lint", "deploy", "docs"]
remove_unordered(tasks, 1)
print(tasks)
```

Output:

```text
['build', 'docs', 'lint', 'deploy']
```

Removing `"test"` with `tasks.pop(1)` would shift three elements. Swapping with the last element and popping is $\Theta(1)$, at the cost of changing the order, which is fine for a set of pending tasks but not for a sorted list.

## Applications

- **Lookup tables and buffers.** Image pixels, audio samples, and network packets are stored in arrays because they are accessed by position and processed sequentially.
- **Matrix and scientific computing.** NumPy, BLAS, and GPU libraries store matrices as contiguous arrays and choose loop orders that match the memory layout.
- **Implementing other structures.** Stacks, queues (as ring buffers), heaps, hash tables, and adjacency lists are all built on arrays.
- **Databases and columnar storage** store each column as a contiguous array so that scans and aggregates run at memory bandwidth.
- **Everyday programming.** Choosing `append` over `insert(0, x)` or pre-sizing an `ArrayList` are direct uses of this lesson.

## Common mistakes

- **Off-by-one indexing.** Valid indices are $0$ to $n-1$; `a[n]` is out of bounds.
- **Assuming insertion anywhere is cheap.** Only insertion at the end is $\Theta(1)$ (amortized); elsewhere it shifts elements.
- **Confusing size with capacity.** A dynamic array may have room for 16 elements while holding 9; only the size is visible to the program.
- **Using the wrong layout formula.** Row-major and column-major give different addresses for the same $(r, c)$.
- **Treating a Python list of numbers as a compact numeric array.** It stores references to separate objects; use `array` or NumPy when memory and speed matter.

## Revision notes

- Element $i$ is at $B + i \cdot s$; indexing is $\Theta(1)$.
- Row-major: $B + (rC + c)s$. Column-major: $B + (cR + r)s$.
- Search $\Theta(n)$ unsorted, $\Theta(\log n)$ sorted. Insert/delete at position $i$ shifts $n - i$ elements.
- Dynamic arrays grow by a constant factor; append is amortized $\Theta(1)$, a resize is $\Theta(n)$.
- Unordered delete trick: overwrite with the last element and pop, $\Theta(1)$.
- Sequential array scans are cache friendly, which makes arrays fast in practice.

## Practice questions

:::question basic
An array of 2-byte integers starts at address 500. What is the address of the element at index 40?
:::answer
$500 + 40 \times 2 = 580$. The element at index $i$ is $i \times s$ bytes after the base address, where $s$ is the element size.
:::

:::question basic
Why is reading `a[i]` from an array $\Theta(1)$ while reading the $i$-th node of a linked list is $\Theta(i)$?
:::answer
Array elements are contiguous and equally sized, so the address of element $i$ is computed directly as base $+ i \times$ size, a constant number of operations. A linked list stores nodes at arbitrary addresses, and the only way to find the $i$-th node is to follow $i$ links from the head.
:::

:::question intermediate
A row-major 2D array of 4-byte integers has 12 rows and 20 columns and starts at address 4000. Find the address of the element in row 5, column 13. Then find it for column-major storage.
:::answer
Row-major: $4000 + (5 \times 20 + 13) \times 4 = 4000 + 113 \times 4 = 4452$. Column-major: $4000 + (13 \times 12 + 5) \times 4 = 4000 + 161 \times 4 = 4644$.
:::

:::question intermediate
A program builds a list of $n$ items by inserting each new item at index 0 of a Python list. What is the total time complexity, and how would you rewrite it to be linear?
:::answer
Each `insert(0, x)` shifts every existing element, so the $k$-th insertion costs $\Theta(k)$ and the total is $0 + 1 + \dots + (n-1) = \Theta(n^2)$. Rewrite it by appending each item (amortized $\Theta(1)$) and reversing once at the end (`items.reverse()`, $\Theta(n)$), or use `collections.deque` with `appendleft`, which is $\Theta(1)$ per operation.
:::

:::question intermediate
A dynamic array doubles when full and halves when its size drops to one quarter of its capacity. Why not halve as soon as the size drops to one half?
:::answer
Halving at one half invites thrashing. If the array is exactly full and you alternate append and delete, each append doubles the capacity (copying $n$ elements) and the next delete brings the size back to half, triggering a halving copy, so every operation costs $\Theta(n)$. Waiting until a quarter full leaves a buffer: after any resize the array is half full, so many operations must happen before the next resize, which keeps both append and delete amortized $\Theta(1)$.
:::

:::question advanced
You need a collection that supports appending, reading by index, and removing an arbitrary element, all in $O(1)$ time, and order does not matter. Describe how to achieve this, including how to find the element to remove.
:::answer
Store the elements in a dynamic array and keep a hash map from each element (assume elements are distinct) to its current index. Append: add to the end of the array and record its index, amortized $O(1)$. Read by index: direct array access, $O(1)$. Remove element $x$: look up its index $i$ in the map, move the last element into position $i$, update the moved element's index in the map, pop the last slot, and delete $x$ from the map. Every step is $O(1)$ (expected, for the hash map). This is the classic "insert, delete, get random in $O(1)$" design.
:::

## Further learning

- **Next:** *Sliding Window & Two-Pointers* shows how to solve subarray problems in a single linear pass over an array.
- **Related:** *Circular Queues & Deque* reuses a fixed array as a ring buffer so that both ends support $O(1)$ operations.
- **Related:** *Min & Max Heap Implementation* stores a complete binary tree inside an array using index arithmetic.
