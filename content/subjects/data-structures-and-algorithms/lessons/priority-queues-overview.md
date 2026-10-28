---
lesson: priority-queues-overview
title: Priority Queues
summary: Serve items by priority instead of arrival order, compare implementations, and use Python's heapq for scheduling, top-k, and merging problems.
minutes: 45
type: theory
objectives:
  - Define the priority queue ADT and distinguish it from a FIFO queue
  - Compare unsorted-array, sorted-array, and heap implementations by the cost of insert and extract-min
  - Use Python's heapq module, including tie-breaking with tuples and simulating a max-heap
  - Solve top-k, k-way merge, and simple scheduling problems with a priority queue
---

## Introduction

A regular queue serves items in the order they arrive. Many real systems need something different: an emergency room treats the most critical patient first, an operating system runs the highest-priority process, a network router forwards real-time voice packets before bulk downloads, and a navigation algorithm always expands the closest unexplored location. In each case the next item to serve is the one with the **highest priority**, whenever it arrived.

A **priority queue** is the abstract data type for this. Its efficient implementation, the **binary heap**, is covered in detail in the heaps module; here we focus on what a priority queue does, how different implementations compare, and how to use one well.

**Before you start:** you should know queues, arrays, and logarithmic complexity.

## Core theory

### The priority queue ADT

Each item has a **key** (its priority). In a **min-priority queue**, smaller keys are served first; in a max-priority queue, larger keys are served first.

| Operation | Effect |
| :--- | :--- |
| `insert(item, key)` | add an item with the given priority |
| `find_min()` (peek) | return the item with the smallest key |
| `extract_min()` (pop) | remove and return the item with the smallest key |
| `is_empty()`, `size()` | report emptiness and the number of items |
| `decrease_key(item, new_key)` | lower an item's key (needed by some graph algorithms) |

A priority queue does **not** keep all items sorted, and it does not support efficient search for arbitrary items. It only guarantees fast access to the extreme element.

### Implementation choices

| Implementation | insert | find_min | extract_min | Build from $n$ items |
| :--- | :--- | :--- | :--- | :--- |
| Unsorted array | $O(1)$ amortized | $O(n)$ | $O(n)$ | $O(n)$ |
| Sorted array (min at the end) | $O(n)$ | $O(1)$ | $O(1)$ | $O(n \log n)$ |
| Binary heap | $O(\log n)$ | $O(1)$ | $O(\log n)$ | $O(n)$ |
| Balanced BST | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | $O(n \log n)$ |

The unsorted array makes insertion cheap and extraction expensive; the sorted array does the reverse. The **binary heap** balances both at $O(\log n)$, which is why it is the standard choice. For $n$ inserts followed by $n$ extractions, the arrays cost $\Theta(n^2)$ in total while the heap costs $\Theta(n \log n)$.

### The heap in one paragraph

A binary min-heap is a complete binary tree stored in an array, where every parent's key is at most its children's keys. The minimum is therefore at the root, index 0. Inserting appends at the end and "sifts up" by swapping with the parent while it is smaller; extracting moves the last element to the root and "sifts down". Each sift follows one path between the root and a leaf, and the tree's height is $\lfloor \log_2 n \rfloor$, giving $O(\log n)$ operations. The *Min & Max Heap Implementation* lesson builds this from scratch.

### Python's heapq

The standard library module `heapq` implements a min-heap on an ordinary list:

- `heapq.heappush(heap, item)`: insert, $O(\log n)$.
- `heapq.heappop(heap)`: remove and return the smallest, $O(\log n)$.
- `heap[0]`: peek at the smallest, $O(1)$.
- `heapq.heapify(list)`: rearrange a list into a heap in place, $O(n)$.
- `heapq.nsmallest(k, items)` and `heapq.nlargest(k, items)`: convenience functions for top-k.

Items are compared directly, so tuples `(priority, item)` are the usual way to attach priorities. Two practical issues arise:

- **Ties.** If two tuples have equal priority, Python compares the second elements, which fails if they are not comparable (for example, two dictionaries). Insert `(priority, counter, item)`, where `counter` increases with each insertion; it breaks ties in insertion order (making the queue stable) and is never equal for two entries.
- **Max-heaps.** `heapq` only provides a min-heap. For a max-heap, push negated keys, `(-priority, ...)`, and negate again when popping.

### decrease-key and lazy deletion

Some algorithms, notably Dijkstra's shortest paths, need to lower the priority of an item already in the queue. `heapq` has no `decrease_key`. The common workaround is **lazy deletion**: push a new entry with the better key, leave the old entry in the heap, and when an entry is popped, skip it if it is stale (its item was already finalised or has a better recorded key). This keeps operations $O(\log n)$ at the cost of a larger heap.

## Worked examples

### Example 1: Scheduling tasks by priority

```python
import heapq
from itertools import count

tasks, order = [], count()

def add_task(priority, name):
    heapq.heappush(tasks, (priority, next(order), name))

add_task(3, "write report")
add_task(1, "fix outage")
add_task(2, "review pull request")
add_task(1, "page on-call")

while tasks:
    priority, _, name = heapq.heappop(tasks)
    print(priority, name)
```

Output:

```text
1 fix outage
1 page on-call
2 review pull request
3 write report
```

The two priority-1 tasks come out in the order they were added because the counter breaks the tie. Without the counter, equal priorities would fall back to comparing the task names alphabetically, which is not what a scheduler should do.

### Example 2: Top-k largest values in a stream

```python
import heapq

def top_k(stream, k):
    heap = []                       # min-heap of the k largest seen so far
    for x in stream:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)   # pop the smallest, push x, one sift
    return sorted(heap, reverse=True)

readings = [42, 7, 99, 13, 58, 77, 3, 88, 64]
print(top_k(readings, 3))
```

Output:

```text
[99, 88, 77]
```

Keeping a **min**-heap of size $k$ for the **largest** values sounds backwards, but it is exactly right: the root is the smallest of the current top $k$, the value a new candidate must beat. Each item costs $O(\log k)$, so processing $n$ items is $O(n \log k)$ time with $O(k)$ space, far better than sorting everything when $k$ is small or the stream is too large to store.

### Example 3: Merging $k$ sorted lists

```python
import heapq

def merge_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    merged = []
    while heap:
        value, i, j = heapq.heappop(heap)
        merged.append(value)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return merged

print(merge_sorted([[1, 4, 9], [2, 3, 10], [0, 8]]))
```

Output:

```text
[0, 1, 2, 3, 4, 8, 9, 10]
```

The heap holds at most one element from each list: the smallest not yet output. Popping gives the global next element, and pushing its successor keeps one representative per list. For $N$ total elements across $k$ lists, the time is $O(N \log k)$. Python's own `heapq.merge` works this way, and external sorting uses the same idea to merge sorted runs from disk.

## Applications

- **Operating system schedulers** pick the highest-priority runnable process; real-time systems order work by deadline.
- **Graph algorithms**: Dijkstra's shortest paths and Prim's minimum spanning tree repeatedly extract the closest vertex; A* search orders nodes by estimated total cost.
- **Event-driven simulation** processes events in timestamp order by keeping future events in a priority queue.
- **Data compression**: Huffman coding repeatedly merges the two least frequent symbols.
- **Streaming analytics**: top-k queries, median maintenance with two heaps, and merging sorted log files from many servers.

## Common mistakes

- **Expecting a priority queue to be sorted.** Only the root is guaranteed to be the minimum; iterating over a `heapq` list does not give sorted order.
- **Pushing tuples whose tie-breaking element is not comparable,** which raises a `TypeError` when priorities are equal. Add a counter.
- **Forgetting that heapq is a min-heap.** Negate keys to get max-heap behaviour.
- **Searching the heap for an item to update,** which is $O(n)$; use lazy deletion or an indexed heap.
- **Using a priority queue when a plain queue suffices.** If all priorities are equal or follow arrival order, a FIFO queue is simpler and $O(1)$.

## Revision notes

- Priority queue: insert and extract the minimum (or maximum); no fast search or full ordering.
- Unsorted array: insert $O(1)$, extract $O(n)$. Sorted array: insert $O(n)$, extract $O(1)$. Heap: both $O(\log n)$, peek $O(1)$, build $O(n)$.
- `heapq`: `heappush`, `heappop`, `heap[0]`, `heapify`, `heapreplace`, `nsmallest`, `nlargest`.
- Use `(priority, counter, item)` for stable tie-breaking; negate priorities for a max-heap.
- Top-k largest: min-heap of size $k$, $O(n \log k)$. Merge $k$ sorted lists: $O(N \log k)$.
- No decrease-key in heapq: use lazy deletion.

## Practice questions

:::question basic
How does a priority queue differ from a FIFO queue? Give one real situation that needs each.
:::answer
A FIFO queue removes items in arrival order; a priority queue removes the item with the highest priority regardless of arrival time. A print queue in an office fits FIFO (first come, first served). An emergency department's triage queue needs a priority queue, because a critical patient who arrives later must be seen first.
:::

:::question basic
You insert 5, 1, 8, 3 into a min-priority queue and then call extract_min twice. Which values are returned?
:::answer
1 and then 3. Each extract_min returns the smallest key still present: first 1, then the smallest of the remaining 5, 8, 3, which is 3.
:::

:::question intermediate
Compare the total cost of inserting $n$ items and then extracting all of them, using (a) an unsorted array, (b) a sorted array, and (c) a binary heap.
:::answer
(a) Inserts are $O(1)$ each, but each extraction scans for the minimum, $O(n)$, giving $O(n^2)$ in total. (b) Each insertion may shift elements to keep order, $O(n)$, giving $O(n^2)$ for inserts, with $O(1)$ extractions. (c) Both operations are $O(\log n)$, so the total is $O(n \log n)$. The heap is the only one that is not quadratic.
:::

:::question intermediate
Why do we push `(priority, counter, task)` instead of `(priority, task)` into a heapq-based scheduler?
:::answer
When two entries have the same priority, Python compares the next tuple element. If tasks are objects that cannot be compared (for example dictionaries or custom classes without ordering), this raises a `TypeError`. Even when comparison works, it orders tasks by an irrelevant property such as their name. A strictly increasing counter is always comparable and never ties, so equal priorities are served in insertion order.
:::

:::question intermediate
How would you use heapq to always retrieve the largest number first?
:::answer
Push the negated value, `heapq.heappush(heap, -x)`, so the largest original value becomes the smallest stored value and sits at the root. When popping, negate again: `-heapq.heappop(heap)`. For tuples, negate only the priority component, for example `(-priority, counter, item)`.
:::

:::question advanced
Explain why finding the $k$ largest of $n$ numbers with a min-heap of size $k$ takes $O(n \log k)$ time, and why a min-heap (not a max-heap) is used.
:::answer
The heap never holds more than $k$ items, so each push, pop, or replace costs $O(\log k)$, and each of the $n$ items triggers at most one such operation, giving $O(n \log k)$. A min-heap is used because the decision for each new item is "is it larger than the smallest of my current top $k$?" The min-heap keeps that smallest value at the root, available in $O(1)$; if the new item is larger, it replaces the root. A max-heap would put the largest value at the root, which is useless for this test.
:::

## Further learning

- **Next:** *Hash Functions & Collision Handling* covers the structure behind constant-time dictionaries and sets.
- **Related:** *Min & Max Heap Implementation* builds the binary heap and proves its operation costs.
- **Related:** *Shortest Paths: Dijkstra & Bellman-Ford* uses a priority queue with lazy deletion at its core.
