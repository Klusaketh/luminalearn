---
lesson: equivalence-relations-partitions
title: Equivalence Relations & Partitions
summary: Binary relations and their properties (reflexive, symmetric, antisymmetric, transitive), equivalence relations and equivalence classes, the correspondence between equivalence relations and partitions, and partial orders.
minutes: 45
type: theory
objectives:
  - Represent relations as sets of pairs, matrices, or digraphs and test them for reflexivity, symmetry, antisymmetry, and transitivity
  - Identify equivalence relations, compute their equivalence classes, and explain why the classes form a partition
  - Distinguish equivalence relations from partial orders and give examples of each
review: ai-draft
---
## Introduction

A relation captures how elements of a set are connected: "is a friend of", "is less than", "has the same remainder as", "is a prerequisite of". Some relations behave like a kind of **sameness**: same remainder modulo 5, same birthday, same connected component in a network. These are **equivalence relations**, and they split a set into non-overlapping groups. Others behave like **ordering**: divisibility, subset inclusion, task dependencies. Recognising which properties a relation has tells you which algorithms and reasoning apply.

**Before you start:** you should know sets, Cartesian products, functions, and proof techniques.

## Core theory

### Relations

A **binary relation** R on a set A is a subset of $A \times A$; we write $a\,R\,b$ when $(a, b) \in R$. A relation on a finite set can be shown as a list of pairs, as a 0-1 **matrix** with a 1 in row a, column b when $a\,R\,b$, or as a **directed graph** with an arrow from a to b.

### Properties

For a relation R on A:

| Property | Definition | Digraph picture |
| :--- | :--- | :--- |
| Reflexive | $a\,R\,a$ for every $a \in A$ | a loop on every vertex |
| Symmetric | $a\,R\,b \Rightarrow b\,R\,a$ | every arrow has a reverse arrow |
| Antisymmetric | $a\,R\,b \land b\,R\,a \Rightarrow a = b$ | no pair of opposite arrows between distinct vertices |
| Transitive | $a\,R\,b \land b\,R\,c \Rightarrow a\,R\,c$ | every two-step path has a shortcut arrow |

Symmetric and antisymmetric are not opposites: the equality relation is both, and some relations are neither. To show a property fails, give one specific counterexample.

### Equivalence relations and classes

An **equivalence relation** is reflexive, symmetric, and transitive. Examples: equality; "has the same length as" on strings; **congruence modulo n**, $a \equiv b \pmod n$ when $n \mid (a - b)$; and "is reachable from and can reach" in a directed graph.

The **equivalence class** of $a$ is $[a] = \{x \in A \mid x\,R\,a\}$. Key facts:

- Every element is in its own class, by reflexivity.
- Two classes are either **identical** or **disjoint**: if $[a]$ and $[b]$ share an element, transitivity and symmetry make them equal.

### Partitions

A **partition** of A is a collection of non-empty, pairwise disjoint subsets (blocks) whose union is A. The facts above show that the equivalence classes of any equivalence relation form a partition. Conversely, every partition defines an equivalence relation: "is in the same block as". So equivalence relations and partitions are two descriptions of the same structure. Congruence modulo 3 partitions $\mathbb{Z}$ into three classes, $[0]$, $[1]$, and $[2]$; the set of classes is written $\mathbb{Z}_3$.

### Partial orders

A **partial order** is reflexive, **antisymmetric**, and transitive, such as $\le$ on numbers, $\subseteq$ on sets, and divisibility on positive integers. Some pairs may be **incomparable** (neither $2 \mid 3$ nor $3 \mid 2$). If every pair is comparable, it is a **total order**. Finite partial orders are drawn as **Hasse diagrams**, and a **topological sort** lists elements in an order consistent with a partial order, as when scheduling tasks with dependencies.

### Closures

The **transitive closure** of R adds the fewest pairs needed to make R transitive; it answers "is b reachable from a?" and can be computed with Warshall's algorithm in $O(n^3)$ time. Reflexive and symmetric closures are defined similarly.

## Worked examples

### Example 1: Testing properties with code

Test four relations on $A = \{1, 2, 3, 4\}$.

```python
A = [1, 2, 3, 4]

def props(R):
    reflexive = all((a, a) in R for a in A)
    symmetric = all((b, a) in R for a, b in R)
    antisymmetric = all(a == b for a, b in R if (b, a) in R)
    transitive = all((a, d) in R for a, b in R for c, d in R if b == c)
    return reflexive, symmetric, antisymmetric, transitive

relations = {
    "same parity": {(a, b) for a in A for b in A if a % 2 == b % 2},
    "less or equal": {(a, b) for a in A for b in A if a <= b},
    "divides": {(a, b) for a in A for b in A if b % a == 0},
    "differ by 1": {(a, b) for a in A for b in A if abs(a - b) == 1},
}
print("relation       refl  sym   anti  trans")
for name, R in relations.items():
    print(f"{name:<14}", "  ".join(f"{str(p):<5}" for p in props(R)))
```

Output:

```text
relation       refl  sym   anti  trans
same parity    True   True   False  True
less or equal  True   False  True   True
divides        True   False  True   True
differ by 1    False  True   False  False
```

"Same parity" is an equivalence relation. "Less or equal" and "divides" are partial orders. "Differ by 1" is only symmetric: it is not reflexive (1 does not differ from itself by 1) and not transitive (1 relates to 2 and 2 to 3, but not 1 to 3).

### Example 2: Equivalence classes of congruence modulo 4

Find the equivalence classes of $a \equiv b \pmod 4$ on $A = \{0, 1, \dots, 11\}$ and check that they form a partition.

```python
A = range(12)
classes = {}
for x in A:
    classes.setdefault(x % 4, []).append(x)
for r, members in classes.items():
    print(f"[{r}] = {members}")
blocks = list(classes.values())
disjoint = all(set(p).isdisjoint(q) for i, p in enumerate(blocks) for q in blocks[i + 1:])
covers = sorted(x for b in blocks for x in b) == list(A)
print("pairwise disjoint:", disjoint, "| union is A:", covers)
```

Output:

```text
[0] = [0, 4, 8]
[1] = [1, 5, 9]
[2] = [2, 6, 10]
[3] = [3, 7, 11]
pairwise disjoint: True | union is A: True
```

Each number belongs to exactly one class, identified by its remainder. Checking the three properties confirms an equivalence relation: $a - a = 0$ is divisible by 4; if $4 \mid (a - b)$ then $4 \mid (b - a)$; and if $4 \mid (a - b)$ and $4 \mid (b - c)$, then $4 \mid (a - c)$ because $a - c = (a - b) + (b - c)$.

## Applications

- **Union-find data structures:** maintain equivalence classes, as in Kruskal's algorithm and connected components.
- **Modular arithmetic and hashing:** congruence classes underlie hash tables and cryptography.
- **Compilers and type systems:** type equivalence and state minimisation in automata merge equivalent items.
- **Scheduling:** partial orders of task dependencies are topologically sorted.

## Common mistakes

- **Believing symmetric and antisymmetric are opposites.** A relation can be both (equality) or neither.
- **Forgetting reflexivity.** "Has a common factor greater than 1" fails reflexivity at 1.
- **Checking transitivity only for consecutive elements.** Every pair of linked pairs must be checked.
- **Allowing empty blocks or overlaps in a partition.** Blocks must be non-empty and disjoint.

## Revision notes

- A relation on A is a subset of $A \times A$; represented as pairs, matrix, or digraph.
- Reflexive, symmetric, antisymmetric, transitive: know the definitions and digraph pictures.
- Equivalence relation = reflexive + symmetric + transitive.
- Equivalence classes are identical or disjoint and form a partition; every partition gives an equivalence relation.
- Partial order = reflexive + antisymmetric + transitive; total if all pairs are comparable.
- Transitive closure = reachability (Warshall, $O(n^3)$).

## Practice questions

:::question basic
Is "is a sibling of" (on people, meaning sharing at least one parent and being different people) an equivalence relation?
:::answer
No. It is symmetric, but it is not reflexive, because nobody is their own sibling under this definition, and it need not be transitive with half-siblings: A and B may share a mother and B and C share a father, while A and C share no parent.
:::

:::question basic
What are the equivalence classes of congruence modulo 2 on the integers?
:::answer
There are two classes: the even integers $[0] = \{\dots, -2, 0, 2, 4, \dots\}$ and the odd integers $[1] = \{\dots, -1, 1, 3, \dots\}$. Together they partition $\mathbb{Z}$.
:::

:::question intermediate
Prove that if $[a]$ and $[b]$ are equivalence classes of an equivalence relation and they share an element c, then $[a] = [b]$.
:::answer
Since $c \in [a]$ and $c \in [b]$, we have $c\,R\,a$ and $c\,R\,b$. By symmetry $a\,R\,c$, and by transitivity $a\,R\,b$. Now take any $x \in [a]$: $x\,R\,a$ and $a\,R\,b$ give $x\,R\,b$ by transitivity, so $x \in [b]$; hence $[a] \subseteq [b]$. The same argument with a and b swapped gives $[b] \subseteq [a]$, so the classes are equal.
:::

:::question intermediate
Is divisibility on the positive integers a total order? Explain.
:::answer
It is a partial order (reflexive, antisymmetric, transitive) but not a total order, because some pairs are incomparable: neither 2 divides 3 nor 3 divides 2.
:::

:::question advanced
How many equivalence relations are there on a 3-element set $\{a, b, c\}$? List the corresponding partitions.
:::answer
Equivalence relations correspond one-to-one with partitions, and a 3-element set has 5 partitions (the Bell number $B_3 = 5$): $\{\{a\},\{b\},\{c\}\}$; $\{\{a,b\},\{c\}\}$; $\{\{a,c\},\{b\}\}$; $\{\{b,c\},\{a\}\}$; and $\{\{a,b,c\}\}$. So there are 5 equivalence relations, from equality (all singletons) to the relation in which everything is equivalent.
:::

## Further learning

- **Next:** *Counting Principles & Pigeonhole Principle* counts the objects these structures contain.
- **Related:** *Minimum Spanning Trees & Disjoint Sets* uses union-find to maintain equivalence classes.
