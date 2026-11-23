---
lesson: functions-scope-and-closures
title: Defining Functions & Scope Resolution
summary: Write reusable functions with flexible parameters, trace how Python finds a name with the LEGB rule, and pass functions around as values.
minutes: 45
type: theory
objectives:
  - Define functions with positional, keyword, default, *args and **kwargs parameters
  - Explain why default values are evaluated once and avoid the mutable default trap
  - Trace name lookup with the LEGB rule and use global and nonlocal correctly
  - Treat functions as values by passing, returning and storing them, including closures and lambdas
---

## Introduction

A **function** gives a name to a piece of logic so you can run it many times with different inputs. Functions make programs shorter, easier to test and easier to read: `average(marks)` says what happens, while the six lines inside say how.

In Python, functions are also ordinary objects. You can store them in variables, put them in lists, pass them to other functions and return them from functions. This single idea powers sorting by a custom key, callbacks, decorators and much of Python's standard library.

**Before you start:** you should be comfortable with variables, types, `if` statements and loops (*Conditional Branching & Loops*).

## Core theory

### Defining and calling a function

`def` creates a function object and binds it to a name. `return` sends a value back to the caller and ends the function immediately. A function that reaches its end without `return` returns `None`.

A **docstring**, the string on the first line of the body, documents what the function does; tools such as `help()` display it. **Type hints** such as `def average(values: list[float]) -> float:` document the expected types. Python does not enforce them at run time, but editors and checkers such as mypy do.

### Parameters and arguments

| Kind | Definition | Call |
| :--- | :--- | :--- |
| Positional or keyword | `def area(w, h):` | `area(3, 4)` or `area(h=4, w=3)` |
| Default value | `def greet(name, greeting="Hello"):` | `greet("Asha")` |
| Variable positional | `def total(*values):` | `total(1, 2, 3)`: `values` is a tuple |
| Keyword-only | `def connect(host, *, timeout=5):` | `connect("db", timeout=10)` |
| Variable keyword | `def tag(**attrs):` | `tag(id=1, cls="x")`: `attrs` is a dict |

Parameters with defaults must come after those without. A bare `*` in the parameter list makes every later parameter keyword-only, which prevents mistakes such as `connect("db", 10)` where it is unclear what 10 means.

### Default values are evaluated once

A default value is computed **once, when `def` runs**, not each time the function is called. For immutable defaults such as `0` or `"Hello"` this never matters. For a mutable default such as `[]`, every call that uses the default shares the same list, so changes from one call leak into the next. The standard fix is `None` as a sentinel: `def add(item, items=None):` then `if items is None: items = []` inside the body.

### Scope and the LEGB rule

A name's **scope** is the region of code where it can be used. When Python meets a name, it searches four scopes in order and uses the first match:

| Letter | Scope | Contains |
| :--- | :--- | :--- |
| L | Local | Names assigned inside the current function, including its parameters |
| E | Enclosing | Local names of any outer function, when functions are nested |
| G | Global | Names assigned at the top level of the module |
| B | Built-in | Names Python provides, such as `len`, `print` and `range` |

Any assignment inside a function makes the name **local to that function for the whole body**. That is why reading a global and then assigning to it in the same function raises `UnboundLocalError`. To assign to a module-level name, declare `global name`; to assign to a name in an enclosing function, declare `nonlocal name`. Use both sparingly: returning values is usually clearer than changing shared state.

### Functions as values: higher-order functions, lambdas and closures

A **higher-order function** takes or returns another function. `sorted(students, key=get_mark)` passes a function as the sort key. A `lambda` writes a small one-expression function inline: `key=lambda s: s[1]`.

A **closure** is a function that remembers names from the enclosing scope where it was created, even after that outer function has returned. Closures let you build configured functions, such as a counter that keeps its own count, without classes or global variables.

## Worked examples

### Example 1: The mutable default trap and its fix

```python
def add_score_buggy(score, scores=[]):
    scores.append(score)
    return scores

def add_score(score, scores=None):
    if scores is None:
        scores = []
    scores.append(score)
    return scores

print(add_score_buggy(10))
print(add_score_buggy(20))   # the same default list is reused
print(add_score(10))
print(add_score(20))         # a fresh list every call
```

Output:

```text
[10]
[10, 20]
[10]
[20]
```

The buggy version created one list when `def` ran, and both calls appended to it. The fixed version builds a new list inside the body whenever the caller does not supply one.

### Example 2: Tracing the LEGB rule

```python
level = "global"

def outer():
    level = "enclosing"

    def inner():
        print("inner sees:", level)      # found in the enclosing scope

    inner()
    print("outer sees:", level)

outer()
print("module sees:", level)
print("built-in len:", len("lumina"))   # found in the built-in scope

def bump():
    count = 0

    def step():
        nonlocal count                   # assign to the enclosing name
        count += 1
        return count

    step()
    step()
    return step()

print("bumped to", bump())
```

Output:

```text
inner sees: enclosing
outer sees: enclosing
module sees: global
built-in len: 6
bumped to 3
```

`inner` has no local `level`, so lookup moves outward and finds the enclosing one before reaching the global. Each function's assignment creates its own name, so the global `level` never changes. In `bump`, `nonlocal count` lets `step` update the variable in `bump` instead of creating a new local one.

### Example 3: Flexible parameters, higher-order functions and closures

```python
def summary(title, *values, decimals=1, **labels):
    mean = sum(values) / len(values)
    tags = ", ".join(f"{k}={v}" for k, v in sorted(labels.items()))
    return f"{title}: mean {mean:.{decimals}f} ({tags})"

print(summary("Quiz", 7, 8, 10, decimals=2, subject="DSA", week=3))

def make_scaler(factor):
    def scale(x):
        return x * factor            # factor is remembered by the closure
    return scale

double = make_scaler(2)
to_percent = make_scaler(100)
print(double(21), to_percent(0.85))

results = [("Asha", 82), ("Ravi", 67), ("Meera", 91)]
print(sorted(results, key=lambda r: r[1], reverse=True))
print(list(map(double, [1, 2, 3])))
```

Output:

```text
Quiz: mean 8.33 (subject=DSA, week=3)
42 85.0
[('Meera', 91), ('Asha', 82), ('Ravi', 67)]
[2, 4, 6]
```

`*values` collects the extra positional arguments into a tuple, `decimals` is keyword-only because it follows `*values`, and `**labels` gathers the remaining keyword arguments into a dictionary. `make_scaler` returns a new function each time, and each closure remembers its own `factor`. The last two lines pass functions as arguments: a lambda as the sort key, and `double` to `map`.

## Applications

- **Reusable building blocks.** Validation, formatting and calculation logic lives in small functions that tests can check one at a time.
- **Sorting and filtering.** `sorted`, `min`, `max` and `filter` take a function that says how to compare or select items.
- **Callbacks and event handlers.** Web frameworks and GUIs register functions to run later, when a request arrives or a button is clicked.
- **Configured functions.** Closures build specialised functions, such as a scaler or a logger with a fixed prefix, and they are the basis of decorators.
- **Flexible APIs.** `*args`, `**kwargs` and keyword-only parameters let libraries accept optional settings without breaking existing callers.

## Common mistakes

- **Using a mutable default such as `[]` or `{}`.** It is shared between calls. Use `None` and create the object inside the body.
- **Forgetting `return`.** A function without `return` gives `None`, so `result = average(marks)` silently stores `None`.
- **Assigning to a global without declaring it.** The name becomes local for the whole function, and reading it first raises `UnboundLocalError`.
- **Calling instead of passing.** `sorted(data, key=get_mark())` calls `get_mark` immediately; pass the function itself with `key=get_mark`.
- **Overusing `global` state.** Functions that read and change globals are hard to test. Pass values in and return results instead.

## Revision notes

- `def` creates a function object; `return` ends it with a value, and the default return value is `None`.
- Parameter order: positional, defaults, `*args`, keyword-only, `**kwargs`.
- Default values are evaluated once, at definition time; use `None` for mutable defaults.
- LEGB: names are looked up in Local, then Enclosing, then Global, then Built-in scope.
- Assignment makes a name local to the whole function; `global` and `nonlocal` change that.
- Functions are first-class values; a closure remembers the enclosing names it uses.

## Practice questions

:::question basic
What does `def f(): x = 5` followed by `print(f())` print, and why?
:::answer
It prints `None`. The function assigns to `x` but never returns anything, and a function that reaches the end of its body without `return` returns `None`.
:::

:::question basic
In `def total(*values):`, what is the type of `values` when you call `total(4, 5, 6)`?
:::answer
A tuple: `(4, 5, 6)`. The `*` gathers all remaining positional arguments into a tuple. With no extra arguments it is the empty tuple `()`.
:::

:::question intermediate
Why does this code raise `UnboundLocalError`? `count = 0` then `def tick(): count += 1`.
:::answer
`count += 1` assigns to `count`, so Python treats `count` as a local name throughout `tick`. The augmented assignment must first read the local `count`, which has not been assigned yet. Declaring `global count` inside `tick` (or, better, passing and returning the value) fixes it.
:::

:::question intermediate
Rewrite `def log(message, lines=[]): lines.append(message); return lines` so that each call without `lines` starts with an empty list.
:::answer
Use `None` as the default and create the list inside: `def log(message, lines=None):` then `if lines is None: lines = []`, then append and return. The original default list was created once when `def` ran and shared by every call that omitted `lines`.
:::

:::question advanced
What does this print? `def make_counter(): n = 0` with a nested `def inc(): nonlocal n; n += 1; return n` and `return inc`; then `a = make_counter(); b = make_counter(); a(); a(); print(a(), b())`.
:::answer
It prints `3 1`. Each call to `make_counter` creates a new `n` and a new closure bound to it. `a` has been called three times, so its `n` is 3; `b` has its own `n`, called once, so it is 1.
:::

:::question advanced
Why is `def connect(host, *, timeout=5, retries=3):` safer than `def connect(host, timeout=5, retries=3):` for callers?
:::answer
The bare `*` makes `timeout` and `retries` keyword-only. A call like `connect("db", 3)` is then an error instead of silently setting `timeout` to 3 when the caller meant retries. Callers must write `connect("db", retries=3)`, which is self-explanatory, and the author can later reorder or add keyword-only parameters without breaking existing calls.
:::

## Further learning

- **Next:** *Iterators & Generators* shows functions that produce values lazily with `yield`.
- **Related:** *Closures & Decorators* builds on closures to wrap functions with extra behaviour, such as timing or caching.
- **Related:** *Unit Testing & Debugging* shows how small, pure functions make testing straightforward.
