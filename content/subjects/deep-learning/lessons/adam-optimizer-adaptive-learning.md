---
lesson: adam-optimizer-adaptive-learning
title: Adam Optimizer & Adaptive Learning Rates
summary: Optimisers for deep learning: stochastic gradient descent and its limits on ill-conditioned problems, momentum, AdaGrad, RMSProp, and Adam with bias correction, AdamW's decoupled weight decay, and learning-rate schedules such as warm-up and cosine decay.
minutes: 45
type: theory
objectives:
  - Explain why plain SGD is slow on ill-conditioned problems and how momentum helps
  - Apply the AdaGrad, RMSProp, and Adam update rules, including Adam's bias correction
  - Choose learning-rate schedules and explain the difference between Adam with L2 regularisation and AdamW
review: ai-draft
---
## Introduction

Backpropagation tells us the gradient; the **optimiser** decides what to do with it. Plain gradient descent takes a step proportional to the gradient, which works well on round, bowl-shaped losses but crawls along long, narrow valleys, which are common in deep networks where different parameters have very different sensitivities. Momentum and adaptive methods such as RMSProp and **Adam** fix this, and Adam has become the default optimiser for training Transformers and many other models.

**Before you start:** you should know gradient descent from *Linear Regression & Gradient Descent* and the training loop from *Loss Functions & the Training Loop*.

## Core theory

### Stochastic gradient descent and its limits

SGD updates $\theta \leftarrow \theta - \eta\,\mathbf{g}$ using the gradient $\mathbf{g}$ of a mini-batch loss. The **learning rate** $\eta$ is the most important hyperparameter. On a quadratic loss, stability requires $\eta < 2/\lambda_{\max}$, where $\lambda_{\max}$ is the largest curvature (Hessian eigenvalue). But progress along the flattest direction is proportional to $\eta\lambda_{\min}$, so the number of steps grows with the **condition number** $\kappa = \lambda_{\max}/\lambda_{\min}$. In a narrow valley, SGD bounces between the steep walls while inching along the valley floor.

### Momentum

Momentum keeps a running **velocity**:

$$\mathbf{v} \leftarrow \beta\mathbf{v} + \mathbf{g}, \qquad \theta \leftarrow \theta - \eta\mathbf{v}$$

with $\beta$ typically 0.9. In directions where the gradient is consistent, velocity builds up (towards $\mathbf{g}/(1 - \beta)$, ten times the gradient for $\beta = 0.9$); in directions where it oscillates, successive gradients cancel. **Nesterov momentum** evaluates the gradient at the look-ahead position, which often converges a little faster.

### Adaptive learning rates

- **AdaGrad** divides each parameter's step by the square root of the sum of all its past squared gradients. Rarely updated parameters (such as embeddings of rare words) get larger steps. But the sum only grows, so learning rates decay towards zero.
- **RMSProp** uses an exponential moving average instead: $s \leftarrow \rho s + (1 - \rho)g^2$ and $\theta \leftarrow \theta - \eta\,g/(\sqrt{s} + \varepsilon)$, so the effective step adapts to the recent gradient scale of each parameter.

### Adam

Adam (Kingma and Ba, 2015) combines momentum with RMSProp-style scaling:

$$\mathbf{m} \leftarrow \beta_1\mathbf{m} + (1 - \beta_1)\mathbf{g}, \qquad \mathbf{v} \leftarrow \beta_2\mathbf{v} + (1 - \beta_2)\mathbf{g}^2$$

$$\hat{\mathbf{m}} = \frac{\mathbf{m}}{1 - \beta_1^t}, \qquad \hat{\mathbf{v}} = \frac{\mathbf{v}}{1 - \beta_2^t}, \qquad \theta \leftarrow \theta - \eta\frac{\hat{\mathbf{m}}}{\sqrt{\hat{\mathbf{v}}} + \varepsilon}$$

Because $\mathbf{m}$ and $\mathbf{v}$ start at zero, they are biased towards zero early in training; the **bias correction** divides that out. Default settings are $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\varepsilon = 10^{-8}$, and $\eta = 10^{-3}$. Each parameter's step is roughly $\eta$ times the ratio of its average gradient to its typical gradient size, which makes Adam largely insensitive to how the gradients are scaled.

### Weight decay: Adam versus AdamW

Adding an L2 penalty to the loss makes its gradient pass through Adam's per-parameter scaling, so parameters with large gradients are regularised less. **AdamW** (Loshchilov and Hutter) **decouples** weight decay, shrinking weights directly: $\theta \leftarrow \theta - \eta(\text{Adam step} + \lambda\theta)$. AdamW is the standard for Transformers.

### Learning-rate schedules

- **Step decay** divides the rate by a factor (such as 10) at set epochs.
- **Cosine annealing** lowers it smoothly along a cosine curve to near zero.
- **Warm-up** increases it linearly from near zero over the first steps, stabilising early training when Adam's statistics are unreliable and gradients are large; it is standard for Transformers.
- **One-cycle** schedules rise and then fall during training.

In practice, Adam or AdamW converges quickly with little tuning; well-tuned SGD with momentum sometimes generalises slightly better in computer vision.

## Worked examples

### Example 1: How optimisers cope with a narrow valley

The program minimises $f(x, y) = x^2 + \kappa y^2$ from $(5, 1)$ and counts steps until $f < 10^{-6}$. Larger $\kappa$ means a narrower valley (the condition number of the problem is $\kappa$).

```python
import math


def steps_to_converge(update, kappa, lr, limit=10000):
    """Minimise f(x, y) = x^2 + kappa * y^2 from (5, 1); count steps until f < 1e-6."""
    p, state = [5.0, 1.0], {}
    for t in range(1, limit + 1):
        g = [2 * p[0], 2 * kappa * p[1]]
        p = update(p, g, state, t, lr)
        f = p[0] ** 2 + kappa * p[1] ** 2
        if f < 1e-6:
            return str(t)
        if f > 1e12:
            return "diverged"
    return f">{limit}"


def sgd(p, g, s, t, lr):
    return [pi - lr * gi for pi, gi in zip(p, g)]


def momentum(p, g, s, t, lr, beta=0.9):
    s["v"] = [beta * v + gi for v, gi in zip(s.get("v", [0, 0]), g)]
    return [pi - lr * v for pi, v in zip(p, s["v"])]


def rmsprop(p, g, s, t, lr, rho=0.9, eps=1e-8):
    s["sq"] = [rho * q + (1 - rho) * gi * gi for q, gi in zip(s.get("sq", [0, 0]), g)]
    return [pi - lr * gi / (math.sqrt(q) + eps) for pi, gi, q in zip(p, g, s["sq"])]


def adam(p, g, s, t, lr, b1=0.9, b2=0.999, eps=1e-8):
    s["m"] = [b1 * m + (1 - b1) * gi for m, gi in zip(s.get("m", [0, 0]), g)]
    s["v"] = [b2 * v + (1 - b2) * gi * gi for v, gi in zip(s.get("v", [0, 0]), g)]
    m_hat = [m / (1 - b1 ** t) for m in s["m"]]          # bias correction
    v_hat = [v / (1 - b2 ** t) for v in s["v"]]
    return [pi - lr * mh / (math.sqrt(vh) + eps) for pi, mh, vh in zip(p, m_hat, v_hat)]


print("steps until f < 1e-6 on f = x^2 + kappa*y^2 (larger kappa = narrower valley)")
print(f"{'method':32} {'kappa=10':>9} {'kappa=100':>10} {'kappa=1000':>11}")
rows = [
    ("SGD, lr = 0.9/kappa", sgd, lambda k: 0.9 / k),
    ("SGD, lr = 1.05/kappa", sgd, lambda k: 1.05 / k),
    ("momentum 0.9, lr = 0.9/kappa", momentum, lambda k: 0.9 / k),
    ("RMSProp, lr = 0.1", rmsprop, lambda k: 0.1),
    ("Adam, lr = 0.1", adam, lambda k: 0.1),
]
for name, rule, lr in rows:
    print(f"{name:32} " + " ".join(f"{steps_to_converge(rule, k, lr(k)):>{w}}" for k, w in ((10, 9), (100, 10), (1000, 11))))

state = {}
first = adam([5.0, 1.0], [10.0, 2000.0], state, 1, 0.1)
print(f"Adam's first step with gradients (10, 2000): moves {5.0 - first[0]:.4f} and {1.0 - first[1]:.4f}")
```

Output:

```text
steps until f < 1e-6 on f = x^2 + kappa*y^2 (larger kappa = narrower valley)
method                            kappa=10  kappa=100  kappa=1000
SGD, lr = 0.9/kappa                     44        469        4728
SGD, lr = 1.05/kappa              diverged   diverged    diverged
momentum 0.9, lr = 0.9/kappa           133        160         384
RMSProp, lr = 0.1                   >10000     >10000      >10000
Adam, lr = 0.1                         178        181         187
Adam's first step with gradients (10, 2000): moves 0.1000 and 0.1000
```

SGD's step count grows in proportion to $\kappa$ (44, 469, 4,728) even with the learning rate at 90% of its stability limit, and just 5% above the limit it diverges at every $\kappa$. Momentum is much less sensitive (133, 160, 384). Adam needs about 180 steps whatever the conditioning, because it rescales each coordinate by its own gradient size; its very first step moves both coordinates by exactly the learning rate even though their gradients differ by a factor of 200. Plain RMSProp with a constant learning rate never reaches the tolerance: its steps stay about $\eta$ in size, so it hovers around the minimum. That is why adaptive optimisers are paired with decaying learning-rate schedules, and Adam's momentum averaging helps it settle. Note also that for the well-conditioned problem ($\kappa = 10$), plain SGD was fastest: no optimiser wins everywhere.

### Example 2: Adam's first steps and momentum by hand

**Adam, step 1,** with gradient $g = 10$: $m = 0.1 \times 10 = 1$, $v = 0.001 \times 100 = 0.1$. Bias correction: $\hat{m} = 1/(1 - 0.9) = 10$ and $\hat{v} = 0.1/(1 - 0.999) = 100$. Step $= \eta \times 10/\sqrt{100} = \eta$. With $g = 2000$, the same arithmetic gives $\hat{m} = 2000$, $\hat{v} = 4{,}000{,}000$, and again a step of $\eta$.

**Adam, step 2,** with the same gradient 10: $m = 0.9 \times 1 + 1 = 1.9$, $\hat{m} = 1.9/(1 - 0.81) = 10$; $v = 0.999 \times 0.1 + 0.1 = 0.1999$, $\hat{v} = 0.1999/(1 - 0.999^2) \approx 100$. The step is again $\eta$: with consistent gradients, Adam moves at a steady pace of $\eta$ per step.

**Momentum** with a constant gradient of 4 and $\beta = 0.9$: $v_1 = 4$, $v_2 = 0.9 \times 4 + 4 = 7.6$, $v_3 = 0.9 \times 7.6 + 4 = 10.84$, approaching $4/(1 - 0.9) = 40$: along a consistent slope, momentum eventually moves ten times faster than plain SGD.

## Applications

- **Transformers and large language models:** AdamW with warm-up and cosine decay.
- **Computer vision:** SGD with momentum and step or cosine schedules remains common.
- **Recommendation and NLP with sparse features:** AdaGrad-style adaptivity for rare features.
- **Reinforcement learning:** Adam for policy and value networks.
- **Fine-tuning:** small learning rates with short warm-ups.

## Common mistakes

- **Using one learning rate for every optimiser.** Adam's typical $\eta$ ($10^{-3}$) is far smaller than SGD's ($10^{-1}$ to $10^{-2}$).
- **Combining Adam with L2 loss penalties and expecting weight decay.** Use AdamW for decoupled decay.
- **Skipping warm-up on large Transformers.** Early instability can ruin training.
- **Never decaying the learning rate.** Constant steps hover around the minimum.
- **Assuming Adam always generalises best.** Compare with SGD plus momentum on your task.

## Revision notes

- SGD: $\theta \leftarrow \theta - \eta g$; stable only for $\eta < 2/\lambda_{\max}$; steps grow with the condition number.
- Momentum: $v \leftarrow \beta v + g$; damps oscillations, accelerates consistent directions.
- AdaGrad (sum of squares), RMSProp (moving average of squares): per-parameter step sizes.
- Adam: moving averages $m$ and $v$, bias correction $1/(1 - \beta^t)$, step $\eta\hat{m}/(\sqrt{\hat{v}} + \varepsilon)$; defaults 0.9, 0.999, $10^{-8}$, $10^{-3}$.
- AdamW decouples weight decay from the adaptive scaling.
- Schedules: step, cosine, warm-up, one-cycle.

## Practice questions

:::question basic
What do the parameters $\beta_1$ and $\beta_2$ control in Adam?
:::answer
$\beta_1$ (typically 0.9) sets how quickly the moving average of gradients (the momentum term $m$) forgets old gradients. $\beta_2$ (typically 0.999) does the same for the moving average of squared gradients $v$, which sets each parameter's step-size scaling.
:::

:::question basic
Why does Adam need bias correction?
:::answer
$m$ and $v$ are initialised to zero, so during the first steps they are weighted averages that include many zeros and are biased towards zero; $v$ especially, with $\beta_2 = 0.999$, would stay tiny for hundreds of steps. Dividing by $1 - \beta^t$ removes this bias, so early steps have the intended size.
:::

:::question intermediate
With momentum $\beta = 0.9$ and a constant gradient of 2, compute the velocity after three steps, starting from zero.
:::answer
$v_1 = 2$; $v_2 = 0.9 \times 2 + 2 = 3.8$; $v_3 = 0.9 \times 3.8 + 2 = 5.42$. It approaches $2/(1 - 0.9) = 20$.
:::

:::question intermediate
Why is learning-rate warm-up used when training Transformers?
:::answer
At the start of training, weights are random, gradients can be large and erratic, and Adam's second-moment estimates are based on very few steps, so full-size updates can push the model into a poor region or make training diverge. Increasing the learning rate gradually over the first few thousand steps keeps early updates small until the statistics and the model settle.
:::

:::question advanced
Explain why "Adam with L2 regularisation" and AdamW behave differently.
:::answer
With L2 regularisation, the penalty's gradient $\lambda\theta$ is added to the loss gradient and then divided by $\sqrt{\hat{v}}$ like everything else, so parameters with large historical gradients receive proportionally less shrinkage, and the effective regularisation depends on gradient statistics. AdamW applies weight decay separately, $\theta \leftarrow \theta - \eta\lambda\theta$, outside the adaptive scaling, so every parameter decays at the same relative rate, matching the original intent of weight decay. In practice AdamW generalises better and makes the decay strength easier to tune.
:::

## Further learning

- **Next:** *Regularization: Dropout, Batch Norm & Weight Decay* covers techniques that make training generalise.
- **Related:** *Linear Regression & Gradient Descent* in Machine Learning introduces gradient descent and learning rates.
