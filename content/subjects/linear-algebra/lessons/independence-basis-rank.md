---
lesson: independence-basis-rank
title: Linear Independence, Basis, Dimension & Rank
summary: Linear independence and dependence, spanning sets, bases and coordinates, the dimension of a subspace, the rank of a matrix, and the rank-nullity theorem.
minutes: 50
type: theory
objectives:
  - Test sets of vectors for linear independence using row reduction or determinants
  - Find bases and dimensions of column spaces and null spaces, and express vectors in coordinates relative to a basis
  - Compute the rank of a matrix and apply the rank-nullity theorem
review: ai-draft
---
## Introduction

How many directions does a set of vectors really cover? Three vectors in $\mathbb{R}^3$ may fill all of space, or one of them may be redundant, lying in the plane of the other two. **Linear independence** detects redundancy, a **basis** is a set of vectors with no redundancy that still reaches everything, and the **dimension** counts how many vectors a basis needs. For matrices, the **rank** tells how much information survives a transformation, a number that matters for solving systems, compressing data, and training models.

**Before you start:** you should know span, subspaces, column and null spaces, and row reduction.

## Core theory

### Linear independence

Vectors $\mathbf{v}_1, \dots, \mathbf{v}_k$ are **linearly independent** if the only solution of

$$c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + \cdots + c_k\mathbf{v}_k = \mathbf{0}$$

is $c_1 = \cdots = c_k = 0$. Otherwise they are **dependent**, and at least one vector is a linear combination of the others. To test, put the vectors as columns of a matrix and row-reduce: they are independent exactly when **every column has a pivot**. Quick facts: any set containing $\mathbf{0}$ is dependent; two vectors are dependent exactly when one is a multiple of the other; more than $n$ vectors in $\mathbb{R}^n$ are always dependent; $n$ vectors in $\mathbb{R}^n$ are independent exactly when the determinant of the matrix they form is non-zero.

### Basis and coordinates

A **basis** of a subspace $V$ is a linearly independent set that spans $V$. Every vector in $V$ can be written as a combination of basis vectors in **exactly one** way; the weights are its **coordinates** relative to that basis. The standard basis of $\mathbb{R}^n$ is $\mathbf{e}_1, \dots, \mathbf{e}_n$, but every subspace has many bases, and choosing a good one, such as eigenvectors or principal components, often simplifies a problem.

### Dimension

All bases of a subspace have the same number of vectors, its **dimension**. $\dim \mathbb{R}^n = n$; a plane through the origin has dimension 2; $\{\mathbf{0}\}$ has dimension 0. In a space of dimension $d$, any $d$ independent vectors form a basis, and any $d$ vectors that span form a basis.

### Rank and the rank-nullity theorem

The **rank** of a matrix is the number of pivots, which equals $\dim \text{Col}(A)$ and also the dimension of the row space. A basis for the column space is given by the **pivot columns of the original matrix** (not of its echelon form). The **nullity** is $\dim \text{Null}(A)$, the number of free variables. For an $m \times n$ matrix:

$$\text{rank}(A) + \text{nullity}(A) = n$$

Interpretation: of the $n$ input dimensions, $\text{rank}(A)$ survive the transformation and $\text{nullity}(A)$ are collapsed to zero. A square matrix is invertible exactly when it has **full rank** ($\text{rank} = n$).

## Worked examples

### Example 1: Independence and rank by row reduction

```python
from fractions import Fraction as F

def rank(rows):
    m = [[F(x) for x in row] for row in rows]
    r = 0
    for c in range(len(m[0])):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        for i in range(r + 1, len(m)):
            f = m[i][c] / m[r][c]
            m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
        if r == len(m):
            break
    return r

vectors = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print("rank of {(1,2,3),(4,5,6),(7,8,9)}:", rank(vectors), "-> dependent;", "check: 2*(4,5,6) - (1,2,3) =", [2 * b - a for a, b in zip(vectors[0], vectors[1])])
print("rank of {(1,0,1),(0,1,1),(1,1,0)}:", rank([[1, 0, 1], [0, 1, 1], [1, 1, 0]]), "-> a basis of R^3")
A = [[1, 2, 0, 1], [2, 4, 1, 3], [3, 6, 1, 4]]
r = rank(A)
print(f"A is 3x4: rank {r}, nullity {4 - r}, rank + nullity = {r + (4 - r)} = number of columns")
```

Output:

```text
rank of {(1,2,3),(4,5,6),(7,8,9)}: 2 -> dependent; check: 2*(4,5,6) - (1,2,3) = [7, 8, 9]
rank of {(1,0,1),(0,1,1),(1,1,0)}: 3 -> a basis of R^3
A is 3x4: rank 2, nullity 2, rank + nullity = 4 = number of columns
```

The vectors $(1,2,3)$, $(4,5,6)$, $(7,8,9)$ have rank 2, so they are dependent: the third is $2(4,5,6) - (1,2,3)$, and together they span only a plane. The vectors $(1,0,1)$, $(0,1,1)$, $(1,1,0)$ have rank 3, so they form a basis of $\mathbb{R}^3$. The $3 \times 4$ matrix has rank 2 and nullity 2, which add up to its 4 columns, as the rank-nullity theorem requires.

### Example 2: Bases for the column space and null space

Find bases for $\text{Col}(A)$ and $\text{Null}(A)$ for $A = \begin{pmatrix} 1 & 2 & 0 & 1 \\ 2 & 4 & 1 & 3 \\ 3 & 6 & 1 & 4 \end{pmatrix}$.

Row reduction gives $R_2 \leftarrow R_2 - 2R_1$ and $R_3 \leftarrow R_3 - 3R_1$, then $R_3 \leftarrow R_3 - R_2$:

$$\begin{pmatrix} 1 & 2 & 0 & 1 \\ 0 & 0 & 1 & 1 \\ 0 & 0 & 0 & 0 \end{pmatrix}$$

Pivots are in columns 1 and 3, so a basis for $\text{Col}(A)$ is the **original** columns 1 and 3: $(1, 2, 3)$ and $(0, 1, 1)$. For the null space, the free variables are $x_2 = s$ and $x_4 = t$; the equations give $x_1 = -2s - t$ and $x_3 = -t$:

$$\mathbf{x} = s\begin{pmatrix} -2 \\ 1 \\ 0 \\ 0 \end{pmatrix} + t\begin{pmatrix} -1 \\ 0 \\ -1 \\ 1 \end{pmatrix}$$

These two vectors form a basis of $\text{Null}(A)$; check: $A(-2, 1, 0, 0)^T = (-2 + 2, -4 + 4, -6 + 6) = \mathbf{0}$. Rank 2 plus nullity 2 equals 4 columns.

## Applications

- **Data compression:** low-rank approximations keep the most important directions of a data matrix.
- **Machine learning:** redundant (linearly dependent) features cause unstable models; rank reveals them.
- **Systems of equations:** rank decides consistency and the number of free parameters.
- **Coding theory and networks:** independence of message vectors underlies error-correcting and network codes.

## Common mistakes

- **Using the echelon form's columns as a column-space basis.** Use the original pivot columns.
- **Thinking any spanning set is a basis.** It must also be independent.
- **Confusing rank with the number of non-zero rows of the original matrix.** Count pivots after reduction.
- **Forgetting that more than $n$ vectors in $\mathbb{R}^n$ are dependent.**
- **Mixing up nullity and rank in the theorem.** They add up to the number of columns.

## Revision notes

- Independent: only the trivial combination gives $\mathbf{0}$; test with a pivot in every column.
- Basis: independent and spanning; unique coordinates.
- Dimension: number of vectors in any basis.
- Rank = number of pivots = $\dim \text{Col}(A)$ = $\dim$ row space.
- Column-space basis: original pivot columns; null-space basis from free-variable parameters.
- Rank-nullity: $\text{rank}(A) + \text{nullity}(A) = n$ (columns).

## Practice questions

:::question basic
Are $(1, 2)$ and $(-3, -6)$ linearly independent?
:::answer
No. $(-3, -6) = -3(1, 2)$, so one is a multiple of the other, and they are dependent; they span only a line.
:::

:::question basic
What is the dimension of the subspace of $\mathbb{R}^3$ spanned by $(1, 0, 0)$, $(0, 1, 0)$, and $(1, 1, 0)$?
:::answer
2. The third vector is the sum of the first two, so a basis is $\{(1,0,0), (0,1,0)\}$, and the span is the xy-plane.
:::

:::question intermediate
A $5 \times 7$ matrix has rank 4. What is the dimension of its null space, and of its column space?
:::answer
By rank-nullity, nullity $= 7 - 4 = 3$. The column space has dimension equal to the rank, 4 (a subspace of $\mathbb{R}^5$).
:::

:::question intermediate
For which $k$ are $(1, 1, 0)$, $(0, 1, 1)$, and $(1, 0, k)$ linearly independent?
:::answer
Form the matrix with these columns and compute its determinant: $1(k - 0) - 0 + 1(1 - 0) = k + 1$. The vectors are independent exactly when $k \ne -1$.
:::

:::question advanced
Explain why a $4 \times 6$ matrix cannot have linearly independent columns, and what this means for $A\mathbf{x} = \mathbf{0}$.
:::answer
Its rank is at most 4, the number of rows, so at most 4 of the 6 columns can contain pivots. At least 2 columns are free, so the columns are dependent, and by rank-nullity the null space has dimension at least $6 - 4 = 2$. Hence $A\mathbf{x} = \mathbf{0}$ has infinitely many non-trivial solutions.
:::

## Further learning

- **Next:** *Linear Transformations* connects rank and nullity to images and kernels of maps.
- **Related:** *Principal Component Analysis (PCA)* in Machine Learning finds a low-dimensional basis for data.
