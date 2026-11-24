---
lesson: propositional-predicate-logic
title: Propositional & Predicate Logic
summary: Propositions and logical connectives, truth tables, tautologies and logical equivalence, De Morgan's laws, and predicate logic with quantifiers and their negation.
minutes: 50
type: theory
objectives:
  - Build truth tables for compound propositions and classify them as tautologies, contradictions, or contingencies
  - Prove and apply logical equivalences, including De Morgan's laws and the conditional rewrites
  - Translate statements with universal and existential quantifiers and negate them correctly
review: ai-draft
---
## Introduction

Logic is the language of precise reasoning. Every `if` condition in a program, every database query, and every mathematical proof relies on it. Propositional logic studies statements that are simply true or false and how connectives such as "and", "or", and "if ... then" combine them. Predicate logic adds variables and **quantifiers** ("for all", "there exists"), which let us state properties of whole collections, such as "every array index is valid".

**Before you start:** no prerequisites beyond school algebra; familiarity with `if` statements helps.

## Core theory

### Propositions and connectives

A **proposition** is a declarative statement that is either true (T) or false (F): "7 is prime" is true; "x > 3" is not a proposition until x is known. Compound propositions use **connectives**:

| Connective | Symbol | Read as | True when |
| :--- | :--- | :--- | :--- |
| Negation | $\neg p$ | not p | p is false |
| Conjunction | $p \land q$ | p and q | both are true |
| Disjunction | $p \lor q$ | p or q | at least one is true |
| Exclusive or | $p \oplus q$ | p xor q | exactly one is true |
| Conditional | $p \to q$ | if p then q | except when p is true and q false |
| Biconditional | $p \leftrightarrow q$ | p if and only if q | both have the same value |

The **conditional** surprises many learners: $p \to q$ is **true whenever p is false** ("vacuously true"). The promise "if it rains, I carry an umbrella" is broken only when it rains and I carry no umbrella. From $p \to q$ we form the **converse** $q \to p$, the **inverse** $\neg p \to \neg q$, and the **contrapositive** $\neg q \to \neg p$. A conditional is always equivalent to its contrapositive, but **not** to its converse or inverse.

Precedence: $\neg$ binds tightest, then $\land$, then $\lor$, then $\to$, then $\leftrightarrow$.

### Truth tables and classification

A truth table lists every combination of truth values; $n$ variables give $2^n$ rows. A compound proposition is a **tautology** if it is true in every row (such as $p \lor \neg p$), a **contradiction** if false in every row (such as $p \land \neg p$), and a **contingency** otherwise. Two propositions are **logically equivalent**, written $P \equiv Q$, when they have identical truth tables, which is the same as saying $P \leftrightarrow Q$ is a tautology.

### Key equivalences

- **De Morgan's laws:** $\neg(p \land q) \equiv \neg p \lor \neg q$ and $\neg(p \lor q) \equiv \neg p \land \neg q$.
- **Conditional:** $p \to q \equiv \neg p \lor q \equiv \neg q \to \neg p$.
- **Negated conditional:** $\neg(p \to q) \equiv p \land \neg q$.
- **Distributive:** $p \land (q \lor r) \equiv (p \land q) \lor (p \land r)$, and the same with $\land$ and $\lor$ swapped.
- **Double negation** $\neg\neg p \equiv p$, plus commutative, associative, idempotent, absorption, identity, and domination laws.

Equivalences let you simplify conditions in code: `!(a && b)` is `!a || !b`.

### Predicates and quantifiers

A **predicate** $P(x)$ becomes a proposition once $x$ takes a value from a **domain**. Quantifiers bind the variable:

- **Universal:** $\forall x\, P(x)$, "for all x in the domain, P(x)". It is false if a single **counterexample** exists.
- **Existential:** $\exists x\, P(x)$, "there is at least one x with P(x)". It is true if a single **witness** exists.

The truth of a quantified statement depends on the domain: $\forall x\,(x^2 \ge x)$ is true over the integers but false over the reals ($0.5^2 < 0.5$).

**Negating quantifiers** swaps them and negates the predicate:

$$\neg \forall x\, P(x) \equiv \exists x\, \neg P(x), \qquad \neg \exists x\, P(x) \equiv \forall x\, \neg P(x)$$

With **nested quantifiers**, order matters: $\forall x\, \exists y\, (y > x)$ ("every number has a larger one") is true over the integers, but $\exists y\, \forall x\, (y > x)$ ("some number is larger than all numbers") is false.

## Worked examples

### Example 1: Proving equivalences with a truth table program

Check De Morgan's law, the contrapositive, and the converse by comparing all truth assignments.

```python
from itertools import product

def implies(a, b):
    return (not a) or b

def equivalent(f, g, n):
    return all(f(*v) == g(*v) for v in product([True, False], repeat=n))

print("De Morgan:", equivalent(lambda p, q: not (p and q), lambda p, q: (not p) or (not q), 2))
print("contrapositive:", equivalent(lambda p, q: implies(p, q), lambda p, q: implies(not q, not p), 2))
print("converse:", equivalent(lambda p, q: implies(p, q), lambda p, q: implies(q, p), 2))

print("p q | p->q")
for p, q in product([True, False], repeat=2):
    print(int(p), int(q), "|", int(implies(p, q)))
tautology = all(implies(p and implies(p, q), q) for p, q in product([True, False], repeat=2))
print("modus ponens is a tautology:", tautology)
```

Output:

```text
De Morgan: True
contrapositive: True
converse: False
p q | p->q
1 1 | 1
1 0 | 0
0 1 | 1
0 0 | 1
modus ponens is a tautology: True
```

The conditional is false only in the row $p = 1, q = 0$. The converse differs from the conditional in two rows, so they are not equivalent. The last check shows that $(p \land (p \to q)) \to q$, the rule of **modus ponens**, is true in every row.

### Example 2: Negating a quantified statement

Negate "every student in the class passed at least one exam" and simplify.

Let $P(s, e)$ mean "student s passed exam e". The statement is $\forall s\, \exists e\, P(s, e)$. Applying the negation rules from the outside in:

$$\neg \forall s\, \exists e\, P(s, e) \equiv \exists s\, \neg \exists e\, P(s, e) \equiv \exists s\, \forall e\, \neg P(s, e)$$

In words: "some student failed every exam". Note that "no student passed any exam" ($\forall s\, \forall e\, \neg P(s, e)$) is a much stronger statement and is **not** the negation. Similarly, the negation of "$\forall x\, (x > 0 \to x^2 > 0)$" is "$\exists x\, (x > 0 \land x^2 \le 0)$", using $\neg(p \to q) \equiv p \land \neg q$.

## Applications

- **Programming:** simplifying conditions with De Morgan's laws and writing loop invariants.
- **Digital circuits:** truth tables and equivalences design and minimise logic gates.
- **Databases:** SQL `WHERE` clauses, `EXISTS`, and `NOT EXISTS` are predicate logic.
- **Specification and verification:** pre- and post-conditions are quantified statements that tools check.

## Common mistakes

- **Treating $p \to q$ as false when p is false.** A conditional with a false hypothesis is true.
- **Confusing a conditional with its converse.** "If it is a square then it is a rectangle" does not mean every rectangle is a square.
- **Negating "and" as "and".** $\neg(p \land q)$ is $\neg p \lor \neg q$, not $\neg p \land \neg q$.
- **Negating "all" as "none".** The negation of "all are" is "at least one is not".
- **Swapping nested quantifiers.** $\forall x\, \exists y$ and $\exists y\, \forall x$ generally mean different things.

## Revision notes

- Connectives: $\neg, \land, \lor, \oplus, \to, \leftrightarrow$; $n$ variables give $2^n$ truth-table rows.
- $p \to q$ is false only when p is true and q is false; $p \to q \equiv \neg p \lor q \equiv \neg q \to \neg p$.
- Tautology: always true; contradiction: always false; contingency: neither.
- De Morgan: $\neg(p \land q) \equiv \neg p \lor \neg q$; $\neg(p \lor q) \equiv \neg p \land \neg q$.
- $\neg \forall x\, P(x) \equiv \exists x\, \neg P(x)$; $\neg \exists x\, P(x) \equiv \forall x\, \neg P(x)$.
- The domain and the order of nested quantifiers change meaning.

## Practice questions

:::question basic
What is the truth value of "If 2 + 2 = 5, then the moon is made of cheese"?
:::answer
True. The hypothesis "2 + 2 = 5" is false, and a conditional with a false hypothesis is true regardless of its conclusion (it is vacuously true).
:::

:::question basic
Write the contrapositive of "If a number is divisible by 4, then it is even."
:::answer
"If a number is not even, then it is not divisible by 4." The contrapositive $\neg q \to \neg p$ is logically equivalent to the original statement.
:::

:::question intermediate
Use De Morgan's laws to simplify the condition `!(age < 18 || !hasConsent)`.
:::answer
Applying De Morgan's law gives `!(age < 18) && !!hasConsent`, which simplifies to `age >= 18 && hasConsent`: the person is an adult and has given consent.
:::

:::question intermediate
Is $(p \to q) \land (q \to p)$ equivalent to $p \leftrightarrow q$? Justify.
:::answer
Yes. Both are true exactly when p and q have the same truth value: if both are true or both false, each conditional holds; if they differ, one of the two conditionals has a true hypothesis and false conclusion, making the conjunction false. Their truth tables match, so they are equivalent.
:::

:::question advanced
Negate "For every $\varepsilon > 0$ there exists $\delta > 0$ such that for all $x$, if $|x| < \delta$ then $|f(x)| < \varepsilon$," and state it in words.
:::answer
Formally the statement is $\forall \varepsilon > 0\, \exists \delta > 0\, \forall x\, (|x| < \delta \to |f(x)| < \varepsilon)$. Negating swaps each quantifier and negates the conditional: $\exists \varepsilon > 0\, \forall \delta > 0\, \exists x\, (|x| < \delta \land |f(x)| \ge \varepsilon)$. In words: there is some positive $\varepsilon$ such that, no matter how small a positive $\delta$ is chosen, some $x$ within $\delta$ of 0 has $|f(x)|$ at least $\varepsilon$.
:::

## Further learning

- **Next:** *Proof Techniques* uses these rules to build convincing arguments.
- **Related:** *De Morgan's Laws & Canonical Forms* in Digital Logic applies the same equivalences to circuits.
