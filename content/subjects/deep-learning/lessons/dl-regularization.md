---
lesson: dl-regularization
title: Regularization: Dropout, Batch Norm & Weight Decay
summary: Keeping deep networks from overfitting: weight decay, dropout and its inverted scaling, batch normalisation with running statistics (and layer normalisation), early stopping, data augmentation, and label smoothing.
minutes: 50
type: theory
objectives:
  - Apply weight decay and inverted dropout and explain their effect on training and inference
  - Compute batch normalisation for a mini-batch, including running statistics for inference, and compare it with layer normalisation
  - Use early stopping and data augmentation as part of a regularisation strategy
review: ai-draft
---
## Introduction

Modern networks have far more parameters than training examples; they can even memorise datasets whose labels have been replaced at random. Yet with the right techniques they generalise remarkably well. **Regularisation** in deep learning is a toolbox of methods that make memorisation harder and generalisation easier: shrinking weights, randomly silencing neurons, normalising activations, stopping at the right moment, and showing the model more varied data.

**Before you start:** you should know *L1/L2 Regularization & Bias-Variance* and *Loss Functions & the Training Loop*.

## Core theory

### Weight decay

Adding $\frac{\lambda}{2}\|\mathbf{w}\|^2$ to the loss adds $\lambda\mathbf{w}$ to the gradient, so each SGD step becomes

$$\mathbf{w} \leftarrow \mathbf{w} - \eta(\mathbf{g} + \lambda\mathbf{w}) = (1 - \eta\lambda)\mathbf{w} - \eta\mathbf{g}$$

The weights shrink by a constant factor every step, which favours small weights and smoother functions. With Adam, use the decoupled form (AdamW). Typical values of $\lambda$ range from $10^{-5}$ to $10^{-1}$, depending on the optimiser and model.

### Dropout

During training, **dropout** sets each unit's output to zero with probability $p$ (the drop rate), independently for every example and every step; each unit is kept with probability $q = 1 - p$. Units cannot rely on particular partners, so they learn more robust, redundant features, and training resembles averaging an ensemble of exponentially many thinned subnetworks.

**Inverted dropout** divides the kept activations by $q$ during training, so the expected value of each activation is unchanged; at inference, dropout is simply switched off with no rescaling. Typical drop rates are 0.1 in Transformers and up to 0.5 in large fully connected layers. Keeping dropout on at test time and averaging several predictions (**Monte Carlo dropout**) gives a rough uncertainty estimate.

### Batch normalisation

**Batch normalisation** (Ioffe and Szegedy, 2015) normalises each feature over the mini-batch:

$$\mu_B = \frac{1}{m}\sum_i x_i, \quad \sigma_B^2 = \frac{1}{m}\sum_i(x_i - \mu_B)^2, \quad \hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \varepsilon}}, \quad y_i = \gamma\hat{x}_i + \beta$$

The learnable **scale** $\gamma$ and **shift** $\beta$ let the network undo the normalisation where useful. During training, the layer also keeps **running averages** of the mean and variance (for example $\mu_{\text{run}} \leftarrow 0.9\mu_{\text{run}} + 0.1\mu_B$); at **inference**, it uses these running statistics, so a prediction does not depend on which other examples are in the batch. Batch norm allows higher learning rates, makes training less sensitive to initialisation, and adds mild regularisation, because each example's normalisation depends on its random batch-mates. It works poorly with very small batches.

**Layer normalisation** normalises across the features of each single example instead of across the batch, so it behaves identically in training and inference and does not depend on batch size; it is the standard in Transformers and recurrent networks. Group and instance normalisation are other variants.

### Early stopping

Track validation loss during training, keep the best checkpoint, and stop when validation loss has not improved for a set number of epochs (the **patience**). Early stopping limits how far the weights can travel from their small initial values, acting like a regulariser, and saves computation.

### Data augmentation and label smoothing

**Data augmentation** creates new training examples by label-preserving transformations: for images, flips, crops, rotations, colour changes, and erasing patches (cutout); mixing images and labels (mixup); for audio and text, noise, speed changes, or paraphrases. It encodes knowledge about which changes should not alter the answer. **Label smoothing** replaces one-hot targets with slightly softened ones (such as 0.9 for the true class and the rest spread over others), discouraging over-confident predictions.

## Worked examples

### Example 1: Dropout, batch normalisation, and weight decay in numbers

The program applies inverted dropout to eight activations, checks that the expected sum is preserved, normalises a mini-batch of four examples with three features, tracks running means, and compares an SGD step with and without weight decay.

```python
import random

random.seed(4)

# Inverted dropout with keep probability 0.5
activations = [0.8, 1.2, 0.5, 2.0, 0.9, 1.5, 0.3, 1.1]
keep = 0.5
mask = [1 if random.random() < keep else 0 for _ in activations]
dropped = [a * m / keep for a, m in zip(activations, mask)]
print("mask:   ", mask)
print("output: ", [round(d, 2) for d in dropped])
sums = []
for _ in range(20000):
    sums.append(sum(a / keep for a in activations if random.random() < keep))
print(f"original sum {sum(activations):.2f}; average sum after dropout over 20,000 trials {sum(sums) / len(sums):.2f}")

# Batch normalisation of a mini-batch: 4 examples x 3 features
batch = [[1.0, 50.0, -3.0], [2.0, 60.0, -1.0], [3.0, 55.0, 1.0], [6.0, 75.0, 3.0]]
eps, gamma, beta = 1e-5, [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]
means = [sum(col) / len(col) for col in zip(*batch)]
variances = [sum((v - m) ** 2 for v in col) / len(col) for col, m in zip(zip(*batch), means)]
normed = [[g * (v - m) / (var + eps) ** 0.5 + b for v, m, var, g, b in zip(row, means, variances, gamma, beta)]
          for row in batch]
print("batch means:", means, " variances:", [round(v, 2) for v in variances])
for row in normed:
    print("  normalised:", [f"{v:+.3f}" for v in row])

running_mean = [0.0, 0.0, 0.0]
for _ in range(3):                                   # three training steps with momentum 0.1
    running_mean = [0.9 * r + 0.1 * m for r, m in zip(running_mean, means)]
print("running means used at inference after 3 steps:", [round(r, 3) for r in running_mean])

# Weight decay: one SGD step with and without an L2 penalty
w, g, lr, lam = 2.0, 0.3, 0.1, 0.01
print(f"plain step: {w - lr * g:.4f}; with weight decay: {w - lr * (g + lam * w):.4f}")
```

Output:

```text
mask:    [1, 1, 1, 1, 1, 1, 0, 0]
output:  [1.6, 2.4, 1.0, 4.0, 1.8, 3.0, 0.0, 0.0]
original sum 8.30; average sum after dropout over 20,000 trials 8.33
batch means: [3.0, 60.0, 0.0]  variances: [3.5, 87.5, 5.0]
  normalised: ['-1.069', '-1.069', '-1.342']
  normalised: ['-0.535', '+0.000', '-0.447']
  normalised: ['+0.000', '-0.535', '+0.447']
  normalised: ['+1.604', '+1.604', '+1.342']
running means used at inference after 3 steps: [0.813, 16.26, 0.0]
plain step: 1.9700; with weight decay: 1.9680
```

In this draw, six of the eight units survive, and each surviving activation is doubled (divided by the keep probability 0.5). Any single draw changes the total, but averaged over 20,000 random masks the sum is 8.33 against the original 8.30: inverted dropout preserves the expected activation, so no rescaling is needed at inference. Batch normalisation maps each feature column to mean 0 and variance 1 regardless of its original scale: the second feature, in the 50s to 70s, and the first, in single digits, end up comparable. The running means after three steps (0.813 and 16.26, against batch means of 3 and 60) show why running statistics need many steps to warm up. Weight decay makes the step slightly larger, from 1.9700 to 1.9680, by also pulling the weight towards zero.

### Example 2: Batch normalisation and dropout by hand

One feature has values 2, 4, 6, 8 in a mini-batch. The mean is 5 and the variance is $(9 + 1 + 1 + 9)/4 = 5$, so the standard deviation is about 2.236 and the normalised values are

$$\hat{x} = (-1.342,\ -0.447,\ 0.447,\ 1.342)$$

With learned $\gamma = 2$ and $\beta = 1$, the outputs are $2\hat{x} + 1 = (-1.683,\ 0.106,\ 1.894,\ 3.683)$.

**Dropout with keep probability 0.8:** an activation of 2.0 becomes $2.0/0.8 = 2.5$ with probability 0.8 and 0 with probability 0.2. Its expected value is $0.8 \times 2.5 = 2.0$, unchanged.

**Weight decay:** with $\eta = 0.01$ and $\lambda = 0.0005$, each step multiplies the weights by $1 - \eta\lambda = 0.999995$ before the gradient update.

## Applications

- **Image classification:** augmentation, weight decay, and batch normalisation are standard in CNNs.
- **Transformers and language models:** dropout, layer normalisation, weight decay (AdamW), and label smoothing.
- **Small datasets:** heavy augmentation and early stopping prevent memorisation.
- **Medical imaging:** augmentation simulating scanner variation.
- **Uncertainty estimation:** Monte Carlo dropout for risk-aware decisions.

## Common mistakes

- **Leaving dropout or batch-norm training mode on at inference.** Switch the model to evaluation mode.
- **Scaling at test time with inverted dropout.** Inverted dropout already scales during training.
- **Using batch norm with tiny batches.** Statistics become noisy; use layer or group normalisation.
- **Augmenting in ways that change the label.** Flipping a "6" can make it a "9", and vertical flips are wrong for street scenes.
- **Tuning early stopping on the test set.** Use a validation set.

## Revision notes

- Weight decay: $\mathbf{w} \leftarrow (1 - \eta\lambda)\mathbf{w} - \eta\mathbf{g}$; decoupled in AdamW.
- Dropout: zero units with probability $p$ during training; inverted dropout divides by $q = 1 - p$; off at inference.
- Batch norm: normalise per feature over the batch, then $\gamma\hat{x} + \beta$; running statistics at inference.
- Layer norm: normalise per example over features; standard in Transformers.
- Early stopping with patience and best checkpoints.
- Data augmentation and label smoothing encode invariances and reduce over-confidence.

## Practice questions

:::question basic
Why does inverted dropout divide kept activations by the keep probability during training?
:::answer
So that the expected value of every activation during training equals its value at inference, when no units are dropped. Then the network can be used at test time without any rescaling.
:::

:::question basic
How does batch normalisation behave differently during training and inference?
:::answer
During training, it normalises with the mean and variance of the current mini-batch and updates running averages of these statistics. During inference, it uses the stored running averages, so predictions are deterministic and do not depend on the other examples in the batch.
:::

:::question intermediate
With learning rate 0.1 and weight decay 0.01, by what factor does weight decay shrink the weights each step, and what is the effect after 100 steps if gradients are zero?
:::answer
Each step multiplies the weights by $1 - 0.1 \times 0.01 = 0.999$. After 100 steps with zero gradient, the weights are multiplied by $0.999^{100} \approx 0.905$, a shrinkage of about 9.5%.
:::

:::question intermediate
Compare batch normalisation and layer normalisation, and explain why Transformers use layer normalisation.
:::answer
Batch normalisation computes statistics for each feature across the examples in a mini-batch, so it depends on batch size and composition and needs running averages for inference. Layer normalisation computes statistics across the features of each example separately, so it is independent of the batch and identical in training and inference. Transformers process variable-length sequences, often with small or uneven batches, so layer normalisation is more stable and simpler there.
:::

:::question advanced
Explain why dropout can be viewed as training an ensemble, and why this helps generalisation.
:::answer
Each random dropout mask selects a different thinned subnetwork, and all these subnetworks share weights; training with dropout therefore trains an enormous family of networks at once, each on different mini-batches. At inference, using the full network with scaled weights approximates averaging the predictions of all these subnetworks. Like any ensemble, the average has lower variance than its members, and because no unit can rely on specific other units being present, the network learns redundant, more robust features instead of fragile co-adaptations that fit noise.
:::

## Further learning

- **Next:** *Convolutional Layers & Spatial Invariance* builds networks specialised for images.
- **Related:** *L1/L2 Regularization & Bias-Variance* in Machine Learning explains the trade-off these methods manage.
