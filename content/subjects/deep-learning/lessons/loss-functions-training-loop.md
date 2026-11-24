---
lesson: loss-functions-training-loop
title: Loss Functions & the Training Loop
summary: Choosing loss functions for regression (MSE, MAE, Huber) and classification (binary and categorical cross-entropy), the softmax cross-entropy gradient, and the anatomy of the training loop: epochs, mini-batches, forward and backward passes, parameter updates, initialisation, and monitoring.
minutes: 45
type: theory
objectives:
  - Choose and compute loss functions for regression and classification and match them with output layers
  - Describe each step of the training loop and compute epochs, iterations, and batch counts
  - Monitor training and validation loss to diagnose problems and decide when to stop
review: ai-draft
---
## Introduction

A neural network learns by repeatedly asking one question: how wrong am I, and in which direction should each weight move to be less wrong? The **loss function** answers the first part with a single number, and the **training loop** answers the second through backpropagation and gradient descent, millions of times. Getting the loss and the loop right is the difference between a model that learns and one that silently fails.

**Before you start:** you should know *Non-Linear Activations & Gradient Flow* and gradient descent from *Linear Regression & Gradient Descent*.

## Core theory

### Losses for regression

- **Mean squared error** $\frac{1}{n}\sum(\hat{y} - y)^2$ penalises large errors heavily; it is the maximum-likelihood loss under Gaussian noise.
- **Mean absolute error** $\frac{1}{n}\sum|\hat{y} - y|$ is robust to outliers (it targets the median) but has a constant gradient that does not shrink near the optimum.
- **Huber loss** is quadratic for small errors and linear for large ones (beyond a threshold $\delta$), combining the strengths of both.

### Losses for classification

- **Binary cross-entropy** with a sigmoid output: $-[y\ln p + (1 - y)\ln(1 - p)]$.
- **Categorical cross-entropy** with a softmax output: $L = -\sum_k y_k\ln p_k = -\ln p_{\text{true}}$. It is small when the correct class gets high probability and large when the model is confidently wrong.
- The gradient of softmax followed by cross-entropy with respect to the logits is beautifully simple: $\frac{\partial L}{\partial z_k} = p_k - y_k$. Libraries combine the two (for example a "cross-entropy with logits" function) for numerical stability.
- Variants include **label smoothing** (targets like 0.9 instead of 1), **focal loss** for heavy class imbalance, hinge loss, and contrastive losses for embeddings.

### The training loop

For each **epoch** (one pass over the training data):

1. Shuffle the data and split it into **mini-batches**.
2. For each batch: **forward pass** (compute predictions and the loss), **backward pass** (compute gradients of the loss with respect to every parameter by backpropagation), and **update** (an optimiser step such as SGD or Adam).
3. Reset accumulated gradients (in frameworks that accumulate them).
4. After the epoch, evaluate on the validation set and log the metrics.

An **iteration** is one batch update; with $N$ examples and batch size $B$, an epoch has $\lceil N/B \rceil$ iterations. Larger batches give smoother gradients and better hardware use; smaller batches add noise that can help generalisation.

### Initialisation and monitoring

Weights start as small random values (Xavier or He scaling). Initialising every weight to zero would make all units in a layer compute the same thing and receive the same gradient forever: random initialisation **breaks the symmetry**.

Watch both curves. Falling training and validation loss: keep going. Training loss falling while validation loss rises: **overfitting**, so stop early or regularise. Loss not falling: learning rate too low or too high, a bug, or poor initialisation. Loss becoming NaN: exploding values, often a learning rate that is too high. Save **checkpoints** of the best model and use **early stopping**.

## Worked examples

### Example 1: Losses and a complete training loop

The program compares regression losses, computes cross-entropy for a good and a bad prediction, and then trains a 2-4-1 network on XOR with a hand-written forward pass, backward pass, and update.

```python
import math
import random

# Regression losses on the same residuals
residuals = [0.5, -1.0, 3.0]
mse = sum(r * r for r in residuals) / len(residuals)
mae = sum(abs(r) for r in residuals) / len(residuals)
huber = sum(0.5 * r * r if abs(r) <= 1 else abs(r) - 0.5 for r in residuals) / len(residuals)
print(f"residuals {residuals}: MSE {mse:.3f}, MAE {mae:.3f}, Huber(delta=1) {huber:.3f}")

# Cross-entropy for a 3-class prediction where class 0 is correct
for probs in ([0.7, 0.2, 0.1], [0.1, 0.6, 0.3]):
    print(f"predicted {probs}, true class 0: cross-entropy {-math.log(probs[0]):.3f}")

# A complete training loop: a 2-4-1 network learns XOR
random.seed(1)
X = [(0, 0), (0, 1), (1, 0), (1, 1)]
Y = [0, 1, 1, 0]
H = 4
W1 = [[random.uniform(-1, 1) for _ in range(H)] for _ in range(2)]
b1 = [0.0] * H
W2 = [random.uniform(-1, 1) for _ in range(H)]
b2 = 0.0
lr = 0.5


def forward(x):
    h = [math.tanh(x[0] * W1[0][j] + x[1] * W1[1][j] + b1[j]) for j in range(H)]
    p = 1 / (1 + math.exp(-(sum(hj * w for hj, w in zip(h, W2)) + b2)))
    return h, p


for epoch in range(1, 3001):
    gW1 = [[0.0] * H for _ in range(2)]
    gb1, gW2, gb2, loss = [0.0] * H, [0.0] * H, 0.0, 0.0
    for x, y in zip(X, Y):
        h, p = forward(x)                                  # 1. forward pass
        loss += -(y * math.log(p) + (1 - y) * math.log(1 - p)) / len(X)
        dz2 = (p - y) / len(X)                             # 2. backward pass (chain rule)
        for j in range(H):
            gW2[j] += dz2 * h[j]
            dz1 = dz2 * W2[j] * (1 - h[j] ** 2)
            gb1[j] += dz1
            gW1[0][j] += dz1 * x[0]
            gW1[1][j] += dz1 * x[1]
        gb2 += dz2
    for j in range(H):                                     # 3. update the parameters
        W2[j] -= lr * gW2[j]
        b1[j] -= lr * gb1[j]
        W1[0][j] -= lr * gW1[0][j]
        W1[1][j] -= lr * gW1[1][j]
    b2 -= lr * gb2
    if epoch in (1, 100, 500, 1000, 3000):
        print(f"epoch {epoch:4}: loss {loss:.4f}")
print("predictions:", [f"{x} -> {forward(x)[1]:.3f}" for x in X])
```

Output:

```text
residuals [0.5, -1.0, 3.0]: MSE 3.417, MAE 1.500, Huber(delta=1) 1.042
predicted [0.7, 0.2, 0.1], true class 0: cross-entropy 0.357
predicted [0.1, 0.6, 0.3], true class 0: cross-entropy 2.303
epoch    1: loss 0.6918
epoch  100: loss 0.1263
epoch  500: loss 0.0113
epoch 1000: loss 0.0051
epoch 3000: loss 0.0016
predictions: ['(0, 0) -> 0.000', '(0, 1) -> 0.998', '(1, 0) -> 0.998', '(1, 1) -> 0.003']
```

On residuals 0.5, −1, and 3, MSE (3.417) is dominated by the large error, MAE (1.5) weights all errors linearly, and Huber (1.042) sits between them. Cross-entropy is 0.357 when the correct class gets probability 0.7, but 2.303 when it gets only 0.1. In the training loop, the loss starts at 0.69, which is $\ln 2$, the loss of a model guessing 50/50, and falls to 0.0016 after 3,000 epochs as the network learns XOR: its outputs are essentially 0, 1, 1, 0. Every line of the loop corresponds to a step above: forward pass, loss, backward pass via the chain rule, and parameter update.

### Example 2: A cross-entropy gradient and batch arithmetic

Logits $(2, 1, 0.1)$ give softmax probabilities $(0.659, 0.242, 0.099)$. If the true class is 0, the loss is $-\ln 0.659 \approx 0.417$, and the gradient with respect to the logits is

$$\mathbf{p} - \mathbf{y} = (0.659 - 1,\ 0.242,\ 0.099) = (-0.341,\ 0.242,\ 0.099)$$

so gradient descent raises the correct logit and lowers the others, in proportion to the probabilities they wrongly received.

Training on 50,000 images with batch size 128 gives $\lceil 50{,}000/128 \rceil = 391$ iterations per epoch (the last batch is partial), so 10 epochs perform 3,910 parameter updates.

## Applications

- **Image classification:** softmax cross-entropy over thousands of classes.
- **Object detection:** combined losses for class labels and bounding-box regression (often Huber-style smooth L1).
- **Language models:** next-token cross-entropy over a vocabulary of tens of thousands of tokens.
- **Forecasting:** MAE or Huber when outliers are common.
- **Imbalanced detection:** focal loss for rare objects or events.

## Common mistakes

- **Using MSE for classification.** Cross-entropy gives better gradients and probabilistic outputs.
- **Applying softmax twice.** Pass logits to losses that include the softmax.
- **Forgetting to shuffle.** Ordered data produces biased, oscillating updates.
- **Not resetting gradients.** Accumulated gradients from earlier batches corrupt updates.
- **Watching only the training loss.** Validation loss reveals overfitting.
- **Initialising all weights to zero.** Every unit then learns the same thing.

## Revision notes

- Regression: MSE (outlier-sensitive), MAE (robust), Huber (both).
- Classification: binary cross-entropy with sigmoid; categorical cross-entropy with softmax, $L = -\ln p_{\text{true}}$.
- Softmax + cross-entropy gradient with respect to logits: $\mathbf{p} - \mathbf{y}$.
- Loop: shuffle, batches, forward, loss, backward, update, zero gradients; validate each epoch.
- Iterations per epoch $= \lceil N/B \rceil$.
- Random initialisation breaks symmetry; monitor curves, early stopping, checkpoints.

## Practice questions

:::question basic
Compute the MSE and MAE of residuals 2, −2, and 4.
:::answer
MSE $= (4 + 4 + 16)/3 = 8$. MAE $= (2 + 2 + 4)/3 \approx 2.667$.
:::

:::question basic
Why is cross-entropy preferred to MSE for classification networks?
:::answer
Cross-entropy is the negative log-likelihood of the correct class, so minimising it gives calibrated probabilities, and combined with softmax or sigmoid it yields the simple gradient $p - y$, which stays large when the model is confidently wrong. MSE with sigmoid or softmax outputs produces small gradients when predictions saturate, so learning stalls.
:::

:::question intermediate
A dataset has 10,000 examples. With batch size 64, how many iterations are in an epoch, and how many updates do 20 epochs perform?
:::answer
$\lceil 10{,}000/64 \rceil = \lceil 156.25 \rceil = 157$ iterations per epoch (the last batch has 16 examples), so 20 epochs perform $157 \times 20 = 3{,}140$ updates.
:::

:::question intermediate
Why must the weights of a hidden layer not all be initialised to the same value?
:::answer
If every unit in a layer starts with identical weights, they compute identical outputs and receive identical gradients, so they stay identical forever: the layer behaves like a single unit. Random initialisation breaks this symmetry so units can learn different features.
:::

:::question advanced
Training loss keeps falling, but validation loss starts rising after epoch 20. Diagnose the problem and list four responses.
:::answer
The model has started to overfit: it is fitting noise and peculiarities of the training set that do not generalise. Responses: use early stopping and keep the checkpoint from around epoch 20; add regularisation such as weight decay or dropout; use data augmentation or gather more data; reduce model capacity; or lower the learning rate with a schedule so that later training is more conservative.
:::

## Further learning

- **Next:** *Computational Graphs & Chain Rule* explains how the backward pass computes gradients.
- **Related:** *Classification Metrics & ROC Curves* in Machine Learning covers evaluation beyond the loss.
