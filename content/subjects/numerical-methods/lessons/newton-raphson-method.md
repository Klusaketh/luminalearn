---
lesson: newton-raphson-method
title: Newton-Raphson & Fixed-Point Iteration
summary: Newton-Raphson iteration for solving equations, its geometric derivation from the tangent line, quadratic convergence near a simple root and the conditions under which it fails, and fixed-point iteration with its convergence criterion.
minutes: 45
type: theory
objectives:
  - Derive Newton's method from the tangent line and apply it to equations such as square roots and transcendental equations
  - Explain quadratic convergence, recognise failure cases, and choose good starting values
  - Rewrite an equation as a fixed-point problem and decide whether fixed-point iteration converges using the derivative condition
review: ai-draft
---
## Introduction

Newton's method is the most famous root-finding algorithm: from a reasonable starting guess, it typically doubles the number of correct digits at every step. It is how computers compute square roots and reciprocals, how optimisation algorithms find minima, and how engineering software solves nonlinear equations. Its cousin, **fixed-point iteration**, is simpler and underlies many iterative algorithms. Both converge quickly under the right conditions and fail in instructive ways otherwise.

**Before you start:** you should know derivatives, tangent lines, Taylor polynomials, and the bisection and secant methods.

## Core theory

### Newton's method

To solve $f(x) = 0$, replace $f$ near the current estimate $x_n$ by its tangent line $y = f(x_n) + f'(x_n)(x - x_n)$ and solve for where the tangent crosses zero:

$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$

For $f(x) = x^2 - a$, this becomes $x_{n+1} = \frac12\left(x_n + \frac{a}{x_n}\right)$, the ancient Babylonian square-root method.

### Quadratic convergence

If $r$ is a **simple root** ($f(r) = 0$, $f'(r) \ne 0$) and $f$ is smooth, then for starting values close enough to $r$,

$$|e_{n+1}| \approx \left|\frac{f''(r)}{2f'(r)}\right| e_n^2$$

so the error is squared at each step: errors of $10^{-2}$, $10^{-4}$, $10^{-8}$, $10^{-16}$. This **quadratic convergence** follows from the Taylor expansion of $f$ around $x_n$. At a **multiple root** ($f'(r) = 0$) convergence drops to linear.

### When Newton's method fails

- **Zero or tiny derivative:** a horizontal tangent sends the next iterate far away or divides by zero.
- **Poor starting value:** iterates may jump to a different root, diverge, or cycle; for $f(x) = x^3 - 2x + 2$ starting at 0, the iterates cycle between 0 and 1 forever.
- **Cost of derivatives:** $f'$ must be available; the secant method avoids this at a slightly lower rate.

Practical solvers start with bisection to get close, then switch to Newton, or limit the step size ("damped" Newton).

### Fixed-point iteration

Rewrite $f(x) = 0$ as $x = g(x)$, then iterate $x_{n+1} = g(x_n)$. A **fixed point** $r = g(r)$ is a solution. If $g$ is continuously differentiable near $r$ and

$$|g'(r)| < 1$$

the iteration converges for starting values near $r$, linearly with rate about $|g'(r)|$; if $|g'(r)| > 1$ it diverges. The same equation can be rearranged in many ways, some convergent and some not. Newton's method is itself a fixed-point iteration with $g(x) = x - f(x)/f'(x)$, for which $g'(r) = 0$ at a simple root, which explains its speed.

## Worked examples

### Example 1: Square root of 2, and solving $\cos x = x$

```python
from math import cos, sin

def newton(f, df, x, tol=1e-12, max_iter=50):
    history = [x]
    for _ in range(max_iter):
        step = f(x) / df(x)
        x -= step
        history.append(x)
        if abs(step) < tol:
            break
    return x, history

root, hist = newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0)
for k, x in enumerate(hist[:6]):
    print(f"iteration {k}: {x:.15f}  error {abs(x - 2 ** 0.5):.1e}")

x = 1.0
for k in range(1, 100):
    new = cos(x)
    if abs(new - x) < 1e-10:
        break
    x = new
print(f"fixed point of cos: {x:.10f} after {k} iterations")
r, h = newton(lambda x: cos(x) - x, lambda x: -sin(x) - 1, 1.0)
print(f"Newton on cos(x) - x: {r:.10f} after {len(h) - 1} iterations")
```

Output:

```text
iteration 0: 1.000000000000000  error 4.1e-01
iteration 1: 1.500000000000000  error 8.6e-02
iteration 2: 1.416666666666667  error 2.5e-03
iteration 3: 1.414215686274510  error 2.1e-06
iteration 4: 1.414213562374690  error 1.6e-12
iteration 5: 1.414213562373095  error 0.0e+00
fixed point of cos: 0.7390851332 after 58 iterations
Newton on cos(x) - x: 0.7390851332 after 5 iterations
```

Newton's iterates for $\sqrt2$ show quadratic convergence: the error goes $8.6 \times 10^{-2}$, $2.5 \times 10^{-3}$, $2.1 \times 10^{-6}$, $1.6 \times 10^{-12}$, roughly squaring each time, until it reaches the limit of double precision. Fixed-point iteration $x \leftarrow \cos x$ converges because $|g'(r)| = |\sin r| \approx 0.67 < 1$, but only linearly, taking 58 iterations; Newton's method on $\cos x - x$ needs 5.

### Example 2: Choosing a convergent rearrangement

Solve $x^2 - x - 2 = 0$ (roots 2 and $-1$) by fixed-point iteration near $r = 2$.

- $x = x^2 - 2$: $g'(x) = 2x$, so $|g'(2)| = 4 > 1$: **diverges**. From $x_0 = 2.1$: 2.41, 3.81, 12.5, ...
- $x = \sqrt{x + 2}$: $g'(x) = \frac{1}{2\sqrt{x + 2}}$, so $|g'(2)| = \frac14 < 1$: **converges**. From $x_0 = 3$: $\sqrt5 \approx 2.236$, $\sqrt{4.236} \approx 2.058$, $2.014$, $2.004$, ... with each error about a quarter of the previous one.
- $x = 1 + \frac{2}{x}$: $g'(x) = -\frac{2}{x^2}$, so $|g'(2)| = \frac12$: converges, more slowly, alternating around 2.

The derivative condition predicts in advance which rearrangement works.

## Applications

- **Hardware and libraries:** square roots and reciprocals are computed with Newton iterations.
- **Optimisation:** Newton's method for minimisation solves $\nabla f = \mathbf{0}$ using the Hessian.
- **Engineering simulation:** nonlinear circuit and structural equations are solved with Newton-Raphson.
- **Economics and game theory:** equilibria are fixed points of best-response maps.

## Common mistakes

- **Starting far from the root.** Newton's method may diverge or find a different root.
- **Ignoring $f'(x_n) \approx 0$.** Check the derivative before dividing.
- **Expecting quadratic convergence at multiple roots.** It becomes linear.
- **Iterating a fixed-point form with $|g'| > 1$.** It diverges; rearrange the equation.
- **No iteration limit.** Always cap the number of iterations.

## Revision notes

- Newton: $x_{n+1} = x_n - f(x_n)/f'(x_n)$ (tangent-line root).
- Quadratic convergence near a simple root: correct digits roughly double each step.
- Failures: zero derivative, bad start, cycles, multiple roots (linear convergence).
- Fixed point $x = g(x)$; converges if $|g'(r)| < 1$, rate $|g'(r)|$.
- Newton is fixed-point iteration with $g'(r) = 0$.
- Combine with bisection for robustness.

## Practice questions

:::question basic
Write Newton's iteration for $f(x) = x^3 - 5$ and perform one step from $x_0 = 2$.
:::answer
$x_{n+1} = x_n - \frac{x_n^3 - 5}{3x_n^2}$. From $x_0 = 2$: $x_1 = 2 - \frac{8 - 5}{12} = 2 - 0.25 = 1.75$. (The true root is $\sqrt[3]{5} \approx 1.71$.)
:::

:::question basic
What does quadratic convergence mean in terms of correct digits?
:::answer
Each error is roughly proportional to the square of the previous one, so once the iterates are close, the number of correct digits approximately doubles at every step, for example 2, 4, 8, 16 digits.
:::

:::question intermediate
For the iteration $x_{n+1} = \frac{1}{2}\left(x_n + \frac{10}{x_n}\right)$, what number does it converge to and why?
:::answer
It converges to $\sqrt{10} \approx 3.1623$. It is Newton's method for $f(x) = x^2 - 10$: $x - \frac{x^2 - 10}{2x} = \frac12\left(x + \frac{10}{x}\right)$, whose positive fixed point satisfies $x^2 = 10$.
:::

:::question intermediate
Does fixed-point iteration $x_{n+1} = e^{-x_n}$ converge to the solution of $x = e^{-x}$ near 0.567?
:::answer
Yes. With $g(x) = e^{-x}$, $|g'(x)| = e^{-x} \approx 0.567 < 1$ near the fixed point, so the iteration converges linearly, each error shrinking by a factor of about 0.567.
:::

:::question advanced
Explain why Newton's method converges only linearly at the double root of $f(x) = (x - 1)^2$, and show the rate.
:::answer
Here $f'(1) = 0$, so the root is not simple. The iteration is $x_{n+1} = x_n - \frac{(x_n - 1)^2}{2(x_n - 1)} = x_n - \frac{x_n - 1}{2}$, so $e_{n+1} = \frac12 e_n$: the error only halves each step, linear convergence like bisection. Using $x_{n+1} = x_n - 2\frac{f(x_n)}{f'(x_n)}$ (multiplying the step by the root's multiplicity) restores quadratic convergence.
:::

## Further learning

- **Next:** *Polynomial Interpolation: Lagrange & Newton* approximates functions from sample points.
- **Related:** *Gradients, Jacobians & Hessians* in Calculus generalises Newton's method to several variables.
