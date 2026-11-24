---
lesson: proof-techniques
title: Proof Techniques
summary: How to write rigorous mathematical proofs using direct proof, proof by contrapositive, proof by contradiction, proof by cases, and counterexamples, with guidance on structure and common errors.
minutes: 45
type: theory
objectives:
  - Write direct proofs and proofs by contrapositive for statements about integers
  - Construct proofs by contradiction and by cases, and disprove universal claims with counterexamples
  - Choose an appropriate proof strategy for a statement and avoid common logical errors
review: ai-draft
---
## Introduction

A **proof** is a sequence of logically valid steps that establishes a statement beyond doubt, starting from definitions, axioms, and previously proven results. Proofs are how mathematics guarantees that something is true in every case, not just in the cases we tested. In computer science, proofs show that algorithms are correct, that a problem cannot be solved faster than some bound, and that a protocol is secure. This lesson covers the core strategies every later topic relies on.

**Before you start:** you should know propositional and predicate logic, especially conditionals, contrapositives, and quantifiers.

## Core theory

### Definitions are the starting point

Proofs about integers rely on precise definitions:

- $n$ is **even** if $n = 2k$ for some integer $k$; **odd** if $n = 2k + 1$.
- $a$ **divides** $b$, written $a \mid b$, if $b = ak$ for some integer $k$.
- A real number $r$ is **rational** if $r = p/q$ for integers $p, q$ with $q \ne 0$.

Most proof steps either unfold a definition ("since n is odd, $n = 2k + 1$") or fold one back ("so $n^2 = 2m + 1$, which is odd").

### Direct proof

To prove $p \to q$, **assume p** and derive q through a chain of valid steps. This is the most common strategy and should be tried first.

### Proof by contrapositive

Since $p \to q \equiv \neg q \to \neg p$, you may instead assume $\neg q$ and derive $\neg p$. This helps when the negation of the conclusion gives you something concrete to work with, as in "if $n^2$ is even then n is even": assuming n is odd gives a formula for n, while assuming $n^2$ is even gives little.

### Proof by contradiction

Assume the statement is **false** and derive a contradiction, something of the form $r \land \neg r$, such as an integer that is both even and odd or a fraction not in lowest terms after assuming it was. Since a valid argument from a true premise cannot reach a falsehood, the assumption must be wrong. Classic examples are the irrationality of $\sqrt{2}$ and the infinitude of primes.

### Proof by cases (exhaustion)

If every possibility falls into one of finitely many cases, prove the statement in each case separately. Typical splits are "n even or n odd", "x ≥ 0 or x < 0", or remainders modulo 3. The cases must **cover every possibility**.

### Counterexamples

To **disprove** a universal statement $\forall x\, P(x)$, one counterexample suffices: a specific $x$ for which $P(x)$ is false. To prove a universal statement, however, examples are never enough, however many you check.

### Existence proofs

To prove $\exists x\, P(x)$, a **constructive** proof exhibits a specific $x$; a **non-constructive** proof shows that one must exist without saying which.

### Writing proofs well

State what you are proving and which method you use, introduce every variable, justify each step, and end with a clear conclusion (often marked $\blacksquare$). Common errors include assuming what you are trying to prove (circular reasoning), proving only the converse, and generalising from examples.

## Worked examples

### Example 1: Direct proof and proof by contrapositive

**Claim A:** If $n$ is odd, then $n^2$ is odd.

*Direct proof.* Assume n is odd, so $n = 2k + 1$ for some integer k. Then $n^2 = 4k^2 + 4k + 1 = 2(2k^2 + 2k) + 1$. Since $2k^2 + 2k$ is an integer, $n^2$ has the form $2m + 1$ and is odd. $\blacksquare$

**Claim B:** If $n^2$ is even, then $n$ is even.

*Proof by contrapositive.* The contrapositive is "if n is odd, then $n^2$ is odd", which is exactly Claim A, already proven. Therefore Claim B holds. $\blacksquare$

Trying Claim B directly is awkward: from $n^2 = 2m$ there is no simple way to extract a formula for n.

### Example 2: Contradiction, cases, and a counterexample check

**Claim C:** $\sqrt{2}$ is irrational.

*Proof by contradiction.* Suppose $\sqrt{2} = p/q$ with integers $p, q$, $q \ne 0$, and the fraction in lowest terms. Squaring gives $p^2 = 2q^2$, so $p^2$ is even, and by Claim B, p is even: $p = 2r$. Then $4r^2 = 2q^2$, so $q^2 = 2r^2$ is even and q is even too. But then 2 divides both p and q, contradicting lowest terms. Hence $\sqrt{2}$ is irrational. $\blacksquare$

**Claim D:** For every integer $n$, $n^2 + n$ is even.

*Proof by cases.* If n is even, $n = 2k$ and $n^2 + n = 4k^2 + 2k = 2(2k^2 + k)$. If n is odd, $n = 2k + 1$ and $n^2 + n = (2k + 1)(2k + 2) = 2(2k + 1)(k + 1)$. Both cases give an even number, and every integer is even or odd. $\blacksquare$

**Claim E (false):** "$n^2 + n + 41$ is prime for every natural number $n$." It holds for $n = 0, \dots, 39$, which shows why checking examples proves nothing; a program finds the first counterexample:

```python
def is_prime(m):
    return m > 1 and all(m % d for d in range(2, int(m ** 0.5) + 1))

checked = [n for n in range(0, 50) if not is_prime(n * n + n + 41)]
print("first counterexample:", checked[0], "gives", checked[0] ** 2 + checked[0] + 41, "=", 41, "*", 41)
print("claim D holds for -100..100:", all((n * n + n) % 2 == 0 for n in range(-100, 101)))
```

Output:

```text
first counterexample: 40 gives 1681 = 41 * 41
claim D holds for -100..100: True
```

The second line checks Claim D on 201 values, which is reassuring but is **not** a proof; the case analysis above is.

## Applications

- **Algorithm correctness:** proofs by contradiction show greedy choices are optimal; invariants prove loops correct.
- **Complexity theory:** contradiction proves impossibility results, such as lower bounds for comparison sorting.
- **Cryptography:** security reductions are proofs that breaking a scheme would solve a hard problem.
- **Software verification:** proof assistants check machine-readable proofs of program properties.

## Common mistakes

- **Proving by examples.** Checking many cases never proves a universal statement.
- **Proving the converse.** Showing $q \to p$ does not establish $p \to q$.
- **Circular reasoning.** Using the claim itself, or an equivalent restatement, as a step.
- **Incomplete case analysis.** Every possibility must be covered.
- **Reusing a variable.** If m and n are both odd, write $m = 2a + 1$ and $n = 2b + 1$, not the same k for both.

## Revision notes

- Unfold definitions: even $= 2k$, odd $= 2k + 1$, $a \mid b \iff b = ak$.
- Direct: assume p, derive q.
- Contrapositive: assume $\neg q$, derive $\neg p$.
- Contradiction: assume the statement is false and derive $r \land \neg r$.
- Cases: split into exhaustive cases and prove each.
- One counterexample disproves a universal claim; examples never prove one.

## Practice questions

:::question basic
Prove that the sum of two even integers is even.
:::answer
Let $a = 2j$ and $b = 2k$ for integers j and k. Then $a + b = 2j + 2k = 2(j + k)$, and since $j + k$ is an integer, $a + b$ is even.
:::

:::question basic
Disprove: "Every prime number is odd."
:::answer
2 is prime and even, so it is a counterexample. One counterexample is enough to disprove a universal statement.
:::

:::question intermediate
Prove by contrapositive: if $3n + 2$ is odd, then $n$ is odd.
:::answer
The contrapositive is "if n is even, then $3n + 2$ is even". Let $n = 2k$. Then $3n + 2 = 6k + 2 = 2(3k + 1)$, which is even. Since the contrapositive holds, the original statement holds.
:::

:::question intermediate
Prove that for every integer $n$, $n^2 \bmod 3$ is either 0 or 1.
:::answer
Use cases on $n \bmod 3$. If $n = 3k$, then $n^2 = 9k^2 = 3(3k^2)$, remainder 0. If $n = 3k + 1$, then $n^2 = 9k^2 + 6k + 1 = 3(3k^2 + 2k) + 1$, remainder 1. If $n = 3k + 2$, then $n^2 = 9k^2 + 12k + 4 = 3(3k^2 + 4k + 1) + 1$, remainder 1. Every integer falls in one case, so the remainder is never 2.
:::

:::question advanced
Prove that there are infinitely many primes.
:::answer
Suppose, for contradiction, that there are finitely many primes $p_1, p_2, \dots, p_k$. Let $N = p_1 p_2 \cdots p_k + 1$. N is greater than 1, so it has a prime factor p, which must be one of the $p_i$. But each $p_i$ divides $p_1 \cdots p_k$, so if it also divided N it would divide $N - p_1 \cdots p_k = 1$, which is impossible. This contradiction shows the list cannot be complete, so there are infinitely many primes.
:::

## Further learning

- **Next:** *Sets, Functions & Cardinality* applies these techniques to sets and functions.
- **Related:** *Induction Proof Techniques* adds the most important method for statements about all natural numbers.
