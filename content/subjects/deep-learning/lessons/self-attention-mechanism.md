---
lesson: self-attention-mechanism
title: Self-Attention Mechanism & Transformers
summary: Self-attention and the Transformer: queries, keys, and values, scaled dot-product attention, causal and padding masks, multi-head attention, positional encodings, the Transformer block with residual connections, layer normalisation, and feed-forward layers, and the quadratic cost of attention.
minutes: 50
type: theory
objectives:
  - Compute scaled dot-product attention from queries, keys, and values, with and without a causal mask
  - Explain multi-head attention, positional encodings, and the structure of a Transformer block, and count its parameters
  - Analyse the quadratic time and memory cost of attention and how it shapes model design
review: ai-draft
---
## Introduction

In 2017, the paper "Attention Is All You Need" introduced the **Transformer**, an architecture built entirely around attention, without recurrence or convolution. It lets every token look directly at every other token in a single step, captures long-range relationships easily, and trains in parallel on modern hardware. Transformers now underpin large language models, translation systems, vision models, protein-structure prediction, and much more. Understanding **self-attention** is the key to all of them.

**Before you start:** you should know *Multilayer Perceptron & Matrix Algebra*, softmax from *Non-Linear Activations & Gradient Flow*, and ideally *Recurrent Cells, LSTMs & Gated Units*.

## Core theory

### Queries, keys, and values

Each token's embedding $\mathbf{x}_i$ is projected into three vectors with learned matrices: a **query** $\mathbf{q}_i = \mathbf{x}_iW_Q$ (what this token is looking for), a **key** $\mathbf{k}_j = \mathbf{x}_jW_K$ (what each token offers), and a **value** $\mathbf{v}_j = \mathbf{x}_jW_V$ (the information it passes on). The output for token $i$ is a weighted average of all values, with weights from how well its query matches each key.

### Scaled dot-product attention

For all tokens at once, with $Q$, $K$, $V$ as matrices of row vectors:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

Each row of the softmax gives one token's **attention weights**, summing to 1. Dividing by $\sqrt{d_k}$ (the key dimension) keeps the dot products' variance around 1; without it, large dot products push the softmax into saturation, where it becomes nearly one-hot and its gradients vanish.

In **self-attention**, $Q$, $K$, and $V$ all come from the same sequence. In **cross-attention**, used by encoder-decoder models, queries come from the decoder and keys and values from the encoder.

### Masks

- A **causal mask** sets scores for future positions ($j > i$) to $-\infty$ before the softmax, so each token attends only to itself and earlier tokens. Decoder-only language models use it so that predicting the next token never peeks ahead.
- A **padding mask** hides padding tokens added to make sequences in a batch the same length.

### Multi-head attention

Instead of one attention with dimension $d_{\text{model}}$, the model runs $h$ **heads** in parallel, each with its own projections into $d_k = d_{\text{model}}/h$ dimensions, then concatenates their outputs and applies an output projection $W_O$. Different heads can specialise: one may track syntax, another coreference, another nearby words. The four projections $W_Q, W_K, W_V, W_O$ have $4(d_{\text{model}}^2 + d_{\text{model}})$ parameters with biases, independent of $h$.

### Positional information

Attention treats its input as a set: permuting the tokens just permutes the outputs. Word order must be injected through **positional encodings** added to the embeddings. The original Transformer used sinusoids:

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right), \qquad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)$$

which give every position a unique pattern of slow and fast waves. Many models instead learn position embeddings or use relative schemes such as rotary embeddings (RoPE).

### The Transformer block

Each block contains:

1. Multi-head self-attention, with a **residual connection** (add the input back) and **layer normalisation**.
2. A position-wise **feed-forward network**, typically $d_{\text{model}} \to 4d_{\text{model}} \to d_{\text{model}}$ with a GELU or ReLU, again with a residual connection and layer normalisation.

Modern models usually apply layer normalisation before each sub-layer ("pre-norm"), which trains more stably. Stacking dozens of blocks gives encoders (BERT), decoders (GPT), or encoder-decoder models (T5).

### Cost

The score matrix $QK^\top$ has $n \times n$ entries for a sequence of $n$ tokens, so attention costs $O(n^2d)$ time and $O(n^2)$ memory per head and layer. Doubling the context length quadruples this cost. Efficient variants use sparse or local attention, linear approximations, or IO-aware exact algorithms such as FlashAttention.

## Worked examples

### Example 1: Attention weights for three tokens

Three tokens have hand-picked query, key, and value vectors of dimension 2. The program computes full and causal self-attention, sinusoidal positional encodings, and attention sizes.

```python
import math


def softmax(row):
    m = max(row)
    exps = [math.exp(v - m) for v in row]
    return [e / sum(exps) for e in exps]


def attention(Q, K, V, causal=False):
    d_k = len(K[0])
    scores = [[sum(q * k for q, k in zip(qi, kj)) / math.sqrt(d_k) for kj in K] for qi in Q]
    if causal:                                 # token i may not look at tokens after i
        scores = [[s if j <= i else -math.inf for j, s in enumerate(row)] for i, row in enumerate(scores)]
    weights = [softmax(row) for row in scores]
    outputs = [[sum(w * v[c] for w, v in zip(row, V)) for c in range(len(V[0]))] for row in weights]
    return weights, outputs


tokens = ["the", "cat", "sat"]
Q = [[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]]       # queries: what each token is looking for
K = [[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]]       # keys: what each token offers
V = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]       # values: the information passed on
for causal in (False, True):
    weights, outputs = attention(Q, K, V, causal)
    print("causal attention" if causal else "full self-attention")
    for tok, w, o in zip(tokens, weights, outputs):
        print(f"  {tok:3} attends {[round(x, 3) for x in w]} -> output {[round(x, 3) for x in o]}")


def positional_encoding(pos, d_model=4):
    return [math.sin(pos / 10000 ** (i / d_model)) if i % 2 == 0 else math.cos(pos / 10000 ** ((i - 1) / d_model))
            for i in range(d_model)]


for pos in range(3):
    print(f"position {pos}: sinusoidal encoding {[round(v, 4) for v in positional_encoding(pos)]}")

d_model = 512
print(f"multi-head attention projections (Q, K, V, output) for d_model={d_model}: {4 * (d_model * d_model + d_model):,} parameters")
for n in (512, 2048, 8192):
    print(f"sequence length {n:5}: attention score matrix has {n * n:,} entries per head")
```

Output:

```text
full self-attention
  the attends [0.401, 0.198, 0.401] -> output [0.602, 0.398]
  cat attends [0.045, 0.768, 0.187] -> output [0.139, 0.861]
  sat attends [0.198, 0.401, 0.401] -> output [0.398, 0.602]
causal attention
  the attends [1.0, 0.0, 0.0] -> output [1.0, 0.0]
  cat attends [0.056, 0.944, 0.0] -> output [0.056, 0.944]
  sat attends [0.198, 0.401, 0.401] -> output [0.398, 0.602]
position 0: sinusoidal encoding [0.0, 1.0, 0.0, 1.0]
position 1: sinusoidal encoding [0.8415, 0.5403, 0.01, 1.0]
position 2: sinusoidal encoding [0.9093, -0.4161, 0.02, 0.9998]
multi-head attention projections (Q, K, V, output) for d_model=512: 1,050,624 parameters
sequence length   512: attention score matrix has 262,144 entries per head
sequence length  2048: attention score matrix has 4,194,304 entries per head
sequence length  8192: attention score matrix has 67,108,864 entries per head
```

"cat" has the largest query-key match with itself (score $4/\sqrt{2}$), so it puts 77% of its attention on itself and its output is mostly its own value. "the" splits its attention evenly between itself and "sat", whose key resembles its query. With the causal mask, "the" can only see itself (weight 1.0), "cat" sees "the" and itself, and "sat", the last token, sees everything, so its row is unchanged. The positional encodings give position 0 the pattern (0, 1, 0, 1) and change the first pair of dimensions quickly and the second slowly with position. The attention projections of a 512-dimensional model have about a million parameters, and the score matrix grows from 262,144 entries at 512 tokens to 67 million at 8,192.

### Example 2: Attention and parameters by hand

**Two tokens**, query $\mathbf{q} = (2, 0)$, keys $\mathbf{k}_1 = (1, 0)$ and $\mathbf{k}_2 = (0, 1)$, values $\mathbf{v}_1 = (1, 0)$ and $\mathbf{v}_2 = (0, 1)$. Scores: $2/\sqrt{2} \approx 1.414$ and 0. Softmax: $e^{1.414} \approx 4.11$, so the weights are $4.11/5.11 \approx 0.80$ and 0.20, and the output is $(0.80, 0.20)$. Without scaling, the scores 2 and 0 give weights 0.88 and 0.12: a sharper, more saturated softmax.

**Scores (2, 0, 0)** give weights $e^2/(e^2 + 2) \approx 7.389/9.389 \approx 0.787$ and 0.107 for each of the others.

**One Transformer block** with $d_{\text{model}} = 512$ and a 2,048-unit feed-forward layer: attention $4(512^2 + 512) = 1{,}050{,}624$; feed-forward $512 \times 2048 + 2048 + 2048 \times 512 + 512 = 2{,}099{,}712$; two layer norms $2 \times 2 \times 512 = 2{,}048$. Total: 3,152,384 parameters, two-thirds of them in the feed-forward layer.

## Applications

- **Large language models:** decoder-only Transformers with causal attention.
- **Machine translation and summarisation:** encoder-decoder Transformers with cross-attention.
- **Vision:** Vision Transformers treat image patches as tokens.
- **Speech and audio:** Transformer-based recognition and generation.
- **Science:** protein structure prediction and molecule modelling with attention.

## Common mistakes

- **Forgetting the $\sqrt{d_k}$ scaling.** Softmax saturates and training slows.
- **Leaving out the causal mask in a language model.** The model cheats by reading the token it should predict.
- **Assuming attention knows word order.** Without positional information, it treats the input as a bag of tokens.
- **Underestimating the quadratic cost.** Long contexts multiply memory use dramatically.
- **Confusing heads with layers.** Heads run in parallel within a layer; layers are stacked.

## Revision notes

- $\text{Attention}(Q, K, V) = \text{softmax}(QK^\top/\sqrt{d_k})V$; rows of weights sum to 1.
- Self-attention ($Q$, $K$, $V$ from one sequence) vs cross-attention (queries from the decoder).
- Causal mask ($-\infty$ for future positions); padding mask.
- Multi-head: $h$ heads of size $d_{\text{model}}/h$, concatenated and projected; $4(d^2 + d)$ parameters.
- Positional encodings: sinusoidal, learned, or relative (RoPE).
- Block: attention + residual + layer norm, feed-forward ($4d$) + residual + layer norm; cost $O(n^2d)$.

## Practice questions

:::question basic
Why are attention scores divided by $\sqrt{d_k}$?
:::answer
Dot products of $d_k$-dimensional vectors with unit-variance components have variance about $d_k$, so for large $d_k$ the scores become large and the softmax becomes nearly one-hot, with tiny gradients. Dividing by $\sqrt{d_k}$ brings the variance back to about 1, keeping the softmax in a trainable range.
:::

:::question basic
What does a causal mask do, and which models need it?
:::answer
It prevents each position from attending to later positions by setting those scores to $-\infty$ before the softmax. Autoregressive models that generate text left to right, such as GPT-style decoders, need it so that each prediction depends only on earlier tokens.
:::

:::question intermediate
A query's scores against three keys are (2, 0, 0) after scaling. Compute the attention weights.
:::answer
$e^2 \approx 7.389$ and $e^0 = 1$, so the total is 9.389. The weights are $7.389/9.389 \approx 0.787$ for the first key and $1/9.389 \approx 0.107$ for each of the other two.
:::

:::question intermediate
Why do Transformers need positional encodings?
:::answer
Self-attention computes weighted averages that do not depend on the order of the tokens: shuffling the input simply shuffles the output. Since word order changes meaning ("dog bites man" versus "man bites dog"), position information must be added to the token embeddings, through sinusoidal, learned, or relative positional encodings.
:::

:::question advanced
Estimate the memory needed just for the attention score matrices of one layer with 16 heads, sequence length 8,192, and 2-byte (16-bit) numbers, and describe ways to reduce it.
:::answer
Each head's score matrix has $8{,}192^2 = 67{,}108{,}864$ entries; 16 heads give about $1.07 \times 10^9$ entries, and at 2 bytes each that is about 2.1 GB (2 GiB) for a single layer, before storing anything for the backward pass. Remedies include IO-aware exact attention (FlashAttention) that never materialises the full matrix, sparse or sliding-window attention that limits which positions interact, linear-attention approximations, and gradient checkpointing to avoid storing activations for every layer.
:::

## Further learning

- **Next:** *Encoder vs Decoder Transformer Models* in Natural Language Processing compares BERT-style and GPT-style models.
- **Related:** *Vision Transformers (ViT)* in Computer Vision applies attention to images.
