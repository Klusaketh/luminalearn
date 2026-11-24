---
lesson: descriptive-statistics
title: Descriptive Statistics: Center, Spread & Shape
summary: Summarising data with measures of centre (mean, median, mode), spread (range, variance, standard deviation, interquartile range), and shape (skewness, outliers), with box plots and the five-number summary.
minutes: 45
type: theory
objectives:
  - Compute and interpret the mean, median, mode, variance, standard deviation, quartiles, and interquartile range of a data set
  - Choose robust summaries for skewed data or data with outliers, and detect outliers with the 1.5 × IQR rule
  - Read and construct box plots and five-number summaries, and describe the shape of a distribution
review: ai-draft
---
## Introduction

Raw data, such as a thousand response times or a class's exam marks, is hard to understand by looking at the numbers. **Descriptive statistics** condense data into a few meaningful numbers and pictures: where the data is centred, how spread out it is, and what shape it has. Good summaries reveal patterns and problems (an outlier, a skewed distribution) before any formal analysis begins, and choosing the right summary avoids misleading conclusions.

**Before you start:** you should be comfortable with summation notation and basic arithmetic; the idea of expectation and variance from probability helps.

## Core theory

### Measures of centre

For data $x_1, \dots, x_n$:

- **Mean:** $\bar{x} = \frac{1}{n}\sum_i x_i$, the balance point. It uses every value, so a single extreme value can pull it a long way.
- **Median:** the middle value when the data is sorted (the average of the two middle values when $n$ is even). It is **robust**: outliers barely affect it.
- **Mode:** the most frequent value; useful for categorical data.

For **skewed** data, such as incomes or response times with a long right tail, the mean is pulled towards the tail and exceeds the median, so the median is usually the better "typical" value.

### Measures of spread

- **Range:** maximum minus minimum; very sensitive to outliers.
- **Sample variance:** $s^2 = \frac{1}{n - 1}\sum_i (x_i - \bar{x})^2$ and **standard deviation** $s = \sqrt{s^2}$, in the data's units. Dividing by $n - 1$ rather than $n$ (Bessel's correction) makes $s^2$ an unbiased estimate of the population variance, because deviations are measured from $\bar{x}$, which is itself fitted to the data.
- **Quartiles:** $Q_1$, $Q_2$ (the median), and $Q_3$ split the sorted data into quarters; the **interquartile range** $\text{IQR} = Q_3 - Q_1$ is the spread of the middle half and is robust to outliers. (Several slightly different conventions exist for computing quartiles of small samples; software may disagree in the second decimal.)
- **z-score:** $z = (x - \bar{x})/s$ says how many standard deviations a value lies from the mean.

### Shape and outliers

A distribution is **symmetric** if its two halves mirror each other, **right-skewed** (positively skewed) if it has a long right tail, and **left-skewed** if the long tail is on the left. Rough guide: mean > median suggests right skew. A common rule flags **outliers** as values below $Q_1 - 1.5\,\text{IQR}$ or above $Q_3 + 1.5\,\text{IQR}$. Outliers should be investigated, not automatically deleted: they may be errors or the most interesting points.

### Five-number summary and box plots

The **five-number summary** is minimum, $Q_1$, median, $Q_3$, maximum. A **box plot** draws a box from $Q_1$ to $Q_3$ with a line at the median, whiskers to the most extreme non-outlying values, and individual points for outliers. Side-by-side box plots compare groups at a glance. Histograms show the full shape and reveal features box plots hide, such as two peaks (bimodality).

## Worked examples

### Example 1: Summaries of response times

A web service records 12 response times in milliseconds:

`120, 135, 128, 140, 132, 125, 138, 130, 127, 900, 133, 129`

```python
import statistics as st

times = [120, 135, 128, 140, 132, 125, 138, 130, 127, 900, 133, 129]
print("mean", round(st.mean(times), 1), "| median", st.median(times))
print("stdev", round(st.stdev(times), 1), "| range", max(times) - min(times))

s = sorted(times)
lower, upper = s[: len(s) // 2], s[(len(s) + 1) // 2 :]
q1, q3 = st.median(lower), st.median(upper)
iqr = q3 - q1
print("Q1", q1, "| Q3", q3, "| IQR", iqr)
low_fence, high_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
print("fences", low_fence, high_fence, "| outliers", [t for t in times if t < low_fence or t > high_fence])

clean = [t for t in times if t != 900]
print("without outlier: mean", round(st.mean(clean), 1), "| median", st.median(clean), "| stdev", round(st.stdev(clean), 1))
```

Output:

```text
mean 194.8 | median 131.0
stdev 222.2 | range 780
Q1 127.5 | Q3 136.5 | IQR 9.0
fences 114.0 150.0 | outliers [900]
without outlier: mean 130.6 | median 130 | stdev 5.8
```

One slow request (900 ms) drags the mean to 194.8 ms and the standard deviation to 222.2 ms, although almost every request took 120 to 140 ms. The median (131 ms) and IQR (9 ms) describe the typical behaviour well and hardly change when the outlier is removed. Here the quartiles use the "median of each half" convention.

### Example 2: Comparing two classes

Two sections take the same test.

- Section A: 55, 62, 68, 70, 71, 73, 75, 78, 81, 95
- Section B: 40, 52, 66, 71, 72, 74, 76, 79, 88, 98

```python
import statistics as st

A = [55, 62, 68, 70, 71, 73, 75, 78, 81, 95]
B = [40, 52, 66, 71, 72, 74, 76, 79, 88, 98]
for name, data in (("A", A), ("B", B)):
    s = sorted(data)
    q1, q3 = st.median(s[:5]), st.median(s[5:])
    print(name, "five-number:", (s[0], q1, st.median(s), q3, s[-1]), "| mean", st.mean(s), "| sd", round(st.stdev(s), 1))
z = (95 - st.mean(A)) / st.stdev(A)
print("z-score of 95 in A:", round(z, 2))
```

Output:

```text
A five-number: (55, 68, 72.0, 78, 95) | mean 72.8 | sd 10.9
B five-number: (40, 66, 73.0, 79, 98) | mean 71.6 | sd 16.5
z-score of 95 in A: 2.05
```

The centres are almost the same, but section B is much more spread out (standard deviation 16.5 against 10.9), with both weaker and stronger students. A score of 95 in section A is about 2.05 standard deviations above its mean.

## Applications

- **Performance monitoring:** median and high percentiles (such as the 99th) describe latency better than the mean.
- **Education and HR:** five-number summaries and box plots compare groups.
- **Data cleaning:** IQR rules and z-scores flag suspicious values for checking.
- **Exploratory data analysis:** summaries are the first step before modelling.

## Common mistakes

- **Reporting the mean for skewed data.** Report the median (and IQR) too.
- **Dividing by n for the sample variance.** Use $n - 1$ for a sample estimate.
- **Deleting outliers without investigation.** They may be real and important.
- **Comparing standard deviations of data in different units.** Use z-scores or relative measures.
- **Trusting summaries without plotting.** Very different data sets can share the same mean and standard deviation.

## Revision notes

- Mean (sensitive), median (robust), mode (categorical).
- $s^2 = \frac{1}{n-1}\sum (x_i - \bar{x})^2$; $s$ in data units.
- Quartiles, $\text{IQR} = Q_3 - Q_1$; outliers beyond $Q_1 - 1.5\,\text{IQR}$ or $Q_3 + 1.5\,\text{IQR}$.
- Right skew: mean > median; long right tail.
- Five-number summary and box plots; z-score $(x - \bar{x})/s$.
- Always plot the data.

## Practice questions

:::question basic
Find the mean and median of 4, 8, 6, 5, 3, 100.
:::answer
The mean is $126/6 = 21$. Sorted, the data is 3, 4, 5, 6, 8, 100, so the median is $(5 + 6)/2 = 5.5$. The outlier 100 pulls the mean far above the typical values, while the median is unaffected.
:::

:::question basic
Why is the IQR preferred to the range for describing spread when outliers are present?
:::answer
The range depends only on the two most extreme values, so a single outlier can change it drastically. The IQR measures the spread of the middle 50% of the data, which outliers do not affect.
:::

:::question intermediate
For data with $Q_1 = 40$ and $Q_3 = 60$, which of the values 5, 15, 95, and 92 are outliers by the 1.5 × IQR rule?
:::answer
IQR = 20, so the fences are $40 - 30 = 10$ and $60 + 30 = 90$. The values 5, 92, and 95 lie outside the fences and are flagged as outliers; 15 is inside.
:::

:::question intermediate
A distribution of household incomes has mean 72,000 and median 51,000. What does this suggest about its shape?
:::answer
The mean is well above the median, which suggests a right-skewed distribution: most households earn moderate amounts, and a long tail of high incomes pulls the mean upwards. The median is the better description of a typical household.
:::

:::question advanced
Explain why the sample variance divides by $n - 1$ instead of $n$.
:::answer
Deviations are measured from the sample mean $\bar{x}$, which is chosen to minimise the sum of squared deviations for this particular sample, so $\sum (x_i - \bar{x})^2$ is systematically smaller than $\sum (x_i - \mu)^2$ around the true mean. On average it is smaller by exactly one variance's worth, so dividing by $n - 1$ instead of $n$ corrects the bias and makes $s^2$ an unbiased estimator of $\sigma^2$. Intuitively, once the mean is fixed, only $n - 1$ deviations are free to vary.
:::

## Further learning

- **Next:** *Data Collection & Sampling Methods* explains how data should be gathered before it is summarised.
- **Related:** *Expectation, Variance & Moments* in Probability defines the population quantities these statistics estimate.
