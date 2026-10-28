---
lesson: file-systems-vs-dbms
title: File Systems vs DBMS
summary: Why storing an organisation's data in separate application files leads to redundancy, inconsistency, and lost updates, and how a database management system solves these problems with shared schemas, declarative queries, transactions, and access control.
minutes: 30
type: theory
objectives:
  - Identify the problems of file-processing systems, including redundancy, inconsistency, data isolation, integrity, atomicity, concurrency, and security problems
  - Explain how a DBMS addresses each problem through a shared schema, constraints, transactions, and access control
  - Contrast declarative querying with procedural data access
  - Describe the main components of a DBMS and the roles of its users, and judge when a DBMS is not needed
---

## Introduction

Imagine a small company in which each department writes its own programs and keeps its own files. Sales keeps orders in one file, customer service keeps customer details in another, and billing keeps invoices in a third. Each program works on its own. Then a customer moves house. Customer service updates its file, but the orders file still holds the old address, and the next delivery goes to the wrong city. Someone asks "which customers in Mumbai ordered a monitor last month?", and a programmer must write a new program to answer it. Two clerks update the same file at the same time, and one update vanishes.

This is a **file-processing system**, and it was how organisations stored data before database systems became common in the 1960s and 1970s. A **database management system (DBMS)** replaces the collection of private files with one shared, managed collection of data, together with software that answers questions, enforces rules, and protects the data from crashes, conflicts, and unauthorised access. This lesson examines exactly what goes wrong with files, and how each DBMS feature fixes it.

**Before you start:** you should be comfortable reading short Python programs.

## Core theory

### Problems with file-processing systems

1. **Data redundancy and inconsistency.** The same fact (a customer's city) is stored in several files. Copies drift apart when one is updated and another is not, so the data contradicts itself.
2. **Difficulty accessing data.** Every new question needs a new program, because each file has its own format and nobody wrote a general query facility.
3. **Data isolation.** Data is scattered across files with different formats, which makes combining it hard.
4. **Integrity problems.** Rules such as "a balance must never be negative" are buried in the code of each program. Adding or changing a rule means finding and changing every program that writes the data.
5. **Atomicity problems.** A money transfer debits one account and credits another. If the program crashes between the two steps, the money disappears. Files offer no way to say "all of these changes, or none".
6. **Concurrent-access anomalies.** Two programs read the same balance, each subtracts a withdrawal, and each writes its result back: one withdrawal is lost.
7. **Security problems.** It is hard to let a payroll clerk see salaries but not medical records when both live in files that applications read directly.

### What a DBMS provides

| Problem | DBMS solution |
| :--- | :--- |
| Redundancy and inconsistency | one shared, centrally designed **schema**; each fact stored once (normalization) |
| Difficulty accessing data | a **declarative query language** (SQL) that can answer new questions without new programs |
| Data isolation | all data described by one data model and accessible through one interface |
| Integrity | **constraints** (keys, foreign keys, checks) declared once and enforced on every update |
| Atomicity | **transactions**: a group of changes either all take effect or none do |
| Concurrency | **concurrency control** (locking or multiversioning) so concurrent users do not corrupt each other's work |
| Security | **access control**: users, roles, privileges, and views that expose only part of the data |
| Crash safety | **recovery**: logging so that committed work survives failures |

### Declarative versus procedural access

With files, a programmer writes **how** to get the answer: open each file, loop over its records, match customers to orders, filter, and sort. With a DBMS, the user states **what** answer is wanted:

```sql
SELECT c.name, o.item
FROM orders AS o JOIN customers AS c ON c.name = o.customer
WHERE c.city = 'Mumbai';
```

The DBMS's **query optimizer** decides how to compute it, choosing indexes and join methods based on the data. If the data grows or new indexes are added, the same query keeps working, and often becomes faster, without any change.

### Inside a DBMS

- **Query processor:** parses SQL, checks it against the schema, optimizes it, and executes the resulting plan.
- **Storage manager:** stores data in files on disk, manages the buffer of pages cached in memory, and maintains indexes.
- **Transaction manager:** enforces atomicity, isolation, and durability with concurrency control and recovery.
- **Catalog (data dictionary):** stores metadata, the schemas, constraints, statistics, and privileges.

People interact with it in different roles: **end users** run applications and queries, **application programmers** write programs that use the database, and the **database administrator (DBA)** designs the schema, grants privileges, tunes performance, and plans backups.

### When a DBMS is not needed

A DBMS has costs: software, administration, learning, and some overhead per operation. Simple, single-user data that is written once and read sequentially (a configuration file, a log file, a small spreadsheet) often does not need one. Even then, an embedded engine such as SQLite, which runs inside the application with no server, provides most of the benefits cheaply; it is built into every major phone and web browser.

## Worked examples

### Example 1: How duplicated data becomes inconsistent

Two departments keep their own files. The orders file copies each customer's city, and the customers file has the city too.

```python
import csv
import io

orders_file = """order_id,customer,customer_city,item
1,Asha,Pune,Keyboard
2,Ben,Leeds,Monitor
3,Asha,Pune,Mouse
"""
customers_file = """customer,city,phone
Asha,Pune,555-0101
Ben,Leeds,555-0102
"""
orders = list(csv.DictReader(io.StringIO(orders_file)))
customers = list(csv.DictReader(io.StringIO(customers_file)))

for c in customers:                       # Asha moves; customer service updates its own file only
    if c["customer"] == "Asha":
        c["city"] = "Mumbai"

city = {c["customer"]: c["city"] for c in customers}
for o in orders:
    if o["customer_city"] != city[o["customer"]]:
        print(f"order {o['order_id']}: orders file says {o['customer_city']}, "
              f"customers file says {city[o['customer']]}")
```

Output:

```text
order 1: orders file says Pune, customers file says Mumbai
order 3: orders file says Pune, customers file says Mumbai
```

The company now holds two contradictory "truths" about where Asha lives, and nothing in the files says which is correct. The root cause is **redundancy**: the city is stored in more than one place, so every update must find every copy.

### Example 2: The same data in a database

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE customers (name TEXT PRIMARY KEY, city TEXT, phone TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY,
                     customer TEXT REFERENCES customers(name),
                     item TEXT);
INSERT INTO customers VALUES ('Asha', 'Pune', '555-0101'), ('Ben', 'Leeds', '555-0102');
INSERT INTO orders VALUES (1, 'Asha', 'Keyboard'), (2, 'Ben', 'Monitor'), (3, 'Asha', 'Mouse');
""")
db.execute("UPDATE customers SET city = 'Mumbai' WHERE name = 'Asha'")   # the fact is stored once

query = """
SELECT o.order_id, c.name, c.city, o.item
FROM orders AS o JOIN customers AS c ON c.name = o.customer
WHERE c.city = 'Mumbai'
ORDER BY o.order_id
"""
for row in db.execute(query):
    print(row)
```

Output:

```text
(1, 'Asha', 'Mumbai', 'Keyboard')
(3, 'Asha', 'Mumbai', 'Mouse')
```

Each customer's city now exists in exactly one row, and orders refer to customers by key. One `UPDATE` changes the fact everywhere it is used, because nothing else stores a copy. The new question "which orders go to Mumbai?" needed no new program, only a declarative query, which the DBMS planned and executed on its own.

### Example 3: Atomic transfers

A transfer must debit account A and credit account B, never just one of them, and a balance may never go negative.

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE accounts (id TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0));
INSERT INTO accounts VALUES ('A', 100), ('B', 50);
""")

def transfer(amount, fail_midway=False):
    try:
        with db:                          # one transaction: commit on success, roll back on error
            db.execute("UPDATE accounts SET balance = balance - ? WHERE id = 'A'", (amount,))
            if fail_midway:
                raise RuntimeError("crash between the two updates")
            db.execute("UPDATE accounts SET balance = balance + ? WHERE id = 'B'", (amount,))
    except (RuntimeError, sqlite3.IntegrityError) as error:
        print("rolled back:", error)
    print(dict(db.execute("SELECT id, balance FROM accounts")))

transfer(30)
transfer(30, fail_midway=True)
transfer(500)
```

Output:

```text
{'A': 70, 'B': 80}
rolled back: crash between the two updates
{'A': 70, 'B': 80}
rolled back: CHECK constraint failed: balance >= 0
{'A': 70, 'B': 80}
```

The first transfer commits. The second fails after the debit, and the transaction is rolled back, so A's 30 is not lost. The third would make A's balance negative; the `CHECK` constraint, declared once in the schema, rejects it no matter which program attempts it, and again the whole transaction is undone. With plain files, both failures would have left the data damaged.

## Applications

- **Banking and payments** rely on transactions so that transfers are all-or-nothing and survive crashes.
- **E-commerce** keeps one authoritative record of customers, products, and stock, queried by websites, warehouses, and analytics.
- **Healthcare** records use access control to show clinicians, billing staff, and researchers different parts of the same data.
- **Mobile apps and browsers** embed SQLite to store messages, history, and settings reliably.
- **Data analysis** uses declarative SQL so analysts can ask new questions without writing programs for each one.

## Common mistakes

- **Thinking a DBMS is just a faster file.** Its value lies in shared schemas, constraints, transactions, concurrency control, recovery, and security.
- **Copying data "for convenience"** into several tables, which reintroduces the redundancy and inconsistency a DBMS is meant to remove.
- **Enforcing rules only in application code,** so a different program or a manual update can break them; declare them as constraints.
- **Issuing related updates outside a transaction,** which loses atomicity if anything fails halfway.
- **Assuming every program needs a database server.** Simple single-user data may need only a file or an embedded engine.

## Revision notes

- File-processing problems: redundancy and inconsistency, difficult access, data isolation, integrity, atomicity, concurrency anomalies, security.
- A DBMS offers a shared schema, declarative queries, constraints, transactions, concurrency control, recovery, and access control.
- Declarative queries say what is wanted; the optimizer decides how to get it.
- Components: query processor, storage manager, transaction manager, catalog.
- Roles: end users, application programmers, database administrator.
- Embedded engines such as SQLite give DBMS guarantees without a server.

## Practice questions

:::question basic
What is data redundancy, and how does it lead to inconsistency?
:::answer
Redundancy means the same fact is stored in more than one place, such as a customer's address in both the orders file and the customers file. When the fact changes and only some copies are updated, the copies disagree, and the system holds inconsistent data: different programs give different answers to the same question.
:::

:::question basic
Name three services a DBMS provides that a plain file system does not.
:::answer
Any three of: a declarative query language for ad hoc questions; integrity constraints enforced on every update; atomic transactions that apply all or none of a group of changes; concurrency control for simultaneous users; crash recovery that preserves committed work; and fine-grained access control over who can see or change which data.
:::

:::question intermediate
Two clerks simultaneously process withdrawals of 100 and 50 from an account holding 500, using a program that reads the balance from a file, subtracts, and writes it back. What can go wrong, and how does a DBMS prevent it?
:::answer
Both clerks' programs may read 500 before either writes. One writes 400 and the other writes 450, and whichever writes last wins, so the final balance is 400 or 450 instead of 350: a lost update. A DBMS runs each withdrawal as a transaction under concurrency control, for example by locking the row, so the second transaction waits for, or sees, the first transaction's result, and the final balance is 350.
:::

:::question intermediate
Explain the difference between declarative and procedural data access, and why declarative access helps when data volumes grow.
:::answer
Procedural access spells out the steps: which files to open, how to loop, how to match and filter records. Declarative access, as in SQL, describes only the result wanted. Because the DBMS chooses the execution strategy, it can adapt to the data, using an index when one exists, picking a different join method for large tables, or running in parallel, without the query changing. Procedural programs stay fixed to the strategy their authors coded, which may become inefficient as the data grows.
:::

:::question intermediate
A rule says that an order's quantity must be between 1 and 100. Compare enforcing it in each application program with declaring it in the database.
:::answer
In application code, every program that writes orders must include the check, and they may implement it differently or forget it; a manual fix or a new program can insert invalid data. Declared once as a `CHECK (quantity BETWEEN 1 AND 100)` constraint, the rule is enforced by the DBMS on every insert and update from every source, and changing it means changing one definition.
:::

:::question advanced
A start-up stores user profiles as one JSON file per user on disk and asks whether it needs a DBMS. What questions would you ask, and what would push the answer towards using one?
:::answer
Ask how many users and how fast the data grows; whether several servers or processes write the data at once; whether operations must be atomic across several users' files (such as a payment between two users); what questions the business needs to ask across all users; and how important it is never to lose committed updates after a crash. Concurrent writers, multi-record operations that must be atomic, cross-user queries, and strict durability requirements all point to a DBMS. If the data is small, written by one process, and only ever read per user, files may suffice for now, although an embedded database would still add safety at little cost.
:::

## Further learning

- **Next:** *3-Schema Architecture* explains how a DBMS separates how data is viewed, structured, and stored.
- **Related:** *ACID Properties & Transaction States* explains how the guarantees in Example 3 are provided.
- **Related:** *Functional Dependencies & Normal Forms* shows how to design schemas that store each fact once.
