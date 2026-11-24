---
lesson: java-thread-synchronization
title: Thread Synchronization & Concurrency
summary: Creating and coordinating threads in Java, race conditions and why they happen, intrinsic locks with synchronized, visibility with volatile, atomic variables, and thread pools from java.util.concurrent.
minutes: 50
type: theory
objectives:
  - Create threads with Runnable and ExecutorService, and wait for results with join and Future
  - Explain race conditions, atomicity, and visibility, and fix them with synchronized, volatile, and atomic classes
  - Use thread pools and concurrent collections, and recognise deadlock and how to avoid it
review: ai-draft
---
## Introduction

Modern processors have many cores, and servers handle thousands of requests at once. Java has supported **threads**, independent paths of execution within one program, since its first version. Threads let a program do several things at the same time, but when they share data, they can interfere with one another in ways that produce wrong answers only occasionally, which makes such bugs notoriously hard to find. This lesson explains the problems and the standard tools that prevent them.

**Before you start:** you should know classes, interfaces, lambdas, and exceptions.

## Core theory

### Creating threads

A thread runs a `Runnable`, a functional interface with `void run()`:

```java
Thread t = new Thread(() -> System.out.println("hello from a thread"));
t.start();   // runs run() concurrently
t.join();    // wait for it to finish
```

`start()` creates a new thread; calling `run()` directly just runs the code in the current thread. `join()` waits for a thread to finish. In real applications, prefer an **ExecutorService** (thread pool) from `java.util.concurrent`: `Executors.newFixedThreadPool(4)` reuses a fixed set of threads, `submit` returns a `Future` whose `get()` waits for the result, and `shutdown()` stops accepting tasks. Creating a new thread per task is expensive and unbounded.

### Race conditions

`count++` looks like one step but is three: read `count`, add 1, write it back. If two threads interleave, both may read 5 and both write 6, losing an increment. A **race condition** is any bug whose outcome depends on the timing of threads. Because the timing changes from run to run, the program may pass tests and fail in production.

### Atomicity with synchronized

Every object has an **intrinsic lock** (monitor). A `synchronized` method or block acquires the lock before running and releases it afterwards, even if an exception is thrown:

```java
synchronized void increment() { count++; }
// or
synchronized (lock) { count++; }
```

Only one thread can hold a given lock at a time, so code guarded by the **same** lock runs one thread at a time: the critical section becomes **atomic**. Locks in Java are **reentrant**, so a thread that holds a lock can enter other code synchronized on the same lock.

### Visibility and volatile

Without synchronization, a thread may not see another thread's writes promptly, or ever, because values can be cached in registers or reordered by the compiler and CPU. The **Java Memory Model** guarantees visibility when threads synchronize: releasing a lock makes all earlier writes visible to the next thread that acquires the same lock. Declaring a field **`volatile`** guarantees that every read sees the most recent write, which is ideal for simple flags such as `volatile boolean running`. `volatile` does **not** make compound actions like `count++` atomic.

### Atomic classes and concurrent collections

`java.util.concurrent.atomic` provides lock-free atomic operations: `AtomicInteger.incrementAndGet()`, `AtomicLong`, `LongAdder` (fast under heavy contention). Thread-safe collections include `ConcurrentHashMap` (whose `merge` and `compute` update entries atomically), `CopyOnWriteArrayList`, and `BlockingQueue` implementations for producer-consumer designs.

### Deadlock

A **deadlock** occurs when threads wait for each other forever: thread 1 holds lock A and waits for B, while thread 2 holds B and waits for A. The standard prevention is to acquire multiple locks in one **global order** everywhere, keep critical sections short, and avoid calling unknown code while holding a lock.

## Worked examples

### Example 1: A race condition and three fixes

```java
import java.util.concurrent.atomic.AtomicInteger;

public class Main {
    static int unsafeCount = 0;
    static int lockedCount = 0;
    static final Object lock = new Object();
    static final AtomicInteger atomicCount = new AtomicInteger();

    static void work() {
        for (int i = 0; i < 100_000; i++) {
            unsafeCount++;
            synchronized (lock) { lockedCount++; }
            atomicCount.incrementAndGet();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Thread[] threads = new Thread[4];
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(Main::work);
            threads[i].start();
        }
        for (Thread t : threads) t.join();
        System.out.println("expected  " + 4 * 100_000);
        System.out.println("locked    " + lockedCount);
        System.out.println("atomic    " + atomicCount.get());
        System.out.println("unsafe is never more than expected: " + (unsafeCount <= 400_000));
    }
}
```

Output:

```text
expected  400000
locked    400000
atomic    400000
unsafe is never more than expected: true
```

The synchronized and atomic counters always reach 400,000. The unsynchronized counter usually ends lower, by a different amount on each run, because increments are lost when threads interleave; that is why its exact value is not printed. Waiting with `join()` before reading the results also guarantees that the main thread sees the threads' final writes.

### Example 2: A thread pool with futures and a concurrent map

```java
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class Main {
    static long sumRange(long from, long to) {
        long s = 0;
        for (long i = from; i <= to; i++) s += i;
        return s;
    }

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        try {
            List<Future<Long>> parts = new ArrayList<>();
            long n = 1_000_000, chunk = n / 4;
            for (int k = 0; k < 4; k++) {
                long from = k * chunk + 1, to = (k + 1) * chunk;
                parts.add(pool.submit(() -> sumRange(from, to)));
            }
            long total = 0;
            for (Future<Long> f : parts) total += f.get();
            System.out.println("sum 1.." + n + " = " + total + " (formula: " + n * (n + 1) / 2 + ")");

            String[] words = "a b a c b a d c a".split(" ");
            Map<String, Integer> counts = new ConcurrentHashMap<>();
            List<Future<?>> jobs = new ArrayList<>();
            for (String w : words) jobs.add(pool.submit(() -> counts.merge(w, 1, Integer::sum)));
            for (Future<?> j : jobs) j.get();
            System.out.println(new TreeMap<>(counts));
        } finally {
            pool.shutdown();
        }
    }
}
```

Output:

```text
sum 1..1000000 = 500000500000 (formula: 500000500000)
{a=4, b=2, c=2, d=1}
```

The range is split into four chunks summed in parallel, and each `Future.get()` waits for its chunk. `ConcurrentHashMap.merge` updates counts atomically even when several tasks update the same word at once; copying into a `TreeMap` prints the result in key order. Shutting the pool down in `finally` lets the program exit.

## Applications

- **Web servers:** each request is handled by a pooled thread.
- **Responsive apps:** long work runs in the background while the UI thread stays responsive.
- **Parallel computation:** splitting work across cores, as in the summing example.
- **Producer-consumer pipelines:** `BlockingQueue` connects threads that produce and consume work.

## Common mistakes

- **Calling `run()` instead of `start()`.** No new thread is created.
- **Unsynchronized shared counters.** Use `synchronized`, `AtomicInteger`, or `LongAdder`.
- **Thinking `volatile` makes `count++` safe.** It guarantees visibility, not atomicity.
- **Synchronizing on different locks.** Code protecting the same data must use the same lock.
- **Acquiring locks in inconsistent orders.** This causes deadlock; use a global order.
- **Forgetting to shut down executors.** Non-daemon pool threads keep the program alive.

## Revision notes

- `new Thread(runnable).start()`, `join()`; prefer `ExecutorService` with `submit` and `Future.get()`.
- Race condition: outcome depends on thread timing; `count++` is not atomic.
- `synchronized` gives mutual exclusion and visibility on the same lock; locks are reentrant.
- `volatile` gives visibility only; good for flags.
- `AtomicInteger`, `LongAdder`, `ConcurrentHashMap.merge` for lock-free or fine-grained safety.
- Deadlock: circular waiting; prevent with a consistent lock order.

## Practice questions

:::question basic
What is the difference between calling `thread.start()` and `thread.run()`?
:::answer
`start()` creates a new thread of execution, which then calls `run()` concurrently with the caller. Calling `run()` directly executes the method in the current thread like an ordinary method call, so nothing runs in parallel.
:::

:::question basic
Why is `count++` not thread-safe?
:::answer
It consists of three steps: read the value, add one, and write it back. Two threads can both read the same value before either writes, so one increment overwrites the other and is lost.
:::

:::question intermediate
What does `volatile` guarantee, and why is it not enough for a shared counter?
:::answer
`volatile` guarantees visibility and ordering: every read of the field sees the most recent write by any thread. It does not make a read-modify-write sequence such as `count++` atomic, so increments can still be lost; use `synchronized` or `AtomicInteger` instead.
:::

:::question intermediate
Why are thread pools preferred over creating a new thread for each task?
:::answer
Creating and destroying threads is expensive, and an unbounded number of threads can exhaust memory and overwhelm the CPU with context switches. A pool reuses a fixed number of threads, queues extra tasks, limits resource use, and returns results through `Future`s.
:::

:::question advanced
Thread 1 runs `synchronized (a) { synchronized (b) { ... } }` and thread 2 runs `synchronized (b) { synchronized (a) { ... } }`. Explain how this can deadlock and give a fix.
:::answer
If thread 1 acquires `a` and thread 2 acquires `b` at about the same time, each then waits for the lock the other holds, and neither can proceed: a circular wait, which is deadlock. Fix it by imposing a global lock order, so both threads always acquire `a` before `b`; alternatively use `ReentrantLock.tryLock` with a timeout or redesign to need only one lock.
:::

## Further learning

- **Next:** *JVM Architecture & Bytecode* revisits the per-thread stacks and shared heap that make these issues possible.
- **Related:** *Critical Section Problem & Mutexes* in Operating Systems covers the theory behind locks and race conditions.
