---
lesson: first-order-odes
title: First-Order Differential Equations
summary: Differential equations as models of change, separable equations, first-order linear equations with integrating factors, exponential growth and decay, logistic growth, slope fields, and Euler's method for numerical solutions.
minutes: 50
type: theory
objectives:
  - Solve separable differential equations and initial value problems, including exponential growth and decay
  - Solve first-order linear equations with an integrating factor
  - Model growth with the logistic equation, read slope fields, and approximate solutions with Euler's method
review: ai-draft
---
## Introduction

Many laws of nature and engineering describe how a quantity **changes** rather than what it is: a population grows in proportion to its size, a hot drink cools in proportion to its temperature difference from the room, a capacitor discharges in proportion to its charge. Equations that involve derivatives are **differential equations**, and solving them predicts the future from the present. This lesson covers first-order equations, the most common kind, with exact and numerical methods.

**Before you start:** you should know derivatives, integration techniques, and exponential and logarithmic functions.

## Core theory

### Differential equations and initial value problems

A **first-order ordinary differential equation** (ODE) has the form $\frac{dy}{dt} = f(t, y)$. A **solution** is a function satisfying it; there is usually a family of solutions with an arbitrary constant, and an **initial condition** $y(t_0) = y_0$ selects one, forming an **initial value problem**.

### Separable equations

If $\frac{dy}{dt} = g(t)h(y)$, separate the variables and integrate both sides:

$$\int \frac{dy}{h(y)} = \int g(t)\,dt$$

**Exponential growth and decay:** $\frac{dy}{dt} = ky$ separates to $\ln|y| = kt + C$, giving $y = y_0e^{kt}$. Growth if $k > 0$ (doubling time $\frac{\ln 2}{k}$), decay if $k < 0$ (half-life $\frac{\ln 2}{|k|}$). Radioactive decay, continuously compounded interest, and the early growth of epidemics follow this law.

**Newton's law of cooling:** $\frac{dT}{dt} = -k(T - T_{\text{env}})$ gives $T(t) = T_{\text{env}} + (T_0 - T_{\text{env}})e^{-kt}$.

### First-order linear equations

An equation $\frac{dy}{dt} + p(t)y = q(t)$ is solved with an **integrating factor** $\mu(t) = e^{\int p(t)\,dt}$. Multiplying through makes the left side an exact derivative:

$$\frac{d}{dt}\left(\mu y\right) = \mu q \quad \Longrightarrow \quad y = \frac{1}{\mu}\left(\int \mu q\,dt + C\right)$$

### Logistic growth

Unlimited exponential growth is unrealistic; resources limit populations. The **logistic equation**

$$\frac{dP}{dt} = rP\left(1 - \frac{P}{K}\right)$$

has growth rate $r$ when $P$ is small and slows as $P$ approaches the **carrying capacity** $K$. Its solution is the S-shaped curve

$$P(t) = \frac{K}{1 + \left(\frac{K}{P_0} - 1\right)e^{-rt}}$$

with the fastest growth at $P = K/2$. Equilibrium solutions $P = 0$ (unstable) and $P = K$ (stable) are where $\frac{dP}{dt} = 0$.

### Slope fields and Euler's method

A **slope field** draws short segments with slope $f(t, y)$ at grid points; solution curves follow the segments, which shows qualitative behaviour without solving the equation. **Euler's method** follows them numerically with step size $h$:

$$y_{n+1} = y_n + h\,f(t_n, y_n), \qquad t_{n+1} = t_n + h$$

It is first-order accurate: halving $h$ roughly halves the error. Higher-order methods such as Runge-Kutta are far more accurate for the same work.

## Worked examples

### Example 1: Decay with Euler's method, and logistic growth

Solve $\frac{dy}{dt} = -0.3y$, $y(0) = 100$, exactly and with Euler's method, then evaluate a logistic model with $r = 0.5$, $K = 1000$, $P_0 = 50$.

The exact solution is $y = 100e^{-0.3t}$, so $y(5) = 100e^{-1.5} \approx 22.313$.

```python
from math import exp

k, y0 = 0.3, 100.0
exact = lambda t: y0 * exp(-k * t)
for h in (1.0, 0.1, 0.01):
    t, y = 0.0, y0
    while t < 5 - 1e-12:
        y += h * (-k * y)
        t += h
    print(f"Euler h={h}: y(5) = {y:.4f}, exact {exact(5):.4f}, error {abs(y - exact(5)):.4f}")

r, K, P0 = 0.5, 1000, 50
logistic = lambda t: K / (1 + (K / P0 - 1) * exp(-r * t))
print("logistic population at t = 0, 5, 10, 20:", [round(logistic(t), 1) for t in (0, 5, 10, 20)])
print(f"half-life of decay rate 0.3: {0.6931471805599453 / k:.3f}")
```

Output:

```text
Euler h=1.0: y(5) = 16.8070, exact 22.3130, error 5.5060
Euler h=0.1: y(5) = 21.8065, exact 22.3130, error 0.5065
Euler h=0.01: y(5) = 22.2628, exact 22.3130, error 0.0502
logistic population at t = 0, 5, 10, 20: [50.0, 390.7, 886.5, 999.1]
half-life of decay rate 0.3: 2.310
```

Euler's error at $t = 5$ falls from about 5.5 to 0.51 to 0.050 as the step shrinks tenfold each time: first-order convergence. The logistic population starts slowly, grows fastest near 500, and levels off just below the carrying capacity of 1000. The half-life of the decay is $\ln 2/0.3 \approx 2.31$ time units.

### Example 2: A cooling problem and a linear equation

**(a)** Coffee at 90 °C sits in a 20 °C room and cools to 60 °C in 10 minutes. When does it reach 40 °C?

$T(t) = 20 + 70e^{-kt}$. From $60 = 20 + 70e^{-10k}$: $e^{-10k} = \frac47$, so $k = \frac{\ln(7/4)}{10} \approx 0.05596$. For 40 °C: $e^{-kt} = \frac{20}{70} = \frac27$, so $t = \frac{\ln 3.5}{k} \approx \frac{1.2528}{0.05596} \approx 22.4$ minutes.

**(b)** Solve $\frac{dy}{dt} + 2y = 4$, $y(0) = 0$. The integrating factor is $e^{2t}$: $\frac{d}{dt}(e^{2t}y) = 4e^{2t}$, so $e^{2t}y = 2e^{2t} + C$ and $y = 2 + Ce^{-2t}$. The initial condition gives $C = -2$: $y(t) = 2(1 - e^{-2t})$, which rises towards the equilibrium value 2, like a capacitor charging.

## Applications

- **Biology and epidemiology:** population and epidemic models (logistic, SIR).
- **Physics and engineering:** cooling, radioactive decay, RC circuits, and drag.
- **Finance:** continuous compounding and loan balances.
- **Pharmacology:** drug concentrations decay exponentially between doses.

## Common mistakes

- **Losing the constant of integration.** Apply the initial condition only after integrating.
- **Dropping solutions when dividing.** Dividing by $h(y)$ can lose equilibrium solutions such as $y = 0$.
- **Using the wrong sign for decay.** Decay has $k < 0$ in $y' = ky$.
- **Taking large Euler steps.** Errors grow, and the method can even become unstable.
- **Forgetting to multiply the right-hand side by the integrating factor.**

## Revision notes

- ODE + initial condition = initial value problem.
- Separable: $\int \frac{dy}{h(y)} = \int g(t)\,dt$.
- $y' = ky \Rightarrow y = y_0e^{kt}$; doubling time or half-life $\ln 2/|k|$.
- Linear: integrating factor $\mu = e^{\int p\,dt}$; $(\mu y)' = \mu q$.
- Logistic: $P' = rP(1 - P/K)$, S-curve, stable equilibrium at $K$.
- Euler: $y_{n+1} = y_n + hf(t_n, y_n)$, error proportional to $h$.

## Practice questions

:::question basic
Solve $\frac{dy}{dt} = 0.04y$ with $y(0) = 500$, and find the doubling time.
:::answer
$y(t) = 500e^{0.04t}$. The doubling time solves $e^{0.04t} = 2$: $t = \frac{\ln 2}{0.04} \approx 17.3$ time units.
:::

:::question basic
A substance has a half-life of 10 years. What is its decay constant?
:::answer
From $e^{-k \cdot 10} = \frac12$, $k = \frac{\ln 2}{10} \approx 0.0693$ per year.
:::

:::question intermediate
Solve the separable equation $\frac{dy}{dx} = \frac{x}{y}$ with $y(0) = 3$.
:::answer
Separate: $y\,dy = x\,dx$, so $\frac{y^2}{2} = \frac{x^2}{2} + C$, that is $y^2 = x^2 + C'$. With $y(0) = 3$, $C' = 9$, and since $y > 0$ initially, $y = \sqrt{x^2 + 9}$.
:::

:::question intermediate
Apply two steps of Euler's method with $h = 0.5$ to $y' = t + y$, $y(0) = 1$.
:::answer
Step 1: $y_1 = 1 + 0.5(0 + 1) = 1.5$ at $t = 0.5$. Step 2: $y_2 = 1.5 + 0.5(0.5 + 1.5) = 2.5$ at $t = 1$. (The exact value is $2e - 2 \approx 3.437$, showing the large error of big steps.)
:::

:::question advanced
For the logistic equation, show that growth is fastest when $P = K/2$.
:::answer
The growth rate is $g(P) = rP\left(1 - \frac{P}{K}\right) = rP - \frac{r}{K}P^2$. Its derivative with respect to $P$ is $r - \frac{2r}{K}P$, which is zero at $P = \frac{K}{2}$, and the second derivative $-\frac{2r}{K} < 0$ confirms a maximum. So the population grows fastest at half the carrying capacity, the inflection point of the S-curve.
:::

## Further learning

- **Next:** *Runge-Kutta (RK4) Method* in Numerical Methods solves differential equations far more accurately than Euler's method.
- **Related:** *Integration Techniques & Applications* supplies the integrals needed for separable equations.
