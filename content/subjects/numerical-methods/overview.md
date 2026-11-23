Numerical methods are algorithms for solving mathematical problems approximately with a computer when exact answers are impossible or impractical. Most equations that arise in engineering and science cannot be solved by algebra alone, and most integrals have no closed form. Numerical methods find roots, evaluate integrals, and solve differential equations to any accuracy required, and they explain how much the answer can be trusted.

This subject starts with the source of every numerical error: floating-point arithmetic, round-off and truncation error, and the stability of algorithms. It then solves non-linear equations with bisection, the secant method, Newton-Raphson, and fixed-point iteration, comparing their speed and reliability. Interpolation fits polynomials through data points with the Lagrange and Newton forms. The integration and ODE modules approximate definite integrals with the trapezoidal and Simpson's rules and solve initial value problems with the fourth-order Runge-Kutta method. The subject closes with iterative methods, Jacobi and Gauss-Seidel, for large systems of linear equations.

Every method is implemented in a short Python program and traced iteration by iteration, so you can watch the error shrink and see where a method fails.

## What you will learn
- Explain floating-point representation and distinguish round-off error from truncation error
- Measure absolute and relative error and recognise unstable computations
- Find roots with bisection, secant, Newton-Raphson, and fixed-point iteration, and compare their convergence
- Construct interpolating polynomials in Lagrange and Newton form
- Approximate definite integrals with the trapezoidal and Simpson's rules and estimate their error
- Solve initial value problems with Euler's method and the fourth-order Runge-Kutta method
- Solve linear systems iteratively with the Jacobi and Gauss-Seidel methods and check convergence

## Prerequisites
- Calculus: derivatives, integrals, and Taylor series (see the Calculus subject)
- Linear algebra basics: matrices and systems of equations (see the Linear Algebra subject)
- Python programming, for implementing the methods

## Glossary
- **Round-off error**: error caused by storing numbers with finite precision
- **Truncation error**: error caused by approximating an infinite process with a finite one
- **Machine epsilon**: the gap between 1 and the next representable floating-point number
- **Stability**: an algorithm is stable if small errors in its input or arithmetic stay small in its output
- **Root**: a value x with f(x) = 0
- **Order of convergence**: how fast an iterative method's error shrinks; Newton's method converges quadratically
- **Bisection method**: repeatedly halving an interval known to contain a root
- **Newton-Raphson method**: refining a root estimate with xₙ₊₁ = xₙ − f(xₙ) / f′(xₙ)
- **Interpolation**: constructing a function that passes exactly through given data points
- **Quadrature**: numerical approximation of a definite integral
- **Initial value problem**: a differential equation together with the value of the solution at a starting point
- **Runge-Kutta method**: a family of methods that estimate the next solution value from several slope evaluations

## Further reading
- Richard L. Burden and J. Douglas Faires, *Numerical Analysis* (Cengage)
- Steven C. Chapra and Raymond P. Canale, *Numerical Methods for Engineers* (McGraw-Hill)
- William H. Press, Saul A. Teukolsky, William T. Vetterling, and Brian P. Flannery, *Numerical Recipes* (Cambridge University Press)
- Nicholas J. Higham, *Accuracy and Stability of Numerical Algorithms* (SIAM)
