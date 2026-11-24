---
lesson: first-order-logic-resolution
title: First-Order Logic & Resolution
summary: First-order logic with objects, predicates, functions, and quantifiers; translating English into logic; inference with unification and generalised modus ponens; forward and backward chaining; and resolution with CNF conversion, Skolemisation, and refutation.
minutes: 45
type: theory
objectives:
  - Translate statements between English and first-order logic, using quantifiers correctly
  - Compute most general unifiers and apply generalised modus ponens with forward chaining
  - Convert first-order sentences to clausal form with Skolemisation and prove entailment by resolution refutation
review: ai-draft
---
## Introduction

Propositional logic needs a separate symbol for every fact: one for "Asha is a student", another for "Ravi is a student", and so on. It cannot say "every student who studies passes" in one sentence. **First-order logic** (FOL) adds objects, relations, functions, and quantifiers, so a single rule can cover infinitely many cases. It is the language of mathematics, databases, and logic programming, and its inference methods power theorem provers and languages like Prolog.

**Before you start:** you should know *Propositional Logic & Inference*, including CNF and resolution.

## Core theory

### Syntax

- **Constants** name objects: $Asha$, $Ravi$.
- **Predicates** express properties and relations: $Student(x)$, $Knows(x, y)$.
- **Functions** map objects to objects: $Mother(x)$.
- **Variables** such as $x, y$ range over objects. **Terms** are constants, variables, or functions applied to terms.
- **Atomic sentences** apply a predicate to terms; complex sentences use the connectives and the quantifiers $\forall$ (for all) and $\exists$ (there exists), plus equality.

A **model** contains a domain of objects and an interpretation of every symbol.

### Using quantifiers correctly

- "Every student who studies passes": $\forall x\, (Student(x) \land Studies(x)) \Rightarrow Passes(x)$. The universal quantifier pairs naturally with $\Rightarrow$.
- "Some course is difficult": $\exists x\, Course(x) \land Difficult(x)$. The existential quantifier pairs with $\land$; writing $\exists x\, Course(x) \Rightarrow Difficult(x)$ would be true merely if some object is not a course.
- Order matters: $\forall x\, \exists y\, Loves(x, y)$ (everyone loves someone) differs from $\exists y\, \forall x\, Loves(x, y)$ (someone is loved by everyone).
- Negation swaps quantifiers: $\neg\forall x\, P(x) \equiv \exists x\, \neg P(x)$.

### Unification and generalised modus ponens

**Unification** finds a substitution $\theta$ that makes two expressions identical. The **most general unifier** (MGU) commits to as little as possible. A variable cannot be unified with a term that contains it (the **occurs check**), and the variables of different sentences are renamed apart first (**standardising apart**).

**Generalised modus ponens** lifts modus ponens to FOL: from $p_1', \dots, p_n'$ and $(p_1 \land \dots \land p_n \Rightarrow q)$, where $\theta$ unifies each $p_i'$ with $p_i$, infer $q\theta$. Applied repeatedly to definite clauses, it gives **forward chaining** (used in deductive databases such as Datalog) and **backward chaining** (used in Prolog).

### Resolution in first-order logic

To use resolution, convert sentences to **clausal form**:

1. Eliminate $\Leftrightarrow$ and $\Rightarrow$.
2. Move $\neg$ inwards, flipping quantifiers as needed.
3. Standardise variables apart.
4. **Skolemise:** replace each existentially quantified variable with a new function of the enclosing universally quantified variables (or a new constant if there are none).
5. Drop the universal quantifiers.
6. Distribute $\lor$ over $\land$ to obtain clauses.

The resolution rule now unifies complementary literals: from $\neg P(x) \lor Q(x)$ and $P(Ravi)$, with $\theta = \{x/Ravi\}$, infer $Q(Ravi)$. Resolution refutation is **complete**: if the KB entails $\alpha$, adding $\neg\alpha$ will eventually yield the empty clause. However, first-order entailment is only **semidecidable**: if $\alpha$ is not entailed, the procedure may run forever.

## Worked examples

### Example 1: Unification and forward chaining with variables

Lowercase names are variables and capitalised names are constants. The program computes most general unifiers and then derives grandparent facts from a rule.

```python
def is_var(t):
    return isinstance(t, str) and t[0].islower()


def substitute(t, theta):
    if is_var(t):
        return substitute(theta[t], theta) if t in theta else t
    if isinstance(t, tuple):
        return tuple(substitute(x, theta) for x in t)
    return t


def occurs(var, t, theta):
    t = substitute(t, theta)
    return t == var or (isinstance(t, tuple) and any(occurs(var, x, theta) for x in t))


def unify(a, b, theta=None):
    """Most general unifier of terms a and b, or None. Variables start lowercase."""
    theta = {} if theta is None else theta
    a, b = substitute(a, theta), substitute(b, theta)
    if a == b:
        return theta
    if is_var(a):
        return None if occurs(a, b, theta) else {**theta, a: b}
    if is_var(b):
        return unify(b, a, theta)
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b) and a[0] == b[0]:
        for x, y in zip(a[1:], b[1:]):
            theta = unify(x, y, theta)
            if theta is None:
                return None
        return theta
    return None


def show(t):
    return t if not isinstance(t, tuple) else f"{t[0]}({', '.join(show(x) for x in t[1:])})"


pairs = [
    (("Knows", "Asha", "x"), ("Knows", "Asha", "Ravi")),
    (("Knows", "Asha", "x"), ("Knows", "y", ("Mother", "y"))),
    (("Knows", "Asha", "x"), ("Knows", "x", "Ravi")),
    (("Knows", "Asha", "x"), ("Knows", "y", "z")),
    ("x", ("Father", "x")),
]
for a, b in pairs:
    theta = unify(a, b)
    result = "fail" if theta is None else "{" + ", ".join(f"{v}/{show(substitute(v, theta))}" for v in sorted(theta)) + "}"
    print(f"UNIFY({show(a)}, {show(b)}) = {result}")

# Forward chaining with variables: Parent(p, q) & Parent(q, r) => Grandparent(p, r)
facts = {("Parent", "Meena", "Arjun"), ("Parent", "Arjun", "Kavya"), ("Parent", "Arjun", "Dev")}
rule = ([("Parent", "p", "q"), ("Parent", "q", "r")], ("Grandparent", "p", "r"))
new = set()
for f1 in sorted(facts):
    for f2 in sorted(facts):
        theta = unify(rule[0][0], f1)
        theta = unify(rule[0][1], f2, theta) if theta is not None else None
        if theta is not None:
            new.add(substitute(rule[1], theta))
print("derived:", ", ".join(show(f) for f in sorted(new)))
```

Output:

```text
UNIFY(Knows(Asha, x), Knows(Asha, Ravi)) = {x/Ravi}
UNIFY(Knows(Asha, x), Knows(y, Mother(y))) = {x/Mother(Asha), y/Asha}
UNIFY(Knows(Asha, x), Knows(x, Ravi)) = fail
UNIFY(Knows(Asha, x), Knows(y, z)) = {x/z, y/Asha}
UNIFY(x, Father(x)) = fail
derived: Grandparent(Meena, Dev), Grandparent(Meena, Kavya)
```

The second case shows chaining of bindings: $y$ must be Asha, so $x$ must be $Mother(Asha)$. The third case fails because $x$ would have to be both Asha and Ravi; it succeeds if the second sentence is first standardised apart, renaming its $x$ to $x_2$, which gives $\{x/Ravi, x_2/Asha\}$. The fourth result $\{x/z, y/Asha\}$ is the most general unifier: it does not bind $z$ to anything specific. The last case fails the occurs check, since $x = Father(x)$ has no finite solution. Finally, the rule $Parent(p, q) \land Parent(q, r) \Rightarrow Grandparent(p, r)$ fires twice, deriving both grandchildren of Meena.

### Example 2: A resolution refutation

KB: (1) $\forall x\, Student(x) \land Studies(x) \Rightarrow Passes(x)$; (2) $\forall y\, Topper(y) \Rightarrow Studies(y)$; (3) $Student(Ravi)$; (4) $Topper(Ravi)$. Prove $Passes(Ravi)$.

Clauses: (1) $\neg Student(x) \lor \neg Studies(x) \lor Passes(x)$; (2) $\neg Topper(y) \lor Studies(y)$; (3) $Student(Ravi)$; (4) $Topper(Ravi)$; negated goal (5) $\neg Passes(Ravi)$.

1. Resolve (1) and (5) with $\{x/Ravi\}$: (6) $\neg Student(Ravi) \lor \neg Studies(Ravi)$.
2. Resolve (6) and (3): (7) $\neg Studies(Ravi)$.
3. Resolve (7) and (2) with $\{y/Ravi\}$: (8) $\neg Topper(Ravi)$.
4. Resolve (8) and (4): the empty clause.

So $Passes(Ravi)$ is entailed. For Skolemisation, "everyone has a mentor", $\forall x\, \exists y\, Mentor(y, x)$, becomes $Mentor(M(x), x)$ with a Skolem function $M$, because the mentor may depend on $x$; "someone mentors everyone", $\exists y\, \forall x\, Mentor(y, x)$, becomes $Mentor(C, x)$ with a Skolem constant $C$.

## Applications

- **Logic programming:** Prolog answers queries by backward chaining with unification.
- **Deductive databases:** Datalog rules derive new facts by forward chaining.
- **Theorem proving and verification:** resolution-based provers check mathematical proofs and software properties.
- **Knowledge-based systems:** business rules and type checkers rely on unification.

## Common mistakes

- **Using $\land$ with $\forall$.** $\forall x\, Student(x) \land Passes(x)$ claims everything is a student who passes.
- **Using $\Rightarrow$ with $\exists$.** It makes the sentence trivially true.
- **Swapping quantifier order.** $\forall x\, \exists y$ and $\exists y\, \forall x$ mean different things.
- **Skipping the occurs check or standardising apart.** Both can produce wrong unifiers.
- **Skolemising with a constant inside a universal quantifier.** The Skolem term must depend on the enclosing universal variables.

## Revision notes

- FOL: constants, predicates, functions, variables, quantifiers, equality.
- $\forall$ goes with $\Rightarrow$; $\exists$ goes with $\land$; quantifier order matters.
- Unification finds the MGU; occurs check; standardise variables apart.
- Generalised modus ponens; forward chaining (Datalog), backward chaining (Prolog).
- Clausal form: eliminate implications, push negations, standardise, Skolemise, drop $\forall$, distribute.
- Resolution refutation is complete; FOL entailment is semidecidable.

## Practice questions

:::question basic
Translate "Every student who studies passes" into first-order logic.
:::answer
$\forall x\, (Student(x) \land Studies(x)) \Rightarrow Passes(x)$.
:::

:::question basic
Translate "Some course is difficult", and explain why $\Rightarrow$ would be wrong here.
:::answer
$\exists x\, Course(x) \land Difficult(x)$. Writing $\exists x\, Course(x) \Rightarrow Difficult(x)$ would be true as soon as any object is not a course (making the implication true), so it would not say that a difficult course exists.
:::

:::question intermediate
Find the most general unifier of $P(x, F(y))$ and $P(G(z), F(A))$.
:::answer
Match the arguments in order: $x$ with $G(z)$ gives $x/G(z)$, and $F(y)$ with $F(A)$ gives $y/A$. The MGU is $\{x/G(z), y/A\}$; $z$ stays unbound.
:::

:::question intermediate
Skolemise $\forall x\, \exists y\, Parent(y, x)$.
:::answer
The existential variable $y$ lies inside the scope of $\forall x$, so it is replaced by a Skolem function of $x$: $\forall x\, Parent(P(x), x)$, which becomes the clause $Parent(P(x), x)$ after dropping the quantifier. $P(x)$ names "the parent of $x$".
:::

:::question advanced
What does it mean that first-order entailment is semidecidable, and what are the consequences for resolution provers?
:::answer
There is an algorithm (such as resolution refutation) that halts with "yes" whenever $KB \models \alpha$, but no algorithm can always halt with "no" when the sentence is not entailed. A resolution prover may therefore run forever on non-theorems, so practical provers use time limits, restricted fragments of logic (such as Horn clauses or description logics), and strategies such as unit preference and set of support to find proofs faster.
:::

## Further learning

- **Next:** *Bayesian Networks & Probabilistic Inference* handles uncertainty, which logic alone cannot.
- **Related:** *Propositional & Predicate Logic* in Discrete Mathematics covers quantifiers and proofs.
