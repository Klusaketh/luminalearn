---
lesson: eigenvalue-decomposition-svd
title: Eigenvalue Decomposition & SVD
summary: Eigenvalues and eigenvectors and how to compute them, diagonalisation and matrix powers, the spectral theorem for symmetric matrices, power iteration, and the singular value decomposition with its geometric meaning and uses.
minutes: 50
type: theory
objectives:
  - Find eigenvalues from the characteristic polynomial and the corresponding eigenvectors, and verify $A\mathbf{v} = \lambda\mathbf{v}$
  - Diagonalise a matrix and use $A = PDP^{-1}$ to compute powers, and state the spectral theorem for symmetric matrices
  - Explain the singular value decomposition geometrically and describe applications such as low-rank approximation and PCA
review: ai-draft
---
## Introduction

Most vectors change direction when a matrix acts on them, but some special vectors are only stretched or shrunk: the **eigenvectors**, with stretch factors called **eigenvalues**. They reveal the "natural axes" of a transformation, and they explain long-term behaviour: population models, Google's PageRank, vibrations of a bridge, and the stability of numerical methods all come down to eigenvalues. The **singular value decomposition** (SVD) extends the idea to every matrix, even non-square ones, and underlies data compression, recommender systems, and principal component analysis.

**Before you start:** you should know determinants, matrix inverses, bases, and orthogonality.

## Core theory

### Eigenvalues and eigenvectors

A non-zero vector $\mathbf{v}$ is an **eigenvector** of a square matrix $A$ with **eigenvalue** $\lambda$ if

$$A\mathbf{v} = \lambda\mathbf{v}$$

Rewriting as $(A - \lambda I)\mathbf{v} = \mathbf{0}$, a non-zero solution exists exactly when $A - \lambda I$ is singular:

$$\det(A - \lambda I) = 0$$

the **characteristic equation**. For a $2 \times 2$ matrix it is $\lambda^2 - (\text{tr}A)\lambda + \det A = 0$. In general, the sum of the eigenvalues equals the trace and their product equals the determinant. For each eigenvalue, the eigenvectors (with $\mathbf{0}$) form the **eigenspace**, the null space of $A - \lambda I$. Real matrices can have complex eigenvalues: a 90° rotation turns every real vector, so it has no real eigenvectors.

### Diagonalisation and powers

If an $n \times n$ matrix has $n$ linearly independent eigenvectors (guaranteed when its eigenvalues are distinct), then

$$A = PDP^{-1}$$

where the columns of $P$ are eigenvectors and $D$ is diagonal with the eigenvalues. Then $A^k = PD^kP^{-1}$, and $D^k$ simply raises each eigenvalue to the $k$-th power. This explains long-run behaviour: as $k$ grows, the largest eigenvalue in absolute value dominates.

### Symmetric matrices and the spectral theorem

If $A = A^T$ (real symmetric), then all its eigenvalues are real and eigenvectors for different eigenvalues are orthogonal; $A$ can be written as

$$A = QDQ^T$$

with $Q$ orthogonal. Covariance matrices are symmetric, which is why PCA works with orthogonal principal axes.

### Power iteration

Repeatedly multiplying a starting vector by $A$ and normalising makes it line up with the eigenvector of the dominant eigenvalue (the one with largest absolute value), provided it is strictly dominant. The **Rayleigh quotient** $\mathbf{x}^TA\mathbf{x}/\mathbf{x}^T\mathbf{x}$ then estimates that eigenvalue. PageRank is computed essentially this way. Practical libraries use the more sophisticated QR algorithm.

### The singular value decomposition

Every $m \times n$ matrix factors as

$$A = U\Sigma V^T$$

where $U$ ($m \times m$) and $V$ ($n \times n$) are orthogonal and $\Sigma$ is diagonal with non-negative **singular values** $\sigma_1 \ge \sigma_2 \ge \cdots \ge 0$. Geometrically, any linear map is a rotation or reflection ($V^T$), then a stretch along the axes ($\Sigma$), then another rotation or reflection ($U$): it maps the unit circle to an ellipse whose semi-axes have lengths $\sigma_i$. The singular values are the square roots of the eigenvalues of $A^TA$, the number of non-zero ones is the rank, and for a square matrix their product is $|\det A|$.

**Low-rank approximation:** keeping only the $k$ largest singular values gives the best rank-$k$ approximation of $A$ (the Eckart-Young theorem), which compresses images and powers recommender systems and latent semantic analysis. Applying the SVD to a centred data matrix gives **principal component analysis**.

## Worked examples

### Example 1: Eigenvalues, power iteration, powers, and singular values

The program finds the eigenvalues of $A = \begin{pmatrix} 4 & 1 \\ 2 & 3 \end{pmatrix}$ from its characteristic polynomial, checks the eigenvectors, estimates the dominant eigenvalue by power iteration, computes $A^{10}$ by diagonalisation, and finds the singular values of $S = \begin{pmatrix} 3 & 0 \\ 4 & 5 \end{pmatrix}$ from $S^TS$.

```python
from math import sqrt

A = [[4, 1], [2, 3]]
tr, det = A[0][0] + A[1][1], A[0][0] * A[1][1] - A[0][1] * A[1][0]
disc = sqrt(tr * tr - 4 * det)
lams = [(tr + disc) / 2, (tr - disc) / 2]
print("characteristic polynomial: l^2 -", tr, "l +", det, "| eigenvalues:", lams)
for lam in lams:
    v = [A[0][1], lam - A[0][0]]
    Av = [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]]
    print(f"lambda={lam:g}: v={v}, Av={Av}, lambda*v={[lam * x for x in v]}")

x = [1.0, 0.0]
for _ in range(50):
    y = [A[0][0] * x[0] + A[0][1] * x[1], A[1][0] * x[0] + A[1][1] * x[1]]
    norm = sqrt(y[0] ** 2 + y[1] ** 2)
    x = [y[0] / norm, y[1] / norm]
rayleigh = (x[0] * (A[0][0] * x[0] + A[0][1] * x[1]) + x[1] * (A[1][0] * x[0] + A[1][1] * x[1]))
print(f"power iteration estimate of the largest eigenvalue: {rayleigh:.6f}")

P = [[1, 1], [1, -2]]
Pinv = [[2 / 3, 1 / 3], [1 / 3, -1 / 3]]
def mul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
A10 = mul(mul(P, [[5 ** 10, 0], [0, 2 ** 10]]), Pinv)
direct = A
for _ in range(9):
    direct = mul(direct, A)
print("A^10 via diagonalisation:", [[round(v) for v in row] for row in A10], "| direct:", direct)

S = [[3, 0], [4, 5]]
StS = [[sum(S[k][i] * S[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
t, d = StS[0][0] + StS[1][1], StS[0][0] * StS[1][1] - StS[0][1] * StS[1][0]
eig = [(t + sqrt(t * t - 4 * d)) / 2, (t - sqrt(t * t - 4 * d)) / 2]
sigmas = [sqrt(e) for e in eig]
print("singular values of S:", [round(s, 4) for s in sigmas], "| product =", round(sigmas[0] * sigmas[1], 4), "= |det S| =", abs(S[0][0] * S[1][1] - S[0][1] * S[1][0]))
```

Output:

```text
characteristic polynomial: l^2 - 7 l + 10 | eigenvalues: [5.0, 2.0]
lambda=5: v=[1, 1.0], Av=[5.0, 5.0], lambda*v=[5.0, 5.0]
lambda=2: v=[1, -2.0], Av=[2.0, -4.0], lambda*v=[2.0, -4.0]
power iteration estimate of the largest eigenvalue: 5.000000
A^10 via diagonalisation: [[6510758, 3254867], [6509734, 3255891]] | direct: [[6510758, 3254867], [6509734, 3255891]]
singular values of S: [6.7082, 2.2361] | product = 15.0 = |det S| = 15
```

The characteristic polynomial $\lambda^2 - 7\lambda + 10 = (\lambda - 5)(\lambda - 2)$ gives eigenvalues 5 and 2; their sum is the trace 7 and their product the determinant 10. The eigenvectors $(1, 1)$ and $(1, -2)$ are only scaled by $A$. Fifty power iterations recover the dominant eigenvalue 5. With $P$ holding the eigenvectors, $A^{10} = PD^{10}P^{-1}$ matches 9 explicit multiplications. The singular values of $S$ are $\sqrt{45} \approx 6.708$ and $\sqrt{5} \approx 2.236$, and their product equals $|\det S| = 15$.

### Example 2: Eigenvectors of a symmetric matrix by hand

Find the eigenvalues and eigenvectors of $B = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}$.

The characteristic equation is $\lambda^2 - 4\lambda + 3 = 0$, so $\lambda = 3$ or $\lambda = 1$.

- For $\lambda = 3$: $B - 3I = \begin{pmatrix} -1 & 1 \\ 1 & -1 \end{pmatrix}$, whose null space is spanned by $(1, 1)$.
- For $\lambda = 1$: $B - I = \begin{pmatrix} 1 & 1 \\ 1 & 1 \end{pmatrix}$, whose null space is spanned by $(1, -1)$.

The eigenvectors are orthogonal, $(1, 1) \cdot (1, -1) = 0$, as the spectral theorem promises. Normalising gives $Q = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$ and $B = Q\begin{pmatrix} 3 & 0 \\ 0 & 1 \end{pmatrix}Q^T$: the matrix stretches by 3 along the diagonal direction $(1, 1)$ and leaves the perpendicular direction unchanged. Since $B$ is symmetric with positive eigenvalues, its singular values are the same as its eigenvalues, 3 and 1.

## Applications

- **PageRank and Markov chains:** the stationary distribution is an eigenvector with eigenvalue 1.
- **Principal component analysis:** eigenvectors of the covariance matrix (or the SVD of the data) give the directions of greatest variance.
- **Image compression and recommender systems:** truncated SVD keeps the most important structure.
- **Engineering:** natural frequencies of vibrating structures and stability of dynamical systems are eigenvalues.

## Common mistakes

- **Accepting the zero vector as an eigenvector.** Eigenvectors must be non-zero.
- **Assuming every matrix is diagonalisable.** $\begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix}$ has only one independent eigenvector.
- **Confusing singular values with eigenvalues.** They coincide only for symmetric positive semi-definite matrices.
- **Expecting real eigenvalues for every real matrix.** Rotations have complex eigenvalues.
- **Using power iteration without a dominant eigenvalue.** It may fail to converge.

## Revision notes

- $A\mathbf{v} = \lambda\mathbf{v}$, $\mathbf{v} \ne \mathbf{0}$; eigenvalues solve $\det(A - \lambda I) = 0$.
- $2 \times 2$: $\lambda^2 - (\text{tr}A)\lambda + \det A = 0$; sum = trace, product = determinant.
- Diagonalisable: $A = PDP^{-1}$; $A^k = PD^kP^{-1}$.
- Symmetric: real eigenvalues, orthogonal eigenvectors, $A = QDQ^T$.
- Power iteration converges to the dominant eigenvector; Rayleigh quotient estimates $\lambda$.
- SVD: $A = U\Sigma V^T$; $\sigma_i = \sqrt{\text{eig}(A^TA)}$; rank = number of non-zero $\sigma_i$; truncation gives best low-rank approximation.

## Practice questions

:::question basic
Verify that $(1, 2)$ is an eigenvector of $\begin{pmatrix} 3 & 1 \\ 2 & 4 \end{pmatrix}$ and find its eigenvalue.
:::answer
$\begin{pmatrix} 3 & 1 \\ 2 & 4 \end{pmatrix}\begin{pmatrix} 1 \\ 2 \end{pmatrix} = \begin{pmatrix} 5 \\ 10 \end{pmatrix} = 5\begin{pmatrix} 1 \\ 2 \end{pmatrix}$, so it is an eigenvector with eigenvalue 5.
:::

:::question basic
What are the eigenvalues of a triangular matrix such as $\begin{pmatrix} 2 & 7 \\ 0 & -3 \end{pmatrix}$?
:::answer
The diagonal entries, 2 and $-3$. For a triangular matrix, $\det(A - \lambda I)$ is the product of $(a_{ii} - \lambda)$ terms.
:::

:::question intermediate
A $3 \times 3$ matrix has eigenvalues 2, 3, and $-1$. What are its trace and determinant, and is it invertible?
:::answer
Trace $= 2 + 3 - 1 = 4$ and determinant $= 2 \times 3 \times (-1) = -6$. Since the determinant is non-zero (no eigenvalue is 0), it is invertible.
:::

:::question intermediate
If $A = PDP^{-1}$ with $D = \text{diag}(0.5, 1)$, what happens to $A^k\mathbf{x}$ as $k$ grows?
:::answer
$A^k = PD^kP^{-1}$ with $D^k = \text{diag}(0.5^k, 1)$. The component of $\mathbf{x}$ along the first eigenvector shrinks to zero, while the component along the eigenvector with eigenvalue 1 stays fixed, so $A^k\mathbf{x}$ converges to that component: the long-run state lies along the eigenvector for eigenvalue 1, as in a Markov chain approaching its stationary distribution.
:::

:::question advanced
Explain how the SVD gives the best rank-1 approximation of a matrix and why this is useful for compressing an image.
:::answer
Writing $A = \sum_i \sigma_i\mathbf{u}_i\mathbf{v}_i^T$, the term $\sigma_1\mathbf{u}_1\mathbf{v}_1^T$ is, by the Eckart-Young theorem, the rank-1 matrix closest to $A$ in the Frobenius and spectral norms, because it captures the direction of greatest stretch. An $m \times n$ grey-scale image stored with the top $k$ terms needs only $k(m + n + 1)$ numbers instead of $mn$; since singular values of natural images decay quickly, a small $k$ keeps most of the visible structure while greatly reducing storage.
:::

## Further learning

- **Next:** *Principal Component Analysis (PCA)* in Machine Learning applies these decompositions to data.
- **Related:** *Gradients, Jacobians & Hessians* in Calculus uses eigenvalues of the Hessian to classify critical points.
