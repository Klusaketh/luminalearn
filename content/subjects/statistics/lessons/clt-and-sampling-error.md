---
lesson: clt-and-sampling-error
title: Central Limit Theorem & Sampling Error
summary: Sampling distributions of the sample mean and sample proportion, the standard error and its $1/\sqrt{n}$ scaling, the central limit theorem, and using the normal approximation to find probabilities about sample means.
minutes: 40
type: theory
objectives:
  - Describe the sampling distribution of the sample mean and compute its standard error
  - State the central limit theorem and the conditions under which the normal approximation is reasonable
  - Use the normal approximation to compute probabilities for sample means and proportions
review: ai-draft
---
## Introduction

If you sample 100 students and compute their average height, a different random sample would give a slightly different average. How much do such estimates vary, and what shape does their variation take? The answers are the **sampling distribution** of a statistic and the **central limit theorem** (CLT), arguably the most important result in statistics: averages of many independent observations are approximately normally distributed, whatever the shape of the original data. This is what makes confidence intervals and hypothesis tests possible.

**Before you start:** you should know expectation and variance, the normal distribution and z-scores, and the law of large numbers.

## Core theory

### Sampling distributions

A **sampling distribution** is the distribution of a statistic over all possible samples of a given size. For an SRS of size $n$ from a population with mean $\mu$ and standard deviation $\sigma$, the sample mean $\bar{X}$ has

$$E[\bar{X}] = \mu, \qquad \operatorname{SD}(\bar{X}) = \frac{\sigma}{\sqrt{n}}$$

The sample mean is **unbiased** (centred on $\mu$), and its spread, called the **standard error** (SE), shrinks like $1/\sqrt{n}$. Quadrupling the sample size halves the standard error. In practice $\sigma$ is unknown and is replaced by the sample standard deviation $s$: $\widehat{\text{SE}} = s/\sqrt{n}$. (For sampling without replacement from a small population, a finite-population correction applies; it is negligible when the sample is under about 5% of the population.)

### The central limit theorem

If $X_1, \dots, X_n$ are independent and identically distributed with mean $\mu$ and finite standard deviation $\sigma$, then for large $n$

$$\bar{X} \approx N\left(\mu, \frac{\sigma^2}{n}\right), \qquad \text{equivalently} \qquad Z = \frac{\bar{X} - \mu}{\sigma/\sqrt{n}} \approx N(0, 1)$$

regardless of the shape of the population distribution. How large $n$ must be depends on the shape: for roughly symmetric populations, $n \ge 15$ is often enough; for strongly skewed ones, $n \ge 30$ or more; for a normal population, $\bar{X}$ is exactly normal for any $n$. Heavy-tailed distributions with infinite variance do not satisfy the CLT.

### Sample proportions

A proportion is a mean of 0/1 values. If $\hat{p}$ is the proportion of successes in an SRS of size $n$ from a population with proportion $p$:

$$E[\hat{p}] = p, \qquad \operatorname{SD}(\hat{p}) = \sqrt{\frac{p(1 - p)}{n}}$$

and $\hat{p}$ is approximately normal when $np \ge 10$ and $n(1 - p) \ge 10$ (the success-failure condition).

### Sampling error

The difference between a statistic and the parameter it estimates is **sampling error**. It is not a mistake; it is the unavoidable variability of random sampling, and the standard error measures its typical size. It is distinct from **bias**, which a bigger sample cannot remove.

## Worked examples

### Example 1: Watching the CLT work on skewed data

Service times are exponential with mean 4 minutes, a strongly right-skewed distribution with $\sigma = 4$. We compute the exact sampling distribution of the mean of $n$ such times: the sum of $n$ independent exponentials has a gamma distribution, so we can measure how far $\bar{X}$ is from normal without simulation.

```python
from math import exp, factorial, sqrt, erf

def gamma_cdf(x, n, rate):
    # P(sum of n Exp(rate) <= x) = 1 - sum_{k<n} e^{-rate x} (rate x)^k / k!
    return 1 - sum(exp(-rate * x) * (rate * x) ** k / factorial(k) for k in range(n))

def normal_cdf(z):
    return 0.5 * (1 + erf(z / sqrt(2)))

mu, sigma = 4.0, 4.0
for n in (1, 5, 30):
    se = sigma / sqrt(n)
    exact = gamma_cdf(n * (mu + se), n, 1 / mu)
    print(f"n={n:>2}: SE={se:.2f}, P(mean <= mu + 1 SE) exact {exact:.4f} vs normal {normal_cdf(1):.4f}")
```

Output:

```text
n= 1: SE=4.00, P(mean <= mu + 1 SE) exact 0.8647 vs normal 0.8413
n= 5: SE=1.79, P(mean <= mu + 1 SE) exact 0.8475 vs normal 0.8413
n=30: SE=0.73, P(mean <= mu + 1 SE) exact 0.8425 vs normal 0.8413
```

For a single observation the normal approximation is poor, but as $n$ grows the exact probability approaches the normal value 0.8413, and the standard error shrinks like $4/\sqrt{n}$.

### Example 2: Probabilities for a sample mean and a proportion

**(a)** Battery lifetimes have mean 500 hours and standard deviation 60 hours. For a random sample of 36 batteries, what is the probability that the sample mean is below 485 hours?

$\text{SE} = 60/\sqrt{36} = 10$, so $z = (485 - 500)/10 = -1.5$ and $P(\bar{X} < 485) \approx \Phi(-1.5) \approx 0.0668$.

**(b)** 40% of customers prefer a new design. In a sample of 200, what is the probability that the sample proportion exceeds 45%?

$\text{SE} = \sqrt{0.4 \times 0.6/200} \approx 0.0346$, so $z = (0.45 - 0.40)/0.0346 \approx 1.44$ and $P(\hat{p} > 0.45) \approx 0.074$. The conditions hold: $np = 80$ and $n(1 - p) = 120$ are both at least 10.

```python
from math import erf, sqrt

phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
se_mean = 60 / sqrt(36)
print(f"(a) SE = {se_mean:.0f}, P = {phi((485 - 500) / se_mean):.4f}")
se_prop = sqrt(0.4 * 0.6 / 200)
z = (0.45 - 0.40) / se_prop
print(f"(b) SE = {se_prop:.4f}, z = {z:.2f}, P = {1 - phi(z):.4f}")
print(f"sample size for SE of a proportion <= 0.01 (worst case p = 0.5): {round(0.25 / 0.01**2)}")
```

Output:

```text
(a) SE = 10, P = 0.0668
(b) SE = 0.0346, z = 1.44, P = 0.0745
sample size for SE of a proportion <= 0.01 (worst case p = 0.5): 2500
```

The last line shows why national polls use about 1,000 to 2,500 people: the standard error depends on the sample size, not on the size of the population.

## Applications

- **Polling:** margins of error come from the standard error of a proportion.
- **Quality control:** control charts track sample means against limits of $\mu \pm 3\,\text{SE}$.
- **A/B testing:** comparing conversion rates relies on the sampling distribution of proportions.
- **Simulation:** Monte Carlo error bars are standard errors that shrink like $1/\sqrt{n}$.

## Common mistakes

- **Confusing the standard deviation with the standard error.** $\sigma$ describes individuals; $\sigma/\sqrt{n}$ describes sample means.
- **Thinking the CLT makes the data normal.** It is the distribution of the **mean** that becomes approximately normal.
- **Applying the CLT with tiny samples from skewed populations.**
- **Believing the population size matters.** For large populations, precision depends on $n$ alone.
- **Ignoring the success-failure condition for proportions.**

## Revision notes

- $E[\bar{X}] = \mu$; $\text{SE}(\bar{X}) = \sigma/\sqrt{n}$, estimated by $s/\sqrt{n}$.
- CLT: $\bar{X} \approx N(\mu, \sigma^2/n)$ for large $n$, whatever the population shape (finite variance).
- Proportion: $\text{SE}(\hat{p}) = \sqrt{p(1-p)/n}$; normal if $np \ge 10$ and $n(1-p) \ge 10$.
- Halving the SE needs four times the sample size.
- Sampling error is random variability; bias is systematic.
- Use $z = (\bar{x} - \mu)/\text{SE}$ for probabilities about sample means.

## Practice questions

:::question basic
A population has standard deviation 20. What is the standard error of the mean for samples of size 25 and of size 100?
:::answer
For $n = 25$: $20/\sqrt{25} = 4$. For $n = 100$: $20/\sqrt{100} = 2$. Quadrupling the sample size halves the standard error.
:::

:::question basic
Does the central limit theorem say that a large sample of data will look normally distributed?
:::answer
No. The individual data keep the population's shape, which may be skewed. The CLT says that the sampling distribution of the sample mean, the distribution of $\bar{X}$ over repeated samples, is approximately normal for large $n$.
:::

:::question intermediate
Commute times have mean 30 minutes and standard deviation 12 minutes. For a random sample of 64 commuters, what is the probability that the sample mean exceeds 33 minutes?
:::answer
$\text{SE} = 12/\sqrt{64} = 1.5$, so $z = (33 - 30)/1.5 = 2$. $P(\bar{X} > 33) \approx 1 - \Phi(2) \approx 0.0228$.
:::

:::question intermediate
A poll of 1,000 people finds 52% support a policy. Estimate the standard error of the proportion.
:::answer
$\text{SE} \approx \sqrt{0.52 \times 0.48/1000} = \sqrt{0.0002496} \approx 0.0158$, about 1.6 percentage points.
:::

:::question advanced
A researcher wants the standard error of a sample mean to be at most 0.5, and pilot data suggest $\sigma \approx 8$. How large a sample is needed, and what would change if the population were strongly skewed?
:::answer
We need $8/\sqrt{n} \le 0.5$, so $\sqrt{n} \ge 16$ and $n \ge 256$. The standard-error formula holds for any shape, but if the population is strongly skewed, the researcher should also check that $n$ is large enough for the CLT's normal approximation before using normal-based probabilities or intervals; 256 is usually ample, but very heavy tails may need more or a different method.
:::

## Further learning

- **Next:** *Point Estimation & Confidence Intervals* turns the standard error into a range of plausible parameter values.
- **Related:** *Law of Large Numbers & Probability Inequalities* in Probability explains why sample means converge at all.
