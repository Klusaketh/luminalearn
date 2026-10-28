---
lesson: critical-section-problem
title: The Critical Section Problem and Mutexes
summary: How race conditions arise when threads share data, the three requirements for a correct critical-section solution, Peterson's algorithm, atomic hardware instructions, and mutex locks.
minutes: 50
type: theory
objectives:
  - Explain how a race condition arises from interleaved machine instructions and show a lost update
  - State the mutual exclusion, progress, and bounded waiting requirements for a critical-section solution
  - Analyse Peterson's algorithm and incorrect alternatives by exploring their interleavings
  - Describe test-and-set, compare-and-swap, spinlocks, and blocking mutexes, and choose between spinning and sleeping
---

## Introduction

Two threads each add 1 to a shared counter that starts at 0. Afterwards, the counter should be 2. Yet sometimes it is 1. Nothing is wrong with either thread's code on its own; the problem is the **timing** of their steps relative to each other. A bug whose outcome depends on timing is a **race condition**, and it is one of the hardest kinds of bug to find, because it may appear once in a million runs, on one customer's machine, and vanish when you add a print statement to look for it.

The cure is to make sure that only one thread at a time can execute the code that touches the shared data, the **critical section**. This lesson shows exactly how races happen, defines what a correct solution must guarantee, examines a classic software solution, Peterson's algorithm, and then describes how real systems use **atomic hardware instructions** to build **locks**.

**Before you start:** you should know what threads share and that the scheduler can preempt a thread at any instruction.

## Core theory

### How a race happens

A statement such as `counter = counter + 1` usually compiles to three machine instructions:

```text
load  r, counter     ; read the shared value into a private register
add   r, r, 1        ; increment the private copy
store counter, r     ; write it back
```

If thread A is preempted after its `load`, thread B can load the same old value, increment it, and store it; when A resumes, it stores its own stale result, overwriting B's update. One increment is lost. Whether this happens depends on where the preemption falls, which is why the bug is intermittent. On a multicore machine the two threads can also run truly simultaneously, making the window even wider.

### The critical-section problem

Each thread's code has the structure:

```text
loop:
    entry section        ; ask permission
    critical section     ; access the shared data
    exit section         ; announce leaving
    remainder section    ; everything else
```

A correct solution must satisfy three requirements, without assuming anything about the relative speeds of the threads or the number of CPUs:

1. **Mutual exclusion:** at most one thread is in its critical section at any time.
2. **Progress:** if no thread is in its critical section and some threads want to enter, the choice of who enters next cannot be postponed indefinitely, and only threads that are trying to enter take part in it. A thread in its remainder section must not be able to block others.
3. **Bounded waiting:** after a thread asks to enter, there is a limit on how many times other threads can enter before it does. No thread starves.

### Attempts that fail

- **Test, then set a lock variable:** `while lock: pass` followed by `lock = True`. Both threads can see `lock == False` before either sets it, and both enter. The test and the set must be one indivisible step.
- **Strict alternation:** a shared `turn` variable says whose turn it is, and each thread waits until `turn` is its own and passes the turn on when it leaves. Mutual exclusion holds, but **progress** fails: if one thread is busy in its remainder section, the other cannot enter twice in a row.
- **Flags only:** each thread sets `flag[i] = True` and waits while the other's flag is set. Mutual exclusion holds, but if both set their flags at the same time, each waits for the other forever: a **deadlock**.

### Peterson's solution

Peterson's algorithm (Gary Peterson, 1981) combines the flags with a `turn` variable for two threads, $i$ and $j = 1 - i$:

```text
flag[i] = true          ; I want to enter
turn = j                ; but you may go first
while flag[j] and turn == j:
    wait
critical section
flag[i] = false         ; I am done
```

If both threads want to enter, `turn` was written last by one of them, and that thread politely waits; the other enters. This gives mutual exclusion, progress, and bounded waiting: after one thread leaves its critical section, the waiting thread enters before the leaving thread can enter again.

Peterson's algorithm is important for understanding, but it is **not used as-is on modern hardware**. Processors and compilers reorder memory operations for speed, so one thread may not see the other's writes in program order. Correct use requires **memory barriers**, and it only handles two threads. Practical systems use hardware support instead.

### Hardware support

- **Disabling interrupts** prevents preemption on a single-core machine, so a kernel can use it for very short critical sections. It does not work on multicore systems (other cores keep running) and is a privileged instruction, unavailable to user programs.
- **Atomic instructions** read and modify memory in one indivisible step, even across cores:
    - `test_and_set(&x)` sets `x` to true and returns its old value.
    - `compare_and_swap(&x, expected, new)` (CAS) sets `x` to `new` only if it currently equals `expected`, and returns the old value. x86 provides it as `cmpxchg`.

A **spinlock** built on test-and-set:

```text
acquire(lock):  while test_and_set(&lock): spin
release(lock):  lock = false
```

### Mutex locks: spinning versus sleeping

A **mutex** (mutual exclusion lock) offers `acquire` and `release`; only the holder may release it.

- A **spinning** lock busy-waits, repeatedly testing the lock. It wastes CPU time while waiting, but has no context-switch cost, so it is good on multicore systems when critical sections are very short (shorter than two context switches).
- A **blocking** (sleeping) lock puts the waiting thread in a wait queue and lets the CPU run something else; the release wakes a waiter. This is better when critical sections may be long, or on a single core, where spinning is pointless because the holder cannot run while the spinner spins.

Many real mutexes are **hybrids**: they spin briefly and then sleep. Linux's futex-based Pthread mutexes, for example, need a system call only when there is contention.

Good locking practice: keep critical sections short, protect each piece of shared data with a clearly identified lock, and release locks on every path, including errors (Python's `with lock:` does this automatically).

## Worked examples

### Example 1: Counting the interleavings of two increments

Each thread executes `load`, `add`, `store` with its own register. This program tries every possible interleaving of the two threads' six instructions and records the final counter.

```python
from itertools import combinations

def run(order):
    counter, register, pc = 0, [0, 0], [0, 0]
    for t in order:                       # t is the thread that executes the next instruction
        if pc[t] == 0:
            register[t] = counter         # load
        elif pc[t] == 1:
            register[t] += 1              # add
        else:
            counter = register[t]         # store
        pc[t] += 1
    return counter

outcomes = {}
for slots in combinations(range(6), 3):   # choose which 3 of the 6 steps belong to thread 0
    order = [0 if step in slots else 1 for step in range(6)]
    final = run(order)
    outcomes[final] = outcomes.get(final, 0) + 1
print(sum(outcomes.values()), "interleavings:", dict(sorted(outcomes.items())))
```

Output:

```text
20 interleavings: {1: 18, 2: 2}
```

There are $\binom{6}{3} = 20$ ways to interleave the two threads, and only 2 of them, the ones in which one thread runs all three instructions before the other starts, produce the correct result. In the other 18, the second load reads the counter before the first store, and an update is lost. Making the three instructions one indivisible critical section leaves only the two correct orders.

### Example 2: Checking lock algorithms exhaustively

The program below models two threads as small state machines and explores **every** reachable state, checking whether both threads can be in the critical section together, and whether some state is stuck (no thread can ever change it).

```python
from collections import deque

def explore(step, initial):
    seen, queue = {initial}, deque([initial])
    violations, stuck = 0, 0
    while queue:
        state = queue.popleft()
        if state[0] == state[1] == "cs":
            violations += 1                     # both threads in the critical section
        successors = {step(state, i) for i in (0, 1)}
        if successors == {state}:
            stuck += 1                          # neither thread can ever move again
        for nxt in successors - seen:
            seen.add(nxt)
            queue.append(nxt)
    return len(seen), violations, stuck

def test_then_set(state, i):
    pcs, lock = list(state[:2]), state[2]
    if pcs[i] == "test":
        pcs[i] = "set" if lock == 0 else "test"
    elif pcs[i] == "set":
        lock, pcs[i] = 1, "cs"
    elif pcs[i] == "cs":
        pcs[i] = "release"
    elif pcs[i] == "release":
        lock, pcs[i] = 0, "test"
    return (pcs[0], pcs[1], lock)

def flags_only(state, i):
    pcs, flags, j = list(state[:2]), list(state[2]), 1 - i
    if pcs[i] == "want":
        flags[i], pcs[i] = True, "wait"
    elif pcs[i] == "wait":
        if not flags[j]:
            pcs[i] = "cs"
    elif pcs[i] == "cs":
        pcs[i] = "leave"
    elif pcs[i] == "leave":
        flags[i], pcs[i] = False, "want"
    return (pcs[0], pcs[1], tuple(flags))

def peterson(state, i):
    pcs, flags, turn, j = list(state[:2]), list(state[2]), state[3], 1 - i
    if pcs[i] == "want":
        flags[i], pcs[i] = True, "yield"
    elif pcs[i] == "yield":
        turn, pcs[i] = j, "wait"
    elif pcs[i] == "wait":
        if not (flags[j] and turn == j):
            pcs[i] = "cs"
    elif pcs[i] == "cs":
        pcs[i] = "leave"
    elif pcs[i] == "leave":
        flags[i], pcs[i] = False, "want"
    return (pcs[0], pcs[1], tuple(flags), turn)

for name, step, initial in [
    ("test-then-set lock", test_then_set, ("test", "test", 0)),
    ("flags only", flags_only, ("want", "want", (False, False))),
    ("Peterson", peterson, ("want", "want", (False, False), 0)),
]:
    states, violations, stuck = explore(step, initial)
    print(f"{name:18} states={states:>3} both-in-critical-section={violations} stuck={stuck}")
```

Output:

```text
test-then-set lock states= 24 both-in-critical-section=1 stuck=0
flags only         states= 12 both-in-critical-section=0 stuck=1
Peterson           states= 26 both-in-critical-section=0 stuck=0
```

The test-then-set lock can reach a state with both threads in the critical section: both test the lock while it is free, then both set it. The flags-only algorithm never violates mutual exclusion, but it can reach a state in which both flags are set and both threads wait forever, a deadlock that violates progress. Peterson's algorithm avoids both problems in all 26 reachable states. This kind of exhaustive search over interleavings, called **model checking**, is how concurrent algorithms are verified in practice, because testing by running the code rarely hits the bad interleavings. (The model assumes each step is atomic and memory is sequentially consistent, which real hardware does not guarantee without barriers.)

### Example 3: A mutex around the critical section

```python
import threading

counter = 0
lock = threading.Lock()

def work(n):
    global counter
    for _ in range(n):
        with lock:                       # entry section: acquire; exit section: release
            counter += 1                 # critical section

threads = [threading.Thread(target=work, args=(100_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter)
```

Output:

```text
400000
```

With the lock, every increment happens inside a critical section that only one thread can occupy, so the result is always exactly 400,000. The `with` statement releases the lock even if the critical section raises an exception, which avoids a classic bug in which an error path leaves a lock held forever.

## Applications

- **Every multithreaded program** that shares data (a web server's cache, a game's world state, a bank's account balances) needs critical sections.
- **Operating system kernels** protect their own data structures, such as ready queues and file tables, with spinlocks and mutexes.
- **Lock-free data structures** use compare-and-swap directly to update shared queues and counters without locks.
- **Databases** use locks (and latches, their short-term internal equivalent) to keep concurrent transactions from corrupting data.
- **Priority inversion fixes:** real-time systems use priority-inheritance mutexes; a well-known priority inversion bug on NASA's Mars Pathfinder lander in 1997 was fixed by enabling priority inheritance on a mutex.

## Common mistakes

- **Assuming `x += 1` is atomic.** In most languages, it is several machine instructions; in Python, it is several bytecode instructions.
- **Testing a lock and then setting it in separate steps,** which leaves a window for another thread to do the same.
- **Satisfying mutual exclusion but not progress,** as strict alternation and the flags-only algorithm do.
- **Spinning on a single-core machine,** where the lock holder cannot run while the waiter spins, wasting the whole time slice.
- **Holding a lock for a long time,** for example during slow I/O, which serialises the program and destroys concurrency.
- **Forgetting to release a lock on an error path;** use `with` (Python), RAII guards (C++), or `try`/`finally`.

## Revision notes

- Race condition: the result depends on the interleaving of operations on shared data; `load-add-store` can lose updates.
- Critical-section requirements: mutual exclusion, progress, bounded waiting.
- Test-then-set fails mutual exclusion; strict alternation and flags-only fail progress.
- Peterson's algorithm: `flag[i] = true; turn = j; wait while flag[j] and turn == j`. Correct for two threads under sequential consistency; real hardware needs barriers.
- Hardware: disabling interrupts (single core, kernel only), test-and-set, compare-and-swap.
- Spinlocks suit very short sections on multicore; blocking mutexes suit longer sections; hybrids spin briefly and then sleep.

## Practice questions

:::question basic
What is a race condition? Give a two-thread example.
:::answer
A race condition is a situation in which the result of a computation depends on the unpredictable order in which concurrent threads execute operations on shared data. Example: two threads each withdraw 100 from an account with balance 500 by reading the balance, subtracting 100, and writing it back. If both read 500 before either writes, both write 400, and one withdrawal is lost: the correct balance is 300.
:::

:::question basic
State the three requirements for a solution to the critical-section problem.
:::answer
Mutual exclusion: no two threads are in their critical sections at the same time. Progress: when the critical section is free and some threads want to enter, one of them is chosen in finite time, and threads in their remainder sections do not take part in the decision. Bounded waiting: once a thread asks to enter, other threads can enter only a bounded number of times before it does.
:::

:::question intermediate
Strict alternation uses a variable `turn`. Thread 0 waits while `turn != 0`, runs its critical section, and sets `turn = 1`; thread 1 does the opposite. Which requirement does this violate, and how?
:::answer
It violates progress. Suppose thread 0 finishes its critical section and sets `turn = 1`, and thread 1 then goes off to a long remainder section without entering. Thread 0 now wants to enter again, and the critical section is free, but it must wait until thread 1 enters and sets `turn = 0`. A thread that is not even trying to enter blocks the other one. Mutual exclusion does hold.
:::

:::question intermediate
Explain why disabling interrupts is not a suitable way for user programs to protect critical sections on a multicore computer.
:::answer
First, disabling interrupts is a privileged instruction, so user programs cannot execute it, and allowing it would let a program monopolise the CPU. Second, even in the kernel it only stops preemption on the current core; threads running on other cores keep executing and can still enter the critical section simultaneously. It also delays the handling of device interrupts, so it can only be used for very short sections on a single core.
:::

:::question intermediate
When is a spinlock preferable to a blocking mutex, and when is it a bad choice?
:::answer
A spinlock is preferable on a multicore machine when locks are held for a very short time, shorter than the cost of putting a thread to sleep and waking it up (two context switches): the waiter spins briefly and gets the lock without any scheduling overhead. It is a bad choice on a single-core machine, where the holder cannot release the lock while the waiter spins, and whenever critical sections may be long, because spinning wastes CPU time that other threads could use.
:::

:::question advanced
Using compare-and-swap, write pseudocode for a lock-free increment of a shared counter, and explain why it is correct.
:::answer
```text
increment(counter):
    loop:
        old = counter                         # read the current value
        if compare_and_swap(&counter, old, old + 1) == old:
            return                            # nobody changed it in between: done
        # otherwise another thread updated it first; retry with the new value
```
CAS writes `old + 1` only if the counter still equals the value we read, and it does the comparison and the write as one atomic step. If another thread incremented the counter in between, the CAS fails and we retry, so no update is ever lost. At least one thread succeeds in each round of contention, so the system as a whole always makes progress, although an individual thread could, in principle, retry many times.
:::

## Further learning

- **Next:** *Semaphores & Condition Variables* builds higher-level synchronization on top of locks.
- **Related:** *Deadlock Characterization & Prevention* explains what goes wrong when threads hold several locks.
- **Related:** *Kernel vs User Threads* describes the shared memory that makes critical sections necessary.
