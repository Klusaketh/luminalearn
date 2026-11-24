---
lesson: transfer-learning-fine-tuning
title: Transfer Learning & Fine-Tuning
summary: Reusing pretrained models: why features transfer, feature extraction versus fine-tuning, freezing layers and discriminative learning rates, choosing a strategy from data size and domain similarity, risks such as catastrophic forgetting and negative transfer, and parameter-efficient fine-tuning with LoRA.
minutes: 45
type: theory
objectives:
  - Explain why pretrained features transfer and distinguish feature extraction, partial fine-tuning, and full fine-tuning
  - Choose a transfer strategy from the size of the target dataset and its similarity to the source, and count trainable parameters
  - Describe practical fine-tuning techniques and parameter-efficient methods such as LoRA
review: ai-draft
---
## Introduction

Training a large vision or language model from scratch needs millions of examples and enormous computing power. Most real projects have a few thousand labelled examples at best. **Transfer learning** bridges the gap: start from a model already trained on a huge dataset, keep the general knowledge it has learned, and adapt it to the new task. It is how a hospital can build an X-ray classifier from a few thousand images and how a company can adapt a language model to its domain in hours instead of months.

**Before you start:** you should know *Convolutional Layers & Spatial Invariance* and the training loop from *Loss Functions & the Training Loop*.

## Core theory

### Why features transfer

Networks trained on large, diverse datasets such as ImageNet (about 1.28 million images in 1,000 classes) learn a hierarchy of features. Early layers detect edges, colours, and textures that are useful for almost any image; later layers become increasingly specific to the original classes. Language models similarly learn grammar and world knowledge that help many text tasks. The more general a layer's features, the more safely it can be reused.

### Strategies

1. **Feature extraction (linear probing):** freeze the pretrained **backbone**, replace the final classification layer (the **head**) with a new one for the target classes, and train only the head. Fast, needs little data, and cannot overfit the backbone.
2. **Partial fine-tuning:** also unfreeze the last few layers, which hold the most task-specific features, and train them with a small learning rate.
3. **Full fine-tuning:** train all layers, starting from the pretrained weights, usually with a small learning rate. Most accurate with enough data, but most expensive and most prone to overfitting on small datasets.

Useful techniques include **discriminative learning rates** (for example $10^{-3}$ for the new head and $10^{-5}$ for early layers), **gradual unfreezing** (train the head first, then progressively unfreeze deeper layers), and keeping frozen batch-normalisation layers in evaluation mode.

### Choosing a strategy

| Target data | Similar to source | Different from source |
| :--- | :--- | :--- |
| **Small** | Feature extraction | Fine-tune some deeper layers carefully, or extract earlier-layer features |
| **Large** | Fine-tune most or all layers | Full fine-tuning (or even training from scratch) |

Always match the pretrained model's **preprocessing**: input size, colour channels, and normalisation statistics.

### Risks

- **Catastrophic forgetting:** aggressive fine-tuning overwrites useful pretrained knowledge; small learning rates and partial freezing help.
- **Negative transfer:** if source and target are too different, pretrained features can hurt.
- **Domain shift:** for example grayscale medical scans against colour photographs.
- **Inherited bias and licences:** pretrained models carry the biases of their training data and come with usage terms.

### Parameter-efficient fine-tuning

For models with billions of parameters, even storing a fine-tuned copy per task is costly. **Parameter-efficient fine-tuning** (PEFT) trains a small number of new parameters:

- **Adapters:** small bottleneck layers inserted into each block.
- **Prompt and prefix tuning:** learned input vectors that steer a frozen model.
- **LoRA (low-rank adaptation):** keep a weight matrix $W$ ($d \times k$) frozen and learn an update $\Delta W = BA$, where $B$ is $d \times r$ and $A$ is $r \times k$ with a small rank $r$. Only $r(d + k)$ parameters are trained, and $BA$ can be merged into $W$ after training, so inference costs nothing extra. QLoRA combines LoRA with a quantised frozen model to fine-tune very large models on a single GPU.

Because optimisers such as Adam store two extra numbers per **trainable** parameter, PEFT also cuts memory dramatically.

## Worked examples

### Example 1: Counting what each strategy trains

The program counts parameters in a small four-block CNN with a 10-class head, computes how many are trainable under three transfer strategies, and compares LoRA with full fine-tuning of a large weight matrix.

```python
# Parameter accounting for transfer learning on a small convolutional network
layers = [  # (name, kind, in_channels, out_channels, kernel)
    ("conv1", "conv", 3, 32, 3),
    ("conv2", "conv", 32, 64, 3),
    ("conv3", "conv", 64, 128, 3),
    ("conv4", "conv", 128, 256, 3),
    ("head", "dense", 256, 10, 1),          # after global average pooling
]


def count(kind, cin, cout, k):
    return cin * cout * k * k + cout if kind == "conv" else cin * cout + cout


params = {name: count(kind, cin, cout, k) for name, kind, cin, cout, k in layers}
total = sum(params.values())
for name, n in params.items():
    print(f"{name:6} {n:9,} parameters")
print(f"total  {total:9,}")

strategies = {
    "feature extraction (train head only)": ["head"],
    "fine-tune last block + head": ["conv4", "head"],
    "full fine-tuning": list(params),
}
for label, trainable in strategies.items():
    n = sum(params[name] for name in trainable)
    print(f"{label:38}: {n:7,} trainable ({100 * n / total:5.1f}%)")

# LoRA: adapt a d x d weight matrix with a rank-r update B @ A
d = 4096
for r in (4, 8, 16):
    lora = 2 * d * r
    print(f"LoRA rank {r:2} on a {d}x{d} matrix: {lora:,} trainable vs {d * d:,} ({100 * lora / (d * d):.2f}%)")
```

Output:

```text
conv1        896 parameters
conv2     18,496 parameters
conv3     73,856 parameters
conv4    295,168 parameters
head       2,570 parameters
total    390,986
feature extraction (train head only)  :   2,570 trainable (  0.7%)
fine-tune last block + head           : 297,738 trainable ( 76.2%)
full fine-tuning                      : 390,986 trainable (100.0%)
LoRA rank  4 on a 4096x4096 matrix: 32,768 trainable vs 16,777,216 (0.20%)
LoRA rank  8 on a 4096x4096 matrix: 65,536 trainable vs 16,777,216 (0.39%)
LoRA rank 16 on a 4096x4096 matrix: 131,072 trainable vs 16,777,216 (0.78%)
```

Feature extraction trains only the 2,570 head parameters, under 1% of the network. Fine-tuning the last block plus the head trains 76% of all parameters, because the deepest block has by far the most channels: parameter counts grow with $C_{\text{in}} \times C_{\text{out}}$. For a large language model with $4096 \times 4096$ attention matrices, LoRA with rank 8 trains 65,536 parameters per matrix instead of 16.8 million, about 0.39%.

### Example 2: Planning a medical-imaging project

A hospital has 2,000 labelled chest X-rays in three classes and a ResNet-50 pretrained on ImageNet (about 25.6 million parameters, whose final layer maps 2,048 features to 1,000 classes with $2{,}048 \times 1{,}000 + 1{,}000 = 2{,}049{,}000$ parameters).

1. **Replace the head:** $2{,}048 \times 3 + 3 = 6{,}147$ parameters for three classes.
2. **Stage 1, feature extraction:** freeze the backbone and train the head with learning rate $10^{-3}$, with augmentation (small rotations, crops, brightness changes; no flips that would swap left and right anatomy if laterality matters).
3. **Stage 2, partial fine-tuning:** unfreeze the last stage of the network with learning rate $10^{-4}$ for it and $10^{-3}$ for the head, using early stopping on a validation set split by patient.
4. **Preprocessing:** resize to 224×224 and replicate the grayscale channel three times to match the RGB input, normalising with the ImageNet statistics.

The domain differs from ImageNet photographs, so partial fine-tuning is likely to beat pure feature extraction, but the small dataset argues against full fine-tuning.

## Applications

- **Medical imaging:** classifiers and detectors adapted from ImageNet or medical foundation models.
- **Natural language processing:** BERT-style and GPT-style models fine-tuned for classification, question answering, and chat.
- **Speech:** pretrained acoustic models adapted to new accents or languages.
- **Industrial inspection:** detecting defects with few labelled examples.
- **Personalised models:** LoRA adapters per customer or task on one shared base model.

## Common mistakes

- **Using a high learning rate for pretrained layers.** It destroys useful features.
- **Mismatched preprocessing.** The input normalisation must match what the model saw during pretraining.
- **Fine-tuning everything on tiny datasets.** The model overfits; start with feature extraction.
- **Updating batch-norm statistics on a frozen backbone.** Keep frozen normalisation layers in evaluation mode.
- **Ignoring domain shift and licence terms.** Check that pretrained features and weights suit the target use.

## Revision notes

- Early layers learn general features; later layers are task-specific.
- Feature extraction (frozen backbone, new head), partial fine-tuning, full fine-tuning.
- Small and similar data: freeze more; large or different data: fine-tune more.
- Discriminative learning rates, gradual unfreezing, matched preprocessing.
- Risks: catastrophic forgetting, negative transfer, domain shift, inherited bias.
- PEFT: adapters, prompt tuning, LoRA ($\Delta W = BA$, $r(d + k)$ trainable parameters, mergeable).

## Practice questions

:::question basic
What is the difference between feature extraction and fine-tuning?
:::answer
In feature extraction, the pretrained backbone is frozen and only a new head is trained on its outputs. In fine-tuning, some or all pretrained layers are also updated (with a small learning rate) so the features themselves adapt to the new task.
:::

:::question basic
Why are pretrained layers usually trained with a lower learning rate than the new head?
:::answer
The pretrained weights already encode useful features; large updates could destroy them (catastrophic forgetting). The new head starts from random weights and needs larger steps to learn, so it gets a higher learning rate.
:::

:::question intermediate
A backbone outputs 2,048 features. How many parameters does a new head for 20 classes have?
:::answer
$2{,}048 \times 20 = 40{,}960$ weights plus 20 biases, giving 40,980 parameters.
:::

:::question intermediate
You have 500 labelled satellite images in five land-use classes and a model pretrained on everyday photographs. Which strategy would you start with and why?
:::answer
Start with feature extraction (frozen backbone, new head) plus strong augmentation, because 500 images are too few to fine-tune millions of parameters safely. Because satellite imagery differs from everyday photos, next try unfreezing the last block with a small learning rate, comparing on a validation set, and consider features from earlier, more general layers.
:::

:::question advanced
Explain how LoRA works, why a low rank is often enough, and what it saves.
:::answer
LoRA freezes a pretrained weight matrix $W$ and learns an update $\Delta W = BA$, with $B$ of size $d \times r$ and $A$ of size $r \times k$, where $r$ is small (such as 8). Only $r(d + k)$ parameters are trained, for example 65,536 instead of 16.8 million for a $4096 \times 4096$ matrix with $r = 8$. A low rank is often enough because the change needed to adapt a large pretrained model to a specific task appears to lie in a low-dimensional subspace. LoRA saves gradient and optimiser memory (Adam's states exist only for trainable parameters), storage (each task needs only the small adapter), and, since $BA$ can be merged into $W$, adds no inference cost.
:::

## Further learning

- **Next:** *Recurrent Cells, LSTMs & Gated Units* turns to sequence models.
- **Related:** *Large Language Models: Pretraining, Fine-Tuning & Prompting* in Natural Language Processing applies transfer learning to language.
