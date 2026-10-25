---
lesson: kernel-vs-user-threads-concurrency
title: Kernel vs User Threads and Concurrency Models
summary: What threads share and what each owns, why they are cheaper than processes, how user-level and kernel-level threads differ, and how the many-to-one, one-to-one, and many-to-many models map one onto the other.
minutes: 45
type: theory
objectives:
  - Explain what the threads of a process share and what each thread owns, and why threads are cheaper than processes
  - Distinguish concurrency from parallelism and estimate multicore speedup with Amdahl's law
  - Contrast user-level threads with kernel-level threads, including their behaviour on blocking system calls
  - Compare the many-to-one, one-to-one, and many-to-many threading models and identify where each is used
---

## Introduction

A web browser downloads images while you scroll, a word processor checks spelling while you type, and a server handles thousands of clients at once. Each of these programs needs to do several things at the same time, and all of those activities work on the same data: the same page, the same document, the same cache.

Separate processes are a poor fit. They do not share memory by default, and creating and switching between them is relatively expensive. **Threads** solve this. A thread is a single sequence of execution inside a process; one process can contain many threads that run concurrently and share its memory. Threads can be managed entirely by a library in user space or by the kernel, and the choice affects performance, parallelism, and what happens when a thread blocks. This lesson explains those choices.

**Before you start:** you should know the process abstraction, the process control block, and context switches.

## Core theory

### What threads share and what they own

| Shared by all threads of a process | Private to each thread |
| :--- | :--- |
| code (text) | thread ID |
| global and static data | program counter |
| heap | register set |
| open files and sockets | stack (local variables, call frames) |
| address space and memory mappings | thread-local storage |
| signal handlers, working directory, user ID | scheduling state and priority |

The kernel describes each thread with a **thread control block (TCB)** holding its private state, while the process's shared resources stay in the PCB.

### Why threads are cheaper

- **Creation** needs only a new stack and TCB, not a new address space, page tables, and file table.
- **Switching** between threads of the same process does not change the address space, so the page tables stay loaded and TLB entries stay valid.
- **Communication** is simply reading and writing shared memory, with no pipes or message passing required. (The flip side is that shared data must be **synchronized**, the subject of later lessons.)

### Concurrency and parallelism

- **Concurrency:** several tasks make progress over the same period, possibly by taking turns on one core.
- **Parallelism:** several tasks execute at literally the same instant, on different cores.

A single-core machine can be concurrent but not parallel. Threads give concurrency on any machine and parallelism on multicore machines, as long as the kernel can schedule them on different cores.

**Amdahl's law** limits the benefit of parallelism. If a fraction $S$ of a program is serial and the rest is perfectly parallelisable over $N$ cores, the speedup is at most

$$\text{speedup} \le \frac{1}{S + \dfrac{1 - S}{N}}.$$

As $N \to \infty$ the speedup approaches $1/S$: a program that is 10% serial can never run more than 10 times faster, however many cores it is given.

### User-level threads

**User-level threads (ULTs)** are created, scheduled, and switched by a **thread library** running in user space. The kernel knows nothing about them; it sees one process with one execution context.

- **Fast:** creating and switching threads are ordinary function calls, with no system calls or mode switches.
- **Flexible:** the application can use its own scheduling policy.
- **No parallelism:** the kernel schedules the process as a single unit, so its threads cannot run on two cores at once.
- **Blocking problem:** if one thread makes a blocking system call, such as reading from a slow device, the kernel blocks the whole process, and every other thread stops too. Libraries work around this with non-blocking I/O.

### Kernel-level threads

**Kernel-level threads (KLTs)** are created and scheduled by the kernel, which keeps a TCB for each.

- **True parallelism:** threads of one process can run on different cores simultaneously.
- **Independent blocking:** when one thread blocks, the kernel runs another thread of the same process.
- **Slower operations:** creating, switching, and synchronising threads involve system calls, typically far more expensive than a user-space switch.

### Mapping models

A user-visible thread must eventually run on a kernel-schedulable entity. The **threading model** describes the mapping:

| Model | Mapping | Parallelism | Blocking call | Examples |
| :--- | :--- | :--- | :--- | :--- |
| Many-to-one | many user threads on one kernel thread | none | blocks all threads | early "green threads" libraries |
| One-to-one | each user thread is a kernel thread | yes | blocks only that thread | Linux (NPTL), Windows, Java platform threads |
| Many-to-many | $m$ user threads multiplexed over $n$ kernel threads | yes, up to $n$ | runtime moves other threads to other kernel threads | Go's goroutine scheduler; older Solaris |
| Two-level | many-to-many, plus some threads bound one-to-one | yes | as above | some older UNIX systems |

One-to-one dominates general-purpose systems today because kernel threads became cheap enough. Many-to-many has returned in **language runtimes**: Go schedules goroutines over a small pool of OS threads, and Java 21 introduced **virtual threads** that the JVM multiplexes over carrier platform threads.

### Threads in practice

- **POSIX threads (Pthreads)** is the standard C API on UNIX-like systems: `pthread_create`, `pthread_join`, `pthread_exit`, and synchronization functions. On Linux, each Pthread is a kernel thread created with the `clone` system call.
- **Thread pools** create a fixed number of threads in advance and hand them tasks from a queue, avoiding the cost of creating a thread per request and bounding resource use.
- **Python threads** are kernel threads, but in the standard CPython build a **global interpreter lock (GIL)** lets only one thread execute Python bytecode at a time. Threads therefore speed up I/O-bound Python programs, which release the GIL while waiting, but not CPU-bound pure-Python code, which needs processes or native extensions. Python 3.13 added an experimental free-threaded build without the GIL.

## Worked examples

### Example 1: Threads sharing one address space

```python
import threading

data = list(range(1, 1_000_001))
results = [0] * 4                       # shared by every thread in the process

def partial_sum(index, chunk):
    results[index] = sum(chunk)         # each thread writes only its own slot

size = len(data) // 4
threads = [threading.Thread(target=partial_sum, args=(i, data[i * size:(i + 1) * size]))
           for i in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()                            # wait for every thread to finish

total = sum(results)
print(results)
print(total, total == len(data) * (len(data) + 1) // 2)
```

Output:

```text
[31250125000, 93750125000, 156250125000, 218750125000]
500000500000 True
```

All four threads read the same `data` list and write into the same `results` list without copying anything, because they share the process's heap. Each thread writes a different element, so no two threads touch the same memory location and no lock is needed. `join` makes the main thread wait until every worker has finished before it reads the results. (In standard CPython this CPU-bound work would not run faster with threads, because of the GIL, but the sharing it shows is the same in any language.)

### Example 2: A user-level thread scheduler

Generators let a Python program build its own tiny user-level thread library: each "thread" runs until it voluntarily yields, and a scheduler loop picks the next one. The kernel sees only one thread throughout.

```python
from collections import deque

def worker(name, steps):
    for i in range(steps):
        print(f"{name} step {i}")
        yield                            # give up the CPU: a user-level context switch

ready = deque([worker("A", 3), worker("B", 2), worker("C", 1)])
while ready:
    thread = ready.popleft()
    try:
        next(thread)                     # run the thread until its next yield
        ready.append(thread)             # back of the ready queue
    except StopIteration:
        pass                             # the thread has finished
```

Output:

```text
A step 0
B step 0
C step 0
A step 1
B step 1
A step 2
```

The scheduler implements round-robin entirely in user space: switching threads costs a function call, not a system call. But the model's weaknesses are visible too. A thread that never yields would starve the others, because nothing can preempt it; and if any thread called a blocking operation such as `time.sleep(5)`, the whole program, and so every "thread", would stop for five seconds. This is the many-to-one model's blocking problem.

### Example 3: Amdahl's law

```python
def amdahl(serial_fraction, cores):
    return 1 / (serial_fraction + (1 - serial_fraction) / cores)

for s in (0.05, 0.25):
    speedups = ", ".join(f"{n} cores: {amdahl(s, n):.2f}" for n in (2, 4, 16, 1024))
    print(f"serial {s:.0%} -> {speedups}; limit {1 / s:.0f}")
```

Output:

```text
serial 5% -> 2 cores: 1.90, 4 cores: 3.48, 16 cores: 9.14, 1024 cores: 19.64; limit 20
serial 25% -> 2 cores: 1.60, 4 cores: 2.29, 16 cores: 3.37, 1024 cores: 3.99; limit 4
```

With 25% of the work serial, four cores give only a 2.29× speedup, and even 1024 cores cannot reach 4×. Adding threads is not enough; shrinking the serial part, such as code that holds a single lock, is what raises the ceiling.

### Example 4: Creating kernel threads with Pthreads

On a UNIX-like system, this C program starts two kernel threads (compile with `-pthread`):

```c
#include <pthread.h>
#include <stdio.h>

static long squares[2];                 /* shared: global data is visible to all threads */

static void *square(void *arg) {
    long n = (long)arg;                 /* private: each thread has its own stack */
    squares[n - 1] = n * n;
    return NULL;
}

int main(void) {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, square, (void *)1L);
    pthread_create(&t2, NULL, square, (void *)2L);
    pthread_join(t1, NULL);             /* wait for both threads */
    pthread_join(t2, NULL);
    printf("%ld %ld\n", squares[0], squares[1]);   /* prints: 1 4 */
    return 0;
}
```

On Linux, each `pthread_create` makes a `clone` system call that creates a kernel-schedulable task sharing the process's address space, which is the one-to-one model. The two threads may run in parallel on different cores, and if one blocks, the other keeps running.

## Applications

- **Servers** use thread pools so that each request is handled by a thread without paying thread-creation costs per request.
- **Interactive applications** keep a responsive user-interface thread while worker threads do slow work such as loading files or rendering.
- **Parallel computation:** scientific codes, video encoders, and databases split work across one kernel thread per core.
- **Language runtimes:** Go's goroutines and Java's virtual threads use many-to-many scheduling to support hundreds of thousands of lightweight tasks.
- **Asynchronous frameworks** such as Python's `asyncio` apply the user-level, cooperative idea of Example 2 with non-blocking I/O to avoid the blocking problem.

## Common mistakes

- **Assuming threads have separate memory.** Globals and heap objects are shared; only stacks, registers, and thread-local storage are private.
- **Expecting user-level threads to use several cores.** The kernel schedules their process as one unit.
- **Forgetting that one blocking call stalls every thread in the many-to-one model.**
- **Expecting linear speedup from more threads.** Amdahl's law, locking, and memory bandwidth limit it.
- **Using threads for CPU-bound pure-Python code in standard CPython** and expecting a speedup; the GIL serialises bytecode execution.

## Revision notes

- Threads share code, data, heap, and open files; each has its own ID, program counter, registers, and stack.
- Threads are cheaper than processes to create and switch, and communicate through shared memory (which needs synchronization).
- Concurrency = progress over the same period; parallelism = execution at the same instant on several cores.
- Amdahl: speedup $\le 1 / (S + (1 - S)/N)$, with limit $1/S$.
- User-level threads: fast, no kernel support, no parallelism, a blocking call blocks all. Kernel-level threads: parallel, independent blocking, costlier operations.
- Models: many-to-one, one-to-one (Linux, Windows), many-to-many (Go, Java virtual threads), two-level.

## Practice questions

:::question basic
Name three things the threads of one process share and three things each thread has to itself.
:::answer
Shared: the code, the global data and heap, and the open files (also the address space, signal handlers, and working directory). Private: the program counter, the register set, and the stack (also the thread ID and thread-local storage). Each thread needs its own stack because it has its own sequence of function calls.
:::

:::question basic
Why is switching between two threads of the same process usually faster than switching between two processes?
:::answer
Both threads use the same address space, so the kernel does not need to load new page tables, and the TLB entries for the process remain valid. Only the registers, program counter, and stack pointer change. A process switch must also change the memory context, which flushes or invalidates translation caches and usually leaves the caches cold for the new process.
:::

:::question intermediate
A program is 20% serial. What speedup can it reach on 8 cores, and what is the best speedup possible on any number of cores?
:::answer
Speedup $= 1 / (0.2 + 0.8/8) = 1 / (0.2 + 0.1) = 1/0.3 \approx 3.33$. As the number of cores grows, the parallel term vanishes and the speedup approaches $1/0.2 = 5$. Eight cores therefore give one third of the cores' worth of improvement, and no number of cores can exceed a fivefold speedup.
:::

:::question intermediate
In the many-to-one model, one thread calls `read()` on a network socket with no data available. What happens to the other threads, and how do one-to-one and many-to-many models behave differently?
:::answer
In many-to-one, the kernel sees only one schedulable entity, so the blocking `read` blocks the whole process and every other user thread stops until data arrives. In one-to-one, only the kernel thread that called `read` blocks; the kernel keeps scheduling the process's other threads. In many-to-many, the runtime notices the blocked kernel thread and continues running the other user threads on the remaining kernel threads, possibly creating another kernel thread to keep the pool busy.
:::

:::question intermediate
Why does Go use a many-to-many model for goroutines instead of making each goroutine a kernel thread?
:::answer
Programs may create hundreds of thousands of goroutines. Kernel threads each need a kernel data structure and a stack of fixed, relatively large size, and creating or switching them requires system calls, so that many kernel threads would waste memory and time. Goroutines start with small, growable stacks and are switched by the Go runtime in user space, which is much cheaper. Multiplexing them over a pool of kernel threads, roughly one per core, still gives parallelism, and the runtime moves goroutines off a kernel thread that blocks in a system call.
:::

:::question advanced
A CPU-bound image filter written in pure Python runs no faster with 4 threads on a 4-core machine in standard CPython. Explain why, and propose two ways to use all four cores.
:::answer
Standard CPython has a global interpreter lock: only one thread at a time can execute Python bytecode. The four threads take turns holding the GIL, so the computation is effectively serial, and switching between them adds overhead. To use the cores, run the work in separate processes (for example with `multiprocessing` or `concurrent.futures.ProcessPoolExecutor`), each with its own interpreter and GIL; or move the inner loop into native code that releases the GIL, such as NumPy operations, which process whole arrays in C. (The experimental free-threaded build of Python 3.13 removes the GIL, but it is not the default.)
:::

## Further learning

- **Next:** *Scheduling Criteria & Dispatcher* explains how the kernel decides which ready thread runs next.
- **Related:** *Critical Section Problem & Mutexes* covers the race conditions that shared memory makes possible.
- **Related:** *Process Control Block & Lifecycle* describes the process structure that threads live inside.
