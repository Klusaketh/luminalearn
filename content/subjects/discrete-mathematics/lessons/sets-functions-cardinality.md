---
lesson: sets-functions-cardinality
title: Sets, Functions & Cardinality
summary: Sets and their operations, Venn diagrams and set identities, power sets and Cartesian products, functions and their properties (injective, surjective, bijective), composition and inverses, and comparing the sizes of finite and infinite sets.
minutes: 45
type: theory
objectives:
  - Perform set operations, use set-builder notation, and compute sizes of power sets and Cartesian products
  - Determine whether a function is injective, surjective, or bijective, and compose and invert functions
  - Compare cardinalities, distinguish countable from uncountable sets, and outline Cantor's diagonal argument
review: ai-draft
---
## Introduction

Sets and functions are the vocabulary of all of mathematics and much of computer science. A database table is a set of tuples, a type in a programming language is a set of values, and a hash function is a function from keys to bucket indices. Functions also give a precise way to compare the sizes of sets, which leads to one of the most surprising results in mathematics: some infinite sets are strictly bigger than others.

**Before you start:** you should know propositional and predicate logic and basic proof techniques.

## Core theory

### Sets and notation

A **set** is an unordered collection of distinct elements: $\{1, 2, 3\} = \{3, 1, 2, 2\}$. We write $x \in A$ for membership. Sets are described by listing ($\{a, e, i, o, u\}$) or with **set-builder notation**: $\{x \in \mathbb{Z} \mid x^2 < 10\} = \{-3, \dots, 3\}$. Standard sets are $\mathbb{N}$, $\mathbb{Z}$, $\mathbb{Q}$, and $\mathbb{R}$; $\emptyset$ is the empty set. $A \subseteq B$ means every element of A is in B; $A = B$ when $A \subseteq B$ and $B \subseteq A$, which is how set equality is usually proved.

### Operations and identities

| Operation | Notation | Definition |
| :--- | :--- | :--- |
| Union | $A \cup B$ | $\{x \mid x \in A \lor x \in B\}$ |
| Intersection | $A \cap B$ | $\{x \mid x \in A \land x \in B\}$ |
| Difference | $A - B$ | $\{x \mid x \in A \land x \notin B\}$ |
| Complement | $\overline{A}$ | $\{x \in U \mid x \notin A\}$ for a universe U |
| Symmetric difference | $A \oplus B$ | in exactly one of A, B |

Set identities mirror logical equivalences, for example De Morgan's laws $\overline{A \cup B} = \overline{A} \cap \overline{B}$. For finite sets, **inclusion-exclusion** gives $|A \cup B| = |A| + |B| - |A \cap B|$.

The **power set** $\mathcal{P}(A)$ is the set of all subsets of A; if $|A| = n$, then $|\mathcal{P}(A)| = 2^n$, since each element is either in or out of a subset. The **Cartesian product** $A \times B = \{(a, b) \mid a \in A, b \in B\}$ has $|A| \cdot |B|$ ordered pairs.

### Functions

A **function** $f: A \to B$ assigns to every element of the **domain** A exactly one element of the **codomain** B. The **range** (image) is the set of values actually taken. A function is:

- **injective** (one-to-one) if $f(a_1) = f(a_2)$ implies $a_1 = a_2$: no two inputs share an output;
- **surjective** (onto) if every $b \in B$ equals $f(a)$ for some a: the range is the whole codomain;
- **bijective** if both: every element of B is hit exactly once.

The **composition** $(g \circ f)(x) = g(f(x))$ applies f first. A function has an **inverse** $f^{-1}: B \to A$ exactly when it is bijective. Whether a formula is injective or surjective depends on the domain and codomain: $f(x) = x^2$ is not injective on $\mathbb{R}$ but is a bijection from $[0, \infty)$ to $[0, \infty)$.

For finite sets with $|A| = |B| = n$, a function $A \to B$ is injective if and only if it is surjective. The number of functions from an m-element set to an n-element set is $n^m$, and the number of injective ones is $n(n-1)\cdots(n - m + 1)$.

### Cardinality and infinity

Two sets have the **same cardinality** if there is a bijection between them. A set is **countable** if it is finite or has the same cardinality as $\mathbb{N}$, meaning its elements can be listed in a sequence. Surprisingly, $\mathbb{Z}$ is countable (list $0, 1, -1, 2, -2, \dots$), and so is $\mathbb{Q}$ (list fractions by increasing $|p| + q$). But Georg Cantor proved that $\mathbb{R}$ is **uncountable** with the **diagonal argument**: given any list of real numbers in $(0, 1)$, build a number whose $k$-th decimal digit differs from the $k$-th digit of the $k$-th number; it differs from every listed number, so no list contains them all. More generally, $|\mathcal{P}(A)| > |A|$ for every set A, so there are infinitely many sizes of infinity.

## Worked examples

### Example 1: Set operations and counting with Python sets

```python
from itertools import chain, combinations, product

A = {1, 2, 3, 4}
B = {3, 4, 5}
U = set(range(1, 8))
print(sorted(A | B), sorted(A & B), sorted(A - B), sorted(A ^ B))
print("complement of (A union B):", sorted(U - (A | B)), "= (complement A) & (complement B):", sorted((U - A) & (U - B)))
print("|A union B| =", len(A | B), "=", len(A), "+", len(B), "-", len(A & B))

S = ["x", "y", "z"]
power = [set(c) for c in chain.from_iterable(combinations(S, r) for r in range(len(S) + 1))]
print(len(power), "subsets:", [sorted(s) for s in power])
print(len(list(product(A, B))), "pairs in A x B")
```

Output:

```text
[1, 2, 3, 4, 5] [3, 4] [1, 2] [1, 2, 5]
complement of (A union B): [6, 7] = (complement A) & (complement B): [6, 7]
|A union B| = 5 = 4 + 3 - 2
8 subsets: [[], ['x'], ['y'], ['z'], ['x', 'y'], ['x', 'z'], ['y', 'z'], ['x', 'y', 'z']]
12 pairs in A x B
```

The computation confirms De Morgan's law for sets, inclusion-exclusion, $|\mathcal{P}(S)| = 2^3 = 8$, and $|A \times B| = 4 \times 3 = 12$.

### Example 2: Classifying functions

Determine which of these are injective, surjective, or bijective.

1. $f: \mathbb{Z} \to \mathbb{Z}$, $f(n) = 2n + 1$. **Injective:** if $2a + 1 = 2b + 1$ then $a = b$. **Not surjective:** the output is always odd, so 4 is never reached.
2. $g: \mathbb{R} \to \mathbb{R}$, $g(x) = 3x - 5$. **Bijective:** for any $y$, $x = (y + 5)/3$ is the unique solution, so $g^{-1}(y) = (y + 5)/3$.
3. $h: \mathbb{Z} \to \mathbb{N}$, $h(n) = |n|$. **Surjective** (every $m \in \mathbb{N}$ is $h(m)$) but **not injective** ($h(-2) = h(2)$).
4. $k: \mathbb{N} \to \mathbb{Z}$ listing $0, 1, -1, 2, -2, \dots$, defined by $k(n) = n/2$ for even n and $k(n) = -(n + 1)/2$ for odd n. It is a **bijection**, which proves that $\mathbb{N}$ and $\mathbb{Z}$ have the same cardinality.

For compositions, $(g \circ g)(x) = 3(3x - 5) - 5 = 9x - 20$; a composition of bijections is a bijection.

## Applications

- **Databases:** relational algebra operations (union, intersection, difference, product) are set operations.
- **Programming:** set types give fast membership; hash functions map keys to buckets (and collisions show they are not injective).
- **Cryptography:** encryption must be a bijection so that decryption is possible.
- **Computability:** countability arguments show that most functions cannot be computed by any program, since programs are countable but functions are not.

## Common mistakes

- **Treating sets as ordered or with duplicates.** $\{1, 2\} = \{2, 1\} = \{1, 1, 2\}$.
- **Confusing $\in$ and $\subseteq$.** $1 \in \{1, 2\}$ but $\{1\} \subseteq \{1, 2\}$.
- **Forgetting the empty set in a power set.** $\mathcal{P}(A)$ always contains $\emptyset$ and A itself.
- **Ignoring the codomain.** Surjectivity depends on the codomain, not just the formula.
- **Thinking all infinite sets are the same size.** $\mathbb{R}$ is strictly larger than $\mathbb{N}$.

## Revision notes

- Union, intersection, difference, complement, symmetric difference; De Morgan for sets.
- $|A \cup B| = |A| + |B| - |A \cap B|$; $|\mathcal{P}(A)| = 2^{|A|}$; $|A \times B| = |A||B|$.
- Injective: distinct inputs give distinct outputs; surjective: every codomain element is hit; bijective: both.
- Only bijections have inverses; $(g \circ f)(x) = g(f(x))$.
- Same cardinality = a bijection exists; countable = can be listed.
- $\mathbb{N}, \mathbb{Z}, \mathbb{Q}$ are countable; $\mathbb{R}$ is uncountable (Cantor's diagonal argument).

## Practice questions

:::question basic
If $A = \{a, b, c, d\}$, how many subsets does A have, and how many of them contain exactly two elements?
:::answer
A has $2^4 = 16$ subsets. The number with exactly two elements is $\binom{4}{2} = 6$.
:::

:::question basic
In a class of 40, 25 study Python and 18 study Java, and 10 study both. How many study at least one of them?
:::answer
By inclusion-exclusion, $|P \cup J| = 25 + 18 - 10 = 33$ students. The remaining 7 study neither.
:::

:::question intermediate
Is $f: \mathbb{R} \to \mathbb{R}$, $f(x) = x^2$ injective? Surjective? How can you restrict it to make a bijection?
:::answer
It is not injective, since $f(-1) = f(1) = 1$, and not surjective onto $\mathbb{R}$, since negative numbers are never reached. Restricting both domain and codomain to $[0, \infty)$ makes it a bijection with inverse $\sqrt{y}$.
:::

:::question intermediate
How many functions are there from a 3-element set to a 5-element set, and how many of them are injective?
:::answer
Each of the 3 inputs can map to any of 5 outputs, giving $5^3 = 125$ functions. An injective function needs distinct outputs: $5 \times 4 \times 3 = 60$.
:::

:::question advanced
Explain Cantor's diagonal argument showing that the real numbers in $(0, 1)$ cannot be listed.
:::answer
Suppose a list $r_1, r_2, r_3, \dots$ contained every real number in $(0, 1)$, each written as an infinite decimal. Build a new number $x$ whose $k$-th decimal digit is 5 if the $k$-th digit of $r_k$ is not 5, and 4 otherwise (avoiding 0s and 9s sidesteps numbers with two decimal expansions). Then $x$ is in $(0, 1)$ but differs from each $r_k$ in the $k$-th digit, so it is not on the list, contradicting the assumption. Hence the reals in $(0, 1)$ are uncountable.
:::

## Further learning

- **Next:** *Equivalence Relations & Partitions* studies relations, which generalise functions.
- **Related:** *Hash Functions & Collision Handling* in Data Structures & Algorithms applies non-injective functions in practice.
