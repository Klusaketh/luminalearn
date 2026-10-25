---
lesson: amortized-analysis
title: Amortized Analysis
summary: Bound the average cost per operation over a worst-case sequence, and see why dynamic-array appends and binary counters are cheap on average.
minutes: 45
type: theory
objectives:
  - Explain how amortized cost differs from worst-case cost per operation and from average-case cost over random inputs
  - Apply the aggregate method to dynamic-array appends and a binary counter
  - Use the accounting and potential methods to prove an amortized bound
  - Recognise operations whose occasional expensive steps are paid for by many cheap ones
---

## Introduction

Some data structures are usually fast but occasionally slow. Appending to a Python list is a single memory write almost every time, but now and then the list runs out of room and must copy every element into a bigger block of memory. If you judged appends by that worst single operation, you would call them $\Theta(n)$ and conclude that building a list of $n$ items takes $\Theta(n^2)$ time. In reality it takes $\Theta(n)$.

**Amortized analysis** explains the gap. Instead of bounding one operation in isolation, it bounds the **total cost of any sequence of $n$ operations** and divides by $n$. The expensive steps are rare enough that, spread across the cheap ones, each operation costs only a constant amount on average. Crucially, this is a guarantee for every sequence, not an average over lucky inputs.

**Before you start:** you need Big-O notation and the formula for a geometric series, $1 + 2 + 4 + \dots + 2^k = 2^{k+1} - 1$.

## Core theory

### Three different "averages"

| Kind of bound | What it guarantees |
| :--- | :--- |
| Worst case per operation | No single operation ever costs more than this. |
| Average case | Expected cost when inputs are drawn from an assumed probability distribution. |
| Amortized | Over **any** sequence of $n$ operations, the total cost is at most $n$ times this bound. |

Amortized analysis involves no probability. If appends are amortized $O(1)$, then any program that performs $n$ appends spends $O(n)$ time on them in total, whatever values it appends and in whatever order.

### The aggregate method

Compute the total cost $T(n)$ of a worst-case sequence of $n$ operations directly, then the amortized cost per operation is $T(n)/n$.

**Dynamic array with doubling.** A dynamic array stores elements in a fixed-capacity block. Appending into spare capacity costs 1 (one write). When the block is full, the array allocates a block twice as large and copies all $k$ existing elements (cost $k$) before writing the new one.

Starting from capacity 1 and appending $n$ items, resizes happen when the size reaches $1, 2, 4, 8, \dots$, copying that many elements each time. The total copying cost is at most

$$1 + 2 + 4 + \dots + 2^{\lfloor \log_2 n \rfloor} < 2n.$$

Adding the $n$ ordinary writes gives a total below $3n$, so each append is **amortized $O(1)$**.

**Why doubling matters.** If the array grew by a fixed amount instead (say 10 extra slots each time), resizes would happen every 10 appends and copy $10, 20, 30, \dots$ elements, a total of about $n^2/20$. That is $\Theta(n)$ amortized per append. Growing by a constant **factor** (any factor greater than 1, such as 1.5 or 2) is what keeps the amortized cost constant. CPython grows lists by roughly 1.125 times plus a small constant, trading a little more copying for less wasted capacity.

### The accounting method

Charge each operation an **amortized cost** that may be more or less than its actual cost. When the charge exceeds the actual cost, the difference is stored as **credit** on specific elements of the data structure. Expensive operations spend that credit. The bound is valid as long as the credit never goes negative.

For the doubling array, charge **3** per append:

- 1 pays for writing the new element,
- 1 is stored on the new element to pay for moving it at the next resize,
- 1 is stored on an older element (one that was already moved once) to pay for moving it again.

When an array of capacity $k$ fills up, the $k/2$ elements added since the last resize each carry 2 credits, which is exactly enough to move all $k$ elements. Credit never runs out, so every append costs at most 3 amortized.

### The potential method

Define a **potential function** $\Phi$ that maps the state of the data structure to a non-negative number, starting at $\Phi = 0$. Think of it as stored energy. The amortized cost of an operation is

$$\hat{c} = c_{\text{actual}} + \Phi_{\text{after}} - \Phi_{\text{before}}.$$

Summing over a sequence, the potential differences telescope, so the total amortized cost equals the total actual cost plus $\Phi_{\text{final}} - \Phi_{\text{initial}} \ge$ total actual cost. A good potential is large just before an expensive operation, so the drop in potential pays for it.

For the doubling array, use $\Phi = 2 \cdot \text{size} - \text{capacity}$ (which is at least zero once the array is at least half full, as it always is after the first resize):

- **Cheap append** (no resize): actual cost 1, size rises by 1, so $\Phi$ rises by 2. Amortized cost $= 1 + 2 = 3$.
- **Resizing append** when size $=$ capacity $= k$: actual cost $k + 1$. Before: $\Phi = 2k - k = k$. After: size $k+1$, capacity $2k$, so $\Phi = 2(k+1) - 2k = 2$. Amortized cost $= (k+1) + 2 - k = 3$.

Every append has amortized cost 3, matching the other two methods.

### Where amortized bounds appear

- Dynamic arrays (Python `list`, Java `ArrayList`, C++ `std::vector`): append is amortized $O(1)$.
- Hash tables that resize when the load factor gets high: insertion is amortized $O(1)$ (expected, because of hashing).
- A queue built from two stacks: each element is moved between stacks at most once, so each operation is amortized $O(1)$.
- Union-find with path compression and union by rank: nearly constant amortized time per operation.
- Splay trees: $O(\log n)$ amortized per operation, although a single operation can take $\Theta(n)$.

### A caution about real-time systems

Amortized $O(1)$ still allows an individual operation to take $\Theta(n)$. In a game rendering at 60 frames per second, or a controller in a car, one long pause can be unacceptable even if the average is excellent. Such systems use structures with worst-case guarantees, or spread the resize work incrementally across many operations.

## Worked examples

### Example 1: Measuring the copying cost of appends

```python
def append_cost(n, grow):
    capacity, size, copies = 1, 0, 0
    for _ in range(n):
        if size == capacity:
            copies += size          # move every existing element
            capacity = grow(capacity)
        size += 1
    return copies

doubling = lambda c: 2 * c
plus_ten = lambda c: c + 10

for n in (1_000, 10_000, 100_000):
    print(n, append_cost(n, doubling), append_cost(n, plus_ten))
```

Output:

```text
1000 1023 49600
10000 16383 4996000
100000 131071 499960000
```

With doubling, the copying stays below $2n$ (1023 for 1000 appends, 131071 for 100000). With a fixed increment of 10 it grows quadratically: multiplying $n$ by 10 multiplies the copies by about 100. The amortized cost per append is therefore constant for doubling and linear for a fixed increment.

### Example 2: A binary counter (aggregate method)

Incrementing a binary counter flips trailing 1s to 0 and then one 0 to 1. Incrementing from `0111` gives `1000`, flipping 4 bits; from `1000` to `1001` flips only 1.

A single increment can flip all $k$ bits, so the worst case per operation is $\Theta(k)$. But over $n$ increments starting from 0:

- bit 0 flips every time: $n$ flips,
- bit 1 flips every second time: $\lfloor n/2 \rfloor$ flips,
- bit $i$ flips every $2^i$ times: $\lfloor n/2^i \rfloor$ flips.

The total is at most $n(1 + \tfrac12 + \tfrac14 + \dots) < 2n$, so each increment is amortized $O(1)$.

```python
def total_flips(n):
    bits, flips = [0] * 32, 0
    for _ in range(n):
        i = 0
        while bits[i] == 1:     # trailing ones become zeros
            bits[i] = 0
            flips += 1
            i += 1
        bits[i] = 1             # first zero becomes one
        flips += 1
    return flips

for n in (8, 1000, 1024):
    print(n, total_flips(n), 2 * n)
```

Output:

```text
8 15 16
1000 1994 2000
1024 2047 2048
```

The measured totals stay just under $2n$, as the analysis predicts.

### Example 3: A queue from two stacks (accounting method)

```python
class TwoStackQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []

    def enqueue(self, x):
        self.inbox.append(x)

    def dequeue(self):
        if not self.outbox:                 # refill only when empty
            while self.inbox:
                self.outbox.append(self.inbox.pop())
        return self.outbox.pop()

q = TwoStackQueue()
for x in (1, 2, 3):
    q.enqueue(x)
print(q.dequeue(), q.dequeue())
q.enqueue(4)
print(q.dequeue(), q.dequeue())
```

Output:

```text
1 2
3 4
```

A dequeue that finds `outbox` empty may move $k$ elements, costing $\Theta(k)$. Charge each enqueue 3 credits: 1 for the push onto `inbox`, 1 for the later pop from `inbox`, and 1 for the push onto `outbox`. The final pop from `outbox` costs 1 and is charged to the dequeue. Each element is moved from `inbox` to `outbox` at most once, so its prepaid credits always cover the move. Therefore every operation is amortized $O(1)$, even though an individual dequeue can be slow.

## Applications

- **Standard library collections.** Python lists, Java `ArrayList`, and C++ `vector` all rely on geometric growth so that appends are amortized constant time.
- **Hash tables** in every major language resize by a constant factor when they fill up, keeping insertion amortized constant.
- **Garbage-collected runtimes** amortize collection cost over many allocations.
- **Algorithm analysis.** Bounds for union-find, Fibonacci heaps (used in fast shortest-path and spanning-tree algorithms), and splay trees are all amortized.
- **Systems engineering.** Knowing that the cost is amortized tells engineers when to pre-size a collection (for example, `ArrayList(initialCapacity)` in Java) to avoid latency spikes.

## Common mistakes

- **Confusing amortized with average case.** Amortized bounds need no assumptions about input distribution; they hold for the worst sequence.
- **Believing amortized $O(1)$ means every operation is fast.** One operation can still take linear time.
- **Growing by a constant amount instead of a constant factor.** Adding a fixed number of slots on each resize makes appends amortized $\Theta(n)$.
- **Letting credit go negative in the accounting method.** The argument only works if stored credit always covers the expensive operations.
- **Using a potential function that can be negative,** which breaks the inequality that makes total amortized cost an upper bound on total actual cost.

## Revision notes

- Amortized cost = total cost of a worst-case sequence divided by the number of operations.
- Three methods: aggregate (sum directly), accounting (prepay with credits), potential ($\hat c = c + \Delta\Phi$, $\Phi \ge 0$).
- Doubling dynamic array: copies total less than $2n$, so append is amortized $O(1)$; fixed increments give amortized $O(n)$.
- Binary counter: fewer than $2n$ flips over $n$ increments, amortized $O(1)$.
- Two-stack queue: each element moves once, amortized $O(1)$ per operation.
- Amortized bounds do not prevent occasional slow operations; real-time systems may need worst-case bounds.

## Practice questions

:::question basic
A dynamic array doubles its capacity when full. How many element copies are performed in total while appending 16 items, starting from capacity 1? What is the amortized copying cost per append?
:::answer
Resizes happen when size reaches 1, 2, 4, and 8, copying 1 + 2 + 4 + 8 = 15 elements. (The 16th append fits into capacity 16, so no copy is needed.) Over 16 appends that is $15/16 < 1$ copy per append on average, which is a constant, so copying is amortized $O(1)$ per append.
:::

:::question basic
Explain the difference between "this operation is $O(1)$ amortized" and "this operation is $O(1)$ on average".
:::answer
Amortized $O(1)$ means that any sequence of $n$ operations costs $O(n)$ in total, for every possible sequence; no probability is involved. Average $O(1)$ means the expected cost is constant under some assumed distribution of inputs, so a particular unlucky input sequence could cost more. Amortized is a worst-case guarantee about totals.
:::

:::question intermediate
A dynamic array grows by 50% (capacity $\to \lceil 1.5 \times \text{capacity} \rceil$) instead of doubling. Is appending still amortized $O(1)$? Explain.
:::answer
Yes. The capacities form a geometric sequence with ratio 1.5, so the total copying is bounded by a geometric series: the last resize copies at most $n$ elements, the one before about $n/1.5$, then $n/1.5^2$, and so on. The sum is at most $n \cdot \frac{1}{1 - 1/1.5} = 3n$, which is $O(n)$ in total, so $O(1)$ amortized. Any constant growth factor greater than 1 works; smaller factors waste less memory but copy more often.
:::

:::question intermediate
In the two-stack queue, a single `dequeue` can take time proportional to the number of stored elements. Describe a sequence of operations that triggers this, and explain why it does not break the amortized bound.
:::answer
Enqueue $n$ elements, then dequeue once: the first dequeue moves all $n$ elements from `inbox` to `outbox`, costing $\Theta(n)$. But each of those $n$ elements was enqueued with prepaid credit for that one move, and none of them will ever be moved again (later dequeues pop directly from `outbox`). Over the $n$ enqueues plus the following dequeues, total work is $O(n)$ for $O(n)$ operations.
:::

:::question advanced
A stack supports `push`, `pop`, and `multipop(k)`, which pops $\min(k, \text{size})$ elements. A single `multipop` can cost $\Theta(n)$. Use the potential method with $\Phi = $ number of elements on the stack to show every operation is amortized $O(1)$.
:::answer
$\Phi$ starts at 0 and is never negative. `push`: actual cost 1, $\Phi$ rises by 1, amortized cost 2. `pop`: actual cost 1, $\Phi$ falls by 1, amortized cost 0. `multipop(k)` popping $m = \min(k, s)$ elements: actual cost $m$, $\Phi$ falls by $m$, amortized cost $m - m = 0$. Every operation has amortized cost at most 2, so any sequence of $n$ operations costs at most $2n$ in total. Intuitively, an element can be popped only once after being pushed once.
:::

:::question advanced
Why might a real-time audio application avoid a standard dynamic array for its sample buffer, even though appends are amortized $O(1)$? Suggest an alternative.
:::answer
Audio processing must finish each small chunk of work before a hard deadline (a few milliseconds), or the sound glitches. An append that triggers a resize copies the whole buffer, which can take far longer than the deadline, even though such appends are rare. Alternatives are to preallocate a fixed-capacity ring buffer sized for the worst case, or to use a structure with worst-case $O(1)$ operations so that no single operation can cause a long pause.
:::

## Further learning

- **Next:** *Static vs Dynamic Arrays* looks at how dynamic arrays are laid out in memory and why indexing is constant time.
- **Related:** *Minimum Spanning Trees & Disjoint Sets* uses union-find, whose near-constant amortized time is one of the most celebrated results in algorithm analysis.
- **Related:** *Hash Functions & Collision Handling* explains how resizing by a constant factor keeps hash-table operations fast.
