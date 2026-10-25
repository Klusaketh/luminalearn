---
lesson: scheduling-criteria-dispatcher
title: Scheduling Criteria and the Dispatcher
summary: Why processes alternate between CPU and I/O bursts, which schedulers decide what runs, what the dispatcher does, and how utilization, throughput, turnaround, waiting, and response time measure a schedule.
minutes: 40
type: theory
objectives:
  - Describe the CPU-I/O burst cycle and distinguish CPU-bound from I/O-bound processes
  - Distinguish the long-term, medium-term, and short-term schedulers and the role of the dispatcher
  - Identify when scheduling decisions occur and what makes a scheduler preemptive
  - Calculate CPU utilization, throughput, turnaround time, waiting time, and response time from a schedule
---

## Introduction

Whenever more processes are ready to run than there are CPU cores, the operating system must decide who goes next. That decision, made thousands of times per second, shapes how a computer feels: whether the mouse pointer moves smoothly while a video renders, whether a batch job finishes overnight, and whether a server answers every client promptly.

Before comparing scheduling algorithms, we need two things: an understanding of how processes actually use the CPU, and a way to **measure** a schedule. "Good" means different things to different systems: a supercomputer wants to finish as many jobs as possible, a laptop wants instant responses to clicks, and an anti-lock braking controller must meet every deadline. This lesson defines the vocabulary, introduces the components that carry out scheduling decisions, and works through the standard metrics using the simplest policy, first-come, first-served.

**Before you start:** you should know the five-state process model and what a context switch is.

## Core theory

### The CPU-I/O burst cycle

Processes alternate between **CPU bursts**, periods of computation, and **I/O bursts**, periods of waiting for disks, networks, or users. Measurements of real workloads show that most CPU bursts are short, with a long tail of occasional long ones.

- An **I/O-bound** process, such as a text editor or a web server, has many short CPU bursts between waits.
- A **CPU-bound** process, such as a video encoder or a scientific simulation, has a few long CPU bursts.

A good scheduler keeps both the CPU and the I/O devices busy: when one process waits for I/O, another should be using the CPU.

### Three schedulers

| Scheduler | Decides | Runs |
| :--- | :--- | :--- |
| Long-term (job) scheduler | which submitted jobs are admitted into memory, controlling the **degree of multiprogramming** | rarely (seconds or minutes); mainly in batch systems |
| Medium-term scheduler | which processes to **swap out** to disk and back in, to relieve memory pressure | occasionally |
| Short-term (CPU) scheduler | which **ready** process runs next on a CPU | very often (milliseconds) |

Interactive systems such as Windows and Linux have essentially no long-term scheduler: a program starts when the user launches it. "Scheduling" in this subject normally means short-term CPU scheduling.

### When scheduling decisions happen

The CPU scheduler may run when a process:

1. switches from running to waiting (for example, it requests I/O);
2. switches from running to ready (for example, a timer interrupt);
3. switches from waiting to ready (its I/O completes);
4. terminates.

In cases 1 and 4 the CPU is free, so a new process must be chosen. A scheduler that makes decisions **only** in these two cases is **non-preemptive** (cooperative): once a process has the CPU, it keeps it until it blocks or exits. A scheduler that may also act in cases 2 and 3, taking the CPU away from a running process, is **preemptive**. All modern general-purpose operating systems are preemptive; it is essential for responsiveness, but it means shared data can be interrupted mid-update, which is why kernels need synchronization.

### The dispatcher

The scheduler **chooses** the next process; the **dispatcher** **gives it the CPU**. The dispatcher:

1. switches context, saving the old process's state and loading the new one's;
2. switches to user mode;
3. jumps to the right instruction in the new process (its saved program counter).

The time it takes is the **dispatch latency**. It is pure overhead, so it must be small compared with the length of a typical CPU burst.

### Scheduling criteria

| Criterion | Definition | Goal |
| :--- | :--- | :--- |
| CPU utilization | fraction of time the CPU does useful work | maximise |
| Throughput | processes completed per unit of time | maximise |
| Turnaround time | completion time − arrival time | minimise |
| Waiting time | time spent in the ready queue = turnaround − CPU burst (for a process with a single CPU burst) | minimise |
| Response time | time from arrival until the process first runs | minimise |

For interactive systems, **response time** matters most, and so does its **variance**: users prefer predictable responses to fast responses that are occasionally very slow. Batch systems care about throughput and turnaround. Real-time systems care about **meeting deadlines** above all. **Fairness**, ensuring every process eventually gets the CPU (no **starvation**), is a requirement in all of them.

Scheduling algorithms directly affect **waiting time**: the CPU burst itself takes the same time whoever runs it, so choosing well means reducing time spent waiting in the ready queue.

### First-come, first-served (FCFS)

The simplest policy runs processes in arrival order, each to completion of its CPU burst. FCFS is non-preemptive, easy to implement with a FIFO queue, and fair in the sense that nobody is overtaken. But it suffers from the **convoy effect**: one long CPU-bound process holds the CPU while many short processes queue behind it, so their waiting times, and the average, become large, and I/O devices sit idle while the short processes wait.

## Worked examples

### Example 1: Computing the metrics for a schedule

```python
def fcfs(processes):
    """processes: (name, arrival, burst); run in arrival order, each to completion."""
    time, rows = 0, []
    for name, arrival, burst in sorted(processes, key=lambda p: p[1]):
        start = max(time, arrival)            # the CPU may sit idle until the process arrives
        finish = start + burst
        rows.append((name, arrival, burst, start, finish))
        time = finish
    return rows

def report(rows):
    print("proc arrive burst start finish turnaround waiting response")
    tat = wt = rt = 0
    for name, arrival, burst, start, finish in rows:
        t, w, r = finish - arrival, finish - arrival - burst, start - arrival
        tat, wt, rt = tat + t, wt + w, rt + r
        print(f"{name:>4} {arrival:>6} {burst:>5} {start:>5} {finish:>6} {t:>10} {w:>7} {r:>8}")
    n = len(rows)
    print(f"averages: turnaround {tat / n:.2f}, waiting {wt / n:.2f}, response {rt / n:.2f}")

report(fcfs([("P1", 0, 5), ("P2", 2, 3), ("P3", 4, 1), ("P4", 10, 2)]))
```

Output:

```text
proc arrive burst start finish turnaround waiting response
  P1      0     5     0      5          5       0        0
  P2      2     3     5      8          6       3        3
  P3      4     1     8      9          5       4        4
  P4     10     2    10     12          2       0        0
averages: turnaround 4.50, waiting 1.75, response 1.75
```

The Gantt chart is P1 from 0 to 5, P2 from 5 to 8, P3 from 8 to 9, the CPU idle from 9 to 10, and P4 from 10 to 12. For P2: turnaround $= 8 - 2 = 6$, waiting $= 6 - 3 = 3$. Over the 12 time units, the CPU is busy for 11, so utilization is $11/12 \approx 91.7\%$, and the throughput is 4 processes in 12 units, or one process per 3 units. In a non-preemptive policy, a process waits only before it first runs, so its response time equals its waiting time; with preemption the two differ.

### Example 2: The convoy effect

Three processes arrive at time 0 in the order P1 (burst 24), P2 (burst 3), P3 (burst 3). The same `fcfs` and `report` functions compare this order with the order P2, P3, P1.

```python
def fcfs(processes):
    time, rows = 0, []
    for name, arrival, burst in sorted(processes, key=lambda p: p[1]):
        start = max(time, arrival)
        finish = start + burst
        rows.append((name, arrival, burst, start, finish))
        time = finish
    return rows

def averages(rows):
    n = len(rows)
    waiting = sum(finish - arrival - burst for _, arrival, burst, _, finish in rows) / n
    turnaround = sum(finish - arrival for _, arrival, _, _, finish in rows) / n
    order = " ".join(name for name, *_ in rows)
    return f"order {order}: average waiting {waiting:.2f}, average turnaround {turnaround:.2f}"

print(averages(fcfs([("P1", 0, 24), ("P2", 0, 3), ("P3", 0, 3)])))
print(averages(fcfs([("P2", 0, 3), ("P3", 0, 3), ("P1", 0, 24)])))
```

Output:

```text
order P1 P2 P3: average waiting 17.00, average turnaround 27.00
order P2 P3 P1: average waiting 3.00, average turnaround 13.00
```

When the long process arrives first, P2 and P3 wait 24 and 27 units for jobs that take only 3: the average wait is $(0 + 24 + 27)/3 = 17$. Running the short jobs first gives $(0 + 3 + 6)/3 = 3$, almost six times better, with exactly the same total work. Python's `sorted` is stable, so processes with equal arrival times keep their listed order. This gap is what motivates shortest-job-first scheduling.

### Example 3: Choosing a criterion for a workload

| System | Most important criterion | Why |
| :--- | :--- | :--- |
| Overnight payroll batch | throughput, turnaround | no user is waiting at a screen |
| Desktop or phone | response time (and its variance) | users notice delays above roughly a tenth of a second |
| Web server | response time, throughput | many clients, each waiting for a reply |
| Car engine controller | meeting deadlines | a late result is a wrong result |
| Shared university server | fairness | no user should be starved by another |

There is no single best scheduler: a policy that maximises throughput by always running the shortest jobs may starve long ones, and a policy that gives instant responses with tiny time slices pays for it in context-switch overhead.

## Applications

- **Operating system kernels** implement these ideas: Linux's scheduler and the Windows scheduler balance responsiveness for interactive threads with throughput for background work.
- **Capacity planning:** turnaround and waiting time measurements tell administrators whether a server needs more cores.
- **Batch and cluster schedulers** such as those on supercomputers optimise throughput and turnaround for long jobs.
- **Real-time systems** in vehicles, aircraft, and medical devices are scheduled to guarantee deadlines.
- **Everyday queues:** supermarket express lanes are a convoy-effect fix, separating short jobs from long ones.

## Common mistakes

- **Confusing the scheduler with the dispatcher.** The scheduler picks the next process; the dispatcher performs the context switch and starts it.
- **Computing waiting time as start time minus arrival in a preemptive schedule.** That is response time; waiting time includes every period spent in the ready queue, which is turnaround minus burst.
- **Forgetting idle time** when a process arrives after the CPU has become free; the next process starts at its arrival time, not when the previous one finished.
- **Measuring turnaround from time 0** instead of from each process's own arrival time.
- **Assuming one criterion fits all systems.** Interactive, batch, and real-time systems want different things.

## Revision notes

- Processes alternate CPU bursts and I/O bursts; I/O-bound processes have short bursts, CPU-bound ones long bursts.
- Long-term scheduler: admission. Medium-term: swapping. Short-term: picks the next ready process.
- Decisions occur when a process blocks, is preempted, becomes ready, or terminates; non-preemptive schedulers act only when it blocks or terminates.
- Dispatcher: context switch, switch to user mode, jump to the saved PC; its delay is dispatch latency.
- Turnaround = completion − arrival; waiting = turnaround − burst; response = first run − arrival.
- FCFS is simple and non-preemptive, but suffers from the convoy effect.

## Practice questions

:::question basic
Define turnaround time, waiting time, and response time.
:::answer
Turnaround time is the total time from a process's arrival to its completion. Waiting time is the part of that time the process spends in the ready queue, ready to run but not running; for a process with one CPU burst it equals turnaround minus the burst length. Response time is the time from arrival until the process first gets the CPU.
:::

:::question basic
What three steps does the dispatcher perform?
:::answer
It switches context (saving the state of the old process and loading the state of the new one), switches the CPU to user mode, and jumps to the proper location in the new process, its saved program counter, so that it resumes where it left off.
:::

:::question intermediate
Processes A (arrival 0, burst 4), B (arrival 1, burst 3), and C (arrival 2, burst 1) are scheduled FCFS. Compute each process's turnaround and waiting time, and the averages.
:::answer
A runs 0 to 4, B runs 4 to 7, C runs 7 to 8. Turnaround: A $4 - 0 = 4$, B $7 - 1 = 6$, C $8 - 2 = 6$; average $16/3 \approx 5.33$. Waiting: A $4 - 4 = 0$, B $6 - 3 = 3$, C $6 - 1 = 5$; average $8/3 \approx 2.67$.
:::

:::question intermediate
Explain the convoy effect and why it lowers both CPU and device utilization in a mix of CPU-bound and I/O-bound processes.
:::answer
Under FCFS, a CPU-bound process with a long burst holds the CPU while all the I/O-bound processes finish their I/O and line up behind it in the ready queue. During that time the I/O devices are idle, because every I/O-bound process is waiting for the CPU. When the CPU-bound process finally blocks for I/O, the short processes run quickly and all block on I/O, so now the CPU is idle while they wait. The processes move together like a convoy behind a slow truck, and neither the CPU nor the devices are kept busy.
:::

:::question intermediate
Under which of the four scheduling circumstances must a scheduler make a decision, and which ones distinguish a preemptive scheduler?
:::answer
A decision is required when the running process switches to waiting or terminates, because the CPU becomes free. A non-preemptive scheduler decides only then. A preemptive scheduler may also decide when a running process is interrupted (running to ready, such as a timer interrupt) and when a waiting process becomes ready (waiting to ready), possibly taking the CPU away from the process that is running.
:::

:::question advanced
A dispatcher takes 0.1 ms per context switch. Processes run for exactly 10 ms before being switched. What is the CPU utilization? What happens if the time slice is reduced to 0.5 ms, and what does this suggest about choosing a time slice?
:::answer
With 10 ms slices, each cycle is $10 + 0.1 = 10.1$ ms, of which 10 ms is useful: utilization $= 10/10.1 \approx 99.0\%$. With 0.5 ms slices, utilization $= 0.5/0.6 \approx 83.3\%$, so a sixth of the CPU is lost to switching. Shorter slices improve response time but waste more time on overhead, so the slice should be long compared with the dispatch latency yet short enough that interactive processes respond promptly; typical values are a few milliseconds.
:::

## Further learning

- **Next:** *Preemptive Scheduling Algorithms* compares SJF, SRTF, priority, and round-robin scheduling using these metrics.
- **Related:** *Process Control Block & Lifecycle* explains the state transitions that trigger scheduling decisions.
- **Related:** *Kernel vs User Threads* discusses what exactly the kernel schedules.
