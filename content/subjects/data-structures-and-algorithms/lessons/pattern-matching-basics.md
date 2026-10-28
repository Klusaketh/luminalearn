---
lesson: pattern-matching-basics
title: Pattern Matching Basics
summary: Find every occurrence of a pattern in a text, from the naive quadratic method to the linear-time Knuth-Morris-Pratt algorithm.
minutes: 55
type: theory
objectives:
  - Implement naive string matching and identify the inputs that make it take Theta(nm) time
  - Compute the prefix function (failure table) of a pattern by hand and in code
  - Explain how KMP uses the prefix function to avoid re-examining text characters, and why it runs in Theta(n + m)
  - Compare naive matching, KMP, and hashing-based matching for practical use
---

## Introduction

Searching for a word in a document, a gene sequence in a genome, or a signature in network traffic are all instances of the **string matching problem**: given a text $T$ of length $n$ and a pattern $P$ of length $m$, find every position where $P$ occurs in $T$.

The obvious approach tries every starting position and compares character by character. It is simple and often fast enough, but on repetitive inputs it degrades to $\Theta(nm)$ comparisons. The **Knuth-Morris-Pratt (KMP)** algorithm fixes this by precomputing, from the pattern alone, how far it can safely shift after a mismatch. It never moves backwards in the text, so it runs in $\Theta(n + m)$ time in every case.

**Before you start:** you should be comfortable with strings, arrays, and Big-O notation.

## Core theory

### Naive matching

For each shift $s$ from $0$ to $n - m$, compare $P[0..m-1]$ with $T[s..s+m-1]$ from left to right, stopping at the first mismatch.

- **Best and typical case:** mismatches happen early, so each shift costs a few comparisons and the total is close to $\Theta(n)$.
- **Worst case:** text `aaaa...a` and pattern `aaa...ab`. Every shift matches $m - 1$ characters before failing on the last, so the total is $(n - m + 1) \cdot m = \Theta(nm)$ comparisons.

The waste is that after a long partial match, the naive method slides the pattern by one and re-examines text characters it has already seen.

### Borders and the prefix function

A **border** of a string is a proper prefix that is also a suffix. For `abab`, the border `ab` is both a prefix and a suffix; `abcd` has no non-empty border.

The **prefix function** (also called the failure function) of the pattern is an array $\pi$ where

$$\pi[i] = \text{length of the longest proper prefix of } P[0..i] \text{ that is also a suffix of } P[0..i].$$

For $P = $ `ababaca`:

| $i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $P[i]$ | a | b | a | b | a | c | a |
| $\pi[i]$ | 0 | 0 | 1 | 2 | 3 | 0 | 1 |

At $i = 4$, the prefix `ababa` has border `aba` (length 3). At $i = 5$, `ababac` ends in `c`, which never starts the pattern, so its longest border is empty.

### Why borders tell you how far to shift

Suppose the first $q$ characters of the pattern have matched the text, and the next character mismatches. The last $q$ text characters equal $P[0..q-1]$. The next possible alignment that could still succeed must make some prefix of $P$ line up with a suffix of those $q$ characters, which means a prefix of $P$ that is also a suffix of $P[0..q-1]$: a border. The longest border, $\pi[q-1]$, gives the smallest safe shift. KMP therefore continues by assuming $\pi[q-1]$ characters already match, without moving back in the text.

### The KMP matcher

```text
q = 0                              # characters of P currently matched
for each text index i:
    while q > 0 and T[i] != P[q]:
        q = pi[q - 1]              # fall back to the longest border
    if T[i] == P[q]:
        q += 1
    if q == m:
        report a match ending at i (starting at i - m + 1)
        q = pi[q - 1]              # keep searching for overlapping matches
```

### Computing the prefix function

The prefix function is built by running the same idea on the pattern against itself, again in linear time:

```text
pi[0] = 0; k = 0
for i from 1 to m - 1:
    while k > 0 and P[i] != P[k]:
        k = pi[k - 1]
    if P[i] == P[k]:
        k += 1
    pi[i] = k
```

### Why KMP is linear

In the matcher, $q$ increases by at most 1 per text character, so over the whole text it increases at most $n$ times. Every iteration of the inner `while` loop strictly decreases $q$, and $q$ never goes below 0, so the total number of fall-backs is also at most $n$. Hence the matcher does $O(n)$ work. The same argument bounds the prefix-function computation by $O(m)$. Total: $\Theta(n + m)$ time and $\Theta(m)$ extra space for $\pi$.

### Other approaches

- **Rabin-Karp** compares a rolling hash of each text window with the hash of the pattern, checking characters only when hashes agree. Expected time is $O(n + m)$, and it extends naturally to searching for many patterns at once.
- **Boyer-Moore** compares from the right end of the pattern and can skip large chunks of text, making it sublinear on average for natural-language text. Variants of it are widely used in text editors and command-line search tools.
- **Library methods** such as Python's `str.find` and `in` use carefully tuned algorithms. For everyday code, use them; implement KMP when you need guaranteed linear time or the prefix function itself.

## Worked examples

### Example 1: Naive matching and its worst case

```python
def naive_search(text, pattern):
    n, m = len(text), len(pattern)
    matches, comparisons = [], 0
    for s in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[s + j] != pattern[j]:
                break
            j += 1
        if j == m:
            matches.append(s)
    return matches, comparisons

print(naive_search("abracadabra", "abra"))
print(naive_search("a" * 20, "aaab"))
```

Output:

```text
([0, 7], 16)
([], 68)
```

On ordinary text, most shifts fail on the first comparison: the 8 shifts over `abracadabra` cost $4 + 1 + 1 + 2 + 1 + 2 + 1 + 4 = 16$ comparisons, two of them full matches. On `aaaa...` with pattern `aaab`, each of the 17 shifts compares 4 characters before failing, giving 68 comparisons: the $\Theta(nm)$ behaviour.

### Example 2: Building the prefix function

```python
def prefix_function(pattern):
    pi = [0] * len(pattern)
    k = 0
    for i in range(1, len(pattern)):
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    return pi

print(prefix_function("ababaca"))
print(prefix_function("aabaaab"))
```

Output:

```text
[0, 0, 1, 2, 3, 0, 1]
[0, 1, 0, 1, 2, 2, 3]
```

Trace the second pattern at $i = 5$: before it, $k = 2$ (the border `aa` of `aabaa`). Now $P[5] = $ `a` but $P[2] = $ `b`, so fall back to $k = \pi[1] = 1$. Then $P[5] = $ `a` equals $P[1] = $ `a`, so $k = 2$ and $\pi[5] = 2$: the longest border of `aabaaa` is `aa`.

### Example 3: KMP finds all matches, including overlapping ones

```python
def kmp_search(text, pattern):
    pi = prefix_function(pattern)
    matches, q = [], 0
    for i, ch in enumerate(text):
        while q > 0 and ch != pattern[q]:
            q = pi[q - 1]
        if ch == pattern[q]:
            q += 1
        if q == len(pattern):
            matches.append(i - len(pattern) + 1)
            q = pi[q - 1]
    return matches

def prefix_function(pattern):
    pi = [0] * len(pattern)
    k = 0
    for i in range(1, len(pattern)):
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    return pi

print(kmp_search("abracadabra", "abra"))
print(kmp_search("aaaaa", "aa"))
print(kmp_search("ababcabababc", "ababc"))
```

Output:

```text
[0, 7]
[0, 1, 2, 3]
[0, 7]
```

After a full match, setting `q = pi[q - 1]` lets the next match reuse the overlapping border, so `"aa"` is found at every position of `"aaaaa"`. In the third text, after matching `abab` at position 5 and failing on the next character, KMP falls back to the border `ab` instead of restarting, and finds the match at position 7 without moving backwards in the text.

### Example 4: Tracing a mismatch by hand

Text `ababababca`, pattern `ababaca` with $\pi = [0, 0, 1, 2, 3, 0, 1]$:

1. Text positions 0 to 4 match `ababa`, so $q = 5$.
2. Text position 5 is `b`, but $P[5] = $ `c`: mismatch. Fall back to $q = \pi[4] = 3$, meaning `aba` is still matched (text positions 2 to 4).
3. Compare text position 5 (`b`) with $P[3] = $ `b`: match, $q = 4$.
4. Text position 6 is `a` = $P[4]$, so $q = 5$. Text position 7 is `b`, but $P[5] = $ `c`: mismatch, fall back to $q = 3$, then `b` matches $P[3]$, $q = 4$.
5. Text position 8 is `c`, but $P[4] = $ `a`: fall back to $q = \pi[3] = 2$; `c` versus $P[2] = $ `a`, fall back to $q = \pi[1] = 0$; `c` versus $P[0] = $ `a`, no match, $q = 0$.

The text index only ever moved forward; all the backtracking happened inside the pattern via $\pi$.

## Applications

- **Text editors and command-line tools** search files for patterns; efficient matching is what makes searching gigabytes feasible.
- **Bioinformatics** searches DNA (alphabet A, C, G, T) for motifs; the small alphabet makes repetitive, naive-unfriendly inputs common.
- **Intrusion detection systems** scan network packets for known attack signatures in real time, where guaranteed linear time matters.
- **Plagiarism and duplicate detection** uses rolling hashes (Rabin-Karp style) to find shared passages between documents.
- **Compilers and parsers** use related automata to recognise keywords and tokens.

## Common mistakes

- **Using a proper prefix that equals the whole string.** A border must be a proper prefix; otherwise $\pi[i]$ would always equal $i + 1$.
- **Forgetting to fall back after a full match,** which makes KMP miss overlapping occurrences.
- **Off-by-one in the starting index.** A match ending at text index $i$ starts at $i - m + 1$.
- **Assuming the inner `while` loop makes KMP quadratic.** The amortized argument shows the total number of fall-backs is at most $n$.
- **Hand-rolling KMP in production when the standard library suffices.** Use library search for ordinary tasks; KMP is valuable for guarantees and for learning.

## Revision notes

- Naive matching: $\Theta(nm)$ worst case (e.g. `aaa...` vs `aa...ab`), fast on typical text.
- Border = proper prefix that is also a suffix. $\pi[i]$ = longest border of $P[0..i]$.
- On a mismatch after $q$ matched characters, continue with $q = \pi[q-1]$; never move back in the text.
- After a full match, set $q = \pi[m-1]$ to find overlapping matches.
- KMP: $\Theta(n + m)$ time, $\Theta(m)$ space. Prefix function: $\Theta(m)$.
- Alternatives: Rabin-Karp (rolling hash, expected linear), Boyer-Moore (skips, fast on natural text).

## Practice questions

:::question basic
What is a border of a string? List all non-empty borders of `abcabcab`.
:::answer
A border is a proper prefix of a string that is also a suffix. For `abcabcab`, the borders are `ab` (prefix `ab`, suffix `ab`) and `abcab` (prefix `abcab`, suffix `abcab`). `abcabcab` itself is not a border because a border must be proper. So the longest border has length 5.
:::

:::question basic
Give an input for which naive matching performs about $nm$ comparisons, and explain why.
:::answer
Text `aaaaaaaaaa` (all `a`) and pattern `aaab`. At every shift the first three characters match and the fourth fails, so each of the $n - m + 1$ shifts costs $m$ comparisons, about $nm$ in total. The naive method forgets what it learned and re-reads the same text characters at every shift.
:::

:::question intermediate
Compute the prefix function of `abacabab`.
:::answer
$\pi = [0, 0, 1, 0, 1, 2, 3, 2]$. Working through it: `a` 0; `ab` 0; `aba` border `a` (1); `abac` 0; `abaca` border `a` (1); `abacab` border `ab` (2); `abacaba` border `aba` (3); `abacabab`: extending `aba` would need `c` but the character is `b`, so fall back to $\pi[2] = 1$ (`a`), then `ab` matches, giving 2.
:::

:::question intermediate
Using $\pi = [0, 0, 1, 2, 3, 0, 1]$ for the pattern `ababaca`, suppose 5 characters (`ababa`) have matched and the next text character mismatches. What value of $q$ does KMP continue with, and what does that mean?
:::answer
It continues with $q = \pi[4] = 3$. The last five text characters were `ababa`, and its longest border `aba` is both a suffix of what was matched and a prefix of the pattern. So KMP behaves as if the first three pattern characters already match the text and compares the same text character with $P[3]$, without re-reading any text.
:::

:::question intermediate
Why must KMP set `q = pi[q - 1]` after reporting a match, rather than `q = 0`?
:::answer
Setting `q = 0` would discard the overlap between consecutive matches. For text `aaaa` and pattern `aa`, the matches start at 0, 1, and 2. After the first match, the last character `a` is a border of the pattern, so the next match can start one position later. Falling back to $\pi[m-1]$ keeps that partial match and finds overlapping occurrences; resetting to 0 would find only the matches at 0 and 2.
:::

:::question advanced
Prove that the KMP matcher performs at most $2n$ character comparisons in total, regardless of the pattern.
:::answer
Sort the comparisons into two groups. (1) A comparison that fails while $q > 0$ triggers a fall-back that strictly decreases $q$. Since $q$ starts at 0, never goes negative, and increases by at most 1 per text character, its total decrease over the whole run is at most $n$, so there are at most $n$ such comparisons. (2) Every text character is finished by exactly one deciding comparison: either it succeeds (and $q$ grows by 1) or it fails with $q = 0$ (and the matcher moves on). That is exactly $n$ comparisons. Together, at most $2n$ comparisons are made, so the matcher is $O(n)$ no matter how repetitive the pattern is.
:::

## Further learning

- **Next:** *Singly & Doubly Linked Lists* moves from arrays and strings to pointer-based structures.
- **Related:** *Hash Functions & Collision Handling* explains the hashing ideas behind Rabin-Karp's rolling hash.
- **Related:** *Tries & Prefix Search* handles the case of many patterns or many prefix queries over a fixed dictionary.
