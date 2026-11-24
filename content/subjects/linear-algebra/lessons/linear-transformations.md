---
lesson: linear-transformations
title: Linear Transformations
summary: Linear transformations and their defining properties, the standard matrix of a transformation, geometric transformations such as rotations, reflections, projections, and shears, composition as matrix multiplication, and kernels and images.
minutes: 45
type: theory
objectives:
  - Test whether a map is linear and find its standard matrix from the images of the basis vectors
  - Describe rotations, reflections, projections, scalings, and shears with matrices and compose them
  - Find the kernel and image of a linear transformation and relate them to one-to-one and onto maps
review: ai-draft
---
## Introduction

A **linear transformation** moves vectors around in a way that keeps straight lines straight and the origin fixed: rotating an image, projecting a 3-D scene onto a screen, or mixing input features in a neural network layer. Every such map can be written as multiplication by a matrix, and every matrix defines one. Seeing matrices as transformations, rather than as tables of numbers, is the key to understanding what linear algebra computations actually do.

**Before you start:** you should know matrix-vector multiplication, span, null space, and rank.

## Core theory

### Linearity

A function $T: \mathbb{R}^n \to \mathbb{R}^m$ is **linear** if for all vectors $\mathbf{u}, \mathbf{v}$ and scalars $c$:

$$T(\mathbf{u} + \mathbf{v}) = T(\mathbf{u}) + T(\mathbf{v}), \qquad T(c\mathbf{u}) = cT(\mathbf{u})$$

Consequences: $T(\mathbf{0}) = \mathbf{0}$, and $T$ preserves linear combinations. A translation $T(\mathbf{x}) = \mathbf{x} + \mathbf{b}$ with $\mathbf{b} \ne \mathbf{0}$ is **not** linear, because it moves the origin; neither is $T(x) = x^2$.

### The standard matrix

Because $\mathbf{x} = x_1\mathbf{e}_1 + \cdots + x_n\mathbf{e}_n$, linearity gives $T(\mathbf{x}) = x_1T(\mathbf{e}_1) + \cdots + x_nT(\mathbf{e}_n)$. So $T(\mathbf{x}) = A\mathbf{x}$ where

$$A = \begin{bmatrix} T(\mathbf{e}_1) & T(\mathbf{e}_2) & \cdots & T(\mathbf{e}_n) \end{bmatrix}$$

The columns of the matrix are the images of the standard basis vectors. To find the matrix of a geometric transformation, ask where $\mathbf{e}_1$ and $\mathbf{e}_2$ go.

### Geometric transformations of the plane

| Transformation | Matrix |
| :--- | :--- |
| Rotation by angle $\theta$ (anticlockwise) | $\begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$ |
| Reflection in the x-axis | $\begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$ |
| Projection onto the x-axis | $\begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix}$ |
| Scaling by $a$ and $b$ | $\begin{pmatrix} a & 0 \\ 0 & b \end{pmatrix}$ |
| Horizontal shear by $k$ | $\begin{pmatrix} 1 & k \\ 0 & 1 \end{pmatrix}$ |

Rotations and reflections preserve lengths and angles (their matrices are **orthogonal**); projections collapse a dimension (determinant 0).

### Composition

Applying $S$ and then $T$ gives the transformation $T \circ S$ with matrix $AB$ when $T$ has matrix $A$ and $S$ has matrix $B$. The **rightmost** matrix acts first. Since matrix multiplication is not commutative, the order of transformations usually matters: rotating then reflecting differs from reflecting then rotating. Inverse transformations correspond to inverse matrices.

### Kernel and image

- The **kernel** $\ker T = \{\mathbf{x} : T(\mathbf{x}) = \mathbf{0}\}$ is the null space of $A$.
- The **image** (range) is the set of all outputs, the column space of $A$.

$T$ is **one-to-one** (injective) exactly when $\ker T = \{\mathbf{0}\}$, that is, when $A$ has a pivot in every column. $T$ is **onto** (surjective) exactly when its image is all of $\mathbb{R}^m$, that is, when $A$ has a pivot in every row. The rank-nullity theorem reads $\dim(\ker T) + \dim(\text{image } T) = n$.

## Worked examples

### Example 1: Geometric transformations and their order

```python
from math import cos, sin, pi

def apply(M, v):
    return [round(sum(M[i][j] * v[j] for j in range(len(v))), 6) + 0.0 for i in range(len(M))]

def compose(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

theta = pi / 2
rotate = [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]]
reflect_x = [[1, 0], [0, -1]]
project_x = [[1, 0], [0, 0]]
v = [3, 1]
print("rotate 90 deg:", apply(rotate, v))
print("reflect in x-axis:", apply(reflect_x, v))
print("project onto x-axis:", apply(project_x, v))
print("rotate then reflect:", apply(compose(reflect_x, rotate), v), "| reflect then rotate:", apply(compose(rotate, reflect_x), v))
print("projection kernel contains (0, 5):", apply(project_x, [0, 5]) == [0.0, 0.0])
T = [[1, 2, 0], [0, 1, 1]]
print("T(e1), T(e2), T(e3) are the columns:", [apply(T, e) for e in ([1, 0, 0], [0, 1, 0], [0, 0, 1])])
print("T(2, -1, 1) =", apply(T, [2, -1, 1]), "= 2T(e1) - T(e2) + T(e3)")
```

Output:

```text
rotate 90 deg: [-1.0, 3.0]
reflect in x-axis: [3.0, -1.0]
project onto x-axis: [3.0, 0.0]
rotate then reflect: [-1.0, -3.0] | reflect then rotate: [1.0, 3.0]
projection kernel contains (0, 5): True
T(e1), T(e2), T(e3) are the columns: [[1.0, 0.0], [2.0, 1.0], [0.0, 1.0]]
T(2, -1, 1) = [0.0, 0.0] = 2T(e1) - T(e2) + T(e3)
```

Rotating $(3, 1)$ by 90° gives $(-1, 3)$; reflecting it in the x-axis gives $(3, -1)$; projecting gives $(3, 0)$. Rotating then reflecting gives $(-1, -3)$, but reflecting then rotating gives $(1, 3)$: order matters, matching $AB \ne BA$. The projection sends $(0, 5)$ to zero, so its kernel is the y-axis. For the map $T: \mathbb{R}^3 \to \mathbb{R}^2$, the images of the basis vectors are exactly the columns of its matrix, and the vector $(2, -1, 1)$ is sent to $\mathbf{0}$, so it lies in the kernel.

### Example 2: Finding a matrix and its kernel

Find the matrix of the transformation that reflects vectors in the line $y = x$, then find its kernel and image.

Reflection in $y = x$ swaps coordinates: $\mathbf{e}_1 = (1, 0) \mapsto (0, 1)$ and $\mathbf{e}_2 \mapsto (1, 0)$. So

$$A = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$$

Since $\det A = -1 \ne 0$, $A$ is invertible (it is its own inverse: reflecting twice returns every vector). The kernel is $\{\mathbf{0}\}$, so the map is one-to-one, and the image is all of $\mathbb{R}^2$, so it is onto. The negative determinant shows that orientation is reversed, as for any reflection.

For the map $T(x, y, z) = (x + 2y, y + z)$ from Example 1, with matrix $\begin{pmatrix} 1 & 2 & 0 \\ 0 & 1 & 1 \end{pmatrix}$, row reduction shows 2 pivots, so the image is all of $\mathbb{R}^2$ (onto), and the kernel has dimension $3 - 2 = 1$: it is the line spanned by $(2, -1, 1)$, so $T$ is not one-to-one.

## Applications

- **Computer graphics and games:** model, view, and projection matrices transform every vertex.
- **Robotics:** rotation matrices describe orientations of joints and cameras.
- **Image processing:** scaling, rotation, and shear warp images.
- **Neural networks:** each dense layer applies a linear transformation before a non-linearity.

## Common mistakes

- **Treating translations as linear.** They move the origin; graphics uses homogeneous coordinates to handle them.
- **Composing in the wrong order.** In $AB\mathbf{x}$, $B$ acts first.
- **Building the matrix from rows instead of columns.** Columns are the images of the basis vectors.
- **Confusing kernel and image.** The kernel lives in the input space; the image lives in the output space.
- **Assuming every square matrix is invertible.** Projections have non-trivial kernels.

## Revision notes

- Linear: preserves addition and scalar multiplication; $T(\mathbf{0}) = \mathbf{0}$.
- Standard matrix: columns are $T(\mathbf{e}_1), \dots, T(\mathbf{e}_n)$.
- Rotation, reflection, projection, scaling, and shear matrices.
- Composition $T \circ S$ ↔ $AB$; the right factor acts first; order matters.
- Kernel = null space; image = column space; one-to-one ⇔ trivial kernel; onto ⇔ pivot in every row.
- $\dim \ker T + \dim \text{image } T = n$.

## Practice questions

:::question basic
Is $T(x, y) = (x + y, 2x)$ linear? Is $T(x, y) = (x + 1, y)$?
:::answer
The first is linear: it equals multiplication by $\begin{pmatrix} 1 & 1 \\ 2 & 0 \end{pmatrix}$. The second is not, since $T(0, 0) = (1, 0) \ne \mathbf{0}$; it is a translation.
:::

:::question basic
Write the matrix that rotates vectors by 180°.
:::answer
With $\theta = 180°$, $\cos\theta = -1$ and $\sin\theta = 0$, giving $\begin{pmatrix} -1 & 0 \\ 0 & -1 \end{pmatrix}$, which sends every vector to its negative.
:::

:::question intermediate
Find the matrix of the transformation that first scales the x-coordinate by 2 and then rotates by 90° anticlockwise.
:::answer
Scaling is $S = \begin{pmatrix} 2 & 0 \\ 0 & 1 \end{pmatrix}$ and rotation is $R = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$. Scaling acts first, so the matrix is $RS = \begin{pmatrix} 0 & -1 \\ 2 & 0 \end{pmatrix}$.
:::

:::question intermediate
A linear map $T: \mathbb{R}^4 \to \mathbb{R}^3$ is onto. What is the dimension of its kernel?
:::answer
Onto means the image is all of $\mathbb{R}^3$, so the rank is 3. By rank-nullity, the kernel has dimension $4 - 3 = 1$.
:::

:::question advanced
Show that the projection $P$ onto the x-axis satisfies $P^2 = P$, and explain geometrically why any projection should.
:::answer
$P = \begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix}$, and $P^2 = \begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix} = P$. Geometrically, once a vector has been projected onto the axis, it already lies on the axis, so projecting it again changes nothing. Matrices with $P^2 = P$ are called idempotent and characterise projections.
:::

## Further learning

- **Next:** *Orthogonality, Projections & Least Squares* studies projections onto general subspaces.
- **Related:** *Vector Spaces & Matrix Multiplication* explains the column view behind standard matrices.
