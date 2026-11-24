---
lesson: end-to-end-ml-pipeline
title: The End-to-End ML Pipeline
summary: The stages of a machine-learning project from framing the problem to monitoring in production: data collection and cleaning, train/validation/test splits, preprocessing fitted on training data only, baselines, training and evaluation, data leakage, deployment, and drift.
minutes: 35
type: theory
objectives:
  - Describe each stage of an end-to-end ML pipeline and what can go wrong at each one
  - Split data correctly (random, stratified, grouped, or time-based) and fit preprocessing on training data only
  - Recognise target leakage and train-test contamination, and plan deployment monitoring for data and concept drift
review: ai-draft
---
## Introduction

Training a model is a small part of a machine-learning project. Most of the work, and most of the failures, happen around it: choosing what to predict, collecting and cleaning data, splitting it honestly, evaluating fairly, and keeping the model healthy after deployment. A model with 99% test accuracy is worthless if the test was contaminated, if the feature it relies on is unavailable at prediction time, or if the world changes after launch. This lesson walks through the whole pipeline.

**Before you start:** you should know basic Python and the idea of a classifier; probability and statistics help.

## Core theory

### 1. Frame the problem

Decide what will be predicted, for whom, and how the prediction will be used. Is it **classification** (pass or fail), **regression** (exam score), ranking, or clustering? Choose a **success metric** that reflects the real goal (catching fraud may matter more than overall accuracy) and note constraints such as latency, cost, fairness, and privacy. Establish a **baseline**, such as always predicting the most common class, so that model performance has a reference point. Sometimes simple rules beat ML; check first.

### 2. Collect and understand the data

Gather data from logs, databases, sensors, or labelling, and explore it: distributions, missing values, outliers, duplicates, class balance, and label quality. Visualise relationships, and document where the data came from and its known gaps.

### 3. Split before you fit anything

Hold out data the model never sees during development:

- **Training set:** used to fit model parameters.
- **Validation set** (or cross-validation): used to compare models and tune hyperparameters.
- **Test set:** used once, at the end, to estimate performance on new data.

A typical split is 70/15/15. Use **stratified** splits to keep class proportions equal, **group** splits so the same person or device never appears on both sides, and **time-based** splits (train on the past, test on the future) for temporal data.

### 4. Preprocess and engineer features

Handle missing values (imputation), encode categories, scale numbers, and create informative features. Every preprocessing step that learns from data, such as a mean for imputation or the parameters of a scaler, must be **fitted on the training set only** and then applied unchanged to validation, test, and production data. Bundling the steps into a **pipeline** guarantees this.

### 5. Train, tune, and evaluate

Start simple (linear or tree models), compare against the baseline, and tune on validation data. Then evaluate once on the test set, break results down by subgroup, and study the errors.

### Data leakage

**Leakage** makes a model look better in development than it will be in reality:

- **Target leakage:** a feature contains information about the label that would not be available at prediction time, such as "refund issued" when predicting fraud.
- **Train-test contamination:** information from the test data influences training, for example fitting a scaler on the full dataset, selecting features using all labels, or duplicate rows appearing in both splits.

Suspiciously perfect results are the classic warning sign.

### 6. Deploy and monitor

Package the preprocessing and model together, version data, code, and models for reproducibility, and choose batch or real-time serving. After deployment, monitor input distributions and prediction rates. **Data drift** (covariate shift) means the inputs change; **concept drift** means the relationship between inputs and labels changes. Both call for alerts, investigation, and retraining. The practices for running this loop reliably are called **MLOps**.

## Worked examples

### Example 1: A complete mini pipeline, and a leak

The program simulates 200 students (hours studied, attendance, pass or fail), splits them, standardises features using training statistics only, trains logistic regression by gradient descent, compares with a baseline, and finally adds a leaked feature.

```python
import math
import random

random.seed(42)


def make_student():
    hours = random.random() * 10              # hours studied per week
    attendance = 40 + random.random() * 60    # attendance percentage
    p = 1 / (1 + math.exp(-(1.2 * (hours - 5) + 0.08 * (attendance - 75))))
    return [hours, attendance], (1 if random.random() < p else 0)


data = [make_student() for _ in range(200)]

# 1. Split first: the test set stays untouched until the very end
random.shuffle(data)
train, test = data[:150], data[150:]


# 2. Fit preprocessing (standardisation) on the training set only
def fit_scaler(rows):
    cols = list(zip(*[x for x, _ in rows]))
    means = [sum(c) / len(c) for c in cols]
    stds = [math.sqrt(sum((v - m) ** 2 for v in c) / len(c)) for c, m in zip(cols, means)]
    return lambda x: [(v - m) / s for v, m, s in zip(x, means, stds)]


# 3. Train logistic regression with batch gradient descent
def fit(rows, epochs=300, lr=0.5):
    w, b = [0.0] * len(rows[0][0]), 0.0
    for _ in range(epochs):
        gw, gb = [0.0] * len(w), 0.0
        for x, y in rows:
            p = 1 / (1 + math.exp(-(sum(wi * xi for wi, xi in zip(w, x)) + b)))
            gw = [g + (p - y) * xi / len(rows) for g, xi in zip(gw, x)]
            gb += (p - y) / len(rows)
        w, b = [wi - lr * g for wi, g in zip(w, gw)], b - lr * gb
    return w, b


def accuracy(model, rows):
    w, b = model
    return sum((sum(wi * xi for wi, xi in zip(w, x)) + b > 0) == (y == 1) for x, y in rows) / len(rows)


scale = fit_scaler(train)
train_s = [(scale(x), y) for x, y in train]
test_s = [(scale(x), y) for x, y in test]

majority = 1 if sum(y for _, y in train) * 2 >= len(train) else 0
print(f"pass rate in training data: {sum(y for _, y in train) / len(train):.2f}")
print(f"baseline (always predict {majority}): test accuracy {sum(y == majority for _, y in test) / len(test):.2f}")
model = fit(train_s)
print(f"logistic regression: train accuracy {accuracy(model, train_s):.2f}, test accuracy {accuracy(model, test_s):.2f}")
print(f"weights on scaled features: hours {model[0][0]:+.2f}, attendance {model[0][1]:+.2f}")

# 4. A leaky feature: a certificate is issued only AFTER a student passes
leaky_train = [(x + [y], y) for x, y in train]
leaky_test = [(x + [y], y) for x, y in test]
scale2 = fit_scaler(leaky_train)
leaky = fit([(scale2(x), y) for x, y in leaky_train])
print(f"with the leaked 'certificate' feature: test accuracy {accuracy(leaky, [(scale2(x), y) for x, y in leaky_test]):.2f}")
```

Output:

```text
pass rate in training data: 0.50
baseline (always predict 1): test accuracy 0.40
logistic regression: train accuracy 0.89, test accuracy 0.92
weights on scaled features: hours +3.24, attendance +1.26
with the leaked 'certificate' feature: test accuracy 1.00
```

The baseline predicts "pass" for everyone (the training set is exactly half passes) and is right only 40% of the time on this test set. The model reaches 92% test accuracy, close to its 89% training accuracy, so it generalises; with only 50 test students, each one is worth 2 percentage points, so the small gap is noise. On standardised features, the weight for hours (+3.24) is larger than for attendance (+1.26): one standard deviation of study time matters more. The last line shows leakage: a "certificate issued" feature, which only exists after a student passes, gives perfect test accuracy. It looks like a breakthrough, but at prediction time (before results) the feature does not exist, so the real-world accuracy would collapse.

### Example 2: Auditing a feature list for leakage

A hospital wants to predict, at the moment of discharge, whether a patient will be readmitted within 30 days. Proposed features:

| Feature | Available at discharge? | Verdict |
| :--- | :--- | :--- |
| Age, diagnosis codes, number of prior admissions | Yes | Keep |
| Length of the current stay | Yes | Keep |
| "Readmission ward" | Only if readmitted | Target leakage: remove |
| Total days in hospital over the next 30 days | No, it includes the future | Target leakage: remove |
| Average lab value, computed over the whole dataset including test patients | Yes, but computed wrongly | Contamination: compute from training data only |

The split also needs care: a patient admitted several times must have all their visits on one side of the split (a group split), and because hospital practice changes over time, a time-based split (train on earlier years, test on the most recent year) better predicts real performance.

## Applications

- **Recommendation systems:** pipelines retrain daily on fresh interaction logs.
- **Credit scoring:** strict separation of training and evaluation data, with monitoring for drift as economic conditions change.
- **Healthcare:** group- and time-aware splits prevent overly optimistic results.
- **Fraud detection:** concept drift is constant, because fraudsters adapt.
- **Education platforms:** predicting which students need help, with feedback loops to monitor.

## Common mistakes

- **Tuning on the test set.** It then no longer measures performance on unseen data.
- **Fitting preprocessing on all the data.** Scalers, imputers, and feature selectors must learn from training data only.
- **Using features unavailable at prediction time.** Check when each feature becomes known.
- **Random splits for time-series or grouped data.** They let the model peek at the future or at the same person.
- **Skipping the baseline.** Without it, you cannot tell whether the model adds value.
- **Deploying and forgetting.** Models decay as the world changes.

## Revision notes

- Pipeline: frame, collect and explore, split, preprocess, train and tune, evaluate, deploy, monitor.
- Train for parameters, validation for choices, test once at the end.
- Stratified, group, and time-based splits where appropriate.
- Fit preprocessing on training data only; use pipelines.
- Leakage: target leakage and train-test contamination; perfect scores are suspicious.
- Monitor data drift and concept drift; retrain and version everything.

## Practice questions

:::question basic
Why must the test set be kept untouched until the end of a project?
:::answer
Every decision informed by the test set (feature choices, hyperparameters, model selection) slowly fits the model to that particular data. The test score then becomes an optimistic estimate. Kept untouched, it gives an honest estimate of performance on genuinely new data.
:::

:::question basic
Name three stages of the ML pipeline that come after training a model.
:::answer
Evaluation on the held-out test set (including error analysis), deployment (packaging the model with its preprocessing and serving predictions), and monitoring in production (tracking drift and performance, then retraining).
:::

:::question intermediate
A teammate standardises the entire dataset and then splits it into training and test sets. What is wrong, and how should it be fixed?
:::answer
The mean and standard deviation were computed using test rows, so information from the test set leaked into training; the test evaluation is no longer fully independent. Split first, fit the scaler on the training set only, and apply those same parameters to the test set, ideally inside a pipeline.
:::

:::question intermediate
You are predicting whether a customer will cancel their subscription next month. Is "account_closed_date" a valid feature?
:::answer
No. It is only filled in after a customer cancels, so it directly encodes the label and would not be available when making the prediction. It is target leakage and would produce unrealistically high accuracy.
:::

:::question advanced
Three months after deployment, a model's accuracy drops although its code has not changed. Give possible causes and how a team should detect and respond to them.
:::answer
Possible causes are data drift (for example new user demographics or a changed sensor), concept drift (the relationship between features and the label changes, as when fraudsters adapt), upstream pipeline changes (a field renamed, units changed, or values missing), and feedback loops where the model's decisions alter future data. Teams should monitor input feature distributions (for example with population stability or KS statistics), prediction distributions, and data-quality checks, and track accuracy once delayed labels arrive. When alerts fire, they investigate, fix data issues, and retrain on recent data, validating the new model (for example in shadow mode) before replacing the old one.
:::

## Further learning

- **Next:** *Feature Scaling & One-Hot Encoding* details the preprocessing step.
- **Related:** *Cross-Validation & Model Selection* explains how to choose models without touching the test set.
