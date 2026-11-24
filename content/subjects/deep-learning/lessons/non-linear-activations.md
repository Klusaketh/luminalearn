---
lesson: non-linear-activations
title: Non-Linear Activations & Gradient Flow
summary: The activation functions used in neural networks (sigmoid, tanh, ReLU, leaky ReLU, GELU, and softmax), their derivatives and saturation behaviour, vanishing and exploding gradients, dying ReLUs, and initialisation schemes that keep signals stable.
minutes: 35
type: theory
objectives:
  - Compute common activation functions and their derivatives and describe their ranges and saturation behaviour
  - Explain vanishing and exploding gradients through the chain rule and why ReLU-family activations help
  - Choose activations for hidden and output layers and match them with Xavier or He initialisation
review: ai-draft
---
## Introduction

The activation function is the small non-linear twist inside every neuron, and its shape decides whether a deep network can learn at all. In the 1990s, deep networks with sigmoid activations barely trained, because gradients shrank to nothing on their way back through the layers. The switch to the rectified linear unit (ReLU), together with better initialisation, was one of the simple changes that made deep learning work around 2010–2012. This lesson compares the main activations and explains how they affect the flow of gradients.

**Before you start:** you should know derivatives and the chain rule from *Derivatives & The Chain Rule*, and the MLP from *Multilayer Perceptron & Matrix Algebra*.

## Core theory

### Sigmoid and tanh

- **Sigmoid:** $\sigma(x) = \frac{1}{1 + e^{-x}}$, range $(0, 1)$, derivative $\sigma'(x) = \sigma(x)(1 - \sigma(x))$, at most 0.25 (at $x = 0$). For large $|x|$ it **saturates**: the output is nearly flat, so the gradient is nearly 0. Its outputs are always positive (not zero-centred), which makes optimisation zig-zag. Today it is used for gates and binary output probabilities.
- **Tanh:** range $(-1, 1)$, zero-centred, derivative $1 - \tanh^2(x)$, at most 1. Better than sigmoid in hidden layers but still saturates.

### The ReLU family

- **ReLU:** $\max(0, x)$, with derivative 1 for $x > 0$ and 0 for $x < 0$. It does not saturate for positive inputs, is extremely cheap, and produces sparse activations. Its weakness is **dying ReLUs**: a unit whose input is negative for every example outputs 0 and receives zero gradient, so it can never recover (for example after a large update pushes its bias very negative).
- **Leaky ReLU:** $x$ for $x > 0$ and $0.01x$ otherwise, so negative inputs still get a small gradient; **PReLU** learns that slope, and **ELU** uses a smooth exponential curve for negatives.
- **GELU:** $x\,\Phi(x)$, where $\Phi$ is the standard normal CDF: a smooth, slightly non-monotonic version of ReLU, used in Transformers such as BERT and GPT. **SiLU** (Swish), $x\,\sigma(x)$, is similar.

### Softmax for outputs

Softmax turns a vector of scores (logits) into probabilities: $p_k = \frac{e^{z_k}}{\sum_j e^{z_j}}$. Adding a constant to every logit leaves the output unchanged, so implementations subtract the maximum logit first to avoid overflow.

### Vanishing and exploding gradients

Backpropagation multiplies local derivatives layer by layer. For a chain of $L$ layers, the gradient reaching the first layer contains a product like $\prod_{l=1}^{L}\varphi'(z_l)\,w_l$. If these factors are typically below 1, the product shrinks exponentially (**vanishing gradients**): early layers barely learn. If they are above 1, it grows exponentially (**exploding gradients**): training becomes unstable. With sigmoid, each factor $\sigma' \le 0.25$, so even in the best case, 10 layers shrink gradients by $0.25^{10} \approx 10^{-6}$.

### Keeping signals stable: initialisation

Weights should be scaled so that activations and gradients keep roughly the same variance from layer to layer:

- **Xavier (Glorot) initialisation** for tanh and sigmoid: variance $\frac{2}{n_{\text{in}} + n_{\text{out}}}$.
- **He (Kaiming) initialisation** for ReLU: variance $\frac{2}{n_{\text{in}}}$; the factor 2 compensates for ReLU zeroing about half of its inputs.

Normalisation layers, residual connections, and gradient clipping further protect gradient flow in very deep networks.

## Worked examples

### Example 1: Activations, derivatives, and gradients through depth

The program tabulates each activation and its derivative at −2, 0, and 2, then multiplies the derivatives through chains of 5, 10, and 20 layers (with weights of 1 and starting value 0.5), and computes a softmax.

```python
import math


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


ACTS = {
    "sigmoid": (sigmoid, lambda x: sigmoid(x) * (1 - sigmoid(x))),
    "tanh": (math.tanh, lambda x: 1 - math.tanh(x) ** 2),
    "ReLU": (lambda x: max(0.0, x), lambda x: 1.0 if x > 0 else 0.0),
    "leaky ReLU": (lambda x: x if x > 0 else 0.01 * x, lambda x: 1.0 if x > 0 else 0.01),
    "GELU": (lambda x: x * 0.5 * (1 + math.erf(x / math.sqrt(2))),
             lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2))) + x * math.exp(-x * x / 2) / math.sqrt(2 * math.pi)),
}
labels = "".join(f"{'f(%+d)' % x:>8} {'df(%+d)' % x:>8}" for x in (-2, 0, 2))
print(" " * 11 + labels)
for name, (f, df) in ACTS.items():
    print(f"{name:11}" + "".join(f"{f(x):8.3f} {df(x):8.3f}" for x in (-2, 0, 2)))

# Gradient reaching the first layer of a deep chain (each layer: h = act(h), weight 1)
print("gradient factor through depth (input 0.5):")
for name in ("sigmoid", "tanh", "ReLU"):
    f, df = ACTS[name]
    row = []
    for depth in (5, 10, 20):
        h, grad = 0.5, 1.0
        for _ in range(depth):
            grad *= df(h)
            h = f(h)
        row.append(f"depth {depth:2}: {grad:.2e}")
    print(f"  {name:8} " + "   ".join(row))

logits = [2.0, 1.0, 0.1]
exps = [math.exp(z - max(logits)) for z in logits]       # subtract the max for stability
print("softmax of", logits, "=", [round(e / sum(exps), 3) for e in exps])
```

Output:

```text
              f(-2)   df(-2)   f(+0)   df(+0)   f(+2)   df(+2)
sigmoid       0.119    0.105   0.500    0.250   0.881    0.105
tanh         -0.964    0.071   0.000    1.000   0.964    0.071
ReLU          0.000    0.000   0.000    0.000   2.000    1.000
leaky ReLU   -0.020    0.010   0.000    0.010   2.000    1.000
GELU         -0.046   -0.085   0.000    0.500   1.954    1.085
gradient factor through depth (input 0.5):
  sigmoid  depth  5: 6.08e-04   depth 10: 3.48e-07   depth 20: 1.14e-13
  tanh     depth  5: 3.93e-01   depth 10: 2.23e-01   depth 20: 1.07e-01
  ReLU     depth  5: 1.00e+00   depth 10: 1.00e+00   depth 20: 1.00e+00
softmax of [2.0, 1.0, 0.1] = [0.659, 0.242, 0.099]
```

The sigmoid's derivative is at most 0.25 and drops to 0.105 at ±2; tanh reaches 1 at 0. ReLU passes gradient 1 for positive inputs and 0 for negative ones, while leaky ReLU keeps 0.01. GELU is slightly negative at −2 with a negative derivative: unlike ReLU, it is not monotonic. Through depth, the sigmoid chain's gradient collapses to $3.5 \times 10^{-7}$ after 10 layers and $10^{-13}$ after 20, the vanishing-gradient problem in action. Tanh decays slowly here because repeated tanh pushes the value towards 0, where its slope is near 1, although with saturated inputs it vanishes too. ReLU passes the gradient through unchanged. The softmax of $(2, 1, 0.1)$ gives probabilities $(0.659, 0.242, 0.099)$.

### Example 2: Numbers by hand

- $\sigma(0) = 0.5$ and $\sigma'(0) = 0.5 \times 0.5 = 0.25$; ten sigmoid layers at their best still give $0.25^{10} \approx 9.5 \times 10^{-7}$.
- $\tanh(1) \approx 0.762$, so $\tanh'(1) = 1 - 0.762^2 \approx 0.420$.
- **He initialisation** for a layer with 512 inputs: standard deviation $\sqrt{2/512} = 0.0625$.
- **Xavier initialisation** for a 256 → 128 layer: variance $2/(256 + 128) \approx 0.0052$, standard deviation about 0.072.
- **A dying ReLU:** if a unit's bias becomes −10 while its weighted inputs never exceed 5, then $z < 0$ for every example, its output is always 0, and its gradient is always 0, so gradient descent can never revive it. A leaky ReLU would still pass a gradient of 0.01.

## Applications

- **Hidden layers of CNNs and MLPs:** ReLU and its variants are the default.
- **Transformers:** GELU or SiLU in the feed-forward blocks.
- **Gates in LSTMs and GRUs:** sigmoid outputs between 0 and 1 act as soft switches.
- **Output layers:** sigmoid for binary and multi-label tasks, softmax for multi-class.
- **Bounded outputs:** tanh for values in $(-1, 1)$, such as image pixels in GAN generators.

## Common mistakes

- **Using sigmoid in deep hidden layers.** It saturates and causes vanishing gradients.
- **Applying softmax and then a cross-entropy that expects logits.** Many libraries combine them; applying softmax twice gives wrong gradients.
- **Ignoring dead ReLUs.** Very large learning rates can kill many units; monitor activation statistics.
- **Mismatching initialisation and activation.** Use He for ReLU and Xavier for tanh or sigmoid.
- **Computing softmax without subtracting the maximum.** Large logits overflow.

## Revision notes

- Sigmoid: $(0, 1)$, $\sigma' \le 0.25$, saturates, not zero-centred; tanh: $(-1, 1)$, zero-centred, saturates.
- ReLU: $\max(0, x)$, gradient 1 for positive inputs, cheap; risk of dying units; leaky ReLU, PReLU, ELU fix this.
- GELU $x\Phi(x)$ and SiLU $x\sigma(x)$ in Transformers.
- Softmax for multi-class outputs; subtract the max for stability.
- Vanishing/exploding gradients come from products of factors below or above 1 across layers.
- Xavier: $\text{Var} = 2/(n_{\text{in}} + n_{\text{out}})$; He: $\text{Var} = 2/n_{\text{in}}$.

## Practice questions

:::question basic
Compute $\sigma(0)$ and $\sigma'(0)$ for the sigmoid function.
:::answer
$\sigma(0) = 1/(1 + 1) = 0.5$ and $\sigma'(0) = \sigma(0)(1 - \sigma(0)) = 0.25$, the largest value the sigmoid's derivative ever takes.
:::

:::question basic
Why does ReLU reduce the vanishing-gradient problem compared with sigmoid?
:::answer
For positive inputs, ReLU's derivative is exactly 1, so gradients pass through active units without shrinking, however many layers there are. The sigmoid's derivative is at most 0.25 and near 0 when saturated, so its gradients shrink geometrically with depth.
:::

:::question intermediate
What is a dying ReLU, and name two ways to prevent it.
:::answer
A ReLU unit whose pre-activation is negative for every input always outputs 0 and receives zero gradient, so it never learns again. Prevention: use a leaky ReLU, PReLU, or ELU so negative inputs still pass some gradient; use sensible learning rates and He initialisation; normalisation layers also help keep pre-activations in a healthy range.
:::

:::question intermediate
Compute the softmax of $(1, 1, 1)$ and of $(11, 11, 11)$. What property does this illustrate?
:::answer
Both give $(1/3, 1/3, 1/3)$. Adding the same constant to every logit does not change the softmax, which is why implementations safely subtract the largest logit before exponentiating.
:::

:::question advanced
Explain the reasoning behind He initialisation for ReLU networks.
:::answer
For a layer $z = \sum_{i=1}^{n_{\text{in}}} w_ix_i$ with independent zero-mean weights, $\text{Var}(z) = n_{\text{in}}\text{Var}(w)\,\mathbb{E}[x^2]$. A ReLU zeroes roughly half of its inputs, so $\mathbb{E}[x^2]$ is about half the variance of the previous layer's pre-activations. Choosing $\text{Var}(w) = 2/n_{\text{in}}$ cancels both effects, keeping the variance of pre-activations roughly constant from layer to layer, so signals neither vanish nor explode in the forward pass, and similar reasoning applies to gradients in the backward pass.
:::

## Further learning

- **Next:** *Loss Functions & the Training Loop* puts activations to work in training.
- **Related:** *Derivatives & The Chain Rule* in Calculus explains why derivatives multiply through layers.
