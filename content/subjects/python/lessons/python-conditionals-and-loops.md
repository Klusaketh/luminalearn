---
lesson: conditional-branching-and-iteration
title: Conditional Branching & Loops
summary: Make decisions with if, elif and else, repeat work with while and for loops, and control loops with break, continue and else.
minutes: 35
type: theory
objectives:
  - Write if-elif-else chains whose conditions are tested in the right order
  - Predict the truth value of any object and use short-circuit evaluation safely
  - Choose between a while loop and a for loop, and iterate with range, enumerate and zip
  - Control loops with break, continue and the loop else clause
---

## Introduction

A program that runs every line exactly once, top to bottom, cannot do much. Real programs make **decisions** ("is this answer correct?") and **repeat** work ("check every answer in the quiz"). Python provides both with a small set of statements: `if`, `elif` and `else` for decisions, and `while` and `for` for repetition.

Python marks the body of each statement by **indentation** rather than braces. Everything indented under an `if` or a loop belongs to it, and the block ends where the indentation returns to the previous level. Four spaces per level is the standard.

**Before you start:** you should know Python's basic types and how assignment works (*Python Variables & Data Types*).

## Core theory

### if, elif and else

An `if` statement runs its block only when its condition is true. `elif` ("else if") adds further conditions, and `else` catches everything left over:

```text
if condition_1:
    ...            # runs when condition_1 is true
elif condition_2:
    ...            # runs when condition_1 is false and condition_2 is true
else:
    ...            # runs when every condition above is false
```

Python tests the conditions **from top to bottom and runs only the first block whose condition is true**. Order therefore matters: put the most specific conditions first. A conditional expression gives a value in one line: `label = "pass" if score >= 40 else "fail"`.

### Comparisons and logical operators

Comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `not in`) produce `True` or `False`. Python allows **chained comparisons**: `0 <= score <= 100` means `0 <= score and score <= 100`.

`and`, `or` and `not` combine conditions. `and` and `or` **short-circuit**: `a and b` does not evaluate `b` when `a` is false, and `a or b` does not evaluate `b` when `a` is true. This lets you guard a risky test, as in `if count > 0 and total / count > 50:`, which never divides by zero.

### Truthiness

Any object can be used as a condition. These values are **falsy**: `False`, `None`, numeric zero (`0`, `0.0`), and empty containers (`""`, `[]`, `()`, `{}`, `set()`). Almost everything else is **truthy**. Idiomatic Python writes `if items:` rather than `if len(items) > 0:`.

### while loops

A `while` loop repeats its block as long as its condition stays true. Use it when you do not know in advance how many repetitions are needed, for example "keep asking until the input is valid". Something inside the loop must eventually make the condition false, or the loop never ends.

### for loops and range

A `for` loop takes each item of an iterable (a list, string, dictionary, file or `range`) in turn. `range(stop)` produces `0, 1, ..., stop - 1`; `range(start, stop, step)` gives more control, and the `stop` value is never included. Two helpers make `for` loops clearer:

| Helper | Gives you | Example |
| :--- | :--- | :--- |
| `enumerate(seq, start=1)` | Each item with its position | `for i, name in enumerate(names, start=1):` |
| `zip(a, b)` | Matching items from several sequences together | `for name, mark in zip(names, marks):` |

Prefer `for` whenever you are processing a known collection: it cannot loop forever and needs no manual counter.

### break, continue and the loop else clause

- `break` leaves the loop immediately.
- `continue` skips the rest of the current pass and moves to the next one.
- A loop's `else` block runs only if the loop finished **without** a `break`. It is the natural place for "searched everything and did not find it".

### Cost of nested loops

A loop inside a loop runs its inner body once for every combination: two nested loops over $n$ items run about $n^2$ times. That is fine for a few hundred items but slow for millions, so look for a single pass (often with a set or dictionary) before nesting.

## Worked examples

### Example 1: Grading with an if-elif-else chain

```python
def grade(score):
    if not 0 <= score <= 100:
        return "invalid"
    elif score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 40:
        return "C"
    else:
        return "fail"

for s in (95, 75, 74, 39, 120):
    print(s, grade(s))
```

Output:

```text
95 A
75 B
74 C
39 fail
120 invalid
```

The range check comes first, so 120 is rejected before any grade test. Because only the first true branch runs, a score of 95 never reaches `score >= 75`, and each grade test only needs a lower bound.

### Example 2: A while loop with an unknown number of steps

The Collatz rule halves an even number and replaces an odd number $n$ with $3n + 1$. Nobody knows a formula for how many steps it takes to reach 1, which makes it a natural `while` loop.

```python
def collatz_steps(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

for start in (1, 6, 7, 27):
    print(start, collatz_steps(start))
```

Output:

```text
1 0
6 8
7 16
27 111
```

The loop condition `n != 1` is checked before every pass, so a start of 1 takes zero steps. The number of passes varies wildly (27 needs far more than its neighbours), which is exactly the situation where `while` beats `for`.

### Example 3: Searching with break, continue and for-else

```python
marks = {"Asha": 82, "Ravi": -1, "Meera": 91, "Kiran": 67}

for name, mark in marks.items():
    if mark < 0:
        print(f"skipping {name}: mark not entered")
        continue
    if mark >= 90:
        print(f"first distinction: {name} ({mark})")
        break
else:
    print("no distinction found")

for position, (name, mark) in enumerate(marks.items(), start=1):
    print(position, name, mark)
```

Output:

```text
skipping Ravi: mark not entered
first distinction: Meera (91)
1 Asha 82
2 Ravi -1
3 Meera 91
4 Kiran 67
```

`continue` skips Ravi's missing mark without stopping the search. `break` ends the loop at Meera, so the `else` block does not run; if no mark reached 90, the loop would finish normally and `else` would report it. The second loop uses `enumerate` and unpacks each `(name, mark)` pair.

## Applications

- **Input validation.** A `while` loop keeps asking until the user enters a valid value, and an `if-elif-else` chain decides which error message to show.
- **Processing records.** `for` loops walk through rows of a file, results from a database, or answers in a quiz, using `continue` to skip incomplete records.
- **Searching.** `for` with `break` and `else` finds the first match or reports that none exists, without an extra flag variable.
- **Simulations and games.** A main `while` loop runs until the game ends, checking conditions each turn.

## Common mistakes

- **Wrong branch order.** Testing `score >= 40` before `score >= 90` labels every distinction as a pass. Put the most specific condition first.
- **Using `=` instead of `==`.** `if x = 5:` is a syntax error in Python; comparison needs `==`.
- **Infinite while loops.** Forgetting to update the variable in the condition (for example, never changing `n`) makes the loop run forever.
- **Off-by-one with range.** `range(1, 10)` stops at 9. To include 10, write `range(1, 11)`.
- **Changing a list while looping over it.** Removing items during a `for` loop over the same list skips elements. Loop over a copy, or build a new list.
- **Misreading for-else.** The `else` block runs when the loop was **not** broken, not when the loop body "failed".

## Revision notes

- `if-elif-else` runs only the first block whose condition is true, testing from the top.
- Chained comparisons (`0 <= x <= 100`) and short-circuit `and`/`or` keep conditions short and safe.
- Falsy values: `False`, `None`, `0`, `0.0` and empty containers. Everything else is truthy.
- `while` repeats while a condition holds; use it when the number of passes is unknown.
- `for` visits each item of an iterable; use `range`, `enumerate` and `zip` instead of manual counters.
- `break` exits, `continue` skips to the next pass, and a loop's `else` runs only when no `break` happened.
- Two nested loops over $n$ items cost about $n^2$ passes.

## Practice questions

:::question basic
What does `range(2, 11, 3)` produce?
:::answer
`2, 5, 8`. It starts at 2, adds 3 each time, and stops before reaching 11, so 11 itself is never included.
:::

:::question basic
Which of these values are falsy: `0`, `"0"`, `[]`, `[0]`, `None`, `0.0`?
:::answer
`0`, `[]`, `None` and `0.0` are falsy. `"0"` is a non-empty string and `[0]` is a non-empty list, so both are truthy even though they contain a zero.
:::

:::question intermediate
A student writes `if score >= 40: print("pass") elif score >= 90: print("distinction")`. Why does a score of 95 never print "distinction", and how do you fix it?
:::answer
Python runs only the first true branch. A score of 95 satisfies `score >= 40`, so "pass" prints and the `elif` is never tested. Test the stricter condition first: `if score >= 90: ... elif score >= 40: ...`.
:::

:::question intermediate
Why is `if count > 0 and total / count > 50:` safe when `count` is 0, while `if total / count > 50 and count > 0:` is not?
:::answer
`and` evaluates left to right and stops at the first false operand. In the first version `count > 0` is false, so the division is never attempted. In the second version the division runs first and raises `ZeroDivisionError` before `count > 0` is checked.
:::

:::question advanced
Write a loop that prints the first even number in a list `nums`, or "none" if there is no even number, without using a flag variable.
:::answer
Use `for` with `break` and `else`:
`for n in nums:` then, indented, `if n % 2 == 0:` print `n` and `break`; finally an `else:` at the loop's indentation that prints `"none"`. The `else` block runs only when the loop finishes without `break`, which is exactly the "no even number" case.
:::

:::question advanced
Checking whether any two numbers in a list of $n$ numbers add up to a target with two nested loops takes about $n^2$ steps. Describe a single-loop approach and its cost.
:::answer
Loop once and keep a set of numbers seen so far. For each number `x`, check whether `target - x` is already in the set (an average constant-time lookup); if it is, a pair exists. Otherwise add `x` to the set. This makes one pass, so it takes about $n$ steps on average instead of $n^2$.
:::

## Further learning

- **Next:** *Defining Functions & Scope Resolution* packages logic like the grading chain into reusable functions.
- **Related:** *Iterators & Generators* explains what `for` really does behind the scenes and how to write your own iterables.
- **Related:** *Lists, Dictionaries & Comprehensions* shows how many simple loops become one-line comprehensions.
