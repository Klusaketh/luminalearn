---
lesson: foundations-of-big-o-complexity
title: Foundations of Big-O Complexity
summary: Describe how an algorithm's running time grows with input size using Big-O, Big-Omega, and Big-Theta, and analyse real code with them.
minutes: 40
type: theory
objectives:
  - State the formal definitions of Big-O, Big-Omega, and Big-Theta and prove simple bounds with explicit constants
  - Separate the notation (upper, lower, tight bound) from the case being analysed (best, worst, average)
  - Derive the growth rate of loops, nested loops, and halving loops by counting operations
  - Rank common growth rates and use them to predict whether an algorithm is fast enough for a given input size
---

## Introduction

Two programs that solve the same problem can differ enormously in speed, and the gap usually widens as the input grows. Timing a program in seconds is a poor way to compare algorithms: the result depends on the processor, the language, the compiler, and whatever else the machine is doing. What stays the same across machines is the **shape of the growth**: whether doubling the input doubles the work, quadruples it, or barely changes it.

Asymptotic analysis captures that shape. It describes the running time $T(n)$ of an algorithm as a function of the input size $n$, ignores constant factors and small inputs, and keeps only the dominant term. The result is a short label such as $\Theta(n \log n)$ that tells you how an algorithm will scale long before you write or run it.

**Before you start:** you should be comfortable with exponents, logarithms, and summing simple series such as $1 + 2 + \dots + n$.

## Core theory

### Counting basic operations

We measure cost by counting **basic operations**: steps that take a constant amount of time regardless of $n$, such as an arithmetic operation, a comparison, an assignment, or an array access by index. The **input size** $n$ is whatever grows: the length of a list, the number of vertices in a graph, the number of digits in a number.

For example, summing a list of $n$ numbers performs one addition per element plus a little fixed setup, so $T(n) = an + b$ for some constants $a$ and $b$ that depend on the machine. Asymptotic notation lets us say "this grows linearly" without ever knowing $a$ and $b$.

### The three notations

Let $f(n)$ and $g(n)$ be functions from positive integers to non-negative reals.

**Big-O (asymptotic upper bound).** $f(n) = O(g(n))$ if there exist constants $c > 0$ and $n_0 \ge 1$ such that

$$0 \le f(n) \le c \cdot g(n) \quad \text{for all } n \ge n_0.$$

Beyond some point, $f$ never grows faster than a constant multiple of $g$.

**Big-Omega (asymptotic lower bound).** $f(n) = \Omega(g(n))$ if there exist $c > 0$ and $n_0 \ge 1$ such that

$$0 \le c \cdot g(n) \le f(n) \quad \text{for all } n \ge n_0.$$

Beyond some point, $f$ grows at least as fast as a constant multiple of $g$.

**Big-Theta (tight bound).** $f(n) = \Theta(g(n))$ if $f(n) = O(g(n))$ and $f(n) = \Omega(g(n))$. Equivalently, there are constants $c_1, c_2 > 0$ and $n_0$ with $c_1 g(n) \le f(n) \le c_2 g(n)$ for all $n \ge n_0$.

Two stricter relatives appear in proofs: $f(n) = o(g(n))$ means $f$ grows strictly slower, $\lim_{n\to\infty} f(n)/g(n) = 0$; and $f(n) = \omega(g(n))$ means strictly faster, with the limit infinite.

The "$=$" in $f(n) = O(g(n))$ is a convention, not equality. It reads "$f$ belongs to the set of functions bounded above by $g$". So $n = O(n^2)$ is true, but writing $O(n^2) = n$ makes no sense.

### Notation is not the same as case

This is the most common confusion in the topic. The notations describe **bounds on a function**. The **cases** (best, worst, average) describe **which inputs** the function is measured on. They are independent choices.

Consider linear search for a target in a list of $n$ items:

| Case | Input that causes it | Comparisons | Tight bound |
| :--- | :--- | :--- | :--- |
| Best | Target is the first item | 1 | $\Theta(1)$ |
| Worst | Target is absent | $n$ | $\Theta(n)$ |
| Average (target present, every position equally likely) | Random position | $(n+1)/2$ | $\Theta(n)$ |

Each row has its own tight bound. It is perfectly correct to say "the worst case is $\Omega(n)$" (it can be no better than linear) or "the best case is $O(1)$". When someone says "linear search is $O(n)$" without naming a case, they usually mean "on every input, the running time is at most linear", which is a statement about the worst case.

### Simplification rules

These follow directly from the definitions:

1. **Constant factors vanish:** $5n^2 = \Theta(n^2)$, and $\tfrac{n}{100} = \Theta(n)$.
2. **The dominant term wins:** $n^3 + 1000n^2 + 10^6 = \Theta(n^3)$, because the lower-order terms are eventually smaller than any fixed fraction of $n^3$.
3. **Sum rule:** if two parts run one after the other, $O(f) + O(g) = O(\max(f, g))$.
4. **Product rule:** if one part runs inside a loop that repeats another, $O(f) \cdot O(g) = O(f \cdot g)$.
5. **Logarithm bases do not matter:** $\log_a n = \frac{\log_b n}{\log_b a}$, so logs to different bases differ only by a constant factor. We write $\log n$.
6. **Exponential bases do matter:** $2^n$ and $3^n$ are not within a constant factor of each other, because $(3/2)^n$ is unbounded.

### The growth-rate ladder

From slowest-growing to fastest-growing:

| Growth | Name | Typical source |
| :--- | :--- | :--- |
| $1$ | constant | array indexing, hash table lookup (average) |
| $\log n$ | logarithmic | binary search, one step down a balanced tree per level |
| $n$ | linear | one pass over the input |
| $n \log n$ | linearithmic | merge sort, heap sort, efficient comparison sorting |
| $n^2$ | quadratic | all pairs of items, simple nested loops |
| $n^3$ | cubic | naive multiplication of two $n \times n$ matrices |
| $2^n$ | exponential | all subsets of a set |
| $n!$ | factorial | all orderings (permutations) of a set |

A useful rule of thumb: a modern computer performs roughly $10^8$ to $10^9$ simple operations per second. For $n = 10^6$, an $n \log n$ algorithm needs about $2 \times 10^7$ steps (a fraction of a second), while an $n^2$ algorithm needs $10^{12}$ steps (many minutes or hours).

### Reading growth rates from code

- **A loop of $n$ iterations** with constant work inside is $\Theta(n)$.
- **Two nested loops** of $n$ iterations each are $\Theta(n^2)$. If the inner loop's length depends on the outer index, add up the actual iteration counts.
- **A loop that halves (or doubles) its variable** runs about $\log_2 n$ times, so it is $\Theta(\log n)$.
- **Consecutive blocks** add, and the largest term dominates.
- **Library calls are not free.** `x in some_list` scans the list ($\Theta(n)$), while `x in some_set` is $\Theta(1)$ on average.

### Limitations

Asymptotic analysis deliberately hides constants, and sometimes those constants matter. An algorithm with a $\Theta(n^2)$ bound and tiny constants can beat a $\Theta(n \log n)$ algorithm for small inputs, which is why practical sorting libraries switch to insertion sort for short sub-arrays. It also ignores memory-hierarchy effects such as cache misses. Use asymptotics to rule out approaches that cannot scale, then measure to choose among the ones that can.

## Worked examples

### Example 1: Proving a Theta bound with explicit constants

**Claim:** $f(n) = 3n^2 + 5n + 2$ is $\Theta(n^2)$.

*Upper bound.* For $n \ge 1$ we have $n \le n^2$ and $1 \le n^2$, so

$$3n^2 + 5n + 2 \le 3n^2 + 5n^2 + 2n^2 = 10n^2.$$

Take $c = 10$ and $n_0 = 1$. Then $f(n) \le 10 n^2$ for all $n \ge 1$, so $f(n) = O(n^2)$.

*Lower bound.* Every term is non-negative, so $3n^2 + 5n + 2 \ge 3n^2$ for all $n \ge 1$. Take $c = 3$, $n_0 = 1$. So $f(n) = \Omega(n^2)$.

Both bounds hold, therefore $f(n) = \Theta(n^2)$. The constants are not unique: any valid choice proves the claim.

### Example 2: A nested loop whose inner length changes

```python
def count_pairs(n: int) -> int:
    steps = 0
    for i in range(n):
        for j in range(i, n):  # inner loop runs n - i times
            steps += 1
    return steps

for n in (4, 10, 100):
    print(n, count_pairs(n), n * (n + 1) // 2)
```

Output:

```text
4 10 10
10 55 55
100 5050 5050
```

The inner loop runs $n, n-1, \dots, 1$ times as $i$ goes from $0$ to $n-1$. The total is

$$\sum_{i=0}^{n-1} (n - i) = n + (n-1) + \dots + 1 = \frac{n(n+1)}{2} = \frac{n^2}{2} + \frac{n}{2}.$$

The dominant term is $\tfrac{1}{2}n^2$, so the loop is $\Theta(n^2)$. The program confirms the exact count matches the formula. Halving the work compared with a full $n \times n$ grid changes only the constant, not the growth rate.

### Example 3: A halving loop

```python
def halvings(n: int) -> int:
    count = 0
    while n > 1:
        n //= 2
        count += 1
    return count

for n in (8, 1000, 1024, 1_000_000):
    print(n, halvings(n))
```

Output:

```text
8 3
1000 9
1024 10
1000000 19
```

Each iteration halves $n$ (rounding down), so after $k$ iterations the value is at most $n / 2^k$. The loop stops once that reaches 1, which takes $\lfloor \log_2 n \rfloor$ iterations. A million needs only 19 steps: this is why logarithmic algorithms such as binary search scale so well.

### Example 4: Analysing a whole function

```python
def has_duplicate(items: list[int]) -> bool:
    seen = set()            # O(1)
    for x in items:         # n iterations
        if x in seen:       # O(1) on average for a set
            return True
        seen.add(x)         # O(1) on average
    return False
```

The loop runs at most $n$ times with average constant work per iteration, so the worst case (no duplicates) is $\Theta(n)$ time. It also stores up to $n$ items, so it uses $\Theta(n)$ extra space.

Had `seen` been a list, `x in seen` would scan up to $i$ items on iteration $i$, giving $1 + 2 + \dots + n = \Theta(n^2)$ time. Changing one data structure changes the growth rate, which is exactly what asymptotic analysis lets you see.

## Applications

- **Choosing an approach before coding.** If $n$ can reach $10^6$, quadratic algorithms are ruled out immediately; you look for $O(n \log n)$ or better.
- **Comparing library operations.** Knowing that inserting at the front of a Python list is $\Theta(n)$ while appending is amortized $\Theta(1)$ (and that a `collections.deque` gives $\Theta(1)$ at both ends) guides everyday coding decisions.
- **Database and search systems.** An index turns a $\Theta(n)$ table scan into an $O(\log n)$ B+ tree lookup; this is why indexed queries stay fast as tables grow to millions of rows.
- **Capacity planning.** If a nightly job is $\Theta(n \log n)$ and the data doubles, you can predict it will take a little more than twice as long, rather than four times.
- **Technical interviews and examinations,** which routinely ask for the time and space complexity of a proposed solution and a justification.

## Common mistakes

- **Treating Big-O as "worst case" and Big-Omega as "best case".** The notations are bounds; the cases are inputs. "The best case of quicksort is $\Theta(n \log n)$" mixes a case with a tight bound, and is perfectly meaningful.
- **Calling a bound "the complexity" when it is not tight.** Merge sort is $O(n^3)$ as well, because that is a valid (but useless) upper bound. When asked for the complexity, give a tight bound.
- **Adding nested loops instead of multiplying.** Two nested loops of $n$ iterations are $n \times n$, not $n + n$.
- **Dropping a second input variable.** A loop over $n$ rows and $m$ columns is $\Theta(nm)$. It is not $\Theta(n)$ unless $m$ is a constant.
- **Ignoring hidden loops in library calls,** such as `list.index`, `in` on a list, slicing, or concatenating strings inside a loop.
- **Assuming a better bound means faster for every input.** For small $n$, constant factors can make the "worse" algorithm faster in practice.

## Revision notes

- $O$ = upper bound, $\Omega$ = lower bound, $\Theta$ = both (tight). Definitions need constants $c$ and $n_0$.
- Best, worst, and average case are separate from the notation; each case has its own bound.
- Drop constant factors and lower-order terms. Log bases do not matter; exponential bases do.
- Sequence: add, keep the largest. Nesting: multiply.
- Halving or doubling loops are $\Theta(\log n)$. A full nested loop is $\Theta(n^2)$; a triangular one ($j$ from $i$ to $n$) is still $\Theta(n^2)$.
- Ladder: $1 < \log n < n < n\log n < n^2 < n^3 < 2^n < n!$.
- Rough capacity: about $10^8$ simple operations per second.

## Practice questions

:::question basic
Simplify each to a tight bound: (a) $7n^3 + 2n^2 + 100$, (b) $20n + 3\log n$, (c) $4 \cdot 2^n + n^5$.
:::answer
(a) $\Theta(n^3)$: the cubic term dominates. (b) $\Theta(n)$: $\log n$ grows more slowly than $n$. (c) $\Theta(2^n)$: any exponential with base greater than 1 eventually exceeds any polynomial, so $n^5$ is the lower-order term.
:::

:::question basic
Is $n^2 = O(n^3)$ true? Is $n^3 = O(n^2)$ true? Explain each.
:::answer
$n^2 = O(n^3)$ is true: $n^2 \le 1 \cdot n^3$ for all $n \ge 1$, so $c = 1$, $n_0 = 1$ work. $n^3 = O(n^2)$ is false: it would require $n^3 \le c\,n^2$, that is $n \le c$, for all large $n$, which fails once $n > c$ no matter which constant you choose.
:::

:::question intermediate
Prove that $f(n) = 2n^2 - 3n$ is $\Omega(n^2)$ by giving explicit constants $c$ and $n_0$.
:::answer
We need $c\,n^2 \le 2n^2 - 3n$ for large $n$. Try $c = 1$: we need $n^2 \le 2n^2 - 3n$, which rearranges to $3n \le n^2$, that is $n \ge 3$. So $c = 1$ and $n_0 = 3$ work. (Any $c < 2$ works with a large enough $n_0$; $c = 2$ never works because of the $-3n$ term.)
:::

:::question intermediate
What is the time complexity of this code, and why?

```python
i = 1
while i < n:
    for j in range(n):
        print(i, j)
    i *= 2
```
:::answer
$\Theta(n \log n)$. The outer loop doubles `i`, so it runs about $\log_2 n$ times. Each outer iteration runs the inner loop exactly $n$ times. Multiplying gives $n \log n$ print calls. Note that the inner loop does not depend on `i`, unlike Example 2.
:::

:::question intermediate
A function calls `items.index(x)` once for each of the $n$ elements `x` of a Python list `items`. What is its time complexity, and how could you make it linear?
:::answer
`list.index` scans from the start until it finds `x`, which costs up to $i$ steps for the $i$-th element, so the total is $\Theta(n^2)$ in the worst case. To make it linear, build a dictionary that maps each value to its index in one pass (`pos = {v: i for i, v in enumerate(items)}`), then each lookup is $\Theta(1)$ on average, giving $\Theta(n)$ overall at the cost of $\Theta(n)$ extra space.
:::

:::question advanced
Algorithm A takes $100\,n \log_2 n$ steps and algorithm B takes $n^2$ steps. For which input sizes is B faster? Use whole numbers and show your reasoning.
:::answer
B is faster while $n^2 < 100\,n\log_2 n$, that is $n < 100 \log_2 n$. Check values: at $n = 900$, $100\log_2 900 \approx 100 \times 9.81 = 981 > 900$, so B is still faster. At $n = 1000$, $100 \log_2 1000 \approx 996.6 < 1000$, so A is faster. The crossover lies between 996 and 997 ($100 \log_2 996 \approx 996.0$), so B is faster for roughly $n \le 996$ and A wins beyond that. This is why asymptotic bounds predict behaviour for large inputs but not small ones.
:::

:::question advanced
Is it true that if $f(n) = O(g(n))$ then $2^{f(n)} = O(2^{g(n)})$? Prove it or give a counterexample.
:::answer
False. Take $f(n) = 2n$ and $g(n) = n$. Then $f(n) = O(g(n))$ with $c = 2$. But $2^{f(n)} = 4^n$ and $2^{g(n)} = 2^n$, and $4^n / 2^n = 2^n$ is unbounded, so $4^n \ne O(2^n)$. Constant factors inside an exponent become exponential factors outside it.
:::

## Further learning

- **Next:** *Space Complexity & Memory Trade-offs* applies the same notation to memory, and *Amortized Analysis* explains why appending to a dynamic array is $O(1)$ on average even though an occasional append is expensive.
- **Later:** *Call Stack & Recurrence Trees* covers recurrences such as $T(n) = 2T(n/2) + n$ and the Master Theorem, which you need for recursive algorithms like merge sort.
- **Related:** *Binary Search & Invariants* is the canonical logarithmic-time algorithm and shows the halving pattern from Example 3 in action.
