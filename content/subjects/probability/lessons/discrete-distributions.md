---
lesson: discrete-distributions
title: Discrete Distributions: Bernoulli, Binomial, Geometric & Poisson
summary: The four workhorse discrete distributions (Bernoulli, binomial, geometric, and Poisson), the situations each one models, their PMFs, means, and variances, and the Poisson approximation to the binomial.
minutes: 50
type: theory
objectives:
  - Recognise when a situation is modelled by a Bernoulli, binomial, geometric, or Poisson random variable
  - Compute probabilities, means, and variances for each distribution
  - Use the Poisson distribution to approximate a binomial with many trials and a small success probability
review: ai-draft
---
## Introduction

Many random quantities follow a handful of patterns. Whether a single packet is lost is a yes/no trial; the number of defective chips in a batch counts successes in repeated trials; the number of attempts until a password guess succeeds waits for the first success; the number of requests a server receives per second counts rare, independent events. Each pattern has a named distribution with ready-made formulas, so recognising the pattern is most of the work.

**Before you start:** you should know random variables, PMFs, expectation, variance, and binomial coefficients.

## Core theory

### Bernoulli: one trial

A **Bernoulli trial** has two outcomes, success (1) with probability $p$ and failure (0) with probability $1 - p$. If $X \sim \text{Bernoulli}(p)$:

$$P(X = 1) = p, \quad P(X = 0) = 1 - p, \quad E[X] = p, \quad \operatorname{Var}(X) = p(1 - p)$$

### Binomial: number of successes in n trials

$X \sim \text{Binomial}(n, p)$ counts successes in $n$ **independent** Bernoulli trials with the **same** success probability $p$:

$$P(X = k) = \binom{n}{k} p^k (1 - p)^{n - k}, \quad k = 0, \dots, n$$

$$E[X] = np, \qquad \operatorname{Var}(X) = np(1 - p)$$

The mean and variance follow from writing X as a sum of $n$ independent Bernoulli variables. The four conditions to check are: fixed $n$, two outcomes per trial, independence, and constant $p$. Sampling **without** replacement from a small population breaks independence (the hypergeometric distribution then applies).

### Geometric: trials until the first success

$X \sim \text{Geometric}(p)$ counts the trials up to and including the first success:

$$P(X = k) = (1 - p)^{k - 1} p, \quad k = 1, 2, \dots \qquad E[X] = \frac{1}{p}, \quad \operatorname{Var}(X) = \frac{1 - p}{p^2}$$

and $P(X > k) = (1 - p)^k$. The geometric distribution is **memoryless**: $P(X > m + n \mid X > m) = P(X > n)$. Having already failed $m$ times does not make success any more likely on the next try. (Some books count failures before the first success instead, giving mean $(1 - p)/p$; always check the definition.)

### Poisson: counts of rare events

$X \sim \text{Poisson}(\lambda)$ models the number of events in a fixed interval of time or space when events occur independently at a constant average rate $\lambda$ per interval:

$$P(X = k) = \frac{e^{-\lambda} \lambda^k}{k!}, \quad k = 0, 1, 2, \dots \qquad E[X] = \operatorname{Var}(X) = \lambda$$

Examples: calls to a help desk per hour, typos per page, radioactive decays per second. Rates scale with the interval: 3 per minute means $\lambda = 15$ for five minutes. Sums of independent Poisson variables are Poisson with the rates added.

### The Poisson approximation to the binomial

When $n$ is large and $p$ small with $np$ moderate (a common rule of thumb is $n \ge 20$ and $p \le 0.05$), $\text{Binomial}(n, p) \approx \text{Poisson}(\lambda = np)$. This is why counts of rare events among many independent opportunities are Poisson.

## Worked examples

### Example 1: Binomial and geometric probabilities

A network link drops each packet independently with probability $p = 0.1$.

**(a)** Of 20 packets, what is the probability that exactly 2 are dropped, and at most 2?

**(b)** How many packets are sent, on average, up to and including the first drop, and what is the probability that the first 10 all get through?

```python
from math import comb

n, p = 20, 0.1
pmf = [comb(n, k) * p**k * (1 - p)**(n - k) for k in range(n + 1)]
print(f"P(X = 2) = {pmf[2]:.4f}, P(X <= 2) = {sum(pmf[:3]):.4f}")
print(f"mean = {n * p:.1f}, variance = {n * p * (1 - p):.2f}, sum of pmf = {sum(pmf):.6f}")
print(f"geometric: mean = {1 / p:.0f} packets, P(first 10 survive) = {(1 - p)**10:.4f}")
```

Output:

```text
P(X = 2) = 0.2852, P(X <= 2) = 0.6769
mean = 2.0, variance = 1.80, sum of pmf = 1.000000
geometric: mean = 10 packets, P(first 10 survive) = 0.3487
```

The binomial PMF sums to 1 as it must. Waiting for the first drop takes 10 packets on average, yet about 35% of the time the first 10 all survive.

### Example 2: Poisson counts and the approximation

A help desk receives 4 calls per hour on average. What is the probability of no calls in an hour, and of more than 6? Then compare Binomial(1000, 0.003) with Poisson(3).

```python
from math import comb, exp, factorial

def poisson(k, lam):
    return exp(-lam) * lam**k / factorial(k)

lam = 4
print(f"P(0 calls) = {poisson(0, lam):.4f}")
print(f"P(more than 6) = {1 - sum(poisson(k, lam) for k in range(7)):.4f}")
print(f"P(0 calls in 30 min) = {poisson(0, lam / 2):.4f}")

n, p = 1000, 0.003
for k in range(5):
    binom = comb(n, k) * p**k * (1 - p)**(n - k)
    print(k, f"binomial {binom:.4f}  poisson {poisson(k, n * p):.4f}")
```

Output:

```text
P(0 calls) = 0.0183
P(more than 6) = 0.1107
P(0 calls in 30 min) = 0.1353
0 binomial 0.0496  poisson 0.0498
1 binomial 0.1491  poisson 0.1494
2 binomial 0.2242  poisson 0.2240
3 binomial 0.2244  poisson 0.2240
4 binomial 0.1683  poisson 0.1680
```

For half an hour the rate halves to $\lambda = 2$. With 1,000 trials and $p = 0.003$, the Poisson probabilities agree with the exact binomial ones to about three decimal places.

## Applications

- **Quality control:** binomial counts of defective items in a sample.
- **Networking and queues:** Poisson arrivals of packets and requests size buffers and servers.
- **Security:** the geometric distribution gives the expected number of guesses until success.
- **Biology and physics:** mutations and radioactive decays are Poisson processes.

## Common mistakes

- **Using the binomial when trials are dependent.** Drawing without replacement from a small group is hypergeometric.
- **Mixing up geometric conventions.** Trials until success (mean $1/p$) versus failures before it (mean $(1-p)/p$).
- **Forgetting to rescale the Poisson rate.** Match $\lambda$ to the interval in the question.
- **Assuming a Poisson model when events cluster.** Independence and a constant rate are required.
- **Computing "at most" without including the endpoint.** $P(X \le 2)$ includes $k = 0, 1, 2$.

## Revision notes

- Bernoulli(p): mean $p$, variance $p(1-p)$.
- Binomial(n, p): $\binom{n}{k}p^k(1-p)^{n-k}$, mean $np$, variance $np(1-p)$; needs independent identical trials.
- Geometric(p): $(1-p)^{k-1}p$, mean $1/p$, variance $(1-p)/p^2$, memoryless, $P(X > k) = (1-p)^k$.
- Poisson($\lambda$): $e^{-\lambda}\lambda^k/k!$, mean = variance = $\lambda$; rates scale with the interval.
- Binomial with large $n$, small $p$ ≈ Poisson($np$).

## Practice questions

:::question basic
A fair coin is tossed 10 times. What is the probability of exactly 5 heads?
:::answer
$X \sim \text{Binomial}(10, 0.5)$, so $P(X = 5) = \binom{10}{5}(0.5)^{10} = 252/1024 \approx 0.246$.
:::

:::question basic
A basketball player makes 80% of free throws. What is the expected number of attempts until the first miss?
:::answer
A miss is the "success" here, with probability 0.2, so the number of attempts until the first miss is geometric with mean $1/0.2 = 5$.
:::

:::question intermediate
Emails arrive at 12 per hour on average. What is the probability of exactly 2 emails in a 10-minute period?
:::answer
In 10 minutes the rate is $\lambda = 12/6 = 2$. $P(X = 2) = e^{-2} 2^2/2! = 2e^{-2} \approx 0.271$.
:::

:::question intermediate
Explain the memoryless property of the geometric distribution with an example.
:::answer
If each lottery draw is independent with win probability p, then after 50 losing draws, the probability of needing more than 10 further draws is $(1-p)^{10}$, exactly as for someone starting fresh. Past failures do not make a win "due"; the distribution of the remaining waiting time is unchanged.
:::

:::question advanced
A batch of 500 chips each has a 0.4% defect rate independently. Use a suitable approximation to estimate the probability of at least 3 defective chips.
:::answer
$n = 500$ and $p = 0.004$, so use Poisson with $\lambda = np = 2$. $P(X \ge 3) = 1 - [e^{-2}(1 + 2 + 2^2/2)] = 1 - 5e^{-2} \approx 1 - 0.677 = 0.323$.
:::

## Further learning

- **Next:** *Continuous Distributions: Uniform, Exponential & Normal* covers the continuous counterparts.
- **Related:** *Permutations, Combinations & the Binomial Theorem* explains the binomial coefficients in the PMF.
