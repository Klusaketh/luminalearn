---
lesson: t-tests-chi-square
title: t-Tests & Chi-Square Tests
summary: One-sample, paired, and two-sample t-tests for comparing means when the standard deviation is unknown, their assumptions, and chi-square tests of goodness of fit and of independence for categorical data.
minutes: 55
type: theory
objectives:
  - Choose between one-sample, paired, and independent two-sample t-tests and compute their test statistics
  - Explain why pairing increases power and state the assumptions of t procedures
  - Carry out chi-square goodness-of-fit and independence tests from observed and expected counts
review: ai-draft
---
## Introduction

Real comparisons rarely come with a known population standard deviation. Does a training course raise test scores? Do two groups of users spend different amounts of time in an app? Is a preference for a product related to age group? **t-tests** compare means using the sample standard deviation, and **chi-square tests** handle counts in categories. Together they cover a large share of everyday statistical analysis.

**Before you start:** you should know hypothesis testing, p-values, standard errors, and the t distribution.

## Core theory

### One-sample t-test

To test $H_0: \mu = \mu_0$ with unknown $\sigma$:

$$t = \frac{\bar{x} - \mu_0}{s/\sqrt{n}}, \qquad \text{df} = n - 1$$

and the p-value comes from the t distribution with $n - 1$ degrees of freedom.

### Paired t-test

When each observation in one sample is matched with one in the other, such as the same student before and after a course, analyse the **differences** $d_i = x_{i,\text{after}} - x_{i,\text{before}}$ with a one-sample t-test of $H_0: \mu_d = 0$:

$$t = \frac{\bar{d}}{s_d/\sqrt{n}}, \qquad \text{df} = n - 1$$

Pairing removes the variation **between** subjects (some students are simply stronger), which often makes the test far more powerful.

### Independent two-sample t-test

For two separate groups, compare $\bar{x}_1 - \bar{x}_2$ with its standard error. **Welch's** test does not assume equal variances:

$$t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}$$

with degrees of freedom from the Welch-Satterthwaite formula (software computes it; a conservative choice is $\min(n_1, n_2) - 1$). Welch's version is the recommended default. The pooled-variance test assumes equal population variances.

### Assumptions

t procedures assume independent observations (random samples or random assignment) and approximately normal populations, or differences for the paired test. They are **robust** to non-normality when samples are moderately large (roughly $n \ge 30$, by the CLT), but outliers and strong skewness can mislead small-sample tests; check plots first.

### Chi-square goodness of fit

For one categorical variable with $k$ categories, test whether observed counts $O_i$ match the counts $E_i$ expected under $H_0$:

$$\chi^2 = \sum_i \frac{(O_i - E_i)^2}{E_i}, \qquad \text{df} = k - 1$$

### Chi-square test of independence

For a two-way table of counts (an $r \times c$ **contingency table**), $H_0$ says the two variables are independent. Expected counts are

$$E_{ij} = \frac{(\text{row } i \text{ total})(\text{column } j \text{ total})}{\text{grand total}}$$

and $\chi^2 = \sum (O - E)^2/E$ with $\text{df} = (r - 1)(c - 1)$. Large values give small p-values (the test is one-sided by nature). The approximation needs expected counts of at least about 5 in each cell. A significant result shows association, not causation, and not its strength.

## Worked examples

### Example 1: Paired versus independent analysis

Eight students' scores before and after a revision course:

| Student | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Before | 72 | 65 | 80 | 58 | 77 | 69 | 74 | 63 |
| After | 75 | 70 | 79 | 66 | 82 | 71 | 80 | 64 |

```python
import statistics as st
from math import gamma, pi, sqrt

def t_pdf(x, df):
    return gamma((df + 1) / 2) / (sqrt(df * pi) * gamma(df / 2)) * (1 + x * x / df) ** (-(df + 1) / 2)

def t_two_sided_p(t, df, steps=20000):
    t = abs(t)
    h = t / steps
    area = t_pdf(0, df) + t_pdf(t, df) + sum((4 if i % 2 else 2) * t_pdf(i * h, df) for i in range(1, steps))
    return 2 * (0.5 - area * h / 3)

before = [72, 65, 80, 58, 77, 69, 74, 63]
after = [75, 70, 79, 66, 82, 71, 80, 64]
diffs = [a - b for a, b in zip(after, before)]
d_mean, d_sd, n = st.mean(diffs), st.stdev(diffs), len(diffs)
t_paired = d_mean / (d_sd / sqrt(n))
print(f"paired: mean diff {d_mean:.3f}, sd {d_sd:.3f}, t = {t_paired:.3f}, df = {n - 1}, p = {t_two_sided_p(t_paired, n - 1):.4f}")

se_welch = sqrt(st.variance(before) / n + st.variance(after) / n)
t_ind = (st.mean(after) - st.mean(before)) / se_welch
print(f"wrongly treated as independent: t = {t_ind:.3f}, p about {t_two_sided_p(t_ind, 14):.3f}")
```

Output:

```text
paired: mean diff 3.625, sd 2.925, t = 3.506, df = 7, p = 0.0099
wrongly treated as independent: t = 1.026, p about 0.322
```

The t-distribution p-value is computed by integrating its density with Simpson's rule. Analysed correctly as paired data, the average improvement of 3.6 marks is significant ($p \approx 0.01$). Treating the same numbers as two independent groups buries the consistent improvement under the large differences between students, and the test finds nothing ($p \approx 0.32$). The design of the study decides the test.

### Example 2: A chi-square test of independence

A survey asks 200 people of two age groups which of three product designs they prefer.

| | Design A | Design B | Design C | Total |
| :--- | :--- | :--- | :--- | :--- |
| Under 30 | 30 | 45 | 25 | 100 |
| 30 and over | 20 | 25 | 55 | 100 |
| Total | 50 | 70 | 80 | 200 |

With 2 degrees of freedom, the chi-square upper-tail probability has the simple form $P(\chi^2_2 > x) = e^{-x/2}$.

```python
from math import exp

observed = [[30, 45, 25], [20, 25, 55]]
rows = [sum(r) for r in observed]
cols = [sum(c) for c in zip(*observed)]
total = sum(rows)
expected = [[r * c / total for c in cols] for r in rows]
chi2 = sum((o - e) ** 2 / e for orow, erow in zip(observed, expected) for o, e in zip(orow, erow))
df = (len(rows) - 1) * (len(cols) - 1)
print("expected:", [[round(e, 1) for e in row] for row in expected])
print(f"chi-square = {chi2:.2f}, df = {df}, p = {exp(-chi2 / 2):.6f}")
print("critical value at alpha 0.05 for df 2: 5.991 ->", "reject H0" if chi2 > 5.991 else "fail to reject H0")
```

Output:

```text
expected: [[25.0, 35.0, 40.0], [25.0, 35.0, 40.0]]
chi-square = 18.96, df = 2, p = 0.000076
critical value at alpha 0.05 for df 2: 5.991 -> reject H0
```

Under independence, each age group would split like the overall totals (25, 35, 40). The observed counts differ strongly, especially for design C, so design preference is associated with age group.

## Applications

- **Education and medicine:** paired t-tests for before-and-after measurements.
- **Product analytics:** Welch's t-test compares average metrics between two user groups.
- **Survey analysis:** chi-square tests relate categorical answers to demographics.
- **Genetics:** goodness-of-fit tests compare observed offspring ratios with Mendelian predictions.

## Common mistakes

- **Using an independent test on paired data.** It ignores the pairing and loses power.
- **Using the pooled test when variances clearly differ.** Prefer Welch's test.
- **Running chi-square tests on percentages instead of counts.** The statistic needs counts.
- **Ignoring small expected counts.** Combine categories or use an exact test.
- **Reading a significant chi-square as a causal or strong relationship.** It shows association only.

## Revision notes

- One-sample: $t = (\bar{x} - \mu_0)/(s/\sqrt{n})$, df $n - 1$.
- Paired: one-sample t on differences; removes between-subject variation.
- Welch two-sample: $t = (\bar{x}_1 - \bar{x}_2)/\sqrt{s_1^2/n_1 + s_2^2/n_2}$.
- Assumptions: independence, rough normality (or large n), no extreme outliers.
- $\chi^2 = \sum (O - E)^2/E$; goodness of fit df $k - 1$; independence df $(r-1)(c-1)$, $E = $ row × column / total.
- Expected counts should be at least about 5.

## Practice questions

:::question basic
Which t-test should you use to compare the reaction times of the same 15 people with and without caffeine?
:::answer
A paired t-test, because each person is measured under both conditions. Analyse the 15 differences with a one-sample t-test of mean difference 0, using 14 degrees of freedom.
:::

:::question basic
How many degrees of freedom does a chi-square test of independence on a 3 × 4 table have?
:::answer
$(3 - 1)(4 - 1) = 6$ degrees of freedom.
:::

:::question intermediate
A die is rolled 60 times, giving counts 5, 8, 9, 8, 10, 20 for faces 1 to 6. Compute the chi-square goodness-of-fit statistic for fairness.
:::answer
Each expected count is 10. $\chi^2 = (25 + 4 + 1 + 4 + 0 + 100)/10 = 13.4$ with 5 degrees of freedom. The 5% critical value for 5 df is 11.07, so the die appears unfair, mainly because of the excess of sixes.
:::

:::question intermediate
Why does pairing usually make a t-test more powerful?
:::answer
Pairing compares each subject with itself, so the large differences between subjects cancel out of the differences $d_i$. The standard deviation of the differences is then usually much smaller than the spread of the raw scores, giving a smaller standard error and a larger t statistic for the same average effect.
:::

:::question advanced
Two independent groups of 40 users have mean session times 12.4 and 10.9 minutes with standard deviations 3.8 and 4.6. Compute Welch's t statistic and judge significance at the 5% level.
:::answer
$\text{SE} = \sqrt{3.8^2/40 + 4.6^2/40} = \sqrt{0.361 + 0.529} = \sqrt{0.890} \approx 0.943$. $t = (12.4 - 10.9)/0.943 \approx 1.59$. With about 75 degrees of freedom the two-sided 5% critical value is about 1.99, so the difference is not statistically significant; the data are consistent with no difference in mean session time.
:::

## Further learning

- **Next:** *Correlation & Simple Linear Regression* studies the relationship between two numerical variables.
- **Related:** *Significance Testing & P-Values* explains the logic behind every test here.
