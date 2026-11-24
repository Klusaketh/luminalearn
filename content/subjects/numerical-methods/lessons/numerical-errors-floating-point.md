---
lesson: numerical-errors-floating-point
title: Errors, Floating-Point Arithmetic & Stability
summary: Sources of error in numerical computation (round-off, truncation, data error), absolute and relative error, IEEE 754 floating-point numbers and machine epsilon, catastrophic cancellation, conditioning of problems, and stability of algorithms.
minutes: 45
type: theory
objectives:
  - Compute absolute and relative errors and distinguish round-off, truncation, and data errors
  - Explain how IEEE 754 floating-point numbers are stored, what machine epsilon means, and why decimal fractions are inexact
  - Recognise catastrophic cancellation and ill-conditioning, and choose numerically stable formulas
review: ai-draft
---
## Introduction

Computers do not compute with real numbers; they compute with a finite set of **floating-point** numbers. That is why `0.1 + 0.2` is not exactly `0.3` in almost every programming language, why subtracting nearly equal numbers can destroy all accuracy, and why two mathematically equivalent formulas can give wildly different results. Numerical methods are the study of computing accurately despite these limits, and this lesson explains where errors come from and how to keep them small.

**Before you start:** you should know binary numbers, scientific notation, and basic algebra; Taylor series help for truncation error.

## Core theory

### Measuring error

If $x$ is the true value and $\tilde{x}$ an approximation:

$$\text{absolute error} = |x - \tilde{x}|, \qquad \text{relative error} = \frac{|x - \tilde{x}|}{|x|}$$

Relative error is usually more meaningful: an error of 1 mm is negligible for a bridge but huge for a microchip. A relative error of about $10^{-k}$ means roughly $k$ correct significant digits.

### Sources of error

- **Data error:** inputs are measured or rounded before computing begins.
- **Round-off error:** each arithmetic operation rounds its result to the nearest representable number.
- **Truncation (discretisation) error:** a method replaces an infinite process by a finite one, such as stopping a Taylor series or using a finite step size $h$. It depends on the method, not on the hardware.

Often truncation error falls as $h$ shrinks while round-off error grows, so there is an optimal step size.

### Floating-point numbers

IEEE 754 **double precision** stores a number as $\pm m \times 2^e$ with a 52-bit fraction (53 significant bits including the hidden leading 1) and an 11-bit exponent, giving about 15 to 17 significant decimal digits and a range of roughly $10^{-308}$ to $10^{308}$. **Machine epsilon** $\varepsilon = 2^{-52} \approx 2.22 \times 10^{-16}$ is the gap between 1 and the next representable number; every operation has relative error at most $\varepsilon/2$ (the unit round-off). Consequences:

- Decimal fractions such as 0.1 have no finite binary expansion, so they are stored inexactly.
- Floating-point addition is not associative: $(a + b) + c$ may differ from $a + (b + c)$.
- Adding a tiny number to a huge one can have no effect: $10^{16} + 1 = 10^{16}$ in double precision.
- Compare floats with a tolerance, never with `==`.

### Catastrophic cancellation

Subtracting two nearly equal numbers cancels their leading digits, leaving mostly the accumulated rounding errors. The quadratic formula $x = \frac{-b + \sqrt{b^2 - 4ac}}{2a}$ suffers this when $b^2 \gg 4ac$: $\sqrt{b^2 - 4ac} \approx b$. The cure is an algebraically equivalent but stable form, here $x = \frac{2c}{-b - \sqrt{b^2 - 4ac}}$, which adds numbers of the same sign instead.

### Conditioning and stability

- A **problem** is **ill-conditioned** if small changes in its input cause large changes in its output, whatever method is used. The **condition number** measures this amplification; for a linear system $A\mathbf{x} = \mathbf{b}$, it is $\kappa(A) = \|A\|\|A^{-1}\|$, and about $\log_{10}\kappa$ significant digits may be lost.
- An **algorithm** is **stable** if it does not amplify errors more than the problem's conditioning requires. Gaussian elimination with partial pivoting is stable in practice; without pivoting it can be unstable.

A good result needs both a well-conditioned problem and a stable algorithm.

## Worked examples

### Example 1: Floating-point surprises and a stable formula

```python
import sys
from math import sqrt

print("0.1 + 0.2 =", 0.1 + 0.2, "| equal to 0.3?", 0.1 + 0.2 == 0.3)
print("machine epsilon:", sys.float_info.epsilon)
print("1e16 + 1 - 1e16 =", 1e16 + 1 - 1e16)
total = 0.0
for _ in range(10):
    total += 0.1
print("sum of ten 0.1s:", total, "| abs error:", abs(total - 1.0))

a, b, c = 1.0, 1e8, 1.0
naive = (-b + sqrt(b * b - 4 * a * c)) / (2 * a)
stable = (2 * c) / (-b - sqrt(b * b - 4 * a * c))
print(f"small root naive: {naive:.10e}, stable: {stable:.10e}")
x_true, x_approx = 3.14159265, 3.14
print(f"absolute error {abs(x_true - x_approx):.6f}, relative error {abs(x_true - x_approx) / x_true:.2e}")
```

Output:

```text
0.1 + 0.2 = 0.30000000000000004 | equal to 0.3? False
machine epsilon: 2.220446049250313e-16
1e16 + 1 - 1e16 = 0.0
sum of ten 0.1s: 0.9999999999999999 | abs error: 1.1102230246251565e-16
small root naive: -7.4505805969e-09, stable: -1.0000000000e-08
absolute error 0.001593, relative error 5.07e-04
```

`0.1 + 0.2` differs from `0.3` in the 17th significant digit, and ten additions of 0.1 accumulate a similar error. Adding 1 to $10^{16}$ is lost entirely, because the spacing of doubles near $10^{16}$ is 2. For $x^2 + 10^8x + 1 = 0$, the naive formula gets the small root wrong by about 25% because $-b + \sqrt{b^2 - 4ac}$ cancels catastrophically, while the stable formula gives $-1.0 \times 10^{-8}$, correct to all printed digits. Approximating $\pi$ by 3.14 has absolute error 0.0016 and relative error $5 \times 10^{-4}$.

### Example 2: An ill-conditioned system

Consider

$$\begin{aligned} x + y &= 2 \\ x + 1.0001y &= 2.0001 \end{aligned}$$

whose solution is $x = 1$, $y = 1$. Change the second right-hand side to 2.0002, a change of 0.005%. The solution becomes $x = 0$, $y = 2$: a completely different answer. The two equations describe nearly parallel lines, so their intersection moves enormously when either line shifts slightly. The condition number of the coefficient matrix is about 40,000, warning that four to five significant digits of input accuracy can be lost. No algorithm can fix this; the problem itself is sensitive, and the remedy is better data or a reformulated model.

## Applications

- **Scientific computing:** choosing stable formulas and algorithms keeps simulations trustworthy.
- **Finance:** money is stored as integers (cents) or decimal types to avoid binary rounding.
- **Machine learning:** mixed precision (16-bit floats) needs care with underflow and loss scaling.
- **Software testing:** floating-point results are compared with tolerances such as `math.isclose`.

## Common mistakes

- **Comparing floats with `==`.** Use a relative or absolute tolerance.
- **Subtracting nearly equal quantities.** Rearrange formulas to avoid cancellation.
- **Blaming the algorithm for an ill-conditioned problem.** Check the condition number.
- **Using too small a step size.** Round-off error eventually dominates truncation error.
- **Assuming more digits printed means more accuracy.** Only the correct digits matter.

## Revision notes

- Absolute error $|x - \tilde{x}|$; relative error $|x - \tilde{x}|/|x|$ (about $10^{-k}$ means $k$ digits).
- Error sources: data, round-off, truncation.
- Double precision: 53 significant bits, about 16 digits; $\varepsilon \approx 2.2 \times 10^{-16}$.
- 0.1 is inexact in binary; addition is not associative; compare with tolerances.
- Catastrophic cancellation: subtracting close numbers; use equivalent stable formulas.
- Conditioning is a property of the problem ($\kappa(A)$); stability is a property of the algorithm.

## Practice questions

:::question basic
A measurement gives 9.80 m/s² for a true value of 9.81 m/s². Find the absolute and relative errors.
:::answer
The absolute error is $|9.81 - 9.80| = 0.01$ m/s². The relative error is $0.01/9.81 \approx 1.02 \times 10^{-3}$, about 0.1%.
:::

:::question basic
Why does `0.1 + 0.2 == 0.3` evaluate to false in Python?
:::answer
None of 0.1, 0.2, and 0.3 can be represented exactly in binary floating point, so each is stored as a nearby double. The rounded sum of the stored 0.1 and 0.2 is a slightly different double from the stored 0.3, so the exact equality test fails. Compare with a tolerance instead.
:::

:::question intermediate
Rewrite $\sqrt{x + 1} - \sqrt{x}$ to avoid cancellation for large $x$.
:::answer
Multiply by the conjugate: $\sqrt{x + 1} - \sqrt{x} = \frac{(x + 1) - x}{\sqrt{x + 1} + \sqrt{x}} = \frac{1}{\sqrt{x + 1} + \sqrt{x}}$. The new form adds two positive numbers instead of subtracting nearly equal ones, so it is accurate for large $x$.
:::

:::question intermediate
What is the difference between truncation error and round-off error? Give one example of each.
:::answer
Truncation error comes from the method approximating an infinite or continuous process, such as using the first three terms of the Taylor series for $e^x$ or a finite step size in a derivative; it exists even with exact arithmetic. Round-off error comes from storing results with finite precision, such as 0.1 being stored inexactly or each floating-point operation rounding its result.
:::

:::question advanced
A linear system has condition number $10^{12}$, and it is solved in double precision. Roughly how many correct significant digits can you expect in the solution, and why?
:::answer
Double precision carries about 16 significant digits, and an ill-conditioned problem can lose up to about $\log_{10}\kappa = 12$ of them through error amplification. So only about $16 - 12 = 4$ digits can be trusted, even with a stable algorithm such as pivoted elimination. Improving the result requires reformulating or regularising the problem, or using higher precision.
:::

## Further learning

- **Next:** *Bisection & Secant Methods* begins solving equations numerically.
- **Related:** *Sequences, Series & Taylor Expansions* in Calculus explains truncation error through Taylor remainders.
