---
lesson: memoization-vs-tabulation
title: Memoization vs Tabulation
summary: Turn exponential recursions into polynomial algorithms by solving each subproblem once, either top-down with a cache or bottom-up with a table, and choose between the two.
minutes: 60
type: theory
objectives:
  - Identify overlapping subproblems and optimal substructure, the two conditions for dynamic programming
  - Convert an exponential recursive solution into a memoized top-down solution
  - Build a bottom-up table in a valid dependency order, recover a solution from it, and reduce its memory
  - Compare memoization and tabulation by evaluation order, memory use, recursion depth, and the subproblems each one solves
---

## Introduction

The naive recursive Fibonacci function makes more than 2.6 million calls to compute $F(30)$, although there are only 31 different values it could ever be asked for. It recomputes $F(28)$ twice, $F(27)$ three times, $F(26)$ five times, and so on, repeating the same work over and over. **Dynamic programming (DP)** is the technique of solving each distinct subproblem **once**, storing its answer, and reusing it. Applied to Fibonacci, it turns exponential time into linear time.

There are two ways to organise the reuse. **Memoization** keeps the natural recursive solution and adds a cache: before computing a subproblem, check whether its answer is already known. **Tabulation** abandons recursion and fills a table of answers from the smallest subproblems upwards, so that every value a cell needs is already there when the cell is computed. Both give the same answers with the same asymptotic time; they differ in which subproblems they touch, how much memory and stack they use, and how easy they are to optimise. Dynamic programming powers algorithms for sequence alignment in biology, spell checking, route planning, and resource allocation.

**Before you start:** you should know recursion, recursion trees, and dictionaries.

## Core theory

### When dynamic programming applies

A problem is a candidate for dynamic programming when it has:

- **Optimal substructure:** an optimal (or complete) answer can be built from the answers to smaller subproblems of the same kind.
- **Overlapping subproblems:** a straightforward recursion meets the same subproblems many times.

If the subproblems do not overlap, as in merge sort, where every subarray is sorted exactly once, caching gains nothing; that is plain divide and conquer.

### Designing a DP solution

1. **Define the state:** what a subproblem is, and what its value means, in one precise sentence (for example, "$P(r, c)$ is the number of paths from the top-left cell to cell $(r, c)$").
2. **Write the recurrence:** how a state's value follows from smaller states.
3. **Fix the base cases.**
4. **Choose an evaluation order** (for tabulation) in which every state comes after the states it depends on.
5. **Read off the answer,** and if needed, reconstruct the choices that produced it.

The running time is the **number of states times the work per state**. Fibonacci has $n + 1$ states and $O(1)$ work each: $\Theta(n)$. A two-string problem over prefixes has $(m + 1)(n + 1)$ states: $\Theta(mn)$.

### Memoization (top-down)

Write the recursion exactly as the recurrence says, and store each result in a dictionary or array the first time it is computed. In Python, `functools.lru_cache(maxsize=None)` (or `functools.cache`) does this with one line.

- It computes only the states that are actually **reachable** from the original question.
- It is easy to write: correctness follows directly from the recurrence, and no evaluation order needs to be worked out.
- It has recursion overhead and can be **too deep** for long chains of states (CPython's default limit is about 1000 frames).

### Tabulation (bottom-up)

Allocate a table indexed by state, fill in the base cases, and loop over the states in dependency order.

- No recursion, so no depth limit and less overhead per state.
- It computes **every** state in the table, whether or not the final answer needs it.
- The explicit order makes **space optimisation** possible: if each row depends only on the previous row, keep two rows (or one) instead of the whole table.

| | Memoization | Tabulation |
| :--- | :--- | :--- |
| Direction | top-down, from the question to the base cases | bottom-up, from the base cases to the question |
| States computed | only those reachable | all states in the table |
| Order of evaluation | implicit, decided by the recursion | explicit; you must choose a valid order |
| Stack usage | proportional to the longest dependency chain | none |
| Space optimisation | difficult | natural (rolling rows) |
| Typical use | sparse or irregular state spaces, quick prototypes | dense tables, performance-critical code |

### Reconstructing the solution

A DP table usually stores only values, such as lengths, counts, or costs. To recover the actual solution (which items, which path, which characters), either record the choice made at each state, or **walk backwards** from the final state, at each step asking which option of the recurrence produced the stored value.

## Worked examples

### Example 1: Fibonacci three ways

```python
from functools import lru_cache

calls = 0

def fib_naive(n):
    global calls
    calls += 1
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)

@lru_cache(maxsize=None)
def fib_memo(n):                     # top-down: the same recursion, with a cache
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)

def fib_table(n):                    # bottom-up, keeping only the last two values
    if n < 2:
        return n
    prev, curr = 0, 1                # F(0), F(1)
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr

print(fib_naive(30), "naive calls:", calls)
print(fib_memo(30), fib_memo.cache_info())
print(fib_table(30), fib_table(300))
```

Output:

```text
832040 naive calls: 2692537
832040 CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)
832040 222232244629420445529739893461909967206666939096499764990979600
```

The naive version makes 2,692,537 calls. The memoized version computes each of the 31 values $F(0)$ to $F(30)$ once (31 misses); the other 28 calls are answered from the cache. The tabulated version needs no cache at all: $F(i)$ depends only on $F(i - 1)$ and $F(i - 2)$, so two variables replace the whole table, giving $\Theta(n)$ time and $O(1)$ space. It computes $F(300)$ instantly, a call the naive version could never finish and the memoized version would make 300 frames deep.

### Example 2: Counting paths in a grid

Count the paths from the top-left to the bottom-right cell of a grid, moving only right or down and avoiding walls (`#`). The state is a cell, and $P(r, c) = P(r - 1, c) + P(r, c - 1)$, because the last step into $(r, c)$ comes from above or from the left.

```python
from functools import lru_cache

grid = ["....",
        ".#..",
        "...#",
        "...."]
rows, cols = len(grid), len(grid[0])

@lru_cache(maxsize=None)
def paths(r, c):                     # top-down: paths from (0, 0) to (r, c)
    if r < 0 or c < 0 or grid[r][c] == "#":
        return 0
    if r == 0 and c == 0:
        return 1
    return paths(r - 1, c) + paths(r, c - 1)

def paths_table():                   # bottom-up: row by row, left to right
    dp = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#":
                continue
            if r == 0 and c == 0:
                dp[r][c] = 1
            else:
                dp[r][c] = (dp[r - 1][c] if r > 0 else 0) + (dp[r][c - 1] if c > 0 else 0)
    return dp

def paths_one_row():                 # the same order, keeping a single row
    dp = [0] * cols
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#":
                dp[c] = 0
            elif r == 0 and c == 0:
                dp[c] = 1
            elif c > 0:
                dp[c] += dp[c - 1]   # dp[c] still holds the value from the row above
    return dp[-1]

print("top-down:", paths(rows - 1, cols - 1))
for row in paths_table():
    print(row)
print("one row:", paths_one_row())
```

Output:

```text
top-down: 4
[1, 1, 1, 1]
[1, 0, 1, 2]
[1, 1, 2, 0]
[1, 2, 4, 4]
one row: 4
```

The table shows the number of paths into every cell; walls hold 0, and each other cell is the sum of the cell above and the cell to the left. Row-by-row order is valid because both dependencies are filled before the cell that needs them. Since each row uses only the row above, a single array of length `cols` suffices: before `dp[c]` is updated it still holds the value from the previous row, and `dp[c - 1]` already holds the current row's value.

### Example 3: Longest common subsequence, with reconstruction

A **subsequence** keeps characters in order but may skip some. The state $L(i, j)$ is the length of the longest common subsequence of the first $i$ characters of `a` and the first $j$ characters of `b`:

$$L(i, j) = \begin{cases} L(i-1, j-1) + 1 & \text{if } a_i = b_j \\ \max(L(i-1, j),\, L(i, j-1)) & \text{otherwise} \end{cases}$$

with $L(i, 0) = L(0, j) = 0$.

```python
def lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    out, i, j = [], m, n             # walk back from the last cell to recover one LCS
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return dp, "".join(reversed(out))

a, b = "ABCBDAB", "BDCABA"
dp, sequence = lcs(a, b)
print("    " + "  ".join(b))
for i in range(1, len(a) + 1):
    print(a[i - 1], " ".join(f"{v:2}" for v in dp[i][1:]))
print("length", dp[-1][-1], "LCS", sequence)
```

Output:

```text
    B  D  C  A  B  A
A  0  0  0  1  1  1
B  1  1  1  1  2  2
C  1  1  2  2  2  2
B  1  1  2  2  3  3
D  1  2  2  2  3  3
A  1  2  2  3  3  4
B  1  2  2  3  4  4
length 4 LCS BCBA
```

The table has $(7 + 1)(6 + 1) = 56$ states, each computed in constant time, so the algorithm is $\Theta(mn)$, whereas checking all $2^7$ subsequences of `a` against `b` would be exponential. The walk back starts at the bottom-right cell: where the characters match, it records the character and moves diagonally; otherwise it moves towards the neighbour that holds the same value. The result, BCBA, is one of several longest common subsequences; for example, BDAB also has length 4.

## Applications

- **Text comparison:** `diff` tools and version control systems compute line-level longest common subsequences to show changes between files.
- **Bioinformatics:** sequence alignment algorithms such as Needleman-Wunsch and Smith-Waterman are table-based DP over two sequences.
- **Spell checking and fuzzy search:** edit distance (Levenshtein distance) is a two-string DP that measures how many edits turn one word into another.
- **Optimisation problems:** knapsack, shortest paths (Bellman-Ford is a DP over the number of edges), and resource scheduling.
- **Parsing and language processing:** the CYK parsing algorithm and the Viterbi algorithm for hidden Markov models fill DP tables.

## Common mistakes

- **Vague state definitions.** If you cannot say in one sentence what `dp[i][j]` means, the recurrence and base cases are likely to be wrong.
- **Filling the table in an invalid order,** so that a cell reads a neighbour that has not been computed yet and silently uses 0.
- **Memoizing on mutable or unhashable arguments,** such as lists, which `lru_cache` rejects, or caching on a value that does not capture the whole state.
- **Hitting the recursion limit** with memoization on long chains of states; switch to tabulation or reduce the depth.
- **Overwriting values still needed** when compressing a table to one row; check which old values each update reads, and iterate in a direction that preserves them.
- **Using DP when subproblems do not overlap,** which adds memory and overhead for no gain.

## Revision notes

- DP = optimal substructure + overlapping subproblems. Solve each distinct state once.
- Time = number of states × work per state. Fibonacci: $\Theta(n)$. Two strings: $\Theta(mn)$.
- Memoization: recursion plus a cache; computes only reachable states; uses stack depth.
- Tabulation: loops in dependency order; computes every state; no recursion; easy to compress.
- Space optimisation: if row $i$ needs only row $i - 1$, keep one or two rows.
- Reconstruction: walk back from the final state, asking which case of the recurrence produced each value.

## Practice questions

:::question basic
What two properties must a problem have for dynamic programming to help, and which one does merge sort lack?
:::answer
Optimal substructure (an answer can be built from answers to smaller instances of the same problem) and overlapping subproblems (the same smaller instances are needed again and again). Merge sort has optimal substructure, but each subarray is sorted exactly once, so its subproblems do not overlap and caching would save nothing.
:::

:::question basic
How many distinct subproblems does `fib_memo(n)` solve, and what is its running time?
:::answer
It solves $n + 1$ distinct subproblems, $F(0)$ through $F(n)$, each once, with $O(1)$ work apart from the recursive calls, which are answered from the cache after the first time. The running time is $\Theta(n)$, compared with exponential time for the naive recursion.
:::

:::question intermediate
You can climb a staircase one or two steps at a time. Define a DP state and recurrence for the number of ways to reach step $n$, and compute it for $n = 5$.
:::answer
Let $W(i)$ be the number of ways to reach step $i$. The last move into step $i$ came from step $i - 1$ or step $i - 2$, so $W(i) = W(i - 1) + W(i - 2)$, with $W(0) = 1$ (do nothing) and $W(1) = 1$. Then $W(2) = 2$, $W(3) = 3$, $W(4) = 5$, and $W(5) = 8$. It is the Fibonacci recurrence with shifted indices.
:::

:::question intermediate
Give a situation where memoization solves far fewer subproblems than tabulation would.
:::answer
When only a small part of the state space is reachable from the question. For example, a function $f(n)$ that recurses only to $f(n / 2)$ and $f(n / 3)$ (with integer division) touches only about $O(\log^2 n)$ distinct values below $n$, so memoization computes a handful of states, while a table indexed from 0 to $n$ would compute all $n + 1$ entries. For $n = 10^{12}$, tabulation is impossible but memoization is instant.
:::

:::question intermediate
Fill the LCS table for `a = "AB"` and `b = "BA"`. What is the LCS length, and which subsequences achieve it?
:::answer
With rows for "A" and "B" and columns for "B" and "A": $L(1,1) = 0$ (A vs B), $L(1,2) = 1$ (A matches A), $L(2,1) = 1$ (B matches B), and $L(2,2) = \max(L(1,2), L(2,1)) = 1$, because the last characters B and A differ. The length is 1, achieved by both "A" and "B"; "AB" is not common because the letters appear in opposite orders.
:::

:::question advanced
The edit distance between two strings is the minimum number of single-character insertions, deletions, and substitutions that turn one into the other. Write the DP recurrence and give the edit distance between "kitten" and "sitting".
:::answer
Let $E(i, j)$ be the edit distance between the first $i$ characters of `a` and the first $j$ characters of `b`. Then $E(i, 0) = i$, $E(0, j) = j$, and $E(i, j) = \min(E(i-1, j) + 1,\; E(i, j-1) + 1,\; E(i-1, j-1) + [a_i \ne b_j])$, covering deletion, insertion, and substitution (free when the characters match). For "kitten" and "sitting", the distance is 3: substitute k with s, substitute e with i, and insert g at the end. The table has $7 \times 8$ states, so the computation is $\Theta(mn)$.
:::

:::question advanced
The single-row grid DP in Example 2 updates `dp[c] += dp[c - 1]` from left to right. Why is left to right the correct direction here, and what would go wrong if it ran right to left?
:::answer
The cell $(r, c)$ needs the value above it, $(r - 1, c)$, and the value to its left, $(r, c - 1)$. Just before `dp[c]` is updated, it still holds row $r - 1$'s value, which is the "above" value, and moving left to right means `dp[c - 1]` has already been updated to row $r$'s value, which is the "left" value. Running right to left, `dp[c - 1]` would still hold row $r - 1$'s value when `dp[c]` reads it, so each cell would add the wrong neighbour (the cell diagonally up and to the left) and the counts would be incorrect.
:::

## Further learning

- **Next:** *0/1 Knapsack Problem* applies tabulation and one-row space optimisation to a classic optimisation problem.
- **Related:** *Call Stack & Recurrence Trees* explains why the naive recursion is exponential and how deep the memoized recursion goes.
- **Related:** *Greedy Choice & Optimal Substructure* contrasts DP with greedy algorithms, which make one choice per step without comparing alternatives.
