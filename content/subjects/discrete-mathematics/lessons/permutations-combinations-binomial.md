---
lesson: permutations-combinations-binomial
title: Permutations, Combinations & the Binomial Theorem
summary: Counting arrangements and selections: permutations and combinations with and without repetition, arrangements of multisets, Pascal's identity, and the binomial theorem.
minutes: 45
type: theory
objectives:
  - Decide whether order matters and whether repetition is allowed, and apply the matching formula
  - Count arrangements of words with repeated letters and selections with repetition (stars and bars)
  - Expand expressions with the binomial theorem and prove identities such as Pascal's rule combinatorially
review: ai-draft
---
## Introduction

Choosing a team, arranging books on a shelf, forming passwords, and dealing card hands are all counting problems that hinge on two questions: **does order matter?** and **may items repeat?** The four answers lead to four formulas that cover a huge range of problems. The numbers that count selections, the binomial coefficients, also appear when expanding $(x + y)^n$, in probability, and throughout the analysis of algorithms.

**Before you start:** you should know the sum and product rules and factorial notation.

## Core theory

### Permutations: order matters

A **permutation** is an ordered arrangement. The number of ways to arrange all $n$ distinct objects is $n! = n(n-1)\cdots 1$, with $0! = 1$. The number of ordered arrangements of $r$ objects chosen from $n$ distinct objects, an **r-permutation**, is

$$P(n, r) = n(n-1)\cdots(n - r + 1) = \frac{n!}{(n - r)!}$$

by the product rule: $n$ choices for the first position, $n - 1$ for the second, and so on.

### Combinations: order does not matter

A **combination** is an unordered selection. Every set of $r$ objects can be ordered in $r!$ ways, so by the division rule

$$C(n, r) = \binom{n}{r} = \frac{n!}{r!(n - r)!} = \frac{P(n, r)}{r!}$$

Symmetry: $\binom{n}{r} = \binom{n}{n - r}$, since choosing which $r$ to take is the same as choosing which $n - r$ to leave.

### With repetition

| | Order matters | Order does not matter |
| :--- | :--- | :--- |
| No repetition | $P(n, r) = \dfrac{n!}{(n - r)!}$ | $\dbinom{n}{r}$ |
| Repetition allowed | $n^r$ | $\dbinom{n + r - 1}{r}$ |

The bottom-right formula, choosing $r$ items from $n$ types with repetition, comes from **stars and bars**: represent a selection as $r$ stars separated by $n - 1$ bars into $n$ groups; each arrangement of $r + n - 1$ symbols with $n - 1$ bars is one selection. It also counts the non-negative integer solutions of $x_1 + \cdots + x_n = r$.

### Arrangements with repeated objects

The number of distinct arrangements of $n$ objects where there are $n_1$ identical objects of type 1, $n_2$ of type 2, and so on, is the **multinomial coefficient**

$$\frac{n!}{n_1!\, n_2! \cdots n_k!}$$

because swapping identical objects does not create a new arrangement. For example, "LEVEL" has $5!/(2!\,2!\,1!) = 30$ distinct arrangements.

### Pascal's identity and the binomial theorem

**Pascal's identity:** $\binom{n}{k} = \binom{n - 1}{k - 1} + \binom{n - 1}{k}$. Combinatorial proof: fix one particular object; a $k$-subset either contains it (choose the other $k - 1$ from $n - 1$) or does not (choose all $k$ from $n - 1$). This generates **Pascal's triangle**.

The **binomial theorem**:

$$(x + y)^n = \sum_{k=0}^{n} \binom{n}{k} x^{n-k} y^k$$

because each term of the expanded product picks $x$ or $y$ from each of the $n$ factors, and $\binom{n}{k}$ ways choose which $k$ factors contribute $y$. Setting $x = y = 1$ gives $\sum_k \binom{n}{k} = 2^n$, the number of subsets of an $n$-set; setting $x = 1, y = -1$ shows that the alternating sum is 0.

## Worked examples

### Example 1: Choosing the right formula

1. A club of 12 members elects a president, secretary, and treasurer (different people): order matters, no repetition, $P(12, 3) = 12 \times 11 \times 10 = 1320$.
2. The same club chooses a 3-person committee: order does not matter, $\binom{12}{3} = 220$. Note $1320 / 3! = 220$.
3. A 4-digit PIN: order matters, repetition allowed, $10^4 = 10{,}000$.
4. Buying 6 doughnuts from 4 flavours: unordered with repetition, $\binom{4 + 6 - 1}{6} = \binom{9}{6} = 84$.
5. Arrangements of "MISSISSIPPI" (1 M, 4 I, 4 S, 2 P): $\frac{11!}{1!\,4!\,4!\,2!} = 34{,}650$.

```python
from math import comb, factorial, perm
from itertools import combinations_with_replacement, permutations

print(perm(12, 3), comb(12, 3), 10**4, comb(9, 6))
print(factorial(11) // (factorial(4) * factorial(4) * factorial(2)))
print(len(list(combinations_with_replacement("ABCD", 6))))
print(len(set(permutations("LEVEL"))))
```

Output:

```text
1320 220 10000 84
34650
84
30
```

The brute-force checks agree with the formulas: enumerating all 6-doughnut selections gives 84, and the distinct orderings of "LEVEL" number 30.

### Example 2: Binomial expansions and coefficients

Expand $(2a - b)^4$ and find the coefficient of $x^3$ in $(1 + 2x)^7$.

With $x = 2a$, $y = -b$, $n = 4$:

$$(2a - b)^4 = \binom{4}{0}(2a)^4 + \binom{4}{1}(2a)^3(-b) + \binom{4}{2}(2a)^2 b^2 + \binom{4}{3}(2a)(-b)^3 + \binom{4}{4} b^4$$

$$= 16a^4 - 32a^3 b + 24a^2 b^2 - 8ab^3 + b^4$$

For $(1 + 2x)^7$, the $x^3$ term is $\binom{7}{3} \cdot 1^4 \cdot (2x)^3 = 35 \times 8\, x^3 = 280x^3$.

```python
from math import comb
print([comb(4, k) * 2**(4 - k) * (-1)**k for k in range(5)])
print(comb(7, 3) * 2**3)
print([comb(6, k) for k in range(7)], sum(comb(6, k) for k in range(7)))
```

Output:

```text
[16, -32, 24, -8, 1]
280
[1, 6, 15, 20, 15, 6, 1] 64
```

The list gives the coefficients of $a^4, a^3 b, \dots, b^4$. Row 6 of Pascal's triangle sums to $2^6 = 64$.

## Applications

- **Probability:** card hands, lottery odds, and binomial distributions use $\binom{n}{k}$.
- **Algorithms:** the number of subsets or orderings bounds brute-force search.
- **Combinatorial identities:** simplify sums in complexity analysis.
- **Coding theory:** counting bit strings of a given weight uses binomial coefficients.

## Common mistakes

- **Using permutations when order does not matter.** Committees and hands are combinations.
- **Forgetting repetition.** PINs and passwords usually allow repeated characters.
- **Over-counting identical objects.** Divide by the factorials of repeated counts.
- **Misapplying stars and bars.** It counts unordered selections with repetition: $\binom{n + r - 1}{r}$, with $n$ types and $r$ items.
- **Losing signs in binomial expansions.** Keep $y = -b$ and raise it to each power.

## Revision notes

- Ordered, no repetition: $P(n, r) = n!/(n - r)!$; all $n$: $n!$.
- Unordered, no repetition: $\binom{n}{r} = n!/(r!(n - r)!)$; $\binom{n}{r} = \binom{n}{n - r}$.
- Ordered with repetition: $n^r$; unordered with repetition: $\binom{n + r - 1}{r}$.
- Multiset arrangements: $n!/(n_1! \cdots n_k!)$.
- Pascal: $\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}$.
- $(x + y)^n = \sum_k \binom{n}{k} x^{n-k} y^k$; $\sum_k \binom{n}{k} = 2^n$.

## Practice questions

:::question basic
How many ways can 5 different books be arranged on a shelf? How many ways can 3 of them be chosen to take on a trip?
:::answer
Arranging all 5 in order: $5! = 120$. Choosing 3 without regard to order: $\binom{5}{3} = 10$.
:::

:::question basic
How many 5-card hands can be dealt from a standard 52-card deck?
:::answer
A hand is an unordered selection without repetition: $\binom{52}{5} = 2{,}598{,}960$.
:::

:::question intermediate
How many non-negative integer solutions does $x_1 + x_2 + x_3 = 10$ have?
:::answer
By stars and bars, distributing 10 identical units among 3 variables gives $\binom{10 + 3 - 1}{3 - 1} = \binom{12}{2} = 66$ solutions.
:::

:::question intermediate
What is the coefficient of $x^2 y^5$ in $(x + y)^7$, and of $x^2$ in $(3 - x)^5$?
:::answer
In $(x + y)^7$ it is $\binom{7}{5} = 21$. In $(3 - x)^5$ the $x^2$ term is $\binom{5}{2} 3^3 (-x)^2 = 10 \times 27 x^2 = 270x^2$, so the coefficient is 270.
:::

:::question advanced
Give a combinatorial proof that $\sum_{k=0}^{n} \binom{n}{k}^2 = \binom{2n}{n}$.
:::answer
Count the ways to choose $n$ people from a group of $n$ women and $n$ men: directly, $\binom{2n}{n}$. Alternatively, choose $k$ women and $n - k$ men for each $k$: $\binom{n}{k}\binom{n}{n-k} = \binom{n}{k}^2$ ways, and summing over $k$ from 0 to $n$ counts every selection exactly once. Both counts describe the same set, so they are equal.
:::

## Further learning

- **Next:** *Induction Proof Techniques* proves formulas such as $\sum_k \binom{n}{k} = 2^n$ in another way.
- **Related:** *Discrete Distributions: Bernoulli, Binomial, Geometric & Poisson* in Probability builds the binomial distribution from $\binom{n}{k}$.
