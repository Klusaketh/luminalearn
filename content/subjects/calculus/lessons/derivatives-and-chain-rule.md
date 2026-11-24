---
lesson: derivatives-and-chain-rule
title: Derivatives & The Chain Rule
summary: The derivative as a limit and as an instantaneous rate of change, differentiation rules (power, product, quotient), derivatives of exponential, logarithmic, and trigonometric functions, the chain rule for compositions, implicit differentiation, and numerical derivatives.
minutes: 45
type: theory
objectives:
  - Define the derivative as a limit and interpret it as a slope and a rate of change
  - Differentiate functions using the power, product, quotient, and chain rules and standard derivatives
  - Use implicit differentiation and estimate derivatives numerically with finite differences
review: ai-draft
---
## Introduction

The derivative measures how fast something changes: the velocity of a moving object, the rate at which a population grows, the sensitivity of a model's error to one of its parameters. Training a neural network, optimising a design, and modelling physical systems all rely on derivatives. This lesson builds the derivative from limits and develops the rules, especially the **chain rule**, that let you differentiate almost any formula, including the compositions of functions that make up machine-learning models.

**Before you start:** you should know limits, function notation, and basic algebra with exponents, logarithms, and trigonometric functions.

## Core theory

### Definition

The derivative of $f$ at $x$ is

$$f'(x) = \lim_{h \to 0}\frac{f(x + h) - f(x)}{h}$$

if the limit exists. Geometrically it is the **slope of the tangent line**; physically it is the **instantaneous rate of change**. Other notations: $\frac{dy}{dx}$, $\frac{d}{dx}f(x)$. A function differentiable at a point is continuous there, but not conversely: $|x|$ is continuous at 0 but has a corner and no derivative there.

### Basic rules

- Constant: $\frac{d}{dx}c = 0$; constant multiple and sum rules: differentiate term by term.
- **Power rule:** $\frac{d}{dx}x^n = nx^{n-1}$ for any real $n$.
- **Product rule:** $(fg)' = f'g + fg'$.
- **Quotient rule:** $\left(\frac{f}{g}\right)' = \frac{f'g - fg'}{g^2}$.

### Standard derivatives

| $f(x)$ | $f'(x)$ |
| :--- | :--- |
| $e^x$ | $e^x$ |
| $a^x$ | $a^x \ln a$ |
| $\ln x$ | $1/x$ |
| $\sin x$ | $\cos x$ |
| $\cos x$ | $-\sin x$ |
| $\tan x$ | $\sec^2 x$ |

### The chain rule

For a composition $y = f(g(x))$:

$$\frac{dy}{dx} = f'(g(x)) \cdot g'(x), \qquad \text{or} \qquad \frac{dy}{dx} = \frac{dy}{du}\cdot\frac{du}{dx} \text{ with } u = g(x)$$

Differentiate the outer function, keep the inner function unchanged inside it, and multiply by the derivative of the inner function. Rates multiply along a chain: if $y$ changes 3 times as fast as $u$, and $u$ twice as fast as $x$, then $y$ changes 6 times as fast as $x$. Long chains are handled one link at a time, which is exactly what **backpropagation** does in neural networks, applying the chain rule backwards through layers. For several variables, the multivariable chain rule adds the contributions of each path: if $z = f(x, y)$ with $x$ and $y$ depending on $t$, then $\frac{dz}{dt} = \frac{\partial f}{\partial x}\frac{dx}{dt} + \frac{\partial f}{\partial y}\frac{dy}{dt}$.

### Implicit differentiation

When $y$ is defined implicitly, as on the circle $x^2 + y^2 = 25$, differentiate both sides with respect to $x$, treating $y$ as a function of $x$ (so $\frac{d}{dx}y^2 = 2y\frac{dy}{dx}$), then solve: $2x + 2y y' = 0$, so $y' = -x/y$.

### Numerical derivatives

When only function values are available, approximate the derivative with **finite differences**: the forward difference $\frac{f(x + h) - f(x)}{h}$ has error proportional to $h$, while the **central difference** $\frac{f(x + h) - f(x - h)}{2h}$ has error proportional to $h^2$. Making $h$ extremely small eventually increases the error again, because of floating-point round-off. Machine-learning frameworks instead use **automatic differentiation**, which applies the chain rule exactly.

## Worked examples

### Example 1: Rules, chain rule, and a numerical check

Differentiate three functions by hand and compare with central differences:

- $f(x) = x^3$: power rule, $f'(x) = 3x^2$, so $f'(2) = 12$.
- $g(x) = \sin(x^2)$: chain rule with outer $\sin$ and inner $x^2$: $g'(x) = \cos(x^2) \cdot 2x$.
- $k(x) = x e^{2x}$: product rule and chain rule: $k'(x) = e^{2x} + x \cdot 2e^{2x} = e^{2x}(1 + 2x)$.

```python
from math import exp, sin, cos

def numeric_derivative(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)

cases = [
    ("x^3 at 2", lambda x: x**3, lambda x: 3 * x**2, 2.0),
    ("sin(x^2) at 1", lambda x: sin(x * x), lambda x: cos(x * x) * 2 * x, 1.0),
    ("x*e^(2x) at 0.5", lambda x: x * exp(2 * x), lambda x: exp(2 * x) * (1 + 2 * x), 0.5),
]
for name, f, df, x in cases:
    print(f"{name}: exact {df(x):.6f}, central difference {numeric_derivative(f, x):.6f}")
for h in (1e-1, 1e-3, 1e-5):
    forward = (exp(1 + h) - exp(1)) / h
    print(f"forward difference h={h:g}: error {abs(forward - exp(1)):.2e}")
```

Output:

```text
x^3 at 2: exact 12.000000, central difference 12.000000
sin(x^2) at 1: exact 1.080605, central difference 1.080605
x*e^(2x) at 0.5: exact 5.436564, central difference 5.436564
forward difference h=0.1: error 1.41e-01
forward difference h=0.001: error 1.36e-03
forward difference h=1e-05: error 1.36e-05
```

The central difference agrees with the exact derivatives to six decimal places. The forward difference's error shrinks in proportion to $h$: dividing $h$ by 100 divides the error by about 100.

### Example 2: Implicit differentiation and a tangent line

Find the slope of the tangent to the circle $x^2 + y^2 = 25$ at $(3, 4)$, and the equation of the tangent.

Differentiating implicitly: $2x + 2y\frac{dy}{dx} = 0$, so $\frac{dy}{dx} = -\frac{x}{y} = -\frac{3}{4}$ at $(3, 4)$. The tangent line is $y - 4 = -\frac34(x - 3)$, or $y = -\frac34 x + \frac{25}{4}$. Check: the radius from the origin to $(3, 4)$ has slope $\frac43$, and $\frac43 \cdot \left(-\frac34\right) = -1$, so the tangent is perpendicular to the radius, as geometry requires.

## Applications

- **Physics:** velocity and acceleration are first and second derivatives of position.
- **Economics:** marginal cost and marginal revenue are derivatives.
- **Machine learning:** gradients computed by the chain rule (backpropagation) train models.
- **Sensitivity analysis:** derivatives show how outputs respond to small input changes.

## Common mistakes

- **Forgetting the inner derivative in the chain rule.** $\frac{d}{dx}\sin(x^2) \ne \cos(x^2)$.
- **Treating the product rule as $(fg)' = f'g'$.**
- **Sign errors in the quotient rule.** The numerator is $f'g - fg'$, in that order.
- **Forgetting $\frac{dy}{dx}$ when differentiating $y$ terms implicitly.**
- **Choosing $h$ too small in finite differences.** Round-off error grows.

## Revision notes

- $f'(x) = \lim_{h \to 0}\frac{f(x+h) - f(x)}{h}$: slope and instantaneous rate.
- Power $nx^{n-1}$; product $f'g + fg'$; quotient $\frac{f'g - fg'}{g^2}$.
- $(e^x)' = e^x$, $(\ln x)' = 1/x$, $(\sin x)' = \cos x$, $(\cos x)' = -\sin x$.
- Chain rule: $\frac{d}{dx}f(g(x)) = f'(g(x))g'(x)$; backpropagation is the chain rule.
- Implicit: differentiate both sides, $y$ terms gain $\frac{dy}{dx}$.
- Central differences have error $O(h^2)$; forward differences $O(h)$.

## Practice questions

:::question basic
Differentiate $f(x) = 4x^3 - 2x + 7$.
:::answer
Using the power rule term by term, $f'(x) = 12x^2 - 2$. The constant 7 has derivative 0.
:::

:::question basic
Differentiate $y = e^{5x}$ and $y = \ln(x^2 + 1)$.
:::answer
By the chain rule, $\frac{d}{dx}e^{5x} = 5e^{5x}$, and $\frac{d}{dx}\ln(x^2 + 1) = \frac{1}{x^2 + 1}\cdot 2x = \frac{2x}{x^2 + 1}$.
:::

:::question intermediate
Differentiate $h(x) = \frac{x^2}{\sin x}$.
:::answer
By the quotient rule, $h'(x) = \frac{2x\sin x - x^2\cos x}{\sin^2 x}$.
:::

:::question intermediate
A sigmoid neuron computes $\sigma(z) = \frac{1}{1 + e^{-z}}$ with $z = wx + b$. Find $\frac{d\sigma}{dw}$.
:::answer
First $\sigma'(z) = \frac{e^{-z}}{(1 + e^{-z})^2} = \sigma(z)(1 - \sigma(z))$. By the chain rule with $\frac{dz}{dw} = x$: $\frac{d\sigma}{dw} = \sigma(z)(1 - \sigma(z))\,x$. This is the building block of backpropagation for logistic units.
:::

:::question advanced
Explain why the central difference is more accurate than the forward difference, using Taylor expansions.
:::answer
Expand $f(x \pm h) = f(x) \pm hf'(x) + \frac{h^2}{2}f''(x) \pm \frac{h^3}{6}f'''(x) + \cdots$. The forward difference $\frac{f(x+h) - f(x)}{h} = f'(x) + \frac{h}{2}f''(x) + \cdots$ has an error proportional to $h$. In the central difference $\frac{f(x+h) - f(x-h)}{2h}$, the even-power terms cancel, leaving $f'(x) + \frac{h^2}{6}f'''(x) + \cdots$, so the error is proportional to $h^2$, which is far smaller for small $h$.
:::

## Further learning

- **Next:** *Applications of Derivatives* uses derivatives to optimise and to analyse graphs.
- **Related:** *Gradients, Jacobians & Hessians* extends derivatives to functions of several variables.
