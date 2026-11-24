---
lesson: joint-distributions-covariance
title: Joint Distributions, Covariance & Correlation
summary: Joint distributions of two random variables, marginal and conditional distributions, independence, covariance and correlation as measures of linear association, and the variance of sums.
minutes: 50
type: theory
objectives:
  - Build and read joint probability tables, and derive marginal and conditional distributions from them
  - Test random variables for independence using the joint distribution
  - Compute covariance and correlation, interpret them, and use them to find the variance of sums and portfolios
review: ai-draft
---
## Introduction

Interesting questions usually involve several quantities at once. Are study hours related to exam marks? Do two stocks tend to rise together? Is the load on two servers connected? A **joint distribution** describes how random variables behave together, and **covariance** and **correlation** summarise how strongly they move together in a linear way. These ideas underlie regression, portfolio risk, and much of machine learning.

**Before you start:** you should know random variables, expectation, variance, conditional probability, and independence of events.

## Core theory

### Joint distributions

For discrete X and Y, the **joint PMF** is $p(x, y) = P(X = x, Y = y)$, often shown as a table, with all entries non-negative and summing to 1. For continuous variables, a **joint density** $f(x, y)$ gives probabilities as volumes: $P((X, Y) \in R) = \iint_R f(x, y)\,dx\,dy$.

### Marginal and conditional distributions

The **marginal** distribution of X ignores Y by summing over it:

$$p_X(x) = \sum_y p(x, y) \qquad \left(f_X(x) = \int f(x, y)\,dy\right)$$

so the marginals are the row and column totals of a joint table. The **conditional** distribution of Y given $X = x$ is

$$p_{Y \mid X}(y \mid x) = \frac{p(x, y)}{p_X(x)}$$

and the **conditional expectation** $E[Y \mid X = x] = \sum_y y\,p_{Y \mid X}(y \mid x)$ is the best prediction of Y given X in the mean-squared sense, the idea behind regression.

### Independence

X and Y are **independent** if $p(x, y) = p_X(x)\,p_Y(y)$ for **every** pair $(x, y)$ (or $f(x, y) = f_X(x)f_Y(y)$). One failing cell is enough to show dependence. Independence implies $E[XY] = E[X]E[Y]$.

### Covariance and correlation

$$\operatorname{Cov}(X, Y) = E[(X - \mu_X)(Y - \mu_Y)] = E[XY] - E[X]E[Y]$$

Positive covariance means large values of X tend to occur with large values of Y; negative means large with small. Covariance depends on units, so we standardise it into the **correlation coefficient**

$$\rho(X, Y) = \frac{\operatorname{Cov}(X, Y)}{\sigma_X \sigma_Y}, \qquad -1 \le \rho \le 1$$

with $\rho = \pm 1$ exactly when $Y = aX + b$ for some constants (a perfect linear relationship). Properties: $\operatorname{Cov}(X, X) = \operatorname{Var}(X)$; $\operatorname{Cov}(aX + b, cY + d) = ac\operatorname{Cov}(X, Y)$; correlation is unchanged by positive rescaling.

**Independent implies uncorrelated, but uncorrelated does not imply independent.** If X is uniform on $\{-1, 0, 1\}$ and $Y = X^2$, then Y is completely determined by X, yet their covariance is 0: correlation measures only **linear** association. And correlation never by itself proves causation.

### Variance of sums

$$\operatorname{Var}(aX + bY) = a^2 \operatorname{Var}(X) + b^2 \operatorname{Var}(Y) + 2ab\operatorname{Cov}(X, Y)$$

Negative covariance reduces the variance of a sum, which is the mathematical basis of **diversification**: combining assets that do not move together lowers risk.

## Worked examples

### Example 1: A joint table

X is the number of hours a student studies (1, 2, or 3) and Y whether they pass (1) or not (0), with joint probabilities:

| | Y = 0 | Y = 1 |
| :--- | :--- | :--- |
| X = 1 | 0.20 | 0.10 |
| X = 2 | 0.10 | 0.25 |
| X = 3 | 0.05 | 0.30 |

```python
from math import sqrt

joint = {(1, 0): 0.20, (1, 1): 0.10, (2, 0): 0.10, (2, 1): 0.25, (3, 0): 0.05, (3, 1): 0.30}
px = {x: sum(p for (a, _), p in joint.items() if a == x) for x in (1, 2, 3)}
py = {y: sum(p for (_, b), p in joint.items() if b == y) for y in (0, 1)}
print("marginal X:", {k: round(v, 2) for k, v in px.items()}, "marginal Y:", {k: round(v, 2) for k, v in py.items()})
for x in (1, 2, 3):
    print(f"P(pass | X={x}) = {joint[(x, 1)] / px[x]:.3f}")

ex = sum(x * p for x, p in px.items())
ey = sum(y * p for y, p in py.items())
exy = sum(x * y * p for (x, y), p in joint.items())
cov = exy - ex * ey
vx = sum(x * x * p for x, p in px.items()) - ex**2
vy = sum(y * y * p for y, p in py.items()) - ey**2
print(f"E[X]={ex:.2f} E[Y]={ey:.2f} Cov={cov:.4f} rho={cov / sqrt(vx * vy):.3f}")
print("independent?", all(abs(joint[(x, y)] - px[x] * py[y]) < 1e-12 for x in px for y in py))
```

Output:

```text
marginal X: {1: 0.3, 2: 0.35, 3: 0.35} marginal Y: {0: 0.35, 1: 0.65}
P(pass | X=1) = 0.333
P(pass | X=2) = 0.714
P(pass | X=3) = 0.857
E[X]=2.05 E[Y]=0.65 Cov=0.1675 rho=0.436
independent? False
```

The pass rate rises with study time, the covariance is positive, and the correlation of 0.44 indicates a moderate positive linear association. The variables are dependent: for example $P(X = 1, Y = 1) = 0.10$, but $P(X = 1)P(Y = 1) = 0.195$.

### Example 2: Uncorrelated but dependent, and diversification

**(a)** X uniform on $\{-1, 0, 1\}$, $Y = X^2$: $E[X] = 0$, $E[XY] = E[X^3] = 0$, so $\operatorname{Cov}(X, Y) = 0$, although knowing X determines Y exactly.

**(b)** Two assets have returns with standard deviations 20% and 30% and correlation $\rho$. Put half the money in each. The portfolio's variance is $0.25(0.2^2) + 0.25(0.3^2) + 2(0.25)\rho(0.2)(0.3)$.

```python
from math import sqrt

xs = [-1, 0, 1]
cov = sum(x * x * x for x in xs) / 3 - (sum(xs) / 3) * (sum(x * x for x in xs) / 3)
print("Cov(X, X^2) =", cov)

for rho in (1.0, 0.5, 0.0, -0.5):
    var = 0.25 * 0.2**2 + 0.25 * 0.3**2 + 2 * 0.25 * rho * 0.2 * 0.3
    print(f"rho = {rho:+.1f}: portfolio sd = {sqrt(var):.1%}")
```

Output:

```text
Cov(X, X^2) = 0.0
rho = +1.0: portfolio sd = 25.0%
rho = +0.5: portfolio sd = 21.8%
rho = +0.0: portfolio sd = 18.0%
rho = -0.5: portfolio sd = 13.2%
```

With perfectly correlated assets, mixing gives no benefit (25% is just the average of 20% and 30%). The lower the correlation, the lower the risk of the combination: diversification.

## Applications

- **Finance:** portfolio risk depends on the covariances between asset returns.
- **Machine learning:** covariance matrices drive principal component analysis and Gaussian models.
- **Data analysis:** correlation measures association between features; conditional expectations underlie regression.
- **Sensor fusion:** combining correlated measurements requires their covariances.

## Common mistakes

- **Concluding independence from zero correlation.** Non-linear dependence can have zero correlation.
- **Reading correlation as causation.** A third factor may drive both variables.
- **Checking independence in only one cell.** The product rule must hold in every cell.
- **Forgetting the covariance term in variances of sums.**
- **Comparing covariances across different units.** Use correlation, which is unit-free.

## Revision notes

- Joint PMF $p(x, y)$; marginals are row and column sums; conditional = joint / marginal.
- Independent: $p(x, y) = p_X(x)p_Y(y)$ for all cells.
- $\operatorname{Cov}(X, Y) = E[XY] - E[X]E[Y]$; $\rho = \operatorname{Cov}/(\sigma_X\sigma_Y) \in [-1, 1]$.
- Independent ⇒ uncorrelated, not conversely.
- $\operatorname{Var}(aX + bY) = a^2\operatorname{Var}X + b^2\operatorname{Var}Y + 2ab\operatorname{Cov}(X, Y)$.
- Lower correlation between assets lowers portfolio risk.

## Practice questions

:::question basic
In a joint table, how do you obtain the marginal distribution of X?
:::answer
Sum the joint probabilities over all values of Y for each value of X; in a table with X as rows, these are the row totals.
:::

:::question basic
If $\operatorname{Cov}(X, Y) = 6$, $\sigma_X = 2$, and $\sigma_Y = 5$, what is the correlation?
:::answer
$\rho = 6/(2 \times 5) = 0.6$, a moderately strong positive linear association.
:::

:::question intermediate
X and Y each have variance 4 and $\operatorname{Cov}(X, Y) = -1$. Find $\operatorname{Var}(X + Y)$ and $\operatorname{Var}(X - Y)$.
:::answer
$\operatorname{Var}(X + Y) = 4 + 4 + 2(-1) = 6$. $\operatorname{Var}(X - Y) = 4 + 4 - 2(-1) = 10$. The negative covariance makes the sum less variable and the difference more variable.
:::

:::question intermediate
Show that X and Y can be dependent even if $\operatorname{Cov}(X, Y) = 0$.
:::answer
Let X be uniform on $\{-1, 0, 1\}$ and $Y = X^2$. Then $E[X] = 0$ and $E[XY] = E[X^3] = 0$, so the covariance is 0. But $P(X = 0, Y = 1) = 0$ while $P(X = 0)P(Y = 1) = \frac13 \cdot \frac23 \ne 0$, so they are dependent.
:::

:::question advanced
Explain why combining two assets with correlation $-1$ can, with the right weights, remove risk entirely.
:::answer
With $\rho = -1$, the returns move in exact opposite directions linearly: $Y = a - bX$ for some $b > 0$. Choosing weights $w$ and $1 - w$ so that the portfolio's dependence on X cancels, $w - (1 - w)b = 0$, that is $w = b/(1 + b)$, makes the portfolio's return constant, so its variance is zero. In the formula, $\operatorname{Var} = (w\sigma_X - (1-w)\sigma_Y)^2$ when $\rho = -1$, which is zero for $w = \sigma_Y/(\sigma_X + \sigma_Y)$.
:::

## Further learning

- **Next:** *Law of Large Numbers & Probability Inequalities* uses variances to bound how far averages stray.
- **Related:** *Correlation & Simple Linear Regression* in Statistics estimates these quantities from data.
