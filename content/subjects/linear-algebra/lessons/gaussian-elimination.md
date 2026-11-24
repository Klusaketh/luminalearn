---
lesson: gaussian-elimination
title: Systems of Linear Equations & Gaussian Elimination
summary: Writing systems of linear equations as augmented matrices, solving them with Gaussian and Gauss-Jordan elimination, reading row echelon forms, and deciding whether a system has one, infinitely many, or no solutions.
minutes: 50
type: theory
objectives:
  - Represent a linear system as an augmented matrix and apply the three elementary row operations
  - Reduce a matrix to row echelon and reduced row echelon form and read off the solution
  - Classify a system as having a unique solution, infinitely many solutions, or none, and express free variables parametrically
review: ai-draft
---
## Introduction

Systems of linear equations appear everywhere: balancing chemical reactions, computing currents in a circuit, fitting models to data, and solving the huge sparse systems at the heart of graphics and simulation. **Gaussian elimination** is the systematic method for solving them, and it is also the engine behind computing inverses, determinants, and ranks. Learning it well gives a concrete foundation for the whole of linear algebra.

**Before you start:** you should be comfortable with solving two equations in two unknowns by substitution or elimination.

## Core theory

### Linear systems and augmented matrices

A system of $m$ linear equations in $n$ unknowns,

$$\begin{aligned} x + y + z &= 6 \\ 2x - y + z &= 3 \\ x + 2y - z &= 2 \end{aligned}$$

is written compactly as $A\mathbf{x} = \mathbf{b}$, or as the **augmented matrix** $[A \mid \mathbf{b}]$ whose rows hold the coefficients and right-hand sides:

$$\left[\begin{array}{ccc|c} 1 & 1 & 1 & 6 \\ 2 & -1 & 1 & 3 \\ 1 & 2 & -1 & 2 \end{array}\right]$$

### Elementary row operations

Three operations change the system's appearance but not its solution set:

1. **Swap** two rows.
2. **Scale** a row by a non-zero constant.
3. **Replace** a row by itself plus a multiple of another row.

### Echelon forms

A matrix is in **row echelon form** (REF) when all-zero rows are at the bottom and each row's first non-zero entry (its **pivot**) lies to the right of the pivot in the row above. **Gaussian elimination** reaches REF by working column by column: choose a pivot, then use replacements to create zeros below it. **Back substitution** then solves from the last equation upwards.

**Reduced row echelon form** (RREF) additionally requires every pivot to be 1 and to be the only non-zero entry in its column. **Gauss-Jordan elimination** continues to RREF, from which the solution can be read directly. The RREF of a matrix is unique.

### Counting solutions

Columns with pivots correspond to **basic variables**; columns without pivots correspond to **free variables**. For a system $[A \mid \mathbf{b}]$:

- If a row reduces to $[0 \; 0 \; \cdots \; 0 \mid c]$ with $c \ne 0$, the system is **inconsistent**: no solution.
- Otherwise, if every variable has a pivot, there is a **unique** solution.
- Otherwise there are **infinitely many** solutions, described by parameters for the free variables.

A homogeneous system $A\mathbf{x} = \mathbf{0}$ always has the trivial solution $\mathbf{0}$, and it has non-trivial solutions exactly when there is a free variable, which is guaranteed when there are more unknowns than equations.

### Cost and pivoting

Elimination on an $n \times n$ system takes about $\frac{2}{3}n^3$ arithmetic operations. In floating-point arithmetic, **partial pivoting** (choosing the largest available pivot in absolute value) avoids dividing by tiny numbers and keeps rounding errors under control; numerical libraries always pivot.

## Worked examples

### Example 1: Three systems, three outcomes

The program below reduces augmented matrices to RREF with exact fractions and reports the pivot columns.

```python
from fractions import Fraction as F

def rref(rows):
    m = [[F(x) for x in row] for row in rows]
    pivot_cols, r = [], 0
    for c in range(len(m[0]) - 1):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        m[r] = [x / m[r][c] for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                m[i] = [a - m[i][c] * b for a, b in zip(m[i], m[r])]
        pivot_cols.append(c)
        r += 1
    return m, pivot_cols

def show(m):
    for row in m:
        print("  [" + "  ".join(f"{str(x):>4}" for x in row) + "]")

systems = {
    "unique": [[1, 1, 1, 6], [2, -1, 1, 3], [1, 2, -1, 2]],
    "infinite": [[1, 2, -1, 3], [2, 4, -2, 6], [1, 0, 1, 1]],
    "none": [[1, 1, 2], [2, 2, 5]],
}
for name, aug in systems.items():
    m, pivots = rref(aug)
    inconsistent = any(all(x == 0 for x in row[:-1]) and row[-1] != 0 for row in m)
    print(name, "| pivots in columns", pivots, "| inconsistent:", inconsistent)
    show(m)
```

Output:

```text
unique | pivots in columns [0, 1, 2] | inconsistent: False
  [   1     0     0     1]
  [   0     1     0     2]
  [   0     0     1     3]
infinite | pivots in columns [0, 1] | inconsistent: False
  [   1     0     1     1]
  [   0     1    -1     1]
  [   0     0     0     0]
none | pivots in columns [0] | inconsistent: True
  [   1     1     2]
  [   0     0     1]
```

- **Unique:** every variable has a pivot, and the RREF reads $x = 1$, $y = 2$, $z = 3$. Check in the original second equation: $2 - 2 + 3 = 3$.
- **Infinite:** column 3 ($z$) has no pivot, so $z = t$ is free. The RREF rows say $x + z = 1$ and $y - z = 1$, so the solutions are $(x, y, z) = (1 - t, 1 + t, t)$ for any real $t$, a line of solutions. The second original equation was just twice the first.
- **None:** the last row says $0 = 1$, which is impossible: the equations $x + y = 2$ and $2x + 2y = 5$ describe parallel lines.

### Example 2: Elimination by hand with back substitution

Solve the first system by hand. Use row 1 to clear column 1: $R_2 \leftarrow R_2 - 2R_1$ and $R_3 \leftarrow R_3 - R_1$:

$$\left[\begin{array}{ccc|c} 1 & 1 & 1 & 6 \\ 0 & -3 & -1 & -9 \\ 0 & 1 & -2 & -4 \end{array}\right]$$

Swap $R_2$ and $R_3$ to get a convenient pivot, then $R_3 \leftarrow R_3 + 3R_2$:

$$\left[\begin{array}{ccc|c} 1 & 1 & 1 & 6 \\ 0 & 1 & -2 & -4 \\ 0 & 0 & -7 & -21 \end{array}\right]$$

This is row echelon form. Back substitution: $-7z = -21$ gives $z = 3$; then $y - 2(3) = -4$ gives $y = 2$; then $x + 2 + 3 = 6$ gives $x = 1$, matching the program.

## Applications

- **Engineering:** circuit analysis (Kirchhoff's laws) and structural statics produce linear systems.
- **Chemistry:** balancing reaction equations is a homogeneous system.
- **Computer graphics and simulation:** large sparse systems are solved millions of times.
- **Machine learning:** least-squares fitting leads to linear systems (the normal equations).

## Common mistakes

- **Arithmetic slips in replacements.** Apply the operation to every entry, including the right-hand side.
- **Scaling a row by zero.** It destroys information and is not an allowed operation.
- **Calling a system inconsistent because of an all-zero row.** A row $[0 \cdots 0 \mid 0]$ is harmless; only $[0 \cdots 0 \mid c \ne 0]$ means no solution.
- **Forgetting free variables.** Express infinitely many solutions with parameters.
- **Dividing by tiny pivots in floating point.** Use partial pivoting.

## Revision notes

- $A\mathbf{x} = \mathbf{b}$ ↔ augmented matrix $[A \mid \mathbf{b}]$.
- Row operations: swap, scale (non-zero), replace with a multiple of another row.
- REF: staircase of pivots; RREF: pivots are 1 and alone in their columns (unique).
- Pivot columns = basic variables; others = free variables.
- No solution iff a row $[0 \cdots 0 \mid c]$ with $c \ne 0$; unique iff no free variables; otherwise infinitely many.
- Elimination costs about $\frac23 n^3$ operations.

## Practice questions

:::question basic
Write the augmented matrix for $3x - y = 5$, $x + 4y = 6$.
:::answer
$\left[\begin{array}{cc|c} 3 & -1 & 5 \\ 1 & 4 & 6 \end{array}\right]$. Each row holds the coefficients of $x$ and $y$ followed by the right-hand side.
:::

:::question basic
An RREF contains the row $[0 \; 0 \; 0 \mid 4]$. What does this tell you?
:::answer
The system is inconsistent: that row represents the equation $0 = 4$, which no values of the variables can satisfy, so there is no solution.
:::

:::question intermediate
Solve $x + 2y = 4$, $3x + 5y = 9$ by elimination.
:::answer
$R_2 \leftarrow R_2 - 3R_1$ gives $-y = -3$, so $y = 3$. Then $x + 6 = 4$ gives $x = -2$. Check: $3(-2) + 5(3) = 9$.
:::

:::question intermediate
A system in 4 unknowns reduces to an RREF with 2 pivots and no inconsistent rows. How many solutions are there, and how many parameters describe them?
:::answer
Infinitely many solutions. There are $4 - 2 = 2$ free variables, so the solution set is described with 2 parameters (geometrically, a plane in $\mathbb{R}^4$).
:::

:::question advanced
Why does a homogeneous system with more unknowns than equations always have a non-trivial solution?
:::answer
Each pivot occupies a different row, so there are at most $m$ pivots for $m$ equations. With $n > m$ unknowns, at least $n - m \ge 1$ columns have no pivot, giving at least one free variable. A homogeneous system is always consistent, so setting a free variable to a non-zero value produces a non-trivial solution.
:::

## Further learning

- **Next:** *Determinants & Matrix Inverses* uses elimination to test invertibility and compute inverses.
- **Related:** *Linear Independence, Basis, Dimension & Rank* interprets pivots as rank.
