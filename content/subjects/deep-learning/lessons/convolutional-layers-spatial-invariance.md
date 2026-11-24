---
lesson: convolutional-layers-spatial-invariance
title: Convolutional Layers & Spatial Invariance
summary: Convolutional layers for images: kernels as learned feature detectors, local connectivity and weight sharing, output size with padding and stride, channels and parameter counts, pooling, translation equivariance and invariance, receptive fields, and landmark CNN architectures.
minutes: 50
type: theory
objectives:
  - Compute a 2-D convolution (cross-correlation) by hand and in code, including padding and stride
  - Calculate output sizes, parameter counts, and receptive fields of convolutional layers
  - Explain local connectivity, weight sharing, translation equivariance, and the invariance provided by pooling
review: ai-draft
---
## Introduction

A 224×224 colour photo has over 150,000 numbers. Connecting each to every unit of a dense layer would need billions of weights, and the network would have to learn separately that a cat in the top-left corner is the same as a cat in the bottom-right. **Convolutional neural networks** (CNNs) avoid both problems: small filters slide across the image, detecting the same pattern everywhere with the same few weights. Since AlexNet won the 2012 ImageNet challenge, CNNs have driven a revolution in computer vision.

**Before you start:** you should know *Multilayer Perceptron & Matrix Algebra*; the image ideas in *Spatial Convolution & Edge Detection* help.

## Core theory

### The convolution operation

A **kernel** (filter), for example 3×3, slides across the input. At each position, the layer multiplies the kernel elementwise with the patch beneath it, sums the products, and adds a bias, producing one value of the output **feature map**. Deep-learning libraries actually compute **cross-correlation** (the kernel is not flipped), but the name "convolution" is universal and, since kernels are learned, the difference does not matter.

Two ideas make convolution efficient:

- **Local connectivity:** each output depends only on a small neighbourhood of the input.
- **Weight sharing:** the same kernel is used at every position, so a pattern detector learned in one place works everywhere.

### Channels and parameters

Inputs have **channels** (3 for RGB). Each output channel has its own kernel spanning all input channels, so a layer with $C_{\text{in}}$ input channels, $C_{\text{out}}$ output channels, and $k \times k$ kernels has

$$k \cdot k \cdot C_{\text{in}} \cdot C_{\text{out}} + C_{\text{out}}$$

parameters, independent of the image size.

### Output size, padding, and stride

For input size $n$, kernel $k$, padding $p$ (zeros added around the border), and stride $s$ (the step between positions):

$$n_{\text{out}} = \left\lfloor\frac{n + 2p - k}{s}\right\rfloor + 1$$

"Same" padding, $p = (k - 1)/2$ with stride 1, keeps the size; stride 2 roughly halves it.

### Pooling and invariance

**Max pooling** takes the maximum over small windows (typically 2×2 with stride 2), halving the width and height; average pooling takes the mean. **Global average pooling** reduces each whole feature map to one number before the classifier.

Convolution is **translation equivariant**: shifting the input shifts the feature map by the same amount. Pooling adds a little **invariance**: small shifts within a pooling window do not change its maximum. Stacking many layers with pooling gives a network whose final prediction is largely insensitive to where the object appears.

### Receptive fields and hierarchy

The **receptive field** of a unit is the region of the input that can affect it. Stacking layers grows it: two 3×3 layers see 5×5, three see 7×7, and strides multiply the growth. Early layers detect edges and colours, middle layers textures and parts, and deep layers whole objects. Stacking small kernels is preferred to large ones: three 3×3 layers cover a 7×7 field with $27C^2$ weights instead of $49C^2$, and add more non-linearities.

### Variations and landmark architectures

**1×1 convolutions** mix channels cheaply; **dilated** convolutions widen receptive fields without extra parameters; **depthwise separable** convolutions (as in MobileNet) split spatial and channel mixing to save computation. Milestones: LeNet-5 (1998, digits), AlexNet (2012, ReLU and GPUs), VGG (2014, stacks of 3×3 layers), GoogLeNet (2014, inception modules), and ResNet (2015, residual connections enabling 100+ layers).

## Worked examples

### Example 1: Detecting an edge and watching it move

A 6×6 image is dark on the left and bright on the right. A 3×3 kernel that subtracts the left column from the right column responds to left-to-right brightness increases.

```python
def conv2d(image, kernel, stride=1, padding=0):
    """Cross-correlation, as used in deep-learning 'convolution' layers."""
    if padding:
        width = len(image[0]) + 2 * padding
        image = [[0] * width] * padding + [[0] * padding + row + [0] * padding for row in image] + [[0] * width] * padding
    k = len(kernel)
    out_h = (len(image) - k) // stride + 1
    out_w = (len(image[0]) - k) // stride + 1
    return [[sum(image[i * stride + a][j * stride + b] * kernel[a][b] for a in range(k) for b in range(k))
             for j in range(out_w)] for i in range(out_h)]


def max_pool(fm, size=2):
    return [[max(fm[i + a][j + b] for a in range(size) for b in range(size))
             for j in range(0, len(fm[0]) - size + 1, size)] for i in range(0, len(fm) - size + 1, size)]


image = [[0, 0, 0, 9, 9, 9]] * 6                 # dark left half, bright right half
edge = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]      # responds to left-to-right increases
out = conv2d(image, edge)
print("feature map (6x6 input, 3x3 kernel, no padding):")
for row in out:
    print("  ", row)
shifted = [[0, 0, 0, 0, 9, 9]] * 6               # the same edge, one pixel to the right
print("after shifting the image right by one pixel, row 0:", conv2d(shifted, edge)[0])
print("max-pooled original:", max_pool(out), " max-pooled shifted:", max_pool(conv2d(shifted, edge)))
print("with padding=1 the output keeps the input size:", len(conv2d(image, edge, padding=1)), "x",
      len(conv2d(image, edge, padding=1)[0]))
print("stride 2, padding 1:", len(conv2d(image, edge, stride=2, padding=1)), "x",
      len(conv2d(image, edge, stride=2, padding=1)[0]))


def out_size(n, k, s, p):
    return (n + 2 * p - k) // s + 1


print("formula check, 224 input, 7x7 kernel, stride 2, padding 3 ->", out_size(224, 7, 2, 3))
conv_params = 3 * 3 * 3 * 16 + 16
dense_params = (32 * 32 * 3) * (32 * 32 * 16) + 32 * 32 * 16
print(f"32x32x3 -> 32x32x16: conv 3x3 layer {conv_params:,} parameters vs fully connected {dense_params:,}")
```

Output:

```text
feature map (6x6 input, 3x3 kernel, no padding):
   [0, 27, 27, 0]
   [0, 27, 27, 0]
   [0, 27, 27, 0]
   [0, 27, 27, 0]
after shifting the image right by one pixel, row 0: [0, 0, 27, 27]
max-pooled original: [[27, 27], [27, 27]]  max-pooled shifted: [[0, 27], [0, 27]]
with padding=1 the output keeps the input size: 6 x 6
stride 2, padding 1: 3 x 3
formula check, 224 input, 7x7 kernel, stride 2, padding 3 -> 112
32x32x3 -> 32x32x16: conv 3x3 layer 448 parameters vs fully connected 50,348,032
```

The feature map lights up (27) exactly where the 3×3 window straddles the edge and is 0 over flat regions. Shifting the image one pixel to the right shifts the response one position to the right: **equivariance**. After 2×2 max pooling, the right half of the pooled map is unchanged by the shift, but the left half changes from 27 to 0, because the edge response moved out of that pooling window: pooling gives only local, partial invariance. The size checks confirm the formula: padding 1 keeps 6×6, stride 2 gives 3×3, and the classic 7×7, stride-2, padding-3 first layer of ResNet maps 224 to 112. Finally, a 3×3 convolution from 3 to 16 channels needs 448 parameters, while a dense layer producing the same 32×32×16 output would need over 50 million.

### Example 2: Sizes, parameters, and receptive fields by hand

**One output value:** the top-left 3×3 patch in the edge region contains $\begin{pmatrix}0 & 0 & 9\end{pmatrix}$ in each row; with kernel rows $(-1, 0, 1)$, each row contributes $9$, so the output is $3 \times 9 = 27$.

**Output size:** a 32×32 input with a 5×5 kernel, stride 1, and no padding gives $32 - 5 + 1 = 28$; with stride 2 and padding 2 it gives $\lfloor(32 + 4 - 5)/2\rfloor + 1 = 15 + 1 = 16$.

**Parameters:** a 3×3 convolution from 64 to 128 channels has $3 \times 3 \times 64 \times 128 + 128 = 73{,}856$ parameters.

**Receptive field** of three stacked 3×3 layers with strides 1, 2, and 1: working backwards from one output unit with $r = 1$ and $r \leftarrow (r - 1)s + k$ for each layer from last to first: $r = 3$, then $(3 - 1) \times 2 + 3 = 7$, then $(7 - 1) \times 1 + 3 = 9$. Each final unit sees a 9×9 patch of the input.

## Applications

- **Image classification and medical imaging:** detecting diseases in X-rays and scans.
- **Object detection and segmentation:** CNN backbones in self-driving and robotics.
- **Face recognition and document analysis:** feature extraction from images.
- **Audio:** convolutions over spectrograms for speech and music.
- **Time series and genomics:** 1-D convolutions over sequences.

## Common mistakes

- **Getting the output-size formula wrong.** Include padding twice ($2p$) and take the floor.
- **Forgetting input channels in parameter counts.** Each kernel spans all $C_{\text{in}}$ channels.
- **Assuming CNNs are fully translation invariant.** Convolution is equivariant; pooling adds only partial invariance.
- **Using huge kernels.** Stacks of small kernels are cheaper and more expressive.
- **Ignoring the receptive field.** If it is smaller than the objects, the network cannot see them whole.

## Revision notes

- Convolution = sliding dot product of a kernel with input patches (cross-correlation in practice).
- Local connectivity and weight sharing; parameters $k^2C_{\text{in}}C_{\text{out}} + C_{\text{out}}$.
- Output size $\lfloor(n + 2p - k)/s\rfloor + 1$.
- Pooling reduces size and adds local invariance; global average pooling before the classifier.
- Convolution is translation equivariant; receptive fields grow with depth ($r \leftarrow (r - 1)s + k$).
- Architectures: LeNet, AlexNet, VGG, GoogLeNet, ResNet; 1×1, dilated, depthwise separable convolutions.

## Practice questions

:::question basic
How many parameters does a 3×3 convolutional layer from 64 to 128 channels have?
:::answer
$3 \times 3 \times 64 \times 128 = 73{,}728$ weights plus 128 biases, giving 73,856 parameters.
:::

:::question basic
What is the output size for a 64×64 input, a 3×3 kernel, stride 2, and padding 1?
:::answer
$\lfloor(64 + 2 - 3)/2\rfloor + 1 = \lfloor 31.5 \rfloor + 1 = 32$, so the output is 32×32.
:::

:::question intermediate
Explain the difference between translation equivariance and translation invariance in CNNs.
:::answer
Equivariance means that shifting the input shifts the output in the same way: a convolutional feature map moves with the object. Invariance means that shifting the input leaves the output unchanged: a classifier should say "cat" wherever the cat is. Convolution layers are equivariant; pooling and global pooling turn this into (approximate) invariance for the final prediction.
:::

:::question intermediate
Why do modern CNNs stack two 3×3 convolutions instead of using one 5×5 convolution?
:::answer
Two stacked 3×3 layers have the same 5×5 receptive field but use $2 \times 9C^2 = 18C^2$ weights instead of $25C^2$ (for $C$ channels in and out), and they insert an extra non-linearity between them, making the function more expressive at lower cost.
:::

:::question advanced
A network has three 3×3 convolutions with strides 2, 2, and 1. Compute the receptive field of one unit in the final layer.
:::answer
Work backwards with $r \leftarrow (r - 1)s + k$, starting from $r = 1$. The last layer (stride 1): $r = 0 \times 1 + 3 = 3$. The middle layer (stride 2): $r = (3 - 1) \times 2 + 3 = 7$. The first layer (stride 2): $r = (7 - 1) \times 2 + 3 = 15$. Each final unit sees a 15×15 region of the input.
:::

## Further learning

- **Next:** *Transfer Learning & Fine-Tuning* reuses trained CNNs for new tasks.
- **Related:** *Spatial Convolution & Edge Detection* in Computer Vision covers classical filters such as Sobel.
