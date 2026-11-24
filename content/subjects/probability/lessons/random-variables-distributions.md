---
lesson: random-variables-distributions
title: Random Variables & Distributions
summary: Random variables as numerical summaries of outcomes, discrete random variables with probability mass functions, continuous random variables with probability density functions, and cumulative distribution functions for both.
minutes: 45
type: theory
objectives:
  - Define a random variable on a sample space and derive its probability mass function
  - Work with probability density functions, computing probabilities as areas and checking normalisation
  - Use cumulative distribution functions to find probabilities, medians, and percentiles
review: ai-draft
---
## Introduction

Most questions about random experiments are about numbers: the number of heads, the time until a server fails, the total of two dice. A **random variable** attaches a number to each outcome so that we can use arithmetic and calculus on uncertainty. Random variables come in two main kinds, **discrete** (countable values) and **continuous** (values in an interval), described by mass functions and density functions respectively, and both are summarised by a cumulative distribution function.

**Before you start:** you should know sample spaces, events, the probability axioms, and basic integration.

## Core theory

### Random variables

A **random variable** $X$ is a function from the sample space to the real numbers. For two coin tosses, $X$ = "number of heads" maps $HH \mapsto 2$, $HT \mapsto 1$, $TH \mapsto 1$, $TT \mapsto 0$. Events about $X$, such as $\{X = 1\}$ or $\{X \le 1\}$, are events in the sample space. Capital letters name random variables; lowercase letters name their values.

### Discrete random variables and PMFs

$X$ is **discrete** if it takes finitely or countably many values. Its **probability mass function** (PMF) is $p(x) = P(X = x)$, and it satisfies

$$p(x) \ge 0, \qquad \sum_x p(x) = 1$$

For two coin tosses, $p(0) = 1/4$, $p(1) = 1/2$, $p(2) = 1/4$. Probabilities of sets add the masses: $P(X \le 1) = 3/4$.

### Continuous random variables and PDFs

$X$ is **continuous** if probabilities are given by a **probability density function** (PDF) $f(x)$ through areas:

$$P(a \le X \le b) = \int_a^b f(x)\,dx, \qquad f(x) \ge 0, \qquad \int_{-\infty}^{\infty} f(x)\,dx = 1$$

Important consequences: $P(X = a) = 0$ for every single value, so $<$ and $\le$ give the same probabilities; and $f(x)$ is **not** a probability. A density can exceed 1 (the uniform density on $[0, 0.5]$ equals 2), and only areas under it are probabilities. Intuitively, $P(x \le X \le x + \Delta x) \approx f(x)\,\Delta x$ for small $\Delta x$.

### Cumulative distribution functions

The **cumulative distribution function** (CDF) $F(x) = P(X \le x)$ works for every random variable. It is non-decreasing, tends to 0 as $x \to -\infty$ and to 1 as $x \to \infty$, and gives interval probabilities:

$$P(a < X \le b) = F(b) - F(a)$$

For a discrete variable, $F$ is a step function that jumps by $p(x)$ at each value. For a continuous variable, $F$ is continuous and $f(x) = F'(x)$ wherever the derivative exists. The **median** is the value $m$ with $F(m) = 0.5$, and the $q$-th **percentile** solves $F(x) = q/100$.

### Functions of random variables

If $Y = g(X)$, its distribution follows from $X$'s. For a discrete $X$, add the masses of all $x$ with the same $g(x)$. For a continuous $X$ with increasing $g$, use the CDF: $F_Y(y) = P(g(X) \le y) = F_X(g^{-1}(y))$, then differentiate.

## Worked examples

### Example 1: The PMF and CDF of a sum of dice

Let $X$ be the larger of two fair dice. Find its PMF, CDF, and $P(X \ge 5)$.

$X \le x$ means both dice are at most $x$, so $F(x) = (x/6)^2$ for $x = 1, \dots, 6$, and $p(x) = F(x) - F(x - 1) = \frac{x^2 - (x - 1)^2}{36} = \frac{2x - 1}{36}$.

```python
from fractions import Fraction
from itertools import product

outcomes = list(product(range(1, 7), repeat=2))
pmf = {x: Fraction(sum(1 for o in outcomes if max(o) == x), 36) for x in range(1, 7)}
print("PMF:", [str(pmf[x]) for x in range(1, 7)])
print("formula (2x-1)/36 matches:", all(pmf[x] == Fraction(2 * x - 1, 36) for x in pmf))
cdf, running = {}, Fraction(0)
for x in range(1, 7):
    running += pmf[x]
    cdf[x] = running
print("CDF:", [str(cdf[x]) for x in range(1, 7)])
print("P(X >= 5) =", 1 - cdf[4], "| total mass =", sum(pmf.values()))
```

Output:

```text
PMF: ['1/36', '1/12', '5/36', '7/36', '1/4', '11/36']
formula (2x-1)/36 matches: True
CDF: ['1/36', '1/9', '1/4', '4/9', '25/36', '1']
P(X >= 5) = 5/9 | total mass = 1
```

The CDF values are exactly $(x/6)^2$, and $P(X \ge 5) = 1 - F(4) = 1 - 16/36 = 5/9$.

### Example 2: A continuous density

Let $f(x) = cx^2$ on $[0, 3]$ and 0 elsewhere. Find $c$, the CDF, $P(1 \le X \le 2)$, and the median.

- Normalisation: $\int_0^3 cx^2\,dx = c \cdot 9 = 1$, so $c = 1/9$.
- CDF: $F(x) = \int_0^x t^2/9\,dt = x^3/27$ for $0 \le x \le 3$.
- $P(1 \le X \le 2) = F(2) - F(1) = (8 - 1)/27 = 7/27 \approx 0.259$.
- Median: $m^3/27 = 1/2$, so $m = (13.5)^{1/3} \approx 2.381$.

```python
def F(x):
    return 0 if x < 0 else 1 if x > 3 else x**3 / 27

n = 100_000
width = 3 / n
area = sum((((i + 0.5) * width) ** 2 / 9) * width for i in range(n))
print(round(area, 6), round(F(2) - F(1), 4), round(13.5 ** (1 / 3), 3))
print("density at 3 is", 3**2 / 9, "- a density, not a probability")
```

Output:

```text
1.0 0.2593 2.381
density at 3 is 1.0 - a density, not a probability
```

A midpoint-rule sum confirms that the density integrates to 1. The median, 2.381, lies well above the midpoint 1.5 of the interval, because the density is concentrated near 3.

## Applications

- **Reliability engineering:** lifetimes of components are continuous random variables with CDFs giving failure probabilities.
- **Networking:** the number of packets arriving per second is a discrete random variable.
- **Finance:** returns are modelled with continuous distributions; percentiles give "value at risk".
- **Simulation:** inverse CDFs turn uniform random numbers into samples of any distribution.

## Common mistakes

- **Treating a density value as a probability.** Only areas under the PDF are probabilities.
- **Expecting $P(X = a) > 0$ for continuous variables.** Single points have probability zero.
- **Forgetting to check normalisation.** A PMF must sum to 1 and a PDF must integrate to 1.
- **Mixing up PMF and CDF.** $p(x)$ is $P(X = x)$; $F(x)$ is $P(X \le x)$.
- **Off-by-one errors with discrete CDFs.** $P(X \ge 5) = 1 - F(4)$, not $1 - F(5)$.

## Revision notes

- A random variable maps outcomes to numbers.
- Discrete: PMF $p(x) = P(X = x)$, $\sum p(x) = 1$.
- Continuous: PDF $f(x)$, $P(a \le X \le b) = \int_a^b f$, $\int f = 1$, $P(X = a) = 0$.
- CDF $F(x) = P(X \le x)$: non-decreasing, from 0 to 1; $P(a < X \le b) = F(b) - F(a)$.
- Continuous: $f = F'$; discrete: $F$ jumps by $p(x)$.
- Median solves $F(m) = 0.5$.

## Practice questions

:::question basic
Three fair coins are tossed and X counts the heads. Give the PMF of X.
:::answer
$P(X = 0) = 1/8$, $P(X = 1) = 3/8$, $P(X = 2) = 3/8$, $P(X = 3) = 1/8$. Each of the 8 outcomes is equally likely, and $\binom{3}{k}$ of them have exactly $k$ heads.
:::

:::question basic
Can a probability density function take the value 4 at some point? Explain.
:::answer
Yes. A density is not a probability; it only has to be non-negative with total area 1. For example, the uniform density on $[0, 0.25]$ equals 4 everywhere on that interval.
:::

:::question intermediate
A continuous random variable has CDF $F(x) = 1 - e^{-2x}$ for $x \ge 0$. Find $P(X > 1)$ and the PDF.
:::answer
$P(X > 1) = 1 - F(1) = e^{-2} \approx 0.135$. The PDF is the derivative of the CDF: $f(x) = 2e^{-2x}$ for $x \ge 0$ (and 0 for $x < 0$).
:::

:::question intermediate
For the density $f(x) = 2x$ on $[0, 1]$, find $P(X \le 0.5)$ and the median.
:::answer
$F(x) = x^2$, so $P(X \le 0.5) = 0.25$. The median solves $m^2 = 0.5$, giving $m = \sqrt{0.5} \approx 0.707$.
:::

:::question advanced
X is uniform on $[0, 1]$. Find the CDF and PDF of $Y = X^2$.
:::answer
For $0 \le y \le 1$, $F_Y(y) = P(X^2 \le y) = P(X \le \sqrt{y}) = \sqrt{y}$. Differentiating gives $f_Y(y) = \frac{1}{2\sqrt{y}}$ on $(0, 1]$. The density grows without bound near 0, yet it still integrates to 1, illustrating again that density values are not probabilities.
:::

## Further learning

- **Next:** *Expectation, Variance & Moments* summarises a distribution with its mean and spread.
- **Related:** *Discrete Distributions: Bernoulli, Binomial, Geometric & Poisson* and *Continuous Distributions: Uniform, Exponential & Normal* catalogue the most useful named distributions.
