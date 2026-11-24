---
lesson: cross-validation-model-selection
title: Cross-Validation & Model Selection
summary: Estimating generalisation reliably: hold-out validation, k-fold and stratified cross-validation, leave-one-out, grouped and time-series splits, hyperparameter search (grid, random, Bayesian), leakage inside cross-validation, nested cross-validation, and the one-standard-error rule.
minutes: 45
type: theory
objectives:
  - Perform k-fold cross-validation, report the mean and spread of scores, and use it to tune hyperparameters
  - Choose the right splitting scheme (stratified, grouped, time-series) and keep preprocessing inside the folds
  - Explain nested cross-validation, search strategies, and how to select a final model without touching the test set
review: ai-draft
---
## Introduction

How good will a model be on data it has never seen? Training accuracy is no guide, because a flexible model can memorise. A single train/validation split helps, but its verdict depends on which examples happened to land where, and it wastes data on small datasets. **Cross-validation** uses every example for both training and validation, gives an estimate with an error bar, and is the standard way to compare models and tune hyperparameters honestly.

**Before you start:** you should know *The End-to-End ML Pipeline* and the k-NN classifier from *k-NN, Naive Bayes & Support Vector Machines*.

## Core theory

### Hold-out validation

Split the training data once into a fitting part and a validation part. It is simple and fast, but the estimate has high variance (it depends on one random split) and the model is trained on less data.

### k-fold cross-validation

1. Split the training data into $k$ equal **folds**.
2. For each fold $i$: train on the other $k - 1$ folds and evaluate on fold $i$.
3. Report the **mean** of the $k$ scores and their **standard deviation**.

Common choices are $k = 5$ or $10$. Every example is used for validation exactly once. Variants:

- **Stratified k-fold** keeps the class proportions the same in every fold, important for imbalanced classification.
- **Leave-one-out** ($k = n$) trains $n$ models; its estimate is nearly unbiased but has high variance and is expensive.
- **Repeated k-fold** reruns with different shuffles and averages, reducing variance.
- **Group k-fold** keeps all examples from the same group (patient, user, device) in one fold, preventing leakage across related examples.
- **Time-series splits** always train on the past and validate on the future (expanding or sliding windows), never shuffling.

### Hyperparameter search

Hyperparameters (such as $k$ in k-NN, tree depth, or regularisation strength) are chosen by comparing cross-validated scores:

- **Grid search** tries every combination from a grid: thorough but exponential in the number of hyperparameters.
- **Random search** samples combinations at random; when only a few hyperparameters matter, it finds good values with far fewer trials.
- **Bayesian optimisation** models the score as a function of the hyperparameters to choose promising trials; **early stopping** prunes poor runs.

### Leakage inside cross-validation

Any step that learns from data (scaling, imputation, feature selection, oversampling) must be fitted **inside each training fold** and applied to that fold's validation part. Doing it once on all the data before cross-validation leaks validation information and inflates scores. Pipeline objects make this automatic.

### Nested cross-validation and the final model

The best cross-validated score after tuning is optimistically biased, because we picked the maximum of several noisy estimates. **Nested cross-validation** fixes this: an inner loop tunes hyperparameters, and an outer loop evaluates the whole tuning procedure on folds it never touched. In practice, after choosing hyperparameters, retrain on **all** the training data and evaluate once on the held-out test set.

When scores are close, the **one-standard-error rule** picks the simplest model whose score is within one standard error of the best, favouring robustness over noise-chasing.

## Worked examples

### Example 1: Choosing k for k-NN with 5-fold cross-validation

The program builds 120 points in two overlapping classes, holds out 30 for testing, and runs 5-fold cross-validation on the remaining 90 for several values of $k$.

```python
import math
import random

random.seed(3)


def blob(cx, cy, label):
    # sum of three uniforms: a bell-shaped spread without calling math functions
    jitter = lambda: random.random() + random.random() + random.random() - 1.5  # noqa: E731
    return (cx + jitter(), cy + jitter()), label


data = [blob(0, 0, 0) for _ in range(60)] + [blob(1.2, 1.2, 1) for _ in range(60)]
random.shuffle(data)
train, test = data[:90], data[90:]


def knn_predict(rows, x, k):
    nearest = sorted(rows, key=lambda r: math.dist(r[0], x))[:k]
    return 1 if sum(label for _, label in nearest) * 2 > k else 0


def accuracy(train_rows, eval_rows, k):
    return sum(knn_predict(train_rows, x, k) == y for x, y in eval_rows) / len(eval_rows)


folds = [train[i::5] for i in range(5)]                 # 5 folds of 18 examples
results = {}
for k in (1, 3, 5, 9, 15, 31):
    scores = []
    for i in range(5):
        fit_rows = [r for j, f in enumerate(folds) if j != i for r in f]
        scores.append(accuracy(fit_rows, folds[i], k))
    mean = sum(scores) / 5
    std = math.sqrt(sum((s - mean) ** 2 for s in scores) / 4)
    results[k] = mean
    print(f"k = {k:2}: fold accuracies {[round(s, 2) for s in scores]} mean {mean:.3f} +/- {std:.3f}")

best_k = max(results, key=results.get)
print(f"best k by cross-validation: {best_k}")
print(f"retrain on all 90 training examples, test accuracy with k = {best_k}: {accuracy(train, test, best_k):.3f}")
print(f"(for comparison, k = 1 on the test set: {accuracy(train, test, 1):.3f})")
```

Output:

```text
k =  1: fold accuracies [0.72, 0.89, 0.94, 0.78, 0.94] mean 0.856 +/- 0.101
k =  3: fold accuracies [0.83, 0.94, 0.89, 0.89, 0.89] mean 0.889 +/- 0.039
k =  5: fold accuracies [0.89, 1.0, 0.89, 0.89, 0.94] mean 0.922 +/- 0.050
k =  9: fold accuracies [0.83, 1.0, 0.89, 0.89, 0.94] mean 0.911 +/- 0.063
k = 15: fold accuracies [0.83, 0.94, 0.89, 0.89, 0.89] mean 0.889 +/- 0.039
k = 31: fold accuracies [0.83, 0.94, 1.0, 0.89, 0.94] mean 0.922 +/- 0.063
best k by cross-validation: 5
retrain on all 90 training examples, test accuracy with k = 5: 0.867
(for comparison, k = 1 on the test set: 0.867)
```

$k = 1$ has the lowest mean accuracy (0.856) and the largest spread across folds (±0.101): it is high-variance, as expected. $k = 5$ and $k = 31$ tie for the best mean (0.922), and the program takes the first. On the 30 test points, the chosen model scores 0.867, the same as $k = 1$. That is not a contradiction: each test point is worth 3.3 percentage points, and the cross-validation differences are within about one standard deviation, so neither the test set nor the folds can separate these models reliably. Honest model selection reports this uncertainty instead of over-reading small gaps; the one-standard-error rule would favour the smoothest competitive model.

### Example 2: Summaries and costs by hand

Five folds give accuracies 0.80, 0.85, 0.78, 0.82, 0.85.

- Mean $= 4.10/5 = 0.82$.
- Sample standard deviation $= \sqrt{\frac{0.0004 + 0.0009 + 0.0016 + 0 + 0.0009}{4}} = \sqrt{0.00095} \approx 0.031$.

Report $0.82 \pm 0.03$. The standard error of the mean is about $0.031/\sqrt{5} \approx 0.014$.

Cost of a grid search: 4 learning rates × 5 depths = 20 combinations, each evaluated with 5-fold cross-validation, means $20 \times 5 = 100$ model fits, plus 1 final refit on all training data. Nested cross-validation with 5 outer folds would multiply the tuning cost by 5: 500 fits plus 5 outer refits.

## Applications

- **Hyperparameter tuning:** every serious model-building workflow uses cross-validation.
- **Small datasets:** medical and scientific studies where every example counts.
- **Model comparison:** deciding between algorithms with error bars instead of single numbers.
- **Forecasting:** time-series cross-validation for demand and finance models.
- **Kaggle-style competitions:** robust local validation prevents overfitting to a public leaderboard.

## Common mistakes

- **Tuning on the test set.** Use cross-validation on the training data; test once at the end.
- **Preprocessing before splitting into folds.** Fit every data-dependent step inside the folds.
- **Shuffling time-series data.** Validation must come after training in time.
- **Ignoring groups.** The same patient in training and validation folds inflates scores.
- **Reporting only the best mean.** Include the spread, and remember that the maximum of noisy scores is optimistic.

## Revision notes

- Hold-out: simple but high-variance; k-fold: every example validates once; report mean ± SD.
- Stratified (class balance), group (no group in two folds), time-series (train on past) splits.
- LOOCV: nearly unbiased, high variance, expensive.
- Grid, random, Bayesian search; early stopping.
- Preprocessing inside folds (pipelines) to avoid leakage.
- Nested CV for unbiased estimates when tuning; refit on all training data; one-standard-error rule.

## Practice questions

:::question basic
Why should hyperparameters not be tuned using the test set?
:::answer
Choosing the hyperparameters that maximise test performance fits them to the particular test examples, so the test score becomes optimistically biased and no longer estimates performance on new data. Tune with cross-validation (or a validation set) and use the test set once at the end.
:::

:::question basic
In 10-fold cross-validation on 1,000 examples, how many examples are used for training and validation in each fold, and how many models are trained?
:::answer
Each fold trains on 900 examples and validates on the other 100. Ten models are trained, one per fold (plus usually a final model on all 1,000).
:::

:::question intermediate
Someone standardises all features using the whole dataset and then runs 5-fold cross-validation. Why is this a problem?
:::answer
The means and standard deviations used for scaling include the validation fold of every split, so each validation fold has influenced its own training data. This leakage usually makes scores slightly optimistic, and with stronger data-dependent steps (feature selection, oversampling) the bias can be large. The scaler must be fitted within each training fold, ideally via a pipeline.
:::

:::question intermediate
How should cross-validation be done for a model that forecasts next week's sales?
:::answer
Use time-ordered splits: train on data up to a point and validate on the following period, then move the cut-off forward (an expanding or sliding window) and repeat. Never shuffle, because random folds would let the model learn from future weeks when predicting past ones, which is impossible in deployment.
:::

:::question advanced
Explain nested cross-validation and compute the number of model fits for 5 outer folds, 3 inner folds, and 10 hyperparameter candidates.
:::answer
The outer loop splits the data into 5 folds; for each, the inner loop runs 3-fold cross-validation on the outer training part to choose the best of the 10 candidates, then refits the chosen setting on the whole outer training part and scores it on the outer test fold. The average outer score estimates the performance of the entire tuning procedure without optimistic bias. Fits: $5 \times 10 \times 3 = 150$ inner fits plus 5 outer refits, 155 in total.
:::

## Further learning

- **Next:** *L1/L2 Regularization & Bias-Variance* explains what cross-validation is protecting against.
- **Related:** *The End-to-End ML Pipeline* places cross-validation within the full project.
