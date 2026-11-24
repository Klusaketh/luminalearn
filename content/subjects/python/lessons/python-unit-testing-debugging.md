---
lesson: python-unit-testing-debugging
title: Unit Testing & Debugging
summary: Writing automated tests with unittest and pytest, choosing good test cases, and a systematic process for finding and fixing bugs with tracebacks, prints, assertions, and the debugger.
minutes: 45
type: theory
objectives:
  - Write unit tests with assertions using both unittest and pytest, including tests for expected exceptions
  - Choose test cases that cover normal values, edge cases, and invalid input
  - Debug systematically by reproducing, isolating, and fixing a bug, using tracebacks, logging, and pdb
review: ai-draft
---
## Introduction

Every programmer writes bugs; good programmers catch them early. A **unit test** is a small piece of code that calls a function with known inputs and checks the result automatically. A suite of tests lets you change code with confidence, because a broken behaviour shows up the moment you run the tests. When a test fails, or a user reports a problem, **debugging** is the disciplined search for the cause. This lesson covers both.

**Before you start:** you should know functions, exceptions, classes, and how to import a module.

## Core theory

### What a unit test checks

A unit test has three parts, often called **Arrange, Act, Assert**: set up the inputs, call the code under test, and check the outcome. The check is an **assertion**: a statement that must be true. `assert add(2, 3) == 5` raises `AssertionError` if the function returns anything else.

### unittest

The standard library's `unittest` organises tests in classes:

```python
import unittest

class TestAdd(unittest.TestCase):
    def test_small_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_rejects_text(self):
        with self.assertRaises(TypeError):
            add("2", 3)
```

Each method starting with `test` is one test. `TestCase` provides `assertEqual`, `assertTrue`, `assertIn`, `assertAlmostEqual` for floats, and `assertRaises`. `setUp` runs before every test to prepare shared data. Run the tests with `python -m unittest`.

### pytest

**pytest**, the most popular third-party framework, uses plain functions and the plain `assert` statement, and explains failures by showing the values involved:

```python
def test_add():
    assert add(2, 3) == 5

def test_rejects_text():
    with pytest.raises(TypeError):
        add("2", 3)
```

Running `pytest` finds files named `test_*.py` and functions named `test_*`. `@pytest.mark.parametrize` runs one test with many inputs, and **fixtures** supply prepared objects such as temporary files.

### Choosing test cases

Good tests cover: **typical** values; **edge cases** such as empty input, zero, one element, the largest allowed value, and duplicates; **invalid** input that should raise an error; and every branch of the code. A failing test should point clearly at one behaviour, so keep each test small and give it a descriptive name.

### Debugging systematically

1. **Reproduce** the bug reliably, ideally as a failing test.
2. **Read the traceback** from the bottom: the exception type, the message, and the line.
3. **Isolate** the cause: shrink the input, print or log intermediate values, or step through with the debugger. `breakpoint()` opens **pdb**, where `n` runs the next line, `s` steps into a call, `p x` prints a value, and `c` continues.
4. **Fix** the cause, not the symptom, and keep the test so the bug cannot return.

The `logging` module is better than scattered `print` calls in real programs: messages carry levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`) and can be switched on or off without editing code.

## Worked examples

### Example 1: unittest finds a bug

```python
import io
import unittest

def average(values):
    return sum(values) / len(values) if values else 0

def grade(mark):
    if mark >= 90:
        return "A"
    if mark > 75:
        return "B"
    return "C"

class TestGrades(unittest.TestCase):
    def test_average(self):
        self.assertAlmostEqual(average([1, 2, 2]), 5 / 3)

    def test_empty_average(self):
        self.assertEqual(average([]), 0)

    def test_grade_boundaries(self):
        self.assertEqual(grade(90), "A")
        self.assertEqual(grade(75), "B")

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestGrades)
result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
print("ran", result.testsRun, "failures", len(result.failures))
print(result.failures[0][0].id().split(".")[-1])
```

Output:

```text
ran 3 failures 1
test_grade_boundaries
```

The specification says 75 earns a B, but the code uses `mark > 75`. The boundary test catches the off-by-one error that a test with a typical mark such as 80 would miss. Changing the condition to `mark >= 75` fixes it.

### Example 2: Isolating a bug by printing intermediate values

```python
def running_max(values):
    best = 0
    result = []
    for v in values:
        best = max(best, v)
        result.append(best)
    return result

print(running_max([3, 1, 4, 1, 5]))
print(running_max([-3, -1, -4]))

def running_max_fixed(values):
    result = []
    for v in values:
        result.append(v if not result else max(result[-1], v))
    return result

print(running_max_fixed([-3, -1, -4]))
```

Output:

```text
[3, 3, 4, 4, 5]
[0, 0, 0]
[-3, -1, -1]
```

The positive example looks right, which is why the bug survived. All-negative input exposes it: `best` started at 0, a value that never appears in the data. The fix starts from the first real value.

## Applications

- **Continuous integration:** every push runs the test suite automatically, as in this project's CI.
- **Refactoring:** tests confirm that behaviour is unchanged after restructuring code.
- **Bug reports:** each reported bug becomes a failing test before it is fixed.
- **Teaching tools:** the practice sandbox judges your solutions with exactly this kind of test.

## Common mistakes

- **Testing only the happy path.** Bugs live at boundaries and in invalid input.
- **Comparing floats with `==`.** Use `assertAlmostEqual` or `pytest.approx`.
- **Tests that depend on each other.** Each test should set up its own data and pass in any order.
- **Changing code at random while debugging.** Form a hypothesis, test it, and change one thing at a time.

## Revision notes

- Arrange, Act, Assert.
- `unittest`: classes of `test_*` methods, `assertEqual`, `assertRaises`, `setUp`.
- `pytest`: plain functions and `assert`, `pytest.raises`, `parametrize`, fixtures.
- Cover typical, edge, invalid, and every branch.
- Debug: reproduce, read the traceback, isolate, fix the cause, keep the test.
- `breakpoint()` starts pdb; prefer `logging` to `print` in real programs.

## Practice questions

:::question basic
What does an assertion do when its condition is false?
:::answer
It raises `AssertionError`, which a test framework records as a test failure. When the condition is true, nothing happens and execution continues.
:::

:::question basic
How do you test that `int("abc")` raises `ValueError` with pytest?
:::answer
Write `with pytest.raises(ValueError): int("abc")`. The test passes only if the block raises `ValueError` (or a subclass); it fails if no exception, or a different one, is raised.
:::

:::question intermediate
List four test cases for a function `max_of(values)` that returns the largest number in a list, and explain why each matters.
:::answer
A typical list such as `[3, 9, 2]`; a single element `[5]` to check the loop start; all negative numbers `[-4, -2, -7]` to catch code that starts from 0; and an empty list, which should raise `ValueError` or follow whatever rule the specification states. Each targets a different way the implementation could be wrong.
:::

:::question intermediate
Why is `assert 0.1 + 0.2 == 0.3` a bad test, and what should you write instead?
:::answer
Binary floating point cannot represent 0.1, 0.2, or 0.3 exactly, so the sum is `0.30000000000000004` and the equality fails. Use `math.isclose(0.1 + 0.2, 0.3)`, `pytest.approx(0.3)`, or `assertAlmostEqual`.
:::

:::question advanced
A function works on your machine but a user reports a crash. Describe a systematic way to fix it so that it stays fixed.
:::answer
First reproduce it: collect the input and traceback, and write a failing test with the user's input. Read the traceback to find the failing line, then isolate the cause by shrinking the input and inspecting intermediate values with logging or the debugger. Fix the underlying cause, run the new test and the whole suite, and keep the test so a future change cannot reintroduce the bug.
:::

## Further learning

- **Next:** *Algorithmic Patterns in Python* gives you functions worth testing with the techniques from this lesson.
- **Related:** *Try-Except Blocks & Custom Exceptions* explains the exceptions your tests should expect.
