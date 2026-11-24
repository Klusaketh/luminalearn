---
lesson: bisection-secant-methods
title: Bisection & Secant Methods
summary: Finding roots of equations numerically by bracketing with the bisection method, its guaranteed convergence and error bound, and the faster derivative-free secant method, with stopping criteria and a comparison of convergence rates.
minutes: 45
type: theory
objectives:
  - Apply the bisection method, justify its convergence with the intermediate value theorem, and compute the number of iterations needed
  - Apply the secant method and explain its superlinear convergence and its failure modes
  - Choose stopping criteria and compare bracketing and open methods
review: ai-draft
---
## Introduction

Most equations cannot be solved with a formula: there is no algebraic expression for the root of $x^3 - x - 2 = 0$ that anyone would want to use, and none at all for $\cos x = x$. **Root-finding** methods compute solutions to any desired accuracy by repeated refinement. The **bisection method** is slow but can never fail once a root is bracketed; the **secant method** is much faster but less reliable. Understanding both shows the central trade-off of numerical analysis between robustness and speed.

**Before you start:** you should know continuity, the intermediate value theorem, and the idea of convergence of a sequence.

## Core theory

### Bracketing and bisection

If $f$ is continuous on $[a, b]$ and $f(a)$ and $f(b)$ have opposite signs, the intermediate value theorem guarantees a root between them. **Bisection** repeatedly halves the bracket:

1. Compute the midpoint $m = \frac{a + b}{2}$.
2. If $f(a)$ and $f(m)$ have opposite signs, the root is in $[a, m]$; set $b = m$. Otherwise set $a = m$.
3. Stop when the bracket is narrow enough.

After $n$ steps the bracket has width $\frac{b - a}{2^n}$, so the midpoint is within $\frac{b - a}{2^{n+1}}$ of a root. To reach a tolerance $\varepsilon$ from an initial width $w$ takes $n \ge \log_2(w/\varepsilon)$ steps: about 3.3 steps per decimal digit, regardless of the function. This **linear convergence** with ratio $\frac12$ is slow but **guaranteed**. Bisection needs only the sign of $f$, and it finds one root even when the bracket contains several. It cannot find roots where $f$ touches zero without changing sign, such as $x^2 = 0$.

### The secant method

The secant method replaces $f$ by the straight line through the last two points and takes its x-intercept as the next estimate:

$$x_{n+1} = x_n - f(x_n)\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$$

It needs no derivative and only one new function evaluation per step. Near a simple root, it converges **superlinearly** with order $\frac{1 + \sqrt5}{2} \approx 1.618$ (the golden ratio): the number of correct digits grows by about 60% each step. But it is not guaranteed to converge: the iterates can leave the region of the root, and the formula breaks down if $f(x_n) = f(x_{n-1})$.

The **regula falsi** (false position) method uses the secant formula but keeps a bracket, combining safety with some speed; practical solvers such as Brent's method switch between bisection and faster steps automatically.

### Order of convergence

If $e_n$ is the error at step $n$, a method has order $p$ when $|e_{n+1}| \approx C|e_n|^p$. Bisection has $p = 1$ ($C = \frac12$), secant $p \approx 1.618$, and Newton's method $p = 2$.

### Stopping criteria

Common tests are: the bracket width or step size $|x_{n+1} - x_n|$ is below a tolerance; the residual $|f(x_n)|$ is below a tolerance; or a maximum number of iterations is reached (always include one). A small residual does not always mean a small error: for a flat function, $|f(x)|$ can be tiny far from the root.

## Worked examples

### Example 1: Bisection versus secant on $x^3 - x - 2 = 0$

$f(1) = -2 < 0$ and $f(2) = 4 > 0$, so a root lies in $[1, 2]$.

```python
def f(x):
    return x**3 - x - 2

def bisection(f, a, b, tol=1e-8):
    steps = 0
    while b - a > tol:
        m = (a + b) / 2
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
        steps += 1
    return (a + b) / 2, steps

def secant(f, x0, x1, tol=1e-12, max_iter=50):
    for k in range(1, max_iter + 1):
        x2 = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
        if abs(x2 - x1) < tol:
            return x2, k
        x0, x1 = x1, x2
    return x1, max_iter

root_b, n_b = bisection(f, 1, 2)
root_s, n_s = secant(f, 1, 2)
print(f"bisection: root {root_b:.8f} after {n_b} halvings")
print(f"secant:    root {root_s:.8f} after {n_s} iterations")
print(f"f(root) = {f(root_s):.1e}")
import math
print("halvings needed for 1e-8 from width 1:", math.ceil(math.log2(1 / 1e-8)))
```

Output:

```text
bisection: root 1.52137971 after 27 halvings
secant:    root 1.52137971 after 8 iterations
f(root) = 0.0e+00
halvings needed for 1e-8 from width 1: 27
```

Both methods find the root $x \approx 1.52137971$. Bisection needed 27 halvings to shrink the bracket below $10^{-8}$, exactly as predicted by $\lceil \log_2(1/10^{-8}) \rceil = 27$; the secant method reached full double precision in 8 iterations from the same starting points.

### Example 2: Three bisection steps by hand

Find $\sqrt{3}$ as the root of $f(x) = x^2 - 3$ on $[1, 2]$ ($f(1) = -2$, $f(2) = 1$).

| Step | $a$ | $b$ | $m$ | $f(m)$ | New bracket |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 1 | 2 | 1.5 | $-0.75$ | $[1.5, 2]$ |
| 2 | 1.5 | 2 | 1.75 | $0.0625$ | $[1.5, 1.75]$ |
| 3 | 1.5 | 1.75 | 1.625 | $-0.359$ | $[1.625, 1.75]$ |

After three steps the root lies in $[1.625, 1.75]$; its midpoint 1.6875 is within 0.0625 of $\sqrt{3} \approx 1.7321$. One secant step from $x_0 = 1$, $x_1 = 2$ gives $x_2 = 2 - 1 \cdot \frac{2 - 1}{1 - (-2)} = \frac53 \approx 1.667$, and the next gives about 1.7273, already much closer.

## Applications

- **Engineering:** solving for operating points, such as the flow rate where pump and pipe curves meet.
- **Finance:** the internal rate of return is the root of a net-present-value function.
- **Computer graphics:** ray tracing finds intersections with implicit surfaces by root finding.
- **Libraries:** `scipy.optimize.brentq` and similar solvers combine bisection with faster steps.

## Common mistakes

- **Starting bisection without a sign change.** Check $f(a)f(b) < 0$ first.
- **Expecting bisection to find double roots.** Without a sign change, it cannot.
- **Running the secant method without an iteration limit.** It can diverge or cycle.
- **Stopping only on a small residual.** Also check how much $x$ is still changing.
- **Dividing by $f(x_n) - f(x_{n-1})$ when it is zero.** Guard against it.

## Revision notes

- Bisection: keep a sign-changing bracket and halve it; error after $n$ steps $\le (b - a)/2^{n+1}$.
- Iterations needed: $n \ge \log_2(\text{width}/\text{tolerance})$, about 3.3 per digit.
- Secant: $x_{n+1} = x_n - f(x_n)\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$; order about 1.618; no guarantee.
- Order of convergence $p$: $|e_{n+1}| \approx C|e_n|^p$.
- Stop on step size, residual, and an iteration limit.
- Robust hybrids (regula falsi, Brent) combine bracketing with speed.

## Practice questions

:::question basic
Why must $f(a)$ and $f(b)$ have opposite signs before applying bisection?
:::answer
The opposite signs, together with continuity, guarantee a root in $[a, b]$ by the intermediate value theorem. Each step keeps the half-interval where the sign change persists, so the root stays bracketed; without an initial sign change there is no such guarantee.
:::

:::question basic
How many bisection steps are needed to locate a root in $[0, 4]$ to within $10^{-6}$ (bracket width)?
:::answer
We need $4/2^n \le 10^{-6}$, so $2^n \ge 4 \times 10^6$ and $n \ge \log_2(4 \times 10^6) \approx 21.93$. So 22 steps are needed.
:::

:::question intermediate
Apply one secant step to $f(x) = x^2 - 5$ with $x_0 = 2$ and $x_1 = 3$.
:::answer
$f(2) = -1$ and $f(3) = 4$. $x_2 = 3 - 4 \cdot \frac{3 - 2}{4 - (-1)} = 3 - 0.8 = 2.2$. The true root is $\sqrt5 \approx 2.236$.
:::

:::question intermediate
Compare the bisection and secant methods in terms of guaranteed convergence and speed.
:::answer
Bisection always converges once a root is bracketed but only linearly, gaining about one binary digit per step. The secant method converges superlinearly (order about 1.618) and needs no derivative, but it may diverge or break down if started far from the root or if two function values coincide.
:::

:::question advanced
Why can a tiny residual $|f(x_n)|$ be misleading as a stopping criterion? Give an example.
:::answer
If $f$ is very flat near the root, $|f(x)|$ is small over a wide interval, so a point can have a tiny residual yet be far from the root. For $f(x) = (x - 1)^5$, the point $x = 1.01$ has $|f| = 10^{-10}$ while its error is 0.01. Combining the residual test with a test on the change in $x$ (or the bracket width) avoids this.
:::

## Further learning

- **Next:** *Newton-Raphson & Fixed-Point Iteration* uses derivatives for even faster convergence.
- **Related:** *Limits & Continuity* in Calculus provides the intermediate value theorem behind bisection.
