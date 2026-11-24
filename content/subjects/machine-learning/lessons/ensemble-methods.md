---
lesson: ensemble-methods
title: Ensemble Methods: Bagging, Random Forests & Boosting
summary: Combining models for better accuracy: why voting helps, bagging with bootstrap samples and out-of-bag estimates, random forests with random feature subsets, boosting with AdaBoost and gradient boosting, stacking, and how ensembles trade bias against variance.
minutes: 50
type: theory
objectives:
  - Explain why combining diverse models reduces error and compute the accuracy of a majority vote
  - Describe bagging, out-of-bag evaluation, and random forests, and why feature subsampling decorrelates trees
  - Apply AdaBoost's weight updates and explain gradient boosting, its key hyperparameters, and stacking
review: ai-draft
---
## Introduction

A single decision tree is easy to read but unstable and often inaccurate. Combine hundreds of them in the right way and you get some of the most accurate models known for tabular data: random forests and gradient-boosted trees win a large share of data-science competitions and power credit scoring, ranking, and fraud detection systems. **Ensemble methods** rely on a simple statistical fact: averaging many imperfect, partly independent opinions cancels out their individual errors.

**Before you start:** you should know decision trees from *Logistic Regression & Decision Trees* and the binomial distribution.

## Core theory

### Why ensembles work

If $n$ classifiers each have accuracy $p > 0.5$ and make **independent** errors, a majority vote is correct with probability

$$P(\text{majority correct}) = \sum_{k > n/2}\binom{n}{k}p^k(1 - p)^{n - k}$$

which approaches 1 as $n$ grows. Real models' errors are correlated, so the gain is smaller, which is why ensembles work hard to make their members **diverse**. For an average of $B$ models, each with variance $\sigma^2$ and pairwise correlation $\rho$, the variance is $\rho\sigma^2 + \frac{1 - \rho}{B}\sigma^2$: more models remove the second term, but only lower correlation shrinks the first.

### Bagging

**Bootstrap aggregating** (bagging) trains each model on a **bootstrap sample**: $n$ examples drawn with replacement from the $n$ training examples. Each sample contains about $1 - 1/e \approx 63.2\%$ of the distinct examples. Predictions are averaged (regression) or voted (classification). Bagging mainly reduces **variance**, so it helps unstable, low-bias learners such as deep trees. The roughly 36.8% of examples left out of each bootstrap sample are **out-of-bag** (OOB) for that model, and predicting each example using only the models that did not see it gives a free validation estimate.

### Random forests

A random forest is bagged decision trees with one more source of randomness: at every split, each tree considers only a **random subset of features** (commonly $\sqrt{d}$ for classification and $d/3$ for regression). This stops every tree from splitting on the same dominant feature, **decorrelating** the trees so their average has lower variance. Random forests work well with little tuning and provide feature importance measures (impurity decrease or, more reliably, permutation importance).

### Boosting

Boosting trains models **sequentially**, each one focusing on the mistakes of those before it; it mainly reduces **bias**, turning weak learners (barely better than chance) into a strong one.

**AdaBoost** keeps a weight for each training example, starting equal. In round $t$:

1. Train a weak learner $h_t$ minimising the weighted error $\varepsilon_t$.
2. Give it a vote $\alpha_t = \frac{1}{2}\ln\frac{1 - \varepsilon_t}{\varepsilon_t}$ (larger for more accurate learners).
3. Update weights $w_i \leftarrow w_i\,e^{-\alpha_t y_i h_t(x_i)}$ and normalise, so misclassified examples gain weight.

The final classifier is $H(x) = \text{sign}\left(\sum_t \alpha_t h_t(x)\right)$.

**Gradient boosting** generalises this: each new tree is fitted to the negative gradient of the loss with respect to the current predictions, which for squared error is simply the **residuals**. Key hyperparameters are the number of trees, the **learning rate** (shrinking each tree's contribution, typically 0.01 to 0.1), tree depth (often 3 to 8), and subsampling. Too many trees can overfit, so early stopping on validation data is standard. XGBoost, LightGBM, and CatBoost are popular, highly optimised implementations.

### Stacking

**Stacking** trains a **meta-model** (often logistic regression) on the predictions of several different base models, using out-of-fold predictions so the meta-model never sees predictions made on data the base models trained on.

## Worked examples

### Example 1: Voting, bootstrapping, and AdaBoost

The program computes majority-vote accuracy for independent voters, measures the distinct fraction in a bootstrap sample, and runs five rounds of AdaBoost with decision stumps (one-threshold rules) on ten points.

```python
import math
import random

# 1. Why voting helps: independent classifiers, each 70% accurate
for n in (1, 5, 25):
    p_majority = sum(math.comb(n, k) * 0.7 ** k * 0.3 ** (n - k) for k in range(n // 2 + 1, n + 1))
    print(f"{n:2} independent voters at 70% accuracy -> majority correct {p_majority:.4f}")

# 2. Bagging: a bootstrap sample contains about 63.2% of the distinct points
random.seed(1)
n = 10000
sample = [random.randrange(n) for _ in range(n)]
print(f"distinct points in one bootstrap sample: {len(set(sample)) / n:.3f} (theory 1 - 1/e = {1 - 1 / math.e:.3f})")

# 3. AdaBoost with decision stumps on one feature
xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ys = [1, 1, -1, -1, 1, 1, 1, -1, -1, 1]
weights = [1 / len(xs)] * len(xs)
stumps = []


def stump_predict(threshold, sign, x):
    return sign if x < threshold else -sign


for round_ in range(1, 6):
    best = min(((t + 0.5, s) for t in range(0, 11) for s in (1, -1)),
               key=lambda ts: sum(w for w, x, y in zip(weights, xs, ys) if stump_predict(*ts, x) != y))
    error = sum(w for w, x, y in zip(weights, xs, ys) if stump_predict(*best, x) != y)
    alpha = 0.5 * math.log((1 - error) / error)
    stumps.append((alpha, best))
    weights = [w * math.exp(-alpha * y * stump_predict(*best, x)) for w, x, y in zip(weights, xs, ys)]
    weights = [w / sum(weights) for w in weights]
    ensemble = [1 if sum(a * stump_predict(*st, x) for a, st in stumps) > 0 else -1 for x in xs]
    wrong = sum(p != y for p, y in zip(ensemble, ys))
    rule = f"x < {best[0]} -> {best[1]:+d}"
    print(f"round {round_}: stump '{rule:13}' weighted error {error:.3f}, alpha {alpha:.3f}, ensemble training errors {wrong}")
```

Output:

```text
 1 independent voters at 70% accuracy -> majority correct 0.7000
 5 independent voters at 70% accuracy -> majority correct 0.8369
25 independent voters at 70% accuracy -> majority correct 0.9825
distinct points in one bootstrap sample: 0.632 (theory 1 - 1/e = 0.632)
round 1: stump 'x < 7.5 -> +1' weighted error 0.300, alpha 0.424, ensemble training errors 3
round 2: stump 'x < 4.5 -> -1' weighted error 0.286, alpha 0.458, ensemble training errors 4
round 3: stump 'x < 2.5 -> +1' weighted error 0.267, alpha 0.506, ensemble training errors 1
round 4: stump 'x < 0.5 -> -1' weighted error 0.330, alpha 0.355, ensemble training errors 1
round 5: stump 'x < 9.5 -> -1' weighted error 0.337, alpha 0.339, ensemble training errors 0
```

Five independent 70%-accurate voters are right 83.7% of the time, and 25 are right 98.3% of the time, under the optimistic assumption of independence. The bootstrap sample contains 63.2% of the points, matching $1 - 1/e$. In AdaBoost, no single stump can fit the alternating pattern of labels, but every stump has weighted error below 0.5, and the weighted combination reaches zero training errors after five rounds. The path is not monotone: after round 2, the ensemble makes 4 errors, more than after round 1, before improving. The round 4 stump, "x < 0.5 → −1", has its threshold below every point, so it simply predicts +1 everywhere; with the reweighted data even a constant vote is useful.

### Example 2: One AdaBoost weight update by hand

Ten examples start with weight 0.1 each. The first stump misclassifies 3 of them, so $\varepsilon_1 = 0.3$ and

$$\alpha_1 = \tfrac{1}{2}\ln\frac{0.7}{0.3} = \tfrac{1}{2}\ln 2.333 \approx 0.424$$

Misclassified weights are multiplied by $e^{0.424} \approx 1.528$, giving 0.1528; correct ones by $e^{-0.424} \approx 0.655$, giving 0.0655. The total is $3(0.1528) + 7(0.0655) = 0.4583 + 0.4583 = 0.9165$, so after normalising, each misclassified example has weight 0.1667 and each correct one 0.0714. The misclassified examples now hold exactly half of the total weight, so the first stump would have error exactly 0.5 on the new weights: AdaBoost always forces the next learner to find something new.

For the majority vote with 5 voters at 70%: $P = \binom{5}{3}0.7^3 0.3^2 + \binom{5}{4}0.7^4 0.3 + 0.7^5 = 0.3087 + 0.3602 + 0.1681 = 0.8369$, matching the program.

## Applications

- **Tabular prediction:** credit risk, insurance pricing, churn, and fraud use gradient-boosted trees.
- **Search ranking:** boosted trees (such as LambdaMART) rank search results.
- **Remote sensing and ecology:** random forests classify land cover and species presence.
- **Feature importance:** forests help identify influential variables.
- **Competitions:** stacked ensembles frequently top machine-learning leaderboards.

## Common mistakes

- **Expecting bagging to fix high bias.** Averaging many underfitting models still underfits; use boosting or a more flexible base model.
- **Boosting without a learning rate or early stopping.** Many trees then overfit noise.
- **Ensembling near-identical models.** Without diversity, the average barely improves.
- **Trusting impurity-based feature importance blindly.** It favours high-cardinality features; check permutation importance.
- **Stacking with in-sample predictions.** The meta-model must learn from out-of-fold predictions.

## Revision notes

- Majority vote of independent better-than-chance classifiers improves with more voters; correlation limits gains.
- Bagging: bootstrap samples (about 63.2% distinct), average or vote; reduces variance; OOB estimates.
- Random forest: bagging + random feature subsets per split, decorrelating trees.
- AdaBoost: $\alpha = \frac{1}{2}\ln\frac{1 - \varepsilon}{\varepsilon}$; reweight misclassified examples; weighted vote.
- Gradient boosting: fit trees to negative gradients (residuals); learning rate, depth, number of trees, early stopping.
- Stacking: meta-model on out-of-fold predictions.

## Practice questions

:::question basic
What is the main difference between bagging and boosting?
:::answer
Bagging trains models independently, in parallel, on bootstrap samples and averages them, mainly reducing variance. Boosting trains models sequentially, each concentrating on the errors of the previous ones, and combines them with weights, mainly reducing bias.
:::

:::question basic
About what fraction of the training examples appears in a bootstrap sample, and how are the rest used?
:::answer
About 63.2% ($1 - 1/e$) of the distinct examples appear; the remaining 36.8% are out-of-bag for that model. Predicting each example with only the models for which it was out-of-bag gives an out-of-bag estimate of generalisation error, without a separate validation set.
:::

:::question intermediate
An AdaBoost weak learner has weighted error 0.2. What is its vote $\alpha$, and what would $\alpha$ be for error 0.5?
:::answer
$\alpha = \frac{1}{2}\ln\frac{0.8}{0.2} = \frac{1}{2}\ln 4 \approx 0.693$. With error 0.5, $\alpha = \frac{1}{2}\ln 1 = 0$: a learner no better than chance gets no vote.
:::

:::question intermediate
Why do random forests consider only a random subset of features at each split?
:::answer
If one feature is very strong, every bagged tree would split on it first and the trees would be highly correlated, so averaging them would reduce variance only a little. Restricting each split to a random subset forces trees to use different features, decorrelating them and making the forest's average much more stable.
:::

:::question advanced
Using the formula for the variance of an average of correlated models, explain why adding more trees to a forest eventually stops helping.
:::answer
For $B$ models with variance $\sigma^2$ and pairwise correlation $\rho$, the variance of their average is $\rho\sigma^2 + \frac{1 - \rho}{B}\sigma^2$. As $B$ grows, the second term vanishes, but the first term $\rho\sigma^2$ remains. Beyond a few hundred trees, almost all the remaining variance comes from the correlation between trees, so further trees give negligible improvement; reducing $\rho$ (for example with smaller feature subsets) is what helps.
:::

## Further learning

- **Next:** *K-Means & Density-Based Clustering* turns to unsupervised learning.
- **Related:** *L1/L2 Regularization & Bias-Variance* explains the bias-variance trade-off that ensembles exploit.
