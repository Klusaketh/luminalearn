---
lesson: linear-regression-gradient-descent
title: Linear Regression & Gradient Descent
summary: Linear regression as a model and a least-squares problem, the closed-form normal equation, gradient descent and the role of the learning rate, batch versus stochastic and mini-batch updates, and evaluating fits with MSE, RMSE, MAE, and R-squared.
minutes: 45
type: theory
objectives:
  - Fit a linear regression with the closed-form least-squares solution and interpret its coefficients
  - Derive and apply gradient-descent updates, and explain how the learning rate and feature scaling affect convergence
  - Evaluate regression models with MSE, RMSE, MAE, and R-squared, and recognise the assumptions behind them
review: ai-draft
---
## Introduction

How many marks will a student score after studying for nine hours? How much will a flat cost given its area? **Linear regression** answers such questions by fitting a straight line (or a flat plane in many dimensions) through data. It is the simplest learning algorithm, yet it introduces almost every idea in machine learning: a model with parameters, a loss function, an optimisation algorithm, and evaluation metrics. Gradient descent, introduced here, is the same procedure that trains deep neural networks with billions of parameters.

**Before you start:** you should know derivatives and the idea of a minimum; *Derivatives & The Chain Rule* covers what is needed.

## Core theory

### The model and the loss

With one feature, the model predicts $\hat{y} = wx + b$, with **weight** (slope) $w$ and **bias** (intercept) $b$. With $d$ features, $\hat{y} = \mathbf{w}^\top \mathbf{x} + b$, or $\hat{\mathbf{y}} = X\mathbf{w}$ for all examples at once when $X$ includes a column of ones. Training chooses parameters that minimise the **mean squared error**:

$$J(\mathbf{w}) = \frac{1}{n}\sum_{i=1}^{n}(\hat{y}_i - y_i)^2$$

This loss is convex: it has a single minimum and no misleading local minima.

### The closed-form solution

Setting the gradient to zero gives the **normal equation** $\mathbf{w} = (X^\top X)^{-1}X^\top \mathbf{y}$. For one feature, it reduces to

$$w = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}, \qquad b = \bar{y} - w\bar{x}$$

Solving it costs about $O(d^3)$ for $d$ features, fine for small $d$ but too slow for very many features. If features are perfectly collinear, $X^\top X$ is singular; the pseudo-inverse or ridge regularisation fixes this.

### Gradient descent

Gradient descent starts from initial parameters and repeatedly steps downhill:

$$\frac{\partial J}{\partial w} = \frac{2}{n}\sum (\hat{y}_i - y_i)x_i, \qquad \frac{\partial J}{\partial b} = \frac{2}{n}\sum (\hat{y}_i - y_i)$$

$$w \leftarrow w - \eta\frac{\partial J}{\partial w}, \qquad b \leftarrow b - \eta\frac{\partial J}{\partial b}$$

The **learning rate** $\eta$ controls the step size. Too small, and training crawls; too large, and each step overshoots the minimum by more than the last, so the loss explodes. For this quadratic loss, the steps are stable only when $\eta$ is less than $2/\lambda_{\max}$, where $\lambda_{\max}$ is the largest eigenvalue of the loss's Hessian, so features with large values force small learning rates. **Feature scaling** makes the loss surface rounder, allowing larger steps and faster convergence.

- **Batch gradient descent** uses all examples per step.
- **Stochastic gradient descent (SGD)** uses one example per step: noisy but cheap, and the noise can help escape poor regions in non-convex problems.
- **Mini-batch** gradient descent uses small batches (such as 32 to 512 examples) and is the standard in deep learning.

### Evaluating a regression

- **MSE** and its square root **RMSE** (in the units of $y$) penalise large errors heavily.
- **MAE**, the mean absolute error, is more robust to outliers.
- **$R^2 = 1 - \frac{SS_{\text{res}}}{SS_{\text{tot}}}$** is the fraction of the variance in $y$ explained by the model: 1 is perfect, 0 is no better than predicting the mean.

Linear regression assumes a roughly linear relationship and independent errors; for statistical inference (confidence intervals for coefficients) it also assumes constant error variance and roughly normal residuals. Outliers can pull the line strongly. Curved relationships can still be modelled linearly by adding **polynomial features** such as $x^2$, because the model stays linear in its parameters.

## Worked examples

### Example 1: Closed form versus gradient descent

Eight students' study hours and exam scores. The program computes the exact least-squares line, then runs gradient descent with a good and a too-large learning rate.

```python
xs = [1, 2, 3, 4, 5, 6, 7, 8]            # hours studied
ys = [52, 55, 61, 64, 70, 71, 77, 80]    # exam score
n = len(xs)

mx, my = sum(xs) / n, sum(ys) / n
w_exact = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
b_exact = my - w_exact * mx
print(f"closed form: score = {w_exact:.4f} * hours + {b_exact:.4f}")


def mse(w, b):
    return sum((w * x + b - y) ** 2 for x, y in zip(xs, ys)) / n


ss_tot = sum((y - my) ** 2 for y in ys)
print(f"MSE = {mse(w_exact, b_exact):.4f}, R^2 = {1 - mse(w_exact, b_exact) * n / ss_tot:.4f}")


def gradient_descent(lr, epochs, report):
    w = b = 0.0
    for epoch in range(1, epochs + 1):
        dw = sum(2 * (w * x + b - y) * x for x, y in zip(xs, ys)) / n
        db = sum(2 * (w * x + b - y) for x, y in zip(xs, ys)) / n
        w, b = w - lr * dw, b - lr * db
        if epoch in report:
            print(f"  lr {lr}, epoch {epoch:5}: w = {w:10.4f}, b = {b:10.4f}, MSE = {mse(w, b):12.4f}")


gradient_descent(0.02, 10000, {1, 10, 100, 1000, 10000})
print("too large a learning rate:")
gradient_descent(0.04, 50, {1, 10, 50})
print(f"prediction for 9 hours: {w_exact * 9 + b_exact:.1f}")
```

Output:

```text
closed form: score = 4.0714 * hours + 47.9286
MSE = 0.9107, R^2 = 0.9896
  lr 0.02, epoch     1: w =    12.7800, b =     2.6500, MSE =     436.1547
  lr 0.02, epoch    10: w =    11.5829, b =     5.6967, MSE =     368.1963
  lr 0.02, epoch   100: w =     7.7222, b =    27.4030, MSE =      87.6693
  lr 0.02, epoch  1000: w =     4.0741, b =    47.9135, MSE =       0.9108
  lr 0.02, epoch 10000: w =     4.0714, b =    47.9286, MSE =       0.9107
too large a learning rate:
  lr 0.04, epoch     1: w =    25.5600, b =     5.3000, MSE =    5348.7088
  lr 0.04, epoch    10: w =   -21.8493, b =     3.1328, MSE =   29590.8668
  lr 0.04, epoch    50: w = -1713.2387, b =  -278.6236, MSE = 80357184.0022
prediction for 9 hours: 84.6
```

The fitted line is score ≈ 4.07 × hours + 47.93: each extra hour of study adds about 4 marks, and $R^2 = 0.99$ means the line explains 99% of the variation in scores. Gradient descent with $\eta = 0.02$ reaches the same answer: close after 1,000 epochs and exact to four decimals after 10,000. Its path is instructive: the slope first jumps to 12.8 and then falls while the intercept rises slowly, because with uncentred $x$ the two parameters are coupled and the intercept direction is very flat. Doubling the learning rate to 0.04 crosses the stability limit and the MSE explodes to 80 million within 50 epochs. The model predicts 84.6 marks for 9 hours, an extrapolation just beyond the data, which should be treated with caution.

### Example 2: A fit and a gradient step by hand

Data: $x = (1, 2, 3)$, $y = (2, 4, 5)$. Then $\bar{x} = 2$, $\bar{y} = 11/3 \approx 3.667$.

$$w = \frac{(-1)(-1.667) + (0)(0.333) + (1)(1.333)}{1 + 0 + 1} = \frac{3}{2} = 1.5, \qquad b = 3.667 - 1.5 \times 2 = 0.667$$

Predictions 2.167, 3.667, 5.167 leave residuals $-0.167, 0.333, -0.167$, so $SS_{\text{res}} = 0.167$; $SS_{\text{tot}} = 2.778 + 0.111 + 1.778 = 4.667$, and $R^2 = 1 - 0.167/4.667 \approx 0.964$.

One gradient step from $w = b = 0$ with $\eta = 0.1$: all predictions are 0, so

$$\frac{\partial J}{\partial w} = \frac{2}{3}\left(-(2 \cdot 1 + 4 \cdot 2 + 5 \cdot 3)\right) = -16.67, \qquad \frac{\partial J}{\partial b} = \frac{2}{3}(-11) = -7.33$$

giving $w = 1.667$ and $b = 0.733$ after one step, already heading towards the solution.

## Applications

- **Forecasting:** sales, demand, and energy use from historical drivers.
- **Economics and social science:** estimating the effect of variables while controlling for others.
- **Real estate:** price models based on area, location, and age.
- **Engineering:** calibration curves and sensor models.
- **Deep learning:** gradient descent is the training engine for neural networks.

## Common mistakes

- **Setting the learning rate by guesswork without watching the loss.** Plot it; if it rises, reduce $\eta$.
- **Forgetting feature scaling with gradient descent.** Unscaled features make convergence slow or unstable.
- **Interpreting coefficients causally.** Regression shows association; correlated features and confounders can mislead.
- **Extrapolating far beyond the data.** Linear trends rarely continue indefinitely.
- **Judging fit by $R^2$ alone.** Check residual plots for curvature and outliers.

## Revision notes

- Model $\hat{y} = \mathbf{w}^\top\mathbf{x} + b$; loss MSE (convex).
- Closed form: $\mathbf{w} = (X^\top X)^{-1}X^\top\mathbf{y}$; one feature: $w = S_{xy}/S_{xx}$, $b = \bar{y} - w\bar{x}$.
- Gradient: $\frac{2}{n}\sum(\hat{y} - y)x$; update $w \leftarrow w - \eta\,\partial J/\partial w$.
- Learning rate too large diverges; scaling helps convergence.
- Batch, stochastic, and mini-batch gradient descent.
- Metrics: MSE, RMSE, MAE, $R^2 = 1 - SS_{\text{res}}/SS_{\text{tot}}$.

## Practice questions

:::question basic
A model predicts score = 4.07 × hours + 47.93. Interpret both numbers.
:::answer
The slope 4.07 means each additional hour of study is associated with about 4.07 more marks. The intercept 47.93 is the predicted score for zero hours of study, which is meaningful only if zero hours is within the range of the data.
:::

:::question basic
What does $R^2 = 0.99$ tell you, and what does $R^2 = 0$ mean?
:::answer
$R^2 = 0.99$ means the model explains 99% of the variance of the target around its mean. $R^2 = 0$ means the model does no better than always predicting the mean of $y$; negative values mean it does worse.
:::

:::question intermediate
With $w = 1$, $b = 0$, data $x = (1, 2)$, $y = (3, 5)$, and $\eta = 0.1$, compute one gradient-descent step.
:::answer
Predictions are 1 and 2, errors $-2$ and $-3$. $\partial J/\partial w = \frac{2}{2}((-2)(1) + (-3)(2)) = -8$ and $\partial J/\partial b = \frac{2}{2}(-2 - 3) = -5$. New values: $w = 1 - 0.1(-8) = 1.8$ and $b = 0 - 0.1(-5) = 0.5$.
:::

:::question intermediate
Why does feature scaling speed up gradient descent?
:::answer
With features on very different scales, the loss surface is a long, narrow valley: steep along large-valued features and flat along small ones. The learning rate must be small enough for the steep direction, so progress along the flat direction is very slow. Scaling makes the contours rounder, so one learning rate suits all directions and convergence takes far fewer steps.
:::

:::question advanced
When would you prefer gradient descent over the normal equation, and what do you do if $X^\top X$ is singular?
:::answer
The normal equation needs about $O(d^3)$ work to solve a $d \times d$ system and all the data in memory, so gradient descent (especially mini-batch) is preferred with very many features, huge or streaming datasets, or models without closed forms. The normal equation is convenient when $d$ is small. If $X^\top X$ is singular, because features are collinear or there are more features than examples, use the pseudo-inverse (minimum-norm solution), remove redundant features, or add ridge regularisation, which makes $X^\top X + \lambda I$ invertible.
:::

## Further learning

- **Next:** *Logistic Regression & Decision Trees* adapts these ideas to classification.
- **Related:** *Orthogonality, Projections & Least Squares* in Linear Algebra explains least squares geometrically.
