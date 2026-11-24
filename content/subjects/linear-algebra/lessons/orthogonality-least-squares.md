---
lesson: orthogonality-least-squares
title: Orthogonality, Projections & Least Squares
summary: Dot products, lengths, angles, and orthogonality; projecting a vector onto a line or subspace; building orthogonal bases with the Gram-Schmidt process; and solving inconsistent systems by least squares with the normal equations.
minutes: 50
type: theory
objectives:
  - Compute dot products, norms, angles, and orthogonal projections, and test vectors for orthogonality
  - Apply the Gram-Schmidt process to produce an orthogonal or orthonormal basis
  - Solve least-squares problems with the normal equations and interpret the residual as orthogonal to the column space
review: ai-draft
---
## Introduction

Measurements are noisy, so a system of equations built from data rarely has an exact solution: no single line passes through every data point. **Least squares** finds the best compromise, and the key to it is **orthogonality**: the best approximation is the one whose error is perpendicular to everything the model can produce. Orthogonal bases also make computations numerically stable, which is why they appear in signal processing, computer graphics, statistics, and machine learning.

**Before you start:** you should know vectors, matrix multiplication, span and column spaces, and the transpose.

## Core theory

### Dot product, length, and angle

For $\mathbf{u}, \mathbf{v} \in \mathbb{R}^n$, the **dot product** is $\mathbf{u} \cdot \mathbf{v} = \sum_i u_i v_i = \mathbf{u}^T\mathbf{v}$. The **length** (norm) is $\|\mathbf{u}\| = \sqrt{\mathbf{u} \cdot \mathbf{u}}$, and the angle $\theta$ between non-zero vectors satisfies

$$\cos\theta = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|\,\|\mathbf{v}\|}$$

Vectors are **orthogonal** when $\mathbf{u} \cdot \mathbf{v} = 0$. A **unit vector** has length 1; $\mathbf{u}/\|\mathbf{u}\|$ normalises $\mathbf{u}$. The **Cauchy-Schwarz inequality** $|\mathbf{u} \cdot \mathbf{v}| \le \|\mathbf{u}\|\|\mathbf{v}\|$ guarantees that $\cos\theta$ lies in $[-1, 1]$; in data science, $\cos\theta$ is the **cosine similarity**.

### Orthogonal projection

The projection of $\mathbf{y}$ onto the line spanned by $\mathbf{u}$ is

$$\text{proj}_{\mathbf{u}}\mathbf{y} = \frac{\mathbf{y} \cdot \mathbf{u}}{\mathbf{u} \cdot \mathbf{u}}\,\mathbf{u}$$

and the error $\mathbf{y} - \text{proj}_{\mathbf{u}}\mathbf{y}$ is orthogonal to $\mathbf{u}$. More generally, the projection $\hat{\mathbf{y}}$ of $\mathbf{y}$ onto a subspace $W$ is the **closest point** of $W$ to $\mathbf{y}$, characterised by $\mathbf{y} - \hat{\mathbf{y}}$ being orthogonal to every vector in $W$. With an orthogonal basis $\mathbf{u}_1, \dots, \mathbf{u}_k$ of $W$, it is simply the sum of the projections onto each $\mathbf{u}_i$.

### Orthogonal bases and Gram-Schmidt

A set of mutually orthogonal non-zero vectors is automatically linearly independent. An **orthonormal** basis makes coordinates trivial: the coordinate along $\mathbf{q}_i$ is just $\mathbf{y} \cdot \mathbf{q}_i$. A square matrix $Q$ with orthonormal columns satisfies $Q^TQ = I$, so $Q^{-1} = Q^T$; such **orthogonal matrices** preserve lengths and angles.

The **Gram-Schmidt process** turns any basis $\mathbf{v}_1, \dots, \mathbf{v}_k$ into an orthogonal one by subtracting from each vector its projections onto the vectors already built:

$$\mathbf{u}_1 = \mathbf{v}_1, \quad \mathbf{u}_2 = \mathbf{v}_2 - \text{proj}_{\mathbf{u}_1}\mathbf{v}_2, \quad \mathbf{u}_3 = \mathbf{v}_3 - \text{proj}_{\mathbf{u}_1}\mathbf{v}_3 - \text{proj}_{\mathbf{u}_2}\mathbf{v}_3, \ \dots$$

Normalising the results gives an orthonormal basis. Recording the steps as matrices gives the **QR factorisation** $A = QR$.

### Least squares

When $A\mathbf{x} = \mathbf{b}$ has no solution, a **least-squares solution** $\hat{\mathbf{x}}$ minimises $\|A\mathbf{x} - \mathbf{b}\|^2$. Then $A\hat{\mathbf{x}}$ is the projection of $\mathbf{b}$ onto $\text{Col}(A)$, so the residual $\mathbf{b} - A\hat{\mathbf{x}}$ is orthogonal to every column of $A$: $A^T(\mathbf{b} - A\hat{\mathbf{x}}) = \mathbf{0}$. This gives the **normal equations**

$$A^TA\,\hat{\mathbf{x}} = A^T\mathbf{b}$$

which have a unique solution when the columns of $A$ are independent. Fitting a line $y = b_0 + b_1x$ to points $(x_i, y_i)$ uses $A$ with a column of ones and a column of $x_i$. In numerical practice, QR factorisation is preferred to forming $A^TA$, which can lose accuracy.

## Worked examples

### Example 1: Gram-Schmidt and a least-squares line

The program orthogonalises $\mathbf{v}_1 = (1, 1, 0)$, $\mathbf{v}_2 = (1, 0, 1)$, $\mathbf{v}_3 = (0, 1, 1)$ with exact fractions, then fits a line to the points $(0, 1)$, $(1, 3)$, $(2, 4)$, $(3, 4)$ with the normal equations.

```python
from fractions import Fraction as F

def dot(u, v):
    return sum(a * b for a, b in zip(u, v))

def proj(u, onto):
    k = dot(u, onto) / dot(onto, onto)
    return [k * x for x in onto]

v1, v2, v3 = [F(1), F(1), F(0)], [F(1), F(0), F(1)], [F(0), F(1), F(1)]
u1 = v1
u2 = [a - b for a, b in zip(v2, proj(v2, u1))]
u3 = [a - b - c for a, b, c in zip(v3, proj(v3, u1), proj(v3, u2))]
for name, u in (("u1", u1), ("u2", u2), ("u3", u3)):
    print(name, [str(x) for x in u])
print("pairwise dot products:", dot(u1, u2), dot(u1, u3), dot(u2, u3))

xs = [F(0), F(1), F(2), F(3)]
ys = [F(1), F(3), F(4), F(4)]
n = len(xs)
sx, sy = sum(xs), sum(ys)
sxx, sxy = sum(x * x for x in xs), sum(x * y for x, y in zip(xs, ys))
# normal equations [n sx; sx sxx][b0; b1] = [sy; sxy]
det = n * sxx - sx * sx
b0 = (sxx * sy - sx * sxy) / det
b1 = (n * sxy - sx * sy) / det
residuals = [y - (b0 + b1 * x) for x, y in zip(xs, ys)]
print("least-squares line: y =", b0, "+", b1, "x")
print("residuals:", [str(r) for r in residuals])
print("residuals orthogonal to columns of A:", sum(residuals) == 0, sum(r * x for r, x in zip(residuals, xs)) == 0)
print("sum of squared residuals:", sum(r * r for r in residuals))
```

Output:

```text
u1 ['1', '1', '0']
u2 ['1/2', '-1/2', '1']
u3 ['-2/3', '2/3', '2/3']
pairwise dot products: 0 0 0
least-squares line: y = 3/2 + 1 x
residuals: ['-1/2', '1/2', '1/2', '-1/2']
residuals orthogonal to columns of A: True True
sum of squared residuals: 1
```

The three new vectors are mutually orthogonal (all dot products are 0); dividing each by its length would make them orthonormal. The least-squares line is $y = 1.5 + x$. Its residuals sum to zero and are orthogonal to the $x$ values, exactly the conditions $A^T(\mathbf{b} - A\hat{\mathbf{x}}) = \mathbf{0}$ for the two columns of $A$ (ones and $x$). No other line has a smaller sum of squared residuals than 1.

### Example 2: Projecting onto a line by hand

Project $\mathbf{y} = (2, 3)$ onto the line spanned by $\mathbf{u} = (4, 2)$, and find the distance from $\mathbf{y}$ to the line.

$\mathbf{y} \cdot \mathbf{u} = 8 + 6 = 14$ and $\mathbf{u} \cdot \mathbf{u} = 20$, so

$$\text{proj}_{\mathbf{u}}\mathbf{y} = \frac{14}{20}(4, 2) = (2.8, 1.4)$$

The error is $\mathbf{y} - \text{proj} = (-0.8, 1.6)$; check orthogonality: $(-0.8)(4) + (1.6)(2) = 0$. The distance from $\mathbf{y}$ to the line is the length of the error, $\sqrt{0.64 + 2.56} = \sqrt{3.2} \approx 1.789$. The angle between $\mathbf{y}$ and $\mathbf{u}$ satisfies $\cos\theta = 14/(\sqrt{13}\sqrt{20}) \approx 0.868$, so $\theta \approx 29.7°$.

## Applications

- **Data fitting:** linear regression is a least-squares problem.
- **Signal processing:** Fourier series expand signals in an orthogonal basis of sines and cosines.
- **Computer graphics:** orthonormal camera bases and rotation matrices.
- **Recommender systems and search:** cosine similarity compares users, items, and documents.

## Common mistakes

- **Dividing by $\|\mathbf{u}\|$ instead of $\|\mathbf{u}\|^2$ in projections.** The formula uses $\mathbf{u} \cdot \mathbf{u}$.
- **Forgetting to subtract all previous projections in Gram-Schmidt.**
- **Solving $A\mathbf{x} = \mathbf{b}$ directly when it is inconsistent.** Use the normal equations or QR.
- **Assuming orthogonal means orthonormal.** Orthonormal vectors also have length 1.
- **Using $Q^{-1} = Q^T$ for matrices whose columns are not orthonormal.**

## Revision notes

- $\mathbf{u} \cdot \mathbf{v} = \sum u_iv_i$; $\|\mathbf{u}\| = \sqrt{\mathbf{u} \cdot \mathbf{u}}$; $\cos\theta = \mathbf{u} \cdot \mathbf{v}/(\|\mathbf{u}\|\|\mathbf{v}\|)$.
- Orthogonal: dot product 0; orthogonal non-zero vectors are independent.
- $\text{proj}_{\mathbf{u}}\mathbf{y} = \frac{\mathbf{y} \cdot \mathbf{u}}{\mathbf{u} \cdot \mathbf{u}}\mathbf{u}$; the error is orthogonal to $\mathbf{u}$.
- Gram-Schmidt subtracts projections onto earlier vectors; gives QR.
- Orthogonal matrix: $Q^TQ = I$, preserves lengths.
- Least squares: $A^TA\hat{\mathbf{x}} = A^T\mathbf{b}$; residual orthogonal to $\text{Col}(A)$.

## Practice questions

:::question basic
Are $(2, -1, 3)$ and $(1, 5, 1)$ orthogonal?
:::answer
Yes. Their dot product is $2 - 5 + 3 = 0$.
:::

:::question basic
Find the unit vector in the direction of $(3, 4)$.
:::answer
Its length is $\sqrt{9 + 16} = 5$, so the unit vector is $(3/5, 4/5) = (0.6, 0.8)$.
:::

:::question intermediate
Project $\mathbf{y} = (1, 2, 3)$ onto $\mathbf{u} = (1, 1, 1)$.
:::answer
$\mathbf{y} \cdot \mathbf{u} = 6$ and $\mathbf{u} \cdot \mathbf{u} = 3$, so the projection is $2(1, 1, 1) = (2, 2, 2)$. The error $(-1, 0, 1)$ has dot product 0 with $\mathbf{u}$, as required.
:::

:::question intermediate
Apply one step of Gram-Schmidt to $\mathbf{v}_1 = (1, 0, 1)$ and $\mathbf{v}_2 = (1, 1, 0)$.
:::answer
$\mathbf{u}_1 = (1, 0, 1)$. $\text{proj}_{\mathbf{u}_1}\mathbf{v}_2 = \frac{1}{2}(1, 0, 1)$, so $\mathbf{u}_2 = (1, 1, 0) - (0.5, 0, 0.5) = (0.5, 1, -0.5)$. Check: $\mathbf{u}_1 \cdot \mathbf{u}_2 = 0.5 - 0.5 = 0$.
:::

:::question advanced
Explain why the least-squares residual must be orthogonal to the column space of $A$, and derive the normal equations from this fact.
:::answer
$A\mathbf{x}$ ranges over the column space, and the point of a subspace closest to $\mathbf{b}$ is the orthogonal projection: if the error had a component along some direction in the subspace, moving the approximation in that direction would shorten the error. So $\mathbf{b} - A\hat{\mathbf{x}}$ is orthogonal to every column of $A$, which means each column's dot product with it is zero: $A^T(\mathbf{b} - A\hat{\mathbf{x}}) = \mathbf{0}$. Rearranging gives $A^TA\hat{\mathbf{x}} = A^T\mathbf{b}$.
:::

## Further learning

- **Next:** *Eigenvalue Decomposition & SVD* uses orthogonal bases to diagonalise matrices.
- **Related:** *Correlation & Simple Linear Regression* in Statistics applies least squares to data.
