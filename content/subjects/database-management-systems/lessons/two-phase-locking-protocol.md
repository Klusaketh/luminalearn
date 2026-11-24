---
lesson: two-phase-locking-protocol
title: Two-Phase Locking (2PL) & Conflicts
summary: Maintain conflict serializability and concurrency control in database transactions using Two-Phase Locking protocols, growing and shrinking phases, and strict variations to eliminate cascading rollbacks.
minutes: 50
type: theory
objectives:
  - Explain how shared and exclusive locks prevent conflicting operations on database items
  - Prove why the Basic Two-Phase Locking protocol guarantees conflict serializability
  - Distinguish between Basic 2PL, Strict 2PL, and Rigorous 2PL
  - Analyze concurrent execution schedules to identify cascading rollbacks and deadlocks
review: ai-draft
---

## Introduction

Consider an e-commerce database executing two concurrent operations: Transaction $T_1$ transfers $\$50$ from account $A$ to account $B$, while Transaction $T_2$ calculates the total assets across accounts $A$ and $B$. If $T_2$ reads account $A$ after $T_1$ deducts $\$50$, but reads account $B$ before $T_1$ adds $\$50$, $T_2$ computes an incorrect total balance. This phenomenon—an **inconsistent read** caused by interleaved read and write operations—violates the isolation guarantee of database systems.

To preserve correctness, concurrent schedules must be **conflict serializable**, meaning they yield the same outcome as executing the transactions sequentially one after another. However, manually checking serializability by constructing precedence graphs at runtime is computationally prohibitive. Database engines require a real-time protocol that guarantees conflict serializability dynamically as transactions issue operations.

The **Two-Phase Locking (2PL)** protocol solves this challenge by requiring transactions to acquire and release lock permissions in two distinct, monotonic phases. This lesson covers lock modes, the rules governing Basic 2PL, the mathematical proof of its correctness, the problem of cascading rollbacks, and enhanced protocol variants such as Strict 2PL and Rigorous 2PL.

**Before you start:** you need a solid understanding of transaction states, conflict serializability, and conflict types (RW, WR, WW) from *ACID Properties & Transaction States* and *Schedules & Serializability*.

## Core theory

### Lock modes and compatibility

A transaction interacts with a data item (such as a table, page, or tuple) by acquiring a **lock** on that item before performing a read or write operation. The DBMS lock manager supports two primary lock modes:

1. **Shared lock ($S$):** Allows a transaction to read a data item. Multiple transactions can hold shared locks on the same item concurrently.
2. **Exclusive lock ($X$):** Allows a transaction to read and write a data item. Only one transaction can hold an exclusive lock on an item, and no other transaction may hold any lock ($S$ or $X$) on that item simultaneously.

The interaction between requested locks and currently held locks is defined by a **compatibility matrix**:

| Held \ Requested | Shared ($S$) | Exclusive ($X$) |
| :--- | :--- | :--- |
| **Shared ($S$)** | Compatible | Incompatible |
| **Exclusive ($X$)** | Incompatible | Incompatible |

Two operations conflict if they belong to different transactions, access the same data item, and at least one of them is a write. The compatibility matrix mirrors this rule: shared access allows concurrent reads (read-read does not conflict), whereas exclusive access blocks concurrent reads and writes (write-read, read-write, and write-write conflict).

### The Basic Two-Phase Locking (2PL) protocol

The **Two-Phase Locking (2PL)** protocol imposes a simple rule on every transaction: once a transaction releases any lock, it can no longer acquire any new locks. This splits the lifecycle of every transaction into two separate phases:

1. **Growing phase:** The transaction may acquire new locks and upgrade existing shared locks to exclusive locks. It cannot release any locks.
2. **Shrinking phase:** The transaction may release held locks and downgrade exclusive locks to shared locks. It cannot acquire any new locks.

The moment a transaction releases its first lock marks its **lock point**. The lock point is the precise instant when the transaction holds its maximum set of lock permissions.

```mermaid
flowchart LR
    Unlocked[Unlocked State] -->|Acquire S or X Locks| Growing[Growing Phase]
    Growing -->|Reach Max Locks| LockPoint[Lock Point]
    LockPoint -->|Release First Lock| Shrinking[Shrinking Phase]
    Shrinking -->|Release All Locks| Finished[Finished]
```

If a requested lock is unavailable because another transaction holds an incompatible lock, the requesting transaction enters a waiting state until the lock is released.

### Proof outline of conflict serializability

Basic 2PL guarantees that any interleaved schedule of compliant transactions is conflict serializable. We can prove this theorem using a precedence graph (also known as a serialization graph) $G = (V, E)$.

Let $V = \{T_1, T_2, \dots, T_n\}$ be the set of transactions in a schedule $S$. A directed edge $T_i \to T_j$ exists in $G$ if $T_i$ executes an operation $o_i(A)$ that conflicts with a subsequent operation $o_j(A)$ executed by $T_j$.

1. Because $o_i(A)$ and $o_j(A)$ conflict, $T_i$ and $T_j$ must acquire conflicting locks on item $A$.
2. $T_i$ must acquire its lock, execute $o_i(A)$, and release its lock on $A$ **before** $T_j$ can acquire its lock on $A$ and execute $o_j(A)$.
3. Under 2PL, $T_i$ releases its lock on $A$ during or after its growing phase, which occurs no later than its lock point $\text{LP}(T_i)$.
4. $T_j$ acquires its lock on $A$ during its growing phase, which occurs no earlier than its first lock acquisition and no later than its lock point $\text{LP}(T_j)$.
5. Therefore, an edge $T_i \to T_j$ in the precedence graph implies:

$$\text{LP}(T_i) < \text{LP}(T_j)$$

6. If the precedence graph contained a cycle $T_1 \to T_2 \to \dots \to T_k \to T_1$, summing these inequalities would yield:

$$\text{LP}(T_1) < \text{LP}(T_2) < \dots < \text{LP}(T_k) < \text{LP}(T_1)$$

This implies $\text{LP}(T_1) < \text{LP}(T_1)$, an absolute mathematical contradiction. Thus, the precedence graph $G$ is acyclic, proving that every Basic 2PL schedule is conflict serializable. Sorting transactions by their lock points yields an equivalent serial execution order.

### Recoverability and cascading rollbacks

While Basic 2PL guarantees serializability, it does not prevent transactional anomalies related to failure recovery.

A **dirty read** occurs when transaction $T_2$ reads data modified by transaction $T_1$ before $T_1$ commits. If $T_1$ releases an exclusive lock during its shrinking phase and subsequently aborts, $T_2$ has read invalid state. To maintain atomicity, $T_2$ must also be aborted.

```text
T1:  write_lock(A) -> write(A) -> unlock(A) -----------------------> ABORT
T2:                                 write_lock(A) -> read(A) -> COMMIT
```

When aborting one transaction forces the abort of other uncommitted transactions, the system suffers a **cascading rollback** (or **cascading abort**). Cascading rollbacks waste CPU and I/O resources, introduce unpredictability into system latency, and require complex undo logging structures.

### Strict 2PL and Rigorous 2PL

To avoid cascading rollbacks, database systems extend Basic 2PL with stricter rules regarding lock release timing.

1. **Strict 2PL (S2PL):**
   - Transactions follow the standard growing phase rules.
   - All **exclusive locks ($X$)** acquired by a transaction must be held until the transaction completes (either `COMMIT` or `ABORT`).
   - Shared locks ($S$) may be released during a shrinking phase prior to commit.
   - **Properties:** Guarantees conflict serializability and ensures schedules are **cascadeless** (avoiding cascading rollbacks).

2. **Rigorous 2PL (SS2PL / Strong 2PL):**
   - All locks—both **shared ($S$)** and **exclusive ($X$)**—must be held until the transaction completes (`COMMIT` or `ABORT`).
   - The shrinking phase shrinks instantly to zero duration at transaction completion.
   - **Properties:** Guarantees conflict serializability, avoids cascading rollbacks, and ensures that the serialization order matches the exact commit order of transactions.

| Protocol Variant | Releases Shared Locks | Releases Exclusive Locks | Prevents Cascading Aborts? |
| :--- | :--- | :--- | :--- |
| **Basic 2PL** | During shrinking phase | During shrinking phase | No |
| **Strict 2PL** | During shrinking phase | At Commit / Abort | Yes |
| **Rigorous 2PL** | At Commit / Abort | At Commit / Abort | Yes |

### Lock conversions: Upgrades and downgrades

To maximize concurrency, protocols allow transactions to refine lock modes through **lock conversion**:

- **Lock upgrade:** Converting a held shared lock to an exclusive lock ($S \to X$). This can only occur during the **growing phase**.
- **Lock downgrade:** Converting a held exclusive lock to a shared lock ($X \to S$). This counts as a partial release and can only occur during the **shrinking phase**.

Upgrading locks introduces a risk of deadlock. If $T_1$ and $T_2$ both hold $S(A)$ and both issue an upgrade request to $X(A)$, both transactions block indefinitely, waiting for the other to release $S(A)$.

## Worked examples

### Example 1: Validating Basic 2PL compliance in Python

The following program tracks lock requests and releases across multiple transactions to verify compliance with the Basic 2PL protocol.

```python
class LockManager2PL:
    def __init__(self):
        # Maps transaction ID to phase: 'GROWING' or 'SHRINKING'
        self.tx_phase = {}
        # Maps transaction ID to set of held items
        self.held_locks = {}

    def process_op(self, tx_id, op_type, item):
        if tx_id not in self.tx_phase:
            self.tx_phase[tx_id] = 'GROWING'
            self.held_locks[tx_id] = set()

        if op_type in ('LOCK_S', 'LOCK_X'):
            if self.tx_phase[tx_id] == 'SHRINKING':
                return False, f"T{tx_id} requested {op_type}({item}) during SHRINKING phase!"
            self.held_locks[tx_id].add(item)
            return True, f"T{tx_id} acquired {op_type}({item}) [Phase: GROWING]"

        elif op_type == 'UNLOCK':
            if item in self.held_locks[tx_id]:
                self.held_locks[tx_id].remove(item)
                if self.tx_phase[tx_id] == 'GROWING':
                    self.tx_phase[tx_id] = 'SHRINKING'
                return True, f"T{tx_id} released UNLOCK({item}) [Phase: SHRINKING]"
            return False, f"T{tx_id} does not hold lock on {item}"

lm = LockManager2PL()

schedule = [
    (1, 'LOCK_S', 'A'),
    (2, 'LOCK_X', 'B'),
    (1, 'LOCK_X', 'C'),
    (1, 'UNLOCK', 'A'),  # T1 enters SHRINKING phase
    (2, 'UNLOCK', 'B'),  # T2 enters SHRINKING phase
    (1, 'LOCK_S', 'B'),  # Illegal! T1 attempts lock in SHRINKING phase
]

for tx, op, item in schedule:
    success, msg = lm.process_op(tx, op, item)
    print(f"Step: T{tx} {op:8s} {item} -> {msg}")
    if not success:
        print("Schedule violates Basic 2PL!")
        break
```

Output:

```text
Step: T1 LOCK_S   A -> T1 acquired LOCK_S(A) [Phase: GROWING]
Step: T2 LOCK_X   B -> T2 acquired LOCK_X(B) [Phase: GROWING]
Step: T1 LOCK_X   C -> T1 acquired LOCK_X(C) [Phase: GROWING]
Step: T1 UNLOCK   A -> T1 released UNLOCK(A) [Phase: SHRINKING]
Step: T2 UNLOCK   B -> T2 released UNLOCK(B) [Phase: SHRINKING]
Step: T1 LOCK_S   B -> T1 requested LOCK_S(B) during SHRINKING phase!
Schedule violates Basic 2PL!
```

### Example 2: Cascading rollback analysis under Basic 2PL vs. Strict 2PL

Consider three transactions ($T_1, T_2, T_3$) operating on item $A$.

- $T_1$ modifies $A$.
- $T_2$ reads $A$ and adds $10$.
- $T_3$ reads $A$ and multiplies by $2$.

#### Execution under Basic 2PL
1. $T_1$ acquires $X(A)$, performs $write(A)$, and releases $X(A)$ immediately (entering shrinking phase).
2. $T_2$ acquires $S(A)$, performs $read(A)$, writes updated $A$, and releases $S(A)$.
3. $T_3$ acquires $S(A)$, performs $read(A)$, writes updated $A$, and releases $S(A)$.
4. $T_1$ encounters an internal arithmetic error and issues an `ABORT`.

**Resulting behavior:**
Because $T_1$ aborted, its write to $A$ must be reverted. However, $T_2$ read $T_1$'s dirty write, and $T_3$ read $T_2$'s subsequent dirty write. The system must issue a **cascading rollback**, aborting $T_2$ and $T_3$ in cascade:

$$\text{Abort}(T_1) \implies \text{Abort}(T_2) \implies \text{Abort}(T_3)$$

#### Execution under Strict 2PL
1. $T_1$ acquires $X(A)$ and performs $write(A)$.
2. $T_2$ requests $S(A)$ but is blocked because $T_1$ holds $X(A)$ until completion.
3. $T_3$ requests $S(A)$ and is also blocked behind $T_1$.
4. $T_1$ issues `ABORT`. $T_1$'s changes are rolled back, and $X(A)$ is released.
5. $T_2$ acquires $S(A)$ and reads the original, uncorrupted pre-transaction state of $A$.

**Resulting behavior:**
Cascading rollbacks are completely prevented. $T_2$ and $T_3$ complete successfully without reading dirty data.

## Applications

- **Relational Database Management Systems (RDBMS):** Engines like PostgreSQL, MySQL (InnoDB), and Microsoft SQL Server use locking mechanisms (such as Strict 2PL) to enforce serializable isolation levels and lock data rows, pages, or tables during concurrent operations.
- **Distributed Databases & Two-Phase Commit (2PC):** Distributed transactional databases combine Strict 2PL with the Two-Phase Commit protocol to ensure both global data serializability and global atomic agreement across node clusters.
- **Financial Transaction Processing:** Core banking ledgers use Rigorous 2PL to guarantee that concurrent fund transfers, balance audits, and high-frequency deposits yield consistent balance totals that preserve transaction commit order.
- **In-Memory Key-Value Stores:** High-throughput transactional data stores apply row-level 2PL combined with lock upgrading to manage concurrent read-heavy and write-heavy workloads without data corruption.

## Common mistakes

- **Confusing 2PL with Two-Phase Commit (2PC).** Why it is wrong and how to avoid it: Two-Phase Locking (2PL) is a *concurrency control protocol* that manages transaction locks in growing and shrinking phases. Two-Phase Commit (2PC) is an *atomic commitment protocol* that ensures distributed nodes agree to commit or abort a transaction.
- **Assuming Basic 2PL prevents deadlocks.** Why it is wrong and how to avoid it: 2PL guarantees conflict serializability, not deadlock freedom. Cyclic wait conditions (such as $T_1$ holding lock $A$ waiting for $B$, while $T_2$ holds lock $B$ waiting for $A$) can easily occur in 2PL. Deadlocks must be handled separately using prevention schemes (e.g., Wait-Die, Wound-Wait) or detection mechanisms (e.g., wait-for graphs).
- **Believing Strict 2PL holds shared locks until commit.** Why it is wrong and how to avoid it: Strict 2PL requires holding only *exclusive locks ($X$)* until commit or abort. Shared locks ($S$) can be released during the shrinking phase. Holding both $S$ and $X$ locks until commit is required by *Rigorous 2PL*.
- **Assuming lock release can happen anytime during the growing phase.** Why it is wrong and how to avoid it: Releasing any lock immediately terminates the growing phase and transitions the transaction into the shrinking phase. Any subsequent lock request violates the protocol.

## Revision notes

- **Lock modes:** Shared ($S$) locks allow concurrent readers. Exclusive ($X$) locks block all other readers and writers.
- **Basic 2PL rule:** No lock can be acquired after any lock has been released.
- **Two phases:**
  - *Growing phase:* Acquiring locks, upgrading $S \to X$. No locks released.
  - *Shrinking phase:* Releasing locks, downgrading $X \to S$. No locks acquired.
- **Lock point:** The instant when a transaction holds its maximum number of locks.
- **Serializability guarantee:** Basic 2PL guarantees conflict serializability. The equivalent serial schedule is ordered by transaction lock points.
- **Cascading rollbacks:** Basic 2PL permits dirty reads, which can trigger cascading aborts if an uncommitted transaction aborts after releasing exclusive locks.
- **Strict 2PL:** Holds all $X$ locks until `COMMIT` or `ABORT`. Guarantees serializability and eliminates cascading rollbacks (cascadeless).
- **Rigorous 2PL:** Holds all locks ($S$ and $X$) until `COMMIT` or `ABORT`. Serializability order matches commit order.

## Practice questions

:::question basic
A transaction executes the following sequence of lock operations: `LOCK_S(A)`, `LOCK_X(B)`, `UNLOCK(A)`, `LOCK_S(C)`, `UNLOCK(B)`, `UNLOCK(C)`. Does this transaction follow the Basic Two-Phase Locking protocol? Explain why or why not.
:::answer
No, the transaction violates the Basic 2PL protocol. Releasing lock `A` at step 3 transitions the transaction into its shrinking phase. Requesting `LOCK_S(C)` at step 4 violates the fundamental 2PL rule that prohibits acquiring new locks once any lock has been released.
:::

:::question basic
What is a lock point, and how does it determine the equivalent serial execution order of a group of 2PL transactions?
:::answer
The lock point is the precise moment in time when a transaction acquires its final lock (or releases its first lock), representing the peak number of locks held. In a conflict serializable 2PL schedule, topological sorting of the precedence graph yields an ordering identical to sorting transactions chronologically by their lock points.
:::

:::question intermediate
Explain why Strict 2PL prevents cascading rollbacks, whereas Basic 2PL does not.
:::answer
Basic 2PL permits a transaction $T_1$ to release an exclusive lock on item $A$ during its shrinking phase while $T_1$ is still uncommitted. If another transaction $T_2$ reads the uncommitted value written by $T_1$ and $T_1$ subsequently aborts, $T_2$ must also be aborted (a cascading rollback). Strict 2PL holds all exclusive locks until transaction completion (`COMMIT` or `ABORT`), ensuring that no transaction ever reads uncommitted data (dirty reads), thereby preventing cascading rollbacks completely.
:::

:::question intermediate
Consider two transactions $T_1$ and $T_2$ running under Basic 2PL. $T_1$ holds a shared lock $S(A)$ and requests an upgrade to $X(A)$. Simultaneously, $T_2$ holds $S(A)$ and requests an upgrade to $X(A)$. Describe the outcome and identify the problem.
:::answer
A deadlock occurs. $T_1$ cannot upgrade to $X(A)$ because $T_2$ holds an incompatible $S(A)$ lock on $A$. Similarly, $T_2$ cannot upgrade to $X(A)$ because $T_1$ holds $S(A)$. Both transactions enter an indefinite wait state, blocking each other. This demonstrates that Two-Phase Locking does not prevent deadlocks.
:::

:::question advanced
Prove that if every transaction in a schedule obeys Basic 2PL, the precedence graph $G$ contains no directed cycles.
:::answer
Suppose $G$ contains a directed cycle $T_1 \to T_2 \to \dots \to T_k \to T_1$. A directed edge $T_i \to T_j$ implies that $T_i$ released a lock on a shared data item before $T_j$ acquired a conflicting lock on that same item. Under 2PL, $T_i$ releases locks no earlier than its lock point $\text{LP}(T_i)$, and $T_j$ acquires locks no later than its lock point $\text{LP}(T_j)$, establishing the inequality $\text{LP}(T_i) < \text{LP}(T_j)$. Following the cycle yields $\text{LP}(T_1) < \text{LP}(T_2) < \dots < \text{LP}(T_k) < \text{LP}(T_1)$, which reduces to $\text{LP}(T_1) < \text{LP}(T_1)$. This is impossible, proving by contradiction that $G$ cannot contain cycles.
:::

:::question advanced
Compare Rigorous 2PL with Strict 2PL in terms of concurrency level and commitment ordering. Why would a database system select Strict 2PL over Rigorous 2PL?
:::answer
Rigorous 2PL holds both shared ($S$) and exclusive ($X$) locks until transaction commit/abort, forcing the serialization order to match the commit order. Strict 2PL holds only exclusive ($X$) locks until commit/abort, allowing shared ($S$) locks to be released early during the shrinking phase. A database engine might choose Strict 2PL because releasing shared locks earlier allows long-running read-only operations to unlock data sooner, enabling concurrent write transactions to proceed and increasing overall system throughput without sacrificing recoverability.
:::

## Further learning

- **Next:** *Write-Ahead Logging & Checkpoints* explores how atomic transaction state changes and undo/redo operations are recorded on persistent storage during recovery.
- **Related:** *Schedules & Serializability* covers precedence graphs, conflict equivalence, and view serializability in concurrent execution.
- **Related:** *B+ Tree Index Structures* details high-performance index locking schemes (such as lock-crabbing/latching) used during concurrent tree traversals.
- **Textbook:** Silberschatz, Korth, and Sudarshan, *Database System Concepts*.
