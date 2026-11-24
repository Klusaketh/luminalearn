---
lesson: sample-spaces-axioms
title: Sample Spaces, Events & Probability Axioms
summary: The language of probability: experiments, sample spaces, and events, the three axioms and the rules derived from them, and computing probabilities by counting equally likely outcomes.
minutes: 45
type: theory
objectives:
  - Describe the sample space and events of an experiment using set notation
  - State the probability axioms and derive the complement, union, and monotonicity rules
  - Compute probabilities of equally likely outcomes with counting techniques
review: ai-draft
---
## Introduction

Probability is the mathematics of uncertainty. It tells a spam filter how likely an email is to be junk, an engineer how likely a server is to fail this year, and a game designer how often a rare item should drop. Before calculating anything, we need a precise language: what can happen (the **sample space**), which outcomes we care about (**events**), and the few rules (**axioms**) every probability must obey. Everything else in probability theory is built on these foundations.

**Before you start:** you should know sets, unions, intersections, complements, and basic counting (permutations and combinations).

## Core theory

### Experiments, sample spaces, and events

A random **experiment** is a process whose outcome is uncertain, such as rolling a die. The **sample space** $S$ (or $\Omega$) is the set of all possible outcomes: $S = \{1, 2, 3, 4, 5, 6\}$ for one die, $S = \{HH, HT, TH, TT\}$ for two coin tosses. An **event** is a subset of the sample space: "an even number" is $E = \{2, 4, 6\}$. An event **occurs** if the outcome belongs to it.

Events combine with set operations: $A \cup B$ (A or B occurs), $A \cap B$ (both occur), $A^c$ (A does not occur). Events are **mutually exclusive** (disjoint) if $A \cap B = \emptyset$: they cannot both happen.

### The axioms

A probability function $P$ assigns a number to each event so that:

1. **Non-negativity:** $P(A) \ge 0$ for every event A.
2. **Normalisation:** $P(S) = 1$.
3. **Additivity:** if $A_1, A_2, \dots$ are pairwise disjoint, $P(A_1 \cup A_2 \cup \cdots) = P(A_1) + P(A_2) + \cdots$.

These three statements, formulated by Andrey Kolmogorov in 1933, are all the theory needs.

### Consequences

From the axioms we can prove:

- **Complement rule:** $P(A^c) = 1 - P(A)$, since $A$ and $A^c$ are disjoint and their union is $S$.
- $P(\emptyset) = 0$, and $0 \le P(A) \le 1$.
- **Monotonicity:** if $A \subseteq B$, then $P(A) \le P(B)$.
- **Inclusion-exclusion:** $P(A \cup B) = P(A) + P(B) - P(A \cap B)$.

The complement rule is often the easiest route: "at least one" problems become "1 minus the probability of none".

### Equally likely outcomes

If $S$ is finite and every outcome is equally likely, then

$$P(A) = \frac{|A|}{|S|}$$

so probability reduces to counting. This is the **classical** definition, appropriate for fair dice, well-shuffled cards, and random selection. It does not apply when outcomes are not equally likely, such as the sum of two dice viewed as the values 2 to 12. Other interpretations of probability include the **frequentist** view (long-run relative frequency) and the **Bayesian** view (degree of belief); all satisfy the same axioms.

## Worked examples

### Example 1: Two dice by counting

Roll two fair dice. Find the probability that the sum is 7, that at least one die shows 6, and that the sum is 7 or at least one die shows 6.

The sample space has $6 \times 6 = 36$ equally likely ordered pairs.

- Sum 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1), so $6/36 = 1/6$.
- At least one 6: complement of "no 6", so $1 - (5/6)^2 = 1 - 25/36 = 11/36$.
- Union: the overlap "sum 7 and a 6" is (1,6) and (6,1), so by inclusion-exclusion $6/36 + 11/36 - 2/36 = 15/36 = 5/12$.

```python
from fractions import Fraction
from itertools import product

S = list(product(range(1, 7), repeat=2))
def P(event):
    return Fraction(sum(1 for o in S if event(o)), len(S))

seven = lambda o: o[0] + o[1] == 7
six = lambda o: 6 in o
print(P(seven), P(six), P(lambda o: seven(o) or six(o)))
print(P(seven) + P(six) - P(lambda o: seven(o) and six(o)))
print("P(sum = s):", [str(P(lambda o, s=s: sum(o) == s)) for s in range(2, 13)])
```

Output:

```text
1/6 11/36 5/12
5/12
P(sum = s): ['1/36', '1/18', '1/12', '1/9', '5/36', '1/6', '5/36', '1/9', '1/12', '1/18', '1/36']
```

Enumerating the 36 outcomes confirms the hand calculations, and the last line shows that the sums 2 to 12 are **not** equally likely, even though each ordered pair is.

### Example 2: Cards and the birthday problem

**(a)** Five cards are dealt from a standard deck. What is the probability of a flush (all five of one suit)?

There are $\binom{52}{5}$ equally likely hands; a flush picks a suit (4 ways) and 5 of its 13 cards: $4\binom{13}{5}$. So $P = \frac{4 \times 1287}{2{,}598{,}960} \approx 0.00198$ (including straight flushes).

**(b)** In a group of 23 people, what is the probability that two share a birthday (ignoring leap years)?

Use the complement: all birthdays different has probability $\frac{365}{365} \cdot \frac{364}{365} \cdots \frac{343}{365}$.

```python
from math import comb, prod

print(round(4 * comb(13, 5) / comb(52, 5), 5))
for n in (10, 23, 50):
    distinct = prod((365 - i) / 365 for i in range(n))
    print(n, "people:", round(1 - distinct, 4))
```

Output:

```text
0.00198
10 people: 0.1169
23 people: 0.5073
50 people: 0.9704
```

With just 23 people, a shared birthday is more likely than not, because there are $\binom{23}{2} = 253$ pairs that could match.

## Applications

- **Reliability:** the probability that at least one of several components fails uses the complement rule.
- **Security:** the birthday problem explains hash collisions and why hash outputs need many bits.
- **Games and simulations:** fair dice, cards, and loot drops rely on equally likely outcomes.
- **Quality control:** sampling items from a batch is counting with combinations.

## Common mistakes

- **Treating unequal outcomes as equally likely.** The sums of two dice are not uniform.
- **Adding probabilities of overlapping events.** Subtract the intersection.
- **Confusing mutually exclusive with independent.** Disjoint events with positive probability are never independent.
- **Computing "at least one" directly.** The complement is usually much easier.
- **Probabilities outside [0, 1].** A result above 1 or below 0 signals an error.

## Revision notes

- Sample space S: all outcomes; event: a subset of S.
- Axioms: $P(A) \ge 0$; $P(S) = 1$; additivity for disjoint events.
- $P(A^c) = 1 - P(A)$; $P(A \cup B) = P(A) + P(B) - P(A \cap B)$.
- Equally likely outcomes: $P(A) = |A|/|S|$.
- "At least one" = 1 - P(none).
- Birthday problem: 23 people give about a 50.7% chance of a shared birthday.

## Practice questions

:::question basic
A card is drawn from a standard deck. What is the probability it is a heart or a king?
:::answer
$P(\text{heart}) = 13/52$, $P(\text{king}) = 4/52$, and $P(\text{king of hearts}) = 1/52$. By inclusion-exclusion, $13/52 + 4/52 - 1/52 = 16/52 = 4/13$.
:::

:::question basic
If $P(A) = 0.35$, what is $P(A^c)$?
:::answer
$P(A^c) = 1 - 0.35 = 0.65$, by the complement rule.
:::

:::question intermediate
A fair coin is tossed 5 times. What is the probability of at least one head?
:::answer
The only outcome with no heads is TTTTT, with probability $(1/2)^5 = 1/32$. So $P(\text{at least one head}) = 1 - 1/32 = 31/32$.
:::

:::question intermediate
Prove from the axioms that $P(A \cup B) = P(A) + P(B) - P(A \cap B)$.
:::answer
Write $A \cup B$ as the disjoint union of $A$ and $B \cap A^c$, so $P(A \cup B) = P(A) + P(B \cap A^c)$. Also $B$ is the disjoint union of $B \cap A$ and $B \cap A^c$, so $P(B \cap A^c) = P(B) - P(A \cap B)$. Substituting gives the result.
:::

:::question advanced
A committee of 4 is chosen at random from 6 women and 5 men. What is the probability that it contains at least one man?
:::answer
Total committees: $\binom{11}{4} = 330$. Committees with no man: $\binom{6}{4} = 15$. By the complement rule, $P(\text{at least one man}) = 1 - 15/330 = 315/330 = 21/22 \approx 0.955$.
:::

## Further learning

- **Next:** *Conditional Probability & Bayes Theorem* updates probabilities when new information arrives.
- **Related:** *Counting Principles & Pigeonhole Principle* in Discrete Mathematics supplies the counting tools.
