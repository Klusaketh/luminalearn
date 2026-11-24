---
lesson: java-collections-framework-core
title: Java Collections Framework Core
summary: The core interfaces and implementations of the Java Collections Framework (List, Set, Map, Queue), how HashMap buckets entries, the equals and hashCode contract, and choosing between ArrayList, LinkedList, HashSet, TreeSet, HashMap, and TreeMap.
minutes: 50
type: theory
objectives:
  - Choose collection interfaces and implementations based on ordering, uniqueness, and the cost of operations
  - Explain how HashMap stores entries in buckets and why equals and hashCode must be overridden together
  - Iterate and modify collections safely, avoiding ConcurrentModificationException
review: ai-draft
---
## Introduction

Almost every Java program stores groups of objects, and the **Java Collections Framework** provides a consistent set of interfaces and well-tested implementations for doing so. Choosing well matters: a `HashSet` answers "is this here?" in constant time where an `ArrayList` needs a linear scan, and a `TreeMap` keeps keys sorted for free. Correctness matters too: a class used as a `HashMap` key with an inconsistent `equals` and `hashCode` silently breaks lookups.

**Before you start:** you should know interfaces, generics at the level of `List<String>`, and wrapper classes.

## Core theory

### The interfaces

- **`List<E>`**: an ordered sequence with positions and duplicates allowed (`get(i)`, `add`, `remove`).
- **`Set<E>`**: no duplicates (`add` returns `false` for an existing element).
- **`Queue<E>` / `Deque<E>`**: process elements in an order (`offer`, `poll`, `peek`; deques work at both ends).
- **`Map<K, V>`**: key-value pairs with unique keys (`put`, `get`, `getOrDefault`, `merge`, `entrySet`). `Map` is part of the framework but does not extend `Collection`.

### Main implementations

| Implementation | Structure | Key costs | Order |
| :--- | :--- | :--- | :--- |
| `ArrayList` | dynamic array | `get` $O(1)$, add at end amortized $O(1)$, insert/remove in middle $O(n)$ | insertion |
| `LinkedList` | doubly linked list | add/remove at ends $O(1)$, `get(i)` $O(n)$ | insertion |
| `ArrayDeque` | circular array | add/remove at both ends $O(1)$ | insertion |
| `HashSet` / `HashMap` | hash table | average $O(1)$ | unspecified |
| `LinkedHashSet` / `LinkedHashMap` | hash table + linked list | average $O(1)$ | insertion |
| `TreeSet` / `TreeMap` | red-black tree | $O(\log n)$ | sorted |
| `PriorityQueue` | binary heap | `offer`/`poll` $O(\log n)$, `peek` $O(1)$ | smallest first |

In practice `ArrayList` beats `LinkedList` for almost everything, and `ArrayDeque` is the preferred stack and queue.

### How HashMap works

A `HashMap` keeps an array of **buckets**. To store a key, it computes `key.hashCode()`, mixes the bits, and uses the result modulo the table size to choose a bucket. Keys in the same bucket (a **collision**) are kept in a small linked list, or a balanced tree once a bucket grows large (since Java 8). Lookup hashes the key, goes to its bucket, and compares candidates with `equals`. When the number of entries exceeds **capacity × load factor** (0.75 by default), the table doubles and all entries are redistributed, keeping average operations $O(1)$.

### The equals and hashCode contract

To be used correctly in hash-based collections, a class must satisfy:

1. If `a.equals(b)`, then `a.hashCode() == b.hashCode()`.
2. `equals` is reflexive, symmetric, transitive, and consistent; `x.equals(null)` is `false`.
3. `hashCode` returns the same value as long as the fields used by `equals` do not change.

`Object`'s default `equals` compares identity and its `hashCode` is identity-based, so two logically equal objects look different to a `HashSet`. If you override `equals`, you **must** override `hashCode` consistently (for example with `Objects.hash(field1, field2)`), otherwise equal objects land in different buckets and lookups fail. Do not mutate fields used in `hashCode` while an object is a key in a map. Sorted collections instead use `compareTo` (from `Comparable`) or a `Comparator`.

### Iteration and modification

Use the enhanced for loop or an `Iterator`. Structurally modifying a collection (adding or removing elements) while iterating over it with a for-each loop throws `ConcurrentModificationException` (fail-fast iterators). Remove safely with `iterator.remove()` or `collection.removeIf(predicate)`. `List.of`, `Set.of`, and `Map.of` create **immutable** collections, whose modification methods throw `UnsupportedOperationException`.

## Worked examples

### Example 1: equals and hashCode in a HashSet

```java
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

public class Main {
    static class BrokenPoint {
        final int x, y;
        BrokenPoint(int x, int y) { this.x = x; this.y = y; }
        @Override public boolean equals(Object o) {
            if (!(o instanceof BrokenPoint)) return false;
            BrokenPoint p = (BrokenPoint) o;
            return x == p.x && y == p.y;
        }
    }

    static class Point {
        final int x, y;
        Point(int x, int y) { this.x = x; this.y = y; }
        @Override public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Point)) return false;
            Point p = (Point) o;
            return x == p.x && y == p.y;
        }
        @Override public int hashCode() { return Objects.hash(x, y); }
    }

    public static void main(String[] args) {
        Set<BrokenPoint> broken = new HashSet<>();
        broken.add(new BrokenPoint(1, 2));
        broken.add(new BrokenPoint(1, 2));
        System.out.println("broken size " + broken.size() + ", contains? " + broken.contains(new BrokenPoint(1, 2)));

        Set<Point> good = new HashSet<>();
        good.add(new Point(1, 2));
        good.add(new Point(1, 2));
        System.out.println("good size " + good.size() + ", contains? " + good.contains(new Point(1, 2)));
        System.out.println(new Point(1, 2).hashCode() == new Point(1, 2).hashCode());
    }
}
```

Output:

```text
broken size 2, contains? false
good size 1, contains? true
true
```

`BrokenPoint` overrides `equals` but not `hashCode`, so equal points get identity-based hash codes, almost certainly fall in different buckets, and the set treats them as different. `Point` keeps the contract, so duplicates are rejected and lookups succeed.

### Example 2: Choosing collections and modifying safely

```java
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.TreeMap;

public class Main {
    public static void main(String[] args) {
        String text = "to be or not to be that is the question";
        Map<String, Integer> firstSeen = new LinkedHashMap<>();
        Map<String, Integer> sorted = new TreeMap<>();
        for (String w : text.split(" ")) {
            firstSeen.merge(w, 1, Integer::sum);
            sorted.merge(w, 1, Integer::sum);
        }
        System.out.println(firstSeen);
        System.out.println(sorted);

        List<Integer> nums = new ArrayList<>(Arrays.asList(5, 12, 7, 20, 3, 8));
        try {
            for (Integer n : nums) if (n > 10) nums.remove(n);
        } catch (java.util.ConcurrentModificationException e) {
            System.out.println("for-each removal threw ConcurrentModificationException");
        }
        for (Iterator<Integer> it = nums.iterator(); it.hasNext(); ) if (it.next() > 10) it.remove();
        nums.removeIf(n -> n % 2 == 0);
        System.out.println(nums);

        Deque<String> stack = new ArrayDeque<>();
        stack.push("a"); stack.push("b"); stack.push("c");
        PriorityQueue<Integer> pq = new PriorityQueue<>(List.of(9, 4, 7, 1));
        System.out.println(stack.pop() + " " + pq.poll() + " " + pq.poll());
    }
}
```

Output:

```text
{to=2, be=2, or=1, not=1, that=1, is=1, the=1, question=1}
{be=2, is=1, not=1, or=1, question=1, that=1, the=1, to=2}
for-each removal threw ConcurrentModificationException
[5, 7, 3]
c 1 4
```

`LinkedHashMap` keeps first-insertion order and `TreeMap` sorts the keys; a plain `HashMap` would print in an unspecified order. Removing inside a for-each loop throws, while `Iterator.remove` and `removeIf` are safe. `ArrayDeque` works as a stack and `PriorityQueue` returns the smallest element first.

## Applications

- **Caches and indexes:** `HashMap` from IDs to objects.
- **De-duplication:** `HashSet` of emails or visited URLs.
- **Leaderboards and reports:** `TreeMap` for sorted keys and range queries.
- **Scheduling:** `PriorityQueue` of tasks by deadline; `ArrayDeque` for BFS queues.

## Common mistakes

- **Overriding `equals` without `hashCode`.** Hash-based collections then misbehave.
- **Mutating a key after inserting it.** It becomes unreachable in its old bucket.
- **Removing elements in a for-each loop.** Use `removeIf` or an iterator.
- **Using `LinkedList` for random access.** `get(i)` walks the list in $O(n)$.
- **Assuming `HashMap` iteration order.** Use `LinkedHashMap` or `TreeMap` when order matters.

## Revision notes

- `List` (ordered, duplicates), `Set` (unique), `Queue`/`Deque`, `Map` (unique keys).
- `ArrayList` default list; `ArrayDeque` default stack/queue; `HashMap`/`HashSet` average $O(1)$; `TreeMap`/`TreeSet` sorted $O(\log n)$.
- HashMap: hash → bucket → `equals`; resizes past load factor 0.75.
- Equal objects must have equal hash codes; override both together.
- Fail-fast iterators throw `ConcurrentModificationException`; use `iterator.remove` / `removeIf`.
- `List.of` and friends are immutable.

## Practice questions

:::question basic
Which collection would you use to store unique usernames with fast membership checks, and why?
:::answer
A `HashSet<String>`. Sets reject duplicates, and a hash set checks membership in average constant time; ordering is not needed for this task.
:::

:::question basic
What is the difference between `HashMap`, `LinkedHashMap`, and `TreeMap` when iterating?
:::answer
`HashMap` iterates in an unspecified order that can change as it grows. `LinkedHashMap` iterates in insertion order. `TreeMap` iterates in sorted key order.
:::

:::question intermediate
Why must a class that overrides `equals` also override `hashCode`?
:::answer
Hash-based collections first use `hashCode` to choose a bucket and only then compare with `equals`. If two equal objects had different hash codes, they would usually be placed in, and searched for in, different buckets, so a set could store both and `contains` could fail. The contract requires equal objects to have equal hash codes.
:::

:::question intermediate
How do you remove all negative numbers from an `ArrayList<Integer>` safely?
:::answer
Call `list.removeIf(n -> n < 0);`, or iterate with an explicit `Iterator` and call `it.remove()` for each negative element. Removing through the list inside a for-each loop modifies the list behind the iterator's back and throws `ConcurrentModificationException`.
:::

:::question advanced
A `Point` with mutable `x` and `y` is used as a `HashMap` key. After `point.x = 10;`, `map.get(point)` returns `null` even though the entry is still in the map. Explain.
:::answer
The entry was stored in the bucket chosen by the point's old hash code. Changing `x` changes `hashCode`, so `get` now searches a different bucket and does not find the entry, even though it is still in the map under the old bucket. Keys should be immutable, or at least never modified while they are in a hash-based collection.
:::

## Further learning

- **Next:** *Lambdas & the Streams API* processes collections declaratively.
- **Related:** *Hash Functions & Collision Handling* in Data Structures & Algorithms explains bucketing in depth.
