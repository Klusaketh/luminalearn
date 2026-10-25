---
lesson: declarative-sql-queries-filtering-grouping
title: Declarative SQL Queries, Filtering, and Grouping
summary: Write SELECT queries that filter, sort, and summarise data; understand the logical order in which SQL evaluates its clauses, how NULL and three-valued logic behave, and the difference between WHERE and HAVING.
minutes: 60
type: theory
objectives:
  - Contrast declarative SQL with procedural code and trace the logical evaluation order of a SELECT statement
  - Filter rows with comparison, BETWEEN, IN, LIKE, and IS NULL, and sort and limit results
  - Explain three-valued logic and how NULLs affect comparisons and aggregate functions
  - Summarise data with GROUP BY and aggregates, and distinguish row filtering with WHERE from group filtering with HAVING
---

## Introduction

SQL (Structured Query Language) is how people and programs ask relational databases questions. It was developed at IBM in the 1970s, standardised by ANSI and ISO from 1986 onwards, and is now supported, with small dialect differences, by virtually every relational DBMS.

SQL is **declarative**: a query describes the result wanted, not the steps to compute it. "The names and salaries of engineers earning over 90,000, highest first" becomes a single statement, and the database decides whether to scan the table or use an index, and in what order to do the work. This lesson covers the core of everyday SQL: selecting columns, filtering rows, sorting, handling missing values correctly, and summarising data with groups and aggregates. Every query runs against one small table, so you can check each result by hand.

**Before you start:** you should know the relational model, tables, and keys.

## Core theory

### The shape of a query

```sql
SELECT   [DISTINCT] columns or expressions
FROM     tables
WHERE    row condition
GROUP BY grouping columns
HAVING   group condition
ORDER BY sort keys
LIMIT    n
```

Only `SELECT` and (in practice) `FROM` are required. Although the clauses are **written** in this order, they are **logically evaluated** in a different one:

| Step | Clause | What it does |
| :---: | :--- | :--- |
| 1 | `FROM` | identify the input rows (combining tables if several are listed) |
| 2 | `WHERE` | keep only rows whose condition is true |
| 3 | `GROUP BY` | partition the remaining rows into groups |
| 4 | `HAVING` | keep only groups whose condition is true |
| 5 | `SELECT` | compute the output columns and expressions |
| 6 | `DISTINCT` | remove duplicate output rows |
| 7 | `ORDER BY` | sort the result |
| 8 | `LIMIT` | keep the first $n$ rows |

This order explains several rules. `WHERE` cannot use aggregate functions, because groups do not exist yet at step 2. In standard SQL, a column alias defined in `SELECT` cannot be used in `WHERE` (step 2 comes before step 5) but can be used in `ORDER BY` (step 7). (SQLite and some other systems relax the alias rule as an extension.) The database may physically execute the query in any way that produces the same result.

### Filtering rows

| Operator | Example | Meaning |
| :--- | :--- | :--- |
| comparison | `salary > 90000` | `=`, `<>` (or `!=`), `<`, `<=`, `>`, `>=` |
| logical | `dept = 'Sales' AND city = 'Leeds'` | `AND`, `OR`, `NOT`, with parentheses for clarity |
| range | `salary BETWEEN 50000 AND 70000` | inclusive at both ends |
| set membership | `city IN ('Leeds', 'Austin')` | equal to any listed value |
| pattern | `name LIKE 'A%'` | `%` matches any sequence of characters, `_` exactly one |
| missing value | `bonus IS NULL`, `bonus IS NOT NULL` | the only correct way to test for NULL |

Case sensitivity of `LIKE` and string comparison varies between systems; SQLite's `LIKE` ignores case for ASCII letters by default, while PostgreSQL's is case-sensitive.

### NULL and three-valued logic

`NULL` marks a missing or unknown value. Any comparison involving NULL, such as `bonus > 2000` or even `bonus = NULL`, evaluates to **unknown**, not true or false. Logic then has three values:

| `p` | `q` | `p AND q` | `p OR q` | `NOT p` |
| :--- | :--- | :--- | :--- | :--- |
| true | unknown | unknown | true | false |
| false | unknown | false | unknown | true |
| unknown | unknown | unknown | unknown | unknown |

`WHERE` keeps a row only if its condition is **true**; unknown is treated like false. As a result, a row with a NULL bonus satisfies neither `bonus > 2000` nor `NOT (bonus > 2000)`.

Aggregates **ignore NULLs**: `COUNT(bonus)` counts non-NULL bonuses, `AVG(bonus)` averages only them, and `SUM` of no values is NULL. `COUNT(*)` counts rows, whatever they contain. `COALESCE(bonus, 0)` replaces NULL with a default.

### Grouping and aggregation

`GROUP BY` partitions rows into groups that share the values of the grouping columns, and aggregates compute one value per group: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. In a grouped query, every column in `SELECT` must either be a grouping column or appear inside an aggregate; otherwise, the value would be ambiguous (which employee's name represents the Sales department?). Standard SQL rejects such queries, although some systems, including SQLite and older MySQL modes, accept them and return an arbitrary row's value.

### WHERE versus HAVING

- `WHERE` filters **individual rows before grouping**. It decides which rows feed the aggregates.
- `HAVING` filters **whole groups after aggregation**. It can test aggregate values.

Putting a row condition in `WHERE` rather than `HAVING` is also usually faster, because fewer rows reach the grouping step.

## Worked examples

All examples use this table:

| id | name | dept | salary | bonus | city |
| :---: | :--- | :--- | ---: | ---: | :--- |
| 1 | Asha | Engineering | 95000 | 5000 | Pune |
| 2 | Ben | Sales | 60000 | NULL | Leeds |
| 3 | Chen | Engineering | 88000 | 3000 | Pune |
| 4 | Dara | Support | 52000 | NULL | Leeds |
| 5 | Eli | Sales | 65000 | 4000 | Austin |
| 6 | Fay | Engineering | 102000 | NULL | Austin |
| 7 | Gus | Support | 48000 | 1000 | Pune |

### Example 1: Filtering, sorting, and limiting

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER, bonus INTEGER, city TEXT);
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', 95000, 5000, 'Pune'), (2, 'Ben', 'Sales', 60000, NULL, 'Leeds'),
  (3, 'Chen', 'Engineering', 88000, 3000, 'Pune'), (4, 'Dara', 'Support', 52000, NULL, 'Leeds'),
  (5, 'Eli', 'Sales', 65000, 4000, 'Austin'), (6, 'Fay', 'Engineering', 102000, NULL, 'Austin'),
  (7, 'Gus', 'Support', 48000, 1000, 'Pune');
""")

queries = [
    "SELECT name, salary FROM employees WHERE dept = 'Engineering' AND salary > 90000 ORDER BY salary DESC",
    "SELECT name, city FROM employees WHERE city IN ('Leeds', 'Austin') AND salary BETWEEN 50000 AND 70000 ORDER BY name",
    "SELECT name FROM employees WHERE name LIKE '%a%' ORDER BY name",
    "SELECT DISTINCT city FROM employees ORDER BY city",
    "SELECT name, salary + COALESCE(bonus, 0) AS total FROM employees ORDER BY total DESC LIMIT 3",
]
for sql in queries:
    print(db.execute(sql).fetchall())
```

Output:

```text
[('Fay', 102000), ('Asha', 95000)]
[('Ben', 'Leeds'), ('Dara', 'Leeds'), ('Eli', 'Austin')]
[('Asha',), ('Dara',), ('Fay',)]
[('Austin',), ('Leeds',), ('Pune',)]
[('Fay', 102000), ('Asha', 100000), ('Chen', 91000)]
```

In the second query, Fay works in Austin but is excluded because her salary of 102,000 is outside the range; `BETWEEN` includes both ends, so a salary of exactly 70,000 would qualify. The `LIKE '%a%'` pattern matches Asha's capital A because SQLite's `LIKE` ignores ASCII case. `DISTINCT` turns seven city values into three. The last query computes total pay, treating a missing bonus as 0, and sorts by the alias `total`, which is allowed in `ORDER BY` because it is evaluated after `SELECT`.

### Example 2: NULLs and aggregates

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER, bonus INTEGER, city TEXT);
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', 95000, 5000, 'Pune'), (2, 'Ben', 'Sales', 60000, NULL, 'Leeds'),
  (3, 'Chen', 'Engineering', 88000, 3000, 'Pune'), (4, 'Dara', 'Support', 52000, NULL, 'Leeds'),
  (5, 'Eli', 'Sales', 65000, 4000, 'Austin'), (6, 'Fay', 'Engineering', 102000, NULL, 'Austin'),
  (7, 'Gus', 'Support', 48000, 1000, 'Pune');
""")

for label, sql in [
    ("aggregates", "SELECT COUNT(*), COUNT(bonus), SUM(bonus), AVG(bonus) FROM employees"),
    ("bonus = NULL", "SELECT name FROM employees WHERE bonus = NULL"),
    ("bonus IS NULL", "SELECT name FROM employees WHERE bonus IS NULL ORDER BY name"),
    ("bonus > 2000", "SELECT name FROM employees WHERE bonus > 2000 ORDER BY name"),
    ("NOT (bonus > 2000)", "SELECT name FROM employees WHERE NOT (bonus > 2000) ORDER BY name"),
]:
    print(f"{label}: {db.execute(sql).fetchall()}")
```

Output:

```text
aggregates: [(7, 4, 13000, 3250.0)]
bonus = NULL: []
bonus IS NULL: [('Ben',), ('Dara',), ('Fay',)]
bonus > 2000: [('Asha',), ('Chen',), ('Eli',)]
NOT (bonus > 2000): [('Gus',)]
```

There are 7 rows but only 4 known bonuses, and `AVG(bonus)` is $13000 / 4 = 3250$, not $13000 / 7$: the NULLs are ignored, not treated as zero. `bonus = NULL` matches nothing, not even the rows whose bonus is missing, because the comparison is unknown; `IS NULL` is the correct test. The last two queries split the rows into those with a bonus over 2000 and those with a bonus of at most 2000, yet together they return only 4 of the 7 employees: the three with unknown bonuses satisfy neither condition.

### Example 3: Grouping, WHERE, and HAVING

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER, bonus INTEGER, city TEXT);
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', 95000, 5000, 'Pune'), (2, 'Ben', 'Sales', 60000, NULL, 'Leeds'),
  (3, 'Chen', 'Engineering', 88000, 3000, 'Pune'), (4, 'Dara', 'Support', 52000, NULL, 'Leeds'),
  (5, 'Eli', 'Sales', 65000, 4000, 'Austin'), (6, 'Fay', 'Engineering', 102000, NULL, 'Austin'),
  (7, 'Gus', 'Support', 48000, 1000, 'Pune');
""")

for sql in [
    """SELECT dept, COUNT(*) AS staff, AVG(salary) AS avg_salary, MAX(salary)
       FROM employees GROUP BY dept ORDER BY dept""",
    """SELECT dept, COUNT(*) FROM employees
       WHERE salary > 55000 GROUP BY dept HAVING COUNT(*) >= 2 ORDER BY dept""",
    """SELECT dept, AVG(salary) FROM employees
       GROUP BY dept HAVING AVG(salary) > 60000 ORDER BY dept""",
    """SELECT city, dept, COUNT(*) FROM employees
       GROUP BY city, dept ORDER BY city, dept""",
]:
    print(db.execute(sql).fetchall())
```

Output:

```text
[('Engineering', 3, 95000.0, 102000), ('Sales', 2, 62500.0, 65000), ('Support', 2, 50000.0, 52000)]
[('Engineering', 3), ('Sales', 2)]
[('Engineering', 95000.0), ('Sales', 62500.0)]
[('Austin', 'Engineering', 1), ('Austin', 'Sales', 1), ('Leeds', 'Sales', 1), ('Leeds', 'Support', 1), ('Pune', 'Engineering', 2), ('Pune', 'Support', 1)]
```

The first query gives one row per department. In the second, `WHERE salary > 55000` runs first and removes both Support employees (52,000 and 48,000), so Support has no rows left to form a group; then `HAVING COUNT(*) >= 2` keeps groups with at least two qualifying employees. The third query filters on an aggregate, which only `HAVING` can do: Support's average of 50,000 fails the test. Grouping by two columns, as in the last query, makes one group for each combination that occurs.

### Example 4: Tracing the logical order

For `SELECT dept, COUNT(*) FROM employees WHERE salary > 55000 GROUP BY dept HAVING COUNT(*) >= 2 ORDER BY dept`:

| Step | Result |
| :--- | :--- |
| `FROM employees` | all 7 rows |
| `WHERE salary > 55000` | Asha, Ben, Chen, Eli, Fay (5 rows) |
| `GROUP BY dept` | Engineering {Asha, Chen, Fay}, Sales {Ben, Eli} |
| `HAVING COUNT(*) >= 2` | both groups survive |
| `SELECT dept, COUNT(*)` | (Engineering, 3), (Sales, 2) |
| `ORDER BY dept` | Engineering first, then Sales |

Reading a query in this order, rather than top to bottom, is the most reliable way to predict what it returns.

## Applications

- **Business reporting:** totals and averages by region, product, or month are `GROUP BY` queries, often with `HAVING` to show only significant groups.
- **Application back ends** filter, sort, and page results (`ORDER BY` with `LIMIT`) for every list a user sees.
- **Data cleaning:** `IS NULL` and `COUNT(column)` find missing values; `GROUP BY ... HAVING COUNT(*) > 1` finds duplicates.
- **Analytics tools** such as spreadsheets' pivot tables and BI dashboards generate grouped SQL behind the scenes.
- **Monitoring:** queries such as "error counts per service in the last hour, where the count exceeds 100" drive alerts.

## Common mistakes

- **Testing for NULL with `=`,** which never matches; use `IS NULL`.
- **Assuming `AVG` treats NULL as zero.** It ignores NULLs; use `AVG(COALESCE(x, 0))` if zeros are intended.
- **Using aggregates in `WHERE`,** such as `WHERE COUNT(*) > 2`; group conditions belong in `HAVING`.
- **Selecting non-grouped columns in a grouped query,** which standard SQL rejects and some systems answer with an arbitrary row's value.
- **Relying on row order without `ORDER BY`.** Without it, the order of results is not guaranteed and can change between runs.
- **Forgetting that `BETWEEN` is inclusive** and that `LIKE` case sensitivity varies by system.

## Revision notes

- Written order: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT. Logical order: FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT.
- Filters: comparisons, AND/OR/NOT, BETWEEN (inclusive), IN, LIKE (`%`, `_`), IS NULL.
- NULL comparisons are unknown; WHERE keeps only true; aggregates ignore NULLs; `COUNT(*)` counts rows.
- GROUP BY makes one output row per group; selected columns must be grouped or aggregated.
- WHERE filters rows before grouping; HAVING filters groups after aggregation.

## Practice questions

:::question basic
Write a query that lists the names of employees in Pune, in alphabetical order.
:::answer
`SELECT name FROM employees WHERE city = 'Pune' ORDER BY name;` On the example table, it returns Asha, Chen, and Gus.
:::

:::question basic
Why does `SELECT name FROM employees WHERE bonus = NULL` return no rows even though some bonuses are NULL?
:::answer
Comparing anything with NULL, including NULL itself, gives the value unknown rather than true. `WHERE` keeps only rows for which the condition is true, so no row qualifies. The correct condition is `bonus IS NULL`.
:::

:::question intermediate
What does `SELECT COUNT(*), COUNT(bonus) FROM employees WHERE dept = 'Engineering'` return on the example table, and why do the two counts differ?
:::answer
It returns (3, 2). There are three Engineering employees, so `COUNT(*)` is 3. Only Asha and Chen have a bonus; Fay's is NULL, and `COUNT(bonus)` counts only non-NULL values, giving 2.
:::

:::question intermediate
Write a query that shows each city with the average salary of its employees, but only for cities with an average above 70,000. What does it return?
:::answer
`SELECT city, AVG(salary) FROM employees GROUP BY city HAVING AVG(salary) > 70000 ORDER BY city;` Austin averages $(65000 + 102000)/2 = 83500$, Leeds $(60000 + 52000)/2 = 56000$, and Pune $(95000 + 88000 + 48000)/3 = 77000$. The result is Austin (83500.0) and Pune (77000.0).
:::

:::question intermediate
Explain why `SELECT dept, AVG(salary) AS avg FROM employees WHERE avg > 60000 GROUP BY dept` is invalid in standard SQL, and correct it.
:::answer
`WHERE` is evaluated before grouping and before `SELECT`, so neither the aggregate nor its alias `avg` exists when the `WHERE` condition is checked; aggregates are not allowed in `WHERE` at all. The condition must go in `HAVING`: `SELECT dept, AVG(salary) AS avg FROM employees GROUP BY dept HAVING AVG(salary) > 60000;`
:::

:::question advanced
A colleague claims that `WHERE NOT (bonus > 2000)` returns exactly the employees not returned by `WHERE bonus > 2000`. Show why this is wrong, and write a query that does return all the other employees.
:::answer
For employees whose bonus is NULL, `bonus > 2000` is unknown, and `NOT unknown` is still unknown, so those rows are excluded by both queries; on the example table, the two queries together return only 4 of the 7 employees. To include them, test for NULL explicitly: `WHERE bonus <= 2000 OR bonus IS NULL`, or equivalently `WHERE NOT (COALESCE(bonus, 0) > 2000)`, which treats a missing bonus as 0.
:::

## Further learning

- **Next:** *Subqueries, Views & Aggregation* nests queries inside queries and packages them as views.
- **Related:** *Inner, Outer & Self Joins* combines rows from several tables.
- **Related:** *Relational Model & Tuple Algebra* gives the formal operators behind `WHERE` (selection) and `SELECT` (projection).
