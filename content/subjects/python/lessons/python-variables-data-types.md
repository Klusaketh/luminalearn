---
lesson: python-memory-model-dynamic-typing
title: Python Variables & Data Types
summary: Learn what a Python variable really is, how the built-in types behave, and why mutability decides whether a change is shared.
minutes: 35
type: theory
objectives:
  - Explain that a Python variable is a name bound to an object, and that the object, not the name, carries the type
  - Describe the behaviour of int, float, bool, str and None, including integer precision and floating-point rounding
  - Distinguish mutable from immutable types and predict when two names share a change
  - Choose correctly between == and is, and between copying and aliasing a list
---

## Introduction

In many languages a variable is a box: you put a value in it, and the box has a fixed type. Python works differently. A Python variable is a **name** that refers to an **object** stored elsewhere in memory. Assignment does not copy anything; it attaches a name to an object. Two names can refer to the same object, and one name can refer to an integer now and a string later.

This model explains most of the surprises beginners meet: a list that changes "by itself" after a function call, `0.1 + 0.2` printing `0.30000000000000004`, or `is` and `==` giving different answers. Once you can picture names and objects, those behaviours become predictable rather than mysterious.

**Before you start:** you should be able to run a Python 3 script and use `print()`.

## Core theory

### Names, objects and assignment

Every value in Python is an object with three properties:

| Property | Meaning | How to see it |
| :--- | :--- | :--- |
| Identity | Which object it is; never changes during the object's lifetime | `id(x)`, compared with `is` |
| Type | What kind of object it is and which operations it supports | `type(x)` |
| Value | The data the object holds | `print(x)`, compared with `==` |

The statement `x = 42` creates (or reuses) an integer object with value 42 and binds the name `x` to it. The statement `y = x` does **not** copy the object. It binds a second name to the same object, so `x is y` is `True`.

### Dynamic and strong typing

Python is **dynamically typed**: types belong to objects, not to names, and are checked while the program runs. The same name can be rebound to objects of different types.

Python is also **strongly typed**: it does not silently convert between unrelated types. `"3" + 4` raises a `TypeError` instead of guessing whether you meant `"34"` or `7`. You convert explicitly with `int("3")` or `str(4)`.

`type(x)` returns the exact type of an object. `isinstance(x, int)` asks whether `x` is an `int` or a subclass of it, which is usually what you want when checking inputs.

### The core built-in types

| Type | Example | Key facts |
| :--- | :--- | :--- |
| `int` | `42`, `-7`, `10**100` | Arbitrary precision: integers never overflow, they just use more memory |
| `float` | `3.14`, `1e-9` | 64-bit IEEE 754 binary floating point; most decimal fractions are approximations |
| `bool` | `True`, `False` | A subclass of `int`: `True == 1` and `False == 0` |
| `str` | `"lumina"` | An immutable sequence of Unicode characters |
| `NoneType` | `None` | The single "no value" object; test for it with `is None` |

Floating point deserves special care. The decimal number 0.1 has no exact binary representation, so the stored value is very slightly off. Each operation rounds again, and the small errors can become visible when printed. Never compare floats with `==` after arithmetic; use `math.isclose()`, or use `decimal.Decimal` when exact decimal arithmetic matters, as with money.

### Mutable and immutable types

| Category | Types | What "changing" does |
| :--- | :--- | :--- |
| Immutable | `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `None` | Creates a new object; the original never changes |
| Mutable | `list`, `dict`, `set`, most user-defined classes | Modifies the object in place; every name bound to it sees the change |

`s += "learn"` on a string builds a new string and rebinds `s`. `lst.append(4)` on a list changes the existing list object. That difference is why aliasing only causes surprises with mutable objects.

### `==` versus `is`

`a == b` asks whether two objects have **equal values**. `a is b` asks whether they are **the same object**. Two separately built lists `[1, 2]` and `[1, 2]` are equal but not identical. Use `is` only for identity questions, above all `x is None`. Do not use `is` to compare numbers or strings: whether Python reuses an object for equal values is an implementation detail.

### Aliasing and copying

Because assignment never copies, `b = a` with a list makes `a` and `b` two names for one list. To get an independent list, copy it: `a.copy()`, `list(a)` or `a[:]`. These make a **shallow copy**: a new outer list whose items are the same objects as before. For a list of lists, the inner lists are still shared; `copy.deepcopy()` copies them too.

## Worked examples

### Example 1: Rebinding an int versus mutating a list

```python
count = 10
other = count
count += 1                 # ints are immutable: count is rebound to a new object
print(count, other)

scores = [70, 85]
backup = scores            # a second name for the same list
scores.append(90)          # lists are mutable: the shared object changes
print(scores, backup)
print(backup is scores)
```

Output:

```text
11 10
[70, 85, 90] [70, 85, 90]
True
```

`count += 1` cannot change the integer 10, so it builds 11 and rebinds `count`; `other` still refers to 10. `scores.append(90)` changes the one list that both names refer to, so `backup` shows the new score too.

### Example 2: Floating-point rounding and how to compare

```python
import math
from decimal import Decimal

total = 0.1 + 0.2
print(total)
print(total == 0.3)
print(math.isclose(total, 0.3))
print(Decimal("0.1") + Decimal("0.2"))
print(2 ** 100)
```

Output:

```text
0.30000000000000004
False
True
0.3
1267650600228229401496703205376
```

The float sum is not exactly 0.3, so `==` fails while `math.isclose()` succeeds. `Decimal` built from strings does exact decimal arithmetic. The last line shows that integers grow as large as needed: $2^{100}$ is computed exactly.

### Example 3: Shallow and deep copies of nested lists

```python
import copy

grid = [[0, 0], [0, 0]]
shallow = grid.copy()
deep = copy.deepcopy(grid)

grid[0][0] = 9             # change an inner list
grid.append([1, 1])        # change the outer list

print(grid)
print(shallow)
print(deep)
```

Output:

```text
[[9, 0], [0, 0], [1, 1]]
[[9, 0], [0, 0]]
[[0, 0], [0, 0]]
```

The shallow copy has its own outer list, so it does not see the appended row, but it shares the inner lists, so it does see the 9. The deep copy shares nothing and is unaffected by either change.

## Applications

- **Function arguments.** Python passes references to objects. A function that appends to a list argument changes the caller's list; a function that rebinds its parameter does not. Knowing this tells you when to copy before modifying.
- **Configuration and caches.** Dictionaries are shared by reference, so one module can update settings that others read. When you need a snapshot that later changes cannot affect, take a copy.
- **Money and measurements.** Financial code uses `Decimal` to avoid rounding errors; scientific code uses floats with tolerances such as `math.isclose()`.
- **Large integers.** Cryptography and combinatorics rely on Python's arbitrary-precision integers, with no overflow checks needed.

## Common mistakes

- **Expecting `b = a` to copy a list.** It creates an alias. Use `a.copy()` (or `copy.deepcopy()` for nested data) when you need independence.
- **Comparing floats with `==`.** Use `math.isclose()` or a tolerance; for exact decimal values use `Decimal`.
- **Using `is` for value comparisons.** `x is 1000` may work in one place and fail in another. Use `==` for values and keep `is` for `None` and identity checks.
- **Forgetting that `bool` is an `int`.** `True + True` is `2`, and `isinstance(True, int)` is `True`, which matters when validating numeric input.
- **Creating a grid with `[[0] * 3] * 3`.** This repeats the same inner list three times, so changing one row changes all of them. Use `[[0] * 3 for _ in range(3)]`.

## Revision notes

- A variable is a name bound to an object; assignment binds, it never copies.
- Types belong to objects. Python is dynamically typed (checked at run time) and strongly typed (no silent conversions between unrelated types).
- `int` has arbitrary precision; `float` is IEEE 754 binary and approximate; `bool` is a subclass of `int`.
- Immutable objects are replaced when "changed"; mutable objects are modified in place and every alias sees it.
- `==` compares values; `is` compares identity and is reserved for `None` and identity checks.
- `copy()` is shallow (inner objects shared); `copy.deepcopy()` copies everything.

## Practice questions

:::question basic
After `a = [1, 2, 3]` and `b = a`, what does `print(a)` show once you run `b.append(4)`?
:::answer
`[1, 2, 3, 4]`. The statement `b = a` binds a second name to the same list object, so appending through `b` changes the list that `a` also refers to.
:::

:::question basic
Why does `0.1 + 0.2 == 0.3` evaluate to `False`, and what should you write instead?
:::answer
0.1, 0.2 and 0.3 cannot be represented exactly in binary floating point, so the stored sum differs from the stored 0.3 in the last bits. Compare with `math.isclose(0.1 + 0.2, 0.3)`, or use `Decimal("0.1") + Decimal("0.2")` when exact decimal arithmetic is required.
:::

:::question intermediate
What is printed by `s = "lumi"; t = s; s += "na"; print(s, t)`, and why is it different from the list case?
:::answer
It prints `lumina lumi`. Strings are immutable, so `s += "na"` builds a new string and rebinds `s`; `t` still refers to the original `"lumi"`. With a list, `+=` mutates the shared object in place, so both names would see the change.
:::

:::question intermediate
`grid = [[0] * 3] * 3` followed by `grid[0][0] = 1` sets the first element of every row to 1. Explain why and give a correct way to build the grid.
:::answer
`[[0] * 3] * 3` creates one inner list and repeats a reference to it three times, so all three rows are the same object. Changing it through one row shows in every row. Build independent rows with a comprehension: `grid = [[0] * 3 for _ in range(3)]`.
:::

:::question advanced
A function `def add_tag(tags): tags.append("new")` is called as `add_tag(my_tags)`. Another, `def reset(tags): tags = []`, is called as `reset(my_tags)`. Which call changes `my_tags` as seen by the caller, and why?
:::answer
Only `add_tag` does. Python passes a reference to the same list, so `append` mutates the caller's object. In `reset`, `tags = []` rebinds the local name `tags` to a new empty list; the caller's name `my_tags` still refers to the original list, which is unchanged.
:::

:::question advanced
Why is `isinstance(True, int)` `True`, and how would you reject booleans when a function must accept only real integers?
:::answer
`bool` is defined as a subclass of `int`, so every boolean is also an integer (`True` behaves like 1, `False` like 0). To reject booleans, check `isinstance(x, int) and not isinstance(x, bool)`, or test `type(x) is int` if subclasses should also be rejected.
:::

## Further learning

- **Next:** *Type Casting & Operators* covers explicit conversions such as `int()` and `str()`, and how Python's arithmetic and boolean operators work.
- **Related:** *Lists, Dictionaries & Comprehensions* builds on mutability to show how Python's main collections behave.
- **Related:** *Defining Functions & Scope Resolution* explains how names are looked up and why mutable default arguments are dangerous.
