---
lesson: runge-kutta-rk4-solver
title: Runge-Kutta (RK4) Method
summary: Solving initial value problems numerically: Euler's method and its limitations, the classical fourth-order Runge-Kutta method, local and global error and order, step-size choice, and systems of equations.
minutes: 45
type: theory
objectives:
  - Apply Euler's method and the classical RK4 method to initial value problems
  - Explain local and global truncation error and verify the order of a method by halving the step size
  - Extend RK4 to systems of first-order equations and recognise stiffness and the role of adaptive step sizes
review: ai-draft
---
## Introduction

Differential equations describe how systems evolve, but most of them, from planetary orbits to epidemic models to circuit simulations, cannot be solved in closed form. Numerical ODE solvers march the solution forward in small steps. **Euler's method** is the simplest such solver but needs tiny steps to be accurate. The classical **fourth-order Runge-Kutta method** (RK4) samples the slope four times per step and combines them cleverly, achieving dramatically better accuracy for the same effort, which is why it has been the workhorse of scientific computing for a century.

**Before you start:** you should know first-order differential equations, Euler's method, and Taylor series.

## Core theory

### Initial value problems and Euler's method

An initial value problem is $y' = f(t, y)$, $y(t_0) = y_0$. **Euler's method** takes steps of size $h$ along the current slope:

$$y_{n+1} = y_n + h\,f(t_n, y_n)$$

### Local and global error

The **local truncation error** is the error made in a single step assuming the previous value was exact; for Euler it is $O(h^2)$, the first neglected Taylor term. Over the $(t_{\text{end}} - t_0)/h$ steps needed to reach a fixed time, the errors accumulate into a **global error** one power of $h$ lower: $O(h)$ for Euler. A method has **order $p$** if its global error is $O(h^p)$: halving $h$ divides the error by about $2^p$.

### The classical RK4 method

Each step evaluates the slope four times:

$$\begin{aligned}
k_1 &= f(t_n, y_n) \\
k_2 &= f\!\left(t_n + \tfrac{h}{2},\; y_n + \tfrac{h}{2}k_1\right) \\
k_3 &= f\!\left(t_n + \tfrac{h}{2},\; y_n + \tfrac{h}{2}k_2\right) \\
k_4 &= f(t_n + h,\; y_n + hk_3) \\
y_{n+1} &= y_n + \tfrac{h}{6}\left(k_1 + 2k_2 + 2k_3 + k_4\right)
\end{aligned}$$

$k_1$ is the slope at the start, $k_2$ and $k_3$ are estimates at the midpoint, and $k_4$ at the end; the weighted average matches the Taylor expansion of the true solution up to the $h^4$ term. RK4 is a **fourth-order** method: halving $h$ divides the global error by about 16. For $y' = f(t)$, a step of RK4 reduces to Simpson's rule.

### Cost and accuracy

RK4 costs four function evaluations per step against Euler's one, but its accuracy is so much higher that it reaches a given tolerance with far fewer total evaluations. Production solvers such as `scipy.integrate.solve_ivp` (RK45, the Dormand-Prince method) use **embedded** pairs of Runge-Kutta formulas to estimate the local error each step and adapt the step size automatically.

### Systems and higher-order equations

RK4 applies unchanged to systems $\mathbf{y}' = \mathbf{f}(t, \mathbf{y})$, with vectors in place of numbers. A higher-order equation is converted to a first-order system: $y'' = -y$ becomes $y_1' = y_2$, $y_2' = -y_1$ with $y_1 = y$ and $y_2 = y'$.

### Stiffness

Some systems mix very fast and very slow dynamics (such as chemical reactions with widely different rates). For these **stiff** problems, explicit methods like Euler and RK4 need tiny steps for **stability**, not accuracy, and implicit methods (backward Euler, BDF) are preferred.

## Worked examples

### Example 1: Euler versus RK4

Solve $y' = y - t^2 + 1$ with $y(0) = 0.5$ on $[0, 2]$. The exact solution is $y(t) = (t + 1)^2 - \frac12e^t$, so $y(2) \approx 5.305472$.

```python
from math import exp

def euler(f, t, y, h, steps):
    for _ in range(steps):
        y += h * f(t, y)
        t += h
    return y

def rk4(f, t, y, h, steps):
    for _ in range(steps):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h / 2 * k1)
        k3 = f(t + h / 2, y + h / 2 * k2)
        k4 = f(t + h, y + h * k3)
        y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += h
    return y

f = lambda t, y: y - t * t + 1
exact = lambda t: (t + 1) ** 2 - 0.5 * exp(t)
for h in (0.2, 0.1, 0.05):
    steps = round(2 / h)
    e = abs(euler(f, 0, 0.5, h, steps) - exact(2))
    r = abs(rk4(f, 0, 0.5, h, steps) - exact(2))
    print(f"h={h:<5} Euler error {e:.2e}   RK4 error {r:.2e}")
print(f"exact y(2) = {exact(2):.6f}, RK4 with h=0.2: {rk4(f, 0, 0.5, 0.2, 10):.6f}")
```

Output:

```text
h=0.2   Euler error 4.40e-01   RK4 error 1.09e-04
h=0.1   Euler error 2.42e-01   RK4 error 6.99e-06
h=0.05  Euler error 1.27e-01   RK4 error 4.42e-07
exact y(2) = 5.305472, RK4 with h=0.2: 5.305363
```

With $h = 0.2$ (10 steps), Euler's error is 0.44 while RK4's is about $10^{-4}$. Halving the step roughly halves Euler's error (first order) but divides RK4's by about 16 (from $1.09 \times 10^{-4}$ to $6.99 \times 10^{-6}$ to $4.42 \times 10^{-7}$), confirming fourth order. RK4 with 40 function evaluations beats Euler with 40 steps by more than three orders of magnitude.

### Example 2: One RK4 step by hand

Take one RK4 step of size $h = 0.1$ for $y' = -2ty$, $y(0) = 1$ (exact solution $e^{-t^2}$).

- $k_1 = f(0, 1) = 0$
- $k_2 = f(0.05, 1 + 0.05 \times 0) = -2(0.05)(1) = -0.1$
- $k_3 = f(0.05, 1 + 0.05 \times (-0.1)) = -2(0.05)(0.995) = -0.0995$
- $k_4 = f(0.1, 1 + 0.1 \times (-0.0995)) = -2(0.1)(0.99005) = -0.19801$
- $y_1 = 1 + \frac{0.1}{6}(0 - 0.2 - 0.199 - 0.19801) = 1 - \frac{0.1}{6}(0.59701) \approx 0.9900498333$

The exact value is $e^{-0.01} \approx 0.9900498337$: the single step is accurate to about nine decimal places. Euler's method would give $y_1 = 1 + 0.1 \times 0 = 1$, an error of about 0.01.

## Applications

- **Physics and astronomy:** orbits, pendulums, and particle trajectories.
- **Engineering:** circuit transients, control systems, and vehicle dynamics.
- **Epidemiology and ecology:** SIR and predator-prey models.
- **Games and animation:** physics engines integrate motion each frame.

## Common mistakes

- **Using the wrong arguments for $k_2$, $k_3$, $k_4$.** Each uses the previous $k$ and the matching time offset.
- **Forgetting the weights 1, 2, 2, 1 and the factor $h/6$.**
- **Confusing local and global error orders.** RK4 has local error $O(h^5)$ and global error $O(h^4)$.
- **Using explicit methods on stiff problems.** They become unstable unless the step is tiny.
- **Not checking convergence.** Halve the step size and compare results.

## Revision notes

- Euler: $y_{n+1} = y_n + hf(t_n, y_n)$; global error $O(h)$.
- Order $p$: global error $O(h^p)$; halving $h$ divides error by $2^p$.
- RK4: $k_1$ to $k_4$ at start, two midpoints, end; $y_{n+1} = y_n + \frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$.
- RK4 is fourth order: halving $h$ divides error by about 16.
- Systems: apply componentwise; reduce higher-order ODEs to first-order systems.
- Adaptive embedded RK (RK45) for general use; implicit methods for stiff problems.

## Practice questions

:::question basic
Take one Euler step with $h = 0.1$ for $y' = 2y$, $y(0) = 1$, and compare with the exact value.
:::answer
$y_1 = 1 + 0.1 \times 2 = 1.2$. The exact solution is $e^{2t}$, so $y(0.1) = e^{0.2} \approx 1.2214$; the error is about 0.021.
:::

:::question basic
If RK4 has global error $3.2 \times 10^{-6}$ with step $h$, what error do you expect with step $h/2$?
:::answer
RK4 is fourth order, so halving the step divides the error by about $2^4 = 16$, giving roughly $2 \times 10^{-7}$.
:::

:::question intermediate
Convert $y'' + 3y' + 2y = 0$, $y(0) = 1$, $y'(0) = 0$ into a first-order system suitable for RK4.
:::answer
Let $y_1 = y$ and $y_2 = y'$. Then $y_1' = y_2$ and $y_2' = -2y_1 - 3y_2$, with initial conditions $y_1(0) = 1$ and $y_2(0) = 0$. RK4 is applied to the vector $(y_1, y_2)$.
:::

:::question intermediate
Why does RK4 usually need fewer total function evaluations than Euler's method for the same accuracy?
:::answer
Its error falls like $h^4$ instead of $h$, so to reach a small tolerance it can use a much larger step. For example, reducing the error by a factor of 10,000 needs a step 10,000 times smaller with Euler but only 10 times smaller with RK4, so four evaluations per step is a small price.
:::

:::question advanced
What is a stiff differential equation, and why do explicit methods like RK4 struggle with it?
:::answer
A stiff system contains components that decay on very different time scales, for example one mode with rate $-1000$ and another with rate $-1$. Explicit methods are only stable if the step is small relative to the fastest time scale (for RK4 applied to $y' = -1000y$, roughly $h < 0.0028$), even after that fast component has died away and accuracy alone would allow much larger steps. Implicit methods remain stable with large steps, so they are far more efficient for stiff problems.
:::

## Further learning

- **Next:** *Iterative Methods for Linear Systems* turns to solving large systems of equations.
- **Related:** *First-Order Differential Equations* in Calculus solves some of these equations exactly.
