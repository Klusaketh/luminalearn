---
lesson: python-string-formatting
title: String Formatting & Methods
summary: Python strings as immutable sequences of characters, the everyday string methods, f-string formatting with format specifiers, and the difference between text (str) and bytes.
minutes: 30
type: theory
objectives:
  - Use indexing, slicing, and common methods such as split, join, strip, replace, and find on strings
  - Format values with f-strings, including width, alignment, precision, and thousands separators
  - Explain why strings are immutable and convert between str and bytes with encode and decode
review: ai-draft
---
## Introduction

Programs constantly turn data into text and text into data: printing a report, building a file name, reading a line of a CSV file. Python's `str` type stores text as an immutable sequence of Unicode characters and comes with dozens of methods. This lesson covers the methods you will use daily, the **f-string** syntax for formatting numbers and tables, and how text becomes **bytes** when it is saved or sent over a network.

**Before you start:** you should know variables, lists, indexing, slicing, and `for` loops.

## Core theory

### Strings are immutable sequences

A string can be written with single, double, or triple quotes; triple quotes allow several lines. Like a list, a string supports `len(s)`, indexing `s[0]`, slicing `s[1:4]`, `in`, and iteration over characters. Unlike a list, a string is **immutable**: `s[0] = "J"` raises `TypeError`. Every method that seems to change a string returns a **new** string, so you must keep the result: `name = name.strip()`.

Because each `+` creates a new string, building a long string with `+` in a loop copies the text again and again, which can take $O(n^2)$ time. Collect the pieces in a list and call `"".join(pieces)` once, which takes $O(n)$.

### Everyday methods

| Method | Result |
| :--- | :--- |
| `s.lower()`, `s.upper()`, `s.title()` | changed case |
| `s.strip()`, `s.lstrip()`, `s.rstrip()` | whitespace removed from the ends |
| `s.split(sep)` | list of pieces; with no argument, splits on runs of whitespace |
| `sep.join(items)` | one string with `sep` between items (items must be strings) |
| `s.replace(old, new)` | every `old` replaced by `new` |
| `s.find(sub)` | index of the first match, or -1 |
| `s.startswith(p)`, `s.endswith(p)` | `True` or `False` |
| `s.isdigit()`, `s.isalpha()` | character class tests |

### f-strings and format specifiers

An **f-string** has an `f` before the quote and embeds expressions in braces: `f"{name} scored {mark}"`. After a colon you can add a **format specifier**:

- `{x:.2f}`: fixed-point with 2 decimals.
- `{x:8}`, `{s:<10}`, `{s:>10}`, `{s:^10}`: minimum width, left, right, or centre alignment.
- `{n:,}`: thousands separators; `{p:.1%}`: percentage.
- `{n:05d}`: pad an integer with zeros to width 5.
- `{x=}`: prints the expression and its value, handy for debugging.

Older styles still appear in existing code: `"{} and {}".format(a, b)` and `"%d items" % n`. f-strings are the clearest choice in new code.

### Text versus bytes

A `str` holds characters. Files and networks hold **bytes**. **Encoding** converts text to bytes and **decoding** converts back: `"café".encode("utf-8")` gives `b'caf\xc3\xa9'`, five bytes, because `é` needs two bytes in UTF-8. Decoding with the wrong encoding produces garbled text or a `UnicodeDecodeError`, so always state the encoding when reading or writing files.

## Worked examples

### Example 1: Cleaning and splitting a line of input

```python
line = "  Asha, 91 ,Ravi,78  "
parts = [p.strip() for p in line.strip().split(",")]
print(parts)
pairs = list(zip(parts[0::2], parts[1::2]))
print(pairs)
print(" | ".join(name.upper() for name, _ in pairs))
print(line.find("Ravi"), line.find("Zoe"))
```

Output:

```text
['Asha', '91', 'Ravi', '78']
[('Asha', '91'), ('Ravi', '78')]
ASHA | RAVI
12 -1
```

`split(",")` keeps the spaces around each value, so each piece is stripped. The slices `[0::2]` and `[1::2]` take every other item to pair names with marks.

### Example 2: A formatted report

```python
items = [("Notebook", 3, 45.5), ("Pen", 10, 12.0), ("Calculator", 1, 1250.0)]
print(f"{'Item':<12}{'Qty':>5}{'Total':>12}")
grand = 0
for name, qty, price in items:
    total = qty * price
    grand += total
    print(f"{name:<12}{qty:>5}{total:>12,.2f}")
print(f"{'Grand total':<17}{grand:>12,.2f}")
print(f"Tax share: {grand * 0.18 / grand:.1%}")
```

Output:

```text
Item          Qty       Total
Notebook        3      136.50
Pen            10      120.00
Calculator      1    1,250.00
Grand total          1,506.50
Tax share: 18.0%
```

Widths line the columns up: names are left-aligned in 12 characters, numbers right-aligned. `,.2f` adds a thousands separator and two decimals.

## Applications

- **Reports and logs:** f-strings with widths produce aligned tables and readable log lines.
- **Parsing input:** `split`, `strip`, and `int()` turn lines of text into data.
- **File names and URLs:** `join`, `replace`, and `startswith` build and check paths and links.
- **Networking and storage:** `encode` and `decode` move text across files and sockets.

## Common mistakes

- **Forgetting that methods return new strings.** `s.upper()` alone does nothing to `s`; assign the result.
- **Joining non-strings.** `", ".join([1, 2])` raises `TypeError`; convert first with `str`.
- **Building strings with `+` in a long loop.** Collect pieces in a list and `join` once.
- **Mixing up `split()` and `split(" ")`.** With no argument, runs of whitespace count as one separator; `" "` splits on every single space and can produce empty strings.

## Revision notes

- Strings are immutable; methods return new strings.
- `split` breaks text into a list; `sep.join(list)` reverses it.
- `find` returns -1 when not found; `index` raises `ValueError`.
- f-string specifiers: `:.2f`, `:<10`, `:>10`, `:^10`, `:,`, `:.1%`, `:05d`.
- `str.encode("utf-8")` gives bytes; `bytes.decode("utf-8")` gives text.
- Prefer `"".join(parts)` over repeated `+` for long strings.

## Practice questions

:::question basic
What does `"a,b,,c".split(",")` return?
:::answer
It returns `['a', 'b', '', 'c']`. Splitting on an explicit separator keeps the empty string between the two adjacent commas.
:::

:::question basic
Write an f-string that prints the value `3.14159` rounded to two decimal places.
:::answer
`f"{3.14159:.2f}"` produces `'3.14'`. The `.2f` specifier means fixed-point notation with two digits after the decimal point, rounding as needed.
:::

:::question intermediate
Why does `s = "hello"; s[0] = "J"` fail, and how do you produce `"Jello"`?
:::answer
Strings are immutable, so item assignment raises `TypeError`. Build a new string instead: `"J" + s[1:]` or `s.replace("h", "J", 1)`, and assign it to a name if you want to keep it.
:::

:::question intermediate
How many bytes does `"naïve".encode("utf-8")` contain, and why is it not 5?
:::answer
It contains 6 bytes. Four characters are ASCII and take one byte each, but `ï` lies outside ASCII and takes two bytes in UTF-8, so the five characters encode to six bytes.
:::

:::question advanced
A program builds a 1 MB report by running `report += line` for 20,000 lines. Explain why this can be slow and give a faster version.
:::answer
Each `+=` may create a new string and copy everything built so far, so the total copying grows roughly with the square of the number of lines. Instead append each line to a list, `parts.append(line)`, and call `report = "".join(parts)` once at the end, which copies each character only once.
:::

## Further learning

- **Next:** *Classes, Inheritance & Polymorphism* shows how to define `__str__` so your own objects format nicely in f-strings.
- **Related:** *File I/O & Context Managers* uses `encode`, `decode`, and the `encoding` argument when reading and writing text files.
