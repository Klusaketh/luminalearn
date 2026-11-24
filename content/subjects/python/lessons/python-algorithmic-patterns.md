---
lesson: python-algorithmic-patterns
title: Algorithmic Patterns in Python
summary: Idiomatic Python for common algorithmic tasks: sorting with key functions, counting with Counter, grouping with defaultdict, queues and sliding windows with deque, and heaps with heapq.
minutes: 40
type: theory
objectives:
  - Sort data by one or several criteria with key functions, and explain sort stability
  - Solve counting, grouping, and frequency problems with Counter and defaultdict
  - Use deque for breadth-first search and sliding windows, and heapq for top-k and priority problems
review: ai-draft
---
## Introduction

Many interview and contest problems reduce to a handful of patterns: sort by a rule, count things, group things, process items in arrival order, or always pick the smallest. Python has a concise, fast tool for each. Knowing these idioms lets you express an algorithm in a few clear lines and spend your effort on the idea rather than the plumbing. The coding practice section of LuminaLearn uses them constantly.

**Before you start:** you should know lists, dictionaries, tuples, lambda functions, and the standard-library collections covered earlier.

## Core theory

### Sorting with keys

`sorted(items, key=f)` returns a new sorted list; `items.sort(key=f)` sorts in place. The **key function** maps each item to the value to compare: `key=len` sorts by length, `key=str.lower` ignores case. To sort by several criteria, return a tuple: `key=lambda s: (-s.marks, s.name)` sorts by marks descending, then name ascending. Python's sort (Timsort) runs in $O(n \log n)$ and is **stable**: items with equal keys keep their original order, which lets you sort by a secondary key first and a primary key second.

### Counting and grouping

`Counter(items)` builds a frequency table in $O(n)$; two strings are anagrams exactly when `Counter(a) == Counter(b)`. `defaultdict(list)` groups items by a computed key, for example words by their sorted letters. Both replace error-prone "check if the key exists" code.

### Queues and windows with deque

Breadth-first search processes nodes in the order they were discovered, which is a **queue**: `append` to add, `popleft` to take the next, both $O(1)$. A deque also maintains a **sliding window**: add the new item on the right and drop items that fall out on the left. A **monotonic deque**, kept in decreasing order, gives the maximum of every window of size $k$ in $O(n)$ total.

### Heaps with heapq

`heapq` turns a list into a **binary min-heap**: `heappush` and `heappop` take $O(\log n)$ and `heap[0]` is always the smallest item. For a max-heap, push negated values. `heapq.nlargest(k, items)` and `nsmallest` solve top-$k$ problems in $O(n \log k)$. Heaps of tuples such as `(distance, node)` drive Dijkstra's shortest-path algorithm.

### Other idioms

`enumerate` gives indices with values, `zip` walks several lists together, `any` and `all` short-circuit tests, `bisect` searches a sorted list in $O(\log n)$, and a dictionary of "value to index" turns many $O(n^2)$ pair searches into $O(n)$.

## Worked examples

### Example 1: Multi-key sorting and grouping anagrams

```python
from collections import defaultdict

students = [("Ravi", 78), ("Asha", 91), ("John", 78), ("Meena", 85)]
ranked = sorted(students, key=lambda s: (-s[1], s[0]))
print(ranked)

words = ["listen", "google", "silent", "enlist", "gogole", "cat"]
groups = defaultdict(list)
for w in words:
    groups["".join(sorted(w))].append(w)
print([g for g in groups.values() if len(g) > 1])
```

Output:

```text
[('Asha', 91), ('Meena', 85), ('John', 78), ('Ravi', 78)]
[['listen', 'silent', 'enlist'], ['google', 'gogole']]
```

Negating the mark sorts it in descending order while names still sort ascending, so the tie at 78 is broken alphabetically. Anagrams share the same sorted letters, which makes a perfect grouping key.

### Example 2: Breadth-first search and top-k with heapq

```python
from collections import deque
import heapq

graph = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}

def bfs_levels(start):
    level = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph[node]:
            if nxt not in level:
                level[nxt] = level[node] + 1
                queue.append(nxt)
    return level

print(bfs_levels("A"))

scores = [42, 17, 93, 58, 71, 93, 8]
print(heapq.nlargest(3, scores))
heap = []
for s in scores:
    heapq.heappush(heap, s)
    if len(heap) > 3:
        heapq.heappop(heap)
print(sorted(heap, reverse=True))
```

Output:

```text
{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 3}
[93, 93, 71]
[93, 93, 71]
```

BFS records each node the first time it is reached, which is its shortest distance in edges. The size-3 heap keeps only the three largest scores, using $O(k)$ memory however long the input is.

## Applications

- **Leaderboards:** multi-key sorts rank players by score, then by time.
- **Search engines and recommendations:** heaps keep the top-$k$ results.
- **Networking and maps:** BFS finds the fewest hops; heaps power Dijkstra's algorithm.
- **Text analysis:** `Counter` and grouping detect duplicates, anagrams, and frequent words.

## Common mistakes

- **Sorting by one key, then another, in the wrong order.** With stable sorts, sort by the secondary key first.
- **Using `list.pop(0)` for BFS.** It makes the search $O(n^2)$; use `deque.popleft()`.
- **Expecting `heapq` to be a max-heap.** It is a min-heap; negate values for maximum-first order.
- **Marking BFS nodes as visited when popped instead of when pushed.** The same node can then enter the queue many times.

## Revision notes

- `sorted(items, key=lambda x: (k1, -k2))` sorts by several criteria; Python's sort is stable.
- `Counter` for frequencies; `defaultdict(list)` for grouping.
- `deque` for queues, BFS, and sliding windows.
- `heapq` is a min-heap: push/pop $O(\log n)$, `nlargest(k, xs)` is $O(n \log k)$.
- Value-to-index dictionaries remove inner loops.
- `bisect` searches sorted lists in $O(\log n)$.

## Practice questions

:::question basic
How do you sort a list of words by length, shortest first, with ties in alphabetical order?
:::answer
`sorted(words, key=lambda w: (len(w), w))`. Tuples compare element by element, so length decides first and the word itself breaks ties.
:::

:::question basic
Which data structure should hold the frontier in a breadth-first search, and why?
:::answer
A `collections.deque` used as a queue. BFS must process nodes in the order they were discovered, and a deque appends on the right and removes from the left in $O(1)$ time.
:::

:::question intermediate
How can you check whether two strings are anagrams in $O(n)$ time?
:::answer
Compare their letter counts: `Counter(a) == Counter(b)`. Building each counter is linear in the string length, and comparing two counters is linear in the number of distinct letters, avoiding the $O(n \log n)$ cost of sorting.
:::

:::question intermediate
Why does keeping a min-heap of size $k$ find the $k$ largest values, and what does it cost?
:::answer
The heap always holds the $k$ largest values seen so far, and its root is the smallest of them; any new value larger than the root replaces it. Each of the $n$ values costs at most $O(\log k)$ heap work, so the total is $O(n \log k)$ time and $O(k)$ memory.
:::

:::question advanced
Python's sort is stable. Explain how to sort employees by department (ascending) and, within a department, by salary (descending) using two sorts, and why the order of the sorts matters.
:::answer
First sort by the secondary key, salary descending: `staff.sort(key=lambda e: e.salary, reverse=True)`. Then sort by the primary key, department: `staff.sort(key=lambda e: e.department)`. The second sort reorders by department, and because it is stable, employees within the same department keep the salary order produced by the first sort. Doing them in the opposite order would leave the list ordered by salary only.
:::

## Further learning

- **Next:** *Breadth-First Search & Depth-First Search* in Data Structures & Algorithms develops the BFS idea used here.
- **Related:** *Min & Max Heap Implementation* explains how `heapq` keeps the smallest item at the root.
