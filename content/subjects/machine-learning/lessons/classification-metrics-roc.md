---
lesson: classification-metrics-roc
title: Classification Metrics & ROC Curves
summary: Evaluating classifiers beyond accuracy: the confusion matrix, precision, recall, specificity, F1, the accuracy paradox on imbalanced data, threshold trade-offs, ROC curves and AUC, precision-recall curves, multi-class averaging, and calibration.
minutes: 40
type: theory
objectives:
  - Compute accuracy, precision, recall, specificity, and F1 from a confusion matrix and choose the right metric for a task
  - Build an ROC curve by sweeping the threshold and interpret AUC as a ranking probability
  - Explain the accuracy paradox, when to prefer precision-recall curves, and macro versus micro averaging
review: ai-draft
---
## Introduction

A cancer screening model that is "95% accurate" sounds excellent, until you learn that 95% of patients are healthy and the model simply says "healthy" to everyone. Choosing the right metric is as important as choosing the right model: it decides what the model is optimised for and whether it is safe to deploy. This lesson builds the standard toolkit for evaluating classifiers, from the confusion matrix to ROC curves.

**Before you start:** you should know binary classification and probability scores from *Logistic Regression & Decision Trees*.

## Core theory

### The confusion matrix

For a binary classifier with a decision threshold:

| | Predicted positive | Predicted negative |
| :--- | :--- | :--- |
| **Actually positive** | True positive (TP) | False negative (FN) |
| **Actually negative** | False positive (FP) | True negative (TN) |

### Metrics from the matrix

- **Accuracy** $= \frac{TP + TN}{\text{all}}$: the fraction correct.
- **Precision** $= \frac{TP}{TP + FP}$: of those flagged positive, how many really are.
- **Recall** (sensitivity, true positive rate) $= \frac{TP}{TP + FN}$: of the real positives, how many were caught.
- **Specificity** (true negative rate) $= \frac{TN}{TN + FP}$; the **false positive rate** is $1 - $ specificity.
- **F1 score** $= \frac{2 \cdot \text{precision} \cdot \text{recall}}{\text{precision} + \text{recall}}$, the harmonic mean, which is high only when both are high. $F_\beta$ weights recall $\beta$ times as much as precision.
- **Balanced accuracy** averages recall over the classes.

Which matters depends on the costs of errors: **recall** for screening and safety (missing a disease or a fraud is costly), **precision** when false alarms are expensive (flagging a legitimate email as spam).

### Imbalance and the accuracy paradox

When one class is rare, a model that always predicts the majority class achieves high accuracy and is useless. Use precision, recall, F1, balanced accuracy, or precision-recall curves instead, and consider resampling or class weights during training.

### Thresholds and ROC curves

A probabilistic classifier produces scores; the threshold turns them into decisions. Lowering the threshold catches more positives (higher recall) at the cost of more false positives. The **ROC curve** plots the true positive rate against the false positive rate as the threshold sweeps from high to low. The **area under the curve** (AUC) summarises it: 1.0 is perfect ranking and 0.5 is random guessing. AUC equals the probability that a randomly chosen positive gets a higher score than a randomly chosen negative, so it measures **ranking quality**, independent of any threshold.

### Precision-recall curves

With heavy imbalance, the ROC curve can look excellent while precision is poor, because the false positive rate divides by the huge number of negatives. The **precision-recall curve** and its summary, **average precision**, focus on the positive class and are more informative for rare events.

### Multi-class metrics and calibration

For several classes, compute per-class precision and recall, then **macro-average** (each class counts equally) or **micro-average** (each example counts equally, dominated by large classes); the weighted average weights classes by size. Finally, **calibration** asks whether predicted probabilities match observed frequencies: among cases predicted at 0.8, about 80% should be positive. Log-loss and the Brier score reward calibrated probabilities.

## Worked examples

### Example 1: Metrics, an ROC curve, and AUC two ways

Ten predictions with scores and true labels (5 positives, 5 negatives).

```python
scores = [0.95, 0.90, 0.80, 0.75, 0.70, 0.60, 0.55, 0.40, 0.30, 0.20]
labels = [1, 1, 0, 1, 1, 0, 1, 0, 0, 0]


def confusion(threshold):
    tp = sum(s >= threshold and y == 1 for s, y in zip(scores, labels))
    fp = sum(s >= threshold and y == 0 for s, y in zip(scores, labels))
    fn = sum(s < threshold and y == 1 for s, y in zip(scores, labels))
    tn = sum(s < threshold and y == 0 for s, y in zip(scores, labels))
    return tp, fp, fn, tn


tp, fp, fn, tn = confusion(0.5)
precision, recall = tp / (tp + fp), tp / (tp + fn)
print(f"threshold 0.5: TP={tp} FP={fp} FN={fn} TN={tn}")
print(f"  accuracy {(tp + tn) / len(labels):.3f}, precision {precision:.3f}, recall {recall:.3f}, "
      f"F1 {2 * precision * recall / (precision + recall):.3f}, specificity {tn / (tn + fp):.3f}")

# ROC curve: sweep the threshold through every score
roc = [(0.0, 0.0)]
for t in sorted(set(scores), reverse=True):
    tp, fp, fn, tn = confusion(t)
    roc.append((fp / (fp + tn), tp / (tp + fn)))
print("ROC points (FPR, TPR):", " ".join(f"({f:.1f},{t:.1f})" for f, t in roc))
auc = sum((x2 - x1) * (y1 + y2) / 2 for (x1, y1), (x2, y2) in zip(roc, roc[1:]))
pos = [s for s, y in zip(scores, labels) if y == 1]
neg = [s for s, y in zip(scores, labels) if y == 0]
ranked = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))
print(f"AUC by trapezoids {auc:.2f}; fraction of (positive, negative) pairs ranked correctly {ranked:.2f}")

# The accuracy paradox on imbalanced data
y = [1] * 5 + [0] * 95
always_negative = [0] * 100
acc = sum(p == t for p, t in zip(always_negative, y)) / 100
print(f"always predicting 'negative' with 5% positives: accuracy {acc:.2f}, recall 0.00")
```

Output:

```text
threshold 0.5: TP=5 FP=2 FN=0 TN=3
  accuracy 0.800, precision 0.714, recall 1.000, F1 0.833, specificity 0.600
ROC points (FPR, TPR): (0.0,0.0) (0.0,0.2) (0.0,0.4) (0.2,0.4) (0.2,0.6) (0.2,0.8) (0.4,0.8) (0.4,1.0) (0.6,1.0) (0.8,1.0) (1.0,1.0)
AUC by trapezoids 0.84; fraction of (positive, negative) pairs ranked correctly 0.84
always predicting 'negative' with 5% positives: accuracy 0.95, recall 0.00
```

At threshold 0.5, the model catches every positive (recall 1.0) but 2 of its 7 positive predictions are wrong (precision 0.714). The ROC curve climbs from (0, 0) to (1, 1) through each threshold, and the area under it is 0.84. Counting pairs gives the same number: of the 25 (positive, negative) pairs, 21 have the positive scored higher, confirming that AUC is a ranking probability. The last line is the accuracy paradox: on data with 5% positives, a model that never predicts positive scores 95% accuracy while catching nothing.

### Example 2: A screening test by hand

In a population of 1,000 people, 10 have a disease. A test flags 9 of the 10 (TP = 9, FN = 1) and also 99 of the 990 healthy people (FP = 99, TN = 891).

- Accuracy $= (9 + 891)/1000 = 0.90$.
- Recall $= 9/10 = 0.90$; specificity $= 891/990 = 0.90$.
- Precision $= 9/(9 + 99) = 9/108 \approx 0.083$.
- F1 $= 2(0.083)(0.90)/(0.083 + 0.90) \approx 0.153$.

Despite 90% recall and 90% specificity, only about 1 in 12 positive results is a real case, because the disease is rare. This is why positive screening results are followed by confirmatory tests, and why precision must always be read together with the base rate.

## Applications

- **Medical diagnosis:** sensitivity and specificity guide clinical test choice.
- **Fraud and intrusion detection:** precision-recall analysis under extreme imbalance.
- **Search and recommendation:** precision at the top of a ranked list.
- **Credit decisions:** thresholds set from the costs of defaults and lost customers.
- **Model monitoring:** tracking metrics over time to detect degradation.

## Common mistakes

- **Reporting accuracy on imbalanced data.** Use recall, precision, F1, balanced accuracy, or PR curves.
- **Leaving the threshold at 0.5 by default.** Choose it from error costs and the operating needs.
- **Comparing AUCs and ignoring the operating region.** Two models with the same AUC can differ at the threshold you will use.
- **Using ROC curves alone for rare events.** Check precision as well.
- **Macro and micro confusion.** State which average you report.

## Revision notes

- Confusion matrix: TP, FP, FN, TN.
- Precision $TP/(TP + FP)$; recall $TP/(TP + FN)$; specificity $TN/(TN + FP)$; F1 = harmonic mean.
- Accuracy paradox: majority-class predictions look accurate on imbalanced data.
- ROC: TPR against FPR as the threshold varies; AUC = P(positive ranked above negative).
- PR curves and average precision for rare positives.
- Macro (classes equal) vs micro (examples equal) averaging; calibration matters for probabilities.

## Practice questions

:::question basic
A classifier has TP = 40, FP = 10, and FN = 20. Compute precision, recall, and F1.
:::answer
Precision $= 40/50 = 0.80$. Recall $= 40/60 \approx 0.667$. F1 $= 2(0.8)(0.667)/(0.8 + 0.667) \approx 0.727$.
:::

:::question basic
Would you prioritise precision or recall for (a) cancer screening and (b) a spam filter? Why?
:::answer
(a) Recall: missing a cancer (a false negative) is far more harmful than a false alarm, which further tests can resolve. (b) Precision: sending a legitimate email to spam (a false positive) is costly to the user, while letting an occasional spam through is a minor annoyance.
:::

:::question intermediate
What does an AUC of 0.5 mean, and what does an AUC of 0.84 mean in terms of ranking?
:::answer
An AUC of 0.5 means the model ranks a random positive above a random negative only half the time, no better than chance. An AUC of 0.84 means that for a randomly chosen positive and negative pair, the positive receives the higher score 84% of the time.
:::

:::question intermediate
A three-class model has recalls of 0.9 (1,000 examples), 0.5 (100 examples), and 0.2 (50 examples). Compare the macro-averaged and example-weighted recall.
:::answer
Macro average: $(0.9 + 0.5 + 0.2)/3 \approx 0.533$. Weighted by examples: $(0.9 \times 1000 + 0.5 \times 100 + 0.2 \times 50)/1150 = 960/1150 \approx 0.835$. The weighted (micro-style) figure hides the poor performance on the small classes, which the macro average exposes.
:::

:::question advanced
Explain why an ROC curve can look excellent on a fraud dataset with 100 frauds among 1,000,000 transactions while the system is impractical.
:::answer
The false positive rate divides false positives by the number of negatives, here about 1,000,000. An FPR of just 1% still means about 10,000 false alarms, against at most 100 real frauds, so precision is below 1% even with perfect recall, and investigators would be swamped. The ROC curve barely registers this because 1% FPR sits at the far left of its x-axis. A precision-recall curve exposes the problem directly, which is why it is preferred for rare positives.
:::

## Further learning

- **Next:** *Cross-Validation & Model Selection* uses these metrics to choose models reliably.
- **Related:** *Bias, Fairness & Explainability in AI* applies error rates to fairness audits.
