---
lesson: continuous-distributions
title: Continuous Distributions: Uniform, Exponential & Normal
summary: The uniform, exponential, and normal distributions: their densities, CDFs, means, and variances, the memoryless property of the exponential, standardisation with z-scores, and the empirical 68-95-99.7 rule.
minutes: 50
type: theory
objectives:
  - Compute probabilities, means, and variances for uniform and exponential random variables
  - Explain the memoryless property and the link between exponential waiting times and Poisson counts
  - Standardise normal random variables with z-scores and compute normal probabilities and percentiles
review: ai-draft
---
## Introduction

Continuous quantities such as times, lengths, weights, and measurement errors need continuous distributions. Three of them cover a remarkable range of applications. The **uniform** distribution describes "any value in a range is equally likely", as with random number generators. The **exponential** distribution describes waiting times between random events. The **normal** (Gaussian) distribution, the bell curve, describes measurements affected by many small independent influences, and it is central to statistics because of the central limit theorem.

**Before you start:** you should know PDFs, CDFs, expectation and variance, and basic integration of exponentials.

## Core theory

### Uniform distribution

$X \sim U(a, b)$ has constant density on $[a, b]$:

$$f(x) = \frac{1}{b - a}, \quad F(x) = \frac{x - a}{b - a} \;\; (a \le x \le b), \quad E[X] = \frac{a + b}{2}, \quad \operatorname{Var}(X) = \frac{(b - a)^2}{12}$$

Probabilities are proportional to length: $P(c \le X \le d) = (d - c)/(b - a)$ for $a \le c \le d \le b$.

### Exponential distribution

$X \sim \text{Exp}(\lambda)$ with rate $\lambda > 0$:

$$f(x) = \lambda e^{-\lambda x}, \quad F(x) = 1 - e^{-\lambda x} \;\; (x \ge 0), \quad E[X] = \frac{1}{\lambda}, \quad \operatorname{Var}(X) = \frac{1}{\lambda^2}$$

The survival function is $P(X > x) = e^{-\lambda x}$. The exponential distribution is the only continuous **memoryless** distribution: $P(X > s + t \mid X > s) = P(X > t)$. A component whose lifetime is exponential does not "wear out": having survived $s$ hours, its remaining life has the same distribution as a new one. If events form a **Poisson process** with rate $\lambda$ (so counts in an interval of length $t$ are Poisson($\lambda t$)), then the waiting time until the next event is $\text{Exp}(\lambda)$.

### Normal distribution

$X \sim N(\mu, \sigma^2)$ has the bell-shaped density

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right)$$

with mean $\mu$, variance $\sigma^2$, symmetric about $\mu$. Its CDF has no closed form, so probabilities are computed by **standardising**:

$$Z = \frac{X - \mu}{\sigma} \sim N(0, 1), \qquad P(X \le x) = \Phi\left(\frac{x - \mu}{\sigma}\right)$$

where $\Phi$ is the standard normal CDF, found from tables or software ($\Phi(z) = \frac12[1 + \operatorname{erf}(z/\sqrt{2})]$). Symmetry gives $\Phi(-z) = 1 - \Phi(z)$. The **empirical rule**: about 68%, 95%, and 99.7% of values lie within 1, 2, and 3 standard deviations of the mean. Linear transformations of normals are normal, and sums of independent normals are normal with means and variances added.

### Percentiles

To find the value with a given cumulative probability, invert: $x = \mu + z\sigma$, where $z$ is the standard normal percentile (for example $z = 1.645$ for the 95th percentile and $1.96$ for the 97.5th).

## Worked examples

### Example 1: Uniform and exponential calculations

**(a)** A bus arrives uniformly at random between 0 and 20 minutes. What is the probability of waiting more than 15 minutes, and the mean and standard deviation of the wait?

**(b)** A server's time between failures is exponential with mean 200 days. What is the probability it runs more than 300 days? Given that it has already run 100 days, what is the probability it runs another 300?

```python
from math import exp, sqrt

a, b = 0, 20
print(f"P(wait > 15) = {(b - 15) / (b - a):.2f}, mean = {(a + b) / 2:.0f}, sd = {sqrt((b - a)**2 / 12):.2f}")

lam = 1 / 200
survive = lambda t: exp(-lam * t)
print(f"P(T > 300) = {survive(300):.4f}")
print(f"P(T > 400 | T > 100) = {survive(400) / survive(100):.4f}")
print(f"median lifetime = {200 * 0.6931471805599453:.1f} days")
```

Output:

```text
P(wait > 15) = 0.25, mean = 10, sd = 5.77
P(T > 300) = 0.2231
P(T > 400 | T > 100) = 0.2231
median lifetime = 138.6 days
```

The conditional probability equals the unconditional one: the memoryless property in action. The median, $\ln 2 / \lambda \approx 138.6$ days, is well below the mean of 200, because the exponential distribution has a long right tail.

### Example 2: Normal probabilities and percentiles

Exam marks are $N(65, 10^2)$. Find the probability that a student scores above 80, the probability of a mark between 55 and 75, and the mark needed to be in the top 5%.

- Above 80: $z = (80 - 65)/10 = 1.5$, so $P = 1 - \Phi(1.5) \approx 0.0668$.
- Between 55 and 75: $z$ from $-1$ to $1$, about 0.6827 (the empirical rule's 68%).
- Top 5%: $x = 65 + 1.645 \times 10 \approx 81.4$.

```python
from math import erf, sqrt

def phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))

mu, sigma = 65, 10
print(f"P(X > 80) = {1 - phi((80 - mu) / sigma):.4f}")
print(f"P(55 < X < 75) = {phi(1) - phi(-1):.4f}")
for k in (1, 2, 3):
    print(f"within {k} sd: {phi(k) - phi(-k):.4f}")

lo, hi = 0.0, 5.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if phi(mid) < 0.95 else (lo, mid)
print(f"95th percentile z = {lo:.3f}, mark = {mu + lo * sigma:.1f}")
```

Output:

```text
P(X > 80) = 0.0668
P(55 < X < 75) = 0.6827
within 1 sd: 0.6827
within 2 sd: 0.9545
within 3 sd: 0.9973
95th percentile z = 1.645, mark = 81.4
```

The computed probabilities reproduce the 68-95-99.7 rule, and a bisection search inverts $\Phi$ to find the 95th percentile, $z \approx 1.645$.

## Applications

- **Simulation:** uniform random numbers are transformed into samples of other distributions.
- **Reliability and queues:** exponential lifetimes and inter-arrival times.
- **Measurement and quality control:** normal models for errors and manufacturing tolerances.
- **Standardised testing:** z-scores compare results on different scales.

## Common mistakes

- **Confusing rate and mean.** For the exponential, the mean is $1/\lambda$.
- **Forgetting to standardise.** Normal tables give $\Phi(z)$ for $Z \sim N(0, 1)$ only.
- **Using the variance instead of the standard deviation in $z = (x - \mu)/\sigma$.**
- **Assuming everything is normal.** Waiting times and incomes are skewed.
- **Expecting the exponential median to equal its mean.** The median is $\ln 2/\lambda \approx 0.693/\lambda$.

## Revision notes

- Uniform(a, b): density $1/(b-a)$, mean $(a+b)/2$, variance $(b-a)^2/12$.
- Exponential($\lambda$): $P(X > x) = e^{-\lambda x}$, mean $1/\lambda$, variance $1/\lambda^2$, memoryless.
- Poisson process rate $\lambda$: waiting times are Exp($\lambda$).
- Normal: $Z = (X - \mu)/\sigma$, $P(X \le x) = \Phi(z)$, $\Phi(-z) = 1 - \Phi(z)$.
- 68-95-99.7 rule; 95th percentile $z = 1.645$, 97.5th $z = 1.96$.
- Sums of independent normals are normal.

## Practice questions

:::question basic
X is uniform on [2, 10]. Find $P(X < 5)$ and $E[X]$.
:::answer
$P(X < 5) = (5 - 2)/(10 - 2) = 3/8$. $E[X] = (2 + 10)/2 = 6$.
:::

:::question basic
Heights are $N(170, 8^2)$ cm. What is the z-score of a height of 186 cm?
:::answer
$z = (186 - 170)/8 = 2$: the height is two standard deviations above the mean, which only about 2.3% of people exceed.
:::

:::question intermediate
Calls arrive as a Poisson process at 6 per hour. What is the probability that the next call takes more than 15 minutes to arrive?
:::answer
The waiting time is exponential with rate 6 per hour, that is, 0.1 per minute. $P(T > 15) = e^{-0.1 \times 15} = e^{-1.5} \approx 0.223$.
:::

:::question intermediate
A machine fills bottles with $N(500, 4^2)$ ml. What fraction contain less than 492 ml?
:::answer
$z = (492 - 500)/4 = -2$, so $P = \Phi(-2) = 1 - \Phi(2) \approx 1 - 0.9772 = 0.0228$, about 2.3% of bottles.
:::

:::question advanced
Two independent processing steps take $N(10, 2^2)$ and $N(15, 3^2)$ minutes. What is the probability that the total exceeds 30 minutes?
:::answer
The total is normal with mean $10 + 15 = 25$ and variance $4 + 9 = 13$, so $\sigma = \sqrt{13} \approx 3.606$. Then $z = (30 - 25)/3.606 \approx 1.387$, and $P(\text{total} > 30) = 1 - \Phi(1.387) \approx 0.083$.
:::

## Further learning

- **Next:** *Joint Distributions, Covariance & Correlation* studies several random variables together.
- **Related:** *Central Limit Theorem & Sampling Error* in Statistics explains why the normal distribution is everywhere.
