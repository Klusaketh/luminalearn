---
lesson: python-file-io-context-managers
title: File I/O & Context Managers
summary: Reading and writing text files safely with open and with, choosing file modes and encodings, working with JSON, and how context managers guarantee clean-up.
minutes: 35
type: theory
objectives:
  - Open files in the correct mode, read them line by line or all at once, and write and append text
  - Explain how a with statement and a context manager release resources even when errors occur
  - Save and load structured data with the json module and handle common file errors
review: ai-draft
---
## Introduction

Data that should outlive a program, such as settings, scores, logs, or a downloaded dataset, lives in files. Python's built-in `open` function gives you a **file object** for reading or writing, and the `with` statement makes sure the file is closed again, even if something goes wrong halfway. This lesson covers file modes and encodings, the patterns for reading and writing text, saving structured data as **JSON**, and how context managers work.

**Before you start:** you should know strings, lists, dictionaries, and `try` / `except`.

## Core theory

### Opening files: modes and encodings

`open(path, mode, encoding=...)` returns a file object. The **mode** says what you intend to do:

| Mode | Meaning |
| :--- | :--- |
| `"r"` | read text (default); the file must exist |
| `"w"` | write text; creates the file or **erases** an existing one |
| `"a"` | append text to the end; creates the file if needed |
| `"x"` | create a new file; fails if it already exists |
| `"rb"`, `"wb"` | read or write raw bytes (images, PDFs) |

Text mode converts bytes to characters, so pass `encoding="utf-8"` explicitly; the default depends on the operating system, which causes bugs when a file moves between machines.

### Reading and writing

- `f.read()` returns the whole file as one string; fine for small files.
- `for line in f:` reads one line at a time, using little memory even for huge files. Each line keeps its trailing `"\n"`, so use `line.rstrip("\n")` or `line.strip()`.
- `f.readlines()` returns a list of all lines.
- `f.write(text)` writes a string and does **not** add a newline; `print(..., file=f)` does.

### Context managers and with

A file holds an operating-system resource that must be released with `f.close()`. If an exception happens before `close()`, the file stays open. The `with` statement solves this:

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("hello\n")
```

`open` returns a **context manager**: an object with `__enter__` and `__exit__` methods. `with` calls `__enter__` at the start and **always** calls `__exit__` at the end, whether the block finishes normally, returns, or raises. For a file, `__exit__` closes it. Locks, database connections, and temporary directories use the same protocol, and `contextlib.contextmanager` lets you write your own with a generator.

### JSON for structured data

**JSON** is a text format for nested lists and dictionaries that almost every language can read. `json.dump(obj, f, indent=2)` writes a Python object to a file, and `json.load(f)` reads it back; `json.dumps` and `json.loads` work with strings. JSON keys are always strings, so a dictionary with integer keys comes back with string keys, and tuples come back as lists.

### File errors

Opening a missing file for reading raises `FileNotFoundError`; lacking permission raises `PermissionError`; both inherit from `OSError`. Reading invalid JSON raises `json.JSONDecodeError`, a subclass of `ValueError`.

## Worked examples

### Example 1: Write, append, and read line by line

```python
with open("marks.txt", "w", encoding="utf-8") as f:
    f.write("Asha,91\n")
    f.write("Ravi,78\n")

with open("marks.txt", "a", encoding="utf-8") as f:
    print("Meena,85", file=f)

total = 0
with open("marks.txt", encoding="utf-8") as f:
    for line in f:
        name, mark = line.strip().split(",")
        total += int(mark)
        print(f"{name:<6}{mark}")
print("average", round(total / 3, 1))
print(f.closed)
```

Output:

```text
Asha  91
Ravi  78
Meena 85
average 84.7
True
```

Mode `"a"` adds a third line without erasing the first two. After the `with` block, `f.closed` is `True` because the context manager closed the file.

### Example 2: Saving settings as JSON, and a missing file

```python
import json

settings = {"theme": "dark", "font_size": 14, "recent": ["a.py", "b.py"], 1: "one"}
with open("settings.json", "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)

with open("settings.json", encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded["recent"][0], loaded["font_size"] + 1)
print(sorted(loaded.keys()))

try:
    with open("missing.json", encoding="utf-8") as f:
        json.load(f)
except FileNotFoundError:
    print("no saved settings, using defaults")
```

Output:

```text
a.py 15
['1', 'font_size', 'recent', 'theme']
no saved settings, using defaults
```

The integer key `1` comes back as the string `'1'`, because JSON object keys are strings.

## Applications

- **Configuration:** applications store user settings as JSON and load them at start-up.
- **Logs:** append mode adds one line per event without rewriting the file.
- **Data processing:** reading line by line handles log files far larger than memory.
- **Safe resource use:** `with` manages database transactions, network connections, and locks the same way.

## Common mistakes

- **Opening with `"w"` when you meant `"a"`.** Write mode erases the file first.
- **Forgetting the newline.** `f.write("x")` writes no line break; add `"\n"` or use `print(..., file=f)`.
- **Relying on the default encoding.** Always pass `encoding="utf-8"` for text files.
- **Using a file after the `with` block.** It is closed; reading raises `ValueError: I/O operation on closed file`.

## Revision notes

- `open(path, mode, encoding="utf-8")`; modes `r`, `w`, `a`, `x`, plus `b` for bytes.
- `with` guarantees `__exit__`, which closes the file, even on errors.
- Iterate `for line in f` for large files; lines keep `"\n"`.
- `json.dump` / `json.load` for files; `dumps` / `loads` for strings.
- JSON keys are strings; tuples become lists.
- Missing files raise `FileNotFoundError` (an `OSError`).

## Practice questions

:::question basic
What is the difference between opening a file with mode `"w"` and mode `"a"`?
:::answer
Mode `"w"` truncates an existing file to empty before writing, while `"a"` keeps the existing content and adds new text at the end. Both create the file if it does not exist.
:::

:::question basic
Why is `with open(...) as f:` preferred over calling `open` and `close` yourself?
:::answer
The `with` statement calls the file's `__exit__` method when the block ends for any reason, including an exception, so the file is always closed. Manual `close()` calls are skipped when an error happens before them.
:::

:::question intermediate
You save `{"scores": (1, 2), 5: "five"}` with `json.dump` and load it back. What do you get?
:::answer
You get `{"scores": [1, 2], "5": "five"}`. JSON has no tuple type, so the tuple becomes a list, and object keys must be strings, so the integer key 5 becomes `"5"`.
:::

:::question intermediate
Write code that counts the lines in a large text file without loading it all into memory.
:::answer
`with open(path, encoding="utf-8") as f: count = sum(1 for _ in f)`. Iterating over the file object reads one line at a time, so memory use stays small regardless of the file size.
:::

:::question advanced
Explain what happens, step by step, when an exception is raised inside a `with open(...) as f:` block.
:::answer
Python stops executing the block and calls the context manager's `__exit__` method with the exception details. For a file, `__exit__` closes the file and returns a false value, which means "do not suppress the exception". The exception then continues to propagate to the nearest enclosing handler, but the file has already been released.
:::

## Further learning

- **Next:** *Module System & Package Imports* explains how to split a program across several files.
- **Related:** *Try-Except Blocks & Custom Exceptions* covers the error handling used with file operations.
