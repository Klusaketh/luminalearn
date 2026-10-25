---
lesson: cpu-scheduling-algorithms-round-robin
title: Preemptive and Non-Preemptive CPU Scheduling Algorithms
summary: Shortest-job-first, shortest-remaining-time-first, priority, round-robin, and multilevel feedback queue scheduling, compared with Gantt charts and average waiting and turnaround times.
minutes: 50
type: theory
objectives:
  - Schedule processes with SJF and SRTF and explain why SJF minimises average waiting time
  - Apply preemptive and non-preemptive priority scheduling and use aging to prevent starvation
  - Simulate round-robin scheduling and analyse how the time quantum affects response time and overhead
  - Describe multilevel queue and multilevel feedback queue scheduling and why general-purpose systems use them
---

## Introduction

First-come, first-served scheduling is fair but can be painfully slow: one long job at the front of the queue delays every short job behind it. Better policies use more information. If we knew how long each process would run, we could run the short ones first. If some processes are more important, we could give them priority. If users expect quick responses, we could give every process a short turn in rotation.

Each idea is a classic algorithm: **shortest-job-first** and its preemptive form **shortest-remaining-time-first**, **priority scheduling**, and **round-robin**. Each also has a weakness: SJF needs to predict the future, priority scheduling can starve low-priority work, and round-robin's performance depends on the length of its time slice. Real operating systems combine them in **multilevel feedback queues**. This lesson computes Gantt charts and metrics for each algorithm, so that their trade-offs become concrete.

**Before you start:** you should know scheduling criteria (turnaround, waiting, and response time) and FCFS scheduling.

## Core theory

### Shortest-job-first (SJF)

When the CPU becomes free, run the ready process with the **shortest next CPU burst**; ties are broken by arrival order. SJF is non-preemptive in this basic form.

**SJF minimises the average waiting time** for a set of processes available at the same time. The exchange argument: if a longer job runs immediately before a shorter one, swapping them reduces the shorter job's wait by the longer job's burst and increases the longer job's wait by only the shorter job's burst, so the total waiting time falls.

The difficulty is that the next burst length is unknown. Schedulers **predict** it with an exponential average of past bursts:

$$\tau_{n+1} = \alpha\, t_n + (1 - \alpha)\, \tau_n,$$

where $t_n$ is the length of the most recent burst, $\tau_n$ the previous prediction, and $0 \le \alpha \le 1$ weights recent history (commonly $\alpha = 1/2$).

### Shortest-remaining-time-first (SRTF)

The preemptive version of SJF: whenever a new process arrives, compare its burst with the **remaining** time of the running process, and preempt if the newcomer is shorter. SRTF gives the minimum average waiting time when processes arrive at different times, but it preempts more often and, like SJF, can **starve** long processes if short ones keep arriving.

### Priority scheduling

Each process has a priority (in this lesson, a **smaller number means higher priority**, as in many textbooks; real systems differ). The CPU goes to the highest-priority ready process, either non-preemptively or preemptively (a newly ready higher-priority process takes the CPU at once). SJF is a special case in which the priority is the predicted burst length.

The main problem is **starvation** (indefinite blocking): a steady stream of high-priority processes can keep a low-priority one waiting forever. The standard solution is **aging**: gradually raise the priority of processes that have waited a long time, so every process eventually runs.

### Round-robin (RR)

Round-robin is FCFS with preemption, designed for time sharing. Each process runs for at most one **time quantum** $q$ (typically a few milliseconds to tens of milliseconds). If it has not finished, it is preempted and placed at the **back of the ready queue**. With $n$ ready processes, each gets $1/n$ of the CPU, in chunks of at most $q$, and no process waits more than $(n - 1)q$ before its next turn.

The quantum decides RR's behaviour:

- **$q$ very large:** RR degenerates into FCFS.
- **$q$ very small:** responses are quick, but context-switch overhead consumes a large share of the CPU.
- **A common rule of thumb:** choose $q$ so that most CPU bursts (around 80%) finish within one quantum, and keep $q$ much larger than the context-switch time.

RR usually has a higher average turnaround than SJF but much better **response time**, which is what interactive users notice.

A convention is needed when a new process arrives at the same moment a quantum expires. This lesson places the **new arrival in the queue before the preempted process**, a common textbook convention; schedules computed with the opposite convention can differ.

### Multilevel queue and multilevel feedback queue

A **multilevel queue** splits ready processes into fixed classes (for example, real-time, interactive, and batch), each with its own queue and algorithm, with priority between queues. A process stays in its class.

A **multilevel feedback queue (MLFQ)** lets processes **move** between queues according to their behaviour:

- New processes enter the highest-priority queue, which has a short quantum.
- A process that uses its entire quantum (CPU-bound behaviour) is demoted to a lower queue with a longer quantum.
- A process that blocks before its quantum ends (interactive behaviour) stays high.
- Processes that have waited too long in low queues are promoted, which is aging, preventing starvation.

MLFQ approximates SJF without knowing burst lengths: short and interactive jobs finish in the fast top queues, while long CPU-bound jobs sink to the bottom and run when nothing else needs the CPU. Variants of this idea shaped the schedulers of BSD UNIX, Solaris, and Windows.

## Worked examples

### Example 1: SJF, SRTF, and RR on the same processes

Four processes, with arrival times and CPU bursts: P1 (0, 8), P2 (1, 4), P3 (2, 9), P4 (3, 5).

```python
from collections import deque

def simulate(processes, preemptive):
    """Shortest-job-first; with preemptive=True, shortest-remaining-time-first."""
    arrival = {n: p[0] for n, p in processes.items()}
    remaining = {n: p[1] for n, p in processes.items()}
    time, gantt, finish = 0, [], {}
    while remaining:
        ready = [n for n in remaining if arrival[n] <= time]
        if not ready:
            time = min(arrival[n] for n in remaining)
            continue
        current = min(ready, key=lambda n: (remaining[n], n))
        if preemptive:                       # run until the next arrival or completion
            later = [arrival[n] for n in remaining if arrival[n] > time]
            run = min([remaining[current]] + [a - time for a in later])
        else:
            run = remaining[current]
        if gantt and gantt[-1][0] == current:
            gantt[-1] = (current, gantt[-1][1], time + run)
        else:
            gantt.append((current, time, time + run))
        time += run
        remaining[current] -= run
        if remaining[current] == 0:
            del remaining[current]
            finish[current] = time
    return gantt, finish

def round_robin(processes, quantum):
    arrival = {n: p[0] for n, p in processes.items()}
    remaining = {n: p[1] for n, p in processes.items()}
    order = sorted(processes, key=lambda n: arrival[n])
    time, queue, gantt, finish, i = 0, deque(), [], {}, 0
    while len(finish) < len(processes):
        while i < len(order) and arrival[order[i]] <= time:
            queue.append(order[i])
            i += 1
        if not queue:
            time = arrival[order[i]]
            continue
        current = queue.popleft()
        run = min(quantum, remaining[current])
        if gantt and gantt[-1][0] == current:
            gantt[-1] = (current, gantt[-1][1], time + run)
        else:
            gantt.append((current, time, time + run))
        time += run
        remaining[current] -= run
        while i < len(order) and arrival[order[i]] <= time:   # arrivals join before the preempted process
            queue.append(order[i])
            i += 1
        if remaining[current]:
            queue.append(current)
        else:
            finish[current] = time
    return gantt, finish

def show(name, processes, result):
    gantt, finish = result
    chart = " ".join(f"{p}[{s}-{e}]" for p, s, e in gantt)
    waits = {n: finish[n] - processes[n][0] - processes[n][1] for n in processes}
    tat = {n: finish[n] - processes[n][0] for n in processes}
    print(f"{name}: {chart}")
    print(f"  waiting {waits}, average {sum(waits.values()) / len(waits):.2f}; average turnaround {sum(tat.values()) / len(tat):.2f}")

procs = {"P1": (0, 8), "P2": (1, 4), "P3": (2, 9), "P4": (3, 5)}
show("SJF ", procs, simulate(procs, preemptive=False))
show("SRTF", procs, simulate(procs, preemptive=True))
show("RR q=4", procs, round_robin(procs, 4))
```

Output:

```text
SJF : P1[0-8] P2[8-12] P4[12-17] P3[17-26]
  waiting {'P1': 0, 'P2': 7, 'P3': 15, 'P4': 9}, average 7.75; average turnaround 14.25
SRTF: P1[0-1] P2[1-5] P4[5-10] P1[10-17] P3[17-26]
  waiting {'P1': 9, 'P2': 0, 'P3': 15, 'P4': 2}, average 6.50; average turnaround 13.00
RR q=4: P1[0-4] P2[4-8] P3[8-12] P4[12-16] P1[16-20] P3[20-24] P4[24-25] P3[25-26]
  waiting {'P1': 12, 'P2': 3, 'P3': 15, 'P4': 17}, average 11.75; average turnaround 18.25
```

Non-preemptive SJF must let P1 finish, because it is the only process present at time 0. SRTF preempts P1 at time 1, when P2 arrives with a burst of 4, less than P1's remaining 7. At time 5, P4 (5 units) beats P1 (7 remaining), and P3 (9) runs last. SRTF's average wait, 6.5, is the lowest of the three. Round-robin has the worst averages here, but no process ever waits more than three quanta for a turn.

### Example 2: Priority scheduling

Five processes arrive at time 0 with (burst, priority): P1 (10, 3), P2 (1, 1), P3 (2, 4), P4 (1, 5), P5 (5, 2). A smaller number means a higher priority.

| Order | Runs | Waiting time |
| :--- | :--- | :--- |
| P2 (priority 1) | 0 to 1 | 0 |
| P5 (priority 2) | 1 to 6 | 1 |
| P1 (priority 3) | 6 to 16 | 6 |
| P3 (priority 4) | 16 to 18 | 16 |
| P4 (priority 5) | 18 to 19 | 18 |

The average waiting time is $(0 + 1 + 6 + 16 + 18)/5 = 41/5 = 8.2$. P4, a one-unit job, waits the longest because of its low priority. If new high-priority processes kept arriving, P3 and P4 could wait forever; with aging, for instance raising a waiting process's priority by one level every few hundred milliseconds, they would eventually reach the top.

### Example 3: How the quantum changes round-robin

Three processes arrive at time 0: P1 (24), P2 (3), P3 (3). The `round_robin` function from Example 1 is reused, and the number of switches between different processes is counted as the number of boundaries in the Gantt chart.

```python
from collections import deque

def round_robin(processes, quantum):
    remaining = dict(processes)
    queue, time, gantt, finish = deque(processes), 0, [], {}
    while queue:
        current = queue.popleft()
        run = min(quantum, remaining[current])
        if gantt and gantt[-1][0] == current:
            gantt[-1] = (current, gantt[-1][1], time + run)   # the same process continues
        else:
            gantt.append((current, time, time + run))
        time += run
        remaining[current] -= run
        if remaining[current]:
            queue.append(current)
        else:
            finish[current] = time
    return gantt, finish

bursts = {"P1": 24, "P2": 3, "P3": 3}
for q in (1, 4, 30):
    gantt, finish = round_robin(bursts, q)
    waiting = sum(finish[p] - bursts[p] for p in bursts) / len(bursts)
    first_run = {}
    for p, start, _ in gantt:
        first_run.setdefault(p, start)
    response = sum(first_run.values()) / len(bursts)
    print(f"q={q:>2}: switches {len(gantt) - 1:>2}, average waiting {waiting:.2f}, average response {response:.2f}")
```

Output:

```text
q= 1: switches  9, average waiting 5.67, average response 1.00
q= 4: switches  3, average waiting 5.67, average response 3.67
q=30: switches  2, average waiting 17.00, average response 17.00
```

With $q = 30$, every process finishes within one quantum and RR becomes FCFS, convoy effect included. With $q = 4$, the short jobs finish in their first turns, cutting the average wait from 17 to 5.67. Shrinking the quantum to 1 does not lower the average wait any further here but triples the number of process switches; in a real system each switch costs time, so the very small quantum would make everything slower. Response time improves steadily as $q$ shrinks, which is the benefit interactive users feel.

### Example 4: Predicting burst lengths

With $\alpha = 1/2$ and an initial guess $\tau_0 = 10$, suppose the actual bursts are 6, 4, 6, 4, 13.

| Burst $n$ | Prediction $\tau_n$ | Actual $t_n$ | Next prediction $\tau_{n+1} = (t_n + \tau_n)/2$ |
| :---: | :---: | :---: | :---: |
| 0 | 10 | 6 | 8 |
| 1 | 8 | 4 | 6 |
| 2 | 6 | 6 | 6 |
| 3 | 6 | 4 | 5 |
| 4 | 5 | 13 | 9 |

The prediction follows the trend while smoothing out noise: after the unusually long burst of 13, it rises to 9 rather than jumping all the way to 13. With $\alpha = 0$ the prediction never changes, and with $\alpha = 1$ it simply equals the last burst.

## Applications

- **General-purpose operating systems** use priority-based preemptive scheduling with feedback: Windows boosts the priority of threads that wake from I/O, and Linux's schedulers favour tasks that have used little CPU time recently.
- **Interactive systems** depend on round-robin-style time slicing to keep many programs responsive at once.
- **Real-time systems** use fixed priorities (for example, rate-monotonic scheduling, where shorter-period tasks get higher priority) or deadline-based priorities.
- **Networking:** routers schedule packets from different flows with round-robin and priority queues for fairness and quality of service.
- **Batch and cluster schedulers** use shortest-job-first ideas, with user-supplied run-time estimates, to reduce average turnaround.

## Common mistakes

- **Running SJF preemptively by accident** (or SRTF non-preemptively). SJF waits for the running job to finish; SRTF compares remaining times at every arrival.
- **Comparing a new arrival with the running process's original burst** instead of its remaining time in SRTF.
- **Ignoring the arrival-versus-requeue convention in round-robin,** which changes the schedule when an arrival coincides with a quantum expiry.
- **Mixing up priority conventions.** State whether a small number means high or low priority before computing a schedule.
- **Concluding that a smaller quantum is always better.** Response time improves, but overhead grows and turnaround may not improve at all.
- **Forgetting starvation.** SJF, SRTF, and priority scheduling all need aging (or similar) in a real system.

## Revision notes

- SJF: shortest next burst first; optimal average waiting time for jobs available together; non-preemptive.
- SRTF: preemptive SJF; compares the newcomer with the running process's remaining time.
- Burst prediction: $\tau_{n+1} = \alpha t_n + (1 - \alpha)\tau_n$.
- Priority: highest priority first, preemptive or not; aging prevents starvation.
- Round-robin: quantum $q$; at most $(n-1)q$ wait between turns; large $q$ → FCFS, small $q$ → high overhead.
- Multilevel feedback queues demote CPU-bound processes and keep interactive ones high, approximating SJF without knowing burst lengths.

## Practice questions

:::question basic
Why can SJF not be implemented exactly at the level of CPU scheduling, and how do systems approximate it?
:::answer
It needs the length of each process's next CPU burst, which is not known in advance. Systems predict it from past behaviour, usually with an exponential average $\tau_{n+1} = \alpha t_n + (1 - \alpha) \tau_n$, and schedule by the prediction. Multilevel feedback queues approximate SJF in another way, by observing whether processes use their whole quantum.
:::

:::question basic
What is starvation in priority scheduling, and how does aging prevent it?
:::answer
Starvation is when a low-priority ready process never runs because higher-priority processes keep arriving. Aging gradually increases the priority of a process the longer it waits, so eventually it becomes the highest-priority process and is scheduled.
:::

:::question intermediate
Processes A (arrival 0, burst 7), B (arrival 2, burst 4), C (arrival 4, burst 1), and D (arrival 5, burst 4) are scheduled with SRTF. Give the Gantt chart and the average waiting time.
:::answer
A runs 0 to 2. At 2, B (4) beats A's remaining 5: B runs 2 to 4. At 4, C (1) beats B's remaining 2: C runs 4 to 5. At 5, the remaining times are A 5, B 2, D 4, so B runs 5 to 7, then D (4, less than A's 5) runs 7 to 11, then A runs 11 to 16. Waiting times: A $16 - 0 - 7 = 9$, B $7 - 2 - 4 = 1$, C $5 - 4 - 1 = 0$, D $11 - 5 - 4 = 2$; average $12/4 = 3$.
:::

:::question intermediate
Schedule P1 (burst 5), P2 (burst 3), and P3 (burst 1), all arriving at time 0 in that order, with round-robin and a quantum of 2. Give the Gantt chart and each process's turnaround time.
:::answer
P1 runs 0 to 2 (3 left), P2 runs 2 to 4 (1 left), P3 runs 4 to 5 and finishes, P1 runs 5 to 7 (1 left), P2 runs 7 to 8 and finishes, P1 runs 8 to 9 and finishes. Turnaround times: P1 9, P2 8, P3 5, an average of $22/3 \approx 7.33$.
:::

:::question intermediate
In round-robin with $n = 5$ ready processes and a quantum of 20 ms, what is the longest a process can wait between the end of one turn and the start of its next? What if the quantum is 100 ms?
:::answer
At most $(n - 1)q$, because the other four processes may each use a full quantum first: $4 \times 20 = 80$ ms, or $4 \times 100 = 400$ ms with the larger quantum. A 400 ms pause between turns would be noticeable in an interactive program, which is one reason quanta are kept fairly short.
:::

:::question advanced
Explain how a multilevel feedback queue treats a text editor and a video encoder differently, and why this approximates shortest-job-first.
:::answer
Both start in the top queue with a short quantum. The editor runs briefly and then blocks waiting for a keystroke, never using its full quantum, so it stays in the high-priority queue and gets the CPU quickly whenever it becomes ready. The encoder uses its full quantum every time, so it is demoted step by step into lower queues with longer quanta, where it runs when higher queues are empty and is switched less often. Processes with short CPU bursts therefore get priority and processes with long bursts sink, which is the outcome SJF aims for, achieved by observing behaviour rather than by predicting burst lengths. Periodic promotion (aging) keeps the encoder from starving.
:::

## Further learning

- **Next:** *Critical Section Problem & Mutexes* turns from scheduling to the problems preemption creates for shared data.
- **Related:** *Scheduling Criteria & Dispatcher* defines the metrics used throughout this lesson.
- **Related:** *Priority Queues Overview* (Data Structures & Algorithms) covers the heap structure used to find the highest-priority process quickly.
