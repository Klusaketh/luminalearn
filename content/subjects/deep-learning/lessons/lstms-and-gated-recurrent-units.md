---
lesson: lstms-and-gated-recurrent-units
title: Recurrent Cells, LSTMs & Gated Units
summary: Recurrent neural networks for sequences: the recurrence and backpropagation through time, vanishing and exploding gradients with gradient clipping, LSTM gates and cell state, GRUs, parameter counts, sequence architectures, and why attention replaced recurrence.
minutes: 50
type: theory
objectives:
  - Describe a simple RNN, unroll it through time, and explain vanishing and exploding gradients and gradient clipping
  - Compute an LSTM step with its forget, input, and output gates and explain how the cell state preserves information
  - Compare LSTMs and GRUs, count their parameters, and choose sequence architectures for different tasks
review: ai-draft
---
## Introduction

Language, speech, sensor readings, and stock prices are sequences: their meaning depends on order, and their length varies. A **recurrent neural network** (RNN) reads a sequence one step at a time while carrying a hidden state that summarises what it has seen. Simple RNNs struggle to remember for long, a problem solved by **gated** designs: the long short-term memory (LSTM, 1997) and the gated recurrent unit (GRU, 2014). They powered machine translation, speech recognition, and text generation until Transformers took over, and they remain useful for streaming and resource-limited settings.

**Before you start:** you should know *Non-Linear Activations & Gradient Flow* and *Computational Graphs & Chain Rule*.

## Core theory

### The simple RNN

At each time step $t$:

$$\mathbf{h}_t = \tanh(W_x\mathbf{x}_t + W_h\mathbf{h}_{t-1} + \mathbf{b}), \qquad \mathbf{y}_t = W_y\mathbf{h}_t$$

The same weights are used at every step, so the network handles sequences of any length with a fixed number of parameters. Training **unrolls** the network through time into a deep feed-forward graph and applies backpropagation: **backpropagation through time** (BPTT). For long sequences, **truncated** BPTT backpropagates over limited windows.

### Vanishing and exploding gradients

The gradient of a late loss with respect to an early hidden state contains a product of one Jacobian per step:

$$\frac{\partial\mathbf{h}_T}{\partial\mathbf{h}_0} = \prod_{t=1}^{T}\frac{\partial\mathbf{h}_t}{\partial\mathbf{h}_{t-1}}$$

each involving $W_h$ and the tanh derivative. If these factors are typically smaller than 1, the product **vanishes** exponentially and the network cannot learn long-range dependencies; if larger than 1, it **explodes**. **Gradient clipping**, rescaling the gradient whenever its norm exceeds a threshold, prevents explosions but does nothing for vanishing gradients.

### The LSTM

An LSTM adds a **cell state** $\mathbf{c}_t$, a memory that is updated additively, controlled by three **gates** with sigmoid outputs between 0 and 1:

$$\begin{aligned}
\mathbf{f}_t &= \sigma(W_f[\mathbf{h}_{t-1}, \mathbf{x}_t] + \mathbf{b}_f) && \text{forget gate: how much old memory to keep} \\
\mathbf{i}_t &= \sigma(W_i[\mathbf{h}_{t-1}, \mathbf{x}_t] + \mathbf{b}_i) && \text{input gate: how much new content to write} \\
\mathbf{g}_t &= \tanh(W_g[\mathbf{h}_{t-1}, \mathbf{x}_t] + \mathbf{b}_g) && \text{candidate content} \\
\mathbf{o}_t &= \sigma(W_o[\mathbf{h}_{t-1}, \mathbf{x}_t] + \mathbf{b}_o) && \text{output gate: how much memory to reveal} \\
\mathbf{c}_t &= \mathbf{f}_t \odot \mathbf{c}_{t-1} + \mathbf{i}_t \odot \mathbf{g}_t, \qquad \mathbf{h}_t = \mathbf{o}_t \odot \tanh(\mathbf{c}_t)
\end{aligned}$$

Along the cell state, the gradient is multiplied by the forget gate at each step rather than by a weight matrix and a squashing derivative. When the forget gate is near 1, information and gradients flow across many steps almost unchanged. Initialising the forget-gate bias to a positive value (such as 1) encourages remembering early in training.

### The GRU

A GRU merges the cell and hidden state and uses two gates: an **update gate** $\mathbf{z}_t$ that blends old state and new candidate, and a **reset gate** $\mathbf{r}_t$ that controls how much past state feeds the candidate:

$$\tilde{\mathbf{h}}_t = \tanh(W[\mathbf{r}_t \odot \mathbf{h}_{t-1}, \mathbf{x}_t] + \mathbf{b}), \qquad \mathbf{h}_t = (1 - \mathbf{z}_t) \odot \mathbf{h}_{t-1} + \mathbf{z}_t \odot \tilde{\mathbf{h}}_t$$

(some texts swap the roles of $\mathbf{z}_t$ and $1 - \mathbf{z}_t$). With three weight blocks instead of four, a GRU has about 25% fewer parameters than an LSTM and performs similarly on many tasks.

### Parameter counts and architectures

With input size $x$ and hidden size $h$, each gate block has $h(x + h) + h$ parameters (with one bias vector), so an LSTM has $4[h(x + h) + h]$ and a GRU $3[h(x + h) + h]$. Common architectures: **many-to-one** (sentiment of a review), **many-to-many** aligned (tagging each word), **sequence-to-sequence** with an encoder and decoder (translation), **bidirectional** RNNs that read both directions, and stacked layers.

RNNs process tokens one after another, which prevents parallelism across time and still makes very long-range dependencies hard; attention and Transformers address both.

## Worked examples

### Example 1: Gradients through time and an LSTM remembering

The program shows how a recurrent weight below or above 1 makes gradients vanish or explode, clips a gradient, runs a scalar LSTM that sees one input pulse and then only zeros, and counts parameters.

```python
import math

# 1. Vanishing and exploding gradients: backpropagating through T steps multiplies by w each step
for w in (0.5, 0.9, 1.1, 1.5):
    print(f"recurrent weight {w}: gradient factor after 10 steps {w ** 10:9.3e}, after 50 steps {w ** 50:9.3e}")

grad = [30.0, -40.0]                                   # gradient clipping by norm
norm = math.hypot(*grad)
clipped = [g * 5.0 / norm for g in grad] if norm > 5.0 else grad
print(f"gradient {grad} has norm {norm}; clipped to norm 5: {clipped}")


# 2. One LSTM cell (scalar version) processing a sequence
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


W = {"f": (0.0, 0.0, 3.0), "i": (2.0, 0.0, -1.0), "o": (0.0, 0.0, 2.0), "g": (2.0, 0.0, 0.0)}  # (w_x, w_h, bias)
c, h = 0.0, 0.0
for t, x in enumerate([1.0, 0.0, 0.0, 0.0, 0.0], 1):
    gate = {k: wx * x + wh * h + b for k, (wx, wh, b) in W.items()}
    f, i, o, g = sigmoid(gate["f"]), sigmoid(gate["i"]), sigmoid(gate["o"]), math.tanh(gate["g"])
    c = f * c + i * g                                  # forget some old memory, write some new
    h = o * math.tanh(c)
    print(f"t={t} x={x:.0f}: forget {f:.3f} input {i:.3f} output {o:.3f} -> cell {c:.3f}, hidden {h:.3f}")

# 3. Parameter counts (one bias vector per gate)
x_size, h_size = 100, 256
per_gate = h_size * (x_size + h_size) + h_size
print(f"LSTM (4 gates): {4 * per_gate:,} parameters; GRU (3 gates): {3 * per_gate:,}; simple RNN: {per_gate:,}")
```

Output:

```text
recurrent weight 0.5: gradient factor after 10 steps 9.766e-04, after 50 steps 8.882e-16
recurrent weight 0.9: gradient factor after 10 steps 3.487e-01, after 50 steps 5.154e-03
recurrent weight 1.1: gradient factor after 10 steps 2.594e+00, after 50 steps 1.174e+02
recurrent weight 1.5: gradient factor after 10 steps 5.767e+01, after 50 steps 6.376e+08
gradient [30.0, -40.0] has norm 50.0; clipped to norm 5: [3.0, -4.0]
t=1 x=1: forget 0.953 input 0.731 output 0.881 -> cell 0.705, hidden 0.535
t=2 x=0: forget 0.953 input 0.269 output 0.881 -> cell 0.671, hidden 0.516
t=3 x=0: forget 0.953 input 0.269 output 0.881 -> cell 0.639, hidden 0.497
t=4 x=0: forget 0.953 input 0.269 output 0.881 -> cell 0.609, hidden 0.479
t=5 x=0: forget 0.953 input 0.269 output 0.881 -> cell 0.580, hidden 0.461
LSTM (4 gates): 365,568 parameters; GRU (3 gates): 274,176; simple RNN: 91,392
```

With a recurrent factor of 0.5, the gradient after 50 steps is about $10^{-15}$, effectively zero; with 1.5, it is about $6 \times 10^8$. Clipping rescales the gradient $(30, -40)$, of norm 50, to $(3, -4)$, keeping its direction. In the LSTM, the input pulse at $t = 1$ is written into the cell (0.705). Afterwards the input gate is low and the candidate is 0, but the forget gate stays at 0.953, so the memory decays only slowly: after four more steps the cell still holds 0.580, and the hidden state still reports it. A simple RNN with a recurrent factor of 0.5 would have lost the information within a few steps. The parameter counts show the 4:3:1 ratio of LSTM, GRU, and simple RNN.

### Example 2: An LSTM step and parameter counts by hand

At $t = 1$ in the example: $f = \sigma(3) \approx 0.953$, $i = \sigma(2 \times 1 - 1) = \sigma(1) \approx 0.731$, $g = \tanh(2) \approx 0.964$, and $o = \sigma(2) \approx 0.881$. With $c_0 = 0$:

$$c_1 = 0.953 \times 0 + 0.731 \times 0.964 \approx 0.705, \qquad h_1 = 0.881 \times \tanh(0.705) \approx 0.881 \times 0.607 \approx 0.535$$

**Another cell update:** with $f = 0.5$, $c_{t-1} = 2$, $i = 0.8$, and $g = -0.5$: $c_t = 1 - 0.4 = 0.6$.

**A GRU** with input size 50 and hidden size 128 has $3 \times (128 \times 178 + 128) = 3 \times 22{,}912 = 68{,}736$ parameters. (Frameworks such as PyTorch use two bias vectors per gate, giving slightly more.)

## Applications

- **Speech recognition and keyword spotting:** streaming audio processed step by step on devices.
- **Time-series forecasting:** sensor, energy, and demand data.
- **Handwriting recognition and generation:** sequences of pen strokes.
- **Language tasks:** tagging, language modelling, and translation (historically).
- **Music generation:** modelling note sequences.

## Common mistakes

- **Expecting clipping to fix vanishing gradients.** It only limits exploding ones; use gated cells.
- **Confusing hidden state and cell state.** The cell state is the long-term memory; the hidden state is the gated output.
- **Initialising the forget-gate bias to a large negative value.** The cell then forgets everything.
- **Using RNNs where parallelism matters most.** Transformers train much faster on long sequences with modern hardware.
- **Ignoring sequence padding.** Mask padded steps so they do not affect states or losses.

## Revision notes

- RNN: $\mathbf{h}_t = \tanh(W_x\mathbf{x}_t + W_h\mathbf{h}_{t-1} + \mathbf{b})$, shared weights; trained with BPTT.
- Products of per-step factors cause vanishing ($< 1$) or exploding ($> 1$) gradients; clipping handles explosions.
- LSTM: forget, input, output gates; $\mathbf{c}_t = \mathbf{f} \odot \mathbf{c}_{t-1} + \mathbf{i} \odot \mathbf{g}$; $\mathbf{h}_t = \mathbf{o} \odot \tanh(\mathbf{c}_t)$.
- GRU: update and reset gates; fewer parameters, similar accuracy.
- Parameters: LSTM $4[h(x + h) + h]$, GRU $3[\cdot]$, simple RNN $1[\cdot]$.
- Architectures: many-to-one, many-to-many, seq2seq, bidirectional, stacked.

## Practice questions

:::question basic
Why does an RNN use the same weights at every time step?
:::answer
Sharing weights lets one network process sequences of any length with a fixed number of parameters and apply the same learned processing to a pattern wherever it occurs in the sequence, which improves generalisation.
:::

:::question basic
What is the role of the forget gate in an LSTM?
:::answer
It decides, for each component of the cell state, what fraction of the previous memory to keep: values near 1 preserve the memory and values near 0 erase it. This lets the LSTM hold information over long spans or clear it when it is no longer relevant.
:::

:::question intermediate
Clip the gradient $(6, 8)$ to a maximum norm of 5.
:::answer
Its norm is $\sqrt{36 + 64} = 10$, which exceeds 5, so multiply by $5/10 = 0.5$: the clipped gradient is $(3, 4)$, with the same direction and norm 5.
:::

:::question intermediate
How many parameters does an LSTM layer with input size 100 and hidden size 256 have (one bias vector per gate)?
:::answer
Each gate block has $256 \times (100 + 256) + 256 = 91{,}392$ parameters, and there are four blocks: $4 \times 91{,}392 = 365{,}568$.
:::

:::question advanced
Explain why LSTMs suffer much less from vanishing gradients than simple RNNs.
:::answer
In a simple RNN, the gradient flowing back one step is multiplied by $W_h^\top$ and the tanh derivative, so over many steps it is a long product of factors that typically shrink it exponentially. In an LSTM, the cell state is updated additively, $\mathbf{c}_t = \mathbf{f}_t \odot \mathbf{c}_{t-1} + \mathbf{i}_t \odot \mathbf{g}_t$, so the direct path from $\mathbf{c}_t$ back to $\mathbf{c}_{t-1}$ is multiplied only by the forget gate. When the network learns to keep the forget gate near 1 for information it needs, gradients pass through many steps nearly unchanged, so long-range dependencies can be learned.
:::

## Further learning

- **Next:** *Self-Attention Mechanism & Transformers* replaces recurrence with attention.
- **Related:** *Seq2Seq, Attention & Machine Translation* in Natural Language Processing shows RNN encoder-decoders in action.
