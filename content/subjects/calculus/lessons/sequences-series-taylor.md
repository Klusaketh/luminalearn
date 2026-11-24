---
lesson: sequences-series-taylor
title: Sequences, Series & Taylor Expansions
summary: Sequences and their limits, infinite series and convergence tests (geometric, divergence, integral, comparison, ratio, alternating series), power series, and Taylor and Maclaurin polynomials with error estimates.
minutes: 55
type: theory
objectives:
  - Determine whether sequences and series converge, using the main convergence tests
  - Find sums of geometric series and the radius of convergence of power series
  - Build Taylor and Maclaurin polynomials and estimate the error of a Taylor approximation
review: ai-draft
---
## Introduction

How does a calculator compute $e^{0.3}$ or $\sin(1.2)$? It cannot draw curves; it adds up a few terms of a **power series**. Infinite sums also describe compound growth, the probability of eventual events, and the running time of recursive algorithms. This lesson covers when an infinite sum has a finite value, how to test it, and how **Taylor polynomials** approximate complicated functions with simple ones, an idea that runs through numerical methods, physics, and machine learning.

**Before you start:** you should know limits, derivatives of all orders, and basic integration.

## Core theory

### Sequences

A **sequence** $a_1, a_2, a_3, \dots$ **converges** to $L$ if its terms approach $L$; otherwise it diverges. For example $\frac{n}{n + 1} \to 1$ and $(1 + \frac1n)^n \to e$, while $(-1)^n$ diverges. A bounded, monotonic sequence always converges.

### Series and partial sums

A **series** $\sum_{k=1}^\infty a_k$ converges to $S$ if its partial sums $S_n = a_1 + \cdots + a_n$ converge to $S$.

- **Geometric series:** $\sum_{k=0}^\infty ar^k = \frac{a}{1 - r}$ when $|r| < 1$; it diverges when $|r| \ge 1$.
- **Divergence test:** if $a_k \not\to 0$, the series diverges. The converse is false: the **harmonic series** $\sum \frac1k$ has terms tending to 0 but diverges, growing like $\ln n$.
- **p-series:** $\sum \frac{1}{k^p}$ converges exactly when $p > 1$ (for example $\sum \frac{1}{k^2} = \frac{\pi^2}{6}$).

### Convergence tests

- **Integral test:** for positive decreasing $f$, $\sum f(k)$ and $\int_1^\infty f(x)\,dx$ converge or diverge together.
- **Comparison test:** if $0 \le a_k \le b_k$ and $\sum b_k$ converges, so does $\sum a_k$; if $\sum a_k$ diverges, so does $\sum b_k$.
- **Ratio test:** if $\lim \left|\frac{a_{k+1}}{a_k}\right| = L$, the series converges absolutely when $L < 1$, diverges when $L > 1$, and the test is inconclusive when $L = 1$. It suits factorials and powers.
- **Alternating series test:** if $b_k$ decreases to 0, then $\sum (-1)^{k+1}b_k$ converges, and the error after $n$ terms is at most $b_{n+1}$. The alternating harmonic series converges to $\ln 2$ although the harmonic series diverges: it converges **conditionally**, not absolutely.

### Power series

A **power series** $\sum c_k (x - a)^k$ converges for $|x - a| < R$ and diverges for $|x - a| > R$, where $R$ is the **radius of convergence**, usually found with the ratio test. Inside it, power series can be differentiated and integrated term by term.

### Taylor and Maclaurin series

The **Taylor polynomial** of degree $n$ of $f$ around $a$ matches $f$ and its first $n$ derivatives at $a$:

$$T_n(x) = \sum_{k=0}^{n}\frac{f^{(k)}(a)}{k!}(x - a)^k$$

With $a = 0$ it is a **Maclaurin** polynomial. Important series:

$$e^x = \sum_{k=0}^\infty \frac{x^k}{k!}, \quad \sin x = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots, \quad \cos x = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots, \quad \frac{1}{1 - x} = \sum_{k=0}^\infty x^k \;(|x| < 1)$$

The **Lagrange remainder** bounds the error: $|f(x) - T_n(x)| \le \frac{M}{(n + 1)!}|x - a|^{n+1}$, where $M$ bounds $|f^{(n+1)}|$ between $a$ and $x$. Approximations are best near $a$ and improve rapidly as $n$ grows when the factorial dominates.

## Worked examples

### Example 1: Taylor approximations and series behaviour

```python
from math import cos, exp, factorial

def taylor_exp(x, n):
    return sum(x**k / factorial(k) for k in range(n + 1))

def taylor_cos(x, n):
    return sum((-1) ** k * x ** (2 * k) / factorial(2 * k) for k in range(n + 1))

for n in (2, 4, 8):
    print(f"degree {n}: e^1 approx {taylor_exp(1, n):.6f} (error {abs(taylor_exp(1, n) - exp(1)):.1e})")
print(f"cos(0.5) with 3 terms: {taylor_cos(0.5, 2):.8f} vs {cos(0.5):.8f}")
partial = 0.0
for k in range(1, 1001):
    partial += 1 / k
print(f"harmonic partial sum to 1000: {partial:.4f} (diverges, slowly)")
print(f"geometric sum of (1/2)^k, k=0..30: {sum(0.5**k for k in range(31)):.9f} -> 2")
print(f"alternating harmonic to 10000: {sum((-1) ** (k + 1) / k for k in range(1, 10001)):.5f} vs ln 2 = 0.69315")
```

Output:

```text
degree 2: e^1 approx 2.500000 (error 2.2e-01)
degree 4: e^1 approx 2.708333 (error 9.9e-03)
degree 8: e^1 approx 2.718279 (error 3.1e-06)
cos(0.5) with 3 terms: 0.87760417 vs 0.87758256
harmonic partial sum to 1000: 7.4855 (diverges, slowly)
geometric sum of (1/2)^k, k=0..30: 1.999999999 -> 2
alternating harmonic to 10000: 0.69310 vs ln 2 = 0.69315
```

Each additional pair of Taylor terms cuts the error in $e \approx T_n(1)$ dramatically, because of the $(n + 1)!$ in the remainder. Three terms of the cosine series give $\cos 0.5$ to four decimal places, with error below the first omitted term, $\frac{0.5^6}{720} \approx 2.2 \times 10^{-5}$. The harmonic partial sum after 1,000 terms is only about 7.49, yet the series diverges (its partial sums grow like $\ln n$); the geometric series approaches 2; and the alternating harmonic series creeps towards $\ln 2$, within the alternating-series error bound $\frac{1}{10001}$.

### Example 2: Radius of convergence and a Taylor polynomial by hand

**(a)** Find the radius of convergence of $\sum_{k=0}^\infty \frac{x^k}{2^k}$. The ratio test gives $\left|\frac{x^{k+1}/2^{k+1}}{x^k/2^k}\right| = \frac{|x|}{2} < 1$, so $R = 2$. (It is a geometric series with ratio $\frac{x}{2}$, summing to $\frac{2}{2 - x}$ inside its interval.)

**(b)** Find the degree-2 Taylor polynomial of $f(x) = \sqrt{x}$ around $a = 4$ and estimate $\sqrt{4.2}$.

$f(4) = 2$, $f'(x) = \frac{1}{2}x^{-1/2}$ so $f'(4) = \frac14$, and $f''(x) = -\frac14x^{-3/2}$ so $f''(4) = -\frac{1}{32}$:

$$T_2(x) = 2 + \frac14(x - 4) - \frac{1}{64}(x - 4)^2$$

$T_2(4.2) = 2 + 0.05 - \frac{0.04}{64} = 2.049375$, compared with $\sqrt{4.2} \approx 2.0493902$: an error of about $1.5 \times 10^{-5}$.

## Applications

- **Scientific computing:** libraries evaluate $\sin$, $\exp$, and $\log$ with polynomial approximations.
- **Physics and engineering:** small-angle approximations ($\sin\theta \approx \theta$) are first-order Taylor polynomials.
- **Algorithm analysis:** geometric series bound the cost of doubling arrays and recursive algorithms.
- **Optimisation:** Newton's method and gradient descent rely on local Taylor approximations.

## Common mistakes

- **Concluding convergence because terms tend to 0.** The harmonic series is the counterexample.
- **Using the geometric formula when $|r| \ge 1$.** The series then diverges.
- **Forgetting the factorials in Taylor coefficients.**
- **Trusting a Taylor polynomial far from its centre.** Error grows with $|x - a|$.
- **Treating the ratio test's $L = 1$ as a verdict.** It is inconclusive.

## Revision notes

- Series converge when partial sums converge; terms must tend to 0, but that is not enough.
- Geometric: $\frac{a}{1 - r}$ for $|r| < 1$; p-series converge iff $p > 1$; harmonic diverges.
- Tests: integral, comparison, ratio ($L < 1$ converges), alternating (error ≤ next term).
- Power series converge within the radius $R$.
- $T_n(x) = \sum \frac{f^{(k)}(a)}{k!}(x - a)^k$; key series for $e^x$, $\sin$, $\cos$, $\frac{1}{1 - x}$.
- Remainder $\le \frac{M}{(n+1)!}|x - a|^{n+1}$.

## Practice questions

:::question basic
Find the sum of $3 + 1 + \frac13 + \frac19 + \cdots$.
:::answer
It is geometric with $a = 3$ and $r = \frac13$, so the sum is $\frac{3}{1 - 1/3} = \frac{3}{2/3} = 4.5$.
:::

:::question basic
Does $\sum_{k=1}^\infty \frac{k}{k + 1}$ converge?
:::answer
No. Its terms tend to 1, not 0, so it diverges by the divergence test.
:::

:::question intermediate
Use the ratio test on $\sum_{k=1}^\infty \frac{3^k}{k!}$.
:::answer
$\left|\frac{a_{k+1}}{a_k}\right| = \frac{3^{k+1}/(k+1)!}{3^k/k!} = \frac{3}{k + 1} \to 0 < 1$, so the series converges (in fact to $e^3 - 1$).
:::

:::question intermediate
Write the Maclaurin polynomial of degree 3 for $\sin x$ and use it to estimate $\sin 0.2$, with an error bound.
:::answer
$T_3(x) = x - \frac{x^3}{6}$, so $\sin 0.2 \approx 0.2 - \frac{0.008}{6} \approx 0.198667$. The series alternates with decreasing terms, so the error is at most the next term, $\frac{0.2^5}{120} \approx 2.7 \times 10^{-6}$.
:::

:::question advanced
Explain why $\sum \frac{1}{k^2}$ converges while $\sum \frac1k$ diverges, using the integral test.
:::answer
Both terms are positive and decreasing, so each series behaves like the corresponding integral. $\int_1^\infty \frac{dx}{x^2} = \left[-\frac1x\right]_1^\infty = 1$ is finite, so $\sum \frac{1}{k^2}$ converges. $\int_1^\infty \frac{dx}{x} = \lim_{b \to \infty}\ln b = \infty$, so $\sum \frac1k$ diverges; its partial sums grow like $\ln n$, without bound but very slowly.
:::

## Further learning

- **Next:** *Gradients, Jacobians & Hessians* extends Taylor approximation to several variables.
- **Related:** *Errors, Floating-Point Arithmetic & Stability* in Numerical Methods discusses truncation error from series.
