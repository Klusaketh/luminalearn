---
lesson: string-manipulation-encodings
title: String Manipulation and Character Encodings
summary: How text is stored as bytes, why immutability changes the cost of string operations, and efficient patterns for building and transforming strings.
minutes: 45
type: theory
objectives:
  - Explain the difference between characters, code points, and bytes, and how ASCII and UTF-8 encode text
  - Analyse the cost of common string operations, including the hidden quadratic cost of repeated concatenation
  - Use efficient patterns such as joining lists of parts, two-pointer reversal, and character counting
  - Solve classic string problems such as palindrome and anagram checks in linear time
---

## Introduction

A string looks like the simplest possible data: a sequence of characters. Underneath, it is an array of bytes interpreted through an **encoding**, and the details of that encoding decide how long a string is, how fast you can index into it, and whether a program handles names like "José" or "Zoë" correctly. Strings are also **immutable** in many languages, including Python and Java, which makes some innocent-looking code surprisingly slow.

This lesson treats strings as a data structure: how they are represented, what each operation costs, and which patterns produce correct and efficient text-processing code.

**Before you start:** you should understand arrays, Big-O notation, and Python dictionaries.

## Core theory

### Characters, code points, and bytes

- A **character** is an abstract unit of text, such as the letter A or the euro sign.
- **Unicode** assigns every character a number called a **code point**, written like U+0041 for A and U+20AC for €. There are over a million possible code points.
- An **encoding** maps code points to bytes so text can be stored and transmitted.

**ASCII** is a 7-bit encoding covering 128 characters: English letters, digits, punctuation, and control codes. `A` is 65, `a` is 97, and `0` is 48. Because each character is one byte, the $i$-th character is at byte $i$.

**UTF-8** is the dominant encoding on the web and in modern systems. It uses a **variable number of bytes** per code point:

| Code point range | Bytes | Examples |
| :--- | :---: | :--- |
| U+0000 to U+007F | 1 | ASCII: `A`, `7`, `?` |
| U+0080 to U+07FF | 2 | `é`, `ñ`, Greek, Cyrillic |
| U+0800 to U+FFFF | 3 | `€`, most Chinese, Japanese, and Korean characters |
| U+10000 to U+10FFFF | 4 | emoji, historic scripts |

UTF-8 is backwards compatible with ASCII: an ASCII file is already valid UTF-8. The cost of variable width is that the $i$-th character no longer sits at byte $i$; finding it requires scanning from the start. Languages handle this differently. Python 3 stores each string internally using a fixed width chosen from the widest character it contains (1, 2, or 4 bytes per code point), so indexing a `str` stays $\Theta(1)$. Converting to UTF-8 bytes for a file or network happens with `.encode()`.

### Length depends on what you count

The string `"café"` has 4 code points but 5 bytes in UTF-8, because `é` takes 2 bytes. Some visible characters are even built from several code points (an emoji with a skin-tone modifier, or a letter followed by a combining accent). Always be clear whether a length limit means characters, code points, or bytes; databases and network protocols often limit bytes.

### Immutability

In Python, Java, and C#, strings are **immutable**: once created, a string never changes. Operations that appear to modify a string, such as `s + t`, `s.upper()`, or `s.replace(a, b)`, build a **new** string and copy characters into it.

Immutability makes strings safe to share between parts of a program and lets them be used as dictionary keys, but it changes the cost of building text:

```python
result = ""
for word in words:
    result += word        # copies everything built so far
```

Each `+=` copies the whole current result. If the final string has length $L$ built from $n$ pieces, the total copying can reach $\Theta(nL)$, which is quadratic when pieces are similar in size. The fix is to collect pieces in a list and join once:

```python
result = "".join(words)   # computes the total length, then copies each piece once
```

`str.join` is $\Theta(L)$. (CPython sometimes optimises `+=` in place when no other reference to the string exists, but this is an implementation detail; do not rely on it.) Java's equivalent tool is `StringBuilder`.

### Costs of common operations

For a string of length $n$ (and pattern or second string of length $m$):

| Operation | Cost | Note |
| :--- | :--- | :--- |
| `s[i]` | $\Theta(1)$ | Python `str` |
| `len(s)` | $\Theta(1)$ | length is stored |
| `s + t` | $\Theta(n + m)$ | new string |
| `s[a:b]` | $\Theta(b - a)$ | slicing copies |
| `s == t` | $O(\min(n, m))$ | stops at first difference |
| `t in s`, `s.find(t)` | typically fast, worst case can be $O(nm)$ | depends on the search algorithm |
| `s.split()`, `s.upper()`, `s.replace()` | $\Theta(n)$ | builds new strings |
| `"".join(parts)` | $\Theta(\text{total length})$ | the right way to build |

### Useful techniques

- **Two pointers** compare or swap characters from both ends: palindrome checks, reversing words.
- **Counting with a dictionary or fixed array** solves anagram and frequency problems in $\Theta(n)$. With a known small alphabet (26 lowercase letters), a list of 26 counters is fastest.
- **Character arithmetic** with `ord()` and `chr()` converts between characters and code points: `ord("c") - ord("a")` is 2.
- **Normalisation** before comparing text: lowercasing (`casefold()` handles more languages than `lower()`), stripping whitespace, and Unicode normalisation (so `é` written as one code point equals `e` plus a combining accent).

## Worked examples

### Example 1: Bytes versus characters

```python
for word in ("cat", "café", "€5"):
    encoded = word.encode("utf-8")
    print(word, len(word), len(encoded), list(encoded))
```

Output:

```text
cat 3 3 [99, 97, 116]
café 4 5 [99, 97, 102, 195, 169]
€5 2 4 [226, 130, 172, 53]
```

`é` (U+00E9) becomes the two bytes 195 and 169, and `€` (U+20AC) becomes three bytes. ASCII letters keep their single-byte values, which is why UTF-8 and ASCII agree on plain English text.

### Example 2: Palindrome check with two pointers

```python
def is_palindrome(text):
    chars = [c.casefold() for c in text if c.isalnum()]
    left, right = 0, len(chars) - 1
    while left < right:
        if chars[left] != chars[right]:
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome("A man, a plan, a canal: Panama"))
print(is_palindrome("Data structures"))
```

Output:

```text
True
False
```

The function first normalises: it keeps letters and digits and folds case, so punctuation and spaces do not matter. The pointers then meet in the middle, comparing $n/2$ pairs: $\Theta(n)$ time, plus $\Theta(n)$ space for the cleaned list.

### Example 3: Anagram check by counting

```python
from collections import Counter

def is_anagram(a, b):
    clean = lambda s: [c for c in s.casefold() if c.isalpha()]
    return Counter(clean(a)) == Counter(clean(b))

print(is_anagram("Listen", "Silent"))
print(is_anagram("Dormitory", "Dirty room"))
print(is_anagram("Apple", "Paper"))
```

Output:

```text
True
True
False
```

Two strings are anagrams exactly when every letter appears the same number of times. Counting takes $\Theta(n)$, and comparing two counters takes time proportional to the number of distinct letters. Sorting both strings and comparing would also work but costs $\Theta(n \log n)$.

### Example 4: Reversing the order of words

```python
def reverse_words(sentence):
    return " ".join(reversed(sentence.split()))

print(reverse_words("  the quick   brown fox "))
```

Output:

```text
fox brown quick the
```

`split()` with no arguments splits on runs of whitespace and drops leading and trailing spaces, so the result is clean. The function builds a list of words, reverses it, and joins once: $\Theta(n)$ total. In a language with mutable character arrays, the same result is obtained in place by reversing the whole string and then reversing each word with two pointers.

## Applications

- **Web and data exchange.** HTTP, JSON, and HTML are exchanged as UTF-8 bytes; correct encoding and decoding is essential for international text.
- **Databases.** Column limits such as `VARCHAR(50)` may count bytes or characters depending on the system, which affects names in non-Latin scripts.
- **Search and natural language processing.** Tokenising, normalising, and counting words are the first steps of search engines and language models.
- **Security.** Input validation must handle encodings correctly; mismatched normalisation has caused real vulnerabilities in filters and URL parsers.
- **Logging and templating.** Building large text outputs efficiently relies on joining parts rather than repeated concatenation.

## Common mistakes

- **Building strings with `+=` in a loop,** which can be quadratic. Collect parts in a list and use `"".join(parts)`.
- **Assuming one character is one byte.** That holds only for ASCII; UTF-8 uses up to 4 bytes per code point.
- **Comparing text without normalising case or Unicode form,** so "Straße" and "STRASSE", or two encodings of "é", compare unequal.
- **Treating slicing as free.** `s[1:]` copies $n - 1$ characters; slicing inside a loop can add a hidden factor of $n$.
- **Decoding with the wrong encoding,** which produces garbled text such as "cafÃ©" when UTF-8 bytes are read as Latin-1.

## Revision notes

- Character = abstract symbol; code point = its Unicode number; encoding = how code points become bytes.
- ASCII: 1 byte, 128 characters. UTF-8: 1 to 4 bytes, ASCII-compatible, dominant on the web.
- Python `str` indexing and `len` are $\Theta(1)$; `.encode("utf-8")` gives bytes.
- Strings are immutable in Python and Java: every "modification" builds a new string.
- Build long strings with `"".join(...)` (or Java's `StringBuilder`), never repeated `+=`.
- Palindromes: two pointers. Anagrams: character counts. Word reversal: split, reverse, join.

## Practice questions

:::question basic
How many bytes does the string `"naïve"` occupy in UTF-8, and how many code points does it contain?
:::answer
It has 5 code points: n, a, ï, v, e. The letter ï (U+00EF) needs 2 bytes in UTF-8, and the other four are ASCII (1 byte each), so the total is $4 + 2 = 6$ bytes.
:::

:::question basic
Why is `"".join(parts)` preferred over `result += part` inside a loop?
:::answer
Strings are immutable, so each `+=` creates a new string and copies everything accumulated so far. Over many iterations the copying can grow quadratically with the final length. `join` first computes the total length, allocates the result once, and copies each part exactly once, which is linear in the total length.
:::

:::question intermediate
Write an expression that converts a lowercase letter `c` into its position in the alphabet (a = 0, b = 1, ..., z = 25), and another that converts a position `k` back into a letter.
:::answer
Position: `ord(c) - ord("a")`. Letter: `chr(k + ord("a"))`. This works because the lowercase letters have consecutive code points from 97 (`a`) to 122 (`z`). The same arithmetic underlies simple ciphers and array-of-26 counting.
:::

:::question intermediate
Describe a $\Theta(n)$ algorithm that finds the first character in a string that appears exactly once. What does it return for `"aabbcbd"`?
:::answer
Pass once over the string, counting each character in a dictionary. Then pass over the string again and return the first character whose count is 1. Both passes are $\Theta(n)$, and the dictionary holds at most one entry per distinct character. For `"aabbcbd"` the counts are a: 2, b: 3, c: 1, d: 1, so the answer is `"c"`. Note that the second pass must follow the string's order, not the dictionary's, to find the *first* such character.
:::

:::question intermediate
A text field must accept at most 255 bytes when stored. A user enters 200 Chinese characters. Will it fit in UTF-8? Explain.
:::answer
No. Common Chinese characters lie in the range U+0800 to U+FFFF, which UTF-8 encodes with 3 bytes each, so 200 characters need about 600 bytes, far more than 255. A limit expressed in bytes allows only 85 such characters. This is why systems should state whether limits count bytes or characters.
:::

:::question advanced
Explain why `s[::-1]` reverses a Python string correctly for most text, but may produce a visibly wrong result for some emoji or accented letters written with combining marks.
:::answer
`s[::-1]` reverses the sequence of code points. Some visible characters (grapheme clusters) consist of several code points, such as `e` followed by a combining acute accent, or an emoji followed by a skin-tone modifier. Reversing the code points puts the combining mark before its base character, so it attaches to the wrong character or displays on its own. Correct reversal of user-visible text must operate on grapheme clusters, which needs Unicode segmentation rules (for example the third-party `regex` module's `\X`).
:::

## Further learning

- **Next:** *Pattern Matching Basics* covers how to search for a pattern inside a long text, from the naive method to the linear-time KMP algorithm.
- **Related:** *Hash Functions & Collision Handling* explains how strings are hashed so they can be dictionary keys.
- **Related:** *Tries & Prefix Search* builds a tree of characters for fast prefix queries over many strings.
