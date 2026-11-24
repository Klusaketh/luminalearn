---
lesson: vector-spaces-matrix-mult
title: Vector Spaces & Matrix Multiplication
summary: Vectors and the operations of addition and scalar multiplication, vector spaces and subspaces, span and the column space, and matrix multiplication understood as combining columns and composing transformations.
minutes: 45
type: theory
objectives:
  - Perform vector operations, compute linear combinations, and decide whether a vector is in a span
  - Identify vector spaces and subspaces, including the column space and null space of a matrix
  - Multiply matrices, explain the column view of $A\mathbf{x}$, and use the algebraic rules of matrix products, including non-commutativity
review: ai-draft
---
## Introduction

Vectors describe anything with several numeric components: positions, velocities, colours, word embeddings, or the features of a data point. A **vector space** is any collection where vectors can be added and scaled while staying in the collection, and this simple idea unifies geometry, systems of equations, and data. **Matrix multiplication** then becomes the language for combining vectors and chaining transformations, which is why it is the most heavily optimised operation in scientific computing and deep learning.

**Before you start:** you should know Gaussian elimination and be comfortable with coordinates in 2-D and 3-D.

## Core theory

### Vectors and linear combinations

A vector in $\mathbb{R}^n$ is an ordered list of $n$ numbers, usually written as a column. Vectors add componentwise and are scaled by multiplying every component. A **linear combination** of $\mathbf{v}_1, \dots, \mathbf{v}_k$ is $c_1\mathbf{v}_1 + \cdots + c_k\mathbf{v}_k$. The **span** of a set of vectors is the set of all their linear combinations: the span of one non-zero vector in $\mathbb{R}^3$ is a line through the origin; of two non-parallel vectors, a plane.

Asking whether $\mathbf{b}$ lies in the span of $\mathbf{v}_1, \dots, \mathbf{v}_k$ is the same as asking whether the system with augmented matrix $[\mathbf{v}_1 \cdots \mathbf{v}_k \mid \mathbf{b}]$ is consistent.

### Vector spaces and subspaces

A **vector space** is a set with addition and scalar multiplication satisfying the familiar rules (associativity, commutativity of addition, a zero vector, additive inverses, distributivity, and so on). Examples: $\mathbb{R}^n$; polynomials of degree at most $d$; $m \times n$ matrices; functions. A **subspace** is a subset of a vector space that is itself a vector space; to check it, verify that it contains $\mathbf{0}$, and is **closed** under addition and scalar multiplication. Lines and planes through the origin are subspaces of $\mathbb{R}^3$; a line not through the origin is not.

Two subspaces come with every $m \times n$ matrix $A$:

- the **column space** $\text{Col}(A)$, the span of its columns, a subspace of $\mathbb{R}^m$; $A\mathbf{x} = \mathbf{b}$ is solvable exactly when $\mathbf{b} \in \text{Col}(A)$;
- the **null space** $\text{Null}(A) = \{\mathbf{x} : A\mathbf{x} = \mathbf{0}\}$, a subspace of $\mathbb{R}^n$.

### Matrix-vector multiplication: the column view

For $A$ with columns $\mathbf{a}_1, \dots, \mathbf{a}_n$,

$$A\mathbf{x} = x_1\mathbf{a}_1 + x_2\mathbf{a}_2 + \cdots + x_n\mathbf{a}_n$$

so $A\mathbf{x}$ is a linear combination of the columns with weights from $\mathbf{x}$. Entry by entry, the $i$-th component is the dot product of row $i$ with $\mathbf{x}$. A matrix therefore defines a **linear transformation** $\mathbf{x} \mapsto A\mathbf{x}$; its columns are the images of the standard basis vectors.

### Matrix multiplication

If $A$ is $m \times n$ and $B$ is $n \times p$, then $AB$ is $m \times p$ with

$$(AB)_{ij} = \sum_{k=1}^{n} a_{ik} b_{kj}$$

Each column of $AB$ is $A$ times the corresponding column of $B$. The product represents **composition**: applying $B$ first and then $A$. Rules:

- Associative: $(AB)C = A(BC)$; distributive over addition.
- **Not commutative:** in general $AB \ne BA$, and one may be defined when the other is not.
- $(AB)^T = B^T A^T$.
- $AB = 0$ does not imply $A = 0$ or $B = 0$, and $AB = AC$ does not imply $B = C$ unless $A$ is invertible.

Multiplying two $n \times n$ matrices with the definition takes $n^3$ multiplications; GPUs and libraries such as BLAS are built to do this extremely fast.

## Worked examples

### Example 1: Products, non-commutativity, and the column view

```python
def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

A = [[1, 2], [3, 4]]
B = [[0, 1], [1, 0]]
print("AB =", matmul(A, B), "| BA =", matmul(B, A))
M = [[1, 0, 2], [0, 1, -1]]
v = [[3], [4], [1]]
print("Mv =", [row[0] for row in matmul(M, v)], "= 3*col1 + 4*col2 + 1*col3 =",
      [3 * M[i][0] + 4 * M[i][1] + 1 * M[i][2] for i in range(2)])
C = [[1, 1], [0, 1]]
print("shear twice:", matmul(C, C), "| (AB)^T == B^T A^T:",
      [list(r) for r in zip(*matmul(A, B))] == matmul([list(r) for r in zip(*B)], [list(r) for r in zip(*A)]))
```

Output:

```text
AB = [[2, 1], [4, 3]] | BA = [[3, 4], [1, 2]]
Mv = [5, 3] = 3*col1 + 4*col2 + 1*col3 = [5, 3]
shear twice: [[1, 2], [0, 1]] | (AB)^T == B^T A^T: True
```

$B$ swaps coordinates. $AB$ applies the swap first and then $A$, which swaps the **columns** of $A$; $BA$ swaps the **rows** of $A$; the results differ, so $AB \ne BA$. $M\mathbf{v}$ equals 3 times column 1 plus 4 times column 2 plus 1 times column 3. Applying the shear $C$ twice composes into a shear with twice the slope. The transpose rule $(AB)^T = B^TA^T$ checks out.

### Example 2: Is a vector in a span? Is a set a subspace?

**(a)** Is $\mathbf{b} = (7, 4, 1)$ in the span of $\mathbf{v}_1 = (1, 2, 3)$ and $\mathbf{v}_2 = (3, 0, -1)$?

Solve $c_1\mathbf{v}_1 + c_2\mathbf{v}_2 = \mathbf{b}$: from the second component, $2c_1 = 4$, so $c_1 = 2$; from the first, $2 + 3c_2 = 7$, so $c_2 = 5/3$; the third component then gives $3(2) - 5/3 = 13/3 \ne 1$. The system is inconsistent, so $\mathbf{b}$ is **not** in the span: it lies off the plane spanned by $\mathbf{v}_1$ and $\mathbf{v}_2$.

**(b)** Is $W = \{(x, y, z) : x + 2y - z = 0\}$ a subspace of $\mathbb{R}^3$? It contains $\mathbf{0}$; if $\mathbf{u}$ and $\mathbf{w}$ satisfy the equation, so does $\mathbf{u} + \mathbf{w}$ (add the equations) and $c\mathbf{u}$ (multiply by $c$). So yes: it is a plane through the origin, the null space of $[1 \; 2 \; -1]$. The set $\{x + 2y - z = 5\}$ is not a subspace, because it does not contain $\mathbf{0}$.

## Applications

- **Computer graphics:** chains of transformations are matrix products applied to every vertex.
- **Neural networks:** each layer computes $W\mathbf{x} + \mathbf{b}$; training is dominated by matrix multiplication.
- **Data science:** a data set is a matrix whose rows are samples and columns are features.
- **Markov chains:** state distributions evolve by repeated matrix-vector multiplication.

## Common mistakes

- **Assuming $AB = BA$.** Order matters: $AB$ applies $B$ first.
- **Multiplying incompatible shapes.** The inner dimensions must match: $(m \times n)(n \times p)$.
- **Multiplying entrywise.** Matrix multiplication uses row-by-column dot products.
- **Calling a set a subspace without checking the zero vector.** Lines not through the origin fail.
- **Cancelling matrices.** $AB = AC$ does not give $B = C$ unless $A$ is invertible.

## Revision notes

- Linear combination $\sum c_i\mathbf{v}_i$; span = all linear combinations.
- Subspace test: contains $\mathbf{0}$, closed under addition and scalar multiplication.
- $\text{Col}(A)$ = span of columns ($A\mathbf{x} = \mathbf{b}$ solvable iff $\mathbf{b} \in \text{Col}(A)$); $\text{Null}(A)$ = solutions of $A\mathbf{x} = \mathbf{0}$.
- $A\mathbf{x} = \sum x_j\mathbf{a}_j$ (column view).
- $(AB)_{ij} = \sum_k a_{ik}b_{kj}$; $AB$ = apply $B$ then $A$; not commutative.
- $(AB)^T = B^TA^T$.

## Practice questions

:::question basic
Compute $\begin{pmatrix} 2 & 0 \\ 1 & 3 \end{pmatrix}\begin{pmatrix} 4 \\ -1 \end{pmatrix}$ using the column view.
:::answer
$4\begin{pmatrix} 2 \\ 1 \end{pmatrix} + (-1)\begin{pmatrix} 0 \\ 3 \end{pmatrix} = \begin{pmatrix} 8 \\ 4 \end{pmatrix} + \begin{pmatrix} 0 \\ -3 \end{pmatrix} = \begin{pmatrix} 8 \\ 1 \end{pmatrix}$.
:::

:::question basic
If $A$ is $3 \times 5$ and $B$ is $5 \times 2$, what are the shapes of $AB$ and $BA$?
:::answer
$AB$ is $3 \times 2$ because the inner dimensions (5 and 5) match. $BA$ would need $(5 \times 2)(3 \times 5)$, whose inner dimensions 2 and 3 differ, so $BA$ is undefined.
:::

:::question intermediate
Is the set of $2 \times 2$ matrices with determinant 0 a subspace of all $2 \times 2$ matrices?
:::answer
No. It contains the zero matrix, but it is not closed under addition: $\begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix}$ and $\begin{pmatrix} 0 & 0 \\ 0 & 1 \end{pmatrix}$ both have determinant 0, yet their sum is the identity, with determinant 1.
:::

:::question intermediate
Give $2 \times 2$ matrices $A$ and $B$, both non-zero, with $AB = 0$.
:::answer
$A = \begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix}$ and $B = \begin{pmatrix} 0 & 0 \\ 0 & 1 \end{pmatrix}$: $AB = 0$. $B$ maps everything onto the y-axis, which $A$ then sends to zero. This shows matrices can have "zero divisors", unlike real numbers.
:::

:::question advanced
Explain why the columns of $AB$ are linear combinations of the columns of $A$, and what this implies about $\text{Col}(AB)$.
:::answer
Column $j$ of $AB$ is $A\mathbf{b}_j$, where $\mathbf{b}_j$ is column $j$ of $B$, and by the column view $A\mathbf{b}_j$ is a linear combination of the columns of $A$ with weights from $\mathbf{b}_j$. Hence every column of $AB$ lies in $\text{Col}(A)$, so $\text{Col}(AB) \subseteq \text{Col}(A)$, and in particular $\text{rank}(AB) \le \text{rank}(A)$.
:::

## Further learning

- **Next:** *Linear Independence, Basis, Dimension & Rank* measures the size of spans and subspaces.
- **Related:** *Linear Transformations* studies maps like $\mathbf{x} \mapsto A\mathbf{x}$ in their own right.
