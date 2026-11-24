---
lesson: propositional-logic-inference
title: Propositional Logic & Inference
summary: Knowledge-based agents and propositional logic, syntax and truth-table semantics, entailment, validity and satisfiability, inference by model checking and by resolution, conjunctive normal form, Horn clauses with forward and backward chaining, and SAT solving.
minutes: 50
type: theory
objectives:
  - Evaluate propositional sentences with truth tables and decide entailment, validity, and satisfiability
  - Convert sentences to conjunctive normal form and prove entailment with resolution refutation
  - Apply forward and backward chaining to Horn clauses and explain how SAT solvers such as DPLL scale
review: ai-draft
---
## Introduction

A **knowledge-based agent** keeps a knowledge base (KB) of sentences, adds what it learns with TELL, and asks questions with ASK, deriving answers by logical inference. Propositional logic is the simplest language for this: facts are true or false statements combined with connectives. Despite its simplicity, it underlies hardware verification, planning, configuration, and the SAT solvers that routinely handle millions of variables.

**Before you start:** you should know truth tables and the connectives AND, OR, NOT, and implication.

## Core theory

### Syntax and semantics

**Atomic sentences** are proposition symbols such as $Rain$ or $Study$. **Complex sentences** use the connectives $\neg$ (not), $\land$ (and), $\lor$ (or), $\Rightarrow$ (implies), and $\Leftrightarrow$ (if and only if). A **model** assigns true or false to every symbol, and truth tables define each connective. Note that $P \Rightarrow Q$ is false only when $P$ is true and $Q$ is false.

### Entailment, validity, and satisfiability

- **Entailment:** $KB \models \alpha$ means $\alpha$ is true in **every** model in which $KB$ is true.
- **Valid** (a tautology): true in all models, such as $P \lor \neg P$.
- **Satisfiable:** true in at least one model.
- **Deduction theorem:** $KB \models \alpha$ exactly when $KB \Rightarrow \alpha$ is valid.
- **Refutation:** $KB \models \alpha$ exactly when $KB \land \neg\alpha$ is unsatisfiable.

**Model checking** enumerates all $2^n$ models for $n$ symbols. It is **sound** (only derives entailed sentences) and **complete** (derives every entailed sentence), but exponential.

### Inference rules and equivalences

**Modus Ponens:** from $\alpha \Rightarrow \beta$ and $\alpha$, infer $\beta$. **And-Elimination:** from $\alpha \land \beta$, infer $\alpha$. Useful equivalences include implication elimination ($\alpha \Rightarrow \beta \equiv \neg\alpha \lor \beta$), contraposition ($\alpha \Rightarrow \beta \equiv \neg\beta \Rightarrow \neg\alpha$), and De Morgan's laws.

### Resolution and CNF

The **resolution** rule combines two clauses that contain complementary literals:

$$\frac{A \lor B \qquad \neg B \lor C}{A \lor C}$$

Resolution works on **conjunctive normal form** (CNF): a conjunction of clauses, each a disjunction of literals. To convert: (1) replace $\alpha \Leftrightarrow \beta$ with $(\alpha \Rightarrow \beta) \land (\beta \Rightarrow \alpha)$; (2) replace $\alpha \Rightarrow \beta$ with $\neg\alpha \lor \beta$; (3) move $\neg$ inwards with De Morgan's laws and double negation; (4) distribute $\lor$ over $\land$. To prove $KB \models \alpha$, add $\neg\alpha$ to the clauses and resolve until the **empty clause** appears, a contradiction. Resolution refutation is complete for propositional logic.

### Horn clauses and chaining

A **Horn clause** has at most one positive literal; a **definite clause** has exactly one, so it can be written as a rule $P_1 \land \dots \land P_k \Rightarrow Q$ or a fact $Q$. For definite clauses:

- **Forward chaining** starts from known facts and fires every rule whose premises are all known, adding conclusions until nothing new appears. It is data-driven and runs in time linear in the size of the KB.
- **Backward chaining** starts from the query and works back through rules whose conclusion matches it, proving their premises recursively. It is goal-driven and touches only relevant facts, as in Prolog.

### SAT solving

The **DPLL** algorithm improves on enumeration with early termination (a clause is true as soon as one literal is true), the **pure symbol** heuristic, and **unit propagation** (a clause with one unassigned literal forces it). Modern **CDCL** solvers add clause learning from conflicts and routinely solve industrial problems with millions of variables. **WalkSAT** is a local-search alternative.

## Worked examples

### Example 1: Entailment by model checking, and forward chaining

The KB says: if it rains, the match is cancelled; if the match is cancelled, I study; it rains.

```python
from itertools import product

SYMBOLS = ["Rain", "Cancelled", "Study"]


def implies(a, b):
    return (not a) or b


def kb(m):  # Rain -> Cancelled, Cancelled -> Study, Rain
    return implies(m["Rain"], m["Cancelled"]) and implies(m["Cancelled"], m["Study"]) and m["Rain"]


def entails(kb, query):
    models = [dict(zip(SYMBOLS, values)) for values in product([True, False], repeat=len(SYMBOLS))]
    kb_models = [m for m in models if kb(m)]
    return all(query(m) for m in kb_models), len(kb_models), len(models)


ok, n_kb, n = entails(kb, lambda m: m["Study"])
print(f"KB |= Study ? {ok}  (KB true in {n_kb} of {n} models)")
kb2 = lambda m: implies(m["Rain"], m["Cancelled"]) and implies(m["Cancelled"], m["Study"])  # noqa: E731
ok, n_kb, n = entails(kb2, lambda m: m["Study"])
print(f"without the fact Rain: KB |= Study ? {ok}  (KB true in {n_kb} of {n} models)")
ok, *_ = entails(kb2, lambda m: implies(m["Rain"], m["Study"]))
print(f"but KB still entails Rain -> Study ? {ok}")

# Forward chaining over Horn clauses: (premises, conclusion)
rules = [({"Rain"}, "Cancelled"), ({"Cancelled"}, "Study"), ({"Study", "Coffee"}, "Pass"), ({"Holiday"}, "Travel")]
facts = {"Rain", "Coffee"}
changed = True
while changed:
    changed = False
    for premises, conclusion in rules:
        if premises <= facts and conclusion not in facts:
            facts.add(conclusion)
            print(f"  {' & '.join(sorted(premises))} => {conclusion}")
            changed = True
print("derived facts:", sorted(facts))
```

Output:

```text
KB |= Study ? True  (KB true in 1 of 8 models)
without the fact Rain: KB |= Study ? False  (KB true in 4 of 8 models)
but KB still entails Rain -> Study ? True
  Rain => Cancelled
  Cancelled => Study
  Coffee & Study => Pass
derived facts: ['Cancelled', 'Coffee', 'Pass', 'Rain', 'Study']
```

With all three sentences, only one of the 8 models satisfies the KB, and Study is true in it, so $KB \models Study$. Without the fact $Rain$, the KB holds in 4 models, including ones where Study is false, so Study is no longer entailed; yet $Rain \Rightarrow Study$ still is, since it is true in every remaining model. Forward chaining reaches the same conclusion by firing rules, and the rule for Travel never fires because Holiday is not known.

### Example 2: A resolution proof

Prove $Study$ from $Rain \Rightarrow Cancelled$, $Cancelled \Rightarrow Study$, and $Rain$.

Convert to CNF clauses: (1) $\neg Rain \lor Cancelled$; (2) $\neg Cancelled \lor Study$; (3) $Rain$. Add the negated goal: (4) $\neg Study$.

1. Resolve (2) with (4) on $Study$: (5) $\neg Cancelled$.
2. Resolve (1) with (5) on $Cancelled$: (6) $\neg Rain$.
3. Resolve (6) with (3) on $Rain$: the **empty clause**.

The KB together with $\neg Study$ is contradictory, so $KB \models Study$. As a CNF conversion exercise, $A \Leftrightarrow B$ becomes $(\neg A \lor B) \land (\neg B \lor A)$.

## Applications

- **Hardware and software verification:** SAT and SMT solvers check circuits and programs.
- **Planning and scheduling:** problems are encoded as satisfiability instances (SATPlan).
- **Configuration:** product configurators enforce compatibility rules.
- **Expert systems and rule engines:** forward and backward chaining over business rules.
- **Puzzle solving:** Sudoku and logic puzzles reduce to SAT.

## Common mistakes

- **Misreading implication.** $P \Rightarrow Q$ is true whenever $P$ is false.
- **Confusing entailment with satisfiability.** Entailment needs truth in every model of the KB, not just one.
- **Distributing in the wrong direction.** CNF distributes $\lor$ over $\land$.
- **Forgetting to negate the goal in resolution.** Refutation proves $\alpha$ by deriving a contradiction from $KB \land \neg\alpha$.
- **Using forward chaining on non-Horn clauses.** It is complete only for definite clauses.

## Revision notes

- Model: truth assignment; $KB \models \alpha$ if $\alpha$ holds in every model of $KB$.
- Valid = true in all models; satisfiable = true in some model.
- Model checking: sound, complete, $O(2^n)$.
- CNF: eliminate $\Leftrightarrow$ and $\Rightarrow$, push $\neg$ inwards, distribute $\lor$ over $\land$.
- Resolution refutation: add $\neg\alpha$, derive the empty clause; complete.
- Horn clauses: forward chaining (data-driven, linear) and backward chaining (goal-driven).

## Practice questions

:::question basic
When is $P \Rightarrow Q$ false?
:::answer
Only when $P$ is true and $Q$ is false. In the other three rows of the truth table it is true.
:::

:::question basic
Is $P \lor \neg P$ valid, satisfiable, or both?
:::answer
Both. It is true in every model, so it is valid, and every valid sentence is also satisfiable.
:::

:::question intermediate
Convert $\neg(P \land Q) \Rightarrow R$ to CNF.
:::answer
Eliminate the implication: $\neg\neg(P \land Q) \lor R$, which simplifies to $(P \land Q) \lor R$. Distribute $\lor$ over $\land$: $(P \lor R) \land (Q \lor R)$.
:::

:::question intermediate
Given the facts $A$ and $B$ and the rules $A \land B \Rightarrow C$, $C \Rightarrow D$, and $E \Rightarrow F$, which facts does forward chaining derive?
:::answer
From $A$ and $B$ it derives $C$, then from $C$ it derives $D$. The rule $E \Rightarrow F$ never fires because $E$ is not known. The final set is $\{A, B, C, D\}$.
:::

:::question advanced
Why does truth-table model checking not scale, and how does DPLL do better?
:::answer
It enumerates $2^n$ models: with 100 symbols that is about $1.27 \times 10^{30}$ models, far beyond any computer. DPLL searches over partial assignments and prunes: it stops exploring a branch as soon as a clause is false, assigns pure symbols immediately, and uses unit propagation to force values. Modern CDCL solvers also learn new clauses from conflicts, so they rarely make the same mistake twice and can handle millions of variables in practice.
:::

## Further learning

- **Next:** *First-Order Logic & Resolution* adds objects, relations, and quantifiers.
- **Related:** *Propositional & Predicate Logic* in Discrete Mathematics covers the mathematical foundations.
