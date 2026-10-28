---
lesson: semaphores-condition-variables
title: Semaphores and Condition Variables
summary: Counting and binary semaphores, condition variables and monitors, and their use in the bounded-buffer, readers-writers, and dining-philosophers problems.
minutes: 50
type: theory
objectives:
  - Define semaphore wait and signal operations and distinguish counting from binary semaphores
  - Solve the bounded-buffer producer-consumer problem with semaphores and with a condition variable
  - Explain why condition-variable waits must be in a loop and the difference between signal and broadcast
  - Analyse the dining-philosophers problem, show how it deadlocks, and apply a resource-ordering fix
---

## Introduction

A mutex answers one question: "may I enter the critical section?" Concurrent programs need to coordinate in richer ways. A consumer thread must **wait until** there is an item to consume. A producer must wait until there is room in the buffer. A pool of database connections must let in at most ten clients at once. A thread must wait until all the others reach a checkpoint.

Two classic tools handle this kind of coordination. A **semaphore**, invented by Edsger Dijkstra in the 1960s, is an integer counter with atomic operations to wait for and signal events. A **condition variable**, used together with a mutex in the **monitor** pattern, lets a thread sleep until some condition on shared data becomes true. This lesson explains both, and applies them to the standard synchronization problems that appear again and again in operating systems and concurrent software.

**Before you start:** you should know race conditions, critical sections, and mutex locks.

## Core theory

### Semaphores

A semaphore $S$ holds a non-negative integer and supports two atomic operations:

- **wait(S)** (also written `P`, `down`, or `acquire`): if $S > 0$, decrement it and continue; otherwise **block** until it is positive, then decrement it.
- **signal(S)** (also `V`, `up`, or `release`): increment $S$, waking one blocked thread if any are waiting.

Implementations keep a **queue of blocked threads** with each semaphore, so waiting threads sleep instead of spinning. The two operations must themselves be atomic, which the kernel or library ensures with a short internal lock.

Two kinds are common:

- A **counting semaphore** can take any non-negative value; it counts available units of a resource. Initialised to $N$, it lets at most $N$ threads past `wait` at once.
- A **binary semaphore** takes only 0 or 1 and can act as a lock (initialise to 1, `wait` to enter, `signal` to leave). Unlike a mutex, it has no owner: any thread may signal it, which also lets it be used for **signalling** between threads (initialise to 0; one thread waits until another signals).

### The bounded-buffer problem

Producers put items into a buffer with $N$ slots; consumers take them out. Three semaphores solve it:

```text
mutex = 1         ; protects the buffer itself
empty = N         ; counts free slots
full  = 0         ; counts filled slots

producer:                      consumer:
    wait(empty)                    wait(full)
    wait(mutex)                    wait(mutex)
    add item                       remove item
    signal(mutex)                  signal(mutex)
    signal(full)                   signal(empty)
```

A producer blocks on `empty` when the buffer is full, and a consumer blocks on `full` when it is empty. The **order** of the waits matters: if a producer took `mutex` first and then blocked on `empty`, no consumer could ever take `mutex` to free a slot, a deadlock.

### Condition variables and monitors

A **condition variable** is always used with a mutex that protects some shared state. It provides:

- **wait(cv, mutex):** atomically release the mutex and sleep; when woken, reacquire the mutex before returning.
- **signal(cv)** (`notify`): wake one waiting thread, if any.
- **broadcast(cv)** (`notify_all`): wake all waiting threads.

The pattern is always:

```text
lock(mutex)
while not condition:          ; a while loop, never an if
    wait(cv, mutex)
... use the shared state ...
unlock(mutex)
```

The loop is essential. With the common **Mesa semantics** (used by Pthreads, Java, and Python), a signalled thread does not run immediately; by the time it reacquires the mutex, another thread may have changed the state again. Implementations may also wake a thread without any signal (a **spurious wakeup**). Rechecking the condition handles both.

A **monitor** packages shared data, a mutex, and condition variables into one object whose methods run with the mutex held. Java's `synchronized` methods with `wait`/`notify`, and Python classes using `threading.Condition`, follow this design.

Condition variables, unlike semaphores, have **no memory**: a signal sent when no thread is waiting is simply lost. That is why the waiting thread always tests a condition on shared state before sleeping.

### Readers and writers

Many threads may read shared data at once, but a writer needs exclusive access. A **readers-writer lock** allows either any number of readers or one writer. Simple solutions favour readers, which can starve writers when readers keep arriving; fairer versions queue new readers behind a waiting writer.

### The dining philosophers

Five philosophers sit around a table with one fork between each pair. A philosopher needs both neighbouring forks to eat. If every philosopher picks up the left fork and then waits for the right one, all five hold one fork and wait forever: a **deadlock**. Standard fixes:

- **Resource ordering:** number the forks and always pick up the lower-numbered fork first. Then one philosopher reaches for the forks in the opposite order from the others, which breaks the circle of waiting.
- **Limit the diners:** allow at most four philosophers to try at once (a counting semaphore initialised to 4).
- **Pick up both or neither:** use a monitor that grants both forks atomically when both are free.

## Worked examples

### Example 1: Producer and consumer with semaphores

```python
import threading
from collections import deque

CAPACITY = 3
buffer = deque()
mutex = threading.Lock()                  # protects the buffer itself
empty = threading.Semaphore(CAPACITY)     # counts free slots
full = threading.Semaphore(0)             # counts filled slots
consumed, most_buffered = [], 0

def producer():
    global most_buffered
    for item in range(1, 11):
        empty.acquire()                   # wait for a free slot
        with mutex:
            buffer.append(item)
            most_buffered = max(most_buffered, len(buffer))
        full.release()                    # announce one more item

def consumer():
    for _ in range(10):
        full.acquire()                    # wait for an item
        with mutex:
            item = buffer.popleft()
        empty.release()                   # announce one more free slot
        consumed.append(item)

threads = [threading.Thread(target=producer), threading.Thread(target=consumer)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(consumed)
print("never more than", CAPACITY, "items buffered:", most_buffered <= CAPACITY)
```

Output:

```text
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
never more than 3 items buffered: True
```

However the two threads are scheduled, the consumer receives every item exactly once and in order, and the buffer never holds more than 3 items: the producer blocks on `empty` whenever it gets 3 items ahead. The exact interleaving differs from run to run, but the guarantees do not.

### Example 2: A bounded queue as a monitor

The same buffer written with a condition variable. Two producers and two consumers share it.

```python
import threading
from collections import deque

class BoundedQueue:
    def __init__(self, capacity):
        self.items, self.capacity = deque(), capacity
        self.changed = threading.Condition()   # a mutex and a condition variable in one

    def put(self, item):
        with self.changed:                     # lock the monitor
            while len(self.items) >= self.capacity:
                self.changed.wait()            # releases the lock while asleep
            self.items.append(item)
            self.changed.notify_all()          # wake consumers (and producers) to recheck

    def get(self):
        with self.changed:
            while not self.items:
                self.changed.wait()
            item = self.items.popleft()
            self.changed.notify_all()
            return item

queue, results = BoundedQueue(2), []
results_lock = threading.Lock()

def produce(start):
    for value in range(start, start + 5):
        queue.put(value)

def consume():
    for _ in range(5):
        value = queue.get()
        with results_lock:
            results.append(value)

threads = [threading.Thread(target=produce, args=(s,)) for s in (0, 100)]
threads += [threading.Thread(target=consume) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(sorted(results))
```

Output:

```text
[0, 1, 2, 3, 4, 100, 101, 102, 103, 104]
```

The order in which the two consumers receive items varies between runs, so the program sorts the results before printing; the important fact is that all ten values arrive exactly once. Both methods wait in a `while` loop: a consumer woken by `notify_all` may find that the other consumer already took the item, and it must go back to sleep. With an `if` instead, it would call `popleft` on an empty deque and crash. `notify_all` is used because producers and consumers wait on the same condition; with `notify`, a producer might wake another producer instead of a consumer.

### Example 3: How the dining philosophers deadlock, and how ordering prevents it

This model gives every philosopher one move in turn, the worst-case schedule, in which each grabs a first fork before anyone grabs a second.

```python
def first_moves(n, fork_order):
    holder = [None] * n                            # holder[f] = philosopher holding fork f
    waiting_for = {}
    for p in range(n):                             # everyone grabs a first fork in turn
        first, second = fork_order(p, n)
        if holder[first] is None:
            holder[first] = p
            waiting_for[p] = second
        else:
            waiting_for[p] = first
    able = [p for p, f in waiting_for.items() if holder[f] is None]
    return able

left_first = lambda p, n: (p, (p + 1) % n)        # fork p is on philosopher p's left
lower_first = lambda p, n: tuple(sorted((p, (p + 1) % n)))

print("left fork first:  can continue ->", first_moves(5, left_first))
print("lower fork first: can continue ->", first_moves(5, lower_first))
```

Output:

```text
left fork first:  can continue -> []
lower fork first: can continue -> [3]
```

When everyone takes the left fork first, all five forks are held and every philosopher waits for a fork that a neighbour holds, so nobody can continue: a deadlock. With the lower-numbered fork first, philosopher 4's forks are 4 and 0, so it reaches for fork 0, which philosopher 0 already holds; it waits holding nothing, which leaves fork 4 free. Philosopher 3, holding fork 3, can pick up fork 4 and eat, and when it finishes, the others proceed in turn. The same rule, acquire locks in one global order, prevents deadlock in any program that takes several locks.

## Applications

- **Connection and thread pools** use counting semaphores to limit how many clients use a resource at once.
- **Pipelines and message queues,** from Unix pipes to Python's `queue.Queue`, are bounded buffers internally.
- **Event signalling:** a binary semaphore or condition variable lets one thread tell another that data is ready, a job finished, or a shutdown was requested.
- **Readers-writer locks** protect caches, routing tables, and configuration data that are read often and written rarely.
- **Lock ordering** is a standard rule in large code bases such as operating system kernels, and tools like Linux's `lockdep` check it automatically.

## Common mistakes

- **Waiting on a condition with `if` instead of `while`,** which fails after spurious wakeups or when another thread changes the state first.
- **Calling `wait` or `notify` without holding the associated lock;** Python raises an error, and in other languages it causes races.
- **Taking the mutex before waiting on `empty` or `full`** in the bounded buffer, which can deadlock.
- **Using `notify` when different kinds of waiters share one condition,** waking the wrong kind; use `notify_all` or separate condition variables.
- **Expecting a condition variable to remember a signal.** If nobody is waiting, the signal is lost; the state variable is what records events.
- **Forgetting a matching `signal` for every `wait`** on a counting semaphore, which slowly leaks units until every thread blocks.

## Revision notes

- Semaphore: integer with atomic `wait` (decrement or block) and `signal` (increment, wake one).
- Counting semaphores count resources; binary semaphores act as locks or signals and have no owner.
- Bounded buffer: `mutex = 1`, `empty = N`, `full = 0`; wait on `empty`/`full` before `mutex`.
- Condition variable: `wait` releases the mutex and sleeps; always loop on the condition; `signal` wakes one, `broadcast` all.
- Monitor = shared data + mutex + condition variables.
- Dining philosophers: left-first deadlocks; resource ordering, limiting diners, or atomic acquisition fix it.

## Practice questions

:::question basic
A counting semaphore starts at 3. Five threads call `wait` and nobody calls `signal`. How many threads continue, and what is the semaphore's value?
:::answer
Three threads continue; each decrements the semaphore, from 3 to 2, 1, and 0. The fourth and fifth threads find the value 0 and block. The semaphore's value stays 0 (in the usual definition it never goes negative; some textbook implementations let it go to $-2$ to record the two waiters). Each later `signal` releases one blocked thread.
:::

:::question basic
What is the difference between a binary semaphore and a mutex?
:::answer
Both can provide mutual exclusion, but a mutex has an owner: only the thread that locked it may unlock it, and many implementations check this. A binary semaphore has no owner; any thread may signal it. That makes a semaphore usable for signalling between threads (one thread waits, another signals), which a mutex is not meant for.
:::

:::question intermediate
In the semaphore solution to the bounded-buffer problem, what goes wrong if the producer calls `wait(mutex)` before `wait(empty)`?
:::answer
If the buffer is full, the producer acquires `mutex` and then blocks on `empty` while still holding `mutex`. A consumer must acquire `mutex` to remove an item and signal `empty`, but `mutex` is held by the sleeping producer, so the consumer blocks too. Neither can proceed: a deadlock. Waiting for a slot must come before entering the critical section.
:::

:::question intermediate
Why must a thread waiting on a condition variable recheck the condition in a loop after `wait` returns?
:::answer
Being woken does not guarantee that the condition is true. Under Mesa semantics, between the signal and the moment the woken thread reacquires the mutex, another thread may run and change the state, for example take the item that triggered the signal. Implementations may also produce spurious wakeups with no signal at all. Rechecking in a `while` loop makes the thread go back to sleep if the condition no longer holds.
:::

:::question intermediate
Show how a single counting semaphore prevents deadlock in the dining-philosophers problem.
:::answer
Create a semaphore `seats` initialised to 4. Each philosopher calls `wait(seats)` before picking up any fork and `signal(seats)` after putting both down. At most four philosophers compete for five forks, so by the pigeonhole principle at least one of them can obtain both neighbouring forks, eat, and release them. A circular wait among all five can therefore never form.
:::

:::question advanced
Design a reusable barrier for $N$ threads using a mutex and a condition variable: every thread calls `arrive()`, and no thread returns until all $N$ have arrived. Explain why a generation counter is needed.
:::answer
Keep `count` (threads arrived in this round) and `generation`, protected by a mutex with one condition variable. In `arrive()`: lock; remember `g = generation`; increment `count`; if `count == N`, set `count = 0`, increment `generation`, and `broadcast`; otherwise `while generation == g: wait`. Then unlock. The generation counter is needed because the barrier is reused: without it, a fast thread could leave, call `arrive()` again for the next round, and change `count` before slow threads from the previous round have rechecked their condition, confusing the rounds. Waiting until the generation changes ties each waiter to its own round, and it also makes the code immune to spurious wakeups.
:::

## Further learning

- **Next:** *Deadlock Characterization & Prevention* explains in general why the dining philosophers deadlock and how to prevent it.
- **Related:** *Critical Section Problem & Mutexes* covers the locks that semaphores and monitors build on.
- **Related:** *Circular Queues & Deque* (Data Structures & Algorithms) shows the ring buffer often used inside bounded buffers.
