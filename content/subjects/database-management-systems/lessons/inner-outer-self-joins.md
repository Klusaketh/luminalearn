---
lesson: inner-outer-self-joins
title: Inner, Outer, and Self Joins
summary: Combine rows from several tables with cross, inner, left, right, and full outer joins, join a table to itself for hierarchies, find unmatched rows with anti-joins, and see how nested-loop, sort-merge, and hash joins execute them.
minutes: 45
type: theory
objectives:
  - Write cross, inner (equi- and theta-), and natural joins and predict their result sizes
  - Use left, right, and full outer joins to keep unmatched rows, and anti-joins to find them
  - Join a table to itself to query hierarchical or comparative relationships
  - Explain and compare the nested-loop, index nested-loop, sort-merge, and hash join algorithms
---

## Introduction

A well-designed relational database stores each fact once, which means the facts needed to answer a question are usually spread across several tables. An order row holds a customer ID, not the customer's name; an employee row holds a department code, not the department's floor; a manager is another row of the same employees table. To answer "list each order with its customer's name" or "who reports to whom?", the database must **join** tables, pairing up rows that belong together.

Joins are the most important operation in SQL and often the most expensive. This lesson covers every kind of join you will meet: the inner join that keeps only matching pairs, the outer joins that also keep rows with no partner, the self join that pairs a table with itself, and the anti-join that finds rows with no match. It ends with how a database engine actually computes a join, and why the choice of algorithm matters so much for performance.

**Before you start:** you should know SELECT, WHERE, GROUP BY, primary keys, and foreign keys.

## Core theory

### Cross join

`A CROSS JOIN B` (or `FROM A, B` with no condition) pairs **every** row of `A` with **every** row of `B`: the Cartesian product, with $|A| \times |B|$ rows. It is rarely what you want on its own; a missing join condition that silently produces a cross join is a classic bug that multiplies result sizes.

### Inner join

`A JOIN B ON condition` (also `INNER JOIN`) keeps only the pairs that satisfy the condition: the product followed by a selection.

- An **equi-join** uses equality, usually between a foreign key and the key it references: `ON e.dept = d.dept`.
- A **theta join** uses any comparison, such as `ON a.price < b.price`.
- A **natural join** (`NATURAL JOIN`) joins on all columns with the same name and keeps one copy of each. It is concise but fragile: adding a column with a common name, such as `updated_at`, to both tables silently changes the join.

Rows with **no matching partner** disappear from an inner join, and so do rows whose join column is NULL.

### Outer joins

Outer joins keep unmatched rows, filling the other table's columns with NULL:

| Join | Keeps |
| :--- | :--- |
| `A LEFT JOIN B` | every row of `A`; unmatched `A` rows get NULLs for `B`'s columns |
| `A RIGHT JOIN B` | every row of `B`; unmatched `B` rows get NULLs for `A`'s columns |
| `A FULL OUTER JOIN B` | every row of both, matched where possible |

`A RIGHT JOIN B` is the same as `B LEFT JOIN A` with the columns reordered, so many people write only left joins.

### Conditions in ON versus WHERE

For inner joins, putting a condition in `ON` or in `WHERE` gives the same result. For outer joins, it does not:

- A condition in **`ON`** decides which rows **match**; rows of the preserved table without a match are still kept, with NULLs.
- A condition in **`WHERE`** filters the **result** after the join; rows whose NULL-filled columns fail the test are removed, which can quietly turn an outer join into an inner join.

### Anti-joins and semi-joins

- An **anti-join** finds rows with **no** match: `A LEFT JOIN B ON ... WHERE B.key IS NULL`, or equivalently `NOT EXISTS`. Testing the key column (which is never NULL in a real match) is what makes it reliable.
- A **semi-join** finds rows of `A` that have **at least one** match, without duplicating `A`'s rows: `EXISTS` or `IN`.

### Self joins

A **self join** joins a table to itself under two aliases. It answers questions that compare rows of the same table: each employee with their manager (`e.manager_id = m.id`), pairs of customers in the same city, or consecutive readings of the same sensor. The aliases are essential, because they let each copy play a different role.

### Join algorithms

For tables $R$ and $S$ with $n_R$ and $n_S$ rows:

| Algorithm | How it works | Cost (comparisons or steps) | Best when |
| :--- | :--- | :--- | :--- |
| Nested loop | for each row of $R$, scan all of $S$ | $n_R \cdot n_S$ | one table is tiny, or any condition (theta joins) |
| Index nested loop | for each row of $R$, look up matches in an index on $S$ | about $n_R \cdot \log n_S$ (B+ tree) | $S$ has an index on the join column |
| Sort-merge | sort both on the join column, then merge in one pass | $O(n_R \log n_R + n_S \log n_S)$ for sorting plus $O(n_R + n_S)$ to merge | inputs already sorted, or the output must be sorted |
| Hash join | build a hash table on the smaller input, probe it with each row of the other | about $n_R + n_S$ | equi-joins on large unsorted inputs |

Real systems measure cost in disk pages read as well as comparisons, use **block** nested loops that read many rows of the outer table at a time, and let the **query optimizer** choose the algorithm and the join order using table statistics.

## Worked examples

The examples use `departments(dept, floor)` with Engineering, Sales, Support, and Research, and `employees(id, name, dept, manager_id)` with eight employees. Hana works in Marketing, which is not in the departments table, and nobody works in Research.

### Example 1: Inner and outer joins

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE departments (dept TEXT PRIMARY KEY, floor INTEGER);
INSERT INTO departments VALUES ('Engineering', 3), ('Sales', 1), ('Support', 2), ('Research', 4);
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT,
                        manager_id INTEGER REFERENCES employees(id));
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', NULL), (2, 'Ben', 'Sales', 5), (3, 'Chen', 'Engineering', 1),
  (4, 'Dara', 'Support', NULL), (5, 'Eli', 'Sales', NULL), (6, 'Fay', 'Engineering', 1),
  (7, 'Gus', 'Support', 4), (8, 'Hana', 'Marketing', NULL);
""")

print(db.execute("""SELECT e.name, d.dept, d.floor FROM employees AS e
                    JOIN departments AS d ON d.dept = e.dept ORDER BY e.id""").fetchall())
print(db.execute("""SELECT e.name, d.dept FROM employees AS e
                    LEFT JOIN departments AS d ON d.dept = e.dept WHERE d.dept IS NULL""").fetchall())
print(db.execute("""SELECT e.name, d.dept FROM employees AS e
                    RIGHT JOIN departments AS d ON d.dept = e.dept WHERE e.id IS NULL""").fetchall())
print(db.execute("""SELECT
    (SELECT COUNT(*) FROM employees CROSS JOIN departments),
    (SELECT COUNT(*) FROM employees AS e JOIN departments AS d ON d.dept = e.dept),
    (SELECT COUNT(*) FROM employees AS e LEFT JOIN departments AS d ON d.dept = e.dept),
    (SELECT COUNT(*) FROM employees AS e RIGHT JOIN departments AS d ON d.dept = e.dept),
    (SELECT COUNT(*) FROM employees AS e FULL OUTER JOIN departments AS d ON d.dept = e.dept)
""").fetchall())
```

Output:

```text
[('Asha', 'Engineering', 3), ('Ben', 'Sales', 1), ('Chen', 'Engineering', 3), ('Dara', 'Support', 2), ('Eli', 'Sales', 1), ('Fay', 'Engineering', 3), ('Gus', 'Support', 2)]
[('Hana', None)]
[(None, 'Research')]
[(32, 7, 8, 8, 9)]
```

The inner join returns 7 rows: Hana disappears because Marketing has no department row, and Research disappears because it has no employees. The left join keeps all 8 employees, and filtering for a NULL department finds Hana, the anti-join pattern. The right join keeps all 4 departments, and the NULL-employee filter finds Research. The full outer join keeps both unmatched rows, $7 + 1 + 1 = 9$, while the cross join pairs everything, $8 \times 4 = 32$.

### Example 2: Self joins and the ON-versus-WHERE trap

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE departments (dept TEXT PRIMARY KEY, floor INTEGER);
INSERT INTO departments VALUES ('Engineering', 3), ('Sales', 1), ('Support', 2), ('Research', 4);
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT,
                        manager_id INTEGER REFERENCES employees(id));
INSERT INTO employees VALUES
  (1, 'Asha', 'Engineering', NULL), (2, 'Ben', 'Sales', 5), (3, 'Chen', 'Engineering', 1),
  (4, 'Dara', 'Support', NULL), (5, 'Eli', 'Sales', NULL), (6, 'Fay', 'Engineering', 1),
  (7, 'Gus', 'Support', 4), (8, 'Hana', 'Marketing', NULL);
""")

print(db.execute("""SELECT e.name, m.name AS manager FROM employees AS e
                    JOIN employees AS m ON m.id = e.manager_id ORDER BY e.id""").fetchall())
print(db.execute("""SELECT d.dept, COUNT(e.id) FROM departments AS d
                    LEFT JOIN employees AS e ON e.dept = d.dept
                    GROUP BY d.dept ORDER BY d.dept""").fetchall())
print(db.execute("""SELECT d.dept, e.name FROM departments AS d
                    LEFT JOIN employees AS e ON e.dept = d.dept AND e.name LIKE 'A%'
                    ORDER BY d.dept""").fetchall())
print(db.execute("""SELECT d.dept, e.name FROM departments AS d
                    LEFT JOIN employees AS e ON e.dept = d.dept
                    WHERE e.name LIKE 'A%' ORDER BY d.dept""").fetchall())
```

Output:

```text
[('Ben', 'Eli'), ('Chen', 'Asha'), ('Fay', 'Asha'), ('Gus', 'Dara')]
[('Engineering', 3), ('Research', 0), ('Sales', 2), ('Support', 2)]
[('Engineering', 'Asha'), ('Research', None), ('Sales', None), ('Support', None)]
[('Engineering', 'Asha')]
```

The self join reads `employees` twice: `e` is the employee and `m` the manager whose `id` equals `e.manager_id`. Employees without a manager drop out, because their `manager_id` is NULL. Counting staff per department needs a left join and `COUNT(e.id)`: Research has no employees, so its only row has a NULL `e.id`, which `COUNT(e.id)` does not count, giving 0 (`COUNT(*)` would wrongly give 1). The last two queries differ only in where the name condition sits. In `ON`, it limits which employees match, and every department still appears. In `WHERE`, it removes the NULL-filled rows after the join, and the outer join behaves like an inner join.

### Example 3: Nested-loop join versus hash join

```python
def nested_loop_join(orders, customers):
    result, comparisons = [], 0
    for order_id, customer_id in orders:
        for cid, name in customers:              # scan the whole inner table each time
            comparisons += 1
            if customer_id == cid:
                result.append((order_id, name))
    return result, comparisons

def hash_join(orders, customers):
    table, steps = {}, 0
    for cid, name in customers:                  # build phase: hash the smaller input
        table.setdefault(cid, []).append(name)
        steps += 1
    result = []
    for order_id, customer_id in orders:         # probe phase: one lookup per row
        steps += 1
        for name in table.get(customer_id, []):
            result.append((order_id, name))
    return result, steps

orders = [(i, i % 100) for i in range(5000)]     # 5000 orders from 100 customers
customers = [(c, f"customer-{c}") for c in range(100)]
nl, comparisons = nested_loop_join(orders, customers)
hj, steps = hash_join(orders, customers)
print(len(nl), "rows by nested loop with", comparisons, "comparisons")
print(len(hj), "rows by hash join with", steps, "build and probe steps")
print("same result:", sorted(nl) == sorted(hj))
```

Output:

```text
5000 rows by nested loop with 500000 comparisons
5000 rows by hash join with 5100 build and probe steps
same result: True
```

The nested loop compares every order with every customer: $5000 \times 100 = 500{,}000$ comparisons. The hash join builds a table of the 100 customers once and then needs a single lookup per order: $100 + 5000 = 5100$ steps, about 100 times less work. The gap grows with the table sizes, which is why optimizers choose hash joins for large equi-joins, and why an index on a foreign-key column is so valuable: it turns the inner scan of a nested loop into a fast lookup.

## Applications

- **Every multi-table report** is a join: orders with customers, invoices with products, enrolments with students and courses.
- **Finding gaps:** anti-joins list customers who have never ordered, products never sold, or rows whose foreign keys point nowhere in imported data.
- **Hierarchies:** self joins (and recursive queries) show reporting lines, category trees, and bills of materials.
- **Data warehouses** join large fact tables to dimension tables, typically with hash joins.
- **Performance tuning:** checking which join algorithm and order the optimizer chose (with `EXPLAIN`) and adding indexes on join columns are routine tuning steps.

## Common mistakes

- **Forgetting the join condition,** producing a cross join with $|A| \times |B|$ rows.
- **Using an inner join when unmatched rows matter,** silently losing customers without orders or departments without staff.
- **Filtering an outer join's NULL-filled side in `WHERE`,** which removes the very rows the outer join kept; put such conditions in `ON`.
- **Counting with `COUNT(*)` after an outer join,** which counts the NULL-filled row as 1; count a column from the optional side instead.
- **Relying on `NATURAL JOIN`,** whose meaning changes when tables gain columns with shared names.
- **Omitting aliases in a self join,** which makes it impossible to say which copy each column comes from.

## Revision notes

- Cross join: $|A| \times |B|$ rows. Inner join: matching pairs only (equi, theta, natural).
- Left, right, and full outer joins keep unmatched rows from one or both sides, padding with NULLs.
- Conditions in `ON` shape the match; conditions in `WHERE` filter the joined result.
- Anti-join: `LEFT JOIN ... WHERE right.key IS NULL` or `NOT EXISTS`. Semi-join: `EXISTS` or `IN`.
- Self join: one table under two aliases, for managers, pairs, and sequences.
- Algorithms: nested loop ($n_R n_S$), index nested loop, sort-merge, hash join (about $n_R + n_S$ for equi-joins).

## Practice questions

:::question basic
Table `A` has 12 rows and table `B` has 5. How many rows does `A CROSS JOIN B` return, and what is the largest possible size of `A JOIN B ON ...`?
:::answer
The cross join returns $12 \times 5 = 60$ rows. An inner join is a filtered cross join, so it returns at most 60 rows, reached only if every pair satisfies the condition.
:::

:::question basic
What is the difference between an inner join and a left outer join?
:::answer
An inner join returns only pairs of rows that satisfy the join condition, so rows of either table without a match are dropped. A left outer join returns every row of the left table: matched rows are paired as usual, and left rows without a match appear once with NULLs in the right table's columns.
:::

:::question intermediate
Write a query that lists customers who have never placed an order, given `customers(id, name)` and `orders(id, customer_id)`.
:::answer
`SELECT c.name FROM customers AS c LEFT JOIN orders AS o ON o.customer_id = c.id WHERE o.id IS NULL;` The left join keeps every customer, and customers without orders have NULL in all order columns. Testing `o.id`, the orders key, is reliable because a real match always has a non-NULL key. An equivalent form is `WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id)`.
:::

:::question intermediate
Using `employees(id, name, manager_id)`, write a query that lists each employee together with their manager's manager.
:::answer
Join the table to itself twice: `SELECT e.name, gm.name AS grand_manager FROM employees AS e JOIN employees AS m ON m.id = e.manager_id JOIN employees AS gm ON gm.id = m.manager_id;` Each alias plays a role: the employee, the manager, and the manager's manager. Use left joins instead if employees with fewer than two levels above them should still appear.
:::

:::question intermediate
A hash join of tables with 1,000,000 and 10,000 rows is planned. Which table should be used to build the hash table, and roughly how many steps does the join take compared with a nested loop?
:::answer
Build on the smaller table, the 10,000 rows, so the hash table is small and more likely to fit in memory, then probe it with each of the 1,000,000 rows: about $10{,}000 + 1{,}000{,}000 = 1.01$ million steps. A plain nested loop would make $10^6 \times 10^4 = 10^{10}$ comparisons, about ten thousand times more.
:::

:::question advanced
A report uses `FROM departments d LEFT JOIN employees e ON e.dept = d.dept WHERE e.salary > 50000`, and the team notices that departments with no well-paid staff are missing. Explain why, and give two correct alternatives.
:::answer
For a department with no employees earning over 50,000 (or with no employees at all), the left join produces rows whose employee columns are NULL or whose salaries fail the test. The `WHERE` clause runs after the join; `e.salary > 50000` is false or unknown for those rows, so they are removed, and the outer join behaves like an inner join. To keep every department, move the condition into the join: `LEFT JOIN employees e ON e.dept = d.dept AND e.salary > 50000`. Alternatively, keep the join plain and filter inside an aggregate, for example `COUNT(CASE WHEN e.salary > 50000 THEN 1 END)` with `GROUP BY d.dept`, which reports 0 for departments without such staff.
:::

## Further learning

- **Next:** *Functional Dependencies & Normal Forms* explains why data is split into the tables that joins reassemble.
- **Related:** *Subqueries, Views & Aggregation* covers `EXISTS` and `IN`, the semi- and anti-join forms.
- **Related:** *Query Processing & Optimization* shows how optimizers choose join algorithms and orders.
