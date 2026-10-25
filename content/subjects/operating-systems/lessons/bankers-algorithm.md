---
lesson: bankers-algorithm
title: Banker's Algorithm and Deadlock Avoidance
summary: Avoid deadlock by granting resource requests only when the system stays in a safe state, using the Available, Max, Allocation, and Need matrices, the safety algorithm, and the resource-request algorithm.
minutes: 40
type: theory
objectives:
  - Distinguish safe, unsafe, and deadlocked states and explain why avoidance keeps the system safe
  - Compute the Need matrix from Max and Allocation and run the safety algorithm to find a safe sequence
  - Apply the resource-request algorithm to decide whether a request is granted, delayed, or rejected
  - Evaluate the costs and practical limitations of deadlock avoidance
---

## Introduction

Deadlock prevention removes one of the four necessary conditions everywhere, which is simple but restrictive. **Deadlock avoidance** takes a more flexible approach: let processes request resources in any order, but before granting each request, check whether granting it could lead to a deadlock in the future. If it could, make the process wait, even though the resources are free right now.

To look into the future, the system needs some information: each process declares in advance the **maximum** number of instances of each resource type it may ever need. With that, the system can tell whether there is some order in which every process could still finish. Edsger Dijkstra's **banker's algorithm** does exactly this. The name comes from a bank that never lends out its cash in a way that would leave it unable to satisfy every customer's maximum credit line. This lesson develops the algorithm step by step and traces it on a standard example.

**Before you start:** you should know the four conditions for deadlock and resource-allocation graphs.

## Core theory

### Safe and unsafe states

A state is **safe** if there is a **safe sequence** $\langle P_1, P_2, \dots, P_n \rangle$ of all processes such that each $P_i$'s remaining needs can be satisfied by the currently available resources **plus** the resources held by all the processes before it in the sequence. Then $P_1$ can finish and release its resources, which lets $P_2$ finish, and so on.

- A safe state is **not deadlocked**, and from a safe state the system can always avoid deadlock.
- An **unsafe** state is **not necessarily deadlocked**, but it might lead to deadlock if processes request their maximum amounts.
- Avoidance means **never leaving the set of safe states**.

### The data structures

For $n$ processes and $m$ resource types:

| Structure | Size | Meaning |
| :--- | :--- | :--- |
| Available | $m$ | free instances of each resource type |
| Max | $n \times m$ | maximum demand of each process |
| Allocation | $n \times m$ | instances currently held by each process |
| Need | $n \times m$ | remaining possible demand: $\text{Need} = \text{Max} - \text{Allocation}$ |

### The safety algorithm

1. Let `Work = Available`, and mark every process unfinished.
2. Find an unfinished process $P_i$ with $\text{Need}_i \le \text{Work}$ (component by component). If none exists, go to step 4.
3. Pretend $P_i$ runs to completion and releases everything: `Work = Work + Allocation_i`; mark $P_i$ finished; go back to step 2.
4. The state is safe if and only if every process is finished.

The algorithm takes $O(m \cdot n^2)$ time. The order in which finished processes are found is a safe sequence. There may be several; the algorithm only needs one.

### The resource-request algorithm

When process $P_i$ requests a vector $\text{Request}_i$:

1. If $\text{Request}_i > \text{Need}_i$ in any component, raise an **error**: the process has exceeded its declared maximum.
2. If $\text{Request}_i > \text{Available}$ in any component, $P_i$ must **wait**: the resources are not free.
3. Otherwise, **pretend** to grant it:
    - $\text{Available} = \text{Available} - \text{Request}_i$
    - $\text{Allocation}_i = \text{Allocation}_i + \text{Request}_i$
    - $\text{Need}_i = \text{Need}_i - \text{Request}_i$
4. Run the safety algorithm on the new state. If it is safe, **grant** the request. If not, **restore** the old state and make $P_i$ wait.

### Limitations

- Every process must declare its maximum needs in advance, which is rarely realistic for interactive programs.
- The number of processes and resources must be fixed, and processes must eventually release what they hold.
- Running the safety check on every request costs time.
- Avoidance is conservative: it can make a process wait even when no deadlock would actually have occurred, which reduces utilization.

For these reasons, general-purpose operating systems do not use the banker's algorithm for user programs, but its ideas appear in admission control, where a system accepts new work only if it can still meet its commitments.

## Worked examples

### Example 1: A safe sequence

Five processes, P0 to P4, share three resource types: A (10 instances), B (5), and C (7).

| Process | Allocation (A B C) | Max (A B C) | Need (A B C) |
| :--- | :--- | :--- | :--- |
| P0 | 0 1 0 | 7 5 3 | 7 4 3 |
| P1 | 2 0 0 | 3 2 2 | 1 2 2 |
| P2 | 3 0 2 | 9 0 2 | 6 0 0 |
| P3 | 2 1 1 | 2 2 2 | 0 1 1 |
| P4 | 0 0 2 | 4 3 3 | 4 3 1 |

The allocations total (7, 2, 5), so Available = (10, 5, 7) − (7, 2, 5) = (3, 3, 2). Running the safety algorithm, scanning the processes in index order:

| Step | Work before | Process chosen | Need ≤ Work? | Work after |
| :--- | :--- | :--- | :--- | :--- |
| 1 | (3, 3, 2) | P1 | (1, 2, 2) ≤ (3, 3, 2) | (5, 3, 2) |
| 2 | (5, 3, 2) | P3 | (0, 1, 1) ≤ (5, 3, 2) | (7, 4, 3) |
| 3 | (7, 4, 3) | P4 | (4, 3, 1) ≤ (7, 4, 3) | (7, 4, 5) |
| 4 | (7, 4, 5) | P0 | (7, 4, 3) ≤ (7, 4, 5) | (7, 5, 5) |
| 5 | (7, 5, 5) | P2 | (6, 0, 0) ≤ (7, 5, 5) | (10, 5, 7) |

Every process can finish, so the state is safe with sequence ⟨P1, P3, P4, P0, P2⟩. In step 1, P0 and P2 are skipped because their needs exceed Work. The final Work equals the total resources, as it must once everyone has released everything.

### Example 2: Deciding requests in code

```python
def is_safe(available, allocation, need):
    work, finish, sequence = list(available), [False] * len(allocation), []
    progress = True
    while progress:
        progress = False
        for i in range(len(allocation)):
            if not finish[i] and all(n <= w for n, w in zip(need[i], work)):
                work = [w + a for w, a in zip(work, allocation[i])]   # P_i finishes and releases
                finish[i], progress = True, True
                sequence.append(f"P{i}")
    return all(finish), sequence

def request(state, pid, req):
    available, allocation, need = state
    if any(r > n for r, n in zip(req, need[pid])):
        return "error: exceeds its declared maximum", state
    if any(r > a for r, a in zip(req, available)):
        return "wait: resources not available", state
    new_available = [a - r for a, r in zip(available, req)]           # pretend to grant it
    new_allocation = [row[:] for row in allocation]
    new_need = [row[:] for row in need]
    new_allocation[pid] = [a + r for a, r in zip(allocation[pid], req)]
    new_need[pid] = [n - r for n, r in zip(need[pid], req)]
    safe, sequence = is_safe(new_available, new_allocation, new_need)
    if not safe:
        return "wait: granting it would leave an unsafe state", state     # roll back
    return f"granted; safe sequence {' '.join(sequence)}", (new_available, new_allocation, new_need)

allocation = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
maximum = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
available = [3, 3, 2]
need = [[m - a for m, a in zip(mrow, arow)] for mrow, arow in zip(maximum, allocation)]

print("Need:", need)
safe, sequence = is_safe(available, allocation, need)
print("initial state safe:", safe, "sequence", " ".join(sequence))

state = (available, allocation, need)
for pid, req in [(1, [1, 0, 2]), (4, [3, 3, 0]), (0, [0, 2, 0]), (3, [0, 2, 0])]:
    result, state = request(state, pid, req)
    print(f"P{pid} requests {req}: {result}")
print("Available now:", state[0])
```

Output:

```text
Need: [[7, 4, 3], [1, 2, 2], [6, 0, 0], [0, 1, 1], [4, 3, 1]]
initial state safe: True sequence P1 P3 P4 P0 P2
P1 requests [1, 0, 2]: granted; safe sequence P1 P3 P4 P0 P2
P4 requests [3, 3, 0]: wait: resources not available
P0 requests [0, 2, 0]: wait: granting it would leave an unsafe state
P3 requests [0, 2, 0]: error: exceeds its declared maximum
Available now: [2, 3, 0]
```

The four requests show all three outcomes. P1's request (1, 0, 2) fits within its need and within Available, and the resulting state is still safe, so it is granted and Available drops to (2, 3, 0). P4's request (3, 3, 0) must wait simply because only 2 instances of A are free. P0's request (0, 2, 0) could be satisfied from the free resources, but the pretend state would leave Work = (2, 1, 0), and no process's need fits within that, so the state would be unsafe: P0 waits even though the resources exist. P3's request is an error, because P3 declared that it would need at most 1 more instance of B.

### Example 3: Why unsafe does not mean deadlocked

Consider the pretend state after P0's request in Example 2: Available (2, 1, 0) and Need P1 = (0, 2, 0), P3 = (0, 1, 1). No process can be guaranteed to finish, so the state is unsafe. But a deadlock happens only if the processes actually request their full remaining needs. If P3 happened to finish using only what it holds and released its resources, Available would rise to (4, 2, 1), and P1 could then finish. The banker's algorithm does not gamble on such luck: it refuses any state from which deadlock is **possible**, which is why avoidance is safe but conservative.

## Applications

- **Teaching and analysis:** the safety algorithm is the clearest way to reason about whether a set of resource commitments can all be honoured.
- **Admission control:** real-time and cloud systems accept a new task or virtual machine only if their guarantees to existing tasks can still be met, the same "stay safe" principle.
- **Banking and credit:** the original analogy, a lender who keeps enough reserves to cover the maximum claims of customers in some order.
- **Batch and embedded systems** with known, fixed resource demands can apply avoidance directly.
- **Deadlock detection** reuses the safety algorithm's structure with current requests in place of maximum needs.

## Common mistakes

- **Using Max instead of Need** in the safety check. The comparison is always between what a process may still request and the resources available.
- **Forgetting to add the finishing process's Allocation to Work.** A finished process releases everything it holds, not just its Need.
- **Granting a request because the resources are free,** without running the safety check on the resulting state.
- **Not rolling back** the pretend allocation when the resulting state is unsafe.
- **Believing an unsafe state is a deadlock.** Unsafe states only make deadlock possible.
- **Thinking there is only one safe sequence.** Different scanning orders can find different valid sequences.

## Revision notes

- Safe state: some order lets every process obtain its remaining need and finish. Unsafe ≠ deadlocked.
- Need = Max − Allocation; Available = total − sum of allocations.
- Safety algorithm: Work = Available; repeatedly pick an unfinished process with Need ≤ Work and add its Allocation to Work. Safe if all finish. $O(mn^2)$.
- Resource request: error if Request > Need; wait if Request > Available; otherwise pretend, check safety, grant or roll back.
- Avoidance needs advance maximum claims and is conservative; general-purpose OSes rarely use it.

## Practice questions

:::question basic
What is the difference between an unsafe state and a deadlocked state?
:::answer
In a deadlocked state, some processes are already waiting for one another in a cycle and none can proceed. In an unsafe state, no deadlock has necessarily occurred yet, but the system cannot guarantee that every process will be able to finish: if processes request their maximum needs, a deadlock may follow. Every deadlocked state is unsafe, but not every unsafe state is deadlocked.
:::

:::question basic
A process has Max (5, 2, 3) and Allocation (2, 1, 3). What is its Need?
:::answer
Need = Max − Allocation = (5 − 2, 2 − 1, 3 − 3) = (3, 1, 0). The process may still request up to 3 more instances of the first resource type and 1 of the second, and none of the third.
:::

:::question intermediate
A system has 12 tape drives. P0 has Max 10 and holds 5; P1 has Max 4 and holds 2; P2 has Max 9 and holds 2. Is the state safe? What if P2 is given one more drive?
:::answer
Available $= 12 - (5 + 2 + 2) = 3$. Needs: P0 5, P1 2, P2 7. P1 can finish (2 ≤ 3), leaving 5 available; then P0 (5 ≤ 5), leaving 10; then P2 (7 ≤ 10). The sequence ⟨P1, P0, P2⟩ is safe. If P2 receives one more drive, Available is 2 and P2's need becomes 6. P1 can still finish (2 ≤ 2), leaving 4, but then P0 needs 5 and P2 needs 6, both more than 4, so the state is unsafe. The banker's algorithm would make P2 wait.
:::

:::question intermediate
In the state of Example 1, P1 requests (1, 0, 2). Show the pretend state and verify that it is safe.
:::answer
Request ≤ Need (1, 2, 2) and ≤ Available (3, 3, 2), so pretend: Available becomes (2, 3, 0), P1's Allocation becomes (3, 0, 2), and its Need becomes (0, 2, 0). Safety: Work (2, 3, 0) covers P1's need (0, 2, 0), so Work becomes (5, 3, 2); P3's need (0, 1, 1) fits, giving (7, 4, 3); P4's (4, 3, 1) fits, giving (7, 4, 5); P0's (7, 4, 3) fits, giving (7, 5, 5); P2's (6, 0, 0) fits. All finish, so the request is granted.
:::

:::question intermediate
What is the time complexity of the safety algorithm, and why?
:::answer
$O(m \cdot n^2)$ for $n$ processes and $m$ resource types. Each pass over the processes checks up to $n$ processes, each comparison of Need with Work costs $O(m)$, and at least one process finishes per useful pass, so there are at most $n$ passes: $n \times n \times m$.
:::

:::question advanced
Explain why the banker's algorithm can reduce resource utilization, using Example 2's request by P0.
:::answer
P0 asked for (0, 2, 0) when (2, 3, 0) was free, so the request could have been satisfied immediately. The algorithm refused because the resulting state would be unsafe: if every process then demanded its full remaining need, no process could be guaranteed to finish. Many runs might never reach that worst case, for instance if P3 finished early, but the algorithm cannot know this, so it leaves free resources idle and makes P0 wait. Avoidance trades utilization for the guarantee that deadlock will never occur.
:::

## Further learning

- **Next:** *Deadlock Detection & Recovery* lets deadlocks happen and then finds and breaks them.
- **Related:** *Deadlock Characterization & Prevention* covers the four conditions and the alternative of prevention.
- **Related:** *Scheduling Criteria & Dispatcher* shows another place where the OS trades utilization for guarantees.
