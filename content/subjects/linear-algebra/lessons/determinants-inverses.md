---
lesson: determinants-inverses
title: Determinants & Matrix Inverses
summary: Computing determinants by cofactor expansion and by row reduction, their key properties and geometric meaning as a volume scale factor, and computing and using matrix inverses, including the invertible matrix theorem.
minutes: 45
type: theory
objectives:
  - Compute 2 × 2 and 3 × 3 determinants by formula, cofactor expansion, and row reduction
  - Apply determinant properties under row operations, products, transposes, and scaling, and interpret the determinant geometrically
  - Compute inverses with the 2 × 2 formula and Gauss-Jordan elimination, and connect invertibility to determinants and unique solutions
review: ai-draft
---
## Introduction

A square matrix has a single number, its **determinant**, that tells you whether the matrix can be inverted, how it scales areas and volumes, and whether the linear system it represents has a unique solution. The **inverse** matrix undoes the transformation, so $A^{-1}A = I$. Together they answer the basic question "is this transformation reversible, and how?", which underlies solving systems, changing coordinates, and analysing stability.

**Before you start:** you should know matrix multiplication and Gaussian elimination.

## Core theory

### Small determinants

For a $2 \times 2$ matrix,

$$\det\begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc$$

For larger matrices, **cofactor expansion** along any row or column gives

$$\det(A) = \sum_{j} (-1)^{i + j} a_{ij} \det(M_{ij})$$

where $M_{ij}$ is $A$ with row $i$ and column $j$ removed. The signs follow a checkerboard pattern. Expanding along a row or column with many zeros saves work. Cofactor expansion takes about $n!$ operations, so it is only practical for small matrices.

### Properties and row reduction

- Swapping two rows multiplies the determinant by $-1$.
- Scaling a row by $k$ multiplies it by $k$; so $\det(kA) = k^n \det(A)$ for an $n \times n$ matrix.
- Adding a multiple of one row to another leaves it unchanged.
- The determinant of a triangular matrix is the product of its diagonal entries.
- $\det(AB) = \det(A)\det(B)$, $\det(A^T) = \det(A)$, and $\det(A^{-1}) = 1/\det(A)$.

So the efficient method is to row-reduce to triangular form, keeping track of swaps and scalings, and multiply the pivots: $O(n^3)$ work.

### Geometric meaning

$|\det(A)|$ is the factor by which the transformation $\mathbf{x} \mapsto A\mathbf{x}$ scales areas (in 2-D) or volumes (in 3-D); the sign tells whether orientation is preserved or reversed (a reflection gives a negative determinant). A zero determinant means space is flattened into a lower dimension, so information is lost and the transformation cannot be undone.

### Inverses

$A$ is **invertible** if there is a matrix $A^{-1}$ with $AA^{-1} = A^{-1}A = I$. For $2 \times 2$:

$$\begin{pmatrix} a & b \\ c & d \end{pmatrix}^{-1} = \frac{1}{ad - bc}\begin{pmatrix} d & -b \\ -c & a \end{pmatrix}$$

In general, row-reduce $[A \mid I]$; if the left side becomes $I$, the right side is $A^{-1}$; if a zero row appears on the left, $A$ is singular. Useful rules: $(AB)^{-1} = B^{-1}A^{-1}$ (reversed order) and $(A^T)^{-1} = (A^{-1})^T$.

### The invertible matrix theorem

For an $n \times n$ matrix, the following are equivalent: $A$ is invertible; $\det(A) \ne 0$; $A\mathbf{x} = \mathbf{b}$ has exactly one solution for every $\mathbf{b}$; $A\mathbf{x} = \mathbf{0}$ has only the trivial solution; $A$ has $n$ pivots; its columns are linearly independent; its rank is $n$.

In numerical work, one rarely computes $A^{-1}$ explicitly to solve $A\mathbf{x} = \mathbf{b}$: elimination (an LU factorisation) is faster and more accurate.

## Worked examples

### Example 1: Determinant and inverse of a 3 × 3 matrix

Let $A = \begin{pmatrix} 2 & 1 & 3 \\ 0 & -1 & 4 \\ 1 & 2 & 0 \end{pmatrix}$. By cofactor expansion along the first column (which has a zero):

$$\det A = 2\det\begin{pmatrix} -1 & 4 \\ 2 & 0 \end{pmatrix} - 0 + 1\det\begin{pmatrix} 1 & 3 \\ -1 & 4 \end{pmatrix} = 2(0 - 8) + (4 + 3) = -9$$

The program computes the same determinant by row reduction and the inverse by Gauss-Jordan elimination, with exact fractions.

```python
from fractions import Fraction as F

def det(m):
    m = [[F(x) for x in row] for row in m]
    n, sign, result = len(m), 1, F(1)
    for c in range(n):
        p = next((r for r in range(c, n) if m[r][c] != 0), None)
        if p is None:
            return F(0)
        if p != c:
            m[c], m[p] = m[p], m[c]
            sign = -sign
        result *= m[c][c]
        for r in range(c + 1, n):
            factor = m[r][c] / m[c][c]
            m[r] = [a - factor * b for a, b in zip(m[r], m[c])]
    return sign * result

def inverse(m):
    n = len(m)
    aug = [[F(x) for x in row] + [F(int(i == j)) for j in range(n)] for i, row in enumerate(m)]
    for c in range(n):
        p = next(r for r in range(c, n) if aug[r][c] != 0)
        aug[c], aug[p] = aug[p], aug[c]
        aug[c] = [x / aug[c][c] for x in aug[c]]
        for r in range(n):
            if r != c:
                aug[r] = [a - aug[r][c] * b for a, b in zip(aug[r], aug[c])]
    return [row[n:] for row in aug]

A = [[2, 1, 3], [0, -1, 4], [1, 2, 0]]
print("det(A) =", det(A))
Ainv = inverse(A)
print("A^-1 =", [[str(x) for x in row] for row in Ainv])
product = [[sum(F(A[i][k]) * Ainv[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
print("A * A^-1 is identity:", product == [[F(int(i == j)) for j in range(3)] for i in range(3)])
print("det(2A) =", det([[2 * x for x in row] for row in A]), "= 2^3 * det(A)")
print("singular example det:", det([[1, 2, 3], [2, 4, 6], [1, 0, 1]]))
```

Output:

```text
det(A) = -9
A^-1 = [['8/9', '-2/3', '-7/9'], ['-4/9', '1/3', '8/9'], ['-1/9', '1/3', '2/9']]
A * A^-1 is identity: True
det(2A) = -72 = 2^3 * det(A)
singular example det: 0
```

Since $\det A = -9 \ne 0$, $A$ is invertible, and multiplying back gives the identity. Scaling the $3 \times 3$ matrix by 2 multiplies the determinant by $2^3 = 8$. The last matrix has a row equal to twice another, so its determinant is 0 and it has no inverse.

### Example 2: The 2 × 2 formula and solving a system

Solve $3x + 2y = 7$, $x + y = 3$ using the inverse.

$A = \begin{pmatrix} 3 & 2 \\ 1 & 1 \end{pmatrix}$, $\det A = 3 - 2 = 1$, so $A^{-1} = \begin{pmatrix} 1 & -2 \\ -1 & 3 \end{pmatrix}$, and

$$\mathbf{x} = A^{-1}\mathbf{b} = \begin{pmatrix} 1 & -2 \\ -1 & 3 \end{pmatrix}\begin{pmatrix} 7 \\ 3 \end{pmatrix} = \begin{pmatrix} 1 \\ 2 \end{pmatrix}$$

Check: $3 + 4 = 7$ and $1 + 2 = 3$. Geometrically, $A$ maps the unit square to a parallelogram of area $|\det A| = 1$, so it preserves area while shearing and stretching.

## Applications

- **Solving systems:** invertibility guarantees unique solutions.
- **Computer graphics:** inverse transformations map screen coordinates back to world coordinates.
- **Calculus:** the Jacobian determinant rescales areas in a change of variables.
- **Cryptography:** the Hill cipher needs a key matrix invertible modulo 26.

## Common mistakes

- **$\det(A + B) = \det A + \det B$.** False in general; only products behave nicely.
- **$\det(kA) = k\det A$.** It is $k^n \det A$ for an $n \times n$ matrix.
- **Wrong order in $(AB)^{-1}$.** It is $B^{-1}A^{-1}$.
- **Forgetting sign changes from row swaps.**
- **Using cofactor expansion on large matrices.** Row reduction is vastly faster.

## Revision notes

- $2 \times 2$: $ad - bc$; cofactor expansion with checkerboard signs.
- Row swap: ×(−1); row scale by $k$: ×$k$; row replacement: unchanged; triangular: product of diagonal.
- $\det(AB) = \det A \det B$; $\det(A^T) = \det A$; $\det(kA) = k^n \det A$.
- $|\det A|$ = area/volume scale factor; 0 means collapse to lower dimension.
- Inverse by $[A \mid I] \to [I \mid A^{-1}]$; $2 \times 2$ formula; $(AB)^{-1} = B^{-1}A^{-1}$.
- Invertible ⇔ $\det \ne 0$ ⇔ $n$ pivots ⇔ unique solutions ⇔ independent columns.

## Practice questions

:::question basic
Compute $\det\begin{pmatrix} 4 & 7 \\ 2 & 5 \end{pmatrix}$ and the inverse.
:::answer
$\det = 20 - 14 = 6$. The inverse is $\frac16\begin{pmatrix} 5 & -7 \\ -2 & 4 \end{pmatrix}$.
:::

:::question basic
If $\det A = 3$ for a $4 \times 4$ matrix, what is $\det(2A)$?
:::answer
$\det(2A) = 2^4 \det A = 16 \times 3 = 48$, because scaling the matrix scales each of its 4 rows by 2.
:::

:::question intermediate
If $\det A = 5$ and $\det B = -2$ for $3 \times 3$ matrices, find $\det(AB)$, $\det(A^{-1})$, and $\det(A^T B^2)$.
:::answer
$\det(AB) = 5 \times (-2) = -10$. $\det(A^{-1}) = 1/5$. $\det(A^T B^2) = \det(A)\det(B)^2 = 5 \times 4 = 20$.
:::

:::question intermediate
For which values of $k$ is $\begin{pmatrix} 1 & k \\ k & 4 \end{pmatrix}$ not invertible?
:::answer
$\det = 4 - k^2$, which is zero when $k = 2$ or $k = -2$. For those values the matrix is singular; for all other $k$ it is invertible.
:::

:::question advanced
Explain geometrically why a matrix with determinant 0 cannot have an inverse.
:::answer
A zero determinant means the transformation squashes space into a lower dimension, for example the whole plane onto a line. Then many different input vectors map to the same output vector, so there is no way to determine which input produced a given output: the mapping is not one-to-one, and no inverse transformation can exist.
:::

## Further learning

- **Next:** *Vector Spaces & Matrix Multiplication* builds the geometric picture of what matrices do.
- **Related:** *Systems of Linear Equations & Gaussian Elimination* provides the row operations used here.
