---
lesson: mlp-matrix-algebra
title: Multilayer Perceptron & Matrix Algebra
summary: Artificial neurons and the perceptron, why a single layer cannot learn XOR, multilayer perceptrons written as matrix operations on batches, shapes and parameter counts, why non-linear activations are essential, output layers, and the universal approximation theorem.
minutes: 40
type: theory
objectives:
  - Write the forward pass of a multilayer perceptron as matrix operations on a batch and track the shape of every tensor
  - Count the parameters of dense layers and networks
  - Explain why non-linear activations are needed, how a hidden layer solves XOR, and what the universal approximation theorem does and does not promise
review: ai-draft
---
## Introduction

Deep learning powers image recognition, speech assistants, translation, and large language models, yet its basic building block is simple: a neuron that computes a weighted sum and applies a non-linear function. Stacking neurons into layers and layers into networks produces the **multilayer perceptron** (MLP), the original deep network and still a component of every modern architecture, including the feed-forward blocks inside Transformers. Writing networks as matrix operations is what makes them fast on GPUs and is the language used by every deep-learning framework.

**Before you start:** you should know matrix multiplication from *Vector Spaces & Matrix Multiplication* and logistic regression from *Logistic Regression & Decision Trees*.

## Core theory

### The artificial neuron

A neuron receives inputs $x_1, \dots, x_d$, computes a weighted sum plus a bias, and applies an **activation function** $\varphi$:

$$z = \mathbf{w}^\top\mathbf{x} + b, \qquad a = \varphi(z)$$

Rosenblatt's **perceptron** (1958) used a step function and a simple learning rule. A single perceptron draws one straight line (a hyperplane) through the input space, so it can only solve **linearly separable** problems. XOR, which outputs 1 when exactly one input is 1, is not linearly separable: no single line separates (0, 1) and (1, 0) from (0, 0) and (1, 1). Minsky and Papert's 1969 analysis of this limitation contributed to the first AI winter.

### Layers as matrix operations

A **dense** (fully connected) layer applies many neurons to the same input at once. For a batch of $B$ examples stored as rows of $X$ (shape $B \times d_{\text{in}}$):

$$H = \varphi(XW + \mathbf{b})$$

where $W$ has shape $d_{\text{in}} \times d_{\text{out}}$ (one column per neuron) and the bias vector $\mathbf{b}$ (length $d_{\text{out}}$) is added to every row (broadcasting). The output $H$ has shape $B \times d_{\text{out}}$. A dense layer has $d_{\text{in}} \cdot d_{\text{out}} + d_{\text{out}}$ parameters and costs about $B \cdot d_{\text{in}} \cdot d_{\text{out}}$ multiply-adds, exactly the kind of work GPUs do well. (Some texts use column vectors and $W\mathbf{x}$ with $W$ of shape $d_{\text{out}} \times d_{\text{in}}$: the same thing transposed.)

### The multilayer perceptron

An MLP chains layers: input → one or more **hidden layers** → output layer. The number of layers is the **depth** and the number of units per layer the **width**. The output layer matches the task:

- **Regression:** linear outputs (no activation).
- **Binary classification:** one sigmoid unit giving a probability.
- **Multi-class classification:** a **softmax** layer giving a probability distribution over classes.

### Why non-linearity is essential

Without activation functions, layers collapse: $(XW_1)W_2 = X(W_1W_2)$, a single linear layer, however many layers you stack. The non-linearity between layers lets each layer bend the representation, so later layers can draw straight boundaries in a transformed space. That is how a hidden layer solves XOR: hidden units compute OR and AND, and the output computes "OR but not AND".

### The universal approximation theorem

An MLP with **one hidden layer**, enough hidden units, and a suitable non-linear activation can approximate any continuous function on a bounded region to any desired accuracy. The theorem guarantees existence, not practicality: the required width can be enormous, and it says nothing about whether training will find the weights. In practice, **depth** is far more efficient: deep networks build hierarchical features (edges, then shapes, then objects) and represent many functions with exponentially fewer units than shallow ones.

## Worked examples

### Example 1: XOR, collapsing layers, and parameter counts

The program solves XOR with a hand-designed 2-2-1 network using step activations, shows that two linear layers equal one, and counts the parameters of a typical MLP for 28×28 images.

```python
def matmul(A, B):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*B)] for row in A]


def add_bias(Z, b):
    return [[z + bi for z, bi in zip(row, b)] for row in Z]


def step(Z):
    return [[1 if z > 0 else 0 for z in row] for row in Z]


# A 2-2-1 network that computes XOR with hand-chosen weights
X = [[0, 0], [0, 1], [1, 0], [1, 1]]          # batch of 4 inputs, shape (4, 2)
W1 = [[1, 1], [1, 1]]                         # shape (2, 2): column 0 -> OR unit, column 1 -> AND unit
b1 = [-0.5, -1.5]
W2 = [[1], [-1]]                              # shape (2, 1): OR and not AND
b2 = [-0.5]
H = step(add_bias(matmul(X, W1), b1))         # shape (4, 2)
Y = step(add_bias(matmul(H, W2), b2))         # shape (4, 1)
for x, h, y in zip(X, H, Y):
    print(f"x = {x} -> hidden (OR, AND) = {h} -> output {y[0]}")

# Without a non-linearity, two layers collapse into one
A1 = [[2, -1], [0, 3]]
A2 = [[1, 4], [-2, 1]]
x = [[1, 2]]
two_layers = matmul(matmul(x, A1), A2)
one_layer = matmul(x, matmul(A1, A2))
print(f"two linear layers: {two_layers[0]}, single merged layer: {one_layer[0]}")

# Parameter count of a 784-128-64-10 MLP for 28x28 images
sizes = [784, 128, 64, 10]
total = 0
for n_in, n_out in zip(sizes, sizes[1:]):
    params = n_in * n_out + n_out
    total += params
    print(f"layer {n_in:3} -> {n_out:3}: weights {n_in * n_out:6,} + biases {n_out:3} = {params:7,}")
print(f"total parameters: {total:,}")
```

Output:

```text
x = [0, 0] -> hidden (OR, AND) = [0, 0] -> output 0
x = [0, 1] -> hidden (OR, AND) = [1, 0] -> output 1
x = [1, 0] -> hidden (OR, AND) = [1, 0] -> output 1
x = [1, 1] -> hidden (OR, AND) = [1, 1] -> output 0
two linear layers: [-8, 13], single merged layer: [-8, 13]
layer 784 -> 128: weights 100,352 + biases 128 = 100,480
layer 128 ->  64: weights  8,192 + biases  64 =   8,256
layer  64 ->  10: weights    640 + biases  10 =     650
total parameters: 109,386
```

The first hidden unit fires when at least one input is 1 (OR); the second only when both are (AND). The output fires for "OR and not AND", which is XOR, something no single-layer network can compute. The second part confirms the collapse: multiplying by $A_1$ then $A_2$ gives the same result, $(-8, 13)$, as multiplying once by the merged matrix $A_1A_2$. The parameter count shows where an MLP's weights live: almost all of its 109,386 parameters are in the first layer, which connects 784 pixels to 128 units.

### Example 2: Shapes and a single neuron by hand

A batch of 32 images flows through the 784-128-64-10 network:

| Tensor | Shape |
| :--- | :--- |
| Input $X$ | $32 \times 784$ |
| $W_1$, $\mathbf{b}_1$ | $784 \times 128$, $128$ |
| Hidden 1 | $32 \times 128$ |
| Hidden 2 | $32 \times 64$ |
| Output (softmax) | $32 \times 10$ |

The first layer alone needs $32 \times 784 \times 128 = 3{,}211{,}264$ multiply-adds for the batch.

One neuron with $\mathbf{x} = (2, -1)$, $\mathbf{w} = (0.5, 1.5)$, and $b = 0.25$: $z = 1 - 1.5 + 0.25 = -0.25$. With ReLU, the output is $\max(0, -0.25) = 0$; with a sigmoid, it is $1/(1 + e^{0.25}) \approx 0.438$.

## Applications

- **Tabular data:** MLPs for prediction from structured features.
- **Classification heads:** the final layers of image and text models are MLPs.
- **Transformers:** every Transformer block contains a position-wise MLP.
- **Recommendation systems:** MLPs combine user and item embeddings.
- **Function approximation:** value and policy networks in reinforcement learning.

## Common mistakes

- **Mismatched shapes.** Track $(B, d_{\text{in}}) \times (d_{\text{in}}, d_{\text{out}})$ at every layer.
- **Forgetting activations between layers.** The network then collapses to a linear model.
- **Using the wrong output layer.** Softmax for exclusive classes, sigmoid for independent binary labels, linear for regression.
- **Reading the universal approximation theorem as a practical guarantee.** It does not say the network is small or trainable.
- **Confusing the weight-matrix convention.** Know whether your framework computes $XW$ or $W\mathbf{x}$.

## Revision notes

- Neuron: $a = \varphi(\mathbf{w}^\top\mathbf{x} + b)$; a single layer separates only linearly separable data.
- Dense layer on a batch: $H = \varphi(XW + \mathbf{b})$; shapes $(B, d_{\text{in}}) \to (B, d_{\text{out}})$.
- Parameters per dense layer: $d_{\text{in}}d_{\text{out}} + d_{\text{out}}$.
- Without non-linearity, stacked layers equal one linear layer.
- Output layers: linear (regression), sigmoid (binary), softmax (multi-class).
- Universal approximation: one wide hidden layer can approximate any continuous function; depth is more efficient.

## Practice questions

:::question basic
How many parameters does a dense layer from 100 inputs to 50 outputs have?
:::answer
$100 \times 50 = 5{,}000$ weights plus 50 biases, giving 5,050 parameters.
:::

:::question basic
Why can a single perceptron not compute XOR?
:::answer
A perceptron's decision boundary is a single straight line. XOR's positive points, (0, 1) and (1, 0), lie on one diagonal and its negative points, (0, 0) and (1, 1), on the other, so no straight line separates them: the problem is not linearly separable.
:::

:::question intermediate
A batch $X$ has shape $64 \times 20$ and a layer has weights of shape $20 \times 8$. What are the shapes of the bias and the output?
:::answer
The bias has length 8 (one per output unit) and is broadcast across the batch; the output $XW + \mathbf{b}$ has shape $64 \times 8$.
:::

:::question intermediate
Show that two linear layers $y = W_2(W_1\mathbf{x} + \mathbf{b}_1) + \mathbf{b}_2$ are equivalent to a single linear layer.
:::answer
Expanding gives $y = (W_2W_1)\mathbf{x} + (W_2\mathbf{b}_1 + \mathbf{b}_2)$, which is a single linear layer with weight matrix $W_2W_1$ and bias $W_2\mathbf{b}_1 + \mathbf{b}_2$. Without a non-linearity, extra layers add no expressive power.
:::

:::question advanced
State the universal approximation theorem and explain why deep networks are still preferred over very wide shallow ones.
:::answer
A feed-forward network with one hidden layer of sufficiently many units and a non-polynomial activation can approximate any continuous function on a compact set to arbitrary accuracy. But the theorem gives no bound on the number of units, which can be exponentially large, and no guarantee that training finds the weights. Deep networks compose simple functions into hierarchical features, so many functions that need exponentially many units in one hidden layer can be represented compactly with depth; deep networks also generalise better in practice on structured data such as images, audio, and text.
:::

## Further learning

- **Next:** *Non-Linear Activations & Gradient Flow* compares activation functions.
- **Related:** *Vector Spaces & Matrix Multiplication* in Linear Algebra covers the matrix operations used here.
