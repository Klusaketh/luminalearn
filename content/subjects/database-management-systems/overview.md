A database management system (DBMS) is software that stores large collections of data and lets many users and programs query and update them safely and efficiently. Banks, airlines, hospitals, online shops, and social networks all depend on databases that must answer queries in milliseconds, survive power failures without losing a committed transaction, and let thousands of users work at once without corrupting each other's changes.

This subject explains how that is achieved. It begins with why databases replaced ad hoc files, the three-schema architecture, and the relational model with its algebra. It then covers data modelling with entity-relationship diagrams and their translation into tables, keys and integrity constraints, and SQL in depth: filtering, grouping, subqueries, views, and joins. Normalization shows how to design schemas without redundancy. The later lessons look inside the engine: transactions and the ACID properties, serializability and two-phase locking, B+ tree indexes, query optimization, and crash recovery with write-ahead logging. The subject closes with NoSQL data models and the consistency trade-offs of distributed databases.

Every SQL example runs in Python's built-in SQLite engine, so each query and its result can be reproduced exactly.

## What you will learn
- Explain the advantages of a DBMS over file processing and the role of the three-schema architecture and data independence
- Describe relations, keys, and integrity constraints, and express queries in relational algebra
- Model a domain with entity-relationship diagrams and map the design to relational tables
- Write SQL queries with filtering, grouping, aggregation, subqueries, views, set operations, and joins
- Identify functional dependencies and normalize schemas to 3NF and BCNF
- Explain ACID transactions, test schedules for serializability, and apply two-phase locking
- Describe B+ tree indexes, query processing and optimization, and log-based crash recovery
- Compare NoSQL data models and reason about consistency with the CAP theorem

## Prerequisites
- Basic programming experience; the examples use Python
- Familiarity with sets and simple logic (and, or, not)
- Data structures such as trees and hash tables help for the indexing lessons

## Glossary
- **Relation**: a table; a set of tuples (rows) that share the same attributes (columns)
- **Schema**: the structure of a database, such as table names, columns, types, and constraints
- **Primary key**: an attribute set chosen to identify each tuple uniquely
- **Foreign key**: an attribute set whose values must match a key in another (or the same) relation
- **SQL**: the standard declarative language for defining, querying, and updating relational databases
- **Join**: an operation that combines tuples from two relations that satisfy a condition
- **Functional dependency**: a constraint $X \to Y$ stating that equal $X$ values imply equal $Y$ values
- **Normal form**: a condition on a schema, such as 3NF or BCNF, that limits redundancy
- **Transaction**: a sequence of operations treated as a single logical unit of work
- **ACID**: atomicity, consistency, isolation, and durability, the guarantees of a transaction
- **Serializable schedule**: an interleaving of transactions equivalent to some serial order
- **Two-phase locking**: a locking protocol in which a transaction acquires all its locks before releasing any
- **Index**: an auxiliary structure, such as a B+ tree, that speeds up finding rows by key
- **Query optimizer**: the component that chooses an efficient execution plan for a query
- **Write-ahead logging**: recording changes in a log before applying them to the database, so they can be redone or undone after a crash
- **CAP theorem**: a distributed system facing a network partition must choose between consistency and availability

## Further reading
- Abraham Silberschatz, Henry F. Korth, and S. Sudarshan, *Database System Concepts* (McGraw-Hill)
- Ramez Elmasri and Shamkant B. Navathe, *Fundamentals of Database Systems* (Pearson)
- Raghu Ramakrishnan and Johannes Gehrke, *Database Management Systems* (McGraw-Hill)
- C. J. Date, *An Introduction to Database Systems* (Addison-Wesley)
- Martin Kleppmann, *Designing Data-Intensive Applications* (O'Reilly)
