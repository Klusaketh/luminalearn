---
lesson: counting-principles-pigeonhole
title: Counting Principles & Pigeonhole Principle
summary: The sum and product rules, the subtraction (inclusion-exclusion) and division rules, tree diagrams for counting, and the pigeonhole principle with its generalised form and classic proofs.
minutes: 45
type: theory
objectives:
  - Count outcomes with the sum, product, subtraction, and division rules, choosing the right rule for each situation
  - Apply inclusion-exclusion to two and three sets
  - State and apply the pigeonhole principle and its generalised form to prove existence results
review: ai-draft
---
## Introduction

How many passwords of a given form exist? How many IP addresses are possible? Must two people in a room share a birthday? Counting questions like these appear everywhere in computer science: estimating the size of a search space, analysing algorithms, judging the strength of a key. A few simple rules, combined carefully, answer most of them. The **pigeonhole principle**, almost too simple to need stating, proves surprisingly powerful existence results.

**Before you start:** you should know sets, unions, Cartesian products, and functions.

## Core theory

### The product rule

If a task consists of a sequence of $k$ steps, where step $i$ can be done in $n_i$ ways regardless of earlier choices, the whole task can be done in $n_1 \times n_2 \times \cdots \times n_k$ ways. Equivalently, $|A_1 \times \cdots \times A_k| = |A_1| \cdots |A_k|$. Examples: there are $2^8 = 256$ bit strings of length 8, and $26^3 \times 10^4$ licence plates of the form three letters then four digits.

### The sum rule

If a task can be done in one of several **mutually exclusive** ways, with $n_1$ ways of the first kind, $n_2$ of the second, and so on, the total is $n_1 + n_2 + \cdots$. Equivalently, $|A \cup B| = |A| + |B|$ for **disjoint** sets. Example: a password of length 6, 7, or 8 counts each length separately and adds.

### The subtraction rule (inclusion-exclusion)

When the ways overlap, subtract the double-counted ones:

$$|A \cup B| = |A| + |B| - |A \cap B|$$

$$|A \cup B \cup C| = |A| + |B| + |C| - |A \cap B| - |A \cap C| - |B \cap C| + |A \cap B \cap C|$$

Often it is easier to count the **complement**: the number of 8-bit strings with at least one 1 is $2^8 - 1$.

### The division rule

If a counting procedure counts every outcome exactly $d$ times, divide by $d$. Seating $n$ people around a round table counts each arrangement $n$ times (once per rotation), so there are $n!/n = (n - 1)!$ distinct circular seatings.

### Tree diagrams

When later choices depend on earlier ones, draw a **tree**: each branch is a choice and each leaf an outcome. Counting leaves handles problems such as "best of three" matches, where the number of games played varies.

### The pigeonhole principle

If $k + 1$ or more objects are placed into $k$ boxes, some box contains at least two objects. Proof: if every box held at most one object, there would be at most $k$ objects.

The **generalised** principle: if $N$ objects are placed into $k$ boxes, some box contains at least $\lceil N/k \rceil$ objects. The art lies in choosing what the "boxes" are.

Classic applications:

- Among any 13 people, two share a birth month.
- Among any 367 people, two share a birthday (counting 29 February).
- A lossless compression algorithm cannot shorten every file: there are $2^n$ files of length $n$ but only $2^n - 1$ shorter bit strings.
- Any hash function from a larger set of keys into fewer buckets must have collisions.

## Worked examples

### Example 1: Passwords with the sum, product, and subtraction rules

A password has 6 to 8 characters, each an uppercase letter or a digit, and must contain at least one digit. How many passwords are possible?

For length $n$: all strings $36^n$, minus those with no digit, $26^n$. By the sum rule over the three lengths:

$$P = \sum_{n=6}^{8} (36^n - 26^n)$$

```python
total = sum(36**n - 26**n for n in range(6, 9))
print(f"{total:,} passwords")
digits = "0123456789"
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + digits
from itertools import product
small = sum(1 for n in (1, 2) for s in product(alphabet, repeat=n) if any(c in digits for c in s))
print(small, "==", sum(36**n - 26**n for n in (1, 2)))
```

Output:

```text
2,684,483,063,360 passwords
630 == 630
```

The last line confirms the complement method by brute force on lengths 1 and 2, where enumerating every string is cheap: $(36 - 26) + (1296 - 676) = 10 + 620 = 630$.

### Example 2: Pigeonhole proofs

**(a)** In any set of 6 integers, two of them have a difference divisible by 5.

*Proof.* Use the 5 possible remainders modulo 5 as boxes. Six integers in five boxes means two share a remainder, say $a \equiv b \pmod 5$, so $5 \mid (a - b)$. $\blacksquare$

**(b)** A university has 1,000 students taking a 7-question true/false quiz. At least how many students give exactly the same answers?

There are $2^7 = 128$ possible answer sheets (boxes) and 1,000 students (objects). By the generalised principle, some answer sheet is shared by at least $\lceil 1000/128 \rceil = \lceil 7.8125 \rceil = 8$ students.

**(c)** Choosing any 5 points inside a square of side 2, two of them are at most $\sqrt{2}$ apart.

*Proof.* Divide the square into four unit squares (boxes). Five points in four boxes put two points in the same unit square, and the farthest apart two points in a unit square can be is its diagonal, $\sqrt{2}$. $\blacksquare$

## Applications

- **Security:** password and key-space sizes measure resistance to brute-force attacks.
- **Hashing:** the pigeonhole principle guarantees collisions, so hash tables must handle them.
- **Compression:** no lossless method can shrink every input.
- **Algorithm analysis:** counting configurations bounds the work of exhaustive search.

## Common mistakes

- **Adding when you should multiply.** Sequential independent choices multiply; alternative exclusive choices add.
- **Double counting overlapping cases.** Use inclusion-exclusion or count the complement.
- **Forgetting that choices depend on earlier ones.** Use a tree or adjust the counts per step.
- **Choosing the wrong boxes in pigeonhole proofs.** The boxes must capture the property you want to force.
- **Misusing the generalised principle.** It is $\lceil N/k \rceil$, a ceiling, not $N/k$.

## Revision notes

- Product rule: sequential choices multiply.
- Sum rule: mutually exclusive alternatives add.
- Inclusion-exclusion: $|A \cup B| = |A| + |B| - |A \cap B|$, extended to three sets with alternating signs.
- Complement counting: total minus the unwanted outcomes.
- Division rule: divide when each outcome is counted $d$ times; circular arrangements $(n - 1)!$.
- Pigeonhole: $N$ objects in $k$ boxes put at least $\lceil N/k \rceil$ in some box.

## Practice questions

:::question basic
How many different 4-digit PINs are there if digits may repeat? How many if they may not?
:::answer
With repetition, each of the 4 positions has 10 choices: $10^4 = 10{,}000$. Without repetition: $10 \times 9 \times 8 \times 7 = 5{,}040$.
:::

:::question basic
What is the minimum number of students needed to guarantee that two of them were born on the same day of the week?
:::answer
8. With 7 days as boxes, 8 students guarantee two in the same box, while 7 students could all be born on different days.
:::

:::question intermediate
How many integers from 1 to 1000 are divisible by 3 or 5?
:::answer
Divisible by 3: $\lfloor 1000/3 \rfloor = 333$; by 5: 200; by both (by 15): 66. By inclusion-exclusion, $333 + 200 - 66 = 467$.
:::

:::question intermediate
In how many ways can 6 people sit around a circular table, if only their relative positions matter?
:::answer
Arranging 6 people in a row gives $6! = 720$ orders, but each circular seating is counted 6 times, once for each rotation. By the division rule there are $720 / 6 = 120 = 5!$ circular seatings.
:::

:::question advanced
Prove that in any group of 6 people, there are either 3 mutual friends or 3 mutual strangers.
:::answer
Pick one person P. Of the other 5, by the generalised pigeonhole principle at least $\lceil 5/2 \rceil = 3$ are friends of P or at least 3 are strangers to P; suppose 3 are friends (the stranger case is symmetric). If any two of those 3 are friends, they and P form 3 mutual friends. Otherwise, those 3 are pairwise strangers, forming 3 mutual strangers. Either way the claim holds (this is the Ramsey number $R(3,3) = 6$).
:::

## Further learning

- **Next:** *Permutations, Combinations & the Binomial Theorem* counts arrangements and selections systematically.
- **Related:** *Hash Functions & Collision Handling* shows the pigeonhole principle at work in data structures.
