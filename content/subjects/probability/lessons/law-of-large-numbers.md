---
lesson: law-of-large-numbers
title: Law of Large Numbers & Probability Inequalities
summary: Markov's and Chebyshev's inequalities for bounding tail probabilities, the weak law of large numbers and why sample averages settle down, and a first look at the central limit theorem.
minutes: 45
type: theory
objectives:
  - Apply Markov's and Chebyshev's inequalities to bound probabilities using only the mean and variance
  - State the weak law of large numbers and prove it from Chebyshev's inequality
  - Explain how the spread of a sample mean shrinks like $1/\sqrt{n}$ and how the central limit theorem refines this
review: ai-draft
---
## Introduction

Toss a fair coin ten times and you may well see seven heads; toss it ten thousand times and the proportion of heads will almost certainly be very close to one half. The **law of large numbers** makes this precise: averages of many independent observations settle down to the expected value. It is why casinos always win in the long run, why opinion polls work, and why Monte Carlo simulations give reliable answers. Along the way, simple **inequalities** let us bound probabilities even when we know almost nothing about a distribution.

**Before you start:** you should know expectation, variance, independence, and the variance of sums.

## Core theory

### Markov's inequality

For a **non-negative** random variable X and any $a > 0$:

$$P(X \ge a) \le \frac{E[X]}{a}$$

Proof: $E[X] \ge E[X \cdot \mathbf{1}_{X \ge a}] \ge a\,P(X \ge a)$. If the average response time is 2 seconds, at most a quarter of responses take 8 seconds or more, whatever the distribution. The bound is crude but needs only the mean.

### Chebyshev's inequality

For any random variable with mean $\mu$ and variance $\sigma^2$, and any $k > 0$:

$$P(|X - \mu| \ge k\sigma) \le \frac{1}{k^2}$$

Proof: apply Markov's inequality to the non-negative variable $(X - \mu)^2$ with $a = k^2\sigma^2$. So at least 75% of any distribution lies within 2 standard deviations of the mean, and at least 89% within 3. For a normal distribution the true figures are 95% and 99.7%; Chebyshev's bound is weaker because it must hold for **every** distribution.

### The sample mean

Let $X_1, \dots, X_n$ be independent and identically distributed (i.i.d.) with mean $\mu$ and variance $\sigma^2$, and let $\bar{X}_n = \frac{1}{n}\sum_i X_i$. By linearity and independence:

$$E[\bar{X}_n] = \mu, \qquad \operatorname{Var}(\bar{X}_n) = \frac{\sigma^2}{n}, \qquad \operatorname{SD}(\bar{X}_n) = \frac{\sigma}{\sqrt{n}}$$

The sample mean is centred on the true mean, and its spread shrinks like $1/\sqrt{n}$: to halve the error you need **four** times as much data.

### The weak law of large numbers

For every $\varepsilon > 0$,

$$P\left(|\bar{X}_n - \mu| \ge \varepsilon\right) \le \frac{\sigma^2}{n\varepsilon^2} \to 0 \quad \text{as } n \to \infty$$

which follows directly from Chebyshev's inequality applied to $\bar{X}_n$. In words: with enough observations, the sample mean is within any chosen distance of the true mean with probability as close to 1 as we like. (The **strong** law says more: $\bar{X}_n \to \mu$ with probability 1.)

The law does **not** say that deviations are "corrected" by later outcomes. After ten heads in a row, the next toss is still 50-50; the excess is not cancelled but **diluted** by the many tosses that follow. Believing otherwise is the **gambler's fallacy**.

### The central limit theorem (preview)

The law of large numbers says where $\bar{X}_n$ goes; the **central limit theorem** says how it is distributed on the way: for large $n$, $\bar{X}_n$ is approximately $N(\mu, \sigma^2/n)$, whatever the distribution of the $X_i$ (as long as the variance is finite). This gives much sharper probabilities than Chebyshev and underlies confidence intervals.

## Worked examples

### Example 1: Comparing the bounds with the truth

Let X count heads in 100 fair coin tosses: $\mu = 50$, $\sigma = 5$. Compare Markov's and Chebyshev's bounds with the exact binomial probability for large deviations.

```python
from math import comb

n = 100
pmf = [comb(n, k) / 2**n for k in range(n + 1)]
print(f"Markov:    P(X >= 70) <= {50 / 70:.3f}, exact {sum(pmf[70:]):.6f}")
for k in (2, 3):
    exact = sum(p for x, p in enumerate(pmf) if abs(x - 50) >= 5 * k)
    print(f"Chebyshev: P(|X-50| >= {5 * k}) <= {1 / k**2:.3f}, exact {exact:.6f}")
```

Output:

```text
Markov:    P(X >= 70) <= 0.714, exact 0.000039
Chebyshev: P(|X-50| >= 10) <= 0.250, exact 0.056888
Chebyshev: P(|X-50| >= 15) <= 0.111, exact 0.003518
```

Both bounds are true but loose, since they use only the mean (and variance). Their value is that they hold for **any** distribution, including ones we cannot compute exactly.

### Example 2: How many samples are enough?

How many fair-coin tosses guarantee, by Chebyshev, that the proportion of heads is within 0.01 of 0.5 with probability at least 95%? For each toss $\sigma^2 = 0.25$, so we need $\frac{0.25}{n(0.01)^2} \le 0.05$, giving $n \ge 50{,}000$. The central limit theorem gives the sharper requirement $1.96\sqrt{0.25/n} \le 0.01$, that is, $n \ge 9{,}604$.

The exact spread of the proportion shrinks with $n$ as predicted:

```python
from math import sqrt

for n in (100, 10_000, 1_000_000):
    sd = sqrt(0.25 / n)
    print(f"n = {n:>9,}: sd of proportion = {sd:.4f}, Chebyshev bound P(|p-0.5| >= 0.01) <= {min(1, 0.25 / (n * 0.01**2)):.4f}")
print("Chebyshev n:", round(0.25 / (0.05 * 0.01**2)), "| CLT n:", round((1.96 / 0.01) ** 2 * 0.25))
```

Output:

```text
n =       100: sd of proportion = 0.0500, Chebyshev bound P(|p-0.5| >= 0.01) <= 1.0000
n =    10,000: sd of proportion = 0.0050, Chebyshev bound P(|p-0.5| >= 0.01) <= 0.2500
n = 1,000,000: sd of proportion = 0.0005, Chebyshev bound P(|p-0.5| >= 0.01) <= 0.0025
Chebyshev n: 50000 | CLT n: 9604
```

Each hundredfold increase in $n$ shrinks the standard deviation tenfold, the $1/\sqrt{n}$ law. With only 100 tosses, Chebyshev's bound is useless (it exceeds 1), while with a million tosses a deviation of 0.01 is extremely unlikely.

## Applications

- **Monte Carlo simulation:** averages of random samples estimate integrals and probabilities, with error shrinking like $1/\sqrt{n}$.
- **Polling and A/B testing:** sample sizes are chosen so that sample proportions are close to the truth.
- **Insurance and casinos:** pooling many independent risks makes average losses predictable.
- **Machine learning:** training on more data reduces the variance of estimates.

## Common mistakes

- **The gambler's fallacy.** Past outcomes do not make future independent outcomes "due".
- **Applying Markov's inequality to variables that can be negative.** It requires $X \ge 0$.
- **Expecting the error to shrink like $1/n$.** It shrinks like $1/\sqrt{n}$.
- **Ignoring independence.** The variance formula $\sigma^2/n$ needs independent observations.
- **Treating Chebyshev's bound as an estimate.** It is an upper bound, often far above the truth.

## Revision notes

- Markov: $P(X \ge a) \le E[X]/a$ for $X \ge 0$.
- Chebyshev: $P(|X - \mu| \ge k\sigma) \le 1/k^2$.
- Sample mean: $E[\bar{X}] = \mu$, $\operatorname{SD}(\bar{X}) = \sigma/\sqrt{n}$.
- Weak law: $P(|\bar{X}_n - \mu| \ge \varepsilon) \le \sigma^2/(n\varepsilon^2) \to 0$.
- Large deviations are diluted, not corrected (gambler's fallacy).
- CLT: $\bar{X}_n \approx N(\mu, \sigma^2/n)$ for large $n$.

## Practice questions

:::question basic
A non-negative random variable has mean 10. What does Markov's inequality say about $P(X \ge 50)$?
:::answer
$P(X \ge 50) \le 10/50 = 0.2$. Whatever the distribution, at most 20% of the probability can lie at 50 or above.
:::

:::question basic
At least what fraction of any distribution lies within 4 standard deviations of its mean?
:::answer
By Chebyshev's inequality, at most $1/4^2 = 1/16$ lies 4 or more standard deviations away, so at least $15/16 = 93.75\%$ lies within.
:::

:::question intermediate
The heights of a population have standard deviation 9 cm. How many people must be measured so that the sample mean's standard deviation is at most 1 cm?
:::answer
We need $9/\sqrt{n} \le 1$, so $\sqrt{n} \ge 9$ and $n \ge 81$ people.
:::

:::question intermediate
After a roulette wheel lands on red ten times in a row, is black more likely next? Relate your answer to the law of large numbers.
:::answer
No. Spins are independent, so the probability of black is unchanged. The law of large numbers does not work by compensating: the run of ten reds is not cancelled by extra blacks but diluted by the thousands of spins that follow, so the long-run proportion still approaches its expected value.
:::

:::question advanced
Use Chebyshev's inequality to prove the weak law of large numbers for i.i.d. variables with finite variance.
:::answer
Let $X_1, \dots, X_n$ be i.i.d. with mean $\mu$ and variance $\sigma^2$. By linearity $E[\bar{X}_n] = \mu$, and by independence $\operatorname{Var}(\bar{X}_n) = \frac{1}{n^2} \cdot n\sigma^2 = \sigma^2/n$. Chebyshev's inequality with deviation $\varepsilon$ gives $P(|\bar{X}_n - \mu| \ge \varepsilon) \le \frac{\sigma^2/n}{\varepsilon^2} = \frac{\sigma^2}{n\varepsilon^2}$, which tends to 0 as $n \to \infty$ for every fixed $\varepsilon > 0$.
:::

## Further learning

- **Next:** *Central Limit Theorem & Sampling Error* in Statistics develops the CLT and its uses.
- **Related:** *Expectation, Variance & Moments* provides the tools these inequalities rely on.
