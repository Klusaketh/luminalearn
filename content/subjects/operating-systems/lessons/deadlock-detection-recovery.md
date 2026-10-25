---
lesson: deadlock-detection-recovery
title: Deadlock Detection and Recovery
summary: Let deadlocks happen and then find them, with cycle detection in wait-for graphs for single-instance resources and a detection algorithm for multiple instances, and recover by terminating processes or preempting resources.
minutes: 45
type: theory
objectives:
  - Detect deadlock in single-instance systems by finding a cycle in a wait-for graph
  - Run the multiple-instance detection algorithm with Available, Allocation, and Request matrices
  - Decide how often to invoke detection by weighing its cost against the cost of undetected deadlocks
  - Recover from deadlock by process termination or resource preemption, choosing victims and avoiding starvation
---

## Introduction

Prevention and avoidance stop deadlocks before they happen, but both have costs: prevention restricts how programs may request resources, and avoidance needs advance knowledge of every process's maximum needs. Many systems take a third approach. They allow processes to request resources freely, accept that a deadlock may occasionally form, and run an algorithm that **detects** it and then **recovers** by breaking it.

This is how database systems handle the locks that transactions hold on rows and tables: deadlocks among transactions are not rare, and the database simply finds them and aborts one transaction, which the application retries. Detection is also how operating systems and debugging tools diagnose hung programs. This lesson presents the detection algorithms for single-instance and multiple-instance resources, the question of when to run them, and the options for recovery.

**Before you start:** you should know the four deadlock conditions, resource-allocation graphs, and the banker's safety algorithm.

## Core theory

### Single instance of each resource: wait-for graphs

If every resource type has one instance, collapse the resource-allocation graph into a **wait-for graph**: a node per process, and an edge $P_i \to P_j$ when $P_i$ waits for a resource that $P_j$ holds. The system is deadlocked **if and only if** the wait-for graph has a cycle, and the processes on the cycle are the deadlocked ones (along with anything waiting on them).

Detecting a cycle with depth-first search takes $O(n + e)$ time for $n$ processes and $e$ edges, which is at most $O(n^2)$.

### Multiple instances: the detection algorithm

With several instances per resource type, a cycle is not enough, so we use an algorithm shaped like the banker's safety check, but with **current requests** instead of maximum needs:

| Structure | Meaning |
| :--- | :--- |
| Available | free instances of each type |
| Allocation | what each process holds |
| Request | what each process is waiting for right now |

1. `Work = Available`. For each process, set `Finish[i] = true` if its Allocation is zero (a process holding nothing cannot be part of a deadlock), otherwise `false`.
2. Find an $i$ with `Finish[i] = false` and $\text{Request}_i \le \text{Work}$. If none exists, go to step 4.
3. `Work = Work + Allocation_i`; `Finish[i] = true`; go back to step 2.
4. Every process with `Finish[i] = false` is **deadlocked**.

Step 3 is **optimistic**: it assumes that a process whose current request can be met will finish and release everything without asking for more. If that assumption is wrong, the process will be blocked again and a later run of the algorithm will catch it. The algorithm runs in $O(m \cdot n^2)$ time for $m$ resource types.

The difference from the banker's algorithm is important: the banker's algorithm asks "could things go wrong in the future?" using Need, while detection asks "are things already stuck?" using Request.

### When to run detection

- **On every request that cannot be granted immediately:** deadlocks are detected the moment they form, and the request that closed the cycle is known, but the overhead is high.
- **Periodically**, for example every few minutes, or **when CPU utilization drops** below some threshold (a deadlock idles the processes involved): cheaper, but deadlocks persist until the next check, and many cycles may have tangled together, making it harder to say which request caused them.

### Recovery by process termination

- **Abort all deadlocked processes:** simple and certain, but expensive, since every one of them loses its work.
- **Abort one process at a time** until the cycle is broken, rerunning detection after each abort: less work is lost, but detection runs repeatedly.

Choosing a **victim** to minimise cost considers:

- the process's priority;
- how long it has run and how much longer it needs;
- how many and what kinds of resources it holds (easy-to-preempt ones are better to reclaim);
- how many more resources it needs to finish;
- whether it is interactive or batch.

Aborting a process in the middle of updating a file can leave the file inconsistent, so termination works best for processes whose effects can be undone, such as database transactions, which are **rolled back** atomically.

### Recovery by resource preemption

Take resources away from some processes and give them to others until the cycle is broken. Three issues arise:

1. **Selecting a victim:** which resources from which processes, to minimise cost.
2. **Rollback:** a process that loses a resource cannot simply continue. It must be rolled back to some safe earlier state, either a **total rollback** (restart it) or a **partial rollback** to a **checkpoint**, which requires the system to have saved checkpoints.
3. **Starvation:** if the same process is always chosen as the victim, it may never finish. Including the number of times a process has been rolled back in the cost factor prevents this.

## Worked examples

### Example 1: A wait-for graph

Processes P1 to P5 wait for one another as follows: P1 waits for P2, P2 for P3, P3 for P4, P4 for P2, and P5 for P1.

```python
def find_cycle(wait_for):
    color, path = {}, []

    def visit(p):
        color[p] = "grey"                     # on the current search path
        path.append(p)
        for q in wait_for.get(p, []):
            if color.get(q) == "grey":
                return path[path.index(q):] + [q]
            if q not in color:
                found = visit(q)
                if found:
                    return found
        color[p] = "black"
        path.pop()
        return None

    for p in wait_for:
        if p not in color:
            found = visit(p)
            if found:
                return found
    return None

print(find_cycle({"P1": ["P2"], "P2": ["P3"], "P3": ["P4"], "P4": ["P2"], "P5": ["P1"]}))
print(find_cycle({"P1": ["P2"], "P2": ["P3"], "P3": []}))
```

Output:

```text
['P2', 'P3', 'P4', 'P2']
None
```

The cycle P2 → P3 → P4 → P2 means these three are deadlocked. P1 and P5 are not on the cycle, but P1 waits for P2 and P5 waits for P1, so they are stuck behind the deadlock and will be released only when it is broken. In the second graph, the waits form a chain ending at P3, which is not waiting for anything; once P3 finishes, P2 and then P1 can proceed.

### Example 2: Detection with multiple instances

Five processes share resource types A (7 instances), B (2), and C (6). Nothing is free at the moment.

| Process | Allocation (A B C) | Request (A B C) |
| :--- | :--- | :--- |
| P0 | 0 1 0 | 0 0 0 |
| P1 | 2 0 0 | 2 0 2 |
| P2 | 3 0 3 | 0 0 0 |
| P3 | 2 1 1 | 1 0 0 |
| P4 | 0 0 2 | 0 0 2 |

```python
def detect(available, allocation, request):
    work = list(available)
    finish = [all(a == 0 for a in row) for row in allocation]   # holding nothing: not deadlocked
    order, progress = [], True
    while progress:
        progress = False
        for i, done in enumerate(finish):
            if not done and all(r <= w for r, w in zip(request[i], work)):
                work = [w + a for w, a in zip(work, allocation[i])]   # assume P_i finishes
                finish[i], progress = True, True
                order.append(f"P{i}")
    deadlocked = [f"P{i}" for i, done in enumerate(finish) if not done]
    return order, deadlocked

allocation = [[0, 1, 0], [2, 0, 0], [3, 0, 3], [2, 1, 1], [0, 0, 2]]
request = [[0, 0, 0], [2, 0, 2], [0, 0, 0], [1, 0, 0], [0, 0, 2]]
available = [0, 0, 0]
print(detect(available, allocation, request))

request[2] = [0, 0, 1]                      # P2 now asks for one more instance of C
print(detect(available, allocation, request))
```

Output:

```text
(['P0', 'P2', 'P3', 'P4', 'P1'], [])
(['P0'], ['P1', 'P2', 'P3', 'P4'])
```

In the first state, nothing is free, yet there is no deadlock: P0 and P2 are not waiting for anything, so they can finish and release (0, 1, 0) and (3, 0, 3), which satisfies P3, then P4, then P1. After P2 requests one more C, only P0 can finish; it releases a single B, which is not enough for anyone else. P1, P2, P3, and P4 are deadlocked.

### Example 3: Choosing a victim

The deadlocked processes of Example 2 have the following properties. Suppose the cost of aborting a process is estimated as its CPU time used plus 10 points per previous rollback.

| Process | CPU time used (s) | Previous rollbacks | Cost | Holds |
| :--- | :--- | :--- | :--- | :--- |
| P1 | 40 | 0 | 40 | A 2 |
| P2 | 5 | 2 | 25 | A 3, C 3 |
| P3 | 12 | 0 | 12 | A 2, B 1, C 1 |
| P4 | 30 | 1 | 40 | C 2 |

The cheapest victim is P3 (cost 12). Aborting it releases (2, 1, 1), so, together with the instance of B released by P0, Work becomes (2, 2, 1). That is still not enough for P1, which needs two instances of C, but P2's request (0, 0, 1) fits. P2 finishes and releases (3, 0, 3), giving (5, 2, 4), after which P1 and P4 both fit. One abort breaks the deadlock. P2 has used the least CPU time, but its two previous rollbacks raise its cost, which keeps it from being chosen again and again and starving.

## Applications

- **Database management systems** build wait-for graphs among transactions; when a cycle appears, they abort and roll back a victim, often the youngest or the one that has done the least work, and report a deadlock error so the application can retry.
- **Operating system debugging:** tools that inspect hung processes reconstruct which thread waits on which lock to find the cycle.
- **Java virtual machines** can detect deadlocked threads on monitors, reporting them in thread dumps and through `ThreadMXBean.findDeadlockedThreads`.
- **Distributed systems** detect deadlock across machines by combining local wait-for graphs, or more commonly use timeouts as a cheap approximation.
- **Checkpointing** in long scientific and batch jobs makes partial rollback possible, limiting the work lost in recovery.

## Common mistakes

- **Using Need (maximum claims) instead of Request** in the detection algorithm; detection looks only at what processes are waiting for now.
- **Marking processes that hold nothing as possibly deadlocked;** they cannot be part of a cycle and start out finished.
- **Assuming a cycle in a multiple-instance graph is a deadlock** without running the detection algorithm.
- **Aborting a process that modifies persistent data without rollback support,** which can leave files or databases inconsistent.
- **Choosing the same victim repeatedly,** which causes starvation; include the rollback count in the victim's cost.

## Revision notes

- Single instances: deadlock ⇔ cycle in the wait-for graph; DFS finds it in $O(n^2)$.
- Multiple instances: Work = Available; processes holding nothing start finished; repeatedly finish any process with Request ≤ Work and add its Allocation; unfinished processes are deadlocked. $O(mn^2)$.
- Detection asks "is it stuck now?" (Request); the banker's algorithm asks "could it get stuck?" (Need).
- Run detection on every failed request (fast discovery, high cost) or periodically or when utilization drops.
- Recovery: abort all deadlocked processes, abort one at a time, or preempt resources with rollback.
- Victim choice weighs priority, work done, resources held, and previous rollbacks (to prevent starvation).

## Practice questions

:::question basic
How is a wait-for graph obtained from a resource-allocation graph, and when is it enough to detect deadlock?
:::answer
Remove the resource nodes and draw an edge $P_i \to P_j$ whenever $P_i$ requests a resource that $P_j$ holds (collapsing the request edge $P_i \to R$ and the assignment edge $R \to P_j$). It is enough when every resource type has a single instance; then a cycle in the wait-for graph is exactly a deadlock.
:::

:::question basic
In the detection algorithm, why are processes that hold no resources marked as finished at the start?
:::answer
A deadlock is a cycle of processes, each holding a resource that another one wants. A process that holds nothing cannot block anyone else, so it cannot be part of the cycle. It may itself be waiting, but it is waiting on others, not causing their waits, so it is excluded from the set of deadlocked processes.
:::

:::question intermediate
Run the detection algorithm on two resource types with Available (1, 0). P0 holds (1, 0) and requests (0, 1); P1 holds (0, 1) and requests (1, 0); P2 holds (1, 1) and requests (0, 0). Which processes are deadlocked?
:::answer
Work starts as (1, 0). P0's request (0, 1) does not fit. P1's request (1, 0) fits, so P1 finishes and Work becomes (1, 1). Now P0's request (0, 1) fits, so P0 finishes: Work (2, 1). P2's request (0, 0) fits trivially: Work (3, 2). Every process finishes, so there is no deadlock, even though P0 is currently waiting.
:::

:::question intermediate
What are the advantages and disadvantages of running the detection algorithm every time a request cannot be granted?
:::answer
Advantage: a deadlock is found the moment it forms, so the processes involved are stuck as briefly as possible, and the request that created the cycle is known, which helps in choosing what to undo. Disadvantage: the algorithm costs $O(mn^2)$ and would run very often under contention, consuming significant CPU time even though most failed requests do not create deadlocks.
:::

:::question intermediate
Why does recovery by resource preemption usually require rollback?
:::answer
A process that has a resource taken away was using it, perhaps halfway through a task, so it cannot simply continue as if nothing happened. It must return to a state from before it acquired the resource: either restart from the beginning (total rollback) or return to a saved checkpoint (partial rollback). Without rollback, the process would continue with an inconsistent view of the resource's state.
:::

:::question advanced
Explain why the detection algorithm's assumption that a process whose request is satisfiable "will finish and release everything" is safe, even though the process might actually request more resources later.
:::answer
The algorithm only needs to decide whether the system is deadlocked now. If a process's current request can be satisfied, it is not blocked in a cycle at this moment: once it receives the resources, it can run. If it later requests more and becomes blocked, that is a new situation, and a future run of the detection algorithm, based on the new Request matrix, will detect any deadlock it causes. So the optimistic assumption never hides an existing deadlock; it only avoids predicting future ones, which is the job of avoidance, not detection.
:::

## Further learning

- **Next:** *Address Binding & Dynamic Relocation* begins the memory-management module.
- **Related:** *Banker's Algorithm & Avoidance* uses the same matrix structure to stay out of unsafe states.
- **Related:** *Breadth-First Search & Depth-First Search* (Data Structures & Algorithms) explains the cycle detection used on wait-for graphs.
