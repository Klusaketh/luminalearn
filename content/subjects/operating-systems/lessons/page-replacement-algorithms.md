---
lesson: page-replacement-algorithms
title: Page Replacement Algorithms
summary: When memory is full and a page fault occurs, choose a victim page with FIFO, optimal, LRU, or second-chance (clock) replacement, count page faults for reference strings, and understand Belady's anomaly.
minutes: 45
type: theory
objectives:
  - Simulate FIFO, optimal (OPT), and LRU page replacement on a reference string and count page faults
  - Explain Belady's anomaly and why stack algorithms such as LRU and OPT are immune to it
  - Describe how LRU can be implemented exactly and why hardware uses approximations such as the clock algorithm
  - Compare global and local replacement and the role of the dirty bit in eviction cost
---

## Introduction

Demand paging works beautifully until memory fills up. Then every page fault forces a choice: some page already in memory must be evicted to make room. Choose well and the evicted page will not be needed again for a long time; choose badly and it will be needed almost immediately, causing another fault, another disk read, and possibly another bad choice.

Because a page fault costs millions of times more than a memory access, the **page-replacement algorithm** has a large effect on performance. This lesson simulates the classic algorithms on the same input so that their behaviour can be compared exactly: first-in, first-out (FIFO), the theoretically optimal algorithm, least recently used (LRU), and the clock algorithm that real systems use to approximate LRU cheaply. Along the way we meet a famous surprise, **Belady's anomaly**, in which giving a program more memory makes it fault more.

**Before you start:** you should know demand paging, page faults, and the referenced and dirty bits.

## Core theory

### Reference strings and fault counts

Algorithms are compared on a **reference string**: the sequence of page numbers a program accesses, with consecutive repeats of the same page removed (they cannot fault). For a given number of frames, the algorithm with **fewer page faults** is better. Faults that fill initially empty frames, called **compulsory** or **cold** faults, happen under every algorithm.

### FIFO

Evict the page that has been in memory **longest**, regardless of how often it is used. A queue of pages in arrival order implements it. FIFO is simple but blind: the oldest page might be a heavily used one, such as a variable initialised early and used throughout.

### Optimal (OPT, or MIN)

Evict the page that will **not be used for the longest time in the future**. László Bélády showed in 1966 that this gives the lowest possible number of faults for any reference string and number of frames. It cannot be implemented in a real system, because it needs to know the future, but it is the yardstick against which practical algorithms are measured.

### Least recently used (LRU)

Evict the page that has **not been used for the longest time in the past**, using the recent past as a prediction of the near future. Thanks to locality, LRU usually performs well, close to OPT.

Exact LRU needs to know, at every fault, which page was used least recently:

- **Counters:** store a timestamp in a page's entry on every access, and evict the page with the oldest timestamp, which needs a search and a write on every memory access.
- **Stack:** keep a doubly linked list of pages ordered by recency, moving a page to the top on every access, which costs several pointer updates per access.

Either way, the work happens on **every memory reference**, which is far too slow without special hardware, so real systems approximate LRU.

### Approximating LRU: the clock (second-chance) algorithm

Hardware sets each page's **referenced bit** when the page is accessed. The **clock algorithm** arranges frames in a circle with a "hand":

1. On a fault, look at the page under the hand.
2. If its referenced bit is 1, clear it (giving the page a **second chance**) and advance the hand.
3. If it is 0, evict that page, put the new page in the frame with its referenced bit set, and advance the hand.

A page that is used regularly keeps getting its bit set and survives; a page that has not been used since the hand last passed is evicted. If every bit is set, the hand goes all the way round and the algorithm behaves like FIFO. An **enhanced** version also considers the **dirty bit**, preferring clean, unreferenced pages, because evicting a dirty page needs a disk write first.

### Belady's anomaly and stack algorithms

For some reference strings, FIFO causes **more** faults with **more** frames. The classic string `1 2 3 4 1 2 5 1 2 3 4 5` causes 9 faults with 3 frames but 10 with 4.

LRU and OPT never show this anomaly. They are **stack algorithms**: the set of pages in memory with $n$ frames is always a subset of the set with $n + 1$ frames. LRU with $n$ frames keeps the $n$ most recently used pages, which are among the $n + 1$ most recently used; so whatever is a hit with $n$ frames is also a hit with $n + 1$. FIFO's contents with different numbers of frames have no such relationship.

### Global and local replacement

- **Global replacement:** the victim may belong to any process. Total throughput is usually better, but one process's behaviour affects the others' fault rates.
- **Local replacement:** a process may evict only its own pages, within its own allocation of frames. Performance is more predictable per process, but memory may be used less efficiently.

Most general-purpose systems use global replacement, and often keep a pool of free frames ready, replenished in the background, so that a fault rarely has to wait for an eviction.

## Worked examples

### Example 1: Four algorithms on one reference string

```python
from collections import OrderedDict, deque

def fifo(refs, frames):
    memory, arrival, faults = set(), deque(), 0
    for page in refs:
        if page not in memory:
            faults += 1
            if len(memory) == frames:
                memory.discard(arrival.popleft())    # evict the oldest arrival
            memory.add(page)
            arrival.append(page)
    return faults

def lru(refs, frames):
    memory, faults = OrderedDict(), 0               # ordered from least to most recently used
    for page in refs:
        if page in memory:
            memory.move_to_end(page)
        else:
            faults += 1
            if len(memory) == frames:
                memory.popitem(last=False)          # evict the least recently used
            memory[page] = True
    return faults

def optimal(refs, frames):
    memory, faults = set(), 0
    for i, page in enumerate(refs):
        if page in memory:
            continue
        faults += 1
        if len(memory) == frames:
            future = refs[i + 1:]
            next_use = lambda p: future.index(p) if p in future else len(future)
            memory.remove(max(memory, key=next_use))   # used furthest in the future, or never
        memory.add(page)
    return faults

def clock(refs, frames):
    slots, referenced, hand, faults = [None] * frames, [0] * frames, 0, 0
    for page in refs:
        if page in slots:
            referenced[slots.index(page)] = 1        # hardware sets the referenced bit
            continue
        faults += 1
        while referenced[hand]:                      # second chance: clear and move on
            referenced[hand] = 0
            hand = (hand + 1) % frames
        slots[hand], referenced[hand] = page, 1
        hand = (hand + 1) % frames
    return faults

refs = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
for frames in (3, 4):
    print(f"{frames} frames: FIFO {fifo(refs, frames)}, OPT {optimal(refs, frames)}, "
          f"LRU {lru(refs, frames)}, clock {clock(refs, frames)}")
```

Output:

```text
3 frames: FIFO 15, OPT 9, LRU 12, clock 14
4 frames: FIFO 10, OPT 8, LRU 8, clock 9
```

With 3 frames, OPT's 9 faults are the minimum possible for this string; 6 of them are compulsory, because the string uses 6 distinct pages. LRU's 12 sits between OPT and FIFO's 15, and the clock approximation, with 14, does a little better than FIFO. Adding a fourth frame helps every algorithm, and LRU then matches OPT.

### Example 2: Tracing LRU by hand

The first ten references of the string above with 3 frames under LRU (F marks a fault):

| Reference | 7 | 0 | 1 | 2 | 0 | 3 | 0 | 4 | 2 | 3 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Frames after | 7 | 7 0 | 7 0 1 | 2 0 1 | 2 0 1 | 2 0 3 | 2 0 3 | 4 0 3 | 4 0 2 | 4 3 2 |
| Fault? | F | F | F | F | | F | | F | F | F |
| Evicted | | | | 7 | | 1 | | 2 | 3 | 0 |

When 2 arrives, page 7 is the least recently used and is evicted. When 3 arrives, the recency order (oldest first) is 1, 2, 0, so page 1 goes, not page 2, which was used more recently. When 4 arrives, the order is 2, 3, 0 (page 0 was just used), so LRU evicts page 2, which is needed at the very next reference. OPT, looking ahead, sees that page 2 is needed next, page 3 after that, and page 0 last, so it would evict page 0 and avoid the fault on 2. LRU can only judge the future by the past, and here the past misleads it.

### Example 3: Belady's anomaly

```python
from collections import deque, OrderedDict

def fifo(refs, frames):
    memory, arrival, faults = set(), deque(), 0
    for page in refs:
        if page not in memory:
            faults += 1
            if len(memory) == frames:
                memory.discard(arrival.popleft())
            memory.add(page)
            arrival.append(page)
    return faults

def lru(refs, frames):
    memory, faults = OrderedDict(), 0
    for page in refs:
        if page in memory:
            memory.move_to_end(page)
        else:
            faults += 1
            if len(memory) == frames:
                memory.popitem(last=False)
            memory[page] = True
    return faults

refs = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
print("FIFO:", {frames: fifo(refs, frames) for frames in range(1, 6)})
print("LRU: ", {frames: lru(refs, frames) for frames in range(1, 6)})
```

Output:

```text
FIFO: {1: 12, 2: 12, 3: 9, 4: 10, 5: 5}
LRU:  {1: 12, 2: 12, 3: 10, 4: 8, 5: 5}
```

FIFO faults 9 times with 3 frames but 10 times with 4: more memory, worse performance. LRU's fault count never increases as frames are added, as the stack property guarantees. With 5 frames, all five distinct pages fit, and only the 5 compulsory faults remain.

## Applications

- **Operating systems** use clock-style approximations of LRU: Linux maintains active and inactive page lists with referenced-bit scanning, and Windows trims working sets using similar aging information.
- **Database buffer pools** choose which disk pages to keep in memory with LRU variants, often resistant to large sequential scans that would otherwise flush useful pages.
- **CPU caches** use LRU or cheap approximations, such as pseudo-LRU, to choose which cache line to replace within a set.
- **Web and content-delivery caches** evict objects with LRU-like policies; `functools.lru_cache` in Python applies LRU to function results.
- **Benchmarking:** OPT, computed offline from a recorded trace, tells designers how close a practical policy comes to the best possible.

## Common mistakes

- **Counting hits as faults** or forgetting the compulsory faults at the start of a simulation.
- **Evicting by arrival time under LRU.** LRU looks at the last use, not the first load; a page loaded early but used recently must stay.
- **Breaking OPT ties carelessly:** a page that is never used again should be evicted before any page that will be used.
- **Assuming more frames always means fewer faults.** It does for stack algorithms, but not for FIFO.
- **Ignoring the cost difference between clean and dirty victims.** Evicting a dirty page costs an extra disk write.

## Revision notes

- FIFO evicts the oldest page; simple, but can evict heavily used pages and shows Belady's anomaly.
- OPT evicts the page used furthest in the future; optimal, unimplementable, the benchmark.
- LRU evicts the least recently used page; close to OPT thanks to locality; exact LRU is too costly without hardware support.
- Clock (second chance): circular scan; referenced bit 1 → clear and skip; 0 → evict. Enhanced clock prefers clean pages.
- Classic string `7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1` with 3 frames: FIFO 15, OPT 9, LRU 12.
- Belady's string `1 2 3 4 1 2 5 1 2 3 4 5`: FIFO 9 faults with 3 frames, 10 with 4. LRU and OPT are stack algorithms and immune.

## Practice questions

:::question basic
Why can the optimal page-replacement algorithm not be used in a real operating system, and what is it used for?
:::answer
It must know which page will be referenced furthest in the future, and an operating system cannot know a program's future references. It is used as a benchmark: running it on a recorded reference string gives the minimum possible number of faults, against which practical algorithms are compared.
:::

:::question basic
Under FIFO with 3 frames, how many page faults does the string `1 2 3 1 4 1` cause?
:::answer
1, 2, 3 are compulsory faults (3 faults). The second reference to 1 is a hit. 4 faults and evicts the oldest page, 1 (4 faults so far). The last reference to 1 then faults again, evicting 2 (5 faults). FIFO evicted page 1 because it arrived first, even though it had just been used, which LRU would not do.
:::

:::question intermediate
Run LRU with 3 frames on `1 2 3 1 4 1 5 2` and count the faults.
:::answer
1, 2, 3: three faults; frames {1, 2, 3}. 1: hit; recency order now 2, 3, 1. 4: fault, evict 2 (least recent); frames {3, 1, 4}. 1: hit; order 3, 4, 1. 5: fault, evict 3; frames {4, 1, 5}. 2: fault, evict 4; frames {1, 5, 2}. Total: 6 faults.
:::

:::question intermediate
Explain how the clock algorithm approximates LRU, and when it degenerates into FIFO.
:::answer
Each frame has a referenced bit that hardware sets on access. When choosing a victim, the hand skips pages whose bit is set, clearing it, and evicts the first page whose bit is clear. A page survives only if it has been used since the hand last passed it, so recently used pages are kept and pages unused for a full revolution are evicted, an approximation of "least recently used". If every page's bit is set, the hand clears them all in one revolution and evicts the page it started at, which is the oldest in clock order, so the algorithm behaves like FIFO.
:::

:::question intermediate
Why does exact LRU need hardware support, and what support would it need?
:::answer
LRU's ordering changes on every memory reference, not just on page faults, and software cannot run on every memory access without making the machine unusably slow. Exact LRU would need hardware that, on every access, writes a timestamp or counter value into the page's entry (and the OS would then search for the oldest at fault time), or that maintains a recency stack. Because this is expensive, most hardware provides only a referenced bit, and systems approximate LRU with it.
:::

:::question advanced
Prove that LRU cannot suffer from Belady's anomaly.
:::answer
Let $M_n(t)$ be the set of pages in memory after reference $t$ with $n$ frames. Under LRU, $M_n(t)$ is exactly the set of the $n$ most recently referenced distinct pages (or all pages referenced so far, if fewer). The $n$ most recently used pages are always among the $n + 1$ most recently used, so $M_n(t) \subseteq M_{n+1}(t)$ for every $t$. Now suppose reference $t + 1$ is a hit with $n$ frames: the page is in $M_n(t)$, hence in $M_{n+1}(t)$, so it is also a hit with $n + 1$ frames. Every hit with $n$ frames is a hit with $n + 1$ frames, so the number of faults with $n + 1$ frames is never larger.
:::

## Further learning

- **Next:** *File System Structure & Inodes* turns from memory to persistent storage.
- **Related:** *Demand Paging & Page Fault Handling* explains the faults these algorithms try to minimise.
- **Related:** *Hash Functions & Collision Handling* and *Singly & Doubly Linked Lists* (Data Structures & Algorithms) describe the structures behind an O(1) LRU cache.
