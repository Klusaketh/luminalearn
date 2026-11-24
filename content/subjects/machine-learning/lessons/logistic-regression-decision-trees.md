---
lesson: logistic-regression-decision-trees
title: Logistic Regression & Decision Trees
summary: Two core classifiers: logistic regression with the sigmoid, log-odds, cross-entropy loss, and decision boundaries; and decision trees built by recursive splitting with entropy, information gain, gain ratio, and Gini impurity, plus overfitting control by pruning.
minutes: 55
type: theory
objectives:
  - Train and interpret logistic regression, including probabilities, log-odds, odds ratios, and the decision boundary
  - Compute entropy, information gain, gain ratio, and Gini impurity to choose decision-tree splits
  - Explain how trees overfit and how depth limits, minimum leaf sizes, and pruning control them
review: ai-draft
---
## Introduction

Will a student pass? Is an email spam? Should a loan be approved? Classification predicts categories, and two classic methods approach it very differently. **Logistic regression** draws a smooth boundary and outputs calibrated probabilities, with coefficients that are easy to interpret. **Decision trees** ask a sequence of yes/no questions, producing rules that anyone can read. Both remain widely used on their own, and trees are the building blocks of random forests and gradient boosting.

**Before you start:** you should know *Linear Regression & Gradient Descent* and logarithms.

## Core theory

### Logistic regression

Logistic regression passes a linear score through the **sigmoid** function:

$$z = \mathbf{w}^\top\mathbf{x} + b, \qquad p = \sigma(z) = \frac{1}{1 + e^{-z}}$$

so $p$ lies between 0 and 1 and is read as $P(y = 1 \mid \mathbf{x})$. Rearranging gives the **log-odds** form $\ln\frac{p}{1 - p} = z$: the model is linear in log-odds. Increasing a feature by one unit multiplies the odds by $e^{w}$, its **odds ratio**.

The **decision boundary** is where $p = 0.5$, that is $z = 0$, a straight line (or hyperplane) in feature space. The threshold can be moved away from 0.5 when false positives and false negatives have different costs.

Training minimises the **binary cross-entropy** (log-loss):

$$J = -\frac{1}{n}\sum_{i}\left[y_i\ln p_i + (1 - y_i)\ln(1 - p_i)\right]$$

This is the negative log-likelihood of the data under a Bernoulli model. It is convex, punishes confident wrong predictions heavily, and has the simple gradient $\frac{1}{n}\sum (p_i - y_i)\mathbf{x}_i$, the same form as linear regression's. For several classes, **softmax regression** generalises the sigmoid.

### Decision trees

A decision tree splits the data recursively: each internal node tests one feature (such as "hours ≥ 4" or "weather = rainy"), and each leaf predicts a class (the majority) or a value (the mean, for regression trees). Splits are chosen greedily to make the child nodes as **pure** as possible.

- **Entropy:** $H = -\sum_k p_k\log_2 p_k$ is 0 for a pure node and 1 for a 50/50 binary node.
- **Information gain:** $IG = H(\text{parent}) - \sum_j \frac{n_j}{n}H(\text{child}_j)$, the reduction in entropy (used by ID3).
- **Gain ratio:** $IG$ divided by the **split information** (the entropy of the split proportions). Information gain favours attributes with many values; gain ratio (used by C4.5) corrects this bias.
- **Gini impurity:** $G = 1 - \sum_k p_k^2$, cheaper to compute and used by CART, which makes binary splits.

Growing stops when nodes are pure or when limits are hit: maximum depth, minimum samples per leaf or per split, or minimum impurity decrease. **Pruning** grows a large tree and then removes branches that do not improve validation performance (cost-complexity pruning).

Trees are interpretable, handle numerical and categorical features, need no scaling, and capture interactions. But a deep tree can memorise its training data, giving **high variance**: small data changes produce very different trees. Ensembles fix this.

## Worked examples

### Example 1: A logistic regression and a split choice

The first part fits logistic regression to hours studied and pass/fail outcomes. The second part evaluates candidate splits for a small tree that predicts whether a student studies late at night.

```python
import math

hours = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
passed = [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1]

w = b = 0.0
for _ in range(5000):                    # gradient descent on the log-loss
    gw = gb = 0.0
    for x, y in zip(hours, passed):
        p = 1 / (1 + math.exp(-(w * x + b)))
        gw += (p - y) * x / len(hours)
        gb += (p - y) / len(hours)
    w, b = w - 0.5 * gw, b - 0.5 * gb

loss = -sum(y * math.log(1 / (1 + math.exp(-(w * x + b)))) + (1 - y) * math.log(1 - 1 / (1 + math.exp(-(w * x + b))))
            for x, y in zip(hours, passed)) / len(hours)
print(f"logistic regression: w = {w:.3f}, b = {b:.3f}, decision boundary at {-b / w:.2f} hours, log-loss {loss:.3f}")
for x in (2, 3.5, 5):
    print(f"  P(pass | {x} hours) = {1 / (1 + math.exp(-(w * x + b))):.3f}")

# Decision-tree split selection: does a student study late tonight?
rows = [  # exam_near, weather, tired -> studies_late
    ("yes", "sunny", "no", "yes"), ("yes", "rainy", "no", "yes"), ("yes", "cloudy", "yes", "yes"),
    ("yes", "sunny", "yes", "no"), ("yes", "rainy", "yes", "yes"), ("no", "sunny", "no", "no"),
    ("no", "rainy", "no", "yes"), ("no", "cloudy", "yes", "no"), ("no", "sunny", "yes", "no"),
    ("no", "cloudy", "no", "no"),
]


def entropy(labels):
    return -sum(labels.count(v) / len(labels) * math.log2(labels.count(v) / len(labels)) for v in set(labels))


def gini(labels):
    return 1 - sum((labels.count(v) / len(labels)) ** 2 for v in set(labels))


labels = [r[-1] for r in rows]
print(f"root: entropy {entropy(labels):.3f}, gini {gini(labels):.3f}")
for col, name in enumerate(["exam_near", "weather", "tired"]):
    groups = {}
    for r in rows:
        groups.setdefault(r[col], []).append(r[-1])
    weighted_h = sum(len(g) / len(rows) * entropy(g) for g in groups.values())
    weighted_g = sum(len(g) / len(rows) * gini(g) for g in groups.values())
    split_info = entropy([r[col] for r in rows])
    gain = entropy(labels) - weighted_h
    print(f"  {name:9}: info gain {gain:.3f}, gain ratio {gain / split_info:.3f}, gini decrease {gini(labels) - weighted_g:.3f}")
```

Output:

```text
logistic regression: w = 1.424, b = -4.630, decision boundary at 3.25 hours, log-loss 0.365
  P(pass | 2 hours) = 0.144
  P(pass | 3.5 hours) = 0.588
  P(pass | 5 hours) = 0.924
root: entropy 1.000, gini 0.500
  exam_near: info gain 0.278, gain ratio 0.278, gini decrease 0.180
  weather  : info gain 0.400, gain ratio 0.255, gini decrease 0.217
  tired    : info gain 0.029, gain ratio 0.029, gini decrease 0.020
```

The model's decision boundary is at 3.25 hours: below it, failing is more likely. Each extra hour multiplies the odds of passing by $e^{1.424} \approx 4.2$. The probabilities rise smoothly (0.144 at 2 hours, 0.588 at 3.5, 0.924 at 5), which is more informative than a hard yes or no.

For the tree, the root is a 5/5 mix, so its entropy is 1 and its Gini impurity 0.5. Weather has the highest information gain (0.400), largely because it splits into three groups, one of them pure (all three rainy days led to studying late). Gain ratio corrects for the three-way split: exam_near wins on gain ratio (0.278 against 0.255). Tiredness barely helps (gain 0.029). Different criteria can choose different splits, which is why C4.5 uses gain ratio.

### Example 2: The numbers by hand

**Entropy for exam_near = yes** (4 "yes", 1 "no"):

$$H = -0.8\log_2 0.8 - 0.2\log_2 0.2 = 0.8(0.322) + 0.2(2.322) = 0.722$$

The exam_near = no branch (1 "yes", 4 "no") also has entropy 0.722, so the weighted child entropy is 0.722 and the information gain is $1 - 0.722 = 0.278$. The split information of a 5/5 split is 1, so the gain ratio is also 0.278. Gini for each branch is $1 - 0.8^2 - 0.2^2 = 0.32$, a decrease of $0.5 - 0.32 = 0.18$ from the root.

**A logistic prediction:** for 4 hours, $z = 1.424 \times 4 - 4.630 = 1.066$, so $p = 1/(1 + e^{-1.066}) = 1/(1 + 0.344) \approx 0.744$.

## Applications

- **Credit and risk scoring:** logistic regression's coefficients are easy to explain to regulators.
- **Medicine:** risk scores and clinical decision rules.
- **Marketing:** predicting customer churn or response to a campaign.
- **Operations:** decision trees encode readable rules for triage and routing.
- **Ensembles:** trees are the base learners of random forests and gradient boosting.

## Common mistakes

- **Using MSE to train logistic regression.** Cross-entropy is convex for this model and gives better gradients.
- **Reading coefficients without scaling in mind.** Compare coefficients only when features share a scale.
- **Always using a 0.5 threshold.** Choose the threshold from the costs of errors.
- **Growing trees without limits.** Unlimited depth memorises noise.
- **Trusting raw information gain for many-valued attributes.** Use gain ratio or binary splits.

## Revision notes

- Logistic regression: $p = \sigma(\mathbf{w}^\top\mathbf{x} + b)$; log-odds linear; odds ratio $e^{w}$.
- Boundary at $z = 0$; loss is binary cross-entropy with gradient $(p - y)\mathbf{x}$.
- Entropy $-\sum p\log_2 p$; information gain = parent entropy − weighted child entropy.
- Gain ratio = IG / split information; Gini $= 1 - \sum p^2$.
- Trees: interpretable, no scaling, but high variance; control with depth, leaf size, pruning.

## Practice questions

:::question basic
Compute $\sigma(0)$ and $\sigma(2)$.
:::answer
$\sigma(0) = 1/(1 + 1) = 0.5$. $\sigma(2) = 1/(1 + e^{-2}) = 1/(1 + 0.135) \approx 0.881$.
:::

:::question basic
What is the entropy of a node with 8 positive and 0 negative examples, and of a node with 4 of each?
:::answer
A pure node (8 and 0) has entropy 0. A balanced node (4 and 4) has entropy $-0.5\log_2 0.5 - 0.5\log_2 0.5 = 1$, the maximum for two classes.
:::

:::question intermediate
Compute the Gini impurity of a node with 3 positive and 1 negative example.
:::answer
$G = 1 - (0.75^2 + 0.25^2) = 1 - (0.5625 + 0.0625) = 0.375$.
:::

:::question intermediate
Why is logistic regression trained with cross-entropy instead of mean squared error?
:::answer
Cross-entropy is the negative log-likelihood of a Bernoulli model, so minimising it gives maximum-likelihood estimates and well-calibrated probabilities. With the sigmoid it is convex, so gradient descent finds the global minimum, and its gradient $(p - y)\mathbf{x}$ stays large when the model is confidently wrong. MSE with a sigmoid is non-convex and its gradients vanish for confident mistakes, slowing learning.
:::

:::question advanced
Explain why fully grown decision trees overfit and list three ways to prevent it.
:::answer
A tree can keep splitting until every leaf is pure, eventually isolating individual training examples, including noisy ones; it then fits accidents of the sample, and small changes in data produce very different trees (high variance). Prevention: limit maximum depth or require a minimum number of samples per leaf or split; prune the full tree using validation data (cost-complexity pruning); or average many trees in an ensemble such as a random forest.
:::

## Further learning

- **Next:** *k-NN, Naive Bayes & Support Vector Machines* introduces three more classifiers.
- **Related:** *Ensemble Methods: Bagging, Random Forests & Boosting* combines trees into stronger models.
