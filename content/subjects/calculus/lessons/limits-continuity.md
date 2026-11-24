---
lesson: limits-continuity
title: Limits & Continuity
summary: The idea of a limit, evaluating limits with limit laws and algebra, one-sided limits and limits at infinity, the special limits of sin(x)/x and (1 + 1/n)^n, and continuity with the intermediate value theorem.
minutes: 50
type: theory
objectives:
  - Explain the meaning of a limit and evaluate limits using limit laws, factoring, and rationalising
  - Find one-sided limits and limits at infinity, and identify when a limit does not exist
  - Define continuity at a point, classify discontinuities, and apply the intermediate value theorem
review: ai-draft
---
## Introduction

Calculus is built on one idea: what happens to a quantity as something gets closer and closer to a value without necessarily reaching it. The speedometer of a car reports an instantaneous speed, which is the limit of average speeds over ever-shorter time intervals. **Limits** make "closer and closer" precise, and **continuity** describes functions without sudden jumps. Every derivative and every integral is defined as a limit.

**Before you start:** you should be comfortable with functions, graphs, algebraic simplification, and basic trigonometry.

## Core theory

### The limit

We write $\lim_{x \to a} f(x) = L$ if $f(x)$ can be made as close to $L$ as we like by taking $x$ close enough to $a$ (but not equal to $a$). The value $f(a)$ itself does not matter; the function need not even be defined there. The formal **epsilon-delta definition**: for every $\varepsilon > 0$ there is a $\delta > 0$ such that $0 < |x - a| < \delta$ implies $|f(x) - L| < \varepsilon$.

### Limit laws and techniques

If $\lim f$ and $\lim g$ exist, the limit of a sum, difference, product, constant multiple, or quotient (with non-zero denominator limit) is the sum, difference, product, multiple, or quotient of the limits. For polynomials and rational functions defined at $a$, **direct substitution** works. When substitution gives the indeterminate form $\frac{0}{0}$:

- **Factor and cancel:** $\lim_{x \to 2}\frac{x^2 - 4}{x - 2} = \lim_{x \to 2}(x + 2) = 4$.
- **Rationalise:** multiply by a conjugate, as in $\lim_{x \to 0}\frac{\sqrt{x + 9} - 3}{x} = \lim_{x \to 0}\frac{1}{\sqrt{x + 9} + 3} = \frac16$.
- **Squeeze theorem:** if $g(x) \le f(x) \le h(x)$ near $a$ and $g$ and $h$ have the same limit $L$, so does $f$. It proves the key limit $\lim_{x \to 0}\frac{\sin x}{x} = 1$ (with $x$ in radians).

### One-sided limits and existence

$\lim_{x \to a^-} f(x)$ approaches from the left and $\lim_{x \to a^+} f(x)$ from the right. The two-sided limit exists exactly when both one-sided limits exist and are equal. A limit fails to exist when the sides disagree (a jump), when values grow without bound, or when the function oscillates, as $\sin(1/x)$ does near 0.

### Limits at infinity

$\lim_{x \to \infty} f(x) = L$ describes long-run behaviour and gives a **horizontal asymptote**. For rational functions, compare the degrees: divide numerator and denominator by the highest power of $x$. A famous example defines Euler's number:

$$e = \lim_{n \to \infty}\left(1 + \frac{1}{n}\right)^n \approx 2.71828$$

### Continuity

$f$ is **continuous at $a$** if $f(a)$ is defined, $\lim_{x \to a} f(x)$ exists, and they are equal. Polynomials, exponentials, sine, and cosine are continuous everywhere, and sums, products, quotients (where the denominator is non-zero), and compositions of continuous functions are continuous. Discontinuities are **removable** (a hole, fixable by redefining one value), **jump**, or **infinite** (a vertical asymptote).

The **intermediate value theorem** (IVT): if $f$ is continuous on $[a, b]$ and $N$ lies between $f(a)$ and $f(b)$, then $f(c) = N$ for some $c$ in $[a, b]$. In particular, a continuous function that changes sign on an interval has a root there, the idea behind the bisection method.

## Worked examples

### Example 1: Watching limits numerically

The table approaches each limit from both sides or along a sequence.

```python
from math import sin

def f(x):
    return (x * x - 4) / (x - 2)

for h in (0.1, 0.01, 0.001):
    print(f"x = 2 - {h}: f = {f(2 - h):.4f} | x = 2 + {h}: f = {f(2 + h):.4f}")
print("sin(x)/x near 0:", [round(sin(x) / x, 6) for x in (0.1, 0.01, 0.001)])
print("(1 + 1/n)^n:", [round((1 + 1 / n) ** n, 5) for n in (10, 1000, 100000)])
step = lambda x: 0 if x < 0 else 1
print("step function one-sided values near 0:", step(-1e-9), step(1e-9))
```

Output:

```text
x = 2 - 0.1: f = 3.9000 | x = 2 + 0.1: f = 4.1000
x = 2 - 0.01: f = 3.9900 | x = 2 + 0.01: f = 4.0100
x = 2 - 0.001: f = 3.9990 | x = 2 + 0.001: f = 4.0010
sin(x)/x near 0: [0.998334, 0.999983, 1.0]
(1 + 1/n)^n: [2.59374, 2.71692, 2.71827]
step function one-sided values near 0: 0 1
```

$\frac{x^2 - 4}{x - 2}$ is undefined at 2, yet its values approach 4 from both sides, matching the algebraic answer. $\frac{\sin x}{x}$ approaches 1 and $(1 + 1/n)^n$ approaches $e$. The step function's one-sided limits at 0 are 0 and 1, so its two-sided limit does not exist. Numbers suggest limits; algebra proves them.

### Example 2: Limits at infinity and an IVT argument

**(a)** Evaluate $\lim_{x \to \infty}\frac{3x^2 - x + 5}{2x^2 + 7}$. Divide every term by $x^2$:

$$\lim_{x \to \infty}\frac{3 - 1/x + 5/x^2}{2 + 7/x^2} = \frac{3}{2}$$

so $y = 1.5$ is a horizontal asymptote.

**(b)** Show that $x^3 + x - 1 = 0$ has a solution between 0 and 1. Let $f(x) = x^3 + x - 1$, a polynomial and hence continuous. $f(0) = -1 < 0$ and $f(1) = 1 > 0$, so by the IVT there is a $c$ in $(0, 1)$ with $f(c) = 0$. The IVT guarantees existence but not the value; numerical methods such as bisection then locate $c \approx 0.6823$.

## Applications

- **Instantaneous rates:** velocity and marginal cost are limits of average rates.
- **Numerical methods:** root-finding algorithms rely on continuity and the IVT.
- **Algorithm analysis:** limits at infinity compare growth rates of running times.
- **Physics and engineering:** asymptotes describe steady states and long-run behaviour.

## Common mistakes

- **Concluding that a $\frac{0}{0}$ limit does not exist.** It is indeterminate; simplify first.
- **Thinking the limit must equal $f(a)$.** That is true only for continuous functions.
- **Using degrees in $\frac{\sin x}{x}$.** The limit 1 holds only for radians.
- **Ignoring one-sided behaviour.** Check both sides at piecewise boundaries.
- **Applying the IVT to discontinuous functions.** Continuity on the closed interval is required.

## Revision notes

- $\lim_{x \to a} f(x) = L$: values approach $L$ as $x \to a$; $f(a)$ is irrelevant.
- Limit laws; direct substitution for continuous functions; factor, rationalise, or squeeze for $\frac00$.
- Two-sided limit exists iff both one-sided limits exist and are equal.
- $\lim_{x \to 0}\frac{\sin x}{x} = 1$; $\lim_{n \to \infty}(1 + 1/n)^n = e$.
- Continuous at $a$: $\lim_{x \to a} f(x) = f(a)$; removable, jump, infinite discontinuities.
- IVT: continuous and sign change ⇒ a root in between.

## Practice questions

:::question basic
Evaluate $\lim_{x \to 3}\frac{x^2 - 9}{x - 3}$.
:::answer
Factor: $\frac{(x - 3)(x + 3)}{x - 3} = x + 3$ for $x \ne 3$, so the limit is $3 + 3 = 6$.
:::

:::question basic
Find $\lim_{x \to \infty}\frac{5x + 2}{x^2 + 1}$.
:::answer
Dividing by $x^2$ gives $\frac{5/x + 2/x^2}{1 + 1/x^2} \to \frac{0}{1} = 0$. The denominator grows faster than the numerator.
:::

:::question intermediate
Let $f(x) = x + 1$ for $x < 2$ and $f(x) = 5 - x$ for $x \ge 2$. Does $\lim_{x \to 2} f(x)$ exist? Is $f$ continuous at 2?
:::answer
The left limit is $2 + 1 = 3$ and the right limit is $5 - 2 = 3$, so the limit exists and equals 3. Since $f(2) = 3$ as well, $f$ is continuous at 2.
:::

:::question intermediate
Evaluate $\lim_{x \to 0}\frac{\sin 3x}{x}$.
:::answer
Rewrite as $3 \cdot \frac{\sin 3x}{3x}$. As $x \to 0$, $3x \to 0$, so $\frac{\sin 3x}{3x} \to 1$ and the limit is 3.
:::

:::question advanced
Use the intermediate value theorem to show that $\cos x = x$ has a solution, and explain why the theorem cannot tell you how many solutions there are.
:::answer
Let $g(x) = \cos x - x$, which is continuous. $g(0) = 1 > 0$ and $g(\pi/2) = -\pi/2 < 0$, so by the IVT there is a $c$ in $(0, \pi/2)$ with $g(c) = 0$, that is, $\cos c = c$. The IVT only guarantees at least one crossing; a function can cross zero several times between two points of opposite sign, so uniqueness needs another argument (here, $g$ is strictly decreasing because $g'(x) = -\sin x - 1 \le 0$, so there is exactly one solution).
:::

## Further learning

- **Next:** *Derivatives & The Chain Rule* defines the derivative as a limit.
- **Related:** *Bisection & Secant Methods* in Numerical Methods turns the IVT into an algorithm.
