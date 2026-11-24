---
lesson: confidence-intervals
title: Point Estimation & Confidence Intervals
summary: Point estimators and their properties, the standard error, and confidence intervals for means and proportions using z and t critical values, with the correct interpretation of confidence and how to choose a sample size.
minutes: 50
type: theory
objectives:
  - Describe point estimators and the properties of unbiasedness and consistency
  - Construct and interpret confidence intervals for a mean (z and t) and for a proportion
  - Explain what a confidence level means, how width depends on confidence and sample size, and how to plan a sample size for a target margin of error
review: ai-draft
---
## Introduction

A sample mean of 72.4 is a useful estimate, but on its own it hides how uncertain it is. A **confidence interval** reports a range of plausible values, such as "72.4 ± 3.1", with a stated **confidence level**. This is how polls report a margin of error and how scientists report results. Constructing intervals is mechanical; interpreting them correctly takes more care, and that is where most mistakes happen.

**Before you start:** you should know the standard error, the central limit theorem, and normal percentiles.

## Core theory

### Point estimators

An **estimator** is a rule for computing an estimate of a parameter from data: $\bar{X}$ estimates $\mu$, $\hat{p}$ estimates $p$, $s^2$ estimates $\sigma^2$. Good estimators are **unbiased** (their expected value equals the parameter) and **consistent** (they converge to the parameter as $n$ grows), and among unbiased estimators we prefer the one with the smallest standard error.

### The general form

Most intervals have the form

$$\text{estimate} \pm (\text{critical value}) \times \text{SE}$$

and the second term is the **margin of error**. The critical value comes from the sampling distribution: for 95% confidence with a normal distribution, $z^* = 1.96$; for 90%, $1.645$; for 99%, $2.576$.

### Interval for a mean, $\sigma$ known

$$\bar{x} \pm z^* \frac{\sigma}{\sqrt{n}}$$

### Interval for a mean, $\sigma$ unknown: the t distribution

When $\sigma$ is estimated by $s$, the standardised mean $\frac{\bar{X} - \mu}{s/\sqrt{n}}$ follows Student's **t distribution** with $n - 1$ **degrees of freedom** (when the population is normal, and approximately otherwise for moderate $n$). The t distribution is bell-shaped but has heavier tails than the normal, reflecting the extra uncertainty in $s$; as the degrees of freedom grow it approaches the normal. The interval is

$$\bar{x} \pm t^*_{n-1} \frac{s}{\sqrt{n}}$$

Typical 95% critical values: $t^* = 2.262$ for 9 degrees of freedom, $2.045$ for 29, $1.984$ for 99, approaching 1.96.

### Interval for a proportion

$$\hat{p} \pm z^* \sqrt{\frac{\hat{p}(1 - \hat{p})}{n}}$$

valid when there are at least about 10 successes and 10 failures. (For small samples, improved intervals such as Wilson's are better.)

### Interpreting confidence

A 95% confidence interval is produced by a **method** that captures the true parameter in 95% of repeated samples. For one computed interval, the parameter is either inside it or not; we do not say "there is a 95% probability that $\mu$ is in this interval" in the frequentist framework. We say "we are 95% confident", meaning the procedure succeeds 95% of the time.

### Width and sample size

The interval is wider for higher confidence (bigger critical value), for more variable data (bigger $\sigma$), and for smaller samples. To achieve a margin of error $E$ for a mean, solve $z^* \sigma/\sqrt{n} \le E$:

$$n \ge \left(\frac{z^* \sigma}{E}\right)^2$$

and for a proportion with no prior estimate, use the worst case $p = 0.5$: $n \ge \left(\frac{z^*}{2E}\right)^2$. Halving the margin of error requires four times the sample.

## Worked examples

### Example 1: A t interval for a mean

Ten students' daily screen times (hours): 3.2, 4.1, 2.8, 5.0, 3.9, 4.4, 3.6, 4.8, 2.9, 4.3. Construct a 95% confidence interval for the mean screen time.

```python
import statistics as st
from math import sqrt

data = [3.2, 4.1, 2.8, 5.0, 3.9, 4.4, 3.6, 4.8, 2.9, 4.3]
n, xbar, s = len(data), st.mean(data), st.stdev(data)
se = s / sqrt(n)
t_star = 2.262  # 95%, 9 degrees of freedom (from a t table)
margin = t_star * se
print(f"n={n} mean={xbar:.2f} s={s:.3f} SE={se:.3f}")
print(f"95% CI: {xbar - margin:.2f} to {xbar + margin:.2f} (margin {margin:.2f})")
print(f"with z* = 1.96 instead: {xbar - 1.96 * se:.2f} to {xbar + 1.96 * se:.2f} (too narrow for n = 10)")
```

Output:

```text
n=10 mean=3.90 s=0.764 SE=0.242
95% CI: 3.35 to 4.45 (margin 0.55)
with z* = 1.96 instead: 3.43 to 4.37 (too narrow for n = 10)
```

We are 95% confident that the mean daily screen time of the population sampled lies between about 3.35 and 4.45 hours. Using $z^*$ would understate the uncertainty for a sample this small.

### Example 2: A proportion interval and checking coverage

In a survey of 400 users, 248 say they would recommend an app. Construct a 95% interval for the true proportion, then simulate the meaning of "95% confidence".

$\hat{p} = 0.62$, $\text{SE} = \sqrt{0.62 \times 0.38/400} \approx 0.0243$, so the interval is $0.62 \pm 1.96 \times 0.0243 = 0.62 \pm 0.048$, from about 0.572 to 0.668.

```python
import random
from math import sqrt

p_hat, n = 248 / 400, 400
se = sqrt(p_hat * (1 - p_hat) / n)
print(f"95% CI: {p_hat - 1.96 * se:.3f} to {p_hat + 1.96 * se:.3f}")

rng = random.Random(1)
true_p, hits, trials = 0.62, 0, 2000
for _ in range(trials):
    successes = sum(rng.random() < true_p for _ in range(n))
    ph = successes / n
    half = 1.96 * sqrt(ph * (1 - ph) / n)
    hits += ph - half <= true_p <= ph + half
print("coverage close to 95%:", 0.93 < hits / trials < 0.97)
```

Output:

```text
95% CI: 0.572 to 0.668
coverage close to 95%: True
```

Repeating the whole survey 2,000 times with a known true proportion, about 95% of the resulting intervals contain it: that long-run success rate is what "95% confidence" means.

## Applications

- **Polls:** "52% ± 3 percentage points" is a 95% interval for a proportion.
- **A/B tests:** intervals for differences in conversion rates show the plausible size of an effect.
- **Engineering:** intervals for mean strength or lifetime support design margins.
- **Science:** results are reported as estimates with confidence intervals rather than single numbers.

## Common mistakes

- **Saying there is a 95% probability the parameter is in a computed interval.** The confidence is in the method.
- **Using z instead of t for small samples with unknown $\sigma$.** The interval is then too narrow.
- **Interpreting the interval as covering 95% of individual values.** It is about the mean (or proportion), not individuals.
- **Ignoring bias.** A confidence interval accounts for sampling error only, not for a biased sample.
- **Forgetting that halving the margin needs four times the data.**

## Revision notes

- Estimate ± critical value × SE; margin of error = critical value × SE.
- $z^*$: 1.645 (90%), 1.96 (95%), 2.576 (99%).
- Mean with unknown $\sigma$: $\bar{x} \pm t^*_{n-1} s/\sqrt{n}$; t has heavier tails, approaches z as df grows.
- Proportion: $\hat{p} \pm z^*\sqrt{\hat{p}(1-\hat{p})/n}$, with at least 10 successes and failures.
- 95% confidence: 95% of intervals from repeated samples contain the parameter.
- Sample size: $n \ge (z^*\sigma/E)^2$; for proportions $n \ge (z^*/(2E))^2$.

## Practice questions

:::question basic
A sample of 100 has mean 50 and known population standard deviation 10. Find a 95% confidence interval for the mean.
:::answer
$\text{SE} = 10/\sqrt{100} = 1$, so the interval is $50 \pm 1.96 \times 1$, from 48.04 to 51.96.
:::

:::question basic
What happens to the width of a confidence interval if the confidence level increases from 95% to 99%, with everything else unchanged?
:::answer
It becomes wider, because the critical value increases from 1.96 to 2.576. Greater confidence that the interval captures the parameter requires a wider net.
:::

:::question intermediate
A pollster wants a margin of error of at most 2 percentage points at 95% confidence for a proportion, with no prior estimate. How many people should be surveyed?
:::answer
Use the worst case $p = 0.5$: $n \ge (1.96/(2 \times 0.02))^2 = (49)^2 = 2401$. About 2,401 people are needed.
:::

:::question intermediate
Why do we use the t distribution rather than the normal when $\sigma$ is unknown?
:::answer
Replacing $\sigma$ with the sample estimate $s$ adds extra uncertainty, since $s$ varies from sample to sample. The standardised mean then follows a t distribution with $n - 1$ degrees of freedom, which has heavier tails than the normal, so its critical values are larger and the interval is appropriately wider, especially for small samples.
:::

:::question advanced
A 95% confidence interval for a mean is (12.1, 15.3). A student says: "95% of all values in the population lie between 12.1 and 15.3." Another says: "There is a 95% chance that μ is between 12.1 and 15.3." Explain what is wrong with each statement and give a correct interpretation.
:::answer
The first confuses an interval for the mean with the spread of individual values; individual values are far more variable than the mean, so many will fall outside the interval. The second treats the fixed parameter as random; in the frequentist framework μ is either in this interval or not. Correct: the interval was produced by a method that captures the true mean in 95% of repeated samples, so we are 95% confident that μ lies between 12.1 and 15.3.
:::

## Further learning

- **Next:** *Significance Testing & P-Values* uses the same sampling distributions to test claims.
- **Related:** *t-Tests & Chi-Square Tests* applies the t distribution to compare groups.
