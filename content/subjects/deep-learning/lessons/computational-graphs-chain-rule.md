---
lesson: computational-graphs-chain-rule
title: Computational Graphs & Chain Rule
summary: How backpropagation works: computational graphs, the chain rule for single and multiple paths, local gradients of common operations, reverse-mode automatic differentiation, gradient accumulation at shared nodes, matrix gradients, and gradient checking with finite differences.
minutes: 50
type: theory
objectives:
  - Represent a computation as a graph and compute gradients by applying the chain rule backwards through it
  - Derive local gradients for addition, multiplication, max, tanh, and matrix multiplication, and accumulate gradients at shared nodes
  - Explain why reverse-mode differentiation suits neural networks and verify gradients with finite differences
review: ai-draft
---
## Introduction

Training a network with millions of parameters needs the derivative of the loss with respect to every one of them, at every step. Deriving these by hand is impossible, and estimating each numerically would be far too slow. **Backpropagation** solves this by breaking the computation into a graph of simple operations, each with an easy local derivative, and applying the chain rule backwards through the graph. Every deep-learning framework, from PyTorch to JAX, implements this as **automatic differentiation**.

**Before you start:** you should know the chain rule and partial derivatives from *Gradients, Jacobians & Hessians*.

## Core theory

### Computational graphs

A **computational graph** represents a calculation as nodes (operations or variables) connected by edges (values). For $f = \tanh(xy + z) \cdot x$, the graph has a multiplication node $xy$, an addition node, a tanh node, and a final multiplication. The **forward pass** evaluates the nodes in order, storing intermediate values.

### The chain rule on graphs

If $L$ depends on $x$ through an intermediate $u$, then $\frac{\partial L}{\partial x} = \frac{\partial L}{\partial u}\frac{\partial u}{\partial x}$. When $x$ influences $L$ along several paths, the contributions **add**:

$$\frac{\partial L}{\partial x} = \sum_{\text{paths}}\prod_{\text{edges on the path}}(\text{local derivative})$$

The **backward pass** starts with $\frac{\partial L}{\partial L} = 1$ and visits nodes in reverse topological order. Each node multiplies the gradient arriving from its output (the **upstream gradient**) by its **local gradient** and sends the result to its inputs. Where a value feeds several operations (**fan-out**), the gradients from each use are **accumulated** (summed).

### Local gradients of common operations

| Operation | Forward | Gradient sent to inputs |
| :--- | :--- | :--- |
| Add | $c = a + b$ | upstream to both $a$ and $b$ (a distributor) |
| Multiply | $c = ab$ | upstream $\times\, b$ to $a$, upstream $\times\, a$ to $b$ (a swapper) |
| Max | $c = \max(a, b)$ | upstream to the larger input, 0 to the other (a router) |
| Tanh | $c = \tanh(a)$ | upstream $\times\,(1 - c^2)$ |
| Sigmoid | $c = \sigma(a)$ | upstream $\times\, c(1 - c)$ |
| Matrix multiply | $Y = XW$ | $\frac{\partial L}{\partial W} = X^\top\frac{\partial L}{\partial Y}$, $\frac{\partial L}{\partial X} = \frac{\partial L}{\partial Y}W^\top$ |

A useful check: every gradient has the same shape as the quantity it belongs to.

### Reverse mode versus forward mode

**Reverse-mode** differentiation (backpropagation) computes the gradient of one output with respect to all inputs in a single backward pass, costing only a small constant factor more than the forward pass. Neural network training has exactly this shape: one scalar loss and millions of parameters. **Forward mode** propagates derivatives alongside values and is efficient when there are few inputs and many outputs. The price of reverse mode is **memory**: intermediate values from the forward pass must be stored until the backward pass uses them. **Gradient checkpointing** trades extra computation for memory by recomputing some intermediates.

Frameworks build the graph either while the code runs (PyTorch's dynamic "define-by-run" graphs) or by tracing and compiling functions (JAX, TensorFlow graphs).

### Gradient checking

A numerical estimate verifies a hand-written backward pass. The central difference

$$\frac{\partial f}{\partial x} \approx \frac{f(x + h) - f(x - h)}{2h}$$

has error proportional to $h^2$. With $h$ around $10^{-5}$ to $10^{-6}$, analytic and numerical gradients should agree to many digits; a large mismatch signals a bug.

## Worked examples

### Example 1: A tiny automatic-differentiation engine

The `Value` class records, for every operation, its inputs and local gradients. `backward()` orders the graph topologically and applies the chain rule from the output back. The function $f = \tanh(xy + z) \cdot x$ uses $x$ twice, so its gradient must be accumulated.

```python
import math


class Value:
    """A scalar that remembers how it was computed, for reverse-mode autodiff."""

    def __init__(self, data, parents=(), local_grads=(), name=""):
        self.data, self.grad = data, 0.0
        self.parents, self.local_grads, self.name = parents, local_grads, name

    def __add__(self, other):
        return Value(self.data + other.data, (self, other), (1.0, 1.0))

    def __mul__(self, other):
        return Value(self.data * other.data, (self, other), (other.data, self.data))

    def tanh(self):
        t = math.tanh(self.data)
        return Value(t, (self,), (1 - t * t,))

    def backward(self):
        order, seen = [], set()

        def visit(v):                       # topological order: parents before children
            if id(v) not in seen:
                seen.add(id(v))
                for p in v.parents:
                    visit(p)
                order.append(v)

        visit(self)
        self.grad = 1.0
        for v in reversed(order):           # chain rule, from the output backwards
            for parent, local in zip(v.parents, v.local_grads):
                parent.grad += local * v.grad   # += accumulates when a value is used twice


def f(x, y, z):
    return (x * y + z).tanh() * x            # x is used twice


x, y, z = Value(0.5, name="x"), Value(-1.5, name="y"), Value(2.0, name="z")
out = f(x, y, z)
out.backward()
print(f"f = {out.data:.6f}")
for v in (x, y, z):
    print(f"df/d{v.name} = {v.grad:.6f}")

eps = 1e-6
base = {"x": 0.5, "y": -1.5, "z": 2.0}
for name in "xyz":
    hi = {k: Value(v + (eps if k == name else 0)) for k, v in base.items()}
    lo = {k: Value(v - (eps if k == name else 0)) for k, v in base.items()}
    numeric = (f(hi["x"], hi["y"], hi["z"]).data - f(lo["x"], lo["y"], lo["z"]).data) / (2 * eps)
    print(f"finite-difference check d/d{name}: {numeric:.6f}")
```

Output:

```text
f = 0.424142
df/dx = 0.637972
df/dy = 0.070104
df/dz = 0.140207
finite-difference check d/dx: 0.637972
finite-difference check d/dy: 0.070104
finite-difference check d/dz: 0.140207
```

All three gradients match the finite-difference estimates to six decimal places. The gradient for $x$ combines two paths: directly through the final multiplication, contributing $\tanh(1.25) \approx 0.848$, and through $xy$ inside the tanh, contributing $x(1 - \tanh^2(1.25))\,y = 0.5 \times 0.280 \times (-1.5) \approx -0.210$. Their sum, 0.638, is what the `+=` accumulation produces. This engine works on scalars; frameworks apply exactly the same logic to tensors.

### Example 2: Backpropagation by hand

Let $f = (x + y)\,z$ with $x = 3$, $y = -1$, $z = 2$.

**Forward:** $q = x + y = 2$; $f = qz = 4$.

**Backward:**

1. $\frac{\partial f}{\partial f} = 1$.
2. Multiply node: $\frac{\partial f}{\partial z} = q = 2$ and $\frac{\partial f}{\partial q} = z = 2$ (the swapper).
3. Add node: $\frac{\partial f}{\partial x} = \frac{\partial f}{\partial q} \times 1 = 2$ and $\frac{\partial f}{\partial y} = 2$ (the distributor).

Check: increasing $x$ by 0.01 gives $(3.01 - 1) \times 2 = 4.02$, an increase of $0.02 = 2 \times 0.01$.

**Matrix shapes:** if $X$ is $32 \times 100$ and $W$ is $100 \times 10$, then $\frac{\partial L}{\partial Y}$ is $32 \times 10$, and $\frac{\partial L}{\partial W} = X^\top\frac{\partial L}{\partial Y}$ is $(100 \times 32)(32 \times 10) = 100 \times 10$, the same shape as $W$, summing contributions over the 32 examples in the batch.

## Applications

- **Every deep-learning framework:** PyTorch autograd, TensorFlow, and JAX implement reverse-mode differentiation.
- **Scientific computing:** differentiable simulators for physics, fluids, and optimisation.
- **Probabilistic programming:** gradient-based inference such as Hamiltonian Monte Carlo.
- **Debugging models:** gradient checks catch errors in custom layers.
- **Meta-learning and hyperparameter optimisation:** differentiating through training steps.

## Common mistakes

- **Overwriting instead of accumulating gradients.** A value used twice needs the sum of both contributions.
- **Visiting nodes in the wrong order.** A node's gradient is complete only after all its consumers have been processed.
- **Mismatched shapes in matrix gradients.** Check that each gradient matches its parameter's shape.
- **Choosing $h$ badly in gradient checks.** Too large gives truncation error; too small gives round-off error.
- **Forgetting that backward needs stored activations.** Memory grows with depth and batch size.

## Revision notes

- Graph of simple operations; forward pass stores values; backward pass applies the chain rule in reverse topological order.
- Multiple paths: gradients add (accumulate at fan-out).
- Local gradients: add distributes, multiply swaps, max routes, tanh $1 - t^2$, sigmoid $s(1 - s)$.
- $Y = XW$: $\partial L/\partial W = X^\top\partial L/\partial Y$, $\partial L/\partial X = \partial L/\partial Y\,W^\top$.
- Reverse mode: all parameter gradients in one pass; costs memory.
- Gradient check: $(f(x + h) - f(x - h))/2h$.

## Practice questions

:::question basic
What does the backward pass of backpropagation compute?
:::answer
It computes the gradient of the loss with respect to every intermediate value and parameter, by starting from $\partial L/\partial L = 1$ and applying the chain rule backwards through the computational graph, multiplying upstream gradients by each node's local gradient.
:::

:::question basic
Describe how gradients flow through an addition node and a multiplication node.
:::answer
An addition node passes the upstream gradient unchanged to each input. A multiplication node sends each input the upstream gradient multiplied by the value of the other input.
:::

:::question intermediate
For $f = xy + y^2$, compute $\partial f/\partial x$ and $\partial f/\partial y$ at $x = 2$, $y = 3$.
:::answer
$\partial f/\partial x = y = 3$. $\partial f/\partial y = x + 2y = 2 + 6 = 8$: $y$ reaches $f$ along two paths (through $xy$ and through $y^2$), and their contributions add.
:::

:::question intermediate
Why is reverse-mode differentiation used for training neural networks instead of forward mode?
:::answer
Training needs the gradient of a single scalar loss with respect to millions of parameters. Reverse mode obtains all of them in one backward pass costing about as much as a forward pass, whereas forward mode would need one pass per parameter (or per input direction), which would be millions of times slower.
:::

:::question advanced
Why does backpropagation need a lot of memory, and how does gradient checkpointing reduce it?
:::answer
The local gradients in the backward pass depend on values computed in the forward pass (for example, the inputs to multiplications and the outputs of activations), so all of these activations must be kept until the backward pass reaches them; memory grows with depth, width, batch size, and sequence length. Gradient checkpointing stores activations only at selected layers and recomputes the others during the backward pass from the nearest checkpoint, trading roughly one extra forward computation for a large memory reduction.
:::

## Further learning

- **Next:** *Adam Optimizer & Adaptive Learning Rates* uses these gradients to update parameters.
- **Related:** *Gradients, Jacobians & Hessians* in Calculus covers the multivariable chain rule.
