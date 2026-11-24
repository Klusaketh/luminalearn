---
lesson: expectation-variance-moments
title: Expectation, Variance & Moments
summary: The expected value of discrete and continuous random variables, linearity of expectation, variance and standard deviation, the effect of linear transformations, covariance of sums, and higher moments.
minutes: 45
type: theory
objectives:
  - Compute expected values of random variables and of functions of them, and apply linearity of expectation
  - Compute variance and standard deviation with the shortcut formula and transform them under $aX + b$
  - Use covariance to find the variance of sums, and interpret higher moments such as skewness
review: ai-draft
---
## Introduction

A whole distribution is often too much information; we want a few numbers that capture its centre and spread. The **expected value** is the long-run average outcome, and the **variance** measures how far outcomes typically fall from it. These two numbers drive decisions everywhere: the expected profit of a strategy, the risk (variance) of an investment, the average running time of a randomised algorithm. A key tool, **linearity of expectation**, makes many seemingly hard calculations easy.

**Before you start:** you should know random variables, PMFs, PDFs, and basic integration and summation.

## Core theory

### Expected value

For a discrete random variable,

$$E[X] = \sum_x x\, p(x)$$

and for a continuous one, $E[X] = \int_{-\infty}^{\infty} x f(x)\,dx$. It is the probability-weighted average of the values, the balance point of the distribution, and by the law of large numbers the long-run average of repeated observations. It need not be a possible value: a fair die has $E[X] = 3.5$.

For a function of X, the **law of the unconscious statistician** gives $E[g(X)] = \sum_x g(x) p(x)$ (or the integral), without finding the distribution of $g(X)$ first. In general $E[g(X)] \ne g(E[X])$; for example $E[X^2] \ne (E[X])^2$.

### Linearity of expectation

For any random variables X and Y and constants a and b,

$$E[aX + bY] = aE[X] + bE[Y]$$

**whether or not X and Y are independent**. This makes complicated counts easy: write the quantity as a sum of simple **indicator variables** ($I_k = 1$ if event $k$ happens, else 0, with $E[I_k] = P(\text{event } k)$) and add their expectations.

### Variance and standard deviation

$$\operatorname{Var}(X) = E[(X - \mu)^2] = E[X^2] - (E[X])^2, \qquad \mu = E[X]$$

The second form is usually easier to compute. The **standard deviation** $\sigma = \sqrt{\operatorname{Var}(X)}$ has the same units as X. Variance is never negative and is zero only for a constant.

For a linear transformation,

$$E[aX + b] = aE[X] + b, \qquad \operatorname{Var}(aX + b) = a^2 \operatorname{Var}(X)$$

Adding a constant shifts the distribution without changing its spread; scaling by $a$ scales the standard deviation by $|a|$.

### Covariance and sums

$$\operatorname{Cov}(X, Y) = E[(X - \mu_X)(Y - \mu_Y)] = E[XY] - E[X]E[Y]$$

and

$$\operatorname{Var}(X + Y) = \operatorname{Var}(X) + \operatorname{Var}(Y) + 2\operatorname{Cov}(X, Y)$$

If X and Y are **independent**, $E[XY] = E[X]E[Y]$, so the covariance is zero and variances add. Averaging $n$ independent copies with variance $\sigma^2$ therefore gives variance $\sigma^2/n$: averages are less variable than single observations.

### Higher moments

The $k$-th moment is $E[X^k]$, and the $k$-th central moment is $E[(X - \mu)^k]$. The third standardised moment, **skewness** $E[(X - \mu)^3]/\sigma^3$, measures asymmetry (positive for a long right tail, such as incomes); the fourth, **kurtosis**, measures how heavy the tails are. **Markov's** and **Chebyshev's inequalities** turn the mean and variance into bounds on tail probabilities.

## Worked examples

### Example 1: A game and its risk

A game costs 5 to play. A fair die is rolled: a 6 pays 20, a 4 or 5 pays 6, and anything else pays nothing. Find the expected profit and its standard deviation.

Profit $X$ takes values $15$ (probability 1/6), $1$ (probability 2/6), and $-5$ (probability 3/6).

- $E[X] = 15 \cdot \frac16 + 1 \cdot \frac26 - 5 \cdot \frac36 = \frac{15 + 2 - 15}{6} = \frac13$.
- $E[X^2] = 225 \cdot \frac16 + 1 \cdot \frac26 + 25 \cdot \frac36 = \frac{225 + 2 + 75}{6} = \frac{302}{6}$.
- $\operatorname{Var}(X) = \frac{302}{6} - \frac19 = \frac{906 - 2}{18} = \frac{452}{9} \approx 50.2$, so $\sigma \approx 7.09$.

```python
from fractions import Fraction
from math import sqrt

values = {15: Fraction(1, 6), 1: Fraction(2, 6), -5: Fraction(3, 6)}
mean = sum(x * p for x, p in values.items())
second = sum(x * x * p for x, p in values.items())
var = second - mean**2
print(mean, var, round(sqrt(var), 2))
doubled = {2 * x + 10: p for x, p in values.items()}
mean2 = sum(x * p for x, p in doubled.items())
var2 = sum(x * x * p for x, p in doubled.items()) - mean2**2
print(mean2, var2, var2 == 4 * var)
```

Output:

```text
1/3 452/9 7.09
32/3 1808/9 True
```

The game is slightly favourable on average but risky: one play's outcome typically misses the mean by about 7. The second line checks the transformation rules for $Y = 2X + 10$: the mean becomes $2 \cdot \frac13 + 10 = \frac{32}{3}$ and the variance is multiplied by $2^2 = 4$.

### Example 2: Linearity with indicators

**(a) Hat-check problem.** $n$ people's hats are returned in random order. What is the expected number of people who get their own hat?

Let $I_k = 1$ if person $k$ gets their own hat; $P(I_k = 1) = 1/n$. By linearity, $E[\sum_k I_k] = n \cdot \frac1n = 1$, for every $n$, even though the $I_k$ are dependent.

**(b) Expected distinct values.** Rolling a die 6 times, the expected number of distinct faces is $6\left(1 - (5/6)^6\right)$, since face $k$ appears at least once with probability $1 - (5/6)^6$.

```python
from itertools import permutations, product
from math import factorial

for n in (3, 4, 5):
    perms = list(permutations(range(n)))
    fixed = sum(sum(1 for i, v in enumerate(p) if i == v) for p in perms)
    print(n, "people: average matches =", fixed / factorial(n))

distinct = sum(len(set(r)) for r in product(range(6), repeat=6)) / 6**6
print(round(distinct, 4), round(6 * (1 - (5 / 6) ** 6), 4))
```

Output:

```text
3 people: average matches = 1.0
4 people: average matches = 1.0
5 people: average matches = 1.0
3.9906 3.9906
```

Brute force over every permutation and every sequence of six rolls agrees exactly with the one-line linearity arguments.

## Applications

- **Algorithm analysis:** the expected running time of randomised quicksort is computed with indicators and linearity.
- **Finance:** expected return and variance (risk) guide portfolio choices; diversification lowers variance.
- **Insurance and gambling:** premiums and house edges are set from expected values.
- **Machine learning:** loss functions are expectations; variance of estimates guides model choice.

## Common mistakes

- **Assuming $E[g(X)] = g(E[X])$.** It fails for non-linear $g$, such as $E[X^2]$.
- **Adding standard deviations.** Variances of independent variables add, not standard deviations.
- **Forgetting the square in $\operatorname{Var}(aX) = a^2 \operatorname{Var}(X)$.**
- **Adding variances of dependent variables without the covariance term.**
- **Thinking linearity of expectation needs independence.** It does not.

## Revision notes

- $E[X] = \sum x p(x)$ or $\int x f(x)\,dx$; $E[g(X)] = \sum g(x)p(x)$.
- Linearity: $E[aX + bY] = aE[X] + bE[Y]$, always.
- Indicators: $E[I_A] = P(A)$; write counts as sums of indicators.
- $\operatorname{Var}(X) = E[X^2] - (E[X])^2$; $\sigma = \sqrt{\operatorname{Var}}$.
- $\operatorname{Var}(aX + b) = a^2\operatorname{Var}(X)$.
- $\operatorname{Var}(X + Y) = \operatorname{Var}X + \operatorname{Var}Y + 2\operatorname{Cov}(X, Y)$; independent means covariance 0.

## Practice questions

:::question basic
Find the expected value and variance of a fair six-sided die.
:::answer
$E[X] = (1 + \cdots + 6)/6 = 3.5$. $E[X^2] = (1 + 4 + 9 + 16 + 25 + 36)/6 = 91/6$, so $\operatorname{Var}(X) = 91/6 - 12.25 = 35/12 \approx 2.92$.
:::

:::question basic
If $E[X] = 4$ and $\operatorname{Var}(X) = 9$, find $E[3X - 2]$ and $\operatorname{Var}(3X - 2)$.
:::answer
$E[3X - 2] = 3 \times 4 - 2 = 10$. $\operatorname{Var}(3X - 2) = 3^2 \times 9 = 81$; subtracting 2 does not change the spread.
:::

:::question intermediate
X and Y are independent with variances 4 and 9. What are the standard deviations of $X + Y$ and $X - Y$?
:::answer
For independent variables variances add, also for a difference: $\operatorname{Var}(X - Y) = \operatorname{Var}(X) + (-1)^2\operatorname{Var}(Y) = 13$. Both $X + Y$ and $X - Y$ have variance 13 and standard deviation $\sqrt{13} \approx 3.61$, not $2 + 3 = 5$.
:::

:::question intermediate
In a random sequence of 100 coin tosses, what is the expected number of occurrences of "HH" (overlapping pairs counted)?
:::answer
There are 99 adjacent pairs, and each is HH with probability 1/4. By linearity with indicators, the expected count is $99 \times \frac14 = 24.75$, even though overlapping pairs are dependent.
:::

:::question advanced
A continuous random variable has density $f(x) = 3x^2$ on $[0, 1]$. Find its mean, variance, and $E[1/X]$.
:::answer
$E[X] = \int_0^1 3x^3\,dx = 3/4$. $E[X^2] = \int_0^1 3x^4\,dx = 3/5$, so $\operatorname{Var}(X) = 3/5 - 9/16 = 3/80 = 0.0375$. $E[1/X] = \int_0^1 3x\,dx = 3/2$, which differs from $1/E[X] = 4/3$, showing that $E[g(X)] \ne g(E[X])$ for non-linear $g$.
:::

## Further learning

- **Next:** *Discrete Distributions: Bernoulli, Binomial, Geometric & Poisson* gives means and variances of named distributions.
- **Related:** *Law of Large Numbers & Probability Inequalities* explains why averages approach the expected value.
