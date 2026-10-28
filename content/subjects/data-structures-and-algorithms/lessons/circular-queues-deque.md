---
lesson: circular-queues-deque
title: Queues, Circular Buffers, and Deques
summary: The first-in, first-out queue, how a fixed array becomes an efficient ring buffer with modulo arithmetic, and the double-ended queue.
minutes: 45
type: theory
objectives:
  - Define the queue ADT and explain why a naive array implementation is inefficient
  - Implement a circular queue with front index, size, and modulo arithmetic, distinguishing full from empty
  - Describe the deque ADT and its uses, including the sliding-window maximum
  - Choose between list, collections.deque, and a ring buffer for a given workload
---

## Introduction

A **queue** is a line: the first item to join is the first to leave. This rule, **FIFO** (first in, first out), is the fair way to serve requests in arrival order, and it appears everywhere: print jobs waiting for a printer, packets waiting in a router, tasks waiting for a CPU, messages in a chat system, and the frontier of breadth-first search.

Queues look trivial until you implement them. Removing from the front of an array shifts every remaining element, so a careless implementation makes every dequeue cost $\Theta(n)$. The standard fix is the **circular buffer** (ring buffer): treat a fixed array as if its end wraps around to its beginning. This lesson builds one, then generalises to the **deque** (double-ended queue), which allows insertion and removal at both ends.

**Before you start:** you need arrays, linked lists, the stack ADT, and the modulo operator.

## Core theory

### The queue ADT

| Operation | Effect |
| :--- | :--- |
| `enqueue(x)` | add `x` at the back (rear) |
| `dequeue()` | remove and return the front item; error if empty |
| `peek()` / `front()` | return the front item without removing it |
| `is_empty()`, `size()` | report emptiness and the number of items |

All operations should be $O(1)$.

### Why a plain array is not enough

If items are stored in an array with the front at index 0, then `dequeue` removes `a[0]` and shifts everything left: $\Theta(n)$. In Python, `list.pop(0)` does exactly this. Keeping a moving "front" index avoids the shifting, but then the array fills up from the left as items leave, wasting space and eventually running off the end even when the queue is small.

### The circular buffer

Use a fixed-capacity array of size $C$ and treat index $C - 1$ as being followed by index 0. Keep:

- `front`: index of the current front item,
- `size`: number of items stored.

The back position is computed rather than stored:

$$\text{rear} = (\text{front} + \text{size}) \bmod C.$$

- **Enqueue:** if `size == C`, the queue is full. Otherwise write at `rear` and increment `size`.
- **Dequeue:** if `size == 0`, the queue is empty. Otherwise read `a[front]`, set `front = (front + 1) mod C`, and decrement `size`.

Both are $\Theta(1)$, and every slot of the array can be used.

### Full versus empty

A ring buffer that stores only a `front` and a `rear` index faces an ambiguity: `front == rear` could mean either empty or full. There are three standard solutions:

1. **Keep a size counter** (as above). This is the simplest.
2. **Leave one slot empty:** the buffer is full when `(rear + 1) mod C == front`. It can hold only $C - 1$ items.
3. **Keep a boolean flag** recording whether the last operation was an enqueue.

### Growing a ring buffer

When a circular queue must grow, copying the array as-is would break the wrap-around order. Instead, copy the items in queue order (front first) into the start of a larger array, and reset `front` to 0. With geometric growth, enqueue becomes amortized $O(1)$, just as for dynamic arrays.

### Linked-list queues

A singly linked list with both a head and a tail pointer also gives $O(1)$ enqueue (at the tail) and dequeue (at the head). It never fills up, but pays a pointer per item and has poorer cache behaviour.

### The deque

A **deque** (pronounced "deck") supports `push_front`, `push_back`, `pop_front`, and `pop_back`, all in $O(1)$. A circular buffer supports this directly: pushing at the front moves `front` back one slot, $(\text{front} - 1) \bmod C$. A doubly linked list also works.

Python's `collections.deque` provides $O(1)$ appends and pops at both ends (it is implemented as a doubly linked list of fixed-size blocks). Indexing into the middle of a deque is $O(n)$, so it is not a replacement for a list when you need random access.

| Need | Best Python choice |
| :--- | :--- |
| Stack (LIFO) | `list` with `append` and `pop` |
| Queue (FIFO) | `collections.deque` with `append` and `popleft` |
| Fixed-size recent history | `collections.deque(maxlen=k)` |
| Random access by index | `list` |

### The monotonic deque

A deque kept in sorted order solves the **sliding-window maximum**: for every window of size $k$, report its maximum. Keep indices in the deque with decreasing values. For each new element, pop from the back every index with a smaller value (it can never be a window maximum again), push the new index, and pop from the front if that index has slid out of the window. The front is always the current maximum. Each index is pushed and popped at most once, so the whole computation is $\Theta(n)$ instead of $\Theta(nk)$.

## Worked examples

### Example 1: A circular queue

```python
class CircularQueue:
    def __init__(self, capacity):
        self.data = [None] * capacity
        self.front = 0
        self.size = 0

    def enqueue(self, item):
        if self.size == len(self.data):
            raise OverflowError("queue is full")
        rear = (self.front + self.size) % len(self.data)
        self.data[rear] = item
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            raise IndexError("queue is empty")
        item = self.data[self.front]
        self.data[self.front] = None          # release the reference
        self.front = (self.front + 1) % len(self.data)
        self.size -= 1
        return item

q = CircularQueue(4)
for job in ("A", "B", "C"):
    q.enqueue(job)
print(q.dequeue(), q.dequeue())
for job in ("D", "E", "F"):
    q.enqueue(job)                             # wraps around the end
print(q.data, q.front, q.size)
print([q.dequeue() for _ in range(4)])
```

Output:

```text
A B
['E', 'F', 'C', 'D'] 2 4
['C', 'D', 'E', 'F']
```

After two dequeues, `front` is 2. Enqueuing D fills index 3, then E and F wrap around to indices 0 and 1. The raw array looks out of order, but reading from `front` around the ring gives C, D, E, F, which is the correct FIFO order.

### Example 2: Index arithmetic by hand

Capacity $C = 5$, `front` $= 3$, `size` $= 4$. The items occupy indices 3, 4, 0, 1. Where does the next enqueue write?

$$\text{rear} = (3 + 4) \bmod 5 = 2.$$

After one dequeue, `front` $= (3 + 1) \bmod 5 = 4$ and `size` $= 3$, so the occupied indices are 4, 0, 1.

### Example 3: Sliding-window maximum with a deque

```python
from collections import deque

def window_maxima(values, k):
    candidates = deque()            # indices; values decrease front to back
    result = []
    for i, v in enumerate(values):
        while candidates and values[candidates[-1]] <= v:
            candidates.pop()        # smaller values can never be a maximum again
        candidates.append(i)
        if candidates[0] <= i - k:
            candidates.popleft()    # the front has left the window
        if i >= k - 1:
            result.append(values[candidates[0]])
    return result

print(window_maxima([1, 3, -1, -3, 5, 3, 6, 7], 3))
```

Output:

```text
[3, 3, 5, 5, 6, 7]
```

For the window `[-1, -3, 5]`, the arrival of 5 pops both -3 and -1 from the back, because neither can ever be a maximum while 5 is in the window. The front of the deque is always the index of the largest value in the current window.

### Example 4: Breadth-first order with a queue

```python
from collections import deque

tree = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": [], "F": []}

def level_order(root):
    order, queue = [], deque([root])
    while queue:
        node = queue.popleft()      # O(1), unlike list.pop(0)
        order.append(node)
        queue.extend(tree[node])
    return order

print(level_order("A"))
```

Output:

```text
['A', 'B', 'C', 'D', 'E', 'F']
```

Because the queue serves nodes in the order they were discovered, all nodes at depth 1 are visited before any at depth 2. This FIFO property is exactly what breadth-first search needs.

## Applications

- **Operating systems**: ready queues for processes, I/O request queues, and keyboard buffers are queues, often ring buffers in the kernel.
- **Networking**: routers and network cards buffer packets in ring buffers; audio and video streaming use them to smooth playback.
- **Producer-consumer systems**: message brokers and logging pipelines pass work between threads through queues.
- **Graph algorithms**: breadth-first search, shortest paths in unweighted graphs, and topological sorting with Kahn's algorithm use queues.
- **Recent-history features**: "last 100 commands" or a rolling window of sensor readings fit `deque(maxlen=100)`.

## Common mistakes

- **Using `list.pop(0)` as a dequeue,** which is $O(n)$ per operation; use `collections.deque.popleft()`.
- **Confusing full and empty** in a ring buffer that stores only `front` and `rear`.
- **Forgetting the modulo** when advancing indices, which runs past the end of the array.
- **Copying a wrapped ring buffer directly when resizing,** which scrambles the order; copy in queue order instead.
- **Indexing into the middle of a deque** in a hot loop; deques are fast only at the ends.

## Revision notes

- Queue = FIFO: enqueue at the back, dequeue at the front, both $O(1)$.
- Ring buffer: `rear = (front + size) % C`; advance `front = (front + 1) % C`.
- Distinguish full and empty with a size counter, a spare slot, or a flag.
- Resize by copying in queue order and resetting `front` to 0.
- Deque: $O(1)$ at both ends; Python's `collections.deque` for queues and deques.
- Monotonic deque gives the sliding-window maximum in $\Theta(n)$.

## Practice questions

:::question basic
Why is `list.pop(0)` a poor way to implement `dequeue` in Python, and what should be used instead?
:::answer
`list.pop(0)` removes the first element of a dynamic array and shifts every remaining element one place left, costing $\Theta(n)$ per dequeue. `collections.deque` with `append` and `popleft` performs both operations in $O(1)$.
:::

:::question basic
A circular queue has capacity 6, `front = 4`, and `size = 3`. Which indices hold items, and where will the next item be enqueued?
:::answer
The items are at indices 4, 5, and 0 (wrapping around). The next enqueue writes at $(4 + 3) \bmod 6 = 1$.
:::

:::question intermediate
A ring buffer stores only `front` and `rear` indices, with `rear` pointing to the next free slot. Explain why `front == rear` is ambiguous and give two ways to resolve it.
:::answer
When the queue is empty, `rear` has caught up with `front`. When the queue is completely full, `rear` has wrapped around and also equals `front`. So the same condition describes two different states. Resolve it by keeping a separate size count (full when size equals capacity), or by never filling the last slot (full when `(rear + 1) % C == front`, so the buffer holds at most $C - 1$ items).
:::

:::question intermediate
Trace the sliding-window maximum algorithm on `[4, 2, 12, 3]` with $k = 2$, giving the deque contents (as values) after each element and the outputs.
:::answer
4: deque [4]; no output yet. 2: [4, 2]; output 4 (window 4, 2). 12: pops 2 and 4 (both at most 12), deque [12]; output 12 (window 2, 12). 3: [12, 3]; index of 12 is still inside the window (12, 3), so output 12. Outputs: `[4, 12, 12]`.
:::

:::question intermediate
When a full circular queue is resized to double its capacity, why must the items be copied starting from `front` rather than from index 0?
:::answer
The items occupy a contiguous run that may wrap around the end of the array, for example indices 3, 4, 0, 1. Copying index 0 first would place later items before earlier ones and corrupt the FIFO order. Copying from `front` around the ring into indices 0, 1, 2, ... of the new array preserves the order, after which `front` is reset to 0.
:::

:::question advanced
Show how to implement a queue using two stacks so that each operation is amortized $O(1)$, and explain why the amortized bound holds.
:::answer
Keep an `inbox` stack for enqueues and an `outbox` stack for dequeues. Enqueue pushes onto `inbox`. Dequeue pops from `outbox`; if `outbox` is empty, first pop every element of `inbox` and push it onto `outbox`, which reverses their order so the oldest element is on top. An individual dequeue can move many elements, but each element is moved from `inbox` to `outbox` at most once in its lifetime. So over any sequence of $n$ operations the total work is $O(n)$, giving amortized $O(1)$ per operation.
:::

## Further learning

- **Next:** *Priority Queues Overview* replaces arrival order with priority order.
- **Related:** *Breadth-First Search & Depth-First Search* uses a queue to explore a graph level by level.
- **Related:** *Monotonic Stacks & Parentheses* covers the stack-based relative of the monotonic deque.
