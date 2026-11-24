---
lesson: integration-techniques
title: Integration Techniques & Applications
summary: Techniques for finding antiderivatives (substitution, integration by parts, partial fractions) and applications of integrals to areas between curves and volumes of solids of revolution, checked numerically.
minutes: 55
type: theory
objectives:
  - Evaluate integrals with u-substitution, including changing the limits of definite integrals
  - Apply integration by parts and partial-fraction decomposition to suitable integrands
  - Compute areas between curves and volumes of revolution with the disc method
review: ai-draft
---
## Introduction

The basic antiderivative rules handle polynomials and simple functions, but most integrals met in practice, such as $\int x e^x\,dx$ or $\int \frac{2x}{x^2 + 1}\,dx$, need a technique. Each technique reverses a differentiation rule: **substitution** reverses the chain rule, **integration by parts** reverses the product rule, and **partial fractions** split rational functions into simple pieces. With them, integrals become tools for computing areas, volumes, probabilities, and work.

**Before you start:** you should know antiderivatives, the Fundamental Theorem of Calculus, and the chain and product rules.

## Core theory

### Substitution

If the integrand has the form $f(g(x))g'(x)$, set $u = g(x)$, so $du = g'(x)\,dx$:

$$\int f(g(x))\,g'(x)\,dx = \int f(u)\,du$$

Look for an "inside function" whose derivative also appears (up to a constant factor). For example, $\int 2x\cos(x^2)\,dx$ with $u = x^2$ becomes $\int \cos u\,du = \sin(x^2) + C$. For definite integrals, either convert back to $x$ or **change the limits** to the corresponding $u$-values: $\int_a^b f(g(x))g'(x)\,dx = \int_{g(a)}^{g(b)} f(u)\,du$.

### Integration by parts

From the product rule, $(uv)' = u'v + uv'$, we get

$$\int u\,dv = uv - \int v\,du$$

Choose $u$ to become simpler when differentiated and $dv$ to be easy to integrate. A common guide is **LIATE** for choosing $u$: Logarithmic, Inverse trigonometric, Algebraic (polynomials), Trigonometric, Exponential. For $\int x e^x\,dx$: $u = x$, $dv = e^x dx$, so $\int x e^x\,dx = xe^x - \int e^x\,dx = e^x(x - 1) + C$. Sometimes parts must be applied twice, or the original integral reappears and can be solved for algebraically.

### Partial fractions

A proper rational function with a factorable denominator splits into simpler fractions:

$$\frac{1}{x(x + 1)} = \frac{A}{x} + \frac{B}{x + 1}$$

Multiplying through gives $1 = A(x + 1) + Bx$; setting $x = 0$ gives $A = 1$, and $x = -1$ gives $B = -1$. Each simple fraction integrates to a logarithm: $\int \frac{dx}{x(x + 1)} = \ln|x| - \ln|x + 1| + C$. Repeated factors need terms $\frac{A}{(x - a)^k}$ for each power, and irreducible quadratics need $\frac{Ax + B}{x^2 + bx + c}$. If the numerator's degree is not smaller than the denominator's, divide first.

### Area between curves

If $f(x) \ge g(x)$ on $[a, b]$, the area between them is

$$\int_a^b \left(f(x) - g(x)\right)dx$$

Find the intersection points to get the limits, and split the interval where the curves cross.

### Volumes of revolution

Rotating the region under $y = f(x)$ on $[a, b]$ about the x-axis produces a solid whose cross-sections are discs of radius $f(x)$. The **disc method** gives

$$V = \int_a^b \pi\,[f(x)]^2\,dx$$

and washers (discs with holes) handle regions between two curves.

## Worked examples

### Example 1: Four techniques, checked numerically

- **By parts:** $\int_0^1 xe^x\,dx = [e^x(x - 1)]_0^1 = 0 - (-1) = 1$.
- **Substitution:** $\int_0^2 \frac{2x}{x^2 + 1}\,dx$ with $u = x^2 + 1$ (limits 1 to 5) $= \int_1^5 \frac{du}{u} = \ln 5$.
- **Partial fractions:** $\int_1^3 \frac{dx}{x(x + 1)} = \left[\ln\frac{x}{x + 1}\right]_1^3 = \ln\frac34 - \ln\frac12 = \ln 1.5$.
- **Volume:** rotating $y = \sqrt{x}$ on $[0, 4]$ about the x-axis: $V = \int_0^4 \pi x\,dx = 8\pi$.

A numerical integrator (Simpson's rule, covered in Numerical Methods) confirms each result.

```python
from math import exp, log, pi

def simpson(f, a, b, n=1000):
    h = (b - a) / n
    s = f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, n))
    return s * h / 3

checks = [
    ("x e^x on [0,1] (by parts: 1)", lambda x: x * exp(x), 0, 1, 1.0),
    ("2x/(x^2+1) on [0,2] (substitution: ln 5)", lambda x: 2 * x / (x * x + 1), 0, 2, log(5)),
    ("1/(x(x+1)) on [1,3] (partial fractions: ln 1.5)", lambda x: 1 / (x * (x + 1)), 1, 3, log(1.5)),
    ("pi (sqrt x)^2 on [0,4] (volume: 8 pi)", lambda x: pi * x, 0, 4, 8 * pi),
]
for name, f, a, b, exact in checks:
    print(f"{name}: numeric {simpson(f, a, b):.6f}, exact {exact:.6f}")
```

Output:

```text
x e^x on [0,1] (by parts: 1): numeric 1.000000, exact 1.000000
2x/(x^2+1) on [0,2] (substitution: ln 5): numeric 1.609438, exact 1.609438
1/(x(x+1)) on [1,3] (partial fractions: ln 1.5): numeric 0.405465, exact 0.405465
pi (sqrt x)^2 on [0,4] (volume: 8 pi): numeric 25.132741, exact 25.132741
```

Every exact answer matches the numerical estimate to six decimal places, a good habit for catching algebra mistakes.

### Example 2: Area between two curves

Find the area enclosed by $y = x$ and $y = x^2$.

The curves meet where $x = x^2$, at $x = 0$ and $x = 1$. On $(0, 1)$, $x \ge x^2$ (for example at $x = 0.5$, $0.5 > 0.25$), so

$$A = \int_0^1 (x - x^2)\,dx = \left[\frac{x^2}{2} - \frac{x^3}{3}\right]_0^1 = \frac12 - \frac13 = \frac16$$

Rotating the same region about the x-axis gives a washer with outer radius $x$ and inner radius $x^2$: $V = \pi\int_0^1 (x^2 - x^4)\,dx = \pi\left(\frac13 - \frac15\right) = \frac{2\pi}{15}$.

## Applications

- **Probability:** integrating densities, such as $\int x\lambda e^{-\lambda x}dx$ for the exponential mean, uses integration by parts.
- **Physics:** work, centre of mass, and moments of inertia.
- **Engineering:** volumes of tanks and machine parts.
- **Signal processing:** Fourier coefficients are integrals evaluated by parts.

## Common mistakes

- **Not converting $dx$ in a substitution.** Every $x$, including $dx$, must be expressed in $u$.
- **Keeping the old limits after substituting.** Change them or convert back to $x$.
- **A poor choice of $u$ in integration by parts.** If the new integral is harder, swap the roles.
- **Forgetting to divide first.** Partial fractions require a proper rational function.
- **Subtracting curves in the wrong order.** Use upper minus lower; split where they cross.

## Revision notes

- Substitution reverses the chain rule: $u = g(x)$, $du = g'(x)dx$; change limits.
- By parts: $\int u\,dv = uv - \int v\,du$; choose $u$ by LIATE.
- Partial fractions: split proper rational functions; each piece gives a log (or arctan) term.
- Area between curves: $\int_a^b (f - g)\,dx$ with $f \ge g$.
- Disc method: $V = \pi\int_a^b f(x)^2\,dx$; washers subtract the inner radius squared.
- Check answers numerically when possible.

## Practice questions

:::question basic
Evaluate $\int 3x^2(x^3 + 1)^4\,dx$.
:::answer
Let $u = x^3 + 1$, so $du = 3x^2dx$. The integral becomes $\int u^4\,du = \frac{u^5}{5} + C = \frac{(x^3 + 1)^5}{5} + C$.
:::

:::question basic
Evaluate $\int x\cos x\,dx$.
:::answer
By parts with $u = x$ and $dv = \cos x\,dx$: $\int x\cos x\,dx = x\sin x - \int \sin x\,dx = x\sin x + \cos x + C$.
:::

:::question intermediate
Evaluate $\int \frac{5x + 1}{(x - 1)(x + 2)}\,dx$.
:::answer
Write $\frac{5x + 1}{(x - 1)(x + 2)} = \frac{A}{x - 1} + \frac{B}{x + 2}$, so $5x + 1 = A(x + 2) + B(x - 1)$. Setting $x = 1$ gives $A = 2$; $x = -2$ gives $B = 3$. The integral is $2\ln|x - 1| + 3\ln|x + 2| + C$.
:::

:::question intermediate
Find the volume when the region under $y = x^2$ on $[0, 2]$ is rotated about the x-axis.
:::answer
By the disc method, $V = \pi\int_0^2 (x^2)^2\,dx = \pi\int_0^2 x^4\,dx = \pi\frac{32}{5} = \frac{32\pi}{5}$.
:::

:::question advanced
Evaluate $\int e^x\sin x\,dx$ using integration by parts twice.
:::answer
Let $I = \int e^x\sin x\,dx$. Parts with $u = \sin x$, $dv = e^xdx$: $I = e^x\sin x - \int e^x\cos x\,dx$. Parts again with $u = \cos x$: $\int e^x\cos x\,dx = e^x\cos x + \int e^x\sin x\,dx = e^x\cos x + I$. So $I = e^x\sin x - e^x\cos x - I$, giving $I = \frac{e^x(\sin x - \cos x)}{2} + C$.
:::

## Further learning

- **Next:** *Sequences, Series & Taylor Expansions* approximates functions with polynomials.
- **Related:** *Numerical Integration: Trapezoidal & Simpson's Rules* in Numerical Methods computes integrals that have no closed form.
