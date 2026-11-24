---
lesson: cpp-stl-containers-iterators
title: STL Containers & Iterators
summary: The main STL containers (vector, deque, list, map, set, unordered_map, unordered_set, and the adaptors stack, queue, and priority_queue), their costs, and how iterators connect them to algorithms.
minutes: 50
type: theory
objectives:
  - Choose an appropriate STL container from the operations and complexity a task needs
  - Use map, set, unordered_map, and priority_queue for lookup, de-duplication, counting, and scheduling
  - Navigate containers with iterators, understand iterator categories, and avoid invalidation bugs
review: ai-draft
---
## Introduction

The **Standard Template Library** (STL) gives C++ a set of tested, efficient containers and algorithms. Knowing which container fits a problem is one of the most valuable C++ skills: the right choice turns an $O(n^2)$ program into an $O(n \log n)$ one with a single line changed. **Iterators** are the glue: every container exposes iterators, and every algorithm works on iterator ranges, so algorithms do not care which container they process.

**Before you start:** you should know templates, `std::vector`, and the basics of hashing and balanced search trees.

## Core theory

### Sequence containers

- **`std::vector`**: contiguous dynamic array; fast indexing and end insertion. The default choice.
- **`std::deque`**: double-ended queue; $O(1)$ insertion at both ends and indexing, not contiguous.
- **`std::list`**: doubly linked list; $O(1)$ insertion and removal anywhere given an iterator, but no indexing and poor cache behaviour.
- **`std::array<T, N>`**: fixed-size array with container interface.

### Associative containers

- **`std::map<K, V>`** and **`std::set<K>`** are usually red-black trees: keys are kept **sorted**, and lookup, insertion, and removal take $O(\log n)$. `map[key]` inserts a default value if the key is missing; `find` and `count` do not.
- **`std::unordered_map`** and **`std::unordered_set`** are hash tables: average $O(1)$ operations, worst case $O(n)$, and **no ordering** (iteration order is unspecified). Keys need a hash function and `==`.
- `multimap` and `multiset` allow duplicate keys.

### Container adaptors

`std::stack` (LIFO), `std::queue` (FIFO), and `std::priority_queue` wrap another container to offer a restricted interface. `priority_queue` is a binary heap whose `top()` is the **largest** element by default; `std::priority_queue<int, std::vector<int>, std::greater<int>>` makes it a min-heap. `push` and `pop` are $O(\log n)$.

### Choosing a container

| Need | Container |
| :--- | :--- |
| A list of items, indexed access | `vector` |
| Add/remove at both ends | `deque` |
| Sorted keys, range queries, ordered iteration | `map` / `set` |
| Fastest lookup, order irrelevant | `unordered_map` / `unordered_set` |
| Always take the largest or smallest next | `priority_queue` |

### Iterators

An iterator behaves like a pointer: `*it` reads the element, `++it` advances, and `begin()`/`end()` delimit a **half-open range** `[begin, end)`. Iterator **categories** determine which algorithms apply: `vector` and `deque` provide random-access iterators (support `it + 5`, needed by `std::sort`); `list`, `map`, and `set` provide bidirectional iterators; hash containers provide forward iterators. Containers differ in which operations **invalidate** iterators: vector reallocation invalidates all of them, while inserting into a `map` or `list` invalidates none, and erasing invalidates only iterators to the erased element. `erase` returns an iterator to the next element, which is the safe way to erase while looping.

## Worked examples

### Example 1: Counting with map and de-duplicating with set

```cpp
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>

int main() {
    std::string text = "the quick brown fox jumps over the lazy dog the end";
    std::istringstream in(text);
    std::map<std::string, int> freq;
    std::set<char> letters;
    std::string word;
    while (in >> word) {
        freq[word]++;
        for (char c : word) letters.insert(c);
    }
    std::cout << "distinct words: " << freq.size() << ", 'the' x" << freq["the"] << '\n';
    std::cout << "first three alphabetically: ";
    int shown = 0;
    for (const auto& [w, n] : freq) {
        if (shown++ == 3) break;
        std::cout << w << '=' << n << ' ';
    }
    std::cout << '\n';
    std::cout << "distinct letters: " << letters.size() << ", first " << *letters.begin() << ", last " << *letters.rbegin() << '\n';
    std::unordered_map<std::string, int> fast(freq.begin(), freq.end());
    std::cout << "contains fox? " << fast.count("fox") << ", contains cat? " << fast.count("cat") << '\n';
    return 0;
}
```

Output:

```text
distinct words: 9, 'the' x3
first three alphabetically: brown=1 dog=1 end=1
distinct letters: 26, first a, last z
contains fox? 1, contains cat? 0
```

The `map` keeps words sorted, so iterating gives alphabetical order. The `set` stores each letter once and keeps them sorted, so `begin()` and `rbegin()` give the smallest and largest; this sentence uses all 26 letters. The `unordered_map` answers membership questions in average constant time, but its iteration order would be unspecified, so it is used here only for lookup.

### Example 2: A priority queue scheduler and safe erasing

```cpp
#include <functional>
#include <iostream>
#include <queue>
#include <string>
#include <utility>
#include <vector>

int main() {
    using Task = std::pair<int, std::string>;
    std::priority_queue<Task> urgent;
    urgent.push({2, "reply to email"});
    urgent.push({5, "fix server outage"});
    urgent.push({1, "water plants"});
    urgent.push({3, "submit report"});
    while (!urgent.empty()) {
        std::cout << urgent.top().first << ": " << urgent.top().second << '\n';
        urgent.pop();
    }

    std::priority_queue<int, std::vector<int>, std::greater<int>> minheap;
    for (int x : {7, 3, 9, 1}) minheap.push(x);
    std::cout << "smallest: " << minheap.top() << '\n';

    std::vector<int> v = {1, 2, 3, 4, 5, 6};
    for (auto it = v.begin(); it != v.end(); ) {
        if (*it % 2 == 0) it = v.erase(it);
        else ++it;
    }
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
    return 0;
}
```

Output:

```text
5: fix server outage
3: submit report
2: reply to email
1: water plants
smallest: 1
1 3 5
```

Pairs compare by their first element, so the default max-heap returns the highest priority first. `std::greater<int>` turns the heap into a min-heap. In the erase loop, `erase` returns the iterator to the element after the one removed, so the loop never uses an invalidated iterator.

## Applications

- **Word counts and indexes:** `map` or `unordered_map` from word to count or positions.
- **Graph algorithms:** `priority_queue` drives Dijkstra and Prim; `unordered_set` tracks visited nodes.
- **Leaderboards and range queries:** ordered `map`/`set` support `lower_bound` and sorted iteration.
- **Simulations:** `queue` models first-come, first-served service.

## Common mistakes

- **Using `map[key]` to check existence.** It inserts the key; use `find` or `count`.
- **Expecting `unordered_map` iteration in a particular order.** Sort the keys if order matters.
- **Forgetting that `priority_queue` is a max-heap.** Use `std::greater` for smallest-first.
- **Erasing in a loop with `it++` after `erase`.** Use the iterator `erase` returns.
- **Using `std::list` for performance.** Its scattered nodes are usually slower than `vector` in practice.

## Revision notes

- `vector` default; `deque` for both ends; `list` for splicing with stable iterators.
- `map`/`set`: sorted, $O(\log n)$; `unordered_*`: hash, average $O(1)$, unordered.
- `stack`, `queue`, `priority_queue` (max-heap by default) are adaptors.
- Ranges are half-open `[begin, end)`; algorithms take iterator pairs.
- Iterator categories: random-access, bidirectional, forward.
- `it = c.erase(it)` erases safely during iteration.

## Practice questions

:::question basic
Which container keeps keys in sorted order with $O(\log n)$ lookup, and which gives average $O(1)$ lookup without order?
:::answer
`std::map` (or `std::set`) keeps keys sorted in a balanced tree with $O(\log n)$ operations. `std::unordered_map` (or `std::unordered_set`) is a hash table with average $O(1)$ operations but no ordering.
:::

:::question basic
What does `std::priority_queue<int>::top()` return?
:::answer
The largest element currently in the queue, because by default the priority queue is a max-heap using `std::less`. Supplying `std::greater<int>` as the comparator makes `top()` return the smallest element.
:::

:::question intermediate
Why is `if (counts[name] > 0)` a subtle bug when `counts` is a `std::map<std::string, int>`?
:::answer
`operator[]` inserts the key with a value-initialised count of 0 when it is missing, so the check silently adds every name it tests. The map grows and later iteration includes names that were never counted. Use `counts.find(name) != counts.end()` or `counts.count(name)`.
:::

:::question intermediate
Why does `std::sort(myList.begin(), myList.end())` not compile for a `std::list`?
:::answer
`std::sort` requires random-access iterators to jump to arbitrary positions, but `std::list` provides only bidirectional iterators. Use the member function `myList.sort()` instead, which is designed for linked lists.
:::

:::question advanced
You must process 10 million words and later print each distinct word with its count in alphabetical order. Compare using `std::map` throughout with counting in an `unordered_map` and sorting at the end.
:::answer
With `std::map`, each of the $10^7$ insert-or-increment operations costs $O(\log d)$ for $d$ distinct words, and the output is already sorted. With `unordered_map`, each operation costs $O(1)$ on average, and then the $d$ distinct entries are copied into a vector and sorted in $O(d \log d)$. Since $d$ is usually far smaller than $10^7$, counting with the hash table and sorting once is typically faster, especially because tree nodes cause more cache misses.
:::

## Further learning

- **Next:** *STL Algorithms & Lambda Expressions* applies algorithms to these containers.
- **Related:** *Balanced Search Trees* and *Hash Functions & Collision Handling* in Data Structures & Algorithms explain how `map` and `unordered_map` work inside.
