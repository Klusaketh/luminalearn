---
lesson: heap-implementation
title: Min and Max Heap Implementation
summary: Store a complete binary tree in an array, maintain the heap property with sift-up and sift-down, build a heap in linear time, and sort with heapsort.
minutes: 45
type: theory
objectives:
  - Store a complete binary tree in an array and move between parents and children with index arithmetic
  - Implement insert and extract with sift-up and sift-down, and explain why each is O(log n)
  - Build a heap from an unsorted array in O(n) time and justify the linear bound
  - Implement heapsort and analyse its time, space, and stability
---

## Introduction

The *Priority Queues* lesson used Python's `heapq` module as a black box. This lesson opens the box. A **binary heap** is a complete binary tree that satisfies the **heap property**: in a min-heap, every node's key is less than or equal to its children's keys, so the minimum is always at the root. Because the tree is complete, it needs no pointers at all; it fits exactly into an ordinary array, and moving between a node and its parent or children is simple arithmetic on indices.

Two short procedures, **sift-up** and **sift-down**, maintain the heap property after every change. With them we get $O(\log n)$ insertion and extraction, an $O(n)$ way to turn any array into a heap, and heapsort, an in-place $O(n \log n)$ sorting algorithm.

**Before you start:** you should know binary trees, the priority queue ADT, and logarithms.

## Core theory

### Two properties

- **Shape property:** the tree is **complete**: every level is full except possibly the last, which is filled from left to right. A complete tree with $n$ nodes has height $\lfloor \log_2 n \rfloor$.
- **Heap property (min-heap):** for every node other than the root, $\text{key}(\text{parent}) \le \text{key}(\text{node})$. A **max-heap** reverses the inequality, putting the maximum at the root.

The heap property orders each path from the root downwards, but it says nothing about siblings or cousins. A heap is therefore much weaker than a sorted array or a BST, which is exactly why it can be maintained so cheaply.

### Array layout

Number the nodes in level order, left to right, starting from 0 at the root. With 0-based indices:

$$\text{parent}(i) = \left\lfloor \frac{i - 1}{2} \right\rfloor, \qquad \text{left}(i) = 2i + 1, \qquad \text{right}(i) = 2i + 2.$$

With 1-based indices (common in textbooks), the formulas become $\lfloor i/2 \rfloor$, $2i$, and $2i + 1$. Because the tree is complete, the array has no gaps. The nodes with indices $\lfloor n/2 \rfloor$ to $n - 1$ are exactly the leaves.

### Sift-up and sift-down

- **Sift-up** (used after inserting at the end): while the node is smaller than its parent, swap them. The node moves up one level per swap.
- **Sift-down** (used after replacing the root): while the node is larger than its smaller child, swap it with that child. Choosing the **smaller** child matters: it is the only one that can become the parent of the other without breaking the heap property.

Each procedure moves along one root-to-leaf path, so it makes at most $\lfloor \log_2 n \rfloor$ swaps.

### Operations

| Operation | Method | Time |
| :--- | :--- | :--- |
| `peek` | return `a[0]` | $O(1)$ |
| `push(x)` | append `x`, sift it up | $O(\log n)$ |
| `pop()` | save `a[0]`, move the last element to index 0, shrink, sift down | $O(\log n)$ |
| `replace(x)` | overwrite `a[0]` with `x`, sift down | $O(\log n)$ |
| build from $n$ items | sift down every internal node, from the last to the root | $O(n)$ |

### Why building a heap is linear

Inserting $n$ items one at a time costs $O(n \log n)$. The bottom-up method is faster: sift down each internal node, starting with the last one, index $\lfloor n/2 \rfloor - 1$, and ending at the root. When a node is processed, both of its subtrees are already heaps, so one sift-down makes its subtree a heap too.

The key observation is that most nodes are near the bottom, where sift-downs are short. A complete tree has about $n/2^{k+1}$ nodes at height $k$, and sifting one of them down costs $O(k)$. The total is

$$\sum_{k=0}^{\lfloor \log_2 n \rfloor} \frac{n}{2^{k+1}} \cdot O(k) = O\left(n \sum_{k=0}^{\infty} \frac{k}{2^k}\right) = O(2n) = O(n),$$

because $\sum_{k \ge 0} k/2^k = 2$. Inserting one at a time is slow for the opposite reason: most nodes are near the bottom, and sift-*up* from the bottom can be long.

### Heapsort

1. Build a **max-heap** from the array in $O(n)$.
2. Repeat $n - 1$ times: swap the root (the maximum) with the last element of the heap, shrink the heap by one, and sift the new root down.

Each step places the current maximum in its final position at the end of the array. Heapsort runs in $O(n \log n)$ time in the **worst case**, sorts **in place** with $O(1)$ extra space, and is **not stable**: equal keys can change their relative order. In practice it is usually slower than a well-implemented quicksort because it jumps around the array and makes poor use of the cache, but its worst-case guarantee makes it a useful fallback: introsort, used by many C++ standard libraries, switches to heapsort when quicksort's recursion goes too deep.

## Worked examples

### Example 1: A min-heap from scratch

```python
class MinHeap:
    def __init__(self):
        self.a = []

    def push(self, x):
        a = self.a
        a.append(x)
        i = len(a) - 1
        while i > 0:                          # sift up
            parent = (i - 1) // 2
            if a[parent] <= a[i]:
                break
            a[parent], a[i] = a[i], a[parent]
            i = parent

    def pop(self):
        a = self.a
        if not a:
            raise IndexError("pop from empty heap")
        top = a[0]
        last = a.pop()
        if a:                                 # move the last element to the root and sift down
            a[0] = last
            self._sift_down(0)
        return top

    def _sift_down(self, i):
        a, n = self.a, len(self.a)
        while True:
            smallest, left, right = i, 2 * i + 1, 2 * i + 2
            if left < n and a[left] < a[smallest]:
                smallest = left
            if right < n and a[right] < a[smallest]:
                smallest = right
            if smallest == i:
                return
            a[i], a[smallest] = a[smallest], a[i]
            i = smallest

h = MinHeap()
for x in [5, 3, 8, 1, 9, 2]:
    h.push(x)
    print(f"push {x}: {h.a}")
print("pop:", h.pop(), h.a)
print("pop:", h.pop(), h.a)
```

Output:

```text
push 5: [5]
push 3: [3, 5]
push 8: [3, 5, 8]
push 1: [1, 3, 8, 5]
push 9: [1, 3, 8, 5, 9]
push 2: [1, 3, 2, 5, 9, 8]
pop: 1 [2, 3, 8, 5, 9]
pop: 2 [3, 5, 8, 9]
```

Pushing 1 appends it at index 3. Its parent, index 1, holds 5, so they swap; its new parent, index 0, holds 3, so they swap again and 1 reaches the root. The first pop removes 1, moves the last element (8) to the root, and sifts it down: the smaller child is 2 at index 2, so they swap, and 8 stops at index 2 because it has no children there. At no point is the array sorted; only the root is guaranteed to be the minimum.

### Example 2: Building a heap bottom-up versus one insert at a time

```python
def sift_up(a, i):
    swaps = 0
    while i > 0 and a[(i - 1) // 2] > a[i]:
        parent = (i - 1) // 2
        a[parent], a[i] = a[i], a[parent]
        i, swaps = parent, swaps + 1
    return swaps

def sift_down(a, i, n):
    swaps = 0
    while True:
        smallest, left, right = i, 2 * i + 1, 2 * i + 2
        if left < n and a[left] < a[smallest]:
            smallest = left
        if right < n and a[right] < a[smallest]:
            smallest = right
        if smallest == i:
            return swaps
        a[i], a[smallest] = a[smallest], a[i]
        i, swaps = smallest, swaps + 1

def is_min_heap(a):
    return all(a[(i - 1) // 2] <= a[i] for i in range(1, len(a)))

n = 1023
data = list(range(n, 0, -1))                 # descending: the worst case for both methods

by_insertion, swaps_up = [], 0
for x in data:
    by_insertion.append(x)
    swaps_up += sift_up(by_insertion, len(by_insertion) - 1)

bottom_up = data[:]
swaps_down = sum(sift_down(bottom_up, i, n) for i in range(n // 2 - 1, -1, -1))

print("one at a time:", swaps_up, "swaps,", is_min_heap(by_insertion))
print("bottom-up:    ", swaps_down, "swaps,", is_min_heap(bottom_up))
```

Output:

```text
one at a time: 8194 swaps, True
bottom-up:     1013 swaps, True
```

With descending input, every inserted value is the smallest so far and must climb all the way to the root, so the insertion method does $\sum_{d=0}^{9} d \cdot 2^d = 8194$ swaps for this perfect tree of height 9. The bottom-up method sifts each internal node down to the bottom, but most internal nodes are near the bottom: 256 nodes need one swap, 128 need two, and only the root needs nine, for a total of 1013, which is less than $n$. Both arrays are valid heaps, though not necessarily the same one.

### Example 3: Heapsort

```python
def sift_down(a, i, n):                      # max-heap on a[0:n]
    while True:
        largest, left, right = i, 2 * i + 1, 2 * i + 2
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest

def heapsort(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):      # phase 1: build a max-heap
        sift_down(a, i, n)
    for end in range(n - 1, 0, -1):          # phase 2: move the maximum to the end
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)                 # the heap is now a[0:end]
    return a

print(heapsort([4, 10, 3, 5, 1]))
print(heapsort([9, 7, 7, 2, 8, 1, 3]))
```

Output:

```text
[1, 3, 4, 5, 10]
[1, 2, 3, 7, 7, 8, 9]
```

For `[4, 10, 3, 5, 1]`, phase 1 sifts down index 1 (no change, because 10 is larger than its children 5 and 1) and then index 0, producing the max-heap `[10, 5, 3, 4, 1]`. Phase 2 swaps 10 to the last position and restores the heap on the first four elements, then swaps 5 into the second-to-last position, and so on. The sorted region grows from the right while the heap shrinks, so no second array is needed.

## Applications

- **Priority queues** in schedulers, simulators, and graph algorithms such as Dijkstra's and Prim's are almost always binary heaps; Python's `heapq` and Java's `PriorityQueue` both use one.
- **Guaranteed-time sorting:** heapsort's $O(n \log n)$ worst case and $O(1)$ extra space make it the fallback inside introsort.
- **Top-k and streaming statistics:** a size-$k$ heap keeps the $k$ largest items seen, and a pair of heaps maintains a running median.
- **Merging sorted sequences:** external sorting merges sorted runs from disk using a heap holding one item per run.
- **Timers and event loops:** many event-driven systems keep pending timers in a heap ordered by expiry time.

## Common mistakes

- **Off-by-one index formulas,** such as mixing the 1-based formula $2i$ with 0-based arrays.
- **Sifting down towards the wrong child.** Always swap with the smaller child in a min-heap (the larger in a max-heap); swapping with the other child breaks the heap property.
- **Starting bottom-up construction at index $n - 1$.** Leaves are already heaps; start at $\lfloor n/2 \rfloor - 1$, the last internal node, and go down to 0.
- **Forgetting to shrink the heap boundary in heapsort,** which sifts the already sorted maximum back into the heap.
- **Expecting a heap to be sorted** or iterating over it in order; only the root is special.
- **Claiming heapsort is stable.** It is not: the swaps move elements over long distances.

## Revision notes

- Heap = complete binary tree + heap property; stored in an array with no gaps.
- 0-based: parent $\lfloor (i-1)/2 \rfloor$, children $2i + 1$ and $2i + 2$; leaves are indices $\lfloor n/2 \rfloor$ to $n - 1$.
- Push: append and sift up. Pop: move the last element to the root and sift down (swap with the smaller child).
- Push, pop, and replace are $O(\log n)$; peek is $O(1)$.
- Bottom-up build sifts down from $\lfloor n/2 \rfloor - 1$ to 0 and costs $O(n)$, because $\sum k/2^k = 2$.
- Heapsort: build a max-heap, then repeatedly swap the root to the end and sift down. $O(n \log n)$ worst case, in place, not stable.

## Practice questions

:::question basic
In a 0-based array heap, what are the parent and children of the node at index 6?
:::answer
The parent is $\lfloor (6 - 1)/2 \rfloor = 2$, and the children are $2 \cdot 6 + 1 = 13$ and $2 \cdot 6 + 2 = 14$, provided those indices are less than the heap's size.
:::

:::question basic
Is the array `[1, 4, 2, 7, 5, 3]` a min-heap? Check every parent.
:::answer
Yes. Index 0 (1) is at most its children 4 and 2. Index 1 (4) is at most its children 7 and 5. Index 2 (2) is at most its only child, 3, at index 5. Indices 3, 4, and 5 are leaves. Every parent is at most its children, so the heap property holds.
:::

:::question intermediate
Insert 0 into the min-heap `[1, 3, 2, 5, 9, 8]`. Show each swap and the final array.
:::answer
Append 0 at index 6: `[1, 3, 2, 5, 9, 8, 0]`. Its parent is index 2 (value 2), which is larger, so swap: `[1, 3, 0, 5, 9, 8, 2]`. The new parent is index 0 (value 1), also larger, so swap: `[0, 3, 1, 5, 9, 8, 2]`. Index 0 is the root, so sift-up stops. Two swaps, at most $\lfloor \log_2 7 \rfloor = 2$ as predicted.
:::

:::question intermediate
Build a min-heap from `[9, 4, 7, 1, 2, 6, 5]` using the bottom-up method. Show the array after each sift-down.
:::answer
$n = 7$, so process indices 2, 1, 0. Index 2 (7) has children 6 and 5; swap with 5: `[9, 4, 5, 1, 2, 6, 7]`. Index 1 (4) has children 1 and 2; swap with 1: `[9, 1, 5, 4, 2, 6, 7]`. Index 0 (9) has children 1 and 5; swap with 1, giving `[1, 9, 5, 4, 2, 6, 7]`, then 9 at index 1 has children 4 and 2; swap with 2: `[1, 2, 5, 4, 9, 6, 7]`. That is the final heap.
:::

:::question intermediate
Explain in words why bottom-up heap construction is $O(n)$, even though each sift-down can cost $O(\log n)$.
:::answer
The cost of a sift-down is proportional to the height of the node, not the height of the tree. About half of all nodes are leaves and need no work, a quarter are one level up and need at most one swap, an eighth need at most two, and so on. Only the root can need $\log_2 n$ swaps. Adding these up, $n/4 \cdot 1 + n/8 \cdot 2 + n/16 \cdot 3 + \dots$, gives at most $n$, so the total is linear.
:::

:::question advanced
Show with a small example that heapsort is not stable.
:::answer
Sort two records with equal keys, `(1, 'a')` and `(1, 'b')`, comparing keys only. Building the max-heap changes nothing, because the child's key is not larger than the root's. Phase 2 then swaps the root with the last element, giving `(1, 'b')`, `(1, 'a')`: the two equal keys have exchanged their original order. A stable sort must keep `(1, 'a')` first.
:::

:::question advanced
You need the $k$ smallest of $n$ unsorted numbers. Compare (a) heapifying all $n$ numbers and popping $k$ times with (b) scanning once with a max-heap of size $k$.
:::answer
(a) Building the min-heap costs $O(n)$ and $k$ pops cost $O(k \log n)$, so the total is $O(n + k \log n)$, with $O(n)$ space if the input must be kept intact. (b) A max-heap of the $k$ smallest seen so far costs $O(\log k)$ per element, $O(n \log k)$ in total, with only $O(k)$ space. Method (a) is faster when $k$ is small relative to $n$ and the data fits in memory; method (b) suits streams, because it never stores more than $k$ items.
:::

## Further learning

- **Next:** *Graph Representations* begins the graphs module, where heaps reappear in shortest-path and spanning-tree algorithms.
- **Related:** *Priority Queues Overview* shows how to use heaps through Python's `heapq`.
- **Related:** *Merge Sort & QuickSort* compares heapsort with the two main divide-and-conquer sorts.
