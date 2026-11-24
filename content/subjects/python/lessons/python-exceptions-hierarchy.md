---
lesson: python-exceptions-hierarchy
title: Try-Except Blocks & Custom Exceptions
summary: How Python reports errors as exceptions, how try, except, else, and finally control what happens next, and how to raise and define your own exception types.
minutes: 35
type: theory
objectives:
  - Read a traceback and identify the exception type, message, and failing line
  - Handle exceptions with try, except, else, and finally, catching specific types rather than everything
  - Raise built-in exceptions and define custom exception classes that form a clear hierarchy
review: ai-draft
---
## Introduction

Programs meet problems they cannot ignore: a file is missing, a user types letters where a number belongs, a network call times out. Python signals such problems with **exceptions**. An exception stops normal execution and travels up the call stack until some code handles it; if nothing does, the program ends with a **traceback**. Handling exceptions well means your program fails gracefully, reports useful messages, and never hides bugs.

**Before you start:** you should know functions, conditionals, and basic classes and inheritance.

## Core theory

### Exceptions and tracebacks

When `int("abc")` runs, Python creates a `ValueError` object and **raises** it. The traceback printed at the end of an unhandled exception lists the chain of calls, the file and line of each, and finally the exception type and message, such as `ValueError: invalid literal for int() with base 10: 'abc'`. Read tracebacks from the bottom up: the last line says what happened, and the lines above say where.

Common built-in exceptions include `ValueError` (right type, bad value), `TypeError` (wrong type), `KeyError` and `IndexError` (missing key or index), `ZeroDivisionError`, `FileNotFoundError`, and `AttributeError`.

### try, except, else, finally

```python
try:
    value = int(text)
except ValueError:
    value = 0
else:
    print("parsed")
finally:
    print("done")
```

- `try` holds the code that may fail.
- Each `except Type:` handles one kind of exception; `except (A, B) as err:` handles several and binds the exception object to `err`.
- `else` runs only if the `try` block raised nothing; keeping success code there keeps the `try` block small.
- `finally` always runs, whether or not an exception occurred, and is used for clean-up such as closing files.

Python checks the `except` clauses in order and uses the first one that matches, so put specific types before general ones.

### The exception hierarchy

Exceptions are classes arranged in a hierarchy. `BaseException` is the root; `Exception` is the parent of nearly all errors a program should handle; `KeyboardInterrupt` and `SystemExit` inherit from `BaseException` directly so that a careless `except Exception` does not stop Ctrl+C from working. Lower down, `LookupError` is the parent of both `KeyError` and `IndexError`, and `OSError` covers `FileNotFoundError` and `PermissionError`. An `except` clause catches its type **and all subclasses**.

### Raising and defining exceptions

`raise ValueError("age must be positive")` signals an error from your own code. Inside an `except` block, a bare `raise` re-raises the current exception, and `raise NewError(...) from err` raises a new one while keeping the original as its cause.

Custom exceptions are classes that inherit from `Exception`. Giving an application a small family of them, such as `class BankError(Exception)` with subclasses `InsufficientFunds(BankError)`, lets callers catch one precise case or the whole family.

## Worked examples

### Example 1: Safe parsing with else and finally

```python
def parse_age(text):
    try:
        age = int(text)
    except ValueError as err:
        print("not a number:", err)
        return None
    else:
        if age < 0:
            raise ValueError("age must not be negative")
        return age
    finally:
        print("checked", repr(text))

print(parse_age("21"))
print(parse_age("twenty"))
try:
    parse_age("-4")
except ValueError as err:
    print("rejected:", err)
```

Output:

```text
checked '21'
21
not a number: invalid literal for int() with base 10: 'twenty'
checked 'twenty'
None
checked '-4'
rejected: age must not be negative
```

`finally` runs before each function returns, even when the `else` block raises. The caller handles the error raised for a negative age.

### Example 2: A custom exception hierarchy

```python
class BankError(Exception):
    pass

class InsufficientFunds(BankError):
    def __init__(self, needed):
        super().__init__(f"short by {needed}")
        self.needed = needed

def withdraw(balance, amount):
    if amount <= 0:
        raise BankError("amount must be positive")
    if amount > balance:
        raise InsufficientFunds(amount - balance)
    return balance - amount

for amount in (30, 150, -5):
    try:
        print(withdraw(100, amount))
    except InsufficientFunds as err:
        print("declined:", err, err.needed)
    except BankError as err:
        print("invalid:", err)
```

Output:

```text
70
declined: short by 50 50
invalid: amount must be positive
```

The more specific `InsufficientFunds` clause comes first. Because it inherits from `BankError`, reversing the clauses would send every bank error to the general handler.

## Applications

- **Input validation:** convert user input inside `try` and ask again on `ValueError`.
- **Resource clean-up:** `finally` (or a `with` statement) releases files, locks, and connections.
- **Libraries:** a package defines its own exception base class so users can catch all of its errors at once.
- **Retries:** network code catches timeout errors and tries again a limited number of times.

## Common mistakes

- **Catching everything with a bare `except:`.** It hides bugs and even catches Ctrl+C. Catch the specific exceptions you expect.
- **Putting too much code in `try`.** An unexpected error from an unrelated line gets handled by the wrong clause; keep `try` blocks small and use `else`.
- **Ordering clauses from general to specific.** The general clause wins and the specific one never runs.
- **Silently passing.** `except ValueError: pass` throws information away; at least log what happened.

## Revision notes

- Exceptions travel up the call stack until handled; unhandled ones print a traceback.
- `try` / `except` / `else` / `finally`: `else` on success, `finally` always.
- `except T` also catches subclasses of `T`; order clauses specific first.
- `raise` signals an error; bare `raise` re-raises; `raise X from err` chains causes.
- Custom exceptions inherit from `Exception`.
- Never use a bare `except:` to hide problems.

## Practice questions

:::question basic
Which exception does `[1, 2, 3][5]` raise, and which does `{"a": 1}["b"]` raise? What is their common parent?
:::answer
The list access raises `IndexError` and the dictionary access raises `KeyError`. Both inherit from `LookupError`, so `except LookupError` would catch either one.
:::

:::question basic
When does the `else` block of a `try` statement run?
:::answer
It runs only when the `try` block finishes without raising an exception. It is skipped if any exception occurs, whether or not an `except` clause handles it.
:::

:::question intermediate
Why should `except ZeroDivisionError` come before `except ArithmeticError` in the same `try` statement?
:::answer
`ZeroDivisionError` is a subclass of `ArithmeticError`, and Python uses the first matching clause. If the general clause came first it would catch the division error too, and the specific handler would never run.
:::

:::question intermediate
What is printed by `try: print(1/0)` followed by `except ZeroDivisionError: print("A")` and `finally: print("B")`?
:::answer
It prints `A` and then `B`. The division raises `ZeroDivisionError`, the matching clause prints `A`, and the `finally` block always runs afterwards.
:::

:::question advanced
Design a small exception hierarchy for a file-upload service that must report "file too large", "unsupported type", and "storage unavailable", and explain how a caller would use it.
:::answer
Define `class UploadError(Exception)` as the base, with subclasses `FileTooLarge(UploadError)`, `UnsupportedType(UploadError)`, and `StorageUnavailable(UploadError)`. A web handler can catch the first two to return a clear message to the user, catch `StorageUnavailable` to retry or show a "try later" page, and catch `UploadError` as a final net for anything else the service raises.
:::

## Further learning

- **Next:** *File I/O & Context Managers* shows how `with` statements guarantee clean-up even when exceptions occur.
- **Related:** *Unit Testing & Debugging* covers testing that code raises the right exception with `pytest.raises`.
