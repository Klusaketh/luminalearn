---
lesson: deadlock-characterization
title: Deadlock Characterization and Prevention
summary: The four necessary conditions for deadlock, resource-allocation graphs, the main strategies for handling deadlock, and how to prevent it by breaking a condition, especially with lock ordering.
minutes: 40
type: theory
objectives:
  - Define deadlock and state the four necessary conditions - mutual exclusion, hold and wait, no preemption, and circular wait
  - Draw and interpret resource-allocation graphs, distinguishing single-instance from multiple-instance resources
  - Compare the strategies of prevention, avoidance, detection and recovery, and ignoring deadlocks
  - Prevent deadlock by breaking one of the conditions, and prove that a global lock order rules out circular wait
---

## Introduction

Two cars meet on a narrow bridge from opposite ends. Neither can move forward, and neither will back up. Each is waiting for the other, and the wait will never end. Computer systems have the same problem. Thread A holds the lock on account 1 and wants account 2; thread B holds account 2 and wants account 1. Neither will release what it holds until it gets what it wants. Both are stuck forever, and anything that later needs either account gets stuck too.

This is a **deadlock**. It does not crash the program or produce wrong answers; the program simply stops making progress, often only under rare timing, which makes it hard to reproduce. This lesson identifies precisely when deadlock can happen, introduces a graph model for reasoning about it, surveys the strategies systems use, and shows how to design programs in which deadlock is impossible.

**Before you start:** you should know mutexes, semaphores, and the dining-philosophers problem.

## Core theory

### The system model

A system has resources of several **types** (locks, memory, printers, database rows), each with one or more identical **instances**. A process uses a resource in three steps: **request** it (waiting if it is unavailable), **use** it, and **release** it.

A set of processes is **deadlocked** when every process in the set is waiting for an event, typically the release of a resource, that only another process in the set can cause.

### Four necessary conditions

Coffman, Elphick, and Shoshani (1971) showed that deadlock can arise only if all four of these hold at the same time:

1. **Mutual exclusion:** at least one resource is non-sharable; only one process can use it at a time.
2. **Hold and wait:** a process holds at least one resource while waiting to acquire others.
3. **No preemption:** a resource cannot be taken away from a process; it is released only voluntarily.
4. **Circular wait:** there is a cycle of processes $P_0, P_1, \dots, P_n$ in which each $P_i$ waits for a resource held by $P_{i+1}$, and $P_n$ waits for one held by $P_0$.

These are **necessary** conditions: if any one is absent, deadlock is impossible. That observation is the basis of deadlock prevention.

### Resource-allocation graphs

A **resource-allocation graph** has a node for each process (circle) and each resource type (rectangle, with a dot per instance), and two kinds of edges:

- a **request edge** $P \to R$: process $P$ is waiting for an instance of $R$;
- an **assignment edge** $R \to P$: an instance of $R$ is held by $P$.

The graph tells us:

- **No cycle → no deadlock.**
- **A cycle, and every resource in it has a single instance → deadlock.** The cycle is exactly a circular wait.
- **A cycle with multiple-instance resources → possibly a deadlock.** Another process outside the cycle might release an instance and break it.

When every resource has one instance, we can simplify the graph to a **wait-for graph** over processes only, with an edge $P_i \to P_j$ when $P_i$ waits for a resource held by $P_j$. Deadlock is then exactly a cycle in the wait-for graph.

### Four strategies

| Strategy | Idea | Cost |
| :--- | :--- | :--- |
| Prevention | design the system so that one of the four conditions can never hold | may reduce resource utilization or concurrency |
| Avoidance | before granting a request, check that the system stays in a safe state (banker's algorithm) | needs advance knowledge of maximum demands; run-time checks |
| Detection and recovery | let deadlocks happen, detect cycles periodically, then break them | detection overhead; recovery may lose work |
| Ignoring | assume deadlocks are rare and let the user or administrator restart things | no overhead, but deadlocks are not handled |

General-purpose operating systems largely **ignore** deadlocks among user programs (sometimes called the "ostrich algorithm"), leaving prevention to application designers, while databases routinely use **detection** and abort a victim transaction.

### Prevention: breaking each condition

- **Mutual exclusion:** make resources sharable where possible (read-only files, or a print spooler that queues jobs so that no process holds the printer directly). Many resources, such as locks, are inherently non-sharable, so this rarely helps.
- **Hold and wait:** require a process to request **all** its resources at once, or to release everything it holds before requesting more. This wastes resources (they are held long before they are needed) and can starve processes that need many popular resources.
- **No preemption:** if a process holding resources requests one that is unavailable, it must release what it holds and retry later; or the system may preempt resources from waiting processes. This works for resources whose state can be saved and restored, such as CPU registers and memory pages, but not for locks protecting half-updated data or a half-printed page.
- **Circular wait:** impose a **total order** on resource types and require every process to request resources in increasing order. This is the most practical method, known in software as **lock ordering**.

**Why ordering works.** Number the resources with a function $F$. Suppose a circular wait existed: $P_0$ waits for $R_0$ held by $P_1$, $P_1$ waits for $R_1$ held by $P_2$, ..., $P_n$ waits for $R_n$ held by $P_0$. Since $P_{i+1}$ holds $R_i$ while requesting $R_{i+1}$, the ordering rule gives $F(R_i) < F(R_{i+1})$ for every $i$, and since $P_0$ holds $R_n$ while requesting $R_0$, also $F(R_n) < F(R_0)$. Chaining these gives $F(R_0) < F(R_1) < \dots < F(R_n) < F(R_0)$, which is impossible.

### Deadlock, livelock, and starvation

- In a **deadlock**, processes are blocked and do nothing.
- In a **livelock**, processes keep running but make no progress, for example two threads that repeatedly release their locks and retry in lockstep, like two people stepping aside in a corridor in the same direction again and again.
- In **starvation**, some processes make progress but one is postponed indefinitely.

## Worked examples

### Example 1: Finding a deadlock in a resource-allocation graph

Each resource below has a single instance. P1 holds R1 and requests R2; P2 holds R2 and requests R3; P3 holds R3 and requests R1; P4 requests R1.

```python
def find_cycle(graph):
    color, path = {}, []

    def visit(node):
        color[node] = "grey"                    # on the current path
        path.append(node)
        for nxt in graph.get(node, []):
            if color.get(nxt) == "grey":
                return path[path.index(nxt):] + [nxt]
            if nxt not in color:
                cycle = visit(nxt)
                if cycle:
                    return cycle
        color[node] = "black"
        path.pop()
        return None

    for node in graph:
        if node not in color:
            cycle = visit(node)
            if cycle:
                return cycle
    return None

# request edges P -> R and assignment edges R -> P
graph = {
    "P1": ["R2"], "P2": ["R3"], "P3": ["R1"], "P4": ["R1"],
    "R1": ["P1"], "R2": ["P2"], "R3": ["P3"],
}
print(" -> ".join(find_cycle(graph)))

graph["P3"] = []                                # P3 no longer waits for R1
print(find_cycle(graph))
```

Output:

```text
P1 -> R2 -> P2 -> R3 -> P3 -> R1 -> P1
None
```

The cycle P1 → R2 → P2 → R3 → P3 → R1 → P1 is a circular wait, and because every resource has one instance, P1, P2, and P3 are deadlocked. P4 is not part of the cycle, but it is stuck too, waiting for R1 forever. If P3 is not waiting for anything, the graph has no cycle: P3 can finish and release R3, then P2 can finish, then P1, and finally P4 gets R1.

### Example 2: A cycle without deadlock

With multiple instances, a cycle is not enough. Suppose R1 and R2 each have **two** instances:

| Process | Holds | Requests |
| :--- | :--- | :--- |
| P1 | one instance of R2 | R1 |
| P2 | one instance of R1 | nothing |
| P3 | one instance of R1 | R2 |
| P4 | one instance of R2 | nothing |

The graph contains the cycle P1 → R1 → P3 → R2 → P1. But P2 and P4 are not waiting for anything. When P4 finishes and releases its instance of R2, P3's request can be granted; when P2 releases R1, P1 can proceed. There is no deadlock, because processes outside the cycle hold instances that will be released.

### Example 3: Preventing deadlock with a lock order

Transfers between bank accounts must lock both accounts. If each thread locks the source account and then the destination, a transfer from A to B and one from B to A can deadlock. Locking in a fixed global order, by account number, makes that impossible.

```python
import threading

class Account:
    def __init__(self, number, balance):
        self.number, self.balance = number, balance
        self.lock = threading.Lock()

def transfer(source, target, amount):
    first, second = sorted((source, target), key=lambda acc: acc.number)   # global lock order
    with first.lock:
        with second.lock:
            source.balance -= amount
            target.balance += amount

a, b, c = Account(1, 1000), Account(2, 1000), Account(3, 1000)
jobs = [(a, b, 10), (b, c, 10), (c, a, 5), (b, a, 2)] * 100
threads = [threading.Thread(target=transfer, args=job) for job in jobs]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(a.balance, b.balance, c.balance, "total", a.balance + b.balance + c.balance)
```

Output:

```text
700 800 1500 total 3000
```

All 400 transfers complete, and the total stays 3000. In each round of four transfers, account 1 loses 10 and gains 7 (net $-3$), account 2 gains 10 and loses 12 (net $-2$), and account 3 gains 10 and loses 5 (net $+5$), so after 100 rounds the balances are 700, 800, and 1500. The transfers 1 → 2, 2 → 3, and 3 → 1 could form a three-way circular wait if each thread locked its source account first. With the global order, every thread locks the lower-numbered account first, so no thread ever holds a higher-numbered lock while waiting for a lower-numbered one, and a cycle of waits cannot form.

## Applications

- **Lock ordering in large systems:** operating system kernels and databases document a global order for their internal locks, and tools such as Linux's `lockdep` report violations.
- **Database systems** detect deadlocks among transactions using wait-for graphs and abort one victim; the application simply retries.
- **Spooling** makes printers effectively sharable: processes write jobs to a queue, and only the spooler uses the device.
- **Timeouts** on lock acquisition (as in `try_lock` with a deadline) break hold-and-wait in practice by making a thread give up and release what it holds.
- **Distributed systems** face deadlocks across machines, such as two services each waiting for the other's reply, and use timeouts and ordering for the same reasons.

## Common mistakes

- **Treating a cycle as proof of deadlock when resources have several instances.** It is proof only when every resource in the cycle has a single instance.
- **Thinking that breaking one condition at one moment is enough.** Prevention requires that the chosen condition can never hold anywhere in the system.
- **Ordering locks inconsistently,** such as by source and destination rather than by a fixed key, which still allows circular wait.
- **Confusing deadlock with starvation or livelock.** Deadlocked processes wait forever; starving processes are passed over; livelocked processes are busy but make no progress.
- **Releasing and retrying without randomness,** which can turn a deadlock into a livelock.

## Revision notes

- Deadlock: every process in a set waits for an event only another member can cause.
- Necessary conditions: mutual exclusion, hold and wait, no preemption, circular wait. All four must hold.
- Resource-allocation graph: request edges $P \to R$, assignment edges $R \to P$. No cycle → no deadlock; cycle with single instances → deadlock; cycle with multiple instances → maybe.
- Strategies: prevention, avoidance (banker's algorithm), detection and recovery, ignoring.
- Prevention: request all resources at once (no hold and wait), preempt (no "no preemption"), or order resources (no circular wait).
- Lock ordering is the most practical prevention technique, and its correctness follows from a simple contradiction argument.

## Practice questions

:::question basic
List the four necessary conditions for deadlock.
:::answer
Mutual exclusion (some resource can be used by only one process at a time), hold and wait (a process holds resources while waiting for more), no preemption (resources are released only voluntarily), and circular wait (a cycle of processes, each waiting for a resource held by the next).
:::

:::question basic
In a resource-allocation graph where every resource type has exactly one instance, what does a cycle mean?
:::answer
It means a deadlock exists. With single instances, each request edge in the cycle points to a resource held by the next process in the cycle, and no other instance can satisfy any of those requests, so each process waits for the next forever. The processes on the cycle are deadlocked.
:::

:::question intermediate
A process must acquire a scanner, a printer, and a disk file. Explain how requesting all three at once prevents deadlock, and give two disadvantages.
:::answer
If a process must obtain all its resources in a single request before it starts, it never holds some resources while waiting for others, so the hold-and-wait condition cannot occur, and deadlock is impossible. Disadvantages: resources are held for long periods without being used (the printer is reserved while the process scans for an hour), lowering utilization; and a process that needs several popular resources may wait a very long time until all of them happen to be free at once, which risks starvation. It also requires knowing all needs in advance.
:::

:::question intermediate
Two threads run `lock(A); lock(B); ...` and `lock(B); lock(A); ...` respectively. Describe an interleaving that deadlocks, and fix the code.
:::answer
Thread 1 locks A; thread 2 locks B; thread 1 now tries to lock B and blocks; thread 2 tries to lock A and blocks. Each holds what the other needs, and all four conditions hold. Fix: impose a global order, for example "A before B", and make both threads lock A first, then B. Now whichever thread locks A first can always get B as well, and circular wait is impossible.
:::

:::question intermediate
Why is preempting resources a workable prevention method for memory but not for a mutex protecting a linked list?
:::answer
A memory page can be taken from a process by saving its contents to disk and restored later, so the process can continue as if nothing happened. A mutex protects data that may be halfway through an update, such as a linked list with one pointer changed and another not yet changed. Taking the mutex away and giving it to another thread would expose the inconsistent list, corrupting the data structure. Resources can be preempted only if their state can be saved and restored safely.
:::

:::question advanced
Prove that if every process requests resources in strictly increasing order of a numbering $F$, no circular wait can occur.
:::answer
Assume a circular wait exists: processes $P_0, \dots, P_n$, where $P_i$ waits for resource $R_i$ held by $P_{i+1}$, and $P_n$ waits for $R_n$ held by $P_0$ (indices modulo $n + 1$). Process $P_{i+1}$ holds $R_i$ and is requesting $R_{i+1}$. Because it requests in increasing order, every resource it holds has a smaller number than the one it requests, so $F(R_i) < F(R_{i+1})$. Applying this around the cycle gives $F(R_0) < F(R_1) < \dots < F(R_n) < F(R_0)$, so $F(R_0) < F(R_0)$, a contradiction. Therefore no circular wait exists, and since circular wait is necessary, no deadlock can occur.
:::

## Further learning

- **Next:** *Banker's Algorithm & Avoidance* grants requests only when the system provably stays safe.
- **Related:** *Deadlock Detection & Recovery* finds and breaks deadlocks after they occur.
- **Related:** *Semaphores & Condition Variables* applies lock ordering to the dining philosophers.
