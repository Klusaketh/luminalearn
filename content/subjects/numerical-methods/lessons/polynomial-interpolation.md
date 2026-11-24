---
lesson: polynomial-interpolation
title: Polynomial Interpolation: Lagrange & Newton
summary: Constructing the unique polynomial through a set of data points with the Lagrange form and with Newton's divided differences, estimating interpolation error, and avoiding Runge's phenomenon with Chebyshev nodes or piecewise interpolation.
minutes: 50
type: theory
objectives:
  - Construct interpolating polynomials in Lagrange form and in Newton form using divided differences
  - State the interpolation error formula and explain what controls the error
  - Recognise Runge's phenomenon and choose remedies such as Chebyshev nodes and piecewise (spline) interpolation
review: ai-draft
---
## Introduction

Data often comes as a table of values: temperatures every hour, a function evaluated at a few points, positions of a robot at sampled times. **Interpolation** estimates values in between by passing a smooth curve exactly through the data. Polynomials are the natural choice, since they are easy to evaluate, differentiate, and integrate, and interpolating polynomials are the foundation of numerical integration and differentiation formulas. They also come with a warning: more points do not always mean a better fit.

**Before you start:** you should know polynomials, systems of linear equations, and Taylor polynomials.

## Core theory

### Existence and uniqueness

Given $n + 1$ points $(x_0, y_0), \dots, (x_n, y_n)$ with distinct $x_i$, there is exactly **one** polynomial $p$ of degree at most $n$ with $p(x_i) = y_i$ for all $i$. Different construction methods produce the same polynomial written in different forms.

### Lagrange form

Build basis polynomials that are 1 at one node and 0 at all the others:

$$L_i(x) = \prod_{j \ne i}\frac{x - x_j}{x_i - x_j}, \qquad p(x) = \sum_{i=0}^{n} y_i L_i(x)$$

The Lagrange form is easy to write down and to reason about, but adding a new point means recomputing everything.

### Newton form and divided differences

The Newton form builds the polynomial incrementally:

$$p(x) = f[x_0] + f[x_0, x_1](x - x_0) + f[x_0, x_1, x_2](x - x_0)(x - x_1) + \cdots$$

The coefficients are **divided differences**, defined recursively:

$$f[x_i] = y_i, \qquad f[x_i, \dots, x_{i+k}] = \frac{f[x_{i+1}, \dots, x_{i+k}] - f[x_i, \dots, x_{i+k-1}]}{x_{i+k} - x_i}$$

Adding a new data point adds just one new term, and the form can be evaluated efficiently with nested multiplication. For data from a polynomial of degree $k$, all divided differences of order above $k$ are zero.

### Interpolation error

If $f$ has $n + 1$ continuous derivatives, then for each $x$ there is a $\xi$ in the interval spanned by the nodes and $x$ with

$$f(x) - p(x) = \frac{f^{(n+1)}(\xi)}{(n + 1)!}\prod_{i=0}^{n}(x - x_i)$$

The error depends on how large the higher derivatives of $f$ are and on the **node polynomial** $\prod(x - x_i)$, which is largest near the ends of the interval when nodes are equally spaced. **Extrapolating** outside the nodes is especially unreliable.

### Runge's phenomenon and remedies

For some smooth functions, such as $f(x) = \frac{1}{1 + 25x^2}$ on $[-1, 1]$, interpolating at more and more **equally spaced** points makes the polynomial oscillate wildly near the ends, and the error grows without bound. Remedies:

- **Chebyshev nodes** $x_i = \cos\left(\frac{(2i + 1)\pi}{2(n + 1)}\right)$ cluster near the ends and keep the node polynomial small, making high-degree interpolation reliable for smooth functions.
- **Piecewise interpolation:** use low-degree polynomials on subintervals, such as piecewise linear or **cubic splines**, which are smooth and avoid oscillation. Splines are the standard in graphics, CAD, and data plotting.

## Worked examples

### Example 1: Divided differences and Runge's phenomenon

The data $(1, 1), (2, 8), (4, 64), (5, 125)$ comes from $f(x) = x^3$. The program computes the Newton coefficients, interpolates at $x = 3$, and then interpolates Runge's function at 5, 11, and 21 equally spaced points.

```python
def lagrange(xs, ys, x):
    total = 0.0
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        term = yi
        for j, xj in enumerate(xs):
            if j != i:
                term *= (x - xj) / (xi - xj)
        total += term
    return total

def divided_differences(xs, ys):
    coef = list(ys)
    n = len(xs)
    for level in range(1, n):
        for i in range(n - 1, level - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - level])
    return coef

xs, ys = [1, 2, 4, 5], [1, 8, 64, 125]
print("Newton coefficients:", divided_differences(xs, ys))
print("interpolate x^3 data at 3:", round(lagrange(xs, ys, 3), 10))

runge = lambda x: 1 / (1 + 25 * x * x)
for n in (5, 11, 21):
    nodes = [-1 + 2 * i / (n - 1) for i in range(n)]
    values = [runge(x) for x in nodes]
    worst = max(abs(lagrange(nodes, values, t / 500) - runge(t / 500)) for t in range(-500, 501))
    print(f"{n} equally spaced points: max error {worst:.3f}")
```

Output:

```text
Newton coefficients: [1, 7.0, 7.0, 1.0]
interpolate x^3 data at 3: 27.0
5 equally spaced points: max error 0.438
11 equally spaced points: max error 1.916
21 equally spaced points: max error 59.768
```

The Newton coefficients are $1, 7, 7, 1$, so $p(x) = 1 + 7(x - 1) + 7(x - 1)(x - 2) + (x - 1)(x - 2)(x - 4)$, which expands to exactly $x^3$, and $p(3) = 27$. For Runge's function, the maximum error on $[-1, 1]$ grows from 0.44 to 1.92 to about 60 as the number of equally spaced points increases: adding points makes the interpolant worse, not better.

### Example 2: A Lagrange interpolant by hand

Find the quadratic through $(0, 1)$, $(1, 3)$, $(2, 7)$ and estimate the value at $x = 1.5$.

$$L_0(x) = \frac{(x - 1)(x - 2)}{(0 - 1)(0 - 2)} = \frac{(x - 1)(x - 2)}{2}, \quad L_1(x) = \frac{x(x - 2)}{(1)(-1)} = -x(x - 2), \quad L_2(x) = \frac{x(x - 1)}{(2)(1)}$$

$$p(x) = 1 \cdot L_0 + 3 \cdot L_1 + 7 \cdot L_2 = x^2 + x + 1$$

Check: $p(0) = 1$, $p(1) = 3$, $p(2) = 7$. Then $p(1.5) = 2.25 + 1.5 + 1 = 4.75$. The Newton form gives the same polynomial: $f[x_0, x_1] = 2$, $f[x_1, x_2] = 4$, $f[x_0, x_1, x_2] = \frac{4 - 2}{2 - 0} = 1$, so $p(x) = 1 + 2x + x(x - 1) = x^2 + x + 1$.

## Applications

- **Numerical integration and differentiation:** Simpson's rule and finite-difference formulas come from integrating or differentiating interpolants.
- **Computer graphics and CAD:** splines and Bézier curves draw smooth shapes.
- **Signal and image processing:** resampling and image scaling interpolate between samples.
- **Tables and look-up:** estimating values between tabulated measurements.

## Common mistakes

- **Using high-degree interpolation on equally spaced points.** Runge's phenomenon can make it useless; use Chebyshev nodes or splines.
- **Extrapolating far beyond the data.** Errors grow rapidly outside the nodes.
- **Repeated x-values.** Nodes must be distinct (otherwise use Hermite interpolation).
- **Confusing interpolation with regression.** Interpolation passes through every point; least-squares fitting does not and is better for noisy data.
- **Recomputing everything to add a point.** The Newton form adds one term.

## Revision notes

- $n + 1$ distinct points determine a unique polynomial of degree at most $n$.
- Lagrange: $p(x) = \sum y_iL_i(x)$ with $L_i(x_j) = \delta_{ij}$.
- Newton: coefficients are divided differences; adding a point adds a term.
- Error: $\frac{f^{(n+1)}(\xi)}{(n+1)!}\prod(x - x_i)$.
- Runge's phenomenon: equally spaced high-degree interpolation can diverge.
- Remedies: Chebyshev nodes, piecewise polynomials, cubic splines.

## Practice questions

:::question basic
How many points are needed to determine a unique cubic polynomial?
:::answer
Four points with distinct x-values. In general, $n + 1$ points determine a unique polynomial of degree at most $n$.
:::

:::question basic
Find the line (degree-1 interpolant) through $(2, 5)$ and $(4, 9)$, and estimate the value at 3.
:::answer
The slope is $(9 - 5)/(4 - 2) = 2$, so $p(x) = 5 + 2(x - 2)$ and $p(3) = 7$.
:::

:::question intermediate
Compute the divided differences for the points $(0, 1), (1, 2), (3, 10)$ and write the Newton form.
:::answer
$f[0, 1] = (2 - 1)/(1 - 0) = 1$ and $f[1, 3] = (10 - 2)/(3 - 1) = 4$, so $f[0, 1, 3] = (4 - 1)/(3 - 0) = 1$. The Newton form is $p(x) = 1 + 1(x - 0) + 1(x - 0)(x - 1) = x^2 + 1$; check $p(3) = 10$.
:::

:::question intermediate
Why are Chebyshev nodes better than equally spaced nodes for high-degree interpolation?
:::answer
The interpolation error contains the node polynomial $\prod(x - x_i)$. With equally spaced nodes this product becomes very large near the ends of the interval, driving Runge's oscillations. Chebyshev nodes cluster near the ends, which minimises the maximum size of the node polynomial, so the error stays small and decreases for smooth functions as the degree grows.
:::

:::question advanced
Use the error formula to bound the error of linear interpolation of $f(x) = \sin x$ between $x = 0$ and $x = 0.2$ at $x = 0.1$.
:::answer
For $n = 1$, $|f(x) - p(x)| = \frac{|f''(\xi)|}{2}|(x - 0)(x - 0.2)|$. Since $|f''| = |\sin\xi| \le \sin 0.2 \approx 0.199$ on $[0, 0.2]$, and $|(0.1)(0.1 - 0.2)| = 0.01$, the error is at most $\frac{0.199}{2} \times 0.01 \approx 0.001$. (The actual error is about $0.0005$.)
:::

## Further learning

- **Next:** *Numerical Integration: Trapezoidal & Simpson's Rules* integrates interpolating polynomials.
- **Related:** *Orthogonality, Projections & Least Squares* in Linear Algebra fits curves to noisy data instead.
