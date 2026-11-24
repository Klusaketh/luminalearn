---
lesson: iterative-linear-systems
title: Iterative Methods for Linear Systems
summary: Solving large linear systems with the Jacobi and Gauss-Seidel iterative methods, convergence conditions such as diagonal dominance, stopping criteria, and when iterative methods are preferable to direct LU factorisation.
minutes: 50
type: theory
objectives:
  - Apply the Jacobi and Gauss-Seidel methods to a linear system
  - Determine convergence using strict diagonal dominance and explain the role of the iteration matrix's spectral radius
  - Compare iterative methods with LU factorisation in cost, memory, and suitability for large sparse systems
review: ai-draft
---
## Introduction

Simulating heat flow, structural stress, or fluid motion produces linear systems with millions of unknowns, but each equation involves only a handful of neighbouring variables: the matrices are **sparse**. Direct elimination would fill in the zeros and run out of memory. **Iterative methods** instead start from a guess and improve it repeatedly, touching only the non-zero entries. Jacobi and Gauss-Seidel are the classic examples and the starting point for the more powerful methods used in scientific computing.

**Before you start:** you should know Gaussian elimination, matrix-vector multiplication, and eigenvalues at a basic level.

## Core theory

### Direct versus iterative methods

**Direct methods** such as Gaussian elimination and **LU factorisation** ($A = LU$, then two triangular solves) compute the exact answer, up to round-off, in a fixed $O(n^3)$ operations for a dense matrix. Once factorised, extra right-hand sides cost only $O(n^2)$ each. **Iterative methods** produce a sequence of approximations that converge to the solution; each iteration costs about one matrix-vector product, $O(\text{non-zeros})$, and the method can stop as soon as the accuracy is sufficient.

### The Jacobi method

Solve the $i$-th equation for $x_i$, using the **previous** iterate for all other unknowns:

$$x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j \ne i} a_{ij}x_j^{(k)}\right)$$

All components are updated simultaneously, which makes Jacobi easy to parallelise.

### The Gauss-Seidel method

Use each new value as soon as it is computed:

$$x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j < i} a_{ij}x_j^{(k+1)} - \sum_{j > i} a_{ij}x_j^{(k)}\right)$$

It needs only one vector of storage and typically converges about twice as fast as Jacobi, but the updates are sequential. **Successive over-relaxation** (SOR) blends each Gauss-Seidel update with the old value using a factor $\omega$, often converging much faster with a well-chosen $\omega$ between 1 and 2.

### Convergence

Both methods can be written as $\mathbf{x}^{(k+1)} = G\mathbf{x}^{(k)} + \mathbf{c}$ for an **iteration matrix** $G$. They converge for every starting guess exactly when the **spectral radius** $\rho(G)$, the largest absolute eigenvalue, is less than 1, and the error shrinks roughly by a factor $\rho(G)$ per iteration. A simple sufficient condition: if $A$ is **strictly diagonally dominant**,

$$|a_{ii}| > \sum_{j \ne i}|a_{ij}| \quad \text{for every row } i$$

then both Jacobi and Gauss-Seidel converge. Gauss-Seidel also converges for symmetric positive definite matrices. Reordering equations to put large coefficients on the diagonal can turn a divergent iteration into a convergent one.

### Stopping criteria

Stop when the change between iterates, $\|\mathbf{x}^{(k+1)} - \mathbf{x}^{(k)}\|$, or the **residual** $\|\mathbf{b} - A\mathbf{x}^{(k)}\|$ falls below a tolerance (often relative to $\|\mathbf{b}\|$), with a cap on the number of iterations. For very large problems, **Krylov methods** such as conjugate gradient (for symmetric positive definite matrices) and GMRES, combined with preconditioning, converge far faster than Jacobi or Gauss-Seidel.

## Worked examples

### Example 1: Jacobi versus Gauss-Seidel

Solve

$$\begin{aligned} 10x_1 - x_2 + 2x_3 &= 6 \\ -x_1 + 11x_2 - x_3 &= 22 \\ 2x_1 - x_2 + 10x_3 &= -10 \end{aligned}$$

whose exact solution is $(1, 2, -1)$. The matrix is strictly diagonally dominant (10 > 3, 11 > 2, 10 > 3), so both methods converge from the zero vector.

```python
A = [[10, -1, 2], [-1, 11, -1], [2, -1, 10]]
b = [6, 22, -10]

def jacobi(A, b, iters):
    x = [0.0] * len(b)
    for _ in range(iters):
        x = [(b[i] - sum(A[i][j] * x[j] for j in range(len(b)) if j != i)) / A[i][i] for i in range(len(b))]
    return x

def gauss_seidel(A, b, iters):
    x = [0.0] * len(b)
    for _ in range(iters):
        for i in range(len(b)):
            x[i] = (b[i] - sum(A[i][j] * x[j] for j in range(len(b)) if j != i)) / A[i][i]
    return x

solution = [1.0, 2.0, -1.0]
for iters in (5, 10, 20):
    ej = max(abs(a - s) for a, s in zip(jacobi(A, b, iters), solution))
    eg = max(abs(a - s) for a, s in zip(gauss_seidel(A, b, iters), solution))
    print(f"{iters:>2} iterations: Jacobi error {ej:.1e}, Gauss-Seidel error {eg:.1e}")
dominant = all(abs(A[i][i]) > sum(abs(A[i][j]) for j in range(3) if j != i) for i in range(3))
print("strictly diagonally dominant:", dominant)
print("Gauss-Seidel after 20 iterations:", [round(v, 6) for v in gauss_seidel(A, b, 20)])
```

Output:

```text
 5 iterations: Jacobi error 1.1e-03, Gauss-Seidel error 1.3e-06
10 iterations: Jacobi error 1.2e-06, Gauss-Seidel error 7.9e-14
20 iterations: Jacobi error 2.2e-12, Gauss-Seidel error 0.0e+00
strictly diagonally dominant: True
Gauss-Seidel after 20 iterations: [1.0, 2.0, -1.0]
```

Gauss-Seidel converges much faster: after 10 iterations its error is about $10^{-13}$, while Jacobi's is about $10^{-6}$; Jacobi needs about twice as many iterations for the same accuracy. Both rely only on the matrix entries, so for a sparse matrix each iteration is cheap.

### Example 2: One Jacobi iteration by hand, and a divergent ordering

For the system above from $\mathbf{x}^{(0)} = (0, 0, 0)$, one Jacobi step gives

$$x_1 = \frac{6}{10} = 0.6, \quad x_2 = \frac{22}{11} = 2, \quad x_3 = \frac{-10}{10} = -1$$

while one Gauss-Seidel step uses the new values immediately: $x_1 = 0.6$, then $x_2 = \frac{22 + 0.6 + 0}{11} \approx 2.0545$, then $x_3 = \frac{-10 - 2(0.6) + 2.0545}{10} \approx -0.9145$.

Now consider the system $x + 3y = 4$, $2x + y = 3$ (solution $(1, 1)$). Its matrix is not diagonally dominant, and Jacobi iteration $x \leftarrow 4 - 3y$, $y \leftarrow 3 - 2x$ diverges: from $(0, 0)$ it gives $(4, 3)$, $(-5, -5)$, $(19, 13)$, and so on, growing without bound. Swapping the equations, $2x + y = 3$ and $x + 3y = 4$, makes the matrix diagonally dominant (2 > 1, 3 > 1), and the iteration $x \leftarrow \frac{3 - y}{2}$, $y \leftarrow \frac{4 - x}{3}$ converges to $(1, 1)$.

## Applications

- **Partial differential equations:** heat, diffusion, and electrostatics on grids produce large sparse systems.
- **Structural engineering:** finite-element models with millions of unknowns.
- **Web and network analysis:** PageRank is computed by a Jacobi-like iteration.
- **Machine learning and graphics:** iterative solvers inside optimisation and physics simulation.

## Common mistakes

- **Using old values in Gauss-Seidel.** Each component must use the newest values available.
- **Assuming every system converges.** Check diagonal dominance or the spectral radius; reorder rows if needed.
- **Stopping on a fixed iteration count only.** Monitor the residual or change.
- **Using iterative methods for small dense systems.** LU factorisation is simpler and exact.
- **Dividing by zero diagonal entries.** Rearrange equations so diagonals are non-zero.

## Revision notes

- Direct (LU): $O(n^3)$ once, exact up to round-off; good for small or dense systems.
- Jacobi: update all components from the previous iterate; parallel-friendly.
- Gauss-Seidel: use new values immediately; usually about twice as fast; SOR accelerates it.
- Converges for any start iff $\rho(G) < 1$; strict diagonal dominance is sufficient.
- Stop on residual or change with an iteration cap.
- Large sparse systems: iterative methods; best-in-class are preconditioned Krylov methods (CG, GMRES).

## Practice questions

:::question basic
Is the matrix $\begin{pmatrix} 5 & 2 & 1 \\ 1 & 4 & 2 \\ 2 & 1 & 6 \end{pmatrix}$ strictly diagonally dominant?
:::answer
Yes. Row 1: $5 > 2 + 1$; row 2: $4 > 1 + 2$; row 3: $6 > 2 + 1$. So Jacobi and Gauss-Seidel are guaranteed to converge.
:::

:::question basic
What is the main practical difference between the Jacobi and Gauss-Seidel updates?
:::answer
Jacobi computes every new component from the previous iterate only, so all components can be updated in parallel. Gauss-Seidel uses each newly computed component immediately in the later updates, which usually speeds convergence and saves memory but makes the updates sequential.
:::

:::question intermediate
Perform one Gauss-Seidel iteration from $(0, 0)$ for $4x - y = 3$, $x + 5y = 6$.
:::answer
$x = \frac{3 + 0}{4} = 0.75$, then $y = \frac{6 - 0.75}{5} = 1.05$. The exact solution is $(1, 1)$, which further iterations approach.
:::

:::question intermediate
Why are iterative methods preferred for very large sparse systems?
:::answer
Each iteration needs only the non-zero entries, so time and memory grow with the number of non-zeros, and the iteration can stop at the accuracy needed. Direct elimination on a sparse matrix creates fill-in, turning zeros into non-zeros, which can make memory and $O(n^3)$ time impractical for millions of unknowns.
:::

:::question advanced
If the Jacobi iteration matrix has spectral radius 0.9, roughly how many iterations reduce the error by a factor of $10^6$? What if it were 0.5?
:::answer
The error shrinks by about $\rho$ per iteration, so we need $\rho^k \le 10^{-6}$, that is $k \ge \frac{6}{-\log_{10}\rho}$. For $\rho = 0.9$, $-\log_{10} 0.9 \approx 0.0458$, giving about 132 iterations. For $\rho = 0.5$, $-\log_{10} 0.5 \approx 0.301$, giving about 20 iterations. The spectral radius controls the speed dramatically.
:::

## Further learning

- **Next:** revisit *Errors, Floating-Point Arithmetic & Stability* to see how conditioning limits the accuracy of any solver.
- **Related:** *Systems of Linear Equations & Gaussian Elimination* in Linear Algebra covers the direct method these iterations complement.
