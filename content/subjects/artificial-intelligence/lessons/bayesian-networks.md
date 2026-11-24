---
lesson: bayesian-networks
title: Bayesian Networks & Probabilistic Inference
summary: Reasoning under uncertainty with Bayesian networks: directed acyclic graphs with conditional probability tables, the factorisation of the joint distribution, conditional independence and explaining away, exact inference by enumeration and variable elimination, and approximate inference by sampling.
minutes: 55
type: theory
objectives:
  - Build a Bayesian network, write its factorised joint distribution, and count its parameters
  - Compute posterior probabilities by enumeration and explain conditional independence, including explaining away
  - Compare exact inference with sampling methods such as rejection sampling and likelihood weighting
review: ai-draft
---
## Introduction

Real agents rarely know facts for certain. An alert at 2 a.m. might mean the server is down, or it might be a false alarm; if the server is down, the cause might be a software bug or a power cut. Logic cannot weigh these possibilities, but probability can. A **Bayesian network** represents the probabilistic relationships among many variables compactly and supports principled reasoning from evidence to causes. Bayesian networks are used in medical diagnosis, fault detection, spam filtering, and risk analysis.

**Before you start:** you should know conditional probability and Bayes' rule from *Conditional Probability & Bayes Theorem*.

## Core theory

### Why not the full joint distribution?

The full joint distribution over $n$ Boolean variables needs $2^n - 1$ numbers, which is impossible to store or estimate for even 50 variables. Most variables, however, directly depend on only a few others. Bayesian networks exploit this.

### Structure and semantics

A Bayesian network is a **directed acyclic graph** whose nodes are random variables. An arrow $X \to Y$ means $X$ directly influences $Y$. Each node has a **conditional probability table** (CPT) giving $P(X_i \mid Parents(X_i))$. The network represents the joint distribution as a product:

$$P(x_1, \dots, x_n) = \prod_{i=1}^{n} P(x_i \mid parents(X_i))$$

A Boolean node with $k$ Boolean parents needs $2^k$ numbers, so a network of $n$ nodes with at most $k$ parents needs at most $n \cdot 2^k$ numbers instead of $2^n - 1$. Building the network in **causal order** (causes before effects) usually gives the most compact structure.

### Conditional independence

Each node is conditionally independent of its non-descendants given its parents. Three basic patterns describe how influence flows:

- **Chain** $A \to B \to C$: $A$ and $C$ are dependent, but independent given $B$.
- **Common cause** $A \leftarrow B \to C$: $A$ and $C$ are dependent, but independent given $B$.
- **Common effect** (v-structure) $A \to B \leftarrow C$: $A$ and $C$ are independent, but become **dependent** once $B$ (or a descendant of $B$) is observed. This is **explaining away**: if the server is down and we learn there was a power cut, a bug becomes less likely.

The general criterion, **d-separation**, decides from the graph alone whether two sets of variables are independent given evidence. A node's **Markov blanket** (its parents, children, and children's other parents) makes it independent of everything else.

### Exact inference

A query asks for $P(X \mid \mathbf{e})$. **Inference by enumeration** sums the factorised joint over all hidden variables and normalises:

$$P(X \mid \mathbf{e}) = \alpha \sum_{\mathbf{h}} P(X, \mathbf{e}, \mathbf{h})$$

This costs $O(2^n)$ in the worst case. **Variable elimination** avoids repeated work by summing out variables one at a time and caching intermediate factors. Exact inference is efficient on **polytrees** (networks without undirected cycles) but NP-hard in general.

### Approximate inference

- **Prior (direct) sampling** generates complete samples in topological order.
- **Rejection sampling** discards samples that disagree with the evidence; it wastes almost every sample when the evidence is unlikely.
- **Likelihood weighting** fixes the evidence variables and weights each sample by the probability of the evidence.
- **Gibbs sampling** (a Markov chain Monte Carlo method) repeatedly resamples one variable from its distribution given its Markov blanket.

## Worked examples

### Example 1: Diagnosing an alert

The network is: PowerCut → ServerDown ← Bug, and ServerDown → Alert, with a 5% chance of a power cut, a 10% chance of a bug, a CPT for ServerDown given both causes, and an alert that fires 95% of the time when the server is down and 2% of the time otherwise.

```python
import random
from itertools import product

P_POWER, P_BUG = 0.05, 0.10
P_DOWN = {(True, True): 0.99, (True, False): 0.90, (False, True): 0.60, (False, False): 0.01}
P_ALERT = {True: 0.95, False: 0.02}


def joint(power, bug, down, alert):
    p = (P_POWER if power else 1 - P_POWER) * (P_BUG if bug else 1 - P_BUG)
    p *= P_DOWN[(power, bug)] if down else 1 - P_DOWN[(power, bug)]
    return p * (P_ALERT[down] if alert else 1 - P_ALERT[down])


def enumerate_query(target, evidence):
    """P(target = True | evidence) by summing the full joint distribution."""
    totals = {True: 0.0, False: 0.0}
    for values in product([True, False], repeat=4):
        world = dict(zip(["power", "bug", "down", "alert"], values))
        if all(world[k] == v for k, v in evidence.items()):
            totals[world[target]] += joint(*values)
    return totals[True] / (totals[True] + totals[False])


print(f"prior P(bug)                        = {P_BUG:.3f}")
print(f"P(bug | alert)                      = {enumerate_query('bug', {'alert': True}):.3f}")
print(f"P(power cut | alert)                = {enumerate_query('power', {'alert': True}):.3f}")
print(f"P(bug | alert, power cut)           = {enumerate_query('bug', {'alert': True, 'power': True}):.3f}")

random.seed(7)
kept = bug_count = 0
for _ in range(100_000):  # rejection sampling: simulate, keep samples that match evidence
    power, bug = random.random() < P_POWER, random.random() < P_BUG
    down = random.random() < P_DOWN[(power, bug)]
    alert = random.random() < P_ALERT[down]
    if alert:
        kept += 1
        bug_count += bug
print(f"rejection sampling P(bug | alert)   ~ {bug_count / kept:.3f}  ({kept:,} of 100,000 samples kept)")
```

Output:

```text
prior P(bug)                        = 0.100
P(bug | alert)                      = 0.484
P(power cut | alert)                = 0.351
P(bug | alert, power cut)           = 0.109
rejection sampling P(bug | alert)   ~ 0.477  (12,344 of 100,000 samples kept)
```

Observing an alert raises the probability of a bug from 10% to 48.4% and of a power cut from 5% to 35.1%. But once we also learn that there was a power cut, the bug probability falls back to 10.9%, close to its prior: the power cut **explains away** the alert. Rejection sampling estimates 0.477, close to the exact 0.484, but it kept only 12,344 of 100,000 samples because alerts are fairly rare; with rarer evidence, almost all samples would be wasted.

### Example 2: Computing with the factorisation

Using the same CPTs, compute the probability that there is a bug and no power cut, the server goes down, and the alert fires:

$$P(\neg p, b, d, a) = P(\neg p)\,P(b)\,P(d \mid \neg p, b)\,P(a \mid d) = 0.95 \times 0.10 \times 0.60 \times 0.95 = 0.05415$$

The probability that the server is down sums over its parents:

$$P(d) = 0.05 \cdot 0.10 \cdot 0.99 + 0.05 \cdot 0.90 \cdot 0.90 + 0.95 \cdot 0.10 \cdot 0.60 + 0.95 \cdot 0.90 \cdot 0.01 = 0.111$$

Then $P(a) = 0.111 \times 0.95 + 0.889 \times 0.02 \approx 0.1232$, matching the fraction of samples kept above. The network needs only 8 numbers (1 + 1 + 4 + 2) instead of the 15 required for the full joint of four Boolean variables.

## Applications

- **Medical diagnosis:** networks link diseases, risk factors, and symptoms.
- **Fault diagnosis:** IT operations, aircraft systems, and manufacturing lines.
- **Spam and fraud detection:** probabilistic models of suspicious features.
- **Risk analysis:** reliability engineering and decision support.
- **Gene regulatory networks:** modelling dependencies in biology.

## Common mistakes

- **Reading arrows as certain causation.** Arrows encode direct dependence; causal interpretation needs extra assumptions.
- **Assuming independent causes stay independent after observing their effect.** Observing a common effect makes them dependent.
- **Forgetting to normalise.** Enumeration gives unnormalised values; divide by their sum.
- **Counting CPT parameters wrongly.** A Boolean node with $k$ Boolean parents needs $2^k$ numbers, not $2^{k+1}$.
- **Using rejection sampling with rare evidence.** Use likelihood weighting or Gibbs sampling instead.

## Revision notes

- Bayesian network: DAG + CPTs; $P(x_1, \dots, x_n) = \prod P(x_i \mid parents)$.
- Compact: at most $n \cdot 2^k$ numbers versus $2^n - 1$.
- Chain and common cause: independent given the middle node; common effect: dependent given the effect (explaining away).
- d-separation; Markov blanket.
- Exact inference: enumeration ($O(2^n)$), variable elimination; NP-hard in general, easy for polytrees.
- Approximate: prior, rejection, likelihood weighting, Gibbs sampling.

## Practice questions

:::question basic
How many probabilities does the CPT of a Boolean node with three Boolean parents contain?
:::answer
$2^3 = 8$: one probability of the node being true for each combination of parent values (the probability of false is one minus it).
:::

:::question basic
Write the factorised joint distribution for the network $A \to B \to C$.
:::answer
$P(a, b, c) = P(a)\,P(b \mid a)\,P(c \mid b)$.
:::

:::question intermediate
Explain "explaining away" with the alert network from this lesson.
:::answer
Bug and PowerCut are independent causes of ServerDown. Observing the alert raises both their probabilities. If we then learn that a power cut occurred, it accounts for the alert, so the probability of a bug drops back towards its prior (from 0.484 to 0.109 here). Observing a common effect makes its independent causes dependent.
:::

:::question intermediate
A network has 30 Boolean nodes, each with at most 3 parents. Compare its parameter count with the full joint distribution.
:::answer
The network needs at most $30 \times 2^3 = 240$ numbers. The full joint needs $2^{30} - 1 \approx 1.07 \times 10^9$, over four million times more.
:::

:::question advanced
Why does rejection sampling become inefficient as evidence becomes less likely, and how does likelihood weighting fix this?
:::answer
Rejection sampling keeps only samples that match the evidence, so the expected fraction kept equals $P(\mathbf{e})$. If $P(\mathbf{e}) = 0.001$, about 1,000 samples are generated for each useful one, and with several evidence variables the probability shrinks exponentially. Likelihood weighting never rejects: it fixes evidence variables to their observed values, samples only the others, and weights each sample by the likelihood of the evidence given its parents, so every sample contributes.
:::

## Further learning

- **Next:** *STRIPS & Forward/Backward State Search* returns to planning with structured action models.
- **Related:** *Conditional Probability & Bayes Theorem* in Probability reviews the underlying rules.
