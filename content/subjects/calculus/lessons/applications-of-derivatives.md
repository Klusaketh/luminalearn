---
lesson: applications-of-derivatives
title: Applications of Derivatives
summary: Using derivatives to find maxima and minima, test critical points with the first and second derivative tests, sketch curves using monotonicity and concavity, solve optimisation and related-rates problems, and evaluate limits with L'Hôpital's rule.
minutes: 55
type: theory
objectives:
  - Find critical points and classify them as maxima, minima, or neither with the first and second derivative tests
  - Solve optimisation problems by modelling a quantity, differentiating, and checking endpoints and constraints
  - Apply related rates, linear approximation, and L'Hôpital's rule to indeterminate limits
review: ai-draft
---
## Introduction

Derivatives answer practical questions. What box dimensions hold the most volume? At what price is profit greatest? How fast is the water level rising in a cone-shaped tank? What does a graph look like without plotting it point by point? This lesson turns the rules of differentiation into tools for optimisation, curve analysis, and modelling change, the same ideas that drive gradient-based optimisation in machine learning.

**Before you start:** you should know how to differentiate with the power, product, quotient, and chain rules.

## Core theory

### Critical points and extrema

A **critical point** of $f$ is a point where $f'(x) = 0$ or $f'$ does not exist. Local maxima and minima of a differentiable function occur only at critical points (Fermat's theorem), but not every critical point is an extremum: $f(x) = x^3$ has $f'(0) = 0$ and no extremum there.

- **First derivative test:** if $f'$ changes from positive to negative at $c$, $f$ has a local maximum; from negative to positive, a local minimum; no sign change, neither.
- **Second derivative test:** if $f'(c) = 0$ and $f''(c) < 0$, local maximum; $f''(c) > 0$, local minimum; $f''(c) = 0$, the test is inconclusive.

On a closed interval $[a, b]$, a continuous function attains an **absolute** maximum and minimum (the extreme value theorem); find them by comparing $f$ at the critical points inside and at both endpoints.

### Shape of a graph

- $f' > 0$: increasing; $f' < 0$: decreasing.
- $f'' > 0$: **concave up** (like a cup); $f'' < 0$: concave down.
- An **inflection point** is where concavity changes.

Together with intercepts and asymptotes, these give a reliable sketch.

### Optimisation

1. Draw a picture and name the variables.
2. Write the quantity to optimise as a function of **one** variable, using constraints to eliminate the others.
3. Find the domain (physical limits).
4. Find critical points and compare with the endpoints.
5. Answer the question asked, with units.

### Related rates

When several quantities change with time and are linked by an equation, differentiate the equation with respect to $t$ (using the chain rule) to relate their rates, then substitute the known values **after** differentiating.

### Linear approximation and L'Hôpital's rule

Near $a$, $f(x) \approx f(a) + f'(a)(x - a)$: the tangent line approximates the function, as in $\sqrt{4.1} \approx 2 + \frac{1}{4}(0.1) = 2.025$.

**L'Hôpital's rule:** if $\lim \frac{f(x)}{g(x)}$ has the form $\frac00$ or $\frac{\infty}{\infty}$, then $\lim \frac{f(x)}{g(x)} = \lim \frac{f'(x)}{g'(x)}$ when the latter exists. For example $\lim_{x \to 0}\frac{e^x - 1}{x} = \lim_{x \to 0}\frac{e^x}{1} = 1$. Other indeterminate forms ($0 \cdot \infty$, $\infty - \infty$, $1^\infty$) must first be rewritten as a quotient.

## Worked examples

### Example 1: The open-box problem

Squares of side $x$ are cut from the corners of a 20 cm × 12 cm sheet, and the sides are folded up to make an open box. Which $x$ maximises the volume?

The volume is $V(x) = x(20 - 2x)(12 - 2x) = 4x^3 - 64x^2 + 240x$ for $0 < x < 6$. Then $V'(x) = 12x^2 - 128x + 240$ and $V''(x) = 24x - 128$.

```python
from math import sqrt

def volume(x):
    return x * (20 - 2 * x) * (12 - 2 * x)

def dvolume(x):
    return 12 * x * x - 128 * x + 240

a, b, c = 12, -128, 240
roots = [(-b - sqrt(b * b - 4 * a * c)) / (2 * a), (-b + sqrt(b * b - 4 * a * c)) / (2 * a)]
valid = [r for r in roots if 0 < r < 6]
best = valid[0]
print("critical points:", [round(r, 4) for r in roots], "| inside (0, 6):", [round(r, 4) for r in valid])
print(f"second derivative at {best:.4f}: {24 * best - 128:.2f} (negative -> maximum)")
print(f"maximum volume {volume(best):.2f} with cut {best:.4f}")
grid = max((volume(i / 1000), i / 1000) for i in range(1, 6000))
print(f"grid search check: {grid[0]:.2f} at x = {grid[1]}")
```

Output:

```text
critical points: [2.4274, 8.2393] | inside (0, 6): [2.4274]
second derivative at 2.4274: -69.74 (negative -> maximum)
maximum volume 262.68 with cut 2.4274
grid search check: 262.68 at x = 2.427
```

The quadratic $V'(x) = 0$ has two roots, but only $x \approx 2.43$ lies in the physical domain. There $V'' < 0$, so it is a maximum, giving about 262.7 cm³. Volume is 0 at both ends of the domain ($x = 0$ and $x = 6$), so this is the absolute maximum, and a brute-force grid search agrees.

### Example 2: Related rates and L'Hôpital

**(a)** Water flows into an inverted cone of radius 3 m and height 6 m at 2 m³/min. How fast is the water level rising when the depth is 4 m?

By similar triangles the water's radius is $r = h/2$, so $V = \frac13\pi r^2 h = \frac{\pi h^3}{12}$. Differentiating with respect to time: $\frac{dV}{dt} = \frac{\pi h^2}{4}\frac{dh}{dt}$. At $h = 4$: $2 = 4\pi\frac{dh}{dt}$, so $\frac{dh}{dt} = \frac{1}{2\pi} \approx 0.159$ m/min.

**(b)** Evaluate $\lim_{x \to 0}\frac{1 - \cos x}{x^2}$. It is $\frac00$; applying L'Hôpital's rule twice gives $\lim \frac{\sin x}{2x} = \lim \frac{\cos x}{2} = \frac12$.

## Applications

- **Engineering and design:** minimising material or cost subject to constraints.
- **Economics:** profit is maximised where marginal revenue equals marginal cost.
- **Machine learning:** training minimises a loss function by moving against its derivative.
- **Physics:** related rates connect changing volumes, distances, and angles.

## Common mistakes

- **Forgetting endpoints.** Absolute extrema can occur at the boundary.
- **Assuming every critical point is an extremum.** Check with a derivative test.
- **Substituting values before differentiating in related rates.** Differentiate first.
- **Applying L'Hôpital's rule to non-indeterminate forms.** It gives wrong answers there.
- **Using the quotient rule in L'Hôpital.** Differentiate numerator and denominator separately.

## Revision notes

- Critical points: $f'(c) = 0$ or undefined; extrema of differentiable functions occur there.
- First derivative test: sign change of $f'$; second derivative test: sign of $f''(c)$.
- Absolute extrema on $[a, b]$: compare critical points and endpoints.
- $f' > 0$ increasing; $f'' > 0$ concave up; inflection where concavity changes.
- Related rates: relate quantities, differentiate in $t$, then substitute.
- $f(x) \approx f(a) + f'(a)(x - a)$; L'Hôpital for $\frac00$ and $\frac{\infty}{\infty}$.

## Practice questions

:::question basic
Find the critical points of $f(x) = x^3 - 3x$ and classify them.
:::answer
$f'(x) = 3x^2 - 3 = 0$ gives $x = \pm 1$. $f''(x) = 6x$: $f''(1) = 6 > 0$, so $x = 1$ is a local minimum ($f = -2$); $f''(-1) = -6 < 0$, so $x = -1$ is a local maximum ($f = 2$).
:::

:::question basic
Use linear approximation to estimate $\sqrt{9.2}$.
:::answer
With $f(x) = \sqrt{x}$, $a = 9$, $f'(9) = \frac{1}{2\sqrt9} = \frac16$: $\sqrt{9.2} \approx 3 + \frac16(0.2) \approx 3.0333$. The true value is about 3.0332.
:::

:::question intermediate
A farmer has 100 m of fencing to enclose a rectangular field along a straight river, with no fence needed on the river side. What dimensions maximise the area?
:::answer
Let the two sides perpendicular to the river be $x$ and the parallel side $100 - 2x$. Area $A = x(100 - 2x) = 100x - 2x^2$, so $A'(x) = 100 - 4x = 0$ gives $x = 25$. The field is 25 m by 50 m with area 1250 m²; $A'' = -4 < 0$ confirms a maximum.
:::

:::question intermediate
Evaluate $\lim_{x \to \infty}\frac{\ln x}{x}$.
:::answer
It has the form $\frac{\infty}{\infty}$, so by L'Hôpital's rule it equals $\lim_{x \to \infty}\frac{1/x}{1} = 0$. Logarithms grow more slowly than any positive power of $x$.
:::

:::question advanced
Show that among all rectangles with perimeter $P$, the square has the largest area.
:::answer
Let the sides be $x$ and $\frac{P}{2} - x$, so the area is $A(x) = x\left(\frac{P}{2} - x\right)$ for $0 < x < \frac{P}{2}$. Then $A'(x) = \frac{P}{2} - 2x = 0$ gives $x = \frac{P}{4}$, and $A'' = -2 < 0$, so this is the maximum. Both sides equal $\frac{P}{4}$: the rectangle is a square, with area $\frac{P^2}{16}$.
:::

## Further learning

- **Next:** *Integrals & the Fundamental Theorem of Calculus* reverses differentiation.
- **Related:** *Newton-Raphson & Fixed-Point Iteration* in Numerical Methods uses derivatives to find roots.
