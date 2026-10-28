---
lesson: subqueries-views-aggregation
title: Subqueries, Views, and Aggregation
summary: Nest queries inside queries with scalar, IN, EXISTS, and correlated subqueries, structure complex queries with derived tables and common table expressions, save queries as views, combine results with set operations, and rank rows with window functions.
minutes: 55
type: theory
objectives:
  - Write scalar, IN, and EXISTS subqueries and explain how a correlated subquery is evaluated
  - Restructure complex aggregation queries with derived tables and common table expressions (WITH)
  - Create and query views and explain when views can and cannot be updated
  - Combine query results with UNION, UNION ALL, INTERSECT, and EXCEPT, and compute per-group rankings with window functions
---

## Introduction

Some questions cannot be answered in a single pass over a table. "Which employees earn more than the company average?" needs the average first. "Which employees earn more than the average of **their own** department?" needs a different average for every row. "Which departments have no employees?" asks about the absence of rows.

SQL handles these by letting a query contain another query, a **subquery**, wherever a value, a list of values, or a table is expected. Complex queries can be broken into named steps with **common table expressions**, saved for reuse as **views**, and combined with **set operations**. **Window functions** extend aggregation by computing values over groups without collapsing the rows. This lesson covers all of these on one small company database, with every result shown.

**Before you start:** you should know SELECT, WHERE, GROUP BY, HAVING, and aggregate functions.

## Core theory

### Where subqueries can appear

| Kind | Returns | Used with | Example |
| :--- | :--- | :--- | :--- |
| Scalar subquery | one value (one row, one column) | comparisons, `SELECT` list | `salary > (SELECT AVG(salary) FROM employees)` |
| List subquery | one column, many rows | `IN`, `NOT IN` | `dept IN (SELECT dept FROM departments WHERE budget > 150000)` |
| Existence test | whether any row exists | `EXISTS`, `NOT EXISTS` | `NOT EXISTS (SELECT 1 FROM employees WHERE ...)` |
| Table subquery (derived table) | a whole table | `FROM` | `FROM (SELECT dept, AVG(salary) AS a FROM employees GROUP BY dept) AS t` |

A scalar subquery that returns no rows yields NULL; one that returns several rows is an error in standard SQL.

### Correlated subqueries

A **correlated** subquery refers to a column of the outer query, so it is logically re-evaluated **for each outer row**:

```sql
SELECT e.name FROM employees AS e
WHERE e.salary > (SELECT AVG(i.salary) FROM employees AS i WHERE i.dept = e.dept);
```

For each employee `e`, the inner query computes the average of `e`'s own department. The table aliases (`e` and `i`) are essential, because both queries read the same table. Optimizers often rewrite correlated subqueries as joins, but the logical meaning is "once per outer row".

### IN, EXISTS, and NULLs

`EXISTS` is true when the subquery returns at least one row; the selected columns do not matter, so `SELECT 1` is conventional. `NOT EXISTS` is the clearest way to ask "for which rows is there no matching row?".

Beware of `NOT IN` with a subquery that can return NULL. `x NOT IN (1, 2, NULL)` means `x <> 1 AND x <> 2 AND x <> NULL`, and the last comparison is unknown, so the whole condition can never be true and the query returns nothing. `NOT EXISTS` does not have this problem.

### Comparing with ALL and ANY

Standard SQL allows `salary > ALL (subquery)` (greater than every value) and `salary > ANY (subquery)` (greater than at least one). They can always be rewritten with aggregates: `> ALL` as `> (SELECT MAX(...))` and `> ANY` as `> (SELECT MIN(...))`, provided the subquery returns no NULLs and, for `ALL`, at least one row. SQLite does not support `ALL` and `ANY`, so this lesson uses the aggregate forms.

### Derived tables and common table expressions

Aggregates of aggregates, such as "the highest department average", need two levels: first compute each department's average, then take the maximum. A **derived table** is a subquery in `FROM`; a **common table expression (CTE)** names the intermediate result up front, which is easier to read:

```sql
WITH dept_avg AS (
    SELECT dept, AVG(salary) AS avg_salary FROM employees GROUP BY dept
)
SELECT MAX(avg_salary) FROM dept_avg;
```

CTEs can reference earlier CTEs in the same `WITH` clause, and **recursive** CTEs (`WITH RECURSIVE`) can traverse hierarchies such as organisation charts.

### Views

A **view** is a named, stored query: `CREATE VIEW name AS SELECT ...`. Querying a view runs its definition against the current data, so a view always reflects the latest rows, unlike a copy made at one moment. Views:

- simplify repeated complex queries;
- form external schemas, showing each user only what they need (security);
- provide logical data independence when base tables change.

A view built from one table with plain columns can usually be updated, with changes passed through to the base table. Views with joins, `GROUP BY`, aggregates, or `DISTINCT` are generally **read-only**, because a change to an aggregated row has no single meaning in the base tables; some systems allow updates through such views with `INSTEAD OF` triggers. A **materialized view** stores its result physically for speed and must be refreshed when the base data changes.

### Set operations

Two queries with compatible columns can be combined:

| Operator | Result |
| :--- | :--- |
| `UNION` | rows in either result, duplicates removed |
| `UNION ALL` | rows in either result, duplicates kept (and cheaper, since no deduplication is needed) |
| `INTERSECT` | rows in both results |
| `EXCEPT` (`MINUS` in Oracle) | rows in the first result but not the second |

### Window functions

A window function computes a value **for each row** from a set of related rows (its window), without merging them:

```sql
RANK() OVER (PARTITION BY dept ORDER BY salary DESC)
```

ranks each employee within their department. `GROUP BY` would collapse each department to one row; a window keeps every row and adds the rank. Common window functions are `ROW_NUMBER`, `RANK`, `DENSE_RANK`, running totals with `SUM(...) OVER (ORDER BY ...)`, and `LAG`/`LEAD` for comparing a row with its neighbours.

## Worked examples

The examples use two tables: `departments(dept, budget, floor)` with Engineering (500,000), Sales (200,000), Support (120,000), and Research (300,000), and `employees(id, name, dept, salary, city)` with seven employees, none of them in Research.

### Example 1: Scalar, correlated, IN, and EXISTS subqueries

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE departments (dept TEXT PRIMARY KEY, budget INTEGER, floor INTEGER);
INSERT INTO departments VALUES ('Engineering', 500000, 3), ('Sales', 200000, 1),
                               ('Support', 120000, 2), ('Research', 300000, 4);
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER, city TEXT);
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', 95000, 'Pune'), (2, 'Ben', 'Sales', 60000, 'Leeds'),
  (3, 'Chen', 'Engineering', 88000, 'Pune'), (4, 'Dara', 'Support', 52000, 'Leeds'),
  (5, 'Eli', 'Sales', 65000, 'Austin'), (6, 'Fay', 'Engineering', 102000, 'Austin'),
  (7, 'Gus', 'Support', 48000, 'Pune');
""")

queries = {
    "above company average":
        "SELECT name, salary FROM employees WHERE salary > (SELECT AVG(salary) FROM employees) ORDER BY name",
    "above own department average": """
        SELECT e.name, e.dept, e.salary FROM employees AS e
        WHERE e.salary > (SELECT AVG(i.salary) FROM employees AS i WHERE i.dept = e.dept)
        ORDER BY e.name""",
    "in big-budget departments":
        "SELECT name FROM employees WHERE dept IN (SELECT dept FROM departments WHERE budget > 150000) ORDER BY name",
    "departments with nobody":
        "SELECT dept FROM departments AS d WHERE NOT EXISTS (SELECT 1 FROM employees AS e WHERE e.dept = d.dept)",
    "earn more than everyone in Sales":
        "SELECT name FROM employees WHERE salary > (SELECT MAX(salary) FROM employees WHERE dept = 'Sales') ORDER BY name",
}
for label, sql in queries.items():
    print(f"{label}: {db.execute(sql).fetchall()}")
```

Output:

```text
above company average: [('Asha', 95000), ('Chen', 88000), ('Fay', 102000)]
above own department average: [('Dara', 'Support', 52000), ('Eli', 'Sales', 65000), ('Fay', 'Engineering', 102000)]
in big-budget departments: [('Asha',), ('Ben',), ('Chen',), ('Eli',), ('Fay',)]
departments with nobody: [('Research',)]
earn more than everyone in Sales: [('Asha',), ('Chen',), ('Fay',)]
```

The company average is $510000 / 7 \approx 72857$, so three people exceed it. The correlated version compares each employee with their own department: Dara (52,000) earns little overall but beats Support's average of 50,000, while Asha (95,000) exactly equals Engineering's average and is not strictly above it. Research is the only department for which no employee row exists. The last query is the aggregate form of `salary > ALL (SELECT salary ... WHERE dept = 'Sales')`.

### Example 2: Derived tables and a CTE

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE departments (dept TEXT PRIMARY KEY, budget INTEGER, floor INTEGER);
INSERT INTO departments VALUES ('Engineering', 500000, 3), ('Sales', 200000, 1),
                               ('Support', 120000, 2), ('Research', 300000, 4);
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER, city TEXT);
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', 95000, 'Pune'), (2, 'Ben', 'Sales', 60000, 'Leeds'),
  (3, 'Chen', 'Engineering', 88000, 'Pune'), (4, 'Dara', 'Support', 52000, 'Leeds'),
  (5, 'Eli', 'Sales', 65000, 'Austin'), (6, 'Fay', 'Engineering', 102000, 'Austin'),
  (7, 'Gus', 'Support', 48000, 'Pune');
""")

print(db.execute("""
    SELECT MAX(avg_salary)
    FROM (SELECT dept, AVG(salary) AS avg_salary FROM employees GROUP BY dept)
""").fetchall())

print(db.execute("""
    WITH totals AS (
        SELECT dept, SUM(salary) AS payroll FROM employees GROUP BY dept
    )
    SELECT t.dept, t.payroll, d.budget, ROUND(100.0 * t.payroll / d.budget, 1) AS pct
    FROM totals AS t JOIN departments AS d ON d.dept = t.dept
    ORDER BY pct DESC
""").fetchall())
```

Output:

```text
[(95000.0,)]
[('Support', 100000, 120000, 83.3), ('Sales', 125000, 200000, 62.5), ('Engineering', 285000, 500000, 57.0)]
```

`MAX(AVG(salary))` is not allowed directly, so the inner query computes one average per department and the outer query takes their maximum. The CTE names the payroll per department, then joins it to the budgets: Support spends the largest share of its budget on salaries. Writing `100.0 * payroll` forces real-number division; with two integers, some databases would truncate the result.

### Example 3: A view that stays current, set operations, and ranking

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER, city TEXT);
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', 95000, 'Pune'), (2, 'Ben', 'Sales', 60000, 'Leeds'),
  (3, 'Chen', 'Engineering', 88000, 'Pune'), (4, 'Dara', 'Support', 52000, 'Leeds'),
  (5, 'Eli', 'Sales', 65000, 'Austin'), (6, 'Fay', 'Engineering', 102000, 'Austin'),
  (7, 'Gus', 'Support', 48000, 'Pune');
CREATE VIEW dept_summary AS
  SELECT dept, COUNT(*) AS staff, ROUND(AVG(salary)) AS avg_salary FROM employees GROUP BY dept;
""")

print(db.execute("SELECT * FROM dept_summary ORDER BY dept").fetchall())
db.execute("INSERT INTO employees VALUES (8, 'Hana', 'Support', 70000, 'Leeds')")
print(db.execute("SELECT * FROM dept_summary ORDER BY dept").fetchall())

engineering = "SELECT city FROM employees WHERE dept = 'Engineering'"
sales = "SELECT city FROM employees WHERE dept = 'Sales'"
for op in ("UNION", "UNION ALL", "INTERSECT", "EXCEPT"):
    print(op, db.execute(f"{engineering} {op} {sales} ORDER BY city").fetchall())

print(db.execute("""
    SELECT dept, name, salary, RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank_in_dept
    FROM employees ORDER BY dept, rank_in_dept
""").fetchall())
```

Output:

```text
[('Engineering', 3, 95000.0), ('Sales', 2, 62500.0), ('Support', 2, 50000.0)]
[('Engineering', 3, 95000.0), ('Sales', 2, 62500.0), ('Support', 3, 56667.0)]
UNION [('Austin',), ('Leeds',), ('Pune',)]
UNION ALL [('Austin',), ('Austin',), ('Leeds',), ('Pune',), ('Pune',)]
INTERSECT [('Austin',)]
EXCEPT [('Pune',)]
[('Engineering', 'Fay', 102000, 1), ('Engineering', 'Asha', 95000, 2), ('Engineering', 'Chen', 88000, 3), ('Sales', 'Eli', 65000, 1), ('Sales', 'Ben', 60000, 2), ('Support', 'Hana', 70000, 1), ('Support', 'Dara', 52000, 2), ('Support', 'Gus', 48000, 3)]
```

The view is not a stored copy: after Hana joins Support, the same `SELECT * FROM dept_summary` shows three Support staff and a new average. Engineering staff work in Pune, Pune, and Austin, and Sales staff in Leeds and Austin. `UNION` removes duplicate cities, `UNION ALL` keeps all five values, `INTERSECT` finds Austin, the only city with both, and `EXCEPT` finds Pune, which has Engineering but not Sales staff. The window function ranks people within each department while keeping every row, which `GROUP BY` could not do.

## Applications

- **Reporting:** CTEs break long reports into readable steps, such as monthly totals, then growth rates, then rankings.
- **Security and simplicity:** views expose curated, read-only slices of data to analysts and applications.
- **Data quality checks:** `NOT EXISTS` finds orphaned rows, such as orders whose customer was deleted, and set operations compare two versions of a dataset.
- **Leaderboards and top-N per group:** window functions find the top three products per category or each customer's most recent order.
- **Hierarchies:** recursive CTEs walk organisation charts, bills of materials, and threaded comments.

## Common mistakes

- **Using `NOT IN` with a subquery that may return NULL,** which silently returns no rows; prefer `NOT EXISTS`.
- **Writing a scalar subquery that can return more than one row,** which is an error (or, in some systems, silently uses one row).
- **Forgetting aliases in correlated subqueries,** so the inner query compares a column with itself instead of with the outer row.
- **Using `UNION` when duplicates should be kept,** or paying for deduplication when `UNION ALL` would do.
- **Expecting a view to store data.** An ordinary view is recomputed from the base tables each time; only materialized views store results.
- **Trying to update an aggregate or join view directly;** such views are usually read-only.

## Revision notes

- Subqueries: scalar (one value), list (`IN`), existence (`EXISTS`), table (`FROM`).
- Correlated subqueries reference the outer row and are logically evaluated once per outer row.
- `NOT EXISTS` is safe with NULLs; `NOT IN` is not.
- `> ALL` ≈ `> MAX(...)`, `> ANY` ≈ `> MIN(...)` (when no NULLs are involved).
- Derived tables and CTEs (`WITH`) allow aggregates of aggregates and readable multi-step queries.
- Views are stored queries: current data, security, independence; usually read-only if they aggregate or join.
- `UNION` (deduplicated), `UNION ALL`, `INTERSECT`, `EXCEPT`. Window functions compute per-row values over partitions.

## Practice questions

:::question basic
Write a query that lists the employees who earn less than the company's average salary.
:::answer
`SELECT name FROM employees WHERE salary < (SELECT AVG(salary) FROM employees);` The scalar subquery computes the average once (about 72,857 for the example data), and the outer query keeps Ben, Dara, Eli, and Gus.
:::

:::question basic
What is the difference between `UNION` and `UNION ALL`?
:::answer
`UNION` returns the rows of both queries with duplicates removed, so a value present in both appears once. `UNION ALL` returns every row from both queries, including duplicates. `UNION ALL` is cheaper because it does not need to sort or hash the rows to remove duplicates.
:::

:::question intermediate
Explain how the database evaluates the correlated subquery in Example 1 for the employee Gus.
:::answer
For the outer row Gus (Support, 48,000), the inner query runs with `e.dept = 'Support'` and computes the average salary of Support employees, $(52000 + 48000)/2 = 50000$. The condition $48000 > 50000$ is false, so Gus is excluded. The same evaluation happens, with a different department value, for every other employee.
:::

:::question intermediate
A table `customers(id)` and a table `orders(customer_id)` exist, and some `orders.customer_id` values are NULL. Why might `SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders)` return no rows, and how do you fix it?
:::answer
`NOT IN` requires `id` to differ from every value in the list. When the list contains a NULL, the comparison `id <> NULL` is unknown, so the overall condition is unknown, never true, for every customer, and no rows are returned. Fix it with `NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = customers.id)`, or filter the NULLs out with `WHERE customer_id IS NOT NULL` inside the subquery.
:::

:::question intermediate
Write a query, using a CTE, that returns the departments whose average salary is above the average of all department averages.
:::answer
```sql
WITH dept_avg AS (
    SELECT dept, AVG(salary) AS avg_salary FROM employees GROUP BY dept
)
SELECT dept FROM dept_avg
WHERE avg_salary > (SELECT AVG(avg_salary) FROM dept_avg);
```
With the example data, the department averages are 95,000, 62,500, and 50,000, whose mean is 69,166.67, so only Engineering is returned.
:::

:::question advanced
Explain why a view defined as `SELECT dept, AVG(salary) FROM employees GROUP BY dept` cannot accept `UPDATE ... SET avg = 70000 WHERE dept = 'Sales'`, and how such an update could be supported if it were really needed.
:::answer
Each view row summarises several base rows, and the update states a desired average without saying how to change the individual salaries: raising one person's salary, raising everyone's equally, or any other combination would produce the new average. Because the change has no unique translation to the base table, the DBMS rejects it. If the business defines a rule, such as scaling every Sales salary proportionally, an `INSTEAD OF UPDATE` trigger on the view can implement that rule explicitly; otherwise, updates should be made to the base table.
:::

## Further learning

- **Next:** *Inner, Outer & Self Joins* combines rows from multiple tables, often the efficient alternative to subqueries.
- **Related:** *3-Schema Architecture* explains views as external schemas.
- **Related:** *Query Processing & Optimization* describes how subqueries are rewritten and executed.
