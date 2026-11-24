---
lesson: python-closures-decorators
title: Closures & Decorators
summary: How nested functions remember variables from their enclosing scope (closures), and how decorators use closures to wrap functions with extra behaviour such as timing, logging, and caching.
minutes: 45
type: theory
objectives:
  - Explain what a closure is and use nonlocal to update captured state
  - Write decorators with and without arguments, preserving metadata with functools.wraps
  - Apply standard decorators such as functools.lru_cache, staticmethod, and property, and reason about their effect
review: ai-draft
---
## Introduction

In Python, functions are **first-class objects**: you can store them in variables, pass them to other functions, and return them from functions. Two powerful ideas follow. A **closure** is a function that remembers variables from the place where it was created. A **decorator** is a function that takes another function and returns an improved version, letting you add logging, timing, access checks, or caching without touching the original code. Frameworks such as Flask, FastAPI, and pytest are built on decorators.

**Before you start:** you should know how to define functions, default arguments, `*args`, `**kwargs`, and the LEGB scope rule.

## Core theory

### Functions as values and nested functions

You can define a function inside another function. The inner function can read the outer function's local variables. If the outer function **returns** the inner one, the inner function still has access to those variables after the outer call has finished: Python keeps them alive in the function's closure cells.

### Closures

```python
def make_multiplier(n):
    def multiply(x):
        return x * n
    return multiply

double = make_multiplier(2)
```

`double` is a closure: it carries the value `n = 2` with it. Each call to `make_multiplier` creates a new, independent closure. Reading a captured variable needs no declaration, but **assigning** to it does: without `nonlocal count`, the statement `count += 1` inside the inner function makes `count` a new local variable and raises `UnboundLocalError`.

A well-known trap is **late binding**: closures capture variables, not values. Functions created in a loop all see the loop variable's final value unless you bind the current value, for example with a default argument `lambda i=i: i`.

### Decorators

A decorator is a callable that takes a function and returns a replacement:

```python
def logged(func):
    def wrapper(*args, **kwargs):
        print("calling", func.__name__)
        return func(*args, **kwargs)
    return wrapper
```

Writing `@logged` above `def area(...)` is exactly the same as `area = logged(area)`. The `wrapper` accepts `*args, **kwargs` so it works with any signature, and it returns the original result.

Wrapping hides the original function's name and docstring, which confuses debugging tools. Decorating `wrapper` with `@functools.wraps(func)` copies them across.

A decorator **with arguments**, such as `@retry(times=3)`, adds one more level: `retry(times=3)` runs first and returns the actual decorator. Several decorators stack bottom-up: the one nearest the `def` is applied first.

### Decorators in the standard library

- `@functools.lru_cache(maxsize=None)` memoizes a function: repeated calls with the same arguments return the stored result.
- `@property` turns a method into a read-only attribute; `@staticmethod` and `@classmethod` change what a method receives as its first argument.
- `@dataclasses.dataclass` generates `__init__`, `__repr__`, and `__eq__` for a class.

## Worked examples

### Example 1: A counter closure with nonlocal

```python
def make_counter(start=0):
    count = start
    def increment(step=1):
        nonlocal count
        count += step
        return count
    return increment

a = make_counter()
b = make_counter(10)
print(a(), a(), a(5))
print(b(), a())
print(a.__closure__[0].cell_contents)
```

Output:

```text
1 2 7
11 8
8
```

`a` and `b` each keep their own `count`. `__closure__` shows the cell where the captured value lives.

### Example 2: A timing-style decorator and lru_cache

```python
import functools

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

@count_calls
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(15), fib.calls, fib.__name__)

@functools.lru_cache(maxsize=None)
def fast_fib(n):
    return n if n < 2 else fast_fib(n - 1) + fast_fib(n - 2)

print(fast_fib(80))
print(fast_fib.cache_info().misses)
```

Output:

```text
610 1973 fib
23416728348467685
81
```

The plain recursive version makes 1,973 calls for `fib(15)`. With `lru_cache`, each value from 0 to 80 is computed once (81 misses), so even `fast_fib(80)` is instant. `functools.wraps` keeps the name `fib`.

## Applications

- **Web routes:** `@app.get("/users")` registers a function as the handler for a URL.
- **Caching:** `lru_cache` speeds up recursive or expensive pure functions.
- **Cross-cutting concerns:** logging, timing, permission checks, and retries are added with one line.
- **Factories:** closures create configured functions, such as validators for different ranges.

## Common mistakes

- **Calling the function in the decorator line.** `@logged()` with parentheses passes nothing to a decorator that expects a function.
- **Forgetting to return the result.** A wrapper that calls `func(*args)` without `return` makes every decorated function return `None`.
- **Omitting `functools.wraps`.** Tracebacks and documentation then show `wrapper` instead of the real name.
- **Late binding in loops.** `[lambda: i for i in range(3)]` gives three functions that all return 2.

## Revision notes

- A closure is an inner function plus the outer variables it captured.
- Use `nonlocal` to assign to a captured variable.
- `@dec` above `def f` means `f = dec(f)`.
- Wrappers take `*args, **kwargs` and return `func(*args, **kwargs)`.
- `functools.wraps` preserves name and docstring.
- `lru_cache` memoizes; `property`, `staticmethod`, `classmethod` are decorators too.

## Practice questions

:::question basic
What does `@timer` above `def work(): ...` mean in plain Python without the `@` syntax?
:::answer
It means `work = timer(work)`. The function is defined, passed to `timer`, and the name `work` is rebound to whatever `timer` returns, usually a wrapper function.
:::

:::question basic
Why does `count += 1` inside an inner function raise `UnboundLocalError` unless you add `nonlocal count`?
:::answer
Assigning to a name makes it local to the inner function for the whole function body, so `count += 1` tries to read a local `count` that has no value yet. `nonlocal count` tells Python to use the variable from the enclosing function instead.
:::

:::question intermediate
What does `funcs = [lambda: i for i in range(3)]` followed by `[f() for f in funcs]` produce, and how do you get `[0, 1, 2]`?
:::answer
It produces `[2, 2, 2]`, because each lambda captures the variable `i`, not its value, and `i` ends at 2. Binding the current value as a default argument fixes it: `[lambda i=i: i for i in range(3)]`.
:::

:::question intermediate
Write a decorator `shout` that upper-cases the string returned by any function.
:::answer
`def shout(func):` then `@functools.wraps(func)` `def wrapper(*args, **kwargs): return func(*args, **kwargs).upper()` and `return wrapper`. The wrapper forwards all arguments, calls the original, transforms the result, and returns it.
:::

:::question advanced
Why does `lru_cache` turn the exponential recursive Fibonacci into a linear-time function, and when would caching be wrong?
:::answer
Naive Fibonacci recomputes the same subproblems many times, giving roughly $O(\varphi^n)$ calls. With a cache, each `n` is computed once and later calls return the stored value, so there are only $n + 1$ distinct computations. Caching is wrong for functions whose result depends on something other than the arguments (time, files, random numbers) or that have side effects, and it needs hashable arguments.
:::

## Further learning

- **Next:** *Classes, Inheritance & Polymorphism* shows `@property` and `@classmethod` in context.
- **Related:** *Memoization vs Tabulation* in Data Structures & Algorithms explains the dynamic-programming idea behind `lru_cache`.
