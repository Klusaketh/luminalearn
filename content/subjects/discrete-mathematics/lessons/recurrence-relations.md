---
lesson: recurrence-relations
title: Recurrence Relations
summary: Modelling problems with recurrence relations, solving them by iteration and by the characteristic equation for linear homogeneous recurrences, handling repeated roots and simple non-homogeneous terms, and connecting recurrences to algorithm running times.
minutes: 50
type: theory
objectives:
  - Write recurrence relations with initial conditions to model counting and growth problems
  - Solve linear homogeneous recurrences with constant coefficients using the characteristic equation, including repeated roots
  - Solve simple non-homogeneous recurrences and recognise divide-and-conquer recurrences from algorithm analysis
review: ai-draft
---
## Introduction

Many quantities are easiest to describe in terms of smaller versions of themselves: a population that grows from last year's, the number of moves to solve the Tower of Hanoi with one more disc, the running time of merge sort on an input twice as large. A **recurrence relation** captures such a rule, and **solving** it gives a closed-form formula that can be evaluated directly or compared with other growth rates.

**Before you start:** you should know induction, sequences and summation, and how to solve quadratic equations.

## Core theory

### Recurrences and initial conditions

A recurrence relation expresses $a_n$ in terms of earlier terms; together with enough **initial conditions** it determines the sequence uniquely. Examples:

- Compound interest: $a_n = 1.05\,a_{n-1}$, $a_0 = 1000$.
- Fibonacci: $F_n = F_{n-1} + F_{n-2}$, $F_0 = 0$, $F_1 = 1$.
- Tower of Hanoi: $H_n = 2H_{n-1} + 1$, $H_1 = 1$: move $n - 1$ discs aside, move the largest, move the $n - 1$ discs back on top.
- Bit strings of length $n$ with no two consecutive 0s: $a_n = a_{n-1} + a_{n-2}$ (end in 1, or end in 10), $a_1 = 2$, $a_2 = 3$.

### Solving by iteration

Unroll the recurrence and spot the pattern. For Hanoi: $H_n = 2H_{n-1} + 1 = 4H_{n-2} + 2 + 1 = \cdots = 2^{n-1}H_1 + 2^{n-2} + \cdots + 1 = 2^n - 1$. Verify the guess by induction.

### Linear homogeneous recurrences with constant coefficients

A recurrence of the form

$$a_n = c_1 a_{n-1} + c_2 a_{n-2} + \cdots + c_k a_{n-k}$$

is **linear homogeneous of degree k**. Trying $a_n = r^n$ gives the **characteristic equation** $r^k - c_1 r^{k-1} - \cdots - c_k = 0$. For degree 2, $r^2 - c_1 r - c_2 = 0$:

- **Distinct roots** $r_1 \ne r_2$: $a_n = \alpha_1 r_1^n + \alpha_2 r_2^n$.
- **Repeated root** $r$: $a_n = (\alpha_1 + \alpha_2 n) r^n$.

The constants $\alpha_i$ come from the initial conditions. For Fibonacci, $r^2 = r + 1$ gives $r = \frac{1 \pm \sqrt{5}}{2}$, and solving for the constants yields **Binet's formula**

$$F_n = \frac{1}{\sqrt{5}}\left(\varphi^n - \psi^n\right), \quad \varphi = \frac{1 + \sqrt{5}}{2} \approx 1.618, \; \psi = \frac{1 - \sqrt{5}}{2}$$

so Fibonacci numbers grow like $\varphi^n$.

### Non-homogeneous recurrences

For $a_n = c_1 a_{n-1} + c_2 a_{n-2} + f(n)$, the general solution is the homogeneous solution plus one **particular solution**. Guess a particular solution of the same form as $f(n)$: a constant for a constant, a polynomial of the same degree for a polynomial, $C s^n$ for $s^n$ (multiplied by $n$ if $s$ is a characteristic root). For Hanoi, $H_n = 2H_{n-1} + 1$: the homogeneous part gives $\alpha 2^n$, a constant guess $C$ gives $C = 2C + 1$, so $C = -1$, and $H_1 = 1$ gives $\alpha = 1$: $H_n = 2^n - 1$.

### Divide-and-conquer recurrences

Algorithms that split a problem of size $n$ into $a$ subproblems of size $n/b$ with $f(n)$ extra work satisfy $T(n) = aT(n/b) + f(n)$. Merge sort gives $T(n) = 2T(n/2) + n$, which solves to $\Theta(n \log n)$; binary search gives $T(n) = T(n/2) + 1$, which is $\Theta(\log n)$. The **master theorem** handles the common cases by comparing $f(n)$ with $n^{\log_b a}$.

## Worked examples

### Example 1: Solving with the characteristic equation

**(a)** $a_n = 5a_{n-1} - 6a_{n-2}$, $a_0 = 1$, $a_1 = 4$.

The characteristic equation $r^2 - 5r + 6 = 0$ has roots 2 and 3, so $a_n = \alpha 2^n + \beta 3^n$. From $a_0$: $\alpha + \beta = 1$; from $a_1$: $2\alpha + 3\beta = 4$. Then $\beta = 2$, $\alpha = -1$, and

$$a_n = 2 \cdot 3^n - 2^n$$

**(b)** $b_n = 6b_{n-1} - 9b_{n-2}$, $b_0 = 1$, $b_1 = 6$.

$r^2 - 6r + 9 = (r - 3)^2$, a repeated root 3, so $b_n = (\alpha + \beta n) 3^n$. $b_0 = \alpha = 1$; $b_1 = 3(\alpha + \beta) = 6$ gives $\beta = 1$. So $b_n = (1 + n) 3^n$.

Checking both closed forms against the recurrences:

```python
def iterate(c1, c2, x0, x1, n):
    seq = [x0, x1]
    while len(seq) < n:
        seq.append(c1 * seq[-1] + c2 * seq[-2])
    return seq

a = iterate(5, -6, 1, 4, 8)
b = iterate(6, -9, 1, 6, 8)
print(a, a == [2 * 3**n - 2**n for n in range(8)])
print(b, b == [(1 + n) * 3**n for n in range(8)])
```

Output:

```text
[1, 4, 14, 46, 146, 454, 1394, 4246] True
[1, 6, 27, 108, 405, 1458, 5103, 17496] True
```

### Example 2: Modelling and solving a counting recurrence

Count the bit strings of length $n$ with no two consecutive 0s.

A valid string of length $n$ either ends in 1, preceded by any valid string of length $n - 1$, or ends in 10, preceded by any valid string of length $n - 2$. So $a_n = a_{n-1} + a_{n-2}$ with $a_1 = 2$ ("0", "1") and $a_2 = 3$ ("01", "10", "11"). This is the Fibonacci recurrence shifted: $a_n = F_{n+2}$.

```python
from itertools import product

def brute(n):
    return sum(1 for bits in product("01", repeat=n) if "00" not in "".join(bits))

fib = [0, 1]
while len(fib) < 15:
    fib.append(fib[-1] + fib[-2])
print([brute(n) for n in range(1, 11)])
print([fib[n + 2] for n in range(1, 11)])
phi = (1 + 5 ** 0.5) / 2
print(round(phi ** 12 / 5 ** 0.5), fib[12])
```

Output:

```text
[2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
[2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
144 144
```

The brute-force count matches the recurrence, and rounding $\varphi^{12}/\sqrt{5}$ gives $F_{12} = 144$, because the $\psi^n$ term in Binet's formula is always smaller than $\tfrac12$ in size.

## Applications

- **Algorithm analysis:** running times of recursive algorithms are recurrences.
- **Dynamic programming:** a DP table is a recurrence evaluated bottom-up.
- **Finance and population models:** growth with interest or birth rates.
- **Counting:** strings, tilings, and paths with constraints.

## Common mistakes

- **Forgetting initial conditions.** A recurrence alone has infinitely many solutions.
- **Mishandling repeated roots.** Use $(\alpha + \beta n) r^n$, not $\alpha r^n + \beta r^n$.
- **Choosing a particular solution that duplicates a homogeneous term.** Multiply the guess by $n$.
- **Sign errors in the characteristic equation.** $a_n = c_1 a_{n-1} + c_2 a_{n-2}$ gives $r^2 - c_1 r - c_2 = 0$.
- **Not verifying the closed form.** Check a few terms or prove it by induction.

## Revision notes

- A recurrence plus initial conditions defines a sequence.
- Iteration: unroll, find the pattern, prove by induction.
- Characteristic equation $r^2 - c_1 r - c_2 = 0$: distinct roots give $\alpha_1 r_1^n + \alpha_2 r_2^n$; a repeated root gives $(\alpha_1 + \alpha_2 n) r^n$.
- Non-homogeneous: homogeneous solution plus a particular solution shaped like $f(n)$.
- Hanoi $2^n - 1$; Fibonacci grows like $\varphi^n$ (Binet).
- Divide and conquer: $T(n) = aT(n/b) + f(n)$; merge sort $\Theta(n \log n)$.

## Practice questions

:::question basic
Find the first five terms of $a_n = 3a_{n-1} - 2$, $a_0 = 2$.
:::answer
$a_0 = 2$, $a_1 = 3 \cdot 2 - 2 = 4$, $a_2 = 10$, $a_3 = 28$, $a_4 = 82$. (In closed form $a_n = 3^n + 1$.)
:::

:::question basic
How many moves does the Tower of Hanoi need for 10 discs?
:::answer
$H_n = 2^n - 1$, so $H_{10} = 1024 - 1 = 1023$ moves.
:::

:::question intermediate
Solve $a_n = a_{n-1} + 6a_{n-2}$ with $a_0 = 3$, $a_1 = 6$.
:::answer
The characteristic equation $r^2 - r - 6 = 0$ has roots 3 and -2, so $a_n = \alpha 3^n + \beta(-2)^n$. Then $\alpha + \beta = 3$ and $3\alpha - 2\beta = 6$, giving $\alpha = 12/5$ and $\beta = 3/5$. So $a_n = \frac{12}{5} 3^n + \frac{3}{5}(-2)^n$; for example $a_2 = \frac{108}{5} + \frac{12}{5} = 24 = 6 + 18$.
:::

:::question intermediate
Write a recurrence for the number of ways to climb $n$ stairs taking 1 or 2 steps at a time, and relate it to Fibonacci.
:::answer
The last move is a single step from stair $n - 1$ or a double step from stair $n - 2$, so $w_n = w_{n-1} + w_{n-2}$ with $w_1 = 1$ and $w_2 = 2$. These are Fibonacci numbers shifted by one: $w_n = F_{n+1}$.
:::

:::question advanced
Solve $a_n = 2a_{n-1} + 3^n$ with $a_0 = 1$.
:::answer
The homogeneous solution is $\alpha 2^n$. Since 3 is not a characteristic root, try a particular solution $C 3^n$: $C 3^n = 2C 3^{n-1} + 3^n$; dividing by $3^{n-1}$ gives $3C = 2C + 3$, so $C = 3$. Then $a_n = \alpha 2^n + 3^{n+1}$, and $a_0 = \alpha + 3 = 1$ gives $\alpha = -2$. So $a_n = 3^{n+1} - 2^{n+1}$; check: $a_1 = 9 - 4 = 5 = 2 \cdot 1 + 3$.
:::

## Further learning

- **Next:** *Graph Theory Fundamentals* introduces structures whose properties are often counted with recurrences.
- **Related:** *Call Stack & Recurrence Trees* in Data Structures & Algorithms solves divide-and-conquer recurrences.
