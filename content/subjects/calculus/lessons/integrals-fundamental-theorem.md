---
lesson: integrals-fundamental-theorem
title: Integrals & the Fundamental Theorem of Calculus
summary: Area and accumulation as limits of Riemann sums, the definite integral and its properties, antiderivatives and indefinite integrals, and the Fundamental Theorem of Calculus that links integration to differentiation.
minutes: 50
type: theory
objectives:
  - Approximate definite integrals with left, right, and midpoint Riemann sums and interpret them as signed area or accumulation
  - Find antiderivatives with basic rules and evaluate definite integrals using the Fundamental Theorem of Calculus
  - Use properties of definite integrals and differentiate accumulation functions with the first part of the theorem
review: ai-draft
---
## Introduction

Derivatives measure how fast something changes; integrals add up the change. If you know a car's speed at every moment, integration gives the total distance travelled; if you know a rate of water flow, it gives the total volume. Integration began as a way to compute areas under curves by slicing them into thin rectangles, and the **Fundamental Theorem of Calculus** reveals the astonishing fact that this area problem is the reverse of differentiation.

**Before you start:** you should know limits, derivatives of standard functions, and summation notation.

## Core theory

### Riemann sums

To find the area under $y = f(x)$ from $a$ to $b$, divide $[a, b]$ into $n$ strips of width $\Delta x = \frac{b - a}{n}$ and add up rectangles whose heights are values of $f$ in each strip:

$$\sum_{i=1}^{n} f(x_i^*)\,\Delta x$$

Choosing the left endpoints, right endpoints, or midpoints gives left, right, and **midpoint** sums. For an increasing function the left sum underestimates and the right sum overestimates. The midpoint sum is usually much more accurate.

### The definite integral

The **definite integral** is the limit of Riemann sums as the strips become infinitely thin:

$$\int_a^b f(x)\,dx = \lim_{n \to \infty}\sum_{i=1}^n f(x_i^*)\,\Delta x$$

It exists for every continuous function. It is **signed area**: area above the x-axis counts positively and area below negatively. If $f$ is a rate, the integral is the **net accumulated change**. Properties: linearity, $\int_a^b f + \int_b^c f = \int_a^c f$, $\int_a^a f = 0$, and $\int_b^a f = -\int_a^b f$.

### Antiderivatives

$F$ is an **antiderivative** of $f$ if $F' = f$. Antiderivatives differ only by a constant, so the **indefinite integral** is written $\int f(x)\,dx = F(x) + C$. Basic rules reverse differentiation:

| $f(x)$ | $\int f(x)\,dx$ |
| :--- | :--- |
| $x^n$ ($n \ne -1$) | $\frac{x^{n+1}}{n + 1} + C$ |
| $\frac{1}{x}$ | $\ln|x| + C$ |
| $e^x$ | $e^x + C$ |
| $\cos x$ | $\sin x + C$ |
| $\sin x$ | $-\cos x + C$ |

### The Fundamental Theorem of Calculus

**Part 1:** if $f$ is continuous on $[a, b]$, the accumulation function $A(x) = \int_a^x f(t)\,dt$ is differentiable and

$$A'(x) = f(x)$$

so integration followed by differentiation gives back the original function.

**Part 2:** if $F$ is any antiderivative of $f$, then

$$\int_a^b f(x)\,dx = F(b) - F(a)$$

so instead of computing limits of sums, we find an antiderivative and evaluate it at the endpoints. With the chain rule, Part 1 gives $\frac{d}{dx}\int_a^{g(x)} f(t)\,dt = f(g(x))\,g'(x)$.

### Average value

The average value of $f$ on $[a, b]$ is $\frac{1}{b - a}\int_a^b f(x)\,dx$, the height of the rectangle with the same area.

## Worked examples

### Example 1: Riemann sums converging to the integral

Approximate $\int_0^3 x^2\,dx$ with left, right, and midpoint sums for increasing $n$, and compare with the Fundamental Theorem.

```python
from math import pi, sin

def riemann(f, a, b, n, rule):
    h = (b - a) / n
    if rule == "left":
        return h * sum(f(a + i * h) for i in range(n))
    if rule == "right":
        return h * sum(f(a + (i + 1) * h) for i in range(n))
    return h * sum(f(a + (i + 0.5) * h) for i in range(n))

f = lambda x: x * x
for n in (4, 40, 400):
    print(n, [round(riemann(f, 0, 3, n, r), 5) for r in ("left", "right", "mid")])
print("exact by the Fundamental Theorem: F(3) - F(0) =", 3**3 / 3)
print("area under sin on [0, pi]:", round(riemann(sin, 0, pi, 1000, "mid"), 6), "(exact: 2)")
```

Output:

```text
4 [5.90625, 12.65625, 8.85938]
40 [8.66531, 9.34031, 8.99859]
400 [8.96628, 9.03378, 8.99999]
exact by the Fundamental Theorem: F(3) - F(0) = 9.0
area under sin on [0, pi]: 2.000001 (exact: 2)
```

Each row shows the left, right, and midpoint sums. As $n$ grows, all three approach 9, the exact value from $F(x) = \frac{x^3}{3}$: $F(3) - F(0) = 9$. The left sums are too small and the right sums too large because $x^2$ is increasing on $[0, 3]$, while the midpoint sums are far more accurate. The area under one arch of $\sin x$ is exactly 2, since $[-\cos x]_0^\pi = 1 - (-1) = 2$.

### Example 2: Net change and the first part of the theorem

**(a)** A particle moves with velocity $v(t) = t^2 - 4t + 3$ m/s for $0 \le t \le 3$. Its displacement is

$$\int_0^3 (t^2 - 4t + 3)\,dt = \left[\frac{t^3}{3} - 2t^2 + 3t\right]_0^3 = 9 - 18 + 9 = 0$$

so it ends where it started. Its total distance is larger: $v(t) = (t - 1)(t - 3)$ is positive on $(0, 1)$ and negative on $(1, 3)$, so the distance is $\int_0^1 v\,dt - \int_1^3 v\,dt = \frac43 + \frac43 = \frac83$ m.

**(b)** If $G(x) = \int_1^{x^2} \sqrt{1 + t^3}\,dt$, then by Part 1 and the chain rule, $G'(x) = \sqrt{1 + x^6} \cdot 2x$, even though the integral itself has no elementary formula.

## Applications

- **Physics:** distance from velocity, work from force, charge from current.
- **Probability:** probabilities are areas under density functions.
- **Economics:** total cost from marginal cost, consumer surplus.
- **Computing:** numerical integration methods are refined Riemann sums.

## Common mistakes

- **Forgetting $+ C$ in indefinite integrals.**
- **Confusing displacement with distance.** Split the integral where the velocity changes sign.
- **Using $\frac{x^{n+1}}{n+1}$ for $n = -1$.** The antiderivative of $\frac1x$ is $\ln|x|$.
- **Subtracting in the wrong order.** It is $F(b) - F(a)$, upper limit first.
- **Treating negative integrals as negative area.** Area is non-negative; signed area can be negative.

## Revision notes

- Riemann sum $\sum f(x_i^*)\Delta x$; left, right, midpoint; limit gives the integral.
- Definite integral = signed area = net accumulation.
- Antiderivative $F' = f$; indefinite integral $F(x) + C$.
- FTC 1: $\frac{d}{dx}\int_a^x f(t)\,dt = f(x)$; with chain rule for variable limits.
- FTC 2: $\int_a^b f = F(b) - F(a)$.
- Average value $\frac{1}{b-a}\int_a^b f$.

## Practice questions

:::question basic
Evaluate $\int_1^2 (3x^2 + 2)\,dx$.
:::answer
An antiderivative is $x^3 + 2x$. Evaluating, $(8 + 4) - (1 + 2) = 12 - 3 = 9$.
:::

:::question basic
Find $\int (4e^x - \frac{2}{x})\,dx$.
:::answer
$4e^x - 2\ln|x| + C$, using the antiderivatives of $e^x$ and $\frac1x$.
:::

:::question intermediate
Compute the left Riemann sum for $\int_0^2 x^3\,dx$ with $n = 4$ and compare it with the exact value.
:::answer
$\Delta x = 0.5$ and the left endpoints are 0, 0.5, 1, 1.5, so the sum is $0.5(0 + 0.125 + 1 + 3.375) = 2.25$. The exact value is $\frac{2^4}{4} = 4$; the left sum underestimates because $x^3$ is increasing.
:::

:::question intermediate
Find $\frac{d}{dx}\int_0^{x} \cos(t^2)\,dt$ and $\frac{d}{dx}\int_0^{3x} \cos(t^2)\,dt$.
:::answer
By the first part of the Fundamental Theorem, the first is $\cos(x^2)$. With the chain rule, the second is $\cos((3x)^2)\cdot 3 = 3\cos(9x^2)$.
:::

:::question advanced
Find the average value of $f(x) = \sin x$ on $[0, \pi]$ and interpret it.
:::answer
The average value is $\frac{1}{\pi}\int_0^\pi \sin x\,dx = \frac{1}{\pi}[-\cos x]_0^\pi = \frac{2}{\pi} \approx 0.637$. A rectangle of height $\frac{2}{\pi}$ over $[0, \pi]$ has the same area, 2, as one arch of the sine curve.
:::

## Further learning

- **Next:** *Integration Techniques & Applications* handles integrals the basic rules cannot.
- **Related:** *Numerical Integration: Trapezoidal & Simpson's Rules* in Numerical Methods improves on Riemann sums.
