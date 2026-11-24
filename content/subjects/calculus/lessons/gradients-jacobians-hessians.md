---
lesson: gradients-jacobians-hessians
title: Gradients, Jacobians & Hessians
summary: Partial derivatives, the gradient as the direction of steepest ascent, directional derivatives, the Jacobian matrix of vector-valued functions, the Hessian and second-order Taylor approximation, classifying critical points including saddle points, and gradient descent.
minutes: 45
type: theory
objectives:
  - Compute partial derivatives, gradients, and directional derivatives, and interpret the gradient geometrically
  - Build Jacobian and Hessian matrices and use the Hessian to classify critical points as minima, maxima, or saddle points
  - Explain and apply gradient descent to minimise a function of several variables
review: ai-draft
---
## Introduction

Most quantities depend on many inputs: a model's loss depends on millions of weights, a building's temperature on position and time, a company's profit on several prices. **Multivariable calculus** generalises derivatives to such functions. The **gradient** points uphill, the **Jacobian** describes how a vector-valued map stretches space, and the **Hessian** captures curvature. Together they power optimisation algorithms such as gradient descent, which trains virtually every neural network.

**Before you start:** you should know single-variable derivatives, the chain rule, matrices, and eigenvalues at a basic level.

## Core theory

### Partial derivatives

For $f(x, y)$, the **partial derivative** $\frac{\partial f}{\partial x}$ is the derivative with respect to $x$ while $y$ is held constant; similarly for $y$. For $f(x, y) = x^2y + \sin y$: $f_x = 2xy$ and $f_y = x^2 + \cos y$. Second partials include $f_{xx}$, $f_{yy}$, and the mixed partials $f_{xy}$ and $f_{yx}$, which are equal for smooth functions (Clairaut's theorem).

### The gradient and directional derivatives

The **gradient** collects the partial derivatives into a vector:

$$\nabla f = \left(\frac{\partial f}{\partial x_1}, \dots, \frac{\partial f}{\partial x_n}\right)$$

The rate of change of $f$ in the direction of a unit vector $\mathbf{u}$ is the **directional derivative** $D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u}$. Since $\nabla f \cdot \mathbf{u} = \|\nabla f\|\cos\theta$, it is largest when $\mathbf{u}$ points along $\nabla f$. So the gradient points in the direction of **steepest ascent**, its length is the steepest slope, $-\nabla f$ is the direction of steepest descent, and the gradient is perpendicular to level curves (contour lines).

### The Jacobian

For a vector-valued function $\mathbf{F}: \mathbb{R}^n \to \mathbb{R}^m$, the **Jacobian** is the $m \times n$ matrix of all first partial derivatives:

$$J = \begin{pmatrix} \frac{\partial F_1}{\partial x_1} & \cdots & \frac{\partial F_1}{\partial x_n} \\ \vdots & & \vdots \\ \frac{\partial F_m}{\partial x_1} & \cdots & \frac{\partial F_m}{\partial x_n} \end{pmatrix}$$

It is the best linear approximation of $\mathbf{F}$ near a point: $\mathbf{F}(\mathbf{x} + \Delta\mathbf{x}) \approx \mathbf{F}(\mathbf{x}) + J\Delta\mathbf{x}$. The multivariable chain rule says the Jacobian of a composition is the product of the Jacobians, which is the matrix form of backpropagation. For a change of variables in an integral, $|\det J|$ is the area or volume scaling factor; for polar coordinates it is $r$.

### The Hessian and second-order approximation

For a scalar function, the **Hessian** is the symmetric matrix of second partial derivatives, $H_{ij} = \frac{\partial^2 f}{\partial x_i \partial x_j}$. The second-order Taylor approximation is

$$f(\mathbf{x} + \Delta\mathbf{x}) \approx f(\mathbf{x}) + \nabla f \cdot \Delta\mathbf{x} + \frac12\Delta\mathbf{x}^T H\,\Delta\mathbf{x}$$

### Classifying critical points

At a **critical point**, $\nabla f = \mathbf{0}$. The Hessian decides its type:

- all eigenvalues positive (**positive definite**): local **minimum**;
- all eigenvalues negative: local **maximum**;
- eigenvalues of both signs: **saddle point**, a minimum along some directions and a maximum along others;
- some zero eigenvalues: the test is inconclusive.

For two variables, with $D = f_{xx}f_{yy} - f_{xy}^2 = \det H$: $D > 0$ and $f_{xx} > 0$ gives a minimum; $D > 0$ and $f_{xx} < 0$ a maximum; $D < 0$ a saddle.

### Gradient descent

To minimise $f$, start somewhere and repeatedly step against the gradient:

$$\mathbf{x}_{k+1} = \mathbf{x}_k - \eta\,\nabla f(\mathbf{x}_k)$$

where $\eta$ is the **learning rate**. Too small and progress is slow; too large and the iterates overshoot or diverge. For a quadratic function, convergence requires $\eta < 2/\lambda_{\max}$, where $\lambda_{\max}$ is the largest Hessian eigenvalue. In high-dimensional machine-learning problems, saddle points are far more common than local minima.

## Worked examples

### Example 1: Gradient descent and the Hessian test

Minimise $f(x, y) = x^2 + 3y^2 - 2xy - 4x$.

The gradient is $\nabla f = (2x - 2y - 4,\; 6y - 2x)$. Setting it to zero: $6y = 2x$ gives $x = 3y$, and then $6y - 2y - 4 = 0$ gives $y = 1$, $x = 3$. The Hessian is constant: $H = \begin{pmatrix} 2 & -2 \\ -2 & 6 \end{pmatrix}$ with $\det H = 12 - 4 = 8 > 0$ and $f_{xx} = 2 > 0$, so $(3, 1)$ is a minimum, with $f(3, 1) = 9 + 3 - 6 - 12 = -6$.

```python
def f(x, y):
    return x * x + 3 * y * y - 2 * x * y - 4 * x

def grad(x, y):
    return (2 * x - 2 * y - 4, 6 * y - 2 * x)

x, y = 0.0, 0.0
for step in range(200):
    gx, gy = grad(x, y)
    x, y = x - 0.1 * gx, y - 0.1 * gy
print(f"gradient descent minimum near ({x:.4f}, {y:.4f}), f = {f(x, y):.4f}")
hessian = [[2, -2], [-2, 6]]
det = hessian[0][0] * hessian[1][1] - hessian[0][1] * hessian[1][0]
print("Hessian", hessian, "det", det, "-> positive definite (minimum)" if det > 0 and hessian[0][0] > 0 else "")
saddle_h = [[2, 0], [0, -2]]
print("x^2 - y^2 at the origin: Hessian", saddle_h, "det", saddle_h[0][0] * saddle_h[1][1], "-> saddle point")
```

Output:

```text
gradient descent minimum near (3.0000, 1.0000), f = -6.0000
Hessian [[2, -2], [-2, 6]] det 8 -> positive definite (minimum)
x^2 - y^2 at the origin: Hessian [[2, 0], [0, -2]] det -4 -> saddle point
```

Two hundred gradient steps with learning rate 0.1 converge to the minimum found analytically. For $g(x, y) = x^2 - y^2$, the origin is a critical point whose Hessian has eigenvalues 2 and $-2$: a saddle, curving up along $x$ and down along $y$.

### Example 2: A gradient and a directional derivative

For $f(x, y) = x^2 y$ at the point $(1, 2)$: $\nabla f = (2xy, x^2) = (4, 1)$.

- The steepest ascent direction is $(4, 1)$, with slope $\|\nabla f\| = \sqrt{17} \approx 4.12$.
- In the direction $\mathbf{u} = \left(\frac{3}{5}, \frac{4}{5}\right)$, $D_{\mathbf{u}}f = 4 \cdot \frac35 + 1 \cdot \frac45 = \frac{16}{5} = 3.2$.
- Along the direction $(1, -4)/\sqrt{17}$, perpendicular to the gradient, the directional derivative is 0: that direction is tangent to the level curve $x^2y = 2$ through the point.

For the map $\mathbf{F}(x, y) = (x^2 y, x + y)$, the Jacobian is $J = \begin{pmatrix} 2xy & x^2 \\ 1 & 1 \end{pmatrix}$, which at $(1, 2)$ is $\begin{pmatrix} 4 & 1 \\ 1 & 1 \end{pmatrix}$ with determinant 3: near that point, $\mathbf{F}$ scales small areas by a factor of 3.

## Applications

- **Machine learning:** gradient descent and its variants (SGD, Adam) train models; Hessians inform second-order methods.
- **Robotics:** Jacobians relate joint velocities to end-effector velocities.
- **Physics:** forces are negative gradients of potential energy.
- **Economics and engineering:** constrained optimisation uses gradients and Lagrange multipliers.

## Common mistakes

- **Forgetting to hold the other variables constant in partial derivatives.**
- **Stepping along $+\nabla f$ when minimising.** Descent moves along $-\nabla f$.
- **Using a learning rate that is too large.** The iterates diverge.
- **Assuming a zero gradient means a minimum.** It may be a maximum or a saddle.
- **Using a non-unit vector in a directional derivative.** Normalise $\mathbf{u}$ first.

## Revision notes

- $\frac{\partial f}{\partial x}$: differentiate in $x$ with other variables fixed; mixed partials are equal for smooth $f$.
- $\nabla f$ points to steepest ascent and is perpendicular to level sets; $D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u}$.
- Jacobian: matrix of first partials of a vector function; best linear approximation; chain rule multiplies Jacobians.
- Hessian: matrix of second partials; second-order Taylor approximation.
- Critical points: positive definite Hessian = minimum, negative definite = maximum, mixed signs = saddle; $D = \det H$ for two variables.
- Gradient descent: $\mathbf{x} \leftarrow \mathbf{x} - \eta\nabla f$.

## Practice questions

:::question basic
Find the partial derivatives of $f(x, y) = 3x^2y^3 + e^{xy}$.
:::answer
$f_x = 6xy^3 + ye^{xy}$ and $f_y = 9x^2y^2 + xe^{xy}$, treating the other variable as a constant each time.
:::

:::question basic
In which direction does $f(x, y) = x^2 + y^2$ increase fastest at $(1, 1)$?
:::answer
Along the gradient $\nabla f = (2x, 2y) = (2, 2)$, that is, directly away from the origin, with steepest slope $\|\nabla f\| = 2\sqrt2$.
:::

:::question intermediate
Find and classify the critical points of $f(x, y) = x^3 - 3x + y^2$.
:::answer
$f_x = 3x^2 - 3 = 0$ gives $x = \pm1$, and $f_y = 2y = 0$ gives $y = 0$. The Hessian is $\begin{pmatrix} 6x & 0 \\ 0 & 2 \end{pmatrix}$. At $(1, 0)$, $D = 12 > 0$ and $f_{xx} = 6 > 0$: a local minimum. At $(-1, 0)$, $D = -12 < 0$: a saddle point.
:::

:::question intermediate
For $f(x, y) = x^2 + 10y^2$, explain why a learning rate of 0.15 makes gradient descent diverge.
:::answer
The Hessian is $\text{diag}(2, 20)$, so $\lambda_{\max} = 20$, and stability requires $\eta < 2/20 = 0.1$. Along $y$, each step multiplies $y$ by $1 - 0.15 \times 20 = -2$, so the $y$-coordinate doubles in size and flips sign every step, and the iterates diverge.
:::

:::question advanced
Compute the Jacobian of the polar-to-Cartesian map $x = r\cos\theta$, $y = r\sin\theta$ and explain the factor $r$ in $dA = r\,dr\,d\theta$.
:::answer
$J = \begin{pmatrix} \cos\theta & -r\sin\theta \\ \sin\theta & r\cos\theta \end{pmatrix}$ and $\det J = r\cos^2\theta + r\sin^2\theta = r$. A small rectangle of size $dr \times d\theta$ in the $(r, \theta)$ plane maps to a region of area $|\det J|\,dr\,d\theta = r\,dr\,d\theta$ in the plane, because arcs at radius $r$ have length $r\,d\theta$. That is why polar integrals include the factor $r$.
:::

## Further learning

- **Next:** *First-Order Differential Equations* models change over time with derivatives.
- **Related:** *Linear Regression & Gradient Descent* in Machine Learning applies gradient descent to real models.
