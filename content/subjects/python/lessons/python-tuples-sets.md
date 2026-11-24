---
lesson: python-tuples-sets
title: Tuples, Sets & Choosing a Collection
summary: Tuples as fixed, immutable records, sets as collections of unique items with fast membership tests, and a practical guide to choosing between list, tuple, set, and dict.
minutes: 40
type: theory
objectives:
  - Create and unpack tuples, and explain what immutability does and does not guarantee
  - Use sets for de-duplication, membership tests, and union, intersection, and difference
  - Choose the right built-in collection for a task by reasoning about order, mutability, uniqueness, and lookup cost
review: ai-draft
---
## Introduction

Lists and dictionaries are the most common Python collections, but two others solve problems they handle badly. A **tuple** is a fixed group of values, such as a coordinate `(x, y)` or a database row, that should not change. A **set** is a bag of unique values with very fast membership tests, ideal for questions like "have I seen this before?" This lesson covers both and ends with a decision guide for choosing a collection.

**Before you start:** you should be comfortable with lists, dictionaries, and the idea that dictionary keys must be hashable.

## Core theory

### Tuples

A tuple is written with commas, usually inside parentheses: `point = (3, 4)`. A one-item tuple needs a trailing comma, `(5,)`, because `(5)` is just the number 5. Tuples support indexing, slicing, `len`, `in`, iteration, `count`, and `index`, like lists, but they are **immutable**: you cannot assign to an item, append, or remove.

**Unpacking** assigns the items to several names at once: `x, y = point`. A starred name collects the rest: `first, *rest = (1, 2, 3)` gives `first = 1` and `rest = [2, 3]`. Swapping two variables, `a, b = b, a`, is tuple packing and unpacking.

Immutability is **shallow**. A tuple's slots always refer to the same objects, but if one of those objects is mutable, such as a list, the list itself can still change. A tuple is **hashable** only when all its items are hashable, so `(1, "a")` can be a dictionary key or set member but `(1, [2])` cannot.

Functions often return tuples to return several values: `return total, count` returns one tuple, which the caller unpacks.

### Sets

A set holds **unique**, hashable items with no order: `tags = {"python", "loops"}`. The empty set is `set()`, because `{}` is an empty dictionary. `set(iterable)` removes duplicates in one step.

Sets are hash tables without values, so `x in s`, `s.add(x)`, and `s.discard(x)` take $O(1)$ time on average. Set algebra follows mathematics:

| Operation | Operator | Meaning |
| :--- | :--- | :--- |
| Union | `a \| b` | items in either set |
| Intersection | `a & b` | items in both |
| Difference | `a - b` | items in `a` but not in `b` |
| Symmetric difference | `a ^ b` | items in exactly one set |
| Subset | `a <= b` | every item of `a` is in `b` |

Because a set has no order, never rely on the order in which a set prints; use `sorted(s)` when order matters. A **frozenset** is an immutable, hashable set that can itself be a set member or dictionary key.

### Choosing a collection

Ask four questions: Does order matter? Will the contents change? Must items be unique? How will I look things up?

| Need | Choose |
| :--- | :--- |
| Ordered items that change, accessed by position | `list` |
| A fixed record, a dictionary key, or several return values | `tuple` |
| Uniqueness or fast "is it there?" tests | `set` |
| Look up values by a key | `dict` |

## Worked examples

### Example 1: Tuples as records

```python
students = [("Asha", 91), ("Ravi", 78), ("Meena", 85)]
for name, mark in students:
    print(f"{name}: {mark}")

best = max(students, key=lambda s: s[1])
print(best)
name, mark = best
print(name.upper(), mark)
```

Output:

```text
Asha: 91
Ravi: 78
Meena: 85
('Asha', 91)
ASHA 91
```

Each record is a tuple, and the `for` loop unpacks it. `max` with `key=lambda s: s[1]` compares by the mark.

### Example 2: Set algebra on course enrolments

```python
python = {"asha", "ravi", "meena", "john"}
dsa = {"ravi", "john", "sara"}
print(sorted(python & dsa))
print(sorted(python | dsa))
print(sorted(python - dsa))
print(sorted(python ^ dsa))
print(len(set([3, 1, 3, 2, 1])))
```

Output:

```text
['john', 'ravi']
['asha', 'john', 'meena', 'ravi', 'sara']
['asha', 'meena']
['asha', 'meena', 'sara']
3
```

Wrapping each result in `sorted` makes the output predictable; printing a set of strings directly can show a different order in each run.

## Applications

- **Removing duplicates:** `set(emails)` keeps one copy of each address.
- **Graph search:** a `visited` set records explored nodes with $O(1)$ checks.
- **Composite keys:** a tuple such as `(row, col)` indexes a grid stored in a dictionary.
- **Comparing groups:** intersections find common friends, shared tags, or students in two courses.

## Common mistakes

- **Writing `(5)` for a one-item tuple.** It is the integer 5; write `(5,)`.
- **Creating an empty set with `{}`.** That is an empty dictionary; use `set()`.
- **Assuming a set keeps insertion order.** It does not; sort it when order matters.
- **Believing a tuple's contents can never change.** A list inside a tuple can still be modified.

## Revision notes

- Tuples: immutable, ordered, support unpacking `a, b = t` and `first, *rest = t`.
- A tuple is hashable only if every item is hashable.
- Sets: unique, unordered, hashable items; average $O(1)$ membership.
- `|`, `&`, `-`, `^` are union, intersection, difference, symmetric difference.
- `set()` is the empty set; `frozenset` is an immutable set.
- Choose by order, mutability, uniqueness, and lookup style.

## Practice questions

:::question basic
What is the type of `(7)` and of `(7,)`?
:::answer
`(7)` is an `int`, because parentheses alone only group an expression. `(7,)` is a `tuple` with one item; the trailing comma is what makes a tuple.
:::

:::question basic
How can you count the distinct values in the list `[4, 4, 1, 9, 1]`?
:::answer
Use `len(set([4, 4, 1, 9, 1]))`, which is 3. Converting to a set removes duplicates, leaving `{1, 4, 9}`.
:::

:::question intermediate
Given `a = {1, 2, 3, 4}` and `b = {3, 4, 5}`, what are `a & b`, `a - b`, and `a ^ b`?
:::answer
`a & b` is `{3, 4}` (in both), `a - b` is `{1, 2}` (in `a` only), and `a ^ b` is `{1, 2, 5}` (in exactly one of the sets).
:::

:::question intermediate
Can `t = (1, [2, 3])` be used as a dictionary key? Can `t[1].append(4)` succeed?
:::answer
It cannot be a key: hashing a tuple hashes its items, and the list item is unhashable, so Python raises `TypeError`. `t[1].append(4)` does succeed, because the tuple still refers to the same list; only the list's contents change. Tuple immutability is shallow.
:::

:::question advanced
You must check 100,000 incoming user IDs against a list of 50,000 banned IDs. Which collection should hold the banned IDs, and roughly how much work does each choice take?
:::answer
Store the banned IDs in a set. With a list, each check scans up to 50,000 items, about $10^5 \times 5 \times 10^4 = 5 \times 10^9$ comparisons in the worst case. Building a set costs about $5 \times 10^4$ operations once, and each check is then $O(1)$ on average, about $10^5$ more operations in total.
:::

## Further learning

- **Next:** *String Formatting & Methods* shows how to present the data you store in these collections.
- **Related:** *Hash Functions & Collision Handling* explains why sets and dictionaries need hashable items.
