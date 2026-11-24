---
lesson: ilp-multicore-parallelism
title: Instruction-Level & Multicore Parallelism
summary: How processors execute many instructions at once: pipelining and its limits, superscalar and out-of-order execution, branch prediction, Flynn's taxonomy, multicore processors, Amdahl's law, and cache coherence with the MESI protocol.
minutes: 50
type: theory
objectives:
  - Explain instruction-level parallelism through superscalar issue, out-of-order execution, and branch prediction, and what limits it
  - Classify architectures with Flynn's taxonomy and estimate multicore speedup with Amdahl's law
  - Describe the cache coherence problem and trace the MESI protocol for reads and writes on multiple cores
review: ai-draft
---
## Introduction

For decades, processors became faster mainly by raising the clock rate. Around 2005 that stopped: higher clocks made chips too hot. Performance has since come from **parallelism**: doing more work per cycle within one core (**instruction-level parallelism**, ILP) and putting many cores on one chip (**thread-level parallelism**). Both raise new problems: dependences between instructions limit ILP, and cores that cache the same memory must keep their copies consistent. This lesson explains the main techniques and their limits.

**Before you start:** you should know the basic five-stage pipeline, hazards, and caches.

## Core theory

### Beyond the simple pipeline

A classic pipeline overlaps instruction stages and ideally completes one instruction per cycle (CPI = 1). Three kinds of **hazards** prevent this: **structural** (two instructions need the same hardware), **data** (an instruction needs a result not yet produced), and **control** (the next instruction is unknown until a branch resolves). Forwarding, stalls, and branch prediction reduce their cost.

### Superscalar and out-of-order execution

A **superscalar** processor fetches, decodes, and issues several instructions per cycle into multiple functional units, so the ideal CPI falls below 1 (equivalently, the **IPC**, instructions per cycle, exceeds 1). Independent instructions can then run in parallel, but dependent ones still must wait.

**Out-of-order** (OoO) execution finds more independent work: instructions enter a window (the **reorder buffer**), wait in reservation stations until their operands are ready, execute as soon as possible, possibly out of program order, and then **retire** in program order so exceptions remain precise. **Register renaming** maps architectural registers onto a larger pool of physical registers, removing false dependences (write-after-read and write-after-write), which arise only from reusing register names, so that only true data dependences (read-after-write) limit parallelism.

### Branch prediction and speculation

About one instruction in five is a branch, so a wide processor would stall constantly if it waited for each branch to resolve. **Branch predictors** guess the outcome from history: a **2-bit saturating counter** per branch changes its prediction only after two consecutive mispredictions, and modern predictors combine global and local history to exceed 95% accuracy. The processor **speculatively** executes the predicted path; on a misprediction it discards the wrong-path work, costing a penalty of many cycles in a deep pipeline. (The Spectre vulnerabilities showed that speculative execution can leave secrets observable through cache timing.)

### Limits of ILP

True dependences, unpredictable branches, cache misses, and the cost and power of larger windows limit how much ILP hardware can extract. Typical programs reach an IPC of about 1 to 4 even on cores that could issue 6 or 8 instructions per cycle. This **ILP wall**, together with the **power wall**, pushed designers towards multiple cores.

### Flynn's taxonomy

Michael Flynn classified architectures by their instruction and data streams:

| Class | Meaning | Example |
| :--- | :--- | :--- |
| SISD | single instruction, single data | a classic single-core processor |
| SIMD | single instruction, multiple data | vector units (SSE, AVX, NEON), GPU warps |
| MISD | multiple instruction, single data | rare; some fault-tolerant systems |
| MIMD | multiple instruction, multiple data | multicore processors, clusters |

### Multicore and Amdahl's law

A **multicore** processor places several cores on one chip, typically with private L1 and L2 caches and a shared last-level cache. Software must be divided into threads to benefit. **Amdahl's law** bounds the speedup when a fraction $p$ of the work can be parallelised across $n$ cores:

$$S(n) = \frac{1}{(1 - p) + \frac{p}{n}}, \qquad \lim_{n \to \infty} S(n) = \frac{1}{1 - p}$$

so the serial part dominates as cores are added: with $p = 0.9$, even infinitely many cores give at most a 10× speedup. **Gustafson's law** offers a more optimistic view when the problem size grows with the number of cores.

### Cache coherence and MESI

When two cores cache the same memory block, a write by one must not leave the other reading a stale copy. A **coherence protocol** guarantees that all cores eventually see writes to a location in the same order. Snooping protocols broadcast bus transactions that every cache watches; directory protocols track sharers in a table, which scales better. The common **MESI** protocol gives each cached line one of four states:

- **Modified (M):** only this cache has the line, and it is dirty (differs from memory).
- **Exclusive (E):** only this cache has it, and it is clean.
- **Shared (S):** several caches may have clean copies.
- **Invalid (I):** the line is not valid here.

A read miss loads the line in E (if no other cache has it) or S. A write to an S line first **invalidates** all other copies, then moves to M; a write to an E line moves to M silently, with no bus traffic, which is the point of the E state. When another core reads a line held in M, the owner supplies the data (writing it back) and both copies become S. **False sharing** occurs when independent variables used by different cores lie in the same cache line, so invalidations bounce the line between caches even though no data is truly shared.

## Worked examples

### Example 1: Amdahl's law in practice

A program spends 80% of its time in a loop that parallelises perfectly. What speedup do 2, 4, 8, and 64 cores give, and what is the limit?

```python
def amdahl(p, n):
    return 1 / ((1 - p) + p / n)

p = 0.80
for n in (2, 4, 8, 64):
    print(f"{n:>2} cores: speedup {amdahl(p, n):.2f}, efficiency {amdahl(p, n) / n:.0%}")
print(f"limit: {1 / (1 - p):.1f}x")
```

Output:

```text
 2 cores: speedup 1.67, efficiency 83%
 4 cores: speedup 2.50, efficiency 62%
 8 cores: speedup 3.33, efficiency 42%
64 cores: speedup 4.71, efficiency 7%
limit: 5.0x
```

The serial 20% dominates quickly: 64 cores give less than a fivefold speedup, using each core only 7% effectively. Reducing the serial fraction is usually worth more than adding cores.

### Example 2: Tracing MESI on two cores

Cores P1 and P2 start with line X invalid in both caches. Trace the states after each operation.

| Step | Operation | P1 state | P2 state | Bus action |
| :--- | :--- | :--- | :--- | :--- |
| 1 | P1 reads X | E | I | read miss; no other copy, so Exclusive |
| 2 | P1 writes X | M | I | none: E to M is silent |
| 3 | P2 reads X | S | S | P2's read miss; P1 supplies the dirty data and writes it back |
| 4 | P2 writes X | I | M | P2 broadcasts an invalidate; P1's copy becomes Invalid |
| 5 | P1 reads X | S | S | P1's read miss; P2 supplies the data and writes it back |

At every step at most one cache holds the line in M or E, and no cache ever reads a stale value. Step 2 shows the benefit of the E state: a private line can be written without any bus traffic. Steps 4 and 5 show the cost of sharing: each write by a different core forces invalidation and a later miss, which is exactly what happens, needlessly, with false sharing.

## Applications

- **Desktop and server processors:** wide out-of-order cores with accurate branch predictors.
- **GPUs and vector units:** SIMD execution for graphics, machine learning, and scientific computing.
- **Parallel software design:** Amdahl's law guides where to optimise and how many cores to buy.
- **Performance tuning:** padding shared data structures to avoid false sharing.

## Common mistakes

- **Assuming n cores give n times the speed.** The serial fraction limits speedup (Amdahl's law).
- **Thinking out-of-order execution changes program results.** Instructions retire in order and results are identical.
- **Confusing coherence with consistency.** Coherence concerns a single location; the memory consistency model concerns the ordering of accesses to different locations.
- **Ignoring false sharing.** Independent variables in one cache line can serialise threads.

## Revision notes

- Hazards: structural, data, control; superscalar issue gives IPC > 1.
- Out-of-order execution with reorder buffer and in-order retirement; renaming removes false dependences.
- Branch prediction (2-bit counters and beyond) enables speculation; mispredictions cost many cycles.
- Flynn: SISD, SIMD, MISD, MIMD.
- Amdahl: $S = 1 / ((1 - p) + p / n)$, limit $1/(1 - p)$.
- MESI states: Modified, Exclusive, Shared, Invalid; writes to shared lines invalidate other copies.

## Practice questions

:::question basic
What does it mean for a processor to be superscalar?
:::answer
It can fetch, decode, and issue more than one instruction per clock cycle to multiple functional units, so in the best case it completes more than one instruction per cycle (IPC above 1).
:::

:::question basic
Classify a GPU executing the same instruction on 32 data elements at once, and a quad-core CPU, using Flynn's taxonomy.
:::answer
The GPU warp is SIMD: a single instruction stream applied to multiple data elements. The quad-core CPU is MIMD: each core runs its own instruction stream on its own data.
:::

:::question intermediate
A program is 95% parallelisable. What is its speedup on 16 cores, and what is the maximum possible speedup?
:::answer
$S(16) = 1 / (0.05 + 0.95/16) = 1 / (0.05 + 0.059375) = 1 / 0.109375 \approx 9.14$. The maximum, as the number of cores grows without bound, is $1 / 0.05 = 20$.
:::

:::question intermediate
What problem does register renaming solve?
:::answer
It removes false (name) dependences, write-after-read and write-after-write, which occur only because instructions reuse the same architectural register names. By mapping each new value to a fresh physical register, independent instructions no longer have to wait for one another, so out-of-order execution can exploit more parallelism.
:::

:::question advanced
Two threads on different cores each increment their own counter, but the counters are adjacent `long` fields in one object. The program scales badly. Explain using MESI, and suggest a fix.
:::answer
Both counters lie in the same cache line. Each increment by one core must first get the line in the Modified state, which invalidates the other core's copy, so the line bounces between the caches on almost every increment: false sharing. Each write causes coherence misses even though the threads share no data. Padding or aligning the counters so each occupies its own cache line (for example 64 bytes apart), or keeping per-thread counters in local variables and combining at the end, removes the contention.
:::

## Further learning

- **Next:** revisit *Hardwired vs Microprogrammed Control* to see why simple control enables deep pipelines.
- **Related:** *Thread Synchronization & Concurrency* in Java shows how software experiences cache coherence and false sharing.
