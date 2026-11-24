---
lesson: correlation-linear-regression
title: Correlation & Simple Linear Regression
summary: Measuring linear association with the Pearson correlation coefficient, fitting a least-squares regression line, interpreting slope, intercept, residuals, and R-squared, and recognising the limits of correlation and extrapolation.
minutes: 50
type: theory
objectives:
  - Compute and interpret the Pearson correlation coefficient and recognise what it does not measure
  - Fit a least-squares line, interpret its slope and intercept, and make predictions within the data range
  - Use residuals and R-squared to judge fit, and explain why plots, outliers, and confounding matter
review: ai-draft
---
## Introduction

Do students who study more score higher? Does a car's weight predict its fuel economy? **Correlation** measures how strongly two numerical variables move together in a straight-line pattern, and **simple linear regression** finds the best straight line for predicting one from the other. These are the most widely used tools for describing relationships in data, and the starting point for the regression models used throughout machine learning.

**Before you start:** you should know means, standard deviations, z-scores, and covariance.

## Core theory

### Scatter plots

Always start with a **scatter plot**: it shows the direction (positive or negative), form (linear or curved), strength, and any outliers. Numbers summarise a pattern only after you have seen it.

### Pearson's correlation coefficient

$$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}} = \frac{1}{n - 1}\sum z_{x_i} z_{y_i}$$

Properties: $-1 \le r \le 1$; the sign gives the direction; $|r| = 1$ only for points exactly on a line; $r$ has no units and is unchanged by changing units; it is symmetric in $x$ and $y$. Rough guide: $|r|$ around 0.1 is weak, 0.5 moderate, 0.8 strong, though context matters.

$r$ measures **linear** association only. A perfect curved relationship can have $r = 0$, and very different data sets can share the same $r$ (Anscombe's quartet). A single outlier can create or destroy a strong correlation.

### The least-squares line

The regression line $\hat{y} = b_0 + b_1 x$ chooses $b_0$ and $b_1$ to minimise the sum of squared **residuals** $e_i = y_i - \hat{y}_i$:

$$b_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2} = r\frac{s_y}{s_x}, \qquad b_0 = \bar{y} - b_1 \bar{x}$$

The line always passes through $(\bar{x}, \bar{y})$, and the residuals sum to zero. The **slope** is the predicted change in $y$ for a one-unit increase in $x$; the **intercept** is the predicted $y$ at $x = 0$, which is meaningful only if $x = 0$ is within or near the data.

### Goodness of fit

**$R^2$** (equal to $r^2$ in simple regression) is the fraction of the variation in $y$ explained by the line:

$$R^2 = 1 - \frac{\sum e_i^2}{\sum (y_i - \bar{y})^2}$$

A **residual plot** (residuals against $x$ or $\hat{y}$) should look like random scatter around zero. A curve suggests the relationship is not linear; a funnel shape suggests the spread changes with $x$.

### Cautions

- **Extrapolation:** predictions outside the range of the observed $x$ values can be wildly wrong.
- **Influential points:** an outlier in $x$ can pull the line towards itself.
- **Correlation is not causation:** a **lurking (confounding) variable** may drive both variables, as with ice-cream sales and drownings, both driven by temperature.
- **Regression to the mean:** extreme values on one measurement tend to be followed by less extreme ones, because $|r| < 1$.

## Worked examples

### Example 1: Study hours and marks

| Hours | 2 | 3 | 5 | 6 | 8 | 9 | 10 | 12 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Marks | 55 | 58 | 65 | 67 | 74 | 78 | 79 | 88 |

```python
import statistics as st

hours = [2, 3, 5, 6, 8, 9, 10, 12]
marks = [55, 58, 65, 67, 74, 78, 79, 88]
n = len(hours)
xbar, ybar = st.mean(hours), st.mean(marks)
sxy = sum((x - xbar) * (y - ybar) for x, y in zip(hours, marks))
sxx = sum((x - xbar) ** 2 for x in hours)
syy = sum((y - ybar) ** 2 for y in marks)
b1 = sxy / sxx
b0 = ybar - b1 * xbar
r = sxy / (sxx * syy) ** 0.5
print(f"slope {b1:.3f}, intercept {b0:.3f}, r = {r:.4f}, R^2 = {r * r:.4f}")
residuals = [y - (b0 + b1 * x) for x, y in zip(hours, marks)]
print("residuals:", [round(e, 2) for e in residuals], "sum", abs(round(sum(residuals), 10)))
print(f"predicted mark for 7 hours: {b0 + b1 * 7:.1f}")
print("check with statistics.linear_regression:", [round(v, 3) for v in st.linear_regression(hours, marks)])
```

Output:

```text
slope 3.222, intercept 48.346, r = 0.9974, R^2 = 0.9947
residuals: [0.21, -0.01, 0.54, -0.68, -0.13, 0.65, -1.57, 0.99] sum 0.0
predicted mark for 7 hours: 70.9
check with statistics.linear_regression: [3.222, 48.346]
```

Each extra hour of study is associated with about 3.2 more marks, and the line explains 99.5% of the variation in marks in this (unusually tidy) sample. The residuals are small, show no pattern, and sum to zero. Predicting for 7 hours is safe, since 7 lies within the observed range; predicting for 40 hours would be extrapolation. These data show association, not proof that studying caused the higher marks, though it is plausible.

### Example 2: What correlation misses

```python
import statistics as st

xs = list(range(-5, 6))
ys = [x * x for x in xs]
print("r for y = x^2 on a symmetric range:", round(st.correlation(xs, ys), 4))
ax = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
ay1 = [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]
ay2 = [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]
for name, ys2 in (("set 1", ay1), ("set 2", ay2)):
    slope, intercept = st.linear_regression(ax, ys2)
    print(name, f"r = {st.correlation(ax, ys2):.3f}, line y = {intercept:.2f} + {slope:.3f}x")
```

Output:

```text
r for y = x^2 on a symmetric range: 0.0
set 1 r = 0.816, line y = 3.00 + 0.500x
set 2 r = 0.816, line y = 3.00 + 0.500x
```

A perfect quadratic relationship has a correlation of exactly zero. The two data sets from Anscombe's quartet have the same correlation and the same regression line, yet set 1 is a noisy straight line while set 2 is a smooth curve. Only a scatter plot reveals the difference.

## Applications

- **Forecasting:** trend lines predict sales, demand, or growth within the observed range.
- **Science and engineering:** calibration lines convert sensor readings into physical quantities.
- **Machine learning:** linear regression is the foundation of many predictive models.
- **Finance:** a stock's beta is the slope of its returns regressed on market returns.

## Common mistakes

- **Concluding causation from correlation.** Look for confounders or run an experiment.
- **Using $r$ for curved relationships.** Plot first; $r$ measures linear association only.
- **Extrapolating beyond the data.**
- **Interpreting an intercept far outside the data range.**
- **Ignoring influential outliers.** Check how the line changes without them.

## Revision notes

- Plot first: direction, form, strength, outliers.
- $r = \frac{1}{n-1}\sum z_x z_y \in [-1, 1]$; linear association only; unit-free.
- Least squares: $b_1 = r s_y/s_x$, $b_0 = \bar{y} - b_1\bar{x}$; line through $(\bar{x}, \bar{y})$.
- Residual $e = y - \hat{y}$; residuals sum to zero; residual plots should be patternless.
- $R^2 = r^2$ = fraction of variation explained.
- No extrapolation; correlation ≠ causation.

## Practice questions

:::question basic
What does a correlation of $r = -0.85$ between hours of TV watched and exam marks indicate?
:::answer
A strong negative linear association: students who watch more TV tend to have lower marks. It does not show that TV causes lower marks; other factors could explain both.
:::

:::question basic
A regression line for house prices is $\hat{y} = 50 + 2.5x$, with $x$ in square metres and $y$ in thousands. Interpret the slope.
:::answer
Each additional square metre of floor area is associated with an average increase of 2.5 thousand (2,500) in predicted price.
:::

:::question intermediate
If $r = 0.6$, $s_x = 4$, $s_y = 10$, $\bar{x} = 20$, and $\bar{y} = 70$, find the regression line of $y$ on $x$.
:::answer
$b_1 = r s_y/s_x = 0.6 \times 10/4 = 1.5$ and $b_0 = 70 - 1.5 \times 20 = 40$. So $\hat{y} = 40 + 1.5x$.
:::

:::question intermediate
A regression of ice-cream sales on drowning deaths shows $R^2 = 0.7$. Explain what this does and does not show.
:::answer
70% of the variation in drowning deaths (or sales) is associated with variation in the other variable through a linear relationship. It does not show that ice cream causes drowning: hot weather is a lurking variable that increases both swimming and ice-cream sales.
:::

:::question advanced
Explain "regression to the mean" using students who score in the top 5% on a first test.
:::answer
Scores combine true ability with luck. Students in the top 5% on the first test are disproportionately those who had good luck as well as high ability. On a second test, their luck averages out, so their scores tend to be closer to the mean, although still above average. Mathematically, the predicted z-score on the second test is $r$ times the first, and with $|r| < 1$ predictions are pulled towards the mean. This happens without any real change in ability.
:::

## Further learning

- **Next:** *Linear Regression & Gradient Descent* in Machine Learning fits lines and planes by optimisation.
- **Related:** *Joint Distributions, Covariance & Correlation* in Probability defines the population versions of these quantities.
