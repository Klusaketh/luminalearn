---
lesson: python-lists-dicts-comprehensions
title: Lists, Dictionaries & Comprehensions
summary: How Python lists and dictionaries store data, how slicing and dictionary lookups work, and how comprehensions build new collections in one readable expression.
minutes: 50
type: theory
objectives:
  - Index, slice, and modify lists, and predict the cost of common list operations
  - Create, read, update, and iterate over dictionaries, and explain why lookups are fast on average
  - Write list, dictionary, and set comprehensions with conditions, and know when a loop is clearer
review: ai-draft
---
## Introduction

Almost every program keeps a collection of values: the marks of a class, the words in a document, the settings of an application. Python's two workhorse collections are the **list**, an ordered sequence you access by position, and the **dictionary** (`dict`), which maps keys to values so you can look things up by name. This lesson explains how both behave, what their operations cost, and how **comprehensions** let you build one collection from another in a single line.

**Before you start:** you should know variables, the basic types (`int`, `float`, `str`, `bool`), `for` loops, and `if` statements.

## Core theory

### Lists: ordered and mutable

A list is written with square brackets: `marks = [72, 85, 91]`. It keeps items in order, allows duplicates, can mix types, and is **mutable**: you can change it after creating it.

- **Indexing:** `marks[0]` is the first item and `marks[-1]` the last. An index outside the list raises `IndexError`.
- **Slicing:** `marks[start:stop:step]` returns a **new** list from `start` up to but not including `stop`. Omitted bounds default to the ends, so `marks[:]` copies the list and `marks[::-1]` reverses it.
- **Changing:** `append(x)` adds at the end, `insert(i, x)` adds at position `i`, `pop()` removes and returns the last item, `remove(x)` deletes the first occurrence of `x`, and `marks[1] = 88` replaces an item.

A list is stored as a dynamic array of references. That explains the costs:

| Operation | Average cost |
| :--- | :--- |
| `a[i]`, `a[i] = x`, `len(a)` | $O(1)$ |
| `a.append(x)`, `a.pop()` | $O(1)$ amortized |
| `a.insert(0, x)`, `a.pop(0)` | $O(n)$, items shift |
| `x in a`, `a.remove(x)` | $O(n)$, linear search |
| `a[i:j]` | $O(j - i)$, copies items |

### Dictionaries: keys to values

A dictionary maps **keys** to **values**: `ages = {"asha": 20, "ravi": 22}`. You read with `ages["asha"]`, add or update with `ages["meena"] = 21`, and delete with `del ages["ravi"]`. Reading a missing key raises `KeyError`; `ages.get("zoe")` returns `None` instead, and `ages.get("zoe", 0)` returns a default.

A dict is a **hash table**. Python computes `hash(key)` to find where the value lives, so lookup, insertion, and deletion take $O(1)$ time on average, whatever the size of the dictionary. This is why keys must be **hashable**: immutable values such as numbers, strings, and tuples of immutables. A list cannot be a key.

Since Python 3.7, dictionaries remember **insertion order**. Iterating gives the keys; use `.values()` for values and `.items()` for `(key, value)` pairs.

### Comprehensions

A **list comprehension** builds a list from an iterable:

$$\texttt{[expression for item in iterable if condition]}$$

`[x * x for x in range(5)]` gives `[0, 1, 4, 9, 16]`, and `[w for w in words if len(w) > 3]` keeps the long words. The same shape builds dictionaries, `{k: v for ...}`, and sets, `{x for ...}`. A comprehension is equivalent to a loop that appends, but it states the intent, "build this collection", in one place. Use a plain loop when the body needs several statements or has side effects such as printing.

### Copies and shared references

Assignment never copies. After `b = a`, both names refer to the **same** list, so `b.append(4)` also changes `a`. Use `a.copy()`, `list(a)`, or `a[:]` for a **shallow copy**: a new outer list whose items are the same objects. For lists of lists, `copy.deepcopy` copies the inner lists too.

## Worked examples

### Example 1: Slicing and modifying a list

```python
scores = [55, 70, 85, 90, 40]
print(scores[1:4])
print(scores[::-1])
scores.append(65)
scores.remove(40)
print(scores, len(scores))
top = sorted(scores, reverse=True)[:3]
print(top)
```

Output:

```text
[70, 85, 90]
[40, 90, 85, 70, 55]
[55, 70, 85, 90, 65] 5
[90, 85, 70]
```

The slice `[1:4]` takes indices 1, 2, and 3. `sorted` returns a new list, so `scores` itself keeps its order.

### Example 2: Counting words with a dictionary, then a comprehension

```python
text = "the cat and the hat and the bat"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)

frequent = {w: c for w, c in counts.items() if c > 1}
print(frequent)
lengths = [len(w) for w in counts]
print(lengths)
```

Output:

```text
{'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
{'the': 3, 'and': 2}
[3, 3, 3, 3, 3]
```

`counts.get(word, 0)` returns 0 the first time a word is seen, which avoids a `KeyError`. The dictionary keeps the order in which words first appeared.

## Applications

- **Tabular data:** a list of dictionaries, one per row, is the shape of most JSON returned by web APIs.
- **Counting and grouping:** dictionaries count votes, words, or errors by category in one pass.
- **Caching:** a dictionary from inputs to results (memoization) avoids repeating expensive work.
- **Data cleaning:** comprehensions filter and transform records, for example removing blank lines from a file.

## Common mistakes

- **Expecting assignment to copy.** `b = a` shares one list. Copy explicitly when you need an independent list.
- **Removing items while looping over the same list.** Items shift and some are skipped. Build a new list with a comprehension instead.
- **Reading a missing key with `d[key]`.** Use `in`, `.get()`, or `collections.defaultdict` when a key may be absent.
- **Using a list as a dictionary key.** Lists are unhashable; convert to a tuple first.
- **Writing very long comprehensions.** Nested conditions and loops in one line hurt readability; a loop is fine.

## Revision notes

- Lists: ordered, mutable, indexed from 0, negative indices count from the end.
- Slices `a[i:j:k]` return new lists and exclude `j`.
- `append` and `pop()` are amortized $O(1)$; inserting or deleting at the front is $O(n)$.
- Dicts are hash tables: average $O(1)$ lookup, keys must be hashable, insertion order is kept.
- `d.get(k, default)` avoids `KeyError`.
- Comprehension pattern: `[expr for x in items if cond]`, also `{k: v ...}` and `{x ...}`.

## Practice questions

:::question basic
What does `[10, 20, 30, 40, 50][1:4]` evaluate to, and why is `50` not included?
:::answer
It evaluates to `[20, 30, 40]`. A slice starts at index 1 and stops **before** index 4, so it includes indices 1, 2, and 3; index 4 (the value 50) is the excluded stop position.
:::

:::question basic
How do you read a dictionary value so that a missing key returns 0 instead of raising an error?
:::answer
Use `d.get(key, 0)`. The `get` method returns the second argument when the key is absent, whereas `d[key]` raises `KeyError`.
:::

:::question intermediate
Rewrite this loop as a list comprehension: `result = []` then `for n in nums: if n % 2 == 0: result.append(n * n)`.
:::answer
`result = [n * n for n in nums if n % 2 == 0]`. The expression comes first, then the loop, then the filter; it builds the same list of squares of even numbers.
:::

:::question intermediate
After `a = [1, 2]`, `b = a`, `b.append(3)`, what is `a`? How would you make `b` independent?
:::answer
`a` is `[1, 2, 3]` because `a` and `b` name the same list object. Write `b = a.copy()` (or `list(a)` or `a[:]`) to create a separate list, after which appending to `b` leaves `a` unchanged.
:::

:::question advanced
Why is checking `x in my_list` slow for a large list but `x in my_dict` fast? What does that suggest for a program that tests membership many times?
:::answer
A list has no index by value, so `in` compares `x` with each item until it finds a match: $O(n)$ per check. A dict hashes `x` and jumps straight to the right slot: $O(1)$ on average. A program that tests membership repeatedly should convert the list to a set or dict once ($O(n)$) and then enjoy fast lookups, turning $O(nm)$ work into $O(n + m)$.
:::

## Further learning

- **Next:** *Tuples, Sets & Choosing a Collection* covers immutable sequences, set algebra, and how to pick the right container for a job.
- **Related:** *Hash Functions & Collision Handling* in Data Structures & Algorithms explains how dictionaries achieve constant-time lookups.
