---
lesson: regularization-bias-variance
title: L1/L2 Regularization & Bias-Variance
summary: Underfitting and overfitting, the bias-variance decomposition of prediction error, learning curves, and regularisation with ridge (L2), lasso (L1), and elastic net, including closed forms, sparsity, choosing lambda, and other ways to control model complexity.
minutes: 45
type: theory
objectives:
  - Explain underfitting and overfitting with the bias-variance decomposition and diagnose them from training and validation errors
  - Apply ridge and lasso regularisation and explain why L2 shrinks coefficients while L1 sets some to zero
  - Choose the regularisation strength by cross-validation and describe other regularisation techniques
review: ai-draft
---
## Introduction

A model that is too simple misses real patterns; a model that is too flexible memorises noise. Both fail on new data. Managing this tension is the central problem of machine learning. The **bias-variance trade-off** explains it, and **regularisation** is the main tool for controlling it: it lets us use flexible models while penalising unnecessary complexity, so they generalise.

**Before you start:** you should know *Linear Regression & Gradient Descent* and *Cross-Validation & Model Selection*.

## Core theory

### Underfitting and overfitting

- **Underfitting:** the model is too simple; training and validation errors are both high and close together.
- **Overfitting:** the model is too complex for the data; training error is low but validation error is much higher.

Model **capacity** grows with the number of parameters, polynomial degree, tree depth, or network size, and shrinks with more training data and stronger regularisation.

### The bias-variance decomposition

For squared error, with data $y = f(x) + \varepsilon$ where the noise has variance $\sigma^2$, the expected error of a model trained on a random dataset is

$$\mathbb{E}[(y - \hat{f}(x))^2] = \text{Bias}[\hat{f}(x)]^2 + \text{Var}[\hat{f}(x)] + \sigma^2$$

- **Bias** is the error of the average model: systematic error from wrong assumptions (too simple).
- **Variance** is how much the model changes between training sets (too sensitive).
- **Irreducible noise** $\sigma^2$ cannot be removed by any model.

Increasing complexity lowers bias and raises variance; the best model balances them.

### Learning curves

Plot training and validation error against the training set size. **High bias:** both curves plateau at a high error, close together; more data will not help, so add capacity or features. **High variance:** a large gap between the curves that narrows as data grows; more data, regularisation, or a simpler model will help.

### Ridge regression (L2)

Ridge adds the squared size of the weights to the loss:

$$J(\mathbf{w}) = \|\mathbf{y} - X\mathbf{w}\|^2 + \lambda\sum_j w_j^2$$

with closed form $\mathbf{w} = (X^\top X + \lambda I)^{-1}X^\top\mathbf{y}$. It shrinks all coefficients smoothly towards zero but rarely to exactly zero, stabilises solutions when features are correlated (it makes $X^\top X + \lambda I$ invertible), and corresponds to a Gaussian prior on the weights. In neural networks, the same idea is called **weight decay**.

### Lasso (L1) and elastic net

Lasso uses absolute values:

$$J(\mathbf{w}) = \|\mathbf{y} - X\mathbf{w}\|^2 + \lambda\sum_j |w_j|$$

Its penalty has corners at zero, so the optimum often lands exactly on them: lasso produces **sparse** models and performs **feature selection**. It has no closed form in general and is solved by coordinate descent. With correlated features, lasso tends to pick one arbitrarily; **elastic net** mixes L1 and L2 penalties to keep sparsity while sharing weight among correlated features.

Practical rules: **standardise features** first (the penalty should treat them equally), do **not penalise the intercept**, and choose $\lambda$ by **cross-validation**, typically over a logarithmic grid. Larger $\lambda$ means more bias and less variance.

### Other regularisers

Early stopping, dropout and data augmentation (in neural networks), pruning and depth limits (in trees), ensembles, and simply collecting more data all reduce variance.

## Worked examples

### Example 1: Polynomial degree and ridge strength

Ten noisy points come from $y = x^3 - x$. The program fits polynomials of degree 1, 3, and 9, then degree 9 with ridge penalties, and measures error against the true curve at 20 new points.

```python
import random

random.seed(5)
xs = [-1 + 2 * i / 9 for i in range(10)]
true = lambda x: x ** 3 - x  # noqa: E731
ys = [true(x) + 0.3 * (random.random() - 0.5) for x in xs]
test_xs = [-0.95 + 0.1 * i for i in range(20)]


def solve(A, b):
    """Gaussian elimination with partial pivoting."""
    n = len(A)
    M = [row[:] + [v] for row, v in zip(A, b)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            M[r] = [a - f * bb for a, bb in zip(M[r], M[c])]
    w = [0.0] * n
    for r in range(n - 1, -1, -1):
        w[r] = (M[r][n] - sum(M[r][k] * w[k] for k in range(r + 1, n))) / M[r][r]
    return w


def fit(degree, lam):
    X = [[x ** p for p in range(degree + 1)] for x in xs]
    A = [[sum(row[i] * row[j] for row in X) + (lam if i == j and i > 0 else 0)  # no penalty on the intercept
          for j in range(degree + 1)] for i in range(degree + 1)]
    b = [sum(row[i] * y for row, y in zip(X, ys)) for i in range(degree + 1)]
    return solve(A, b)


def predict(w, x):
    return sum(c * x ** p for p, c in enumerate(w))


def report(label, w):
    train = sum((predict(w, x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
    test = sum((predict(w, x) - true(x)) ** 2 for x in test_xs) / len(test_xs)
    size = sum(c * c for c in w[1:]) ** 0.5
    print(f"{label:30} train MSE {train:.4f}  test MSE {test:8.4f}  |w| {size:8.2f}")


for degree in (1, 3, 9):
    report(f"degree {degree}, no penalty", fit(degree, 0))
for lam in (1e-4, 1e-2, 1, 10):
    report(f"degree 9, ridge lambda={lam:g}", fit(9, lam))
```

Output:

```text
degree 1, no penalty           train MSE 0.0574  test MSE   0.0289  |w|     0.30
degree 3, no penalty           train MSE 0.0047  test MSE   0.0045  |w|     1.66
degree 9, no penalty           train MSE 0.0000  test MSE   0.0748  |w|   138.81
degree 9, ridge lambda=0.0001  train MSE 0.0017  test MSE   0.0094  |w|     3.82
degree 9, ridge lambda=0.01    train MSE 0.0031  test MSE   0.0054  |w|     1.75
degree 9, ridge lambda=1       train MSE 0.0319  test MSE   0.0187  |w|     0.43
degree 9, ridge lambda=10      train MSE 0.0745  test MSE   0.0577  |w|     0.09
```

Degree 1 **underfits**: a line cannot follow the cubic, so both errors are high (the test error is measured against the noise-free curve, so it can be lower than the training error, which includes noise). Degree 3 matches the true form and is best overall. Degree 9 **overfits**: it passes through every training point (training error 0.0000) with coefficients of norm 139, and its test error is about 17 times that of degree 3. Ridge tames the degree-9 model: as $\lambda$ grows, the coefficient norm shrinks from 139 to 0.09, and test error falls to 0.0054 at $\lambda = 0.01$ before rising again as the model becomes too constrained (0.0577 at $\lambda = 10$, now underfitting). The U-shape of test error against $\lambda$ is the bias-variance trade-off in action.

### Example 2: Ridge and lasso by hand

**Ridge with one feature and no intercept:** minimising $\sum(y_i - wx_i)^2 + \lambda w^2$ gives $w = \frac{\sum x_iy_i}{\sum x_i^2 + \lambda}$. For $x = (1, 2, 3)$ and $y = (1, 2, 2)$: $\sum xy = 11$ and $\sum x^2 = 14$, so

- $\lambda = 0$: $w = 11/14 \approx 0.786$ (ordinary least squares),
- $\lambda = 1$: $w = 11/15 \approx 0.733$,
- $\lambda = 14$: $w = 11/28 \approx 0.393$.

**Ridge versus lasso with orthonormal features** ($X^\top X = I$): if the least-squares coefficients are $(3, 0.4, -1.2)$ and $\lambda = 1$, ridge divides each by $1 + \lambda$, giving $(1.5, 0.2, -0.6)$; lasso **soft-thresholds** each by $\lambda/2 = 0.5$, giving $(2.5, 0, -0.7)$. Ridge shrinks everything proportionally; lasso subtracts a fixed amount and sets the small coefficient exactly to zero.

## Applications

- **High-dimensional data:** genomics and text models with more features than examples rely on regularisation.
- **Feature selection:** lasso identifies a small set of predictive variables.
- **Neural networks:** weight decay, dropout, and early stopping are standard.
- **Econometrics and forecasting:** ridge stabilises estimates with correlated predictors.
- **Model diagnostics:** learning curves guide whether to collect data or change the model.

## Common mistakes

- **Regularising unscaled features.** The penalty then punishes features unequally because of their units.
- **Penalising the intercept.** It shifts predictions towards zero for no reason.
- **Choosing $\lambda$ on the test set.** Use cross-validation.
- **Expecting regularisation to fix underfitting.** It adds bias; an underfit model needs more capacity.
- **Interpreting lasso's selected features as the only causes.** With correlated features, the choice can be arbitrary.

## Revision notes

- Underfitting: high training and validation error; overfitting: low training, high validation error.
- Expected error = bias² + variance + irreducible noise.
- Learning curves: high bias (curves plateau high, close), high variance (large gap).
- Ridge (L2): $(X^\top X + \lambda I)^{-1}X^\top\mathbf{y}$; shrinks, stabilises, no zeros.
- Lasso (L1): sparse solutions via soft-thresholding; elastic net mixes both.
- Standardise, do not penalise the intercept, tune $\lambda$ by cross-validation.

## Practice questions

:::question basic
A model has 99% training accuracy and 70% validation accuracy. Is it underfitting or overfitting, and what could help?
:::answer
It is overfitting: it performs far better on data it has seen. More training data, stronger regularisation, a simpler model (fewer features, smaller depth), data augmentation, or early stopping could help.
:::

:::question basic
Why does L1 regularisation produce sparse models while L2 does not?
:::answer
The L1 penalty grows at a constant rate however small a weight is, so for weights whose contribution to the fit is small, it pays to set them exactly to zero; geometrically, the L1 constraint region has corners on the axes where solutions tend to land. The L2 penalty's slope vanishes near zero, so it shrinks weights towards zero without making them exactly zero.
:::

:::question intermediate
With one feature and no intercept, $\sum x_iy_i = 20$ and $\sum x_i^2 = 10$. Find the ridge coefficient for $\lambda = 0$, 10, and 30.
:::answer
$w = 20/(10 + \lambda)$: $\lambda = 0$ gives 2.0, $\lambda = 10$ gives 1.0, and $\lambda = 30$ gives 0.5. Larger penalties shrink the coefficient towards zero.
:::

:::question intermediate
Describe the learning curves of a high-bias model and of a high-variance model, and what each suggests.
:::answer
For a high-bias model, training and validation errors converge quickly to a similar, high value; adding data will not help, so increase capacity (more features, a more flexible model, less regularisation). For a high-variance model, training error is low and validation error much higher, with the gap shrinking slowly as data grows; more data, stronger regularisation, or a simpler model will help.
:::

:::question advanced
Explain how bias and variance change as the ridge parameter $\lambda$ increases from 0 to very large values, and why test error is U-shaped.
:::answer
At $\lambda = 0$, the model is unconstrained: low bias but high variance, since coefficients fit noise. As $\lambda$ grows, coefficients shrink, so predictions vary less between training sets (variance falls) but are pulled away from the true function (bias rises). Test error is the sum of bias squared, variance, and the constant noise term: it first falls while the variance reduction dominates, then rises once the added bias dominates. As $\lambda \to \infty$, all coefficients go to zero and the model predicts a constant, a maximal-bias model.
:::

## Further learning

- **Next:** *Reinforcement Learning Fundamentals* introduces learning from rewards.
- **Related:** *Regularization: Dropout, Batch Norm & Weight Decay* in Deep Learning applies these ideas to neural networks.
