---
lesson: python-standard-library
title: Standard Library Essentials
summary: A practical tour of the standard-library modules used in everyday programs: collections, itertools, math, datetime, pathlib, json, and random.
minutes: 45
type: theory
objectives:
  - Use Counter, defaultdict, deque, and namedtuple from collections to simplify common tasks
  - Combine iterables with itertools and do exact calculations with math and datetime
  - Work with file paths through pathlib and choose the right standard module for a task
review: ai-draft
---
## Introduction

Python is said to come with "batteries included": its **standard library** ships with every installation and covers counting, combinatorics, dates, paths, data formats, and much more. Knowing these modules saves you from rewriting tested code and makes your programs shorter and faster. This lesson covers the modules that appear in nearly every real project.

**Before you start:** you should know lists, dictionaries, tuples, loops, and how `import` works.

## Core theory

### collections

- **`Counter`** counts hashable items: `Counter("banana")` gives counts per letter, and `most_common(k)` returns the `k` most frequent items.
- **`defaultdict(factory)`** creates a missing key's value on first access, so `groups[key].append(x)` works without checking `if key in groups`.
- **`deque`** is a double-ended queue with $O(1)$ `append`, `appendleft`, `pop`, and `popleft`; a list's `pop(0)` is $O(n)$. `deque(maxlen=k)` keeps only the last `k` items.
- **`namedtuple`** creates lightweight immutable records with named fields: `Point = namedtuple("Point", "x y")`.

### itertools

`itertools` builds efficient iterators:

- `chain(a, b)` iterates over several iterables in sequence.
- `product(a, b)` gives every pair, like nested loops; `permutations(s, r)` and `combinations(s, r)` give ordered and unordered selections.
- `accumulate(nums)` gives running totals; `groupby(items, key)` groups **consecutive** equal keys, so sort first.
- `islice(it, n)` takes the first `n` items of any iterator, including infinite ones such as `count()`.

The number of `r`-combinations of `n` items is $\binom{n}{r} = \frac{n!}{r!(n-r)!}$; `math.comb(n, r)` computes it directly.

### math, statistics, and random

`math` provides `sqrt`, `floor`, `ceil`, `gcd`, `factorial`, `comb`, `isclose`, `pi`, and `inf`. `statistics` adds `mean`, `median`, and `stdev`. `random` generates pseudo-random numbers; `random.seed(n)` makes the sequence repeatable, which is useful for tests. For security tokens, use `secrets`, not `random`.

### datetime

`datetime.date(2026, 3, 1)` and `datetime.datetime(...)` represent dates and times; subtracting two gives a `timedelta`, and adding a `timedelta` moves a date. `strftime` formats a date as text and `strptime` parses text into a date. Store times in UTC with `datetime.timezone.utc` and convert to local time only for display.

### pathlib and json

`pathlib.Path` represents file paths as objects: `Path("data") / "scores.csv"` joins parts portably, `.suffix`, `.stem`, and `.name` split names, `.exists()` checks existence, and `.read_text()` / `.write_text()` handle small files. `json.dumps` and `json.loads` convert between Python objects and JSON text.

## Worked examples

### Example 1: Counting and grouping

```python
from collections import Counter, defaultdict, deque

votes = ["red", "blue", "red", "green", "blue", "red"]
tally = Counter(votes)
print(tally.most_common(2))

by_length = defaultdict(list)
for word in ["ant", "bee", "wasp", "moth", "fly"]:
    by_length[len(word)].append(word)
print(dict(by_length))

recent = deque(maxlen=3)
for page in ["home", "news", "sport", "weather"]:
    recent.append(page)
print(list(recent))
```

Output:

```text
[('red', 3), ('blue', 2)]
{3: ['ant', 'bee', 'fly'], 4: ['wasp', 'moth']}
['news', 'sport', 'weather']
```

`defaultdict(list)` creates an empty list the first time a length is seen. The bounded `deque` drops `"home"` when a fourth page arrives.

### Example 2: itertools, math, datetime, and pathlib together

```python
import itertools, math
from datetime import date, timedelta
from pathlib import Path

team = ["A", "B", "C", "D"]
pairs = list(itertools.combinations(team, 2))
print(len(pairs), math.comb(4, 2), pairs[:3])
print(list(itertools.accumulate([5, 3, 8, 2])))

start = date(2026, 1, 28)
due = start + timedelta(days=10)
print(due.isoformat(), (due - start).days, due.strftime("%d %b %Y"))

path = Path("reports") / "2026" / "summary.final.pdf"
print(path.name, path.stem, path.suffix, path.parent.name)
```

Output:

```text
6 6 [('A', 'B'), ('A', 'C'), ('A', 'D')]
[5, 8, 16, 18]
2026-02-07 10 07 Feb 2026
summary.final.pdf summary.final .pdf 2026
```

Four players form $\binom{4}{2} = 6$ pairs. Adding ten days to 28 January crosses into February correctly, which is exactly the kind of calendar arithmetic that is easy to get wrong by hand.

## Applications

- **Log analysis:** `Counter` finds the most common error codes in seconds.
- **Breadth-first search:** `deque` is the standard queue for BFS.
- **Scheduling:** `datetime` and `timedelta` compute due dates and durations.
- **Portable scripts:** `pathlib` works the same on Windows, macOS, and Linux.

## Common mistakes

- **Using a list as a queue.** `pop(0)` is $O(n)$; use `deque.popleft()`.
- **Calling `groupby` on unsorted data.** It groups only adjacent equal keys.
- **Building paths with string concatenation.** Separators differ between systems; use `pathlib`.
- **Using `random` for passwords or tokens.** It is predictable; use `secrets`.

## Revision notes

- `Counter`, `defaultdict`, `deque`, `namedtuple` live in `collections`.
- `itertools`: `chain`, `product`, `permutations`, `combinations`, `accumulate`, `groupby`, `islice`.
- `math.comb(n, r)` $= \binom{n}{r}$; `math.isclose` compares floats.
- `date` minus `date` is a `timedelta`; `strftime` formats, `strptime` parses.
- `Path("a") / "b"` joins paths; `.stem`, `.suffix`, `.name`, `.parent`.
- `random.seed` for repeatable runs; `secrets` for security.

## Practice questions

:::question basic
Which collection gives $O(1)$ removal from the front of a queue, and which method do you call?
:::answer
`collections.deque`, using `popleft()`. A deque is built for fast operations at both ends, unlike a list, whose `pop(0)` shifts every remaining item.
:::

:::question basic
What does `Counter("mississippi").most_common(1)` return?
:::answer
It returns `[('i', 4)]`. Both `i` and `s` appear four times; `most_common` lists ties in the order the items were first encountered, and `i` appears before `s`.
:::

:::question intermediate
How many items does `itertools.product([1, 2, 3], repeat=2)` yield, and how does that relate to nested loops?
:::answer
It yields $3^2 = 9$ pairs, from `(1, 1)` to `(3, 3)`. It is equivalent to two nested `for` loops over the same list, producing every ordered pair including repeats.
:::

:::question intermediate
Why should `itertools.groupby` usually be applied to sorted data?
:::answer
`groupby` starts a new group whenever the key changes between neighbouring items, so equal keys separated by other keys form separate groups. Sorting by the same key first puts all equal keys together, giving one group per key.
:::

:::question advanced
You need the number of days between two dates typed by users as "07/02/2026" (day/month/year). Write the core code and say why doing the arithmetic yourself is risky.
:::answer
`from datetime import datetime` then `a = datetime.strptime(s1, "%d/%m/%Y")`, `b = datetime.strptime(s2, "%d/%m/%Y")`, and `abs((b - a).days)`. Hand-written arithmetic must handle months of different lengths and leap years; `datetime` already does, and `strptime` also rejects impossible dates such as 31/02/2026.
:::

## Further learning

- **Next:** *Unit Testing & Debugging* shows how to verify code built from these tools.
- **Related:** *Algorithmic Patterns in Python* uses `Counter`, `defaultdict`, and `deque` to solve classic problems.
