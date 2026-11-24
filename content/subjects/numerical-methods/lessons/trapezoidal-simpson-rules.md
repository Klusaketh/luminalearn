---
lesson: trapezoidal-simpson-rules
title: Numerical Integration: Trapezoidal & Simpson's Rules
summary: Approximating definite integrals with the trapezoidal rule and Simpson's rule, their composite forms and error terms, how the error scales with the step size, and choosing between them.
minutes: 45
type: theory
objectives:
  - Derive and apply the trapezoidal and Simpson's rules, including their composite forms
  - State the error terms and use them to predict how the error changes when the step size is halved
  - Choose an appropriate rule and number of subintervals for a required accuracy
review: ai-draft
---
## Introduction

Many integrals have no closed-form antiderivative: the normal-distribution integral $\int e^{-x^2}dx$, the arc length of an ellipse, or an integral of measured data. **Numerical integration** (quadrature) estimates them by integrating simple approximations of the integrand. The **trapezoidal** and **Simpson's** rules, built from linear and quadratic interpolation, are easy to implement and remarkably accurate, and their error terms tell you exactly how much work a given accuracy requires.

**Before you start:** you should know definite integrals, Riemann sums, and polynomial interpolation.

## Core theory

### Newton-Cotes formulas

**Newton-Cotes** rules integrate the interpolating polynomial through equally spaced points. Integrating the straight line through two points gives the trapezoidal rule; integrating the parabola through three points gives Simpson's rule.

### The trapezoidal rule

On one interval $[a, b]$: $\int_a^b f(x)\,dx \approx \frac{b - a}{2}\left(f(a) + f(b)\right)$. The **composite** rule divides $[a, b]$ into $n$ subintervals of width $h = \frac{b - a}{n}$:

$$T_n = h\left(\frac{f(x_0)}{2} + f(x_1) + \cdots + f(x_{n-1}) + \frac{f(x_n)}{2}\right)$$

Its error is

$$E_T = -\frac{(b - a)h^2}{12}f''(\xi)$$

for some $\xi$ in $[a, b]$. The error is **second order**: halving $h$ divides it by about 4. The rule is exact for straight lines, overestimates for concave-up functions, and underestimates for concave-down ones. (For smooth periodic functions integrated over a full period, it is spectacularly accurate.)

### Simpson's rule

Using parabolas through pairs of subintervals ($n$ must be **even**):

$$S_n = \frac{h}{3}\left(f(x_0) + 4f(x_1) + 2f(x_2) + 4f(x_3) + \cdots + 2f(x_{n-2}) + 4f(x_{n-1}) + f(x_n)\right)$$

Its error is

$$E_S = -\frac{(b - a)h^4}{180}f^{(4)}(\xi)$$

**fourth order**: halving $h$ divides the error by about 16. Surprisingly, it is exact for cubics, not just quadratics, because of a symmetry cancellation. Simpson's rule equals a weighted combination of trapezoidal results, $S_{2n} = \frac{4T_{2n} - T_n}{3}$, an example of **Richardson extrapolation**, which removes the leading error term.

### Choosing $n$

From the error bounds, the number of subintervals needed for a tolerance $\varepsilon$ can be computed in advance if a bound on $|f''|$ or $|f^{(4)}|$ is known. In practice, **adaptive** quadrature compares estimates at two step sizes and refines only where the integrand is difficult. For smooth functions, higher-order methods such as Gaussian quadrature reach high accuracy with very few evaluations.

## Worked examples

### Example 1: Error behaviour on $\int_0^\pi \sin x\,dx = 2$

```python
from math import exp, pi, sin

def trapezoid(f, a, b, n):
    h = (b - a) / n
    return h * (f(a) / 2 + sum(f(a + i * h) for i in range(1, n)) + f(b) / 2)

def simpson(f, a, b, n):
    h = (b - a) / n
    return h / 3 * (f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, n)))

exact = 2.0
print(" n   trapezoid error   simpson error")
for n in (4, 8, 16, 32):
    print(f"{n:>2}   {abs(trapezoid(sin, 0, pi, n) - exact):.3e}         {abs(simpson(sin, 0, pi, n) - exact):.3e}")
print("integral of exp(-x^2) on [0, 1] by Simpson, n = 10:", round(simpson(lambda x: exp(-x * x), 0, 1, 10), 8))
```

Output:

```text
 n   trapezoid error   simpson error
 4   1.039e-01         4.560e-03
 8   2.577e-02         2.692e-04
16   6.430e-03         1.659e-05
32   1.607e-03         1.033e-06
integral of exp(-x^2) on [0, 1] by Simpson, n = 10: 0.74682495
```

Each doubling of $n$ divides the trapezoidal error by about 4 (from $1.04 \times 10^{-1}$ to $2.58 \times 10^{-2}$ to $6.43 \times 10^{-3}$) and the Simpson error by about 16 (from $4.56 \times 10^{-3}$ to $2.69 \times 10^{-4}$ to $1.66 \times 10^{-5}$), exactly as the $h^2$ and $h^4$ error terms predict. Simpson's rule with only 10 subintervals gives $\int_0^1 e^{-x^2}dx \approx 0.74682495$; the true value is $0.746824133\ldots$, so the error is under $10^{-6}$ for a function with no elementary antiderivative.

### Example 2: Both rules by hand, and planning $n$

Estimate $\int_0^2 x^3\,dx$ (exact value 4) with $n = 2$ ($h = 1$; points 0, 1, 2 with values 0, 1, 8).

- Trapezoidal: $T_2 = 1\left(\frac02 + 1 + \frac82\right) = 5$, an error of 1 (overestimate, since $x^3$ is concave up on $[0, 2]$).
- Simpson: $S_2 = \frac13(0 + 4 \cdot 1 + 8) = 4$, exact, because Simpson's rule integrates cubics exactly.

How many trapezoidal subintervals guarantee an error below $10^{-6}$ for $\int_0^1 e^{-x^2}dx$? On $[0, 1]$, $|f''(x)| = |(4x^2 - 2)e^{-x^2}| \le 2$. We need $\frac{1 \cdot h^2}{12} \cdot 2 \le 10^{-6}$, so $h \le \sqrt{6 \times 10^{-6}} \approx 0.00245$ and $n \ge 409$. Simpson's rule, with $|f^{(4)}| \le 12$, needs only $\frac{h^4}{180} \cdot 12 \le 10^{-6}$, so $h \le 0.062$ and $n \ge 18$ (even): 19 function evaluations instead of 410, more than 20 times fewer. The bounds are cautious: Example 1 shows that $n = 10$ already meets the tolerance in practice.

## Applications

- **Probability and statistics:** normal and other distribution functions without closed forms.
- **Engineering:** areas, volumes, and work from measured data at regular intervals.
- **Physics simulations:** energy and flux integrals over grids.
- **Finance:** pricing integrals for options and risk measures.

## Common mistakes

- **Using Simpson's rule with an odd number of subintervals.** $n$ must be even.
- **Wrong weights.** Trapezoidal ends get $\frac12$; Simpson's pattern is 1, 4, 2, 4, ..., 2, 4, 1.
- **Expecting halving $h$ to halve the error.** Trapezoidal errors fall by 4 and Simpson's by 16.
- **Ignoring non-smooth integrands.** Error formulas assume bounded derivatives; split the interval at kinks or singularities.
- **Forgetting the factor $h/3$ in Simpson's rule.**

## Revision notes

- Trapezoidal: $T_n = h\left(\frac{f_0}{2} + f_1 + \cdots + f_{n-1} + \frac{f_n}{2}\right)$; error $-\frac{(b-a)h^2}{12}f''(\xi)$.
- Simpson ($n$ even): $\frac{h}{3}(f_0 + 4f_1 + 2f_2 + \cdots + 4f_{n-1} + f_n)$; error $-\frac{(b-a)h^4}{180}f^{(4)}(\xi)$.
- Halving $h$: trapezoidal error ÷ 4, Simpson error ÷ 16.
- Simpson is exact for cubics; trapezoidal for lines.
- $S_{2n} = (4T_{2n} - T_n)/3$ (Richardson extrapolation).
- Plan $n$ from derivative bounds or use adaptive quadrature.

## Practice questions

:::question basic
Apply the trapezoidal rule with one interval to $\int_1^3 \frac1x\,dx$.
:::answer
$\frac{3 - 1}{2}\left(1 + \frac13\right) = 1 \times \frac43 \approx 1.333$. The exact value is $\ln 3 \approx 1.0986$; one trapezoid overestimates because $\frac1x$ is concave up.
:::

:::question basic
If the trapezoidal rule has error $8 \times 10^{-4}$ with $n = 10$, roughly what error do you expect with $n = 20$?
:::answer
The error is proportional to $h^2$, so halving $h$ divides it by about 4, giving roughly $2 \times 10^{-4}$.
:::

:::question intermediate
Apply Simpson's rule with $n = 2$ to $\int_0^1 e^x\,dx$ and compare with the exact value.
:::answer
$h = 0.5$ with values $e^0 = 1$, $e^{0.5} \approx 1.6487$, $e^1 \approx 2.7183$. $S_2 = \frac{0.5}{3}(1 + 4 \times 1.6487 + 2.7183) \approx \frac{0.5}{3}(10.3131) \approx 1.71886$. The exact value is $e - 1 \approx 1.71828$, so the error is about $5.8 \times 10^{-4}$ with only three function values.
:::

:::question intermediate
Why is Simpson's rule exact for cubic polynomials even though it is built from parabolas?
:::answer
On each pair of subintervals, the cubic's difference from the interpolating parabola is a multiple of $(x - x_0)(x - x_1)(x - x_2)$, which is antisymmetric about the midpoint $x_1$, so its integral over the symmetric pair is zero. The error term confirms this: it involves the fourth derivative, which is zero for any cubic.
:::

:::question advanced
Given trapezoidal estimates $T_4 = 2.0950$ and $T_8 = 2.0239$ of some integral, use Richardson extrapolation to improve the estimate.
:::answer
Because the trapezoidal error is proportional to $h^2$, the combination $\frac{4T_8 - T_4}{3}$ cancels the leading error term: $\frac{4 \times 2.0239 - 2.0950}{3} = \frac{8.0956 - 2.0950}{3} = \frac{6.0006}{3} = 2.0002$. This equals Simpson's rule with $n = 8$ and is typically far more accurate than either trapezoidal estimate.
:::

## Further learning

- **Next:** *Runge-Kutta (RK4) Method* applies similar weighted averages to differential equations.
- **Related:** *Integrals & the Fundamental Theorem of Calculus* in Calculus introduces the Riemann sums these rules improve on.
