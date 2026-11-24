---
lesson: feature-scaling-encoding
title: Feature Scaling & One-Hot Encoding
summary: Why and when numerical features need scaling (min-max, standardisation, robust scaling, log transforms), how to encode categorical features (ordinal, one-hot, and strategies for high cardinality), the dummy-variable trap, and fitting transformations on training data only.
minutes: 40
type: theory
objectives:
  - Apply min-max scaling, standardisation, and robust scaling, and decide which models need scaled inputs
  - Encode nominal and ordinal categorical features correctly, including one-hot encoding and the dummy-variable trap
  - Choose strategies for high-cardinality categories and unseen values without leaking information
review: ai-draft
---
## Introduction

Raw data rarely arrives in a form a model can use well. Ages range from 18 to 80 while incomes range from ₹10,000 to ₹10,00,000; cities are words, not numbers. Many algorithms compare distances or follow gradients, so a feature measured in large units can dominate one measured in small units, and a carelessly numbered category can invent an order that does not exist. Scaling and encoding fix both problems, and doing them correctly is one of the cheapest ways to improve a model.

**Before you start:** you should know the mean and standard deviation from *Descriptive Statistics: Center, Spread & Shape*.

## Core theory

### Which models need scaling?

- **Distance-based models** (k-nearest neighbours, k-means, SVMs with RBF kernels) compare feature differences directly: unscaled, the feature with the largest range dominates.
- **Gradient-based training** (linear and logistic regression, neural networks) converges much faster when features have similar scales, because the loss surface is less elongated.
- **Regularised models** penalise coefficient sizes, which is only fair if features share a scale.
- **PCA** finds directions of maximum variance, so unscaled features with large variance dominate.
- **Tree-based models** (decision trees, random forests, gradient boosting) split on thresholds of one feature at a time and are unaffected by monotonic scaling.

### Scaling methods

- **Min-max scaling:** $x' = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$ maps values to $[0, 1]$. It preserves the shape of the distribution but is sensitive to outliers, which squash the other values together.
- **Standardisation (z-score):** $z = \frac{x - \mu}{\sigma}$ gives mean 0 and standard deviation 1. It is the default for most models.
- **Robust scaling:** $\frac{x - \text{median}}{\text{IQR}}$ uses statistics that outliers barely affect.
- **Log transform:** $\log(1 + x)$ compresses heavily skewed features such as income or view counts before scaling.

All scaling parameters ($\mu$, $\sigma$, min, max) must be **learned from the training set** and reused for validation, test, and production data. Fitting them on the full dataset leaks information from the test set.

### Encoding categorical features

- **Nominal** categories have no order (city, colour). **Ordinal** categories have a natural order (small < medium < large; low < medium < high).
- **Ordinal encoding** maps ordered categories to integers that respect the order. Using integers for nominal categories (Chennai = 0, Hyderabad = 1, Pune = 2) invents an order and distances that a linear or distance-based model will take literally.
- **One-hot encoding** creates one binary column per category, with a 1 in the column of the observed category. It adds no false order.
- **Dummy-variable trap:** with an intercept, the one-hot columns always sum to 1, so they are perfectly collinear with the intercept. Unregularised linear models should drop one column (using $k - 1$ dummies, with the dropped category as the reference).
- **Unseen categories** at prediction time need a plan, such as an all-zero row or an explicit "other" category.

### High-cardinality categories

Features with thousands of values (postcodes, product IDs) make one-hot encoding huge and sparse. Alternatives include grouping rare categories into "other", **frequency encoding**, **target encoding** (replacing each category with the average label, computed out-of-fold to avoid leakage), the **hashing trick** (hashing categories into a fixed number of columns), and learned **embeddings** in neural networks.

## Worked examples

### Example 1: How scaling changes the nearest neighbour

Six customers are described by age, monthly income, and city. The query customer is 58 years old and earns ₹50,500. Who is most similar?

```python
import math

# (age, monthly income in rupees, city, bought the premium plan?)
people = [
    (25, 50000, "Hyderabad", "no"),
    (32, 82000, "Pune", "no"),
    (47, 61000, "Chennai", "yes"),
    (52, 95000, "Hyderabad", "yes"),
    (61, 52000, "Pune", "yes"),
    (23, 64000, "Chennai", "no"),
]
query = (58, 50500)


def nearest(points, q):
    return min(range(len(points)), key=lambda i: math.dist(points[i], q))


raw = [(age, income) for age, income, _, _ in people]
i = nearest(raw, query)
print(f"unscaled: nearest to {query} is {people[i][:2]} -> predicts '{people[i][3]}'")

# Standardise each column with the mean and standard deviation of the data
cols = list(zip(*raw))
means = [sum(c) / len(c) for c in cols]
stds = [math.sqrt(sum((v - m) ** 2 for v in c) / len(c)) for c, m in zip(cols, means)]


def z(p):
    return tuple((v - m) / s for v, m, s in zip(p, means, stds))


print(f"means: age {means[0]:.1f}, income {means[1]:.1f}; std devs: age {stds[0]:.2f}, income {stds[1]:.1f}")
scaled = [z(p) for p in raw]
i = nearest(scaled, z(query))
print(f"standardised: query becomes ({z(query)[0]:.3f}, {z(query)[1]:.3f}); nearest is {people[i][:2]} -> predicts '{people[i][3]}'")

# Min-max scaling to [0, 1]
lo, hi = min(cols[1]), max(cols[1])
print("income min-max scaled:", [round((v - lo) / (hi - lo), 3) for v in cols[1]])

# One-hot encoding of the city column
cities = sorted({city for _, _, city, _ in people})
print("one-hot columns:", cities)
for _, _, city, _ in people[:3]:
    print(f"  {city:9} -> {[1 if city == c else 0 for c in cities]}")
```

Output:

```text
unscaled: nearest to (58, 50500) is (25, 50000) -> predicts 'no'
means: age 40.0, income 67333.3; std devs: age 14.21, income 16162.4
standardised: query becomes (1.266, -1.042); nearest is (61, 52000) -> predicts 'yes'
income min-max scaled: [0.0, 0.711, 0.244, 1.0, 0.044, 0.311]
one-hot columns: ['Chennai', 'Hyderabad', 'Pune']
  Hyderabad -> [0, 1, 0]
  Pune      -> [0, 0, 1]
  Chennai   -> [1, 0, 0]
```

Without scaling, income differences of thousands of rupees swamp age differences of tens of years. The nearest neighbour is a 25-year-old whose income is only ₹500 away; the 61-year-old's income is ₹1,500 away, and the age gaps (33 years against 3) barely register, giving distances of about 501 against 1,500. After standardisation, both features are measured in standard deviations, and the nearest neighbour is the 61-year-old with a similar income, a far more sensible match that changes the prediction from "no" to "yes". The min-max scaled incomes lie between 0 and 1, and the one-hot vectors place each city in its own column with no implied order.

### Example 2: Scaling and encoding by hand

Exam marks 40, 50, 60, 70, 80 have mean 60 and (population) standard deviation $\sqrt{(400 + 100 + 0 + 100 + 400)/5} = \sqrt{200} \approx 14.14$.

- **Standardised:** $-1.41, -0.71, 0, 0.71, 1.41$.
- **Min-max:** $0, 0.25, 0.5, 0.75, 1$.

Now add an outlier, 200. Min-max scaling divides by a range of 160, giving $0, 0.0625, 0.125, 0.1875, 0.25, 1$: the original five values are squashed into a quarter of the range. Robust scaling with the median (65) and interquartile range is far less affected.

For a T-shirt size feature (small, medium, large), ordinal encoding 0, 1, 2 is appropriate because the order is real. For a payment-method feature (UPI, card, cash), use one-hot columns; in an unregularised linear regression, keep two of them, so that "cash" becomes the reference category absorbed by the intercept.

## Applications

- **Recommendation and search:** distance and similarity computations on scaled features.
- **Neural networks:** standardised inputs make training stable and fast.
- **Credit scoring:** one-hot and ordinal encodings for categorical applicant data.
- **Click-through prediction:** hashing and embeddings for millions of categorical IDs.
- **Clustering:** customer segmentation with k-means requires comparable feature scales.

## Common mistakes

- **Scaling before splitting.** Fit scalers on the training data only.
- **Integer-encoding nominal categories for linear or distance-based models.** It invents an order.
- **Keeping all one-hot columns in unregularised linear regression.** It creates perfect collinearity.
- **Scaling the target accidentally or inconsistently.** If the target is transformed, invert the transformation for predictions.
- **Target encoding with in-sample means.** Use out-of-fold estimates to avoid leakage.
- **Scaling for tree models and expecting gains.** Trees are insensitive to monotonic scaling.

## Revision notes

- Scale for distance-based, gradient-based, regularised models, and PCA; trees do not need it.
- Min-max to $[0, 1]$ (outlier-sensitive); standardise to mean 0, SD 1; robust scaling with median and IQR; log for skew.
- Fit transformation parameters on training data only.
- Ordinal encoding for ordered categories; one-hot for nominal ones.
- Dummy-variable trap: drop one column when using an intercept without regularisation.
- High cardinality: grouping, frequency, out-of-fold target encoding, hashing, embeddings.

## Practice questions

:::question basic
Which of these models need feature scaling: k-NN, random forest, logistic regression trained by gradient descent, k-means?
:::answer
k-NN, logistic regression trained by gradient descent, and k-means benefit from scaling. A random forest does not need it, because its splits compare one feature with a threshold and are unaffected by rescaling.
:::

:::question basic
A feature has mean 70 and standard deviation 10. What is the standardised value of 85?
:::answer
$z = (85 - 70) / 10 = 1.5$: the value is one and a half standard deviations above the mean.
:::

:::question intermediate
Why should a scaler be fitted on the training set only, and what happens to test values outside the training range?
:::answer
Fitting on the full data uses test statistics during training, a form of leakage that makes evaluation optimistic and does not match production, where future data is unknown. Test values outside the training range are transformed with the training parameters; with min-max scaling they simply fall below 0 or above 1, which is acceptable and realistic.
:::

:::question intermediate
A linear regression with an intercept includes one-hot columns for three cities. Explain the dummy-variable trap and how to avoid it.
:::answer
For every row, the three one-hot columns sum to exactly 1, which equals the intercept column, so the columns are perfectly collinear and the coefficients are not uniquely determined. Drop one city's column; that city becomes the reference category, and each remaining coefficient measures the difference from it. Regularised models can usually keep all columns.
:::

:::question advanced
A dataset has a "pincode" feature with 19,000 distinct values. Compare ways to use it in a model.
:::answer
One-hot encoding would add 19,000 sparse columns, risking overfitting on rare codes and making linear models slow. Options: group pincodes into regions or districts (adds domain knowledge); frequency encoding; target encoding with out-of-fold means and smoothing towards the global mean (powerful but must avoid leakage); the hashing trick into a few thousand columns (fixed size, tolerates unseen codes, small collisions); or learned embeddings in a neural network. Rare and unseen codes need a fallback such as an "other" category.
:::

## Further learning

- **Next:** *Linear Regression & Gradient Descent* shows why scaling speeds up gradient descent.
- **Related:** *Descriptive Statistics: Center, Spread & Shape* in Statistics reviews means, standard deviations, and quartiles.
