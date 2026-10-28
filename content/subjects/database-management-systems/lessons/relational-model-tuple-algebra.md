---
lesson: relational-data-model-and-tuples
title: Relational Data Model & Tuple Algebra
summary: Relations, tuples, attributes, and domains as Edgar Codd defined them, and the relational algebra operators - selection, projection, product, join, set operations, renaming, and division - that every SQL query is built from.
minutes: 40
type: theory
objectives:
  - Define relation, tuple, attribute, domain, degree, and cardinality, and state the properties of a relation
  - Apply selection, projection, Cartesian product, join, union, difference, intersection, renaming, and division
  - Compose relational algebra expressions to answer queries and translate them to SQL
  - Explain how NULLs and SQL's bag semantics differ from the pure set-based relational model
---

## Introduction

In 1970, Edgar F. Codd, a researcher at IBM, published a paper titled "A Relational Model of Data for Large Shared Data Banks". Its idea was radical for the time: represent all data as simple tables, called **relations**, and let users ask questions in terms of the data's values rather than by navigating pointers between records. A query would say what data is wanted, and the system would work out how to find it.

That idea now underlies nearly every database in commercial use. This lesson defines the vocabulary of the relational model precisely and introduces **relational algebra**, a small set of operations that take relations as input and produce relations as output. Relational algebra matters for two reasons: every SQL query can be expressed in it, and database engines translate SQL into algebra-like plans that they then optimize and execute. Understanding the algebra makes SQL predictable.

**Before you start:** you should know basic set notation (union, intersection, difference) and what a table of data looks like.

## Core theory

### Vocabulary

| Term | Meaning | Table analogy |
| :--- | :--- | :--- |
| Relation | a set of tuples with the same attributes | table |
| Tuple | one element of the relation | row |
| Attribute | a named property, with a domain | column |
| Domain | the set of allowed atomic values for an attribute | column type plus rules |
| Degree (arity) | number of attributes | number of columns |
| Cardinality | number of tuples | number of rows |
| Relation schema | name plus attributes, written $R(A_1, \dots, A_n)$ | table definition |

For example, `Student(sid, name, dept)` has degree 3; if it contains 500 students, its cardinality is 500.

### Properties of a relation

Because a relation is a **set**:

- it contains **no duplicate tuples**;
- its tuples have **no order**;
- its attributes, referenced by name, have no meaningful order;
- each value is **atomic** (a single value from the domain, not a list or a nested table), which is the requirement of **first normal form**.

The relational model also requires that some set of attributes, a **key**, identifies each tuple. **Entity integrity** says that primary-key values may never be NULL, and **referential integrity** says that foreign-key values must match existing key values (or be NULL).

### The operators

Let $R$ and $S$ be relations.

| Operator | Notation | Result |
| :--- | :--- | :--- |
| Selection | $\sigma_{p}(R)$ | tuples of $R$ satisfying predicate $p$ (a horizontal slice) |
| Projection | $\pi_{A, B}(R)$ | only attributes $A$ and $B$, with duplicate tuples removed (a vertical slice) |
| Cartesian product | $R \times S$ | every tuple of $R$ concatenated with every tuple of $S$ |
| Union | $R \cup S$ | tuples in either (schemas must be compatible) |
| Difference | $R - S$ | tuples in $R$ but not in $S$ |
| Renaming | $\rho_{T}(R)$ | the same relation under a new name (or with renamed attributes) |
| Intersection | $R \cap S$ | tuples in both; equals $R - (R - S)$ |
| Theta join | $R \bowtie_{\theta} S$ | $\sigma_{\theta}(R \times S)$ |
| Natural join | $R \bowtie S$ | join on all attributes with the same name, keeping one copy of each |
| Division | $R \div S$ | the values that are paired in $R$ with **every** tuple of $S$ |

Selection, projection, product, union, difference, and renaming form a **complete** set: every other operator can be expressed using them. Union, difference, and intersection need **union-compatible** relations, with the same number of attributes and matching domains.

Because every operator returns a relation, operators **compose** into expressions:

$$\pi_{\text{name}}(\sigma_{\text{course} = \text{'DB'}}(\text{Student} \bowtie \text{Enrolled}))$$

"names of students enrolled in DB". Such an expression can be drawn as a tree, with base relations at the leaves and operators at the internal nodes, which is exactly the shape of a query plan.

### Sizes of results

For relations with $|R|$ and $|S|$ tuples:

- $|\sigma_p(R)| \le |R|$;
- $|\pi_A(R)| \le |R|$ (fewer if duplicates are removed);
- $|R \times S| = |R| \cdot |S|$, and the degree is the sum of the degrees;
- $|R \bowtie S| \le |R| \cdot |S|$.

### From algebra to SQL

| Algebra | SQL |
| :--- | :--- |
| $\sigma_{p}(R)$ | `SELECT * FROM R WHERE p` |
| $\pi_{A,B}(R)$ | `SELECT DISTINCT A, B FROM R` |
| $R \times S$ | `SELECT * FROM R CROSS JOIN S` |
| $R \bowtie_{\theta} S$ | `SELECT * FROM R JOIN S ON θ` |
| $R \cup S$, $R - S$, $R \cap S$ | `UNION`, `EXCEPT`, `INTERSECT` |

Two differences matter. SQL tables are **bags** (multisets): they may contain duplicate rows, and `SELECT` keeps duplicates unless `DISTINCT` is written. And SQL allows **NULL** to represent missing or unknown values, which brings three-valued logic: a comparison with NULL is neither true nor false but *unknown*, and `WHERE` keeps only rows whose condition is true.

## Worked examples

### Example 1: Relational algebra in Python

Relations are modelled as Python sets of tuples, which enforces "no duplicates" automatically. Results are sorted only for printing, since a relation has no order.

```python
from collections import namedtuple

Student = namedtuple("Student", "sid name dept")
Enrolled = namedtuple("Enrolled", "sid course")
students = {Student(1, "Asha", "CS"), Student(2, "Ben", "Math"), Student(3, "Chen", "CS")}
enrolled = {Enrolled(1, "DB"), Enrolled(1, "OS"), Enrolled(3, "DB"), Enrolled(2, "Calculus")}

def select(r, predicate):                    # sigma
    return {t for t in r if predicate(t)}

def project(r, *attributes):                 # pi: a set, so duplicates vanish
    return {tuple(getattr(t, a) for a in attributes) for t in r}

def product(r, s):                           # Cartesian product
    return {a + b for a in r for b in s}

def theta_join(r, s, condition):             # sigma applied to the product
    return {a + b for a in r for b in s if condition(a, b)}

def divide(r, s):                            # R(x, y) / S(y): x values paired with every y in S
    xs = {x for x, _ in r}
    return {(x,) for x in xs if all((x, y) in r for (y,) in s)}

print(sorted(select(students, lambda t: t.dept == "CS")))
print(sorted(project(students, "dept")))
print(len(product(students, enrolled)))
joined = theta_join(students, enrolled, lambda st, en: st.sid == en.sid)
print(sorted((t[1], t[4]) for t in joined))  # project name and course
cs_ids = project(select(students, lambda t: t.dept == "CS"), "sid")
os_ids = project(select(enrolled, lambda t: t.course == "OS"), "sid")
print(sorted(cs_ids - os_ids))               # CS students not taking OS
print(sorted(divide(enrolled, {("DB",), ("OS",)})))
```

Output:

```text
[Student(sid=1, name='Asha', dept='CS'), Student(sid=3, name='Chen', dept='CS')]
[('CS',), ('Math',)]
12
[('Asha', 'DB'), ('Asha', 'OS'), ('Ben', 'Calculus'), ('Chen', 'DB')]
[(3,)]
[(1,)]
```

Projecting `dept` from three students gives only two tuples, because the two CS rows become identical and a set keeps one. The product has $3 \times 4 = 12$ tuples, most of them meaningless pairings; the join keeps only the four whose `sid` values match. The difference finds Chen (sid 3), the only CS student not taking OS. Division answers "which students take **every** course in {DB, OS}?": only Asha.

### Example 2: The same queries in SQL

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE student (sid INTEGER PRIMARY KEY, name TEXT, dept TEXT);
CREATE TABLE enrolled (sid INTEGER REFERENCES student(sid), course TEXT, PRIMARY KEY (sid, course));
INSERT INTO student VALUES (1, 'Asha', 'CS'), (2, 'Ben', 'Math'), (3, 'Chen', 'CS');
INSERT INTO enrolled VALUES (1, 'DB'), (1, 'OS'), (3, 'DB'), (2, 'Calculus');
""")

queries = {
    "projection without DISTINCT": "SELECT dept FROM student ORDER BY dept",
    "projection with DISTINCT": "SELECT DISTINCT dept FROM student ORDER BY dept",
    "join": """SELECT s.name, e.course FROM student AS s JOIN enrolled AS e ON s.sid = e.sid
               ORDER BY s.name, e.course""",
    "difference": """SELECT sid FROM student WHERE dept = 'CS'
                     EXCEPT SELECT sid FROM enrolled WHERE course = 'OS'""",
    "division": """SELECT sid FROM enrolled WHERE course IN ('DB', 'OS')
                   GROUP BY sid HAVING COUNT(DISTINCT course) = 2""",
}
for label, sql in queries.items():
    print(f"{label}: {db.execute(sql).fetchall()}")
```

Output:

```text
projection without DISTINCT: [('CS',), ('CS',), ('Math',)]
projection with DISTINCT: [('CS',), ('Math',)]
join: [('Asha', 'DB'), ('Asha', 'OS'), ('Ben', 'Calculus'), ('Chen', 'DB')]
difference: [(3,)]
division: [(1,)]
```

Without `DISTINCT`, SQL keeps the duplicate `CS` row, because SQL tables are bags; with it, the result matches the algebra. SQL has no division operator, so "enrolled in every listed course" is written by counting: a student who appears with both of the two listed courses is in the result.

### Example 3: Reading an expression tree

The expression $\pi_{\text{name}}(\sigma_{\text{dept}=\text{'CS'}}(\text{Student}) \bowtie \sigma_{\text{course}=\text{'DB'}}(\text{Enrolled}))$ is evaluated bottom-up:

| Step | Operation | Result |
| :--- | :--- | :--- |
| 1 | $\sigma_{\text{dept}=\text{'CS'}}(\text{Student})$ | Asha (1), Chen (3) |
| 2 | $\sigma_{\text{course}=\text{'DB'}}(\text{Enrolled})$ | (1, DB), (3, DB) |
| 3 | natural join on `sid` | (1, Asha, CS, DB), (3, Chen, CS, DB) |
| 4 | $\pi_{\text{name}}$ | Asha, Chen |

An equivalent expression applies the selections **after** the join, giving the same answer. But selecting first shrinks the inputs to the join (2 and 2 tuples instead of 3 and 4), which is cheaper. Query optimizers rely on such algebraic equivalences, such as "push selections down", to choose fast plans.

## Applications

- **Every relational DBMS** (PostgreSQL, MySQL, Oracle, SQL Server, SQLite) parses SQL into an algebra-like tree and optimizes it with algebraic rewrite rules.
- **Data processing frameworks** such as Apache Spark's DataFrame API and pandas offer selection, projection, and join operations modelled on relational algebra.
- **Query optimization** depends on algebraic laws such as the commutativity of joins and the pushing of selections below joins.
- **Database theory and design** use the formal model to reason about keys, normalization, and query equivalence.
- **Teaching and tools:** relational algebra interpreters let students check queries before writing SQL.

## Common mistakes

- **Expecting projection in SQL to remove duplicates.** It does only with `DISTINCT`; the algebra's projection always removes them.
- **Writing a Cartesian product when a join is meant,** for example `FROM R, S` without a join condition, which multiplies the result size.
- **Using union or difference on incompatible relations,** such as relations with different numbers or types of attributes.
- **Assuming tuples or rows have an order.** Without `ORDER BY`, a DBMS may return rows in any order.
- **Treating NULL as a value that equals itself.** In SQL, `NULL = NULL` is unknown, not true; use `IS NULL`.

## Revision notes

- Relation = set of tuples over a fixed set of attributes; degree = number of attributes, cardinality = number of tuples.
- Relations have no duplicate tuples, no row order, and atomic values.
- Basic operators: $\sigma$, $\pi$, $\times$, $\cup$, $-$, $\rho$; derived: $\cap$, joins, $\div$.
- $|R \times S| = |R| \cdot |S|$; a join is a selection on a product.
- Division answers "for all" questions; SQL expresses it with grouping and counting or with `NOT EXISTS`.
- SQL uses bags (keep duplicates unless `DISTINCT`) and NULLs with three-valued logic.

## Practice questions

:::question basic
A relation `Book(isbn, title, author, year)` holds 1200 rows. What are its degree and cardinality?
:::answer
Its degree is 4, the number of attributes (isbn, title, author, year). Its cardinality is 1200, the number of tuples.
:::

:::question basic
What is the difference between selection and projection?
:::answer
Selection, $\sigma_p(R)$, keeps the tuples (rows) that satisfy a condition and keeps all attributes. Projection, $\pi_{A}(R)$, keeps only the listed attributes (columns) of every tuple, removing duplicate tuples that result. Selection reduces cardinality; projection reduces degree.
:::

:::question intermediate
$R$ has 30 tuples and 4 attributes, and $S$ has 20 tuples and 3 attributes. What are the degree and cardinality of $R \times S$? What is the largest possible cardinality of $R \bowtie S$?
:::answer
$R \times S$ has degree $4 + 3 = 7$ and cardinality $30 \times 20 = 600$. A join is a selection applied to the product, so its cardinality is at most 600, reached only if every pair satisfies the join condition.
:::

:::question intermediate
Using `Student(sid, name, dept)` and `Enrolled(sid, course)`, write a relational algebra expression for the names of students who are not enrolled in any course.
:::answer
$\pi_{\text{name}}\big(\text{Student} \bowtie (\pi_{\text{sid}}(\text{Student}) - \pi_{\text{sid}}(\text{Enrolled}))\big)$. The difference gives the sids of students with no enrolment, and the join with `Student` recovers their names. Joining back on `sid` is needed because two students may share a name.
:::

:::question intermediate
Why does the SQL query `SELECT dept FROM student` return more rows than $\pi_{\text{dept}}(\text{Student})$?
:::answer
The relational algebra treats relations as sets, so projection removes duplicate tuples: departments shared by several students appear once. SQL tables are bags, and `SELECT` keeps every row's value, so each department appears once per student. Writing `SELECT DISTINCT dept FROM student` gives the set semantics.
:::

:::question advanced
Express the division $\text{Enrolled} \div \text{Courses}$ (students enrolled in every course listed in `Courses(course)`) using only the basic operators.
:::answer
Let $A = \pi_{\text{sid}}(\text{Enrolled})$, the students to consider. $A \times \text{Courses}$ lists every pairing of such a student with a required course. Subtracting the pairings that actually occur, $(A \times \text{Courses}) - \text{Enrolled}$, leaves the missing ones; projecting gives the students who miss at least one course, $\pi_{\text{sid}}((A \times \text{Courses}) - \text{Enrolled})$. The answer is $A - \pi_{\text{sid}}((A \times \text{Courses}) - \text{Enrolled})$: the students with no missing course.
:::

## Further learning

- **Next:** *Entity Sets & Cardinality Ratios* shows how to design relations from a description of a domain.
- **Related:** *Database Keys & Referential Integrity Constraints* covers the keys that identify tuples and link relations.
- **Related:** *Query Processing & Optimization* shows how algebraic equivalences make queries faster.
