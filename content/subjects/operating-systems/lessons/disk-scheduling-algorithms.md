---
lesson: disk-scheduling-algorithms
title: Disk Scheduling Algorithms
summary: Why the order of disk requests matters for hard drives, how seek time, rotational latency, and transfer time add up, and how FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK compare by total head movement and fairness.
minutes: 45
type: theory
objectives:
  - Compute the access time of a hard-disk request from its seek time, rotational latency, and transfer time
  - Schedule a queue of cylinder requests with FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK and compute total head movement
  - Compare the algorithms by throughput, response-time variance, and starvation
  - Explain why solid-state drives need different scheduling and what modern operating systems do
---

## Introduction

A hard disk drive stores data on spinning platters, read by heads mounted on an arm that must physically move across the disk. Moving the arm takes milliseconds, millions of times longer than a CPU instruction. When many processes have requests waiting for the same disk, the order in which they are served can easily double or halve the total time spent moving the arm.

**Disk scheduling** is the operating system's job of choosing that order. The classic algorithms are elevator-like: they balance the efficiency of serving nearby requests first against the fairness of not leaving distant requests waiting forever. This lesson computes the cost of disk accesses, runs every classic algorithm on the same request queue, and then explains why solid-state drives, which have no moving parts, changed the picture.

**Before you start:** you should know how DMA transfers data and the idea of queues of waiting I/O requests.

## Core theory

### How a hard disk works

- Data lies on **tracks**, concentric circles on each platter surface. The tracks at the same position on all surfaces form a **cylinder**.
- Each track is divided into **sectors**, traditionally 512 bytes and now usually 4096 bytes.
- To read a sector, the drive must move the arm to the right cylinder (**seek**), wait for the sector to rotate under the head (**rotational latency**), and then read it as it passes (**transfer**).

$$\text{access time} = \text{seek time} + \text{rotational latency} + \text{transfer time}.$$

Average rotational latency is half a revolution: at 7200 revolutions per minute, one revolution takes $60 / 7200 = 8.33$ ms, so the average wait is about 4.17 ms. Seek times average several milliseconds. Transfer time for a few kilobytes is tiny by comparison. Seek time is the component the OS can influence, by ordering requests so that the arm moves less. Since seek time grows with seek distance, algorithms are compared by the **total head movement**, measured in cylinders.

### The algorithms

All examples use a disk with cylinders 0 to 199, the head at cylinder 53, and the queue 98, 183, 37, 122, 14, 124, 65, 67 (in arrival order).

- **FCFS (first-come, first-served):** serve requests in arrival order. Fair and simple, but the head swings back and forth across the disk.
- **SSTF (shortest seek time first):** always serve the pending request nearest the current head position. Much less movement than FCFS, but like shortest-job-first it can **starve** distant requests if nearby requests keep arriving.
- **SCAN (the elevator algorithm):** move the head in one direction, serving every request on the way, all the way to the end of the disk, then reverse. No starvation; every request is served within two sweeps.
- **C-SCAN (circular SCAN):** move in one direction serving requests; at the end, return to the other end **without serving** anything, and sweep again in the same direction. Waiting times are more uniform than SCAN's, because SCAN serves the middle of the disk twice as often as the edges.
- **LOOK and C-LOOK:** like SCAN and C-SCAN, but the head reverses (or returns) at the last pending request in each direction instead of travelling to the physical end of the disk.

SCAN and C-SCAN as defined here travel to the end of the disk; in practice, implementations behave like LOOK and C-LOOK. Textbooks also differ on whether the return sweep of C-SCAN and C-LOOK counts as head movement; the totals below include it, because the arm really does move.

### Comparing the algorithms

| Algorithm | Movement | Starvation | Response-time variance |
| :--- | :--- | :--- | :--- |
| FCFS | high | none | depends on arrival order |
| SSTF | low | possible | high |
| SCAN / LOOK | low | none | moderate (edges wait longer) |
| C-SCAN / C-LOOK | low to moderate | none | lowest |

### Solid-state drives

An SSD has no arm and no rotation; the time to read a block hardly depends on its address, so minimising seek distance is pointless. SSDs also contain many flash chips that work in parallel and can accept many requests at once, and they perform their own internal scheduling. Operating systems therefore use simpler policies for them: Linux offers schedulers such as `none` (pass requests straight through), `mq-deadline` (which guarantees each request a maximum wait), and BFQ (which shares bandwidth fairly between processes). The concerns become fairness, deadlines, and merging adjacent requests rather than seek distance.

## Worked examples

### Example 1: Access time of one request

A 7200 RPM drive has an average seek time of 9 ms and transfers 150 MB per second. How long does a random 4 KiB read take?

```python
rpm, seek_ms, rate_bytes = 7200, 9.0, 150_000_000
rotation_ms = 60_000 / rpm
latency_ms = rotation_ms / 2                     # on average, wait half a revolution
transfer_ms = 4096 / rate_bytes * 1000
total = seek_ms + latency_ms + transfer_ms
print(f"rotation {rotation_ms:.2f} ms, latency {latency_ms:.2f} ms, transfer {transfer_ms:.3f} ms")
print(f"access time {total:.2f} ms, about {1000 / total:.0f} random reads per second")
```

Output:

```text
rotation 8.33 ms, latency 4.17 ms, transfer 0.027 ms
access time 13.19 ms, about 76 random reads per second
```

Seek and rotation account for over 99% of the time; reading the data itself takes 27 µs. A hard disk can therefore manage only around 76 random 4 KiB reads per second, about 300 KB per second, even though it can stream sequential data at 150 MB per second. Reducing seek distance, and placing related data close together, is what disk scheduling and file-system layout are for.

### Example 2: All six algorithms on one queue

```python
def movement(path):
    return sum(abs(b - a) for a, b in zip(path, path[1:]))

def fcfs(head, requests):
    return [head] + requests

def sstf(head, requests):
    pending, path = list(requests), [head]
    while pending:
        nearest = min(pending, key=lambda r: (abs(r - path[-1]), r))
        pending.remove(nearest)
        path.append(nearest)
    return path

def split(head, requests):
    return sorted(r for r in requests if r < head), sorted(r for r in requests if r >= head)

def scan_down(head, requests):          # towards cylinder 0 first, all the way to the edge
    below, above = split(head, requests)
    return [head] + below[::-1] + [0] + above

def look_up(head, requests):            # towards higher cylinders, reversing at the last request
    below, above = split(head, requests)
    return [head] + above + below[::-1]

def c_scan(head, requests, last=199):   # up to the edge, jump back to 0, continue upwards
    below, above = split(head, requests)
    return [head] + above + [last, 0] + below

def c_look(head, requests):             # up to the last request, jump to the lowest request
    below, above = split(head, requests)
    return [head] + above + below

queue, head = [98, 183, 37, 122, 14, 124, 65, 67], 53
for name, schedule in [("FCFS", fcfs), ("SSTF", sstf), ("SCAN (down)", scan_down),
                       ("LOOK (up)", look_up), ("C-SCAN", c_scan), ("C-LOOK", c_look)]:
    path = schedule(head, queue)
    print(f"{name:11} {movement(path):>4} cylinders  {path}")
```

Output:

```text
FCFS         640 cylinders  [53, 98, 183, 37, 122, 14, 124, 65, 67]
SSTF         236 cylinders  [53, 65, 67, 37, 14, 98, 122, 124, 183]
SCAN (down)  236 cylinders  [53, 37, 14, 0, 65, 67, 98, 122, 124, 183]
LOOK (up)    299 cylinders  [53, 65, 67, 98, 122, 124, 183, 37, 14]
C-SCAN       382 cylinders  [53, 65, 67, 98, 122, 124, 183, 199, 0, 14, 37]
C-LOOK       322 cylinders  [53, 65, 67, 98, 122, 124, 183, 14, 37]
```

FCFS moves the head 640 cylinders, swinging from 183 to 37 to 122 to 14. SSTF and SCAN (moving towards 0 first) both need 236. The direction matters for SCAN-like algorithms: here most requests lie above 53, so heading down first and sweeping up once is cheap, while LOOK heading up first must come all the way back for 37 and 14. C-SCAN's total includes the 199-cylinder return sweep from the top edge to cylinder 0; excluding it, the arm moves 183 cylinders while serving requests. C-LOOK avoids the trips to the physical edges and jumps from 183 straight to 14.

### Example 3: How SSTF can starve a request

The head is at cylinder 100, a request is waiting at cylinder 190, and new requests keep arriving near the head.

| Time | Head | Pending requests | SSTF serves |
| :--- | :--- | :--- | :--- |
| 1 | 100 | 190, 104 | 104 |
| 2 | 104 | 190, 98 | 98 |
| 3 | 98 | 190, 101 | 101 |
| 4 | 101 | 190, 97 | 97 |

As long as a closer request is always waiting, the request for cylinder 190 is never chosen. Under SCAN, the head would continue in its current direction and reach 190 within one sweep, whatever new requests arrived. Production schedulers add **deadlines** for the same reason: a request that has waited too long is served next regardless of position.

## Applications

- **Operating systems:** Linux's I/O schedulers (`mq-deadline`, BFQ, kyber, or `none`) choose orderings and deadlines per device; elevator-style sorting is still used for hard disks.
- **Drive firmware:** hard disks reorder requests internally using native command queuing (NCQ), which knows the exact rotational position.
- **Databases** lay out tables and logs to turn random I/O into sequential I/O, the same principle as minimising seeks.
- **Elevators and robotic arms:** the SCAN idea originated with, and still applies to, physical systems that serve requests along a line.
- **Capacity planning:** knowing that a hard disk manages on the order of 100 random operations per second explains why SSDs transformed database and virtual-machine performance.

## Common mistakes

- **Forgetting the starting head position** when summing movements, or adding up requested cylinder numbers instead of the distances between consecutive positions.
- **Moving SCAN only to the last request.** That is LOOK; SCAN travels to the end of the disk before reversing.
- **Not stating whether C-SCAN's return sweep counts,** which leads to different totals for the same schedule.
- **Assuming SSTF is optimal.** It is greedy: it minimises each step, not the total, and it can starve requests.
- **Applying seek-based scheduling to SSDs,** where address order barely affects access time.

## Revision notes

- Access time = seek + rotational latency (average half a revolution) + transfer. Seek and rotation dominate.
- FCFS: arrival order; fair; large movement.
- SSTF: nearest request first; low movement; can starve far requests.
- SCAN: sweep to the end and reverse (elevator). C-SCAN: sweep one way, return without serving. LOOK and C-LOOK stop at the last request.
- Classic queue (head 53, cylinders 0 to 199): FCFS 640, SSTF 236, SCAN towards 0: 236.
- SSDs have no seek penalty; schedulers focus on fairness, deadlines, and parallelism.

## Practice questions

:::question basic
What are the three components of a hard-disk access time, and which one does disk scheduling try to reduce?
:::answer
Seek time (moving the arm to the right cylinder), rotational latency (waiting for the sector to rotate under the head), and transfer time (reading the data). Disk scheduling reduces seek time by ordering requests so that the arm travels shorter distances.
:::

:::question basic
What is the average rotational latency of a 5400 RPM disk?
:::answer
One revolution takes $60 / 5400 = 0.01111$ s, about 11.1 ms. On average the desired sector is half a revolution away, so the average rotational latency is about 5.56 ms.
:::

:::question intermediate
The head is at cylinder 50, and the queue is 82, 170, 43, 140, 24, 16, 190. Compute the total head movement for FCFS and SSTF.
:::answer
FCFS: $|82 - 50| + |170 - 82| + |43 - 170| + |140 - 43| + |24 - 140| + |16 - 24| + |190 - 16| = 32 + 88 + 127 + 97 + 116 + 8 + 174 = 642$ cylinders. SSTF from 50: 43 (7), 24 (19), 16 (8), 82 (66), 140 (58), 170 (30), 190 (20), a total of 208 cylinders.
:::

:::question intermediate
For the same queue and head position (50), with the head moving towards higher cylinders on a disk with cylinders 0 to 199, compute the movement for LOOK and C-LOOK, counting C-LOOK's jump.
:::answer
LOOK: up through 82, 140, 170, 190 (that is $190 - 50 = 140$ cylinders), then reverse down to 43, 24, 16 ($190 - 16 = 174$), a total of 314. C-LOOK: up to 190 (140 cylinders), jump to the lowest request, 16 ($190 - 16 = 174$), then up to 24 and 43 ($43 - 16 = 27$), a total of 341.
:::

:::question intermediate
Why does C-SCAN give more uniform waiting times than SCAN?
:::answer
In SCAN, after the head reverses at one edge, the requests just behind it near that edge must wait for the head to cross the whole disk and come back, while requests in the middle are passed twice per round trip. So waits depend on position. C-SCAN always sweeps in the same direction and returns quickly to the start, treating the cylinders as a circle; every position is visited once per sweep, so the maximum and average waits are about the same everywhere.
:::

:::question advanced
A database runs on an SSD. A colleague suggests enabling SSTF-style scheduling to improve its performance. Explain why this is unlikely to help and what matters instead.
:::answer
SSTF reduces seek distance, but an SSD has no mechanical seek or rotational latency: reading a block costs about the same wherever it is, so reordering by address saves almost nothing while adding CPU work and the risk of starving requests. What matters for SSDs is keeping enough requests in flight to use their internal parallelism (many flash chips working at once), merging adjacent requests, fairness between processes, and bounding each request's latency, which is why Linux typically uses `none` or `mq-deadline` for SSDs.
:::

## Further learning

- **Next:** *Access Control & OS Security Fundamentals* covers how the operating system protects files and other resources.
- **Related:** *Direct Memory Access (DMA) & Interrupts* explains how each scheduled request is carried out.
- **Related:** *Preemptive Scheduling Algorithms* applies the same efficiency-versus-fairness ideas to the CPU.
