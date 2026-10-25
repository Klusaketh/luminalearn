---
lesson: entity-sets-cardinalities
title: Entity Sets and Cardinality Ratios
summary: Model a domain with the entity-relationship (ER) model - entities, attributes, relationship sets, cardinality ratios, participation, weak entities, and specialization - drawn in Chen and crow's foot notation.
minutes: 45
type: theory
objectives:
  - Identify entity sets, attributes (simple, composite, multivalued, derived), and keys from a description of a domain
  - Determine the cardinality ratio (1:1, 1:N, M:N) and participation (total or partial) of a relationship
  - Recognise weak entity sets and their identifying relationships and partial keys
  - Read and draw ER diagrams in Chen and crow's foot notation, including specialization hierarchies
---

## Introduction

Before creating a single table, a database designer must understand the world the database will describe. What things matter: students, courses, instructors, rooms? What facts about them must be stored? How are they connected, and how many of one can be connected to how many of the other? Getting these answers wrong is expensive, because a badly designed schema leads to redundancy, missing information, and constraints that cannot be enforced.

The **entity-relationship (ER) model**, introduced by Peter Chen in 1976, is the standard tool for this conceptual design. It describes a domain in terms of **entities** (things), their **attributes** (properties), and **relationships** (associations), together with constraints such as how many entities may take part in a relationship. ER diagrams are easy for non-programmers to read, so they serve as a shared language between designers and the people who know the business, and they translate systematically into relational tables. This lesson covers the concepts and notations; the next lesson covers the translation.

**Before you start:** you should know what tables, rows, and keys are.

## Core theory

### Entities and entity sets

An **entity** is a distinguishable object in the domain: the student Asha, the course Databases. An **entity set** is a collection of entities of the same type, such as all students, and is drawn as a rectangle. Each entity set has a **key**: a set of attributes whose values identify each entity uniquely, such as a student ID.

### Attributes

| Kind | Meaning | Example |
| :--- | :--- | :--- |
| Simple | a single, indivisible value | `credits` |
| Composite | made of components | `name` = (first, last); `address` = (street, city, postcode) |
| Single-valued | one value per entity | `date_of_birth` |
| Multivalued | possibly several values per entity | `phone_numbers` |
| Derived | computable from other data | `age`, from `date_of_birth` |

In Chen notation, attributes are ovals; key attributes are underlined, multivalued attributes have double ovals, and derived attributes have dashed ovals.

### Relationship sets and degree

A **relationship** associates entities, for example "Asha **is enrolled in** Databases". A **relationship set** is a set of relationships of the same type, drawn as a diamond. Its **degree** is the number of entity sets involved: **binary** (two, by far the most common), **ternary** (three, such as supplier–part–project), and so on. A relationship can have its own attributes: the `grade` of an enrolment belongs to the pairing of a student and a course, not to either alone. In a **recursive** relationship, the same entity set appears twice in different **roles**, such as an employee who *manages* other employees.

### Cardinality ratios

For a binary relationship between entity sets $A$ and $B$:

| Ratio | Meaning | Example |
| :--- | :--- | :--- |
| 1:1 | each $A$ relates to at most one $B$, and each $B$ to at most one $A$ | a professor heads at most one department, and each department has one head |
| 1:N | each $A$ relates to many $B$s, but each $B$ to at most one $A$ | an instructor advises many students; each student has at most one advisor |
| M:N | each $A$ relates to many $B$s, and each $B$ to many $A$s | students enrol in many courses; courses have many students |

Cardinality is a rule about **every possible** state of the database, decided from the requirements. Sample data can contradict a proposed rule, but it can never prove one.

### Participation

- **Total participation:** every entity of the set must take part in the relationship (drawn as a double line in Chen notation). Every section must belong to a course.
- **Partial participation:** some entities may not take part (a single line). Not every instructor advises students.

Cardinality and participation together are often written as **(min, max)** pairs on each side, such as (0, N) or (1, 1).

### Weak entity sets

A **weak entity set** has no key of its own; its entities are identified only together with an **owner** (identifying) entity. A course section "section 2" means nothing without its course: "Databases, section 2". The weak entity has a **partial key** (discriminator), here the section number, and is connected to its owner by an **identifying relationship**. A weak entity always has total participation in that relationship and is drawn with a double rectangle, with the identifying relationship as a double diamond.

### Specialization and generalization

An entity set can be divided into subclasses that have extra attributes or relationships: `Person` specializes into `Student` and `Employee`. This is an **ISA** hierarchy. Subclasses **inherit** the superclass's attributes and key. Constraints describe the hierarchy:

- **disjoint** (an entity belongs to at most one subclass) or **overlapping** (it may belong to several);
- **total** (every superclass entity belongs to some subclass) or **partial**.

### Notations

Chen notation uses rectangles, diamonds, and ovals. **Crow's foot** (information engineering) notation, used by most design tools, draws relationships as lines and marks each end:

| End symbol | Meaning |
| :--- | :--- |
| a bar (`|`) | exactly one, or at least one |
| a circle (`o`) | zero, so the participation is optional |
| a crow's foot (three prongs) | many |

So "an instructor advises zero or many students, and each student has zero or one advisor" is drawn with `o|` (zero or one) at the instructor end and `o<` (zero or many) at the student end.

## Worked examples

### Example 1: From requirements to an ER design

Requirements for a university:

> Each department has a unique name and a building, and is headed by exactly one professor; a professor heads at most one department. Students have an ID, a name (first and last), one or more phone numbers, and a date of birth. Each student may have one instructor as advisor; an instructor may advise many students. Students enrol in courses, and each enrolment records a grade. Each course has sections numbered 1, 2, 3, and so on within the course.

| Element | Design |
| :--- | :--- |
| Entity sets and keys | Department (`name`), Professor (`id`), Student (`sid`), Course (`course_id`) |
| Composite attribute | Student.`name` = (first, last) |
| Multivalued attribute | Student.`phones` |
| Derived attribute | Student.`age`, from `date_of_birth` |
| Heads: Professor–Department | 1:1; Department participates totally, Professor partially |
| Advises: Instructor–Student | 1:N; both partial |
| Enrolled: Student–Course | M:N, with attribute `grade` on the relationship |
| Weak entity | Section, partial key `number`, owner Course, identifying relationship total |

`grade` sits on the Enrolled relationship because it describes a particular student in a particular course; attached to Student it would allow only one grade per student, and attached to Course only one grade per course.

### Example 2: Checking data against cardinality rules

Data cannot prove a cardinality rule, but it can reveal violations or suggest a ratio. This function reports the most partners any entity has on each side of a relationship instance.

```python
def observed_ratio(pairs):
    partners_of_left, partners_of_right = {}, {}
    for a, b in pairs:
        partners_of_left.setdefault(a, set()).add(b)
        partners_of_right.setdefault(b, set()).add(a)
    left_many = max(len(v) for v in partners_of_left.values()) > 1    # some A has several Bs
    right_many = max(len(v) for v in partners_of_right.values()) > 1  # some B has several As
    return {(False, False): "1:1", (True, False): "1:N",
            (False, True): "N:1", (True, True): "M:N"}[(left_many, right_many)]

advises = [("Smith", "Asha"), ("Smith", "Ben"), ("Lee", "Chen")]
heads = [("Okafor", "Physics"), ("Ruiz", "History")]
enrolled = [("Asha", "DB"), ("Asha", "OS"), ("Ben", "DB"), ("Chen", "OS")]
for name, pairs in [("advises", advises), ("heads", heads), ("enrolled", enrolled)]:
    print(f"{name}: consistent with {observed_ratio(pairs)}")

students = {"Asha", "Ben", "Chen", "Dara"}
advised = {s for _, s in advises}
print("every student has an advisor:", students <= advised, "| missing:", sorted(students - advised))
```

Output:

```text
advises: consistent with 1:N
heads: consistent with 1:1
enrolled: consistent with M:N
every student has an advisor: False | missing: ['Dara']
```

Smith advises two students and each student has one advisor, which fits 1:N. The `heads` data happens to be one-to-one, which agrees with the rule, but if the design said M:N, this small sample could not contradict it either; the requirements decide. Dara has no advisor, so participation of Student in Advises is **partial**, as the requirements said ("may have").

### Example 3: Choosing between an attribute, an entity, and a relationship

| Question | Choice | Reason |
| :--- | :--- | :--- |
| Is a student's phone an attribute or an entity? | multivalued attribute | phones have no attributes or relationships of their own |
| Is "department" an attribute of Instructor or an entity? | entity | departments have their own attributes (building, budget) and relationships (head) |
| Should Enrolled be an entity? | a relationship, or an associative entity if enrolments gain their own relationships | if enrolments later need, say, a related list of assignments, promoting Enrolled to an entity is cleaner |
| Supplier supplies part to project: one ternary or three binary relationships? | usually one ternary | three binary relationships cannot record which supplier supplied which part to which project |

The last row is a classic trap. Knowing that supplier S supplies part P, that S works with project J, and that J uses P does not imply that S supplied P to J.

## Applications

- **Database design projects** start with ER or crow's foot diagrams, reviewed with domain experts before any table is created.
- **Design tools** such as MySQL Workbench, pgModeler, and many diagramming tools draw crow's foot ER models and generate SQL.
- **Object-relational mapping (ORM)** frameworks, such as Django models and Hibernate entities, express one-to-many and many-to-many relationships directly in code.
- **Documentation:** ER diagrams describe existing databases for new team members and auditors.
- **Requirements analysis:** cardinality questions ("can an order have several shipping addresses?") expose ambiguities in business rules early.

## Common mistakes

- **Putting a relationship's attribute on one of the entities,** such as storing `grade` in Student, which cannot represent a student's grades in several courses.
- **Inferring cardinality from sample data.** A rule must come from the requirements; data can only reveal violations.
- **Confusing cardinality with participation.** 1:N says how many partners are allowed at most; total participation says whether at least one is required.
- **Forgetting that a weak entity's identity depends on its owner,** and trying to give it a key that is only unique within the owner.
- **Replacing a ternary relationship with binary ones** and losing the information about which triples actually occurred.

## Revision notes

- Entity set (rectangle) with a key; attributes simple or composite, single- or multivalued, possibly derived.
- Relationship set (diamond); degree binary, ternary, or recursive with roles; relationships may have attributes.
- Cardinality ratios: 1:1, 1:N, M:N; participation: total (at least one) or partial; or (min, max) pairs.
- Weak entity: identified by owner key plus partial key, through a total identifying relationship.
- ISA hierarchies: inheritance; disjoint or overlapping; total or partial.
- Crow's foot: bar = one, circle = zero, crow's foot = many.

## Practice questions

:::question basic
Classify each attribute: a person's full name stored as first and last name; a book's list of authors; an employee's age computed from the date of birth.
:::answer
The full name is a composite attribute, made of the components first name and last name. The list of authors is a multivalued attribute, because one book can have several authors. Age is a derived attribute, because it can be computed from the date of birth and today's date.
:::

:::question basic
What is the cardinality ratio between countries and capital cities, and between authors and books?
:::answer
Country to capital is 1:1 under the usual simplification that each country has one capital and each capital belongs to one country. Author to book is M:N, because an author can write many books and a book can have several authors.
:::

:::question intermediate
A hospital records that each patient is assigned to exactly one ward, a ward can hold many patients, and a ward may be empty. Give the cardinality ratio and the participation of each side.
:::answer
The ratio is 1:N from ward to patient (each patient has one ward; each ward has many patients). Patient participation is total, because every patient must be assigned to a ward. Ward participation is partial, because a ward may have no patients. In (min, max) form: each patient takes part (1, 1) times, and each ward (0, N) times.
:::

:::question intermediate
Why is a hotel room a weak entity if room numbers are reused in each hotel of a chain? What are its partial key and owner?
:::answer
Room number 101 exists in every hotel, so the room number alone does not identify a room in the chain's database. A room can be identified only together with its hotel, so Room is a weak entity, owned by Hotel through an identifying relationship (such as "located in"), with total participation. Its partial key is the room number, and its full identifier is (hotel_id, room_number).
:::

:::question intermediate
An `Employee` entity set is specialized into `Engineer` and `Manager`. What is the difference between a disjoint and an overlapping specialization here, and which seems more realistic?
:::answer
Disjoint means an employee can be at most one of the two, either an engineer or a manager. Overlapping means an employee can be both, such as an engineering manager who still writes code. Overlapping is often more realistic for job roles, while categories such as "full-time" and "part-time" are naturally disjoint.
:::

:::question advanced
Suppliers supply parts to projects. Show why replacing the ternary relationship Supplies(supplier, part, project) by three binary relationships loses information.
:::answer
Suppose the real deliveries are (S1, P1, J2), (S1, P2, J1), and (S2, P1, J1). The three binary relationships then hold the pairs S1–P1, S1–P2, and S2–P1 (supplier–part); S1–J2, S1–J1, and S2–J1 (supplier–project); and P1–J2, P2–J1, and P1–J1 (part–project). Every pair inside the triple (S1, P1, J1) appears: S1 supplies P1, S1 works with J1, and P1 is used in J1. Yet S1 never supplied P1 to J1. The binary relationships cannot tell the real triples apart from such combinations, so a ternary relationship (or an associative entity with three foreign keys) is needed to record exactly which supplier supplied which part to which project.
:::

## Further learning

- **Next:** *ER-to-Relational Mapping* turns ER designs into tables, keys, and foreign keys.
- **Related:** *Database Keys & Referential Integrity Constraints* explains how keys and relationships become constraints.
- **Related:** *Functional Dependencies & Normal Forms* checks a design for redundancy formally.
