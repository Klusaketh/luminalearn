---
lesson: induction-proof-techniques
title: Induction Proof Techniques
summary: Proving statements about all natural numbers with mathematical induction: the base case, inductive hypothesis, and inductive step, strong induction, and induction in algorithm correctness.
minutes: 40
type: theory
objectives:
  - Write complete proofs by weak induction for sums, inequalities, and divisibility statements
  - Use strong induction when the step needs several earlier cases
  - Recognise flawed induction arguments and connect induction to recursion and loop invariants
review: ai-draft
---
## Introduction

How can a finite argument prove a statement for infinitely many numbers? **Mathematical induction** does it like a row of dominoes: show the first one falls, and show that whenever one falls the next one falls too; then they all fall. Induction is the standard tool for proving formulas, analysing recursive algorithms, and verifying loops, and it mirrors recursion so closely that recursive programs are often proved correct by induction on the input size.

**Before you start:** you should know proof techniques, summation notation, and basic algebra.

## Core theory

### The principle of induction

To prove that $P(n)$ is true for all integers $n \ge n_0$:

1. **Base case:** prove $P(n_0)$.
2. **Inductive step:** for an arbitrary $k \ge n_0$, assume $P(k)$ (the **inductive hypothesis**, IH) and prove $P(k + 1)$.

Together these give $P(n_0), P(n_0 + 1), P(n_0 + 2), \dots$. The inductive step is an implication $P(k) \to P(k + 1)$; we assume $P(k)$ only to prove the next case, never the statement for all $n$.

### Writing a good induction proof

- State $P(n)$ precisely.
- Verify the base case explicitly.
- In the step, write out $P(k + 1)$ as the goal, then find where $P(k)$ appears inside it and substitute the IH.
- Finish with the algebra that produces exactly the form of $P(k + 1)$.

### Strong induction

In **strong** (complete) induction the hypothesis is that $P(n_0), P(n_0 + 1), \dots, P(k)$ are **all** true, and we prove $P(k + 1)$. It is equivalent in power to ordinary induction but more convenient when $P(k + 1)$ depends on cases further back, such as $P(k - 1)$ or an arbitrary smaller case. Such proofs may need several base cases. Classic uses: every integer $n \ge 2$ is a product of primes; any postage of 12 cents or more can be made from 4- and 5-cent stamps.

### Induction, recursion, and invariants

A recursive function is correct if it is correct on its base cases and correct on input $n$ whenever its recursive calls on smaller inputs are correct: strong induction on the input size. Loop **invariants** are proved by induction on the number of iterations: true before the first iteration (base) and preserved by each iteration (step), so true when the loop ends.

### Common flaws

An induction "proof" can be wrong if the base case is missing or false, or if the step silently fails for the smallest value of $k$. The famous "all horses are the same colour" argument fails because its step from $k = 1$ to $k = 2$ uses two overlapping groups that do not actually overlap.

## Worked examples

### Example 1: A sum and a divisibility statement

**Claim 1:** For all $n \ge 1$, $1 + 3 + 5 + \cdots + (2n - 1) = n^2$.

*Base case* ($n = 1$): the left side is 1 and $1^2 = 1$.

*Inductive step:* assume $1 + 3 + \cdots + (2k - 1) = k^2$. Then

$$1 + 3 + \cdots + (2k - 1) + (2k + 1) = k^2 + (2k + 1) = (k + 1)^2$$

which is $P(k + 1)$. So the claim holds for all $n \ge 1$. $\blacksquare$

**Claim 2:** For all $n \ge 0$, $3 \mid (n^3 + 2n)$.

*Base case* ($n = 0$): $0^3 + 0 = 0$, divisible by 3.

*Inductive step:* assume $3 \mid (k^3 + 2k)$. Then

$$(k + 1)^3 + 2(k + 1) = (k^3 + 2k) + 3k^2 + 3k + 3 = (k^3 + 2k) + 3(k^2 + k + 1)$$

The first part is divisible by 3 by the IH and the second part clearly is, so the sum is divisible by 3. $\blacksquare$

A quick numerical sanity check (not a proof) of both claims:

```python
print(all(sum(2 * i - 1 for i in range(1, n + 1)) == n * n for n in range(1, 200)))
print(all((n**3 + 2 * n) % 3 == 0 for n in range(0, 200)))
print([sum(2 * i - 1 for i in range(1, n + 1)) for n in range(1, 8)])
```

Output:

```text
True
True
[1, 4, 9, 16, 25, 36, 49]
```

### Example 2: Strong induction for postage

**Claim:** Every amount of postage $n \ge 12$ cents can be formed from 4-cent and 5-cent stamps.

*Base cases:* $12 = 4 + 4 + 4$, $13 = 4 + 4 + 5$, $14 = 4 + 5 + 5$, $15 = 5 + 5 + 5$.

*Inductive step:* let $k \ge 15$ and assume every amount from 12 to $k$ can be formed. Then $k + 1 - 4 = k - 3 \ge 12$ can be formed by the hypothesis; adding one 4-cent stamp forms $k + 1$. $\blacksquare$

The step reaches back four cases, which is why four base cases are needed. A program can find the actual stamps by following the same recursion:

```python
def stamps(n):
    base = {12: [4, 4, 4], 13: [4, 4, 5], 14: [4, 5, 5], 15: [5, 5, 5]}
    if n in base:
        return base[n]
    return stamps(n - 4) + [4]

for amount in (12, 17, 23, 30):
    s = stamps(amount)
    print(amount, "=", " + ".join(map(str, s)), "check:", sum(s) == amount)
```

Output:

```text
12 = 4 + 4 + 4 check: True
17 = 4 + 4 + 5 + 4 check: True
23 = 5 + 5 + 5 + 4 + 4 check: True
30 = 4 + 5 + 5 + 4 + 4 + 4 + 4 check: True
```

The recursive function is the proof turned into code: its base cases are the proof's base cases, and its recursive call is the inductive step.

## Applications

- **Algorithm correctness:** recursive algorithms such as merge sort are proved correct by strong induction on input size.
- **Complexity analysis:** recurrence solutions are verified by induction.
- **Loop invariants:** proving that loops compute the right result.
- **Data structures:** properties of trees, such as "a binary tree of height h has at most $2^{h+1} - 1$ nodes", follow by induction.

## Common mistakes

- **Skipping or mis-checking the base case.** Without it, the chain never starts.
- **Assuming what you want to prove.** The hypothesis is $P(k)$ for one arbitrary $k$, not "for all n".
- **Working backwards from $P(k + 1)$ without justifying each step.** Show the chain from the IH to $P(k + 1)$.
- **Too few base cases in strong induction.** If the step uses $P(k - 3)$, you need four base cases.
- **Treating numerical checks as proof.** They only build confidence.

## Revision notes

- Induction: base case $P(n_0)$, then $P(k) \to P(k + 1)$ for arbitrary $k \ge n_0$.
- Locate $P(k)$ inside $P(k + 1)$ and substitute the inductive hypothesis.
- Strong induction assumes $P(n_0), \dots, P(k)$; may need several base cases.
- Recursion correctness and loop invariants are induction proofs.
- Classic results: $\sum_{i=1}^n i = n(n+1)/2$, $\sum (2i - 1) = n^2$, $\sum_{i=0}^{n} 2^i = 2^{n+1} - 1$.
- Check the step works for the smallest $k$.

## Practice questions

:::question basic
What are the two parts of a proof by induction, and what does each establish?
:::answer
The base case proves the statement for the first value $n_0$. The inductive step proves that if the statement holds for an arbitrary $k \ge n_0$, it also holds for $k + 1$. Together they establish it for every $n \ge n_0$.
:::

:::question basic
Prove by induction that $1 + 2 + \cdots + n = \frac{n(n + 1)}{2}$ for $n \ge 1$.
:::answer
Base case: for $n = 1$, both sides equal 1. Step: assume $1 + \cdots + k = k(k + 1)/2$. Then $1 + \cdots + k + (k + 1) = \frac{k(k + 1)}{2} + (k + 1) = \frac{(k + 1)(k + 2)}{2}$, which is the formula for $n = k + 1$. Hence it holds for all $n \ge 1$.
:::

:::question intermediate
Prove that $2^n > n^2$ for all $n \ge 5$.
:::answer
Base case: $2^5 = 32 > 25$. Step: assume $2^k > k^2$ for some $k \ge 5$. Then $2^{k+1} = 2 \cdot 2^k > 2k^2$. It remains to show $2k^2 \ge (k + 1)^2$, that is, $k^2 \ge 2k + 1$, which holds for $k \ge 3$ since $k^2 - 2k - 1 = (k - 1)^2 - 2 > 0$. So $2^{k+1} > (k + 1)^2$.
:::

:::question intermediate
Why does the postage proof need four base cases?
:::answer
The inductive step builds $k + 1$ from $k - 3$ by adding a 4-cent stamp, so it relies on the case four below. To start the chain for every residue modulo 4, the four consecutive amounts 12, 13, 14, and 15 must be established directly.
:::

:::question advanced
Use strong induction to prove that every integer $n \ge 2$ can be written as a product of primes.
:::answer
Base case: 2 is prime, so it is a product of one prime. Step: assume every integer from 2 to $k$ is a product of primes, and consider $k + 1$. If $k + 1$ is prime, we are done. Otherwise $k + 1 = ab$ with $2 \le a, b \le k$; by the strong hypothesis both a and b are products of primes, so their product $k + 1$ is too. Ordinary induction would not suffice, because a and b are not necessarily equal to k.
:::

## Further learning

- **Next:** *Recurrence Relations* solves the equations that induction is often used to verify.
- **Related:** *Binary Search & Invariants* in Data Structures & Algorithms uses induction-style invariant proofs.
