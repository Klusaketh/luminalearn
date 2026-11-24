---
lesson: knn-naive-bayes-svm
title: k-NN, Naive Bayes & Support Vector Machines
summary: Three classic classifiers: k-nearest neighbours (distance, choice of k, curse of dimensionality), Naive Bayes (Bayes' rule, conditional independence, Laplace smoothing, log probabilities), and support vector machines (maximum margin, support vectors, hinge loss, soft margins, and kernels).
minutes: 55
type: theory
objectives:
  - Classify with k-nearest neighbours and explain how k, distance, and dimensionality affect it
  - Train and apply a multinomial Naive Bayes text classifier with Laplace smoothing in log space
  - Explain the maximum-margin idea, support vectors, the hinge loss, the C parameter, and the kernel trick
review: ai-draft
---
## Introduction

Different classifiers embody different ideas of how to generalise. **k-nearest neighbours** says "you are like your neighbours." **Naive Bayes** says "combine the evidence from each feature using probability." **Support vector machines** say "draw the boundary as far as possible from both classes." Each idea leads to a practical algorithm with characteristic strengths: k-NN needs no training, Naive Bayes is fast and excellent for text, and SVMs are powerful in high dimensions.

**Before you start:** you should know *Conditional Probability & Bayes Theorem* and *Feature Scaling & One-Hot Encoding*.

## Core theory

### k-nearest neighbours

To classify a point, find the $k$ training points closest to it and take a majority vote (or average their values, for regression). k-NN is a **lazy** learner: training just stores the data, and the work happens at prediction time.

- **Distance:** Euclidean is the default; Manhattan and cosine distance suit other data. Features must be **scaled**.
- **Choosing $k$:** small $k$ follows the data closely (low bias, high variance, sensitive to noise); large $k$ smooths the boundary (higher bias). Use odd $k$ for two classes to avoid ties, and tune it by cross-validation. Weighting votes by inverse distance is a common refinement.
- **Cost:** a naive prediction compares the query with all $n$ points, $O(nd)$; KD-trees and approximate nearest-neighbour indexes speed this up.
- **Curse of dimensionality:** in many dimensions, all points become nearly equally far apart, so "nearest" loses meaning. Dimensionality reduction helps.

### Naive Bayes

By Bayes' rule, $P(c \mid \mathbf{x}) \propto P(c)\,P(\mathbf{x} \mid c)$. Naive Bayes assumes the features are **conditionally independent** given the class:

$$P(c \mid x_1, \dots, x_d) \propto P(c)\prod_{i=1}^{d}P(x_i \mid c)$$

The assumption is rarely true, but the classifier often works well because only the ranking of classes matters. Variants: **multinomial** (word counts, for text), **Bernoulli** (word present or absent), and **Gaussian** (continuous features). For text, $P(w \mid c)$ is estimated from word counts with **Laplace (add-one) smoothing**:

$$P(w \mid c) = \frac{\text{count}(w, c) + 1}{\text{total words in } c + |V|}$$

so an unseen word does not force a probability of zero. Multiplying many small probabilities underflows, so implementations add **log probabilities**. Naive Bayes trains in a single pass and is a strong baseline, but its probability estimates tend to be overconfident.

### Support vector machines

A linear SVM looks for the hyperplane $\mathbf{w}^\top\mathbf{x} + b = 0$ that separates the classes with the **largest margin**. With labels $y_i \in \{-1, +1\}$ and the constraint $y_i(\mathbf{w}^\top\mathbf{x}_i + b) \ge 1$, the margin width is $2/\|\mathbf{w}\|$, so the hard-margin SVM solves

$$\min_{\mathbf{w}, b}\ \tfrac{1}{2}\|\mathbf{w}\|^2 \quad \text{subject to} \quad y_i(\mathbf{w}^\top\mathbf{x}_i + b) \ge 1$$

The points that lie on the margin are the **support vectors**; they alone determine the boundary. Real data overlap, so the **soft-margin** SVM allows violations and minimises

$$\tfrac{1}{2}\|\mathbf{w}\|^2 + C\sum_i \max\left(0,\ 1 - y_i(\mathbf{w}^\top\mathbf{x}_i + b)\right)$$

The second term is the **hinge loss**. Large $C$ penalises violations heavily (narrow margin, risk of overfitting); small $C$ allows more violations (wider margin). The **kernel trick** replaces dot products with a kernel function, such as the RBF kernel $K(\mathbf{x}, \mathbf{z}) = e^{-\gamma\|\mathbf{x} - \mathbf{z}\|^2}$, to learn non-linear boundaries without computing high-dimensional features explicitly. SVMs need scaled features and become slow on very large datasets.

## Worked examples

### Example 1: k-NN votes and a spam filter

The first part classifies the query point (3, 3) with different values of $k$. The second trains a multinomial Naive Bayes classifier on six short messages.

```python
import math
from collections import Counter

# k-nearest neighbours
points = [((3.5, 3.2), "B"), ((2.5, 2.4), "A"), ((2.2, 3.5), "A"), ((3.8, 2.1), "A"),
          ((4.5, 4.5), "B"), ((5.0, 3.5), "B"), ((1.0, 1.0), "A")]
query = (3, 3)
ranked = sorted(points, key=lambda p: math.dist(p[0], query))
print("neighbours by distance:", ", ".join(f"{label}@{math.dist(p, query):.2f}" for p, label in ranked))
for k in (1, 3, 5, 7):
    votes = Counter(label for _, label in ranked[:k])
    print(f"  k = {k}: votes {dict(sorted(votes.items()))} -> predict {votes.most_common(1)[0][0]}")

# Multinomial Naive Bayes with Laplace (add-one) smoothing
train = [("win cash prize now", "spam"), ("claim your free prize", "spam"), ("free cash offer now", "spam"),
         ("are we meeting today", "ham"), ("call me when you are free", "ham"), ("lunch today at noon", "ham")]
counts = {"spam": Counter(), "ham": Counter()}
docs = Counter()
for text, label in train:
    counts[label].update(text.split())
    docs[label] += 1
vocab = set(counts["spam"]) | set(counts["ham"])
print(f"vocabulary size {len(vocab)}; words in spam {sum(counts['spam'].values())}, in ham {sum(counts['ham'].values())}")


def log_score(text, label):
    total = sum(counts[label].values())
    score = math.log(docs[label] / len(train))
    for word in text.split():
        if word in vocab:                      # unseen words are ignored
            score += math.log((counts[label][word] + 1) / (total + len(vocab)))
    return score


for message in ["free prize today", "are you free for lunch"]:
    s, h = log_score(message, "spam"), log_score(message, "ham")
    p_spam = 1 / (1 + math.exp(h - s))
    print(f"'{message}': log P(spam, msg) = {s:.3f}, log P(ham, msg) = {h:.3f} -> P(spam | msg) = {p_spam:.3f}")
```

Output:

```text
neighbours by distance: B@0.54, A@0.78, A@0.94, A@1.20, B@2.06, B@2.12, A@2.83
  k = 1: votes {'B': 1} -> predict B
  k = 3: votes {'A': 2, 'B': 1} -> predict A
  k = 5: votes {'A': 3, 'B': 2} -> predict A
  k = 7: votes {'A': 4, 'B': 3} -> predict A
vocabulary size 19; words in spam 12, in ham 14
'free prize today': log P(spam, msg) = -8.798, log P(ham, msg) = -9.391 -> P(spam | msg) = 0.644
'are you free for lunch': log P(spam, msg) = -13.330, log P(ham, msg) = -11.501 -> P(spam | msg) = 0.138
```

The single nearest neighbour is a B point, so 1-NN predicts B; but the next three neighbours are A, so $k = 3, 5, 7$ all predict A. That lone nearby B is plausibly noise, and larger $k$ outvotes it: a direct view of the bias-variance trade-off. In the spam filter, "free" and "prize" are spam-heavy words, so "free prize today" gets a 64% spam probability despite "today" appearing only in ham. "are you free for lunch" is mostly ham words, giving 14%; the unseen word "for" is ignored. Note that the scores are log probabilities, and the posterior is recovered by comparing the two.

### Example 2: Margins, support vectors, and smoothing by hand

Take the line $x_1 + x_2 - 4 = 0$, that is $\mathbf{w} = (1, 1)$, $b = -4$.

| Point | Class $y$ | $f(\mathbf{x}) = x_1 + x_2 - 4$ | $y \cdot f$ | Status |
| :--- | :--- | :--- | :--- | :--- |
| (1, 1) | −1 | −2 | 2 | Beyond the margin |
| (2, 1) | −1 | −1 | 1 | On the margin: support vector |
| (3, 2) | +1 | 1 | 1 | On the margin: support vector |
| (4, 4) | +1 | 4 | 4 | Beyond the margin |

The margin width is $2/\|\mathbf{w}\| = 2/\sqrt{2} \approx 1.414$. A new point (2.5, 2) of class −1 gives $f = 0.5$ and $y \cdot f = -0.5$: it is misclassified, with hinge loss $\max(0, 1 - (-0.5)) = 1.5$.

For the spam filter, $P(\text{free} \mid \text{spam}) = \frac{2 + 1}{12 + 19} = \frac{3}{31} \approx 0.097$, while $P(\text{today} \mid \text{spam}) = \frac{0 + 1}{31} \approx 0.032$: small, but not zero, thanks to smoothing.

## Applications

- **Recommendation and retrieval:** nearest-neighbour search over embeddings.
- **Text classification:** Naive Bayes for spam filtering, sentiment, and topic labelling.
- **Bioinformatics and image classification:** SVMs on high-dimensional features.
- **Anomaly detection:** distance to neighbours and one-class SVMs.
- **Baselines:** all three are quick, strong references before trying complex models.

## Common mistakes

- **Running k-NN or SVMs on unscaled features.** Large-range features dominate distances and margins.
- **Choosing $k = 1$ by default.** It overfits noise; tune $k$ by cross-validation.
- **Forgetting smoothing in Naive Bayes.** One unseen word would zero out a whole class.
- **Multiplying raw probabilities.** Use log probabilities to avoid underflow.
- **Treating Naive Bayes probabilities as calibrated.** They are often too extreme.
- **Using a huge $C$ on noisy data.** The SVM then contorts itself to fit every point.

## Revision notes

- k-NN: majority of $k$ nearest neighbours; lazy; scale features; small $k$ high variance, large $k$ high bias.
- Curse of dimensionality: distances concentrate in high dimensions.
- Naive Bayes: $P(c)\prod P(x_i \mid c)$; conditional independence; Laplace smoothing; log space.
- SVM: maximise margin $2/\|\mathbf{w}\|$; support vectors define the boundary.
- Soft margin: hinge loss $\max(0, 1 - yf)$ weighted by $C$.
- Kernel trick (RBF, polynomial) for non-linear boundaries.

## Practice questions

:::question basic
Why must features be scaled before using k-nearest neighbours?
:::answer
k-NN compares points by distance. A feature with a large numerical range (such as income in rupees) contributes far more to the distance than one with a small range (such as age), so it alone would decide who the neighbours are. Scaling puts features on comparable footing.
:::

:::question basic
What problem does Laplace smoothing solve in Naive Bayes?
:::answer
Without smoothing, a word that never appeared in a class's training documents gets probability zero, which makes the whole product zero and rules the class out regardless of all other evidence. Adding one to every count gives unseen words a small non-zero probability.
:::

:::question intermediate
The five nearest neighbours of a point have labels A, B, B, A, B in order of distance. What do 1-NN, 3-NN, and 5-NN predict?
:::answer
1-NN uses only the nearest point: A. 3-NN uses A, B, B: B wins 2 to 1. 5-NN uses all five: B wins 3 to 2.
:::

:::question intermediate
What are support vectors, and what happens to an SVM if you delete a training point that is not a support vector?
:::answer
Support vectors are the training points that lie on or inside the margin (or are misclassified); the solution depends only on them. Deleting a point that lies strictly outside the margin changes nothing: the optimal hyperplane stays the same.
:::

:::question advanced
Explain the curse of dimensionality for k-NN with a numerical example.
:::answer
Suppose data are uniform in a unit hypercube and we want a neighbourhood containing 10% of the points. In one dimension, an interval of length 0.1 suffices. In 10 dimensions, a sub-cube needs edge length $0.1^{1/10} \approx 0.79$: it spans 79% of the range of every feature, so the "neighbours" are not local at all. As dimension grows, distances between random points also concentrate around the same value, so the nearest and farthest neighbours are almost equally far, and k-NN's notion of similarity breaks down. Feature selection, dimensionality reduction, or learned embeddings help.
:::

## Further learning

- **Next:** *Ensemble Methods: Bagging, Random Forests & Boosting* combines many models for better accuracy.
- **Related:** *Conditional Probability & Bayes Theorem* in Probability explains the rule behind Naive Bayes.
