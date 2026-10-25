---
lesson: er-to-relational-mapping
title: ER-to-Relational Mapping
summary: Convert an entity-relationship design into tables step by step - strong and weak entities, composite and multivalued attributes, 1:1, 1:N, and M:N relationships, n-ary relationships, and specialization hierarchies - with the keys and foreign keys that enforce it.
minutes: 45
type: theory
objectives:
  - Map strong entity sets, composite and derived attributes, and weak entity sets to tables with correct primary keys
  - Map 1:1, 1:N, and M:N relationships using foreign keys or junction tables, and place relationship attributes correctly
  - Map multivalued attributes, n-ary relationships, and specialization hierarchies, comparing the alternatives
  - Verify that the resulting schema enforces the design's cardinality constraints
---

## Introduction

An ER diagram describes a domain conceptually; a relational database stores only tables. The step between them, **mapping** the ER design to a relational schema, is mostly mechanical, which is good news: a careful designer can apply a fixed sequence of rules and obtain a schema whose keys and foreign keys enforce much of what the diagram says.

The rules are worth knowing well even when a tool generates the tables, because the choices they encode (where a foreign key goes, when a separate table is needed, which constraints to declare) decide whether the database can hold contradictory or duplicated data. This lesson walks through the standard mapping rules and applies them to a small university design, then checks with real SQL that the schema enforces the intended constraints.

**Before you start:** you should know ER concepts (entity sets, attributes, cardinality ratios, participation, weak entities) and primary and foreign keys.

## Core theory

### Step 1: strong entity sets

Each strong entity set becomes a table. Its simple attributes become columns, and its key becomes the **primary key**.

- **Composite attributes** are flattened into their components: `name(first, last)` becomes columns `first_name` and `last_name`.
- **Derived attributes** are usually **not stored**: `age` is computed from `date_of_birth` in queries or a view, so it can never go stale.

### Step 2: weak entity sets

Each weak entity set becomes a table containing its own attributes plus the **primary key of its owner** as a foreign key. Its primary key is the **owner's key plus the partial key**. Because a weak entity cannot exist without its owner, the foreign key is usually declared `ON DELETE CASCADE`.

### Step 3: binary 1:1 relationships

Add a foreign key to one of the two tables, referencing the other, and declare it `UNIQUE` so that each value appears at most once. Put it on the side with **total participation**, where it can also be `NOT NULL`: every department has a head, so `department.head_id NOT NULL UNIQUE REFERENCES professor(id)`. (If both sides are total and the entities are always created together, merging them into one table is another option.)

### Step 4: binary 1:N relationships

Add a foreign key to the table on the **N side**, referencing the 1 side: each student has at most one advisor, so `student.advisor_id REFERENCES professor(id)`. The relationship's attributes, if any, go in the same table. Total participation of the N side becomes `NOT NULL`.

### Step 5: binary M:N relationships

Create a **junction table** (also called an associative, bridge, or link table) containing the primary keys of both entity sets as foreign keys, plus the relationship's attributes. Its primary key is the combination of the two foreign keys, so each pairing is recorded at most once: `enrolled(sid, course_id, grade)` with primary key `(sid, course_id)`. An M:N relationship can never be represented by a foreign key in one of the entity tables, because each row would need many values.

### Step 6: multivalued attributes

Create a separate table holding the owner's key and the attribute, with both together as the primary key: `student_phone(sid, phone)`. Storing several phones in one column, as a comma-separated string, would break first normal form and make searching and updating error-prone.

### Step 7: n-ary relationships

Create a table with a foreign key to each participating entity set, plus the relationship's attributes. The primary key is usually the combination of all the foreign keys; but if one participant's side has cardinality 1 given the others, the key can be smaller.

### Step 8: specialization and generalization

For a superclass `Person` with subclasses `Student` and `Employee`, there are three common options:

| Option | Tables | Strengths | Weaknesses |
| :--- | :--- | :--- | :--- |
| One table per class | `person`, `student(id → person)`, `employee(id → person)` | no redundancy; supports overlapping subclasses | queries on a subclass need a join |
| One table per subclass only | `student(...all person columns...)`, `employee(...)` | no joins for subclass queries | only for total, disjoint hierarchies; "all persons" needs a union |
| One single table | `person` with a `type` column and all subclass columns | simple, fast | many NULLs; subclass constraints harder to declare |

### What the mapping does not capture

Some ER constraints have no direct relational equivalent. **Total participation on the 1 side** of a 1:N relationship (every instructor must advise at least one student) cannot be expressed by a foreign key, because the foreign key lives in the other table. Such rules need triggers, assertions, or application checks.

## Worked examples

### Example 1: The university design as tables

The design: Professor and Department with a 1:1 Heads relationship (total for Department); Student with a composite name, a multivalued phone attribute, and a derived age; a 1:N Advises relationship from Professor to Student; Course with weak entity Section; and an M:N Enrolled relationship with a grade.

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript("""
CREATE TABLE professor (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE department (                         -- 1:1 Heads, total on the department side
    name TEXT PRIMARY KEY,
    building TEXT,
    head_id INTEGER NOT NULL UNIQUE REFERENCES professor(id)
);
CREATE TABLE student (                            -- composite name flattened; age is derived
    sid INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT,
    advisor_id INTEGER REFERENCES professor(id)   -- 1:N Advises: foreign key on the N side
);
CREATE TABLE student_phone (                      -- multivalued attribute
    sid INTEGER REFERENCES student(sid) ON DELETE CASCADE,
    phone TEXT,
    PRIMARY KEY (sid, phone)
);
CREATE TABLE course (course_id TEXT PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE section (                            -- weak entity: owner's key + partial key
    course_id TEXT REFERENCES course(course_id) ON DELETE CASCADE,
    number INTEGER,
    room TEXT,
    PRIMARY KEY (course_id, number)
);
CREATE TABLE enrolled (                           -- M:N relationship with its own attribute
    sid INTEGER REFERENCES student(sid),
    course_id TEXT REFERENCES course(course_id),
    grade TEXT,
    PRIMARY KEY (sid, course_id)
);
INSERT INTO professor VALUES (1, 'Okafor'), (2, 'Ruiz');
INSERT INTO department VALUES ('Physics', 'North Hall', 1);
INSERT INTO student VALUES (10, 'Asha', 'Rao', '2004-03-14', 1), (11, 'Ben', 'Cole', '2003-11-02', 1),
                           (12, 'Chen', 'Wu', '2004-07-30', NULL);
INSERT INTO student_phone VALUES (10, '555-0101'), (10, '555-0199'), (11, '555-0102');
INSERT INTO course VALUES ('DB', 'Databases'), ('OS', 'Operating Systems');
INSERT INTO section VALUES ('DB', 1, 'R101'), ('DB', 2, 'R102'), ('OS', 1, 'R201');
INSERT INTO enrolled VALUES (10, 'DB', 'A'), (10, 'OS', 'B'), (11, 'DB', 'A'), (12, 'OS', NULL);
""")

print(db.execute("""SELECT s.first_name, e.course_id, e.grade
                    FROM student AS s JOIN enrolled AS e ON e.sid = s.sid
                    ORDER BY s.sid, e.course_id""").fetchall())
print(db.execute("""SELECT s.first_name, COUNT(p.phone)
                    FROM student AS s LEFT JOIN student_phone AS p ON p.sid = s.sid
                    GROUP BY s.sid ORDER BY s.sid""").fetchall())
```

Output:

```text
[('Asha', 'DB', 'A'), ('Asha', 'OS', 'B'), ('Ben', 'DB', 'A'), ('Chen', 'OS', None)]
[('Asha', 2), ('Ben', 1), ('Chen', 0)]
```

The M:N relationship lives entirely in `enrolled`: Asha appears twice there, once per course, and DB appears twice, once per student. The multivalued phone attribute became `student_phone`, so Asha's two numbers are two rows, and Chen, with none, has zero rows (the left join keeps Chen with a count of 0). Chen's NULL `advisor_id` shows that participation in Advises is partial.

### Example 2: Does the schema enforce the design?

Continuing with the same database, three insertions that break the design's rules, and a deletion of an owner entity:

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript("""
CREATE TABLE professor (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE department (name TEXT PRIMARY KEY, building TEXT,
                         head_id INTEGER NOT NULL UNIQUE REFERENCES professor(id));
CREATE TABLE student (sid INTEGER PRIMARY KEY, first_name TEXT NOT NULL);
CREATE TABLE course (course_id TEXT PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE section (course_id TEXT REFERENCES course(course_id) ON DELETE CASCADE,
                      number INTEGER, room TEXT, PRIMARY KEY (course_id, number));
CREATE TABLE enrolled (sid INTEGER REFERENCES student(sid),
                       course_id TEXT REFERENCES course(course_id),
                       grade TEXT, PRIMARY KEY (sid, course_id));
INSERT INTO professor VALUES (1, 'Okafor'), (2, 'Ruiz');
INSERT INTO department VALUES ('Physics', 'North Hall', 1);
INSERT INTO student VALUES (10, 'Asha');
INSERT INTO course VALUES ('DB', 'Databases'), ('OS', 'Operating Systems');
INSERT INTO section VALUES ('DB', 1, 'R101'), ('DB', 2, 'R102'), ('OS', 1, 'R201');
INSERT INTO enrolled VALUES (10, 'DB', 'A');
""")

for sql in ["INSERT INTO enrolled VALUES (10, 'DB', 'C')",                  # same pair twice
            "INSERT INTO department VALUES ('History', 'South Hall', 1)",   # professor heads two
            "INSERT INTO section VALUES ('AI', 1, 'R301')"]:                # section of no course
    try:
        db.execute(sql)
    except sqlite3.IntegrityError as error:
        print("rejected:", error)

db.execute("DELETE FROM enrolled WHERE course_id = 'DB'")
db.execute("DELETE FROM course WHERE course_id = 'DB'")                    # owner deleted
print("sections left:", db.execute("SELECT course_id, number FROM section").fetchall())
```

Output:

```text
rejected: UNIQUE constraint failed: enrolled.sid, enrolled.course_id
rejected: UNIQUE constraint failed: department.head_id
rejected: FOREIGN KEY constraint failed
sections left: [('OS', 1)]
```

The composite primary key of the junction table stops the same student being enrolled in the same course twice. The `UNIQUE` foreign key makes Heads one-to-one: professor 1 cannot head a second department. The weak entity's foreign key forbids a section of a nonexistent course, and `ON DELETE CASCADE` removes both DB sections when the course is deleted. (The enrolments were deleted first because `enrolled` has no cascade rule, so the database would otherwise refuse to delete a course that students are enrolled in.)

### Example 3: Mapping a specialization

`Person(id, name)` is specialized into `Student(gpa)` and `Employee(salary)`, overlapping (a teaching assistant is both) and partial (visitors are neither).

| Option | Works here? | Reason |
| :--- | :--- | :--- |
| Table per class: `person`, `student(id, gpa)`, `employee(id, salary)` | yes | a teaching assistant has rows in both subclass tables; visitors only in `person` |
| Table per subclass only | no | visitors would have no table, and a teaching assistant's name would be stored twice |
| Single table `person(id, name, gpa, salary)` | yes, with NULLs | simple, but `gpa` and `salary` are NULL for many rows, and "every student has a gpa" is harder to declare |

The table-per-class option is the safest default for an overlapping, partial hierarchy; the single-table option is popular in ORMs because it needs no joins.

## Applications

- **Application development:** ORMs such as Django, Rails' Active Record, and Hibernate generate exactly these structures: foreign keys for one-to-many, junction tables for many-to-many.
- **Design tools** forward-engineer ER diagrams into `CREATE TABLE` scripts using these rules.
- **Data migration:** moving data from spreadsheets with comma-separated lists into proper multivalued-attribute tables.
- **Reporting:** junction tables with attributes (enrolments with grades, order lines with quantities) are among the most-queried tables in practice.
- **Data warehousing:** dimension and fact tables follow the same key and relationship structure.

## Common mistakes

- **Putting the foreign key on the 1 side of a 1:N relationship,** which forces a list of values into one column.
- **Representing M:N with foreign keys in the entity tables** instead of a junction table.
- **Forgetting the composite primary key on a junction table,** which allows the same pair to be recorded twice.
- **Giving a weak entity a key that ignores its owner,** for example making `section.number` the primary key, which allows only one section 1 in the whole university.
- **Storing derived attributes such as age,** which become wrong as time passes.
- **Storing multivalued attributes as delimited strings,** which cannot be indexed, validated, or joined properly.

## Revision notes

- Strong entity → table with primary key; flatten composites; do not store derived attributes.
- Weak entity → table with owner's key + partial key as the primary key; foreign key to the owner, usually cascading.
- 1:1 → foreign key with `UNIQUE`, preferably on the total-participation side.
- 1:N → foreign key on the N side, plus relationship attributes.
- M:N → junction table with both keys as a composite primary key, plus relationship attributes.
- Multivalued attribute → separate table (owner key, value). n-ary → table with all participants' keys.
- ISA: table per class, table per subclass, or single table; choose by overlap, totality, and query patterns.

## Practice questions

:::question basic
How is an M:N relationship between `Author` and `Book` represented in a relational schema?
:::answer
With a junction table, for example `book_author(author_id, isbn)`, in which `author_id` references `author` and `isbn` references `book`. The primary key is the pair `(author_id, isbn)`, so each author–book pairing appears once. Attributes of the relationship, such as the author's position in the author list, also go in this table.
:::

:::question basic
Where does the foreign key go for the 1:N relationship "a customer places many orders"?
:::answer
In the `orders` table, the N side: `orders.customer_id REFERENCES customer(id)`. Each order row stores exactly one customer, while a customer can be referenced by any number of orders. Putting order ids in the customer table would require a list in a single column.
:::

:::question intermediate
A `Room` is a weak entity owned by `Building`, with partial key `room_no`. Write the `CREATE TABLE` statement for `room` with columns for capacity, and explain each key choice.
:::answer
```sql
CREATE TABLE room (
    building_id INTEGER REFERENCES building(id) ON DELETE CASCADE,
    room_no TEXT,
    capacity INTEGER,
    PRIMARY KEY (building_id, room_no)
);
```
`building_id` is the owner's key, included as a foreign key because a room cannot be identified without its building. The primary key combines it with the partial key `room_no`, so room 101 can exist in many buildings but only once per building. `ON DELETE CASCADE` reflects existence dependence: if a building is removed, its rooms go too.
:::

:::question intermediate
An employee manages at most one department, and every department has exactly one manager. Where should the foreign key go, and what constraints should it have?
:::answer
In the `department` table: `manager_id INTEGER NOT NULL UNIQUE REFERENCES employee(id)`. Department participation is total, so the column can be `NOT NULL` and every department must name a manager. `UNIQUE` ensures no employee manages two departments, making the relationship 1:1. Placing the foreign key in `employee` instead would need a nullable column, because most employees manage nothing.
:::

:::question intermediate
Why should a multivalued attribute such as a list of email addresses not be stored in a single text column?
:::answer
A single column holding "a@x.com, b@y.com" violates first normal form. The database cannot enforce that each address is valid or unique, cannot index individual addresses for lookups such as "which person has this email?", and every update means rewriting and re-parsing a string, which invites errors. A separate table with one row per (person, email) pair solves all of these.
:::

:::question advanced
The ER design says every instructor must advise at least one student. Can the mapped schema enforce this with keys and foreign keys alone? If not, how could it be enforced?
:::answer
No. The Advises relationship is mapped as a foreign key in `student`, which can ensure that each student's advisor exists, but no declaration on `professor` can require that some student row refer to each professor. Requiring a row to exist in another table is not a key or foreign-key constraint. It can be enforced with triggers that reject inserting a professor without an advisee and reject deleting or reassigning a professor's last advisee, with an SQL assertion in systems that support them, or with checks in the application, ideally inside transactions so that a professor and their first advisee are created together.
:::

## Further learning

- **Next:** *Database Keys & Referential Integrity Constraints* examines key types and foreign-key actions in detail.
- **Related:** *Entity Sets & Cardinality Ratios* covers the ER concepts mapped here.
- **Related:** *Inner, Outer & Self Joins* shows how to query across the tables this mapping creates.
