---
lesson: significance-testing-p-values
title: Significance Testing & P-Values
summary: The logic of hypothesis testing: null and alternative hypotheses, test statistics, p-values, significance levels and rejection regions, Type I and Type II errors, power, and how to interpret results responsibly.
minutes: 45
type: theory
objectives:
  - Formulate null and alternative hypotheses and compute a z test statistic and its one- or two-sided p-value
  - Make and correctly word decisions at a significance level, using p-values or critical values
  - Explain Type I and Type II errors and power, and avoid common misinterpretations of p-values
review: ai-draft
---
## Introduction

Is a new teaching method better than the old one, or did the better scores happen by chance? Is a coin fair? Did a website change really increase sign-ups? **Hypothesis testing** gives a disciplined way to answer such questions: assume nothing interesting is happening, measure how surprising the data would be under that assumption, and reject the assumption only if the data are surprising enough. The **p-value** quantifies that surprise. It is one of the most used, and most misunderstood, numbers in science.

**Before you start:** you should know sampling distributions, standard errors, the normal distribution, and confidence intervals.

## Core theory

### Hypotheses

- The **null hypothesis** $H_0$ is the default claim of "no effect" or "no difference", stated about a parameter: $H_0: \mu = 500$.
- The **alternative hypothesis** $H_1$ (or $H_a$) is what we look for evidence of: $\mu < 500$ (one-sided), $\mu > 500$ (one-sided), or $\mu \ne 500$ (two-sided).

The alternative must be chosen **before** seeing the data, based on the question. A two-sided test is the default unless only one direction matters.

### Test statistic and p-value

A **test statistic** measures how far the data are from what $H_0$ predicts, in standard-error units. For a mean with known $\sigma$:

$$z = \frac{\bar{x} - \mu_0}{\sigma/\sqrt{n}}$$

The **p-value** is the probability, **assuming $H_0$ is true**, of obtaining a test statistic at least as extreme as the one observed, in the direction(s) of $H_1$. For a two-sided z test, $p = 2P(Z \ge |z|)$. A small p-value means the data would be unusual if $H_0$ were true, which is evidence against $H_0$.

### Significance level and decisions

Before testing, choose a **significance level** $\alpha$, often 0.05. If $p \le \alpha$, **reject $H_0$** ("the result is statistically significant at level $\alpha$"); otherwise **fail to reject $H_0$**. Equivalently, reject when the test statistic falls in the **rejection region** beyond the **critical value**, such as $|z| > 1.96$ for a two-sided test at $\alpha = 0.05$. We never "accept" or "prove" $H_0$: failing to find evidence is not evidence of no effect.

### Errors and power

| | $H_0$ true | $H_0$ false |
| :--- | :--- | :--- |
| Reject $H_0$ | **Type I error** (false positive), probability $\alpha$ | correct (power) |
| Fail to reject | correct | **Type II error** (false negative), probability $\beta$ |

The **power** $1 - \beta$ is the probability of detecting an effect that really exists. Power increases with sample size, with effect size, and with $\alpha$, and decreases with variability. Lowering $\alpha$ reduces Type I errors but, for fixed $n$, raises Type II errors.

### Interpreting p-values responsibly

- A p-value is **not** the probability that $H_0$ is true, nor the probability that the result happened "by chance".
- Statistical significance is not practical importance: with huge samples, trivially small effects become significant. Report **effect sizes and confidence intervals**.
- Testing many hypotheses inflates false positives (at $\alpha = 0.05$, about one in 20 true nulls is rejected). Adjust for **multiple comparisons** and avoid "p-hacking".
- Tests and confidence intervals agree: a two-sided test at level $\alpha$ rejects $H_0: \mu = \mu_0$ exactly when $\mu_0$ lies outside the $(1 - \alpha)$ confidence interval.

## Worked examples

### Example 1: A z test for a mean

A bottling machine should fill 500 ml with a known standard deviation of 30 ml. A sample of 36 bottles averages 488 ml. Is the machine under-filling?

$H_0: \mu = 500$. The question asks about under-filling, but suppose the quality team decided in advance on a two-sided test, since over-filling also matters. $\text{SE} = 30/\sqrt{36} = 5$ and $z = (488 - 500)/5 = -2.4$.

```python
from math import erf, sqrt

phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
mu0, sigma, n, xbar = 500, 30, 36, 488
z = (xbar - mu0) / (sigma / sqrt(n))
print(f"z = {z:.2f}")
print(f"one-sided p (H1: mu < 500) = {phi(z):.4f}")
print(f"two-sided p (H1: mu != 500) = {2 * phi(-abs(z)):.4f}")
for alpha in (0.05, 0.01):
    print(f"alpha {alpha}: two-sided {'reject' if 2 * phi(-abs(z)) < alpha else 'fail to reject'} H0")
```

Output:

```text
z = -2.40
one-sided p (H1: mu < 500) = 0.0082
two-sided p (H1: mu != 500) = 0.0164
alpha 0.05: two-sided reject H0
alpha 0.01: two-sided fail to reject H0
```

At the 5% level there is significant evidence that the mean fill differs from 500 ml; at the stricter 1% level there is not. The 95% confidence interval, $488 \pm 1.96 \times 5 = (478.2, 497.8)$, excludes 500, consistent with rejecting at $\alpha = 0.05$.

### Example 2: An exact binomial test and its power

A coin lands heads 15 times in 20 tosses. Is it biased? $H_0: p = 0.5$ against $H_1: p \ne 0.5$.

```python
from math import comb

n, heads = 20, 15
p_value = sum(comb(n, k) for k in range(heads, n + 1)) / 2**n
print(f"P(X >= {heads} | fair coin) = {p_value:.4f}")
print(f"two-sided p = {2 * p_value:.4f}")
alpha = 0.05
print("decision:", "reject H0" if 2 * p_value < alpha else "fail to reject H0")
power = sum(comb(n, k) * 0.75**k * 0.25**(n - k) for k in range(15, n + 1)) + sum(comb(n, k) * 0.75**k * 0.25**(n - k) for k in range(0, 6))
print(f"power against p = 0.75 (reject when X >= 15 or X <= 5): {power:.3f}")
```

Output:

```text
P(X >= 15 | fair coin) = 0.0207
two-sided p = 0.0414
decision: reject H0
power against p = 0.75 (reject when X >= 15 or X <= 5): 0.617
```

The p-value is exact, computed from the binomial distribution rather than a normal approximation. The last line shows the test's limitation: even if the coin truly lands heads 75% of the time, 20 tosses detect it only about 62% of the time. A larger sample would raise the power.

## Applications

- **A/B testing:** deciding whether a new design changes conversion rates.
- **Medicine:** clinical trials test whether a treatment outperforms placebo.
- **Manufacturing:** testing whether a process mean has drifted from its target.
- **Science:** p-values, with effect sizes and confidence intervals, summarise evidence in experiments.

## Common mistakes

- **Saying "the probability that $H_0$ is true is p".** The p-value assumes $H_0$ is true.
- **"Accepting" the null.** Failing to reject means insufficient evidence, not proof of no effect.
- **Choosing a one-sided test after seeing the data.** This halves the p-value unfairly.
- **Equating significance with importance.** Report the size of the effect.
- **Running many tests and reporting only the significant ones.** Correct for multiple comparisons.

## Revision notes

- $H_0$: no effect (equality); $H_1$: one- or two-sided, chosen in advance.
- $z = (\bar{x} - \mu_0)/(\sigma/\sqrt{n})$; two-sided $p = 2P(Z \ge |z|)$.
- Reject $H_0$ if $p \le \alpha$ (or the statistic is beyond the critical value, 1.96 for two-sided 5%).
- Type I: false positive (probability $\alpha$); Type II: false negative ($\beta$); power $= 1 - \beta$.
- Power grows with $n$, effect size, and $\alpha$.
- Two-sided test at $\alpha$ ↔ $(1 - \alpha)$ confidence interval.

## Practice questions

:::question basic
State $H_0$ and $H_1$ for testing whether a new battery lasts longer than the old mean of 10 hours.
:::answer
$H_0: \mu = 10$ hours (no improvement) and $H_1: \mu > 10$ hours, a one-sided alternative because the question asks only whether it lasts longer.
:::

:::question basic
A test gives $p = 0.03$. What is the decision at $\alpha = 0.05$ and at $\alpha = 0.01$?
:::answer
At $\alpha = 0.05$, $p \le \alpha$, so reject $H_0$. At $\alpha = 0.01$, $p > \alpha$, so fail to reject $H_0$. The same data can be significant at one level and not at a stricter one.
:::

:::question intermediate
Explain the difference between a Type I and a Type II error for a spam filter that "rejects" the hypothesis that an email is legitimate.
:::answer
A Type I error rejects a true null: a legitimate email is marked as spam (a false positive). A Type II error fails to reject a false null: a spam email reaches the inbox (a false negative). Making the filter stricter reduces one error type at the cost of increasing the other.
:::

:::question intermediate
A study with 2 million users finds a statistically significant increase in average session time of 0.2 seconds ($p < 0.001$). Should the company celebrate?
:::answer
Not necessarily. With such a huge sample, even a tiny effect is statistically significant. The practical effect, 0.2 seconds, is probably negligible for the business, so they should look at the effect size and its confidence interval and weigh it against the costs of the change.
:::

:::question advanced
A researcher tests 20 independent hypotheses at $\alpha = 0.05$, all of which are actually true nulls. What is the probability of at least one false positive, and how can it be controlled?
:::answer
The probability of no false positives is $0.95^{20} \approx 0.358$, so the probability of at least one is about $0.642$. Multiple-comparison corrections control this: the Bonferroni method tests each hypothesis at $\alpha/20 = 0.0025$, which keeps the family-wise error rate at most 0.05, while methods such as Benjamini-Hochberg control the false discovery rate with more power.
:::

## Further learning

- **Next:** *t-Tests & Chi-Square Tests* applies this logic when $\sigma$ is unknown and to categorical data.
- **Related:** *Point Estimation & Confidence Intervals* shows the interval view of the same evidence.
