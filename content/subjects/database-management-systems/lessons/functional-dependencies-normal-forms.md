---
lesson: functional-dependencies-normal-forms
title: Functional Dependencies and Normal Forms
summary: Use functional dependencies to find keys and diagnose redundancy, apply the normal forms 1NF, 2NF, 3NF, and BCNF, and decompose relations losslessly while weighing dependency preservation.
minutes: 60
type: theory
objectives:
  - Explain update, insertion, and deletion anomalies and trace them to functional dependencies
  - Compute attribute closures with Armstrong's axioms and use them to find candidate keys
  - Test a relation against 1NF, 2NF, 3NF, and BCNF and identify the dependencies that violate each
  - Decompose a relation, test the decomposition for the lossless-join property and dependency preservation, and choose between 3NF and BCNF
---

## Introduction

Suppose a university keeps one big table of enrolments, with columns for the student's ID and name, the course's ID, title, and instructor, and the grade. It looks convenient: every report is one query away. But the student's name is repeated on every one of their enrolments, so changing it means updating many rows (miss one, and the data contradicts itself). A new course cannot be recorded until someone enrols in it. And if the last student drops a course, the course's title and instructor vanish with the row.

These **anomalies** are symptoms of a design that stores facts redundantly. **Normalization** is the systematic cure. It starts from **functional dependencies**, statements such as "a course ID determines its title", and uses them to decide which attributes belong together in a table. This lesson shows how to reason about dependencies, how to compute keys from them, what each normal form requires, and how to split a table without losing information.

**Before you start:** you should know relations, keys, and natural joins.

## Core theory

### Functional dependencies

For attribute sets $X$ and $Y$ of a relation $R$, the **functional dependency** $X \to Y$ holds if any two tuples that agree on $X$ must also agree on $Y$. "$X$ determines $Y$." For example, `course_id → title, instructor` and `student_id, course_id → grade`.

Like keys, FDs are statements about the **meaning** of the data, true in every legal state; a sample can refute an FD but not prove it. A key is a special case: $K$ is a superkey exactly when $K \to R$ (all attributes).

### Armstrong's axioms

From a set of FDs $F$, other FDs follow by three rules, which are **sound** (they derive only valid FDs) and **complete** (they derive every FD that follows from $F$):

1. **Reflexivity:** if $Y \subseteq X$, then $X \to Y$.
2. **Augmentation:** if $X \to Y$, then $XZ \to YZ$.
3. **Transitivity:** if $X \to Y$ and $Y \to Z$, then $X \to Z$.

Useful derived rules: **union** ($X \to Y$ and $X \to Z$ give $X \to YZ$), **decomposition** ($X \to YZ$ gives $X \to Y$), and **pseudotransitivity** ($X \to Y$ and $WY \to Z$ give $WX \to Z$).

### Attribute closure

The **closure** $X^+$ is the set of all attributes determined by $X$. The algorithm: start with $X$; repeatedly, for each FD $A \to B$ whose left side $A$ is already inside the result, add $B$; stop when nothing changes.

Closure answers the key questions directly:

- $X \to Y$ follows from $F$ if and only if $Y \subseteq X^+$.
- $X$ is a superkey if and only if $X^+$ contains every attribute.
- A candidate key is a superkey none of whose proper subsets is a superkey.

A useful shortcut: an attribute that never appears on the right side of any FD must be part of **every** key.

### Anomalies

| Anomaly | Example in the enrolment table |
| :--- | :--- |
| Update | renaming a student requires changing every row of their enrolments |
| Insertion | a new course cannot be stored until a student enrols in it |
| Deletion | deleting the last enrolment in a course loses the course's title and instructor |

### The normal forms

An attribute is **prime** if it belongs to some candidate key.

| Normal form | Requirement | Removes |
| :--- | :--- | :--- |
| 1NF | every attribute value is atomic (no lists or nested tables) | repeating groups |
| 2NF | 1NF, and no non-prime attribute depends on **part** of a candidate key | partial dependencies |
| 3NF | for every non-trivial FD $X \to A$: $X$ is a superkey **or** $A$ is prime | transitive dependencies on non-key attributes |
| BCNF | for every non-trivial FD $X \to A$: $X$ is a superkey | every dependency not implied by a key |

Each form implies the ones above it: $\text{BCNF} \subset \text{3NF} \subset \text{2NF} \subset \text{1NF}$. Informally, in BCNF "every fact is about the key, the whole key, and nothing but the key". Higher forms such as 4NF deal with multivalued dependencies, where an entity has independent lists of values (a person's phone numbers and their languages) that should not be combined in one table.

### Decomposition

A violation is fixed by **decomposing** $R$ into smaller relations. For a BCNF violation $X \to Y$, replace $R$ by $R_1 = X \cup Y$ and $R_2 = R - (Y - X)$, and repeat until every relation is in BCNF. Two properties matter:

- **Lossless join:** joining the pieces gives back exactly $R$, with no **spurious tuples**. A decomposition into $R_1$ and $R_2$ is lossless if and only if their common attributes form a superkey of $R_1$ or of $R_2$, that is, $(R_1 \cap R_2) \to R_1$ or $(R_1 \cap R_2) \to R_2$.
- **Dependency preservation:** every FD can be checked within a single piece, without joining. Otherwise, enforcing that FD requires a join on every update.

**BCNF decomposition is always lossless but may lose dependencies. 3NF synthesis is always lossless and dependency-preserving**, at the price of a little remaining redundancy. That is the practical choice between them: aim for BCNF, and accept 3NF when BCNF would make an important constraint impossible to check cheaply.

### Normalization is not the whole story

Highly normalized schemas need more joins. Analytical databases sometimes **denormalize** deliberately, storing redundant data to speed up reads, but they do so knowingly, with mechanisms to keep the copies consistent.

## Worked examples

### Example 1: Closures, keys, and violations

The functions below compute closures, find candidate keys by testing attribute sets from smallest to largest, and report which FDs break which normal forms.

```python
from itertools import combinations

def closure(attrs, fds):
    result, changed = set(attrs), True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if set(lhs) <= result and not set(rhs) <= result:
                result |= set(rhs)
                changed = True
    return result

def candidate_keys(attributes, fds):
    keys = []
    for size in range(1, len(attributes) + 1):
        for combo in combinations(attributes, size):
            if closure(combo, fds) >= set(attributes) and not any(set(k) <= set(combo) for k in keys):
                keys.append(combo)
    return keys

def check(attributes, fds):
    keys = candidate_keys(attributes, fds)
    prime = {a for k in keys for a in k}
    print("candidate keys:", keys)
    for lhs, rhs in fds:
        extra = set(rhs) - set(lhs)
        if not extra or closure(lhs, fds) >= set(attributes):
            continue                                  # trivial, or the left side is a superkey
        broken = "BCNF only" if extra <= prime else "3NF and BCNF"
        print(f"  {', '.join(lhs)} -> {', '.join(rhs)} violates {broken}")

print(sorted(closure("A", [("A", "B"), ("B", "C"), ("CD", "E")])))

enrolment = ("sid", "sname", "cid", "title", "instructor", "grade")
check(enrolment, [(("sid",), ("sname",)),
                  (("cid",), ("title", "instructor")),
                  (("sid", "cid"), ("grade",))])
```

Output:

```text
['A', 'B', 'C']
candidate keys: [('sid', 'cid')]
  sid -> sname violates 3NF and BCNF
  cid -> title, instructor violates 3NF and BCNF
```

The closure of $\{A\}$ under $A \to B$, $B \to C$, $CD \to E$ is $\{A, B, C\}$: $A$ gives $B$, $B$ gives $C$, but $E$ needs $D$ as well. For the enrolment table, the only candidate key is (sid, cid). Both `sid → sname` and `cid → title, instructor` have left sides that are only **part** of the key, which makes them partial dependencies: the table is not even in 2NF. Decomposing along these dependencies gives `Student(sid, sname)`, `Course(cid, title, instructor)`, and `Enrolment(sid, cid, grade)`, each of which has only key-based dependencies and is in BCNF. The three anomalies disappear: a name is stored once, a course can exist without students, and dropping an enrolment never deletes course details.

### Example 2: In 3NF but not in BCNF

In a tutoring centre, each instructor teaches exactly one course, and for each course a student has one instructor: `(student, course) → instructor` and `instructor → course`.

```python
from itertools import combinations

def closure(attrs, fds):
    result, changed = set(attrs), True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if set(lhs) <= result and not set(rhs) <= result:
                result |= set(rhs)
                changed = True
    return result

R = {"student", "course", "instructor"}
fds = [(("student", "course"), ("instructor",)), (("instructor",), ("course",))]

keys = [set(c) for n in (1, 2) for c in combinations(sorted(R), n) if closure(c, fds) >= R]
print("candidate keys:", [sorted(k) for k in keys])
print("instructor is a superkey:", closure(["instructor"], fds) >= R)

R1, R2 = {"instructor", "course"}, {"student", "instructor"}       # BCNF decomposition
common = R1 & R2
print("lossless:", closure(common, fds) >= R1 or closure(common, fds) >= R2)
preserved = [lhs for lhs, rhs in fds if any(set(lhs) | set(rhs) <= part for part in (R1, R2))]
print("FDs checkable inside one piece:", preserved)
```

Output:

```text
candidate keys: [['course', 'student'], ['instructor', 'student']]
instructor is a superkey: False
lossless: True
FDs checkable inside one piece: [('instructor',)]
```

The FD `instructor → course` violates BCNF, because `instructor` is not a superkey. It does **not** violate 3NF, because `course` is prime: it belongs to the candidate key (student, course). Decomposing into (instructor, course) and (student, instructor) is lossless, since the shared attribute `instructor` determines all of the first piece. But `(student, course) → instructor` no longer fits inside either piece, so the rule "a student has one instructor per course" can be enforced only by joining the two tables on every change. Here, staying in 3NF is a reasonable choice.

### Example 3: A lossy decomposition

Splitting the same relation into (student, course) and (course, instructor) looks harmless, but the shared attribute `course` is not a key of either piece.

```python
rows = {("Asha", "DB", "Smith"), ("Ben", "DB", "Jones")}       # DB has two instructors
r1 = {(s, c) for s, c, _ in rows}                              # (student, course)
r2 = {(c, i) for _, c, i in rows}                              # (course, instructor)
rejoined = {(s, c, i) for s, c in r1 for c2, i in r2 if c == c2}
print(sorted(rejoined))
print("spurious tuples:", sorted(rejoined - rows))
```

Output:

```text
[('Asha', 'DB', 'Jones'), ('Asha', 'DB', 'Smith'), ('Ben', 'DB', 'Jones'), ('Ben', 'DB', 'Smith')]
spurious tuples: [('Asha', 'DB', 'Jones'), ('Ben', 'DB', 'Smith')]
```

Joining the pieces on `course` pairs every DB student with every DB instructor, inventing two enrolments that never existed. The decomposition is **lossy**: the original information, which student has which instructor, cannot be recovered. "Lossy" means the extra tuples, not missing ones, destroy the information. The test from the core theory predicts this: $\{\text{course}\}^+ = \{\text{course}\}$ contains neither piece.

## Applications

- **Schema design:** normalizing to BCNF or 3NF is a standard step between the ER model and the final tables, catching redundancy the diagram missed.
- **Schema review:** listing the FDs of an existing wide table explains its anomalies and guides refactoring.
- **Data quality:** checking whether a supposed FD holds in real data (for example, does every postcode map to one city?) finds dirty records.
- **Query optimization:** optimizers use keys and FDs to remove redundant `DISTINCT`s and joins.
- **Analytics:** data warehouses deliberately denormalize dimension tables for read speed, a choice informed by the same theory.

## Common mistakes

- **Deriving FDs from sample data.** Data can disprove an FD, but only the meaning of the attributes establishes one.
- **Stopping the closure algorithm early.** Keep applying FDs until a full pass adds nothing.
- **Confusing 3NF with BCNF.** 3NF allows $X \to A$ with a non-superkey $X$ when $A$ is prime; BCNF never does.
- **Decomposing without checking losslessness,** which can create spurious tuples on rejoin.
- **Assuming every BCNF decomposition preserves dependencies.** Some cannot; then 3NF may be the better design.
- **Normalizing until queries need many joins** without considering performance; denormalization is sometimes justified, but should be deliberate.

## Revision notes

- FD $X \to Y$: equal $X$ values imply equal $Y$ values; keys are FDs on all attributes.
- Armstrong's axioms: reflexivity, augmentation, transitivity (plus union, decomposition, pseudotransitivity).
- Closure $X^+$: repeatedly add right sides of FDs whose left sides are included. Superkey iff $X^+ = R$.
- 1NF atomic values; 2NF no partial dependencies of non-prime attributes; 3NF: $X$ superkey or $A$ prime; BCNF: $X$ superkey.
- Lossless binary decomposition iff the common attributes determine one of the pieces.
- BCNF: always lossless, may lose dependencies. 3NF synthesis: lossless and dependency-preserving.

## Practice questions

:::question basic
What does the functional dependency `isbn → title, publisher` mean?
:::answer
Any two rows with the same ISBN must have the same title and the same publisher. Knowing the ISBN determines both values; it does not say anything in the other direction (two different books may share a publisher).
:::

:::question basic
Name the three anomalies that redundancy causes and give a one-line example of each.
:::answer
Update anomaly: changing a course's title requires updating every enrolment row that repeats it. Insertion anomaly: a new course cannot be stored until a student enrols in it. Deletion anomaly: deleting the last enrolment in a course removes the only record of the course's title and instructor.
:::

:::question intermediate
Given $R(A, B, C, D)$ with $A \to B$, $B \to C$, and $C \to A$, find all candidate keys.
:::answer
$D$ never appears on a right side, so every key contains $D$. $\{D\}^+ = \{D\}$, so $D$ alone is not a key. $\{A, D\}^+$: $A$ gives $B$, $B$ gives $C$, so it is $\{A, B, C, D\}$, a key. By the cycle $A \to B \to C \to A$, $\{B, D\}^+$ and $\{C, D\}^+$ are also everything. So the candidate keys are $\{A, D\}$, $\{B, D\}$, and $\{C, D\}$.
:::

:::question intermediate
Is $R(A, B, C)$ with $A \to B$ and $B \to C$ in 3NF? If not, decompose it into BCNF.
:::answer
The only key is $\{A\}$ (since $A^+ = \{A, B, C\}$). The FD $B \to C$ has a left side that is not a superkey, and $C$ is not prime, so it violates 3NF (it is a transitive dependency $A \to B \to C$). Decompose on $B \to C$: $R_1(B, C)$ and $R_2(A, B)$. The common attribute $B$ is a key of $R_1$, so the join is lossless; both FDs fit inside one piece each, so dependencies are preserved, and both pieces are in BCNF.
:::

:::question intermediate
Decompose $R(A, B, C)$ into $R_1(A, B)$ and $R_2(B, C)$ given only the FD $A \to C$. Is the decomposition lossless?
:::answer
The common attribute set is $\{B\}$, and $\{B\}^+ = \{B\}$, which contains neither $R_1$ nor $R_2$, so the decomposition is lossy. For example, the rows $(a_1, b, c_1)$ and $(a_2, b, c_2)$ project to $(a_1, b), (a_2, b)$ and $(b, c_1), (b, c_2)$, and rejoining on $b$ adds the spurious rows $(a_1, b, c_2)$ and $(a_2, b, c_1)$. The FD $A \to C$ is also not preserved.
:::

:::question advanced
Explain why BCNF decomposition can fail to preserve dependencies, using Example 2, and describe how a designer can still enforce the lost dependency.
:::answer
In Example 2, the only way to remove the violation `instructor → course` is to split off (instructor, course). The remaining FD `(student, course) → instructor` mentions all three attributes, but no piece of the BCNF decomposition contains all three, so the FD cannot be checked by a key or unique constraint on one table. The designer can keep the 3NF relation instead, or keep the BCNF tables and enforce the rule with a trigger or check that joins them on each insert or update, or store a materialized view of the join with a unique constraint on (student, course). Each option trades redundancy or performance for the constraint.
:::

## Further learning

- **Next:** *ACID Properties & Transaction States* turns from schema design to correct concurrent updates.
- **Related:** *Database Keys & Referential Integrity Constraints* covers the keys that closures identify.
- **Related:** *ER-to-Relational Mapping* produces the schemas that normalization then refines.
