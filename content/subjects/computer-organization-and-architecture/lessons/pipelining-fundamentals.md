---
lesson: pipelining-fundamentals
title: Pipelining Fundamentals & Speedup
summary: Master the principles of CPU instruction pipelining, the classic 5-stage RISC pipeline, throughput versus latency trade-offs, and speedup calculations under ideal and real hardware conditions.
minutes: 45
type: theory
objectives:
  - Distinguish between instruction latency and overall processor throughput.
  - Trace instruction execution across the classic 5-stage RISC datapath.
  - Calculate clock cycle times and ideal speedup for an arbitrary number of pipeline stages.
  - Compute realistic processor speedup incorporating latch overhead and pipeline stall cycles.
review: ai-draft
---

## Introduction

Imagine a laundry facility with four distinct tasks: washing, drying, folding, and storing. If you process one load entirely through all four steps before starting the next load, washing four loads of laundry takes sixteen hours (assuming each step takes one hour). However, as soon as the first load finishes washing and moves to the dryer, the washer sits idle. By placing the second load into the washer while the first is drying, you overlap the operations. All four loads finish in just five hours.

In computer architecture, **pipelining** applies this exact assembly line technique to CPU instruction execution. Rather than executing an instruction from fetch to write-back in a single long clock cycle—or waiting for one multi-cycle instruction to completely finish before starting the next—a pipelined processor overlaps the execution of multiple instructions. 

This lesson explores how pipelining reorganizes CPU datapath hardware into sequential stages, how pipelining affects latency and throughput, and how to quantitatively analyze both ideal and real-world processor speedup.

**Before you start:** You should be familiar with *Datapath & Register Organization*, the basic *Instruction Cycle & Assembly Language*, and basic processor metrics such as clock cycle time and cycles per instruction (CPI).

## Core theory

### 1. Instruction throughput versus instruction latency

To understand pipelining performance, we must strictly differentiate two fundamental metrics:

*   **Instruction latency** is the elapsed time required to execute a single instruction from start to finish.
*   **Instruction throughput** is the number of instructions completed per unit of time.

Pipelining **does not decrease individual instruction latency**. In fact, due to the overhead of storing intermediate results in internal pipeline hardware, individual instruction latency usually increases slightly. However, pipelining dramatically increases **instruction throughput** by completing one instruction every clock cycle under ideal conditions.

| Metric | Non-Pipelined Single-Cycle | Non-Pipelined Multi-Cycle | Pipelined Processor |
| :--- | :--- | :--- | :--- |
| **Clock Cycle Time ($\tau$)** | Long (covers all stages) | Short (covers longest stage) | Short (covers longest stage + latch delay) |
| **CPI (Cycles Per Inst.)** | $1.0$ | $4.0 - 5.0$ (varies per inst.) | Ideal $1.0$ (plus stall penalty) |
| **Instruction Latency** | $\tau_{\text{single}}$ | $N_{\text{cycles}} \times \tau_{\text{multi}}$ | $k \times \tau_{\text{pipe}}$ |
| **Instruction Throughput** | $1 / \tau_{\text{single}}$ | $1 / (\text{CPI} \times \tau_{\text{multi}})$ | $1 / (\text{CPI}_{\text{pipe}} \times \tau_{\text{pipe}})$ |

### 2. The classic 5-stage RISC pipeline

Standard 32-bit RISC architectures (such as MIPS and basic RISC-V implementations) split instruction processing into five canonical stages:

1.  **Instruction Fetch (IF):** Reads the instruction from instruction memory using the Program Counter (PC) and computes the default next address ($\text{PC} + 4$).
2.  **Instruction Decode / Register Read (ID):** Decodes the instruction bitfields, reads source operands from the register file, and sign-extends immediate values.
3.  **Execute / Address Calculation (EX):** The Arithmetic Logic Unit (ALU) performs an arithmetic/logical operation, calculates a memory address for loads/stores, or evaluates a branch condition.
4.  **Memory Access (MEM):** Performs a read or write operation to data memory for load/store instructions. Non-memory instructions bypass this stage.
5.  **Write-Back (WB):** Writes the computed result or memory-loaded value back to the target register in the register file.

Between adjacent pipeline stages sit **pipeline registers** (also called latches or inter-stage buffers). These registers hold intermediate data, control signals, and target addresses generated in one stage so the next stage can process them in the subsequent clock cycle.

```mermaid
flowchart LR
    IF[Instruction Fetch] --> IFID[IF ID Register]
    IFID --> ID[Instruction Decode]
    ID --> IDEX[ID EX Register]
    IDEX --> EX[Execute]
    EX --> EXMEM[EX MEM Register]
    EXMEM --> MEM[Memory Access]
    MEM --> MEMWB[MEM WB Register]
    MEMWB --> WB[Write Back]
```

Without these registers, signals would cascade asynchronously across stages, causing data corruption as soon as the next instruction enters the datapath.

### 3. Mathematical model of ideal speedup

Consider an unpipelined execution model where a program of $n$ instructions executes on hardware with $k$ perfectly balanced stages. Suppose each stage requires time $\tau$.

In a non-pipelined single-cycle processor, the clock cycle time is equal to the total execution time of all $k$ stages:

$$\tau_{\text{unpipe}} = k \cdot \tau$$

The total time required to execute $n$ instructions without pipelining is:

$$T_{\text{unpipe}} = n \times k \times \tau$$

In a pipelined processor with $k$ stages, the clock cycle time equals the duration of a single stage:

$$\tau_{\text{pipe}} = \tau$$

The first instruction requires $k$ cycles to fill the pipeline (termed the **pipeline latency** or fill time). Once filled, the pipeline outputs one completed instruction on every remaining clock cycle. Thus, executing $n$ instructions requires $k + (n - 1)$ clock cycles:

$$T_{\text{pipe}} = (k + n - 1) \times \tau$$

The **ideal speedup** $S_k$ achieved by a $k$-stage pipeline is the ratio of execution times:

$$S_k = \frac{T_{\text{unpipe}}}{T_{\text{pipe}}} = \frac{n \cdot k \cdot \tau}{(k + n - 1) \cdot \tau} = \frac{n \cdot k}{k + n - 1}$$

Taking the limit as the number of instructions $n$ becomes very large ($n \to \infty$):

$$\lim_{n \to \infty} S_k = \lim_{n \to \infty} \frac{k}{1 + \frac{k - 1}{n}} = k$$

Under ideal conditions—perfectly balanced stages, no overhead, and an infinitely long stream of instructions—a $k$-stage pipeline yields a theoretical maximum **speedup of $k$**.

### 4. Real-world pipeline performance and limitations

In practical processor design, ideal speedup cannot be realized due to three physical factors:

#### A. Unbalanced stage delays
Datapath stages rarely take the exact same amount of time. Because all pipeline stages share a single clock signal, the pipelined clock cycle time $\tau_{\text{pipe}}$ must be scaled to match the **slowest stage**:

$$\tau_{\text{pipe}} = \max(\tau_1, \tau_2, \dots, \tau_k) + d$$

where $d$ is the hardware setup/propagation delay of the **pipeline register** (latch overhead).

#### B. Pipeline register overhead
The internal storage latches introduce a small delay $d$. As $k$ increases, stage delays decrease ($\tau / k$), but the cumulative overhead $k \cdot d$ begins to dominate the total delay, establishing a point of diminishing returns for extremely deep pipelines.

#### C. Pipeline hazards
In real code, instructions depend on previous results or alter control flow. When an instruction cannot proceed to the next stage, the processor inserts **pipeline stalls** (bubble cycles), causing the average $\text{CPI}_{\text{pipe}}$ to rise above $1.0$.

#### General speedup formula
Combining these real-world factors gives the comprehensive equation for speedup:

$$\text{Speedup} = \frac{\text{Execution Time}_{\text{unpipe}}}{\text{Execution Time}_{\text{pipe}}} = \frac{N \times \text{CPI}_{\text{unpipe}} \times \tau_{\text{unpipe}}}{N \times \text{CPI}_{\text{pipe}} \times \tau_{\text{pipe}}}$$

If the unpipelined implementation is single-cycle ($\text{CPI}_{\text{unpipe}} = 1$), this simplifies to:

$$\text{Speedup} = \frac{\tau_{\text{unpipe}}}{(1 + \text{Stall Cycles per Inst.}) \times \tau_{\text{pipe}}}$$

## Worked examples

### Example 1: Calculating clock rate and execution time with stage imbalances

A processor designer is evaluating a 5-stage pipeline with the following stage delays:
*   IF: $180\text{ ps}$
*   ID: $140\text{ ps}$
*   EX: $200\text{ ps}$
*   MEM: $250\text{ ps}$
*   WB: $150\text{ ps}$

Each pipeline register has a latch overhead delay of $20\text{ ps}$. Compute:
1. The single-cycle (unpipelined) clock cycle time $\tau_{\text{unpipe}}$ and maximum clock frequency.
2. The pipelined clock cycle time $\tau_{\text{pipe}}$ and maximum clock frequency.
3. The speedup for running a sequence of $1,000$ instructions, assuming zero hazard stalls.

```python
def analyze_pipeline(n_instructions, stage_delays, latch_delay):
    tau_unpipe = sum(stage_delays)
    time_unpipe = n_instructions * tau_unpipe

    k = len(stage_delays)
    tau_pipe = max(stage_delays) + latch_delay
    total_cycles = k + n_instructions - 1
    time_pipe = total_cycles * tau_pipe

    speedup = time_unpipe / time_pipe

    print(f"Unpipelined clock cycle: {tau_unpipe} ps")
    print(f"Pipelined clock cycle: {tau_pipe} ps")
    print(f"Unpipelined total time: {time_unpipe / 1000:.1f} ns")
    print(f"Pipelined total time: {time_pipe / 1000:.1f} ns")
    print(f"Achieved speedup: {speedup:.2f}x")

analyze_pipeline(1000, [180, 140, 200, 250, 150], 20)
```

Output:

```text
Unpipelined clock cycle: 920 ps
Pipelined clock cycle: 270 ps
Unpipelined total time: 920.0 ns
Pipelined total time: 271.1 ns
Achieved speedup: 3.39x
```

**Step-by-step solution:**

1. **Unpipelined Clock Cycle Time:**
   $$\tau_{\text{unpipe}} = \sum \text{Stage Delays} = 180 + 140 + 200 + 250 + 150 = 920\text{ ps}$$
   $$\text{Frequency}_{\text{unpipe}} = \frac{1}{920 \times 10^{-12}\text{ s}} \approx 1.087\text{ GHz}$$

2. **Pipelined Clock Cycle Time:**
   The stage with the longest latency is MEM ($250\text{ ps}$). Adding the latch delay of $20\text{ ps}$:
   $$\tau_{\text{pipe}} = \max(180, 140, 200, 250, 150) + 20 = 250 + 20 = 270\text{ ps}$$
   $$\text{Frequency}_{\text{pipe}} = \frac{1}{270 \times 10^{-12}\text{ s}} \approx 3.704\text{ GHz}$$

3. **Speedup Calculation:**
   *   $\text{Unpipelined Time} = 1,000 \times 920\text{ ps} = 920,000\text{ ps} = 920.0\text{ ns}$
   *   $\text{Pipelined Time} = (5 + 1,000 - 1) \times 270\text{ ps} = 1,004 \times 270\text{ ps} = 271,080\text{ ps} \approx 271.1\text{ ns}$
   *   $$\text{Speedup} = \frac{920,000\text{ ps}}{271,080\text{ ps}} \approx 3.39\text{x}$$

*Note:* Because of the MEM stage bottleneck and latch overhead, the maximum achievable speedup is $3.39\text{x}$ rather than the ideal $5\text{x}$.

---

### Example 2: Real speedup with pipeline stalls

Consider a 5-stage RISC processor executing a benchmark of $10,000$ instructions.
*   The unpipelined single-cycle datapath has a clock cycle of $1000\text{ ps}$ ($\text{CPI} = 1.0$).
*   The pipelined implementation has a clock cycle of $220\text{ ps}$.
*   Due to data dependencies and control branches, $20\%$ of instructions incur a $2$-cycle pipeline stall (bubble).

Calculate the average pipelined CPI, total execution time, and real speedup over the single-cycle implementation.

**Step-by-step solution:**

1. **Calculate Average Pipelined CPI:**
   Every instruction takes $1$ base clock cycle. In addition, $20\%$ of instructions experience an extra $2$ stall cycles.
   $$\text{CPI}_{\text{pipe}} = \text{Base CPI} + \text{Stalls per Instruction} = 1.0 + (0.20 \times 2) = 1.0 + 0.40 = 1.40$$

2. **Calculate Execution Times:**
   For $N = 10,000$ instructions:
   *   $\text{Time}_{\text{unpipe}} = N \times \text{CPI}_{\text{unpipe}} \times \tau_{\text{unpipe}} = 10,000 \times 1.0 \times 1000\text{ ps} = 10,000,000\text{ ps} = 10.0\text{ ms}$
   *   Ignoring fill time for large $N$:
       $$\text{Time}_{\text{pipe}} \approx N \times \text{CPI}_{\text{pipe}} \times \tau_{\text{pipe}} = 10,000 \times 1.40 \times 220\text{ ps} = 3,080,000\text{ ps} = 3.08\text{ ms}$$

3. **Calculate Real Speedup:**
   $$\text{Speedup} = \frac{\text{Time}_{\text{unpipe}}}{\text{Time}_{\text{pipe}}} = \frac{10,000,000\text{ ps}}{3,080,000\text{ ps}} = \frac{1000}{1.40 \times 220} = \frac{1000}{308} \approx 3.25\text{x}$$

**Final Answer:** The average CPI is **$1.40$**, the execution time is **$3.08\text{ ms}$**, and the real speedup is **$3.25\text{x}$**.

---

### Example 3: Finding optimal pipeline depth under overhead constraints

Suppose a logic circuit takes $T_{\text{logic}} = 1200\text{ ps}$ of total delay to execute an instruction. We want to divide this logic into $k$ balanced pipeline stages. Each stage requires a pipeline register with delay $d = 30\text{ ps}$. Assuming an ideal workload with no stalls ($\text{CPI} = 1.0$), find the optimal value of $k$ that minimizes the total execution time for a large number of instructions $N$.

**Step-by-step solution:**

1. **Express Clock Cycle Time as a Function of $k$:**
   Since the $T_{\text{logic}}$ is split evenly across $k$ stages, each stage delay is $\frac{T_{\text{logic}}}{k}$. Adding register overhead $d$:
   $$\tau(k) = \frac{T_{\text{logic}}}{k} + d = \frac{1200}{k} + 30\text{ ps}$$

2. **Express Total Execution Time for $N$ Instructions:**
   For large $N$, the number of cycles is approximately $N$.
   $$T_{\text{total}}(k) \approx N \times \text{CPI} \times \tau(k) = N \times 1 \times \left( \frac{1200}{k} + 30 \right)$$

3. **Analyze the Latency of a Single Instruction:**
   The total latency for one instruction to pass through all $k$ stages is:
   $$L(k) = k \times \tau(k) = k \left( \frac{1200}{k} + 30 \right) = 1200 + 30k$$

4. **Evaluate Throughput vs Latency:**
   For a purely sequential instruction stream where instruction throughput dominates, total execution time decreases monotonically as $k$ increases, approaching $N \times 30\text{ ps}$ as $k \to \infty$. 

   However, if every instruction depends on the result of its predecessor (requiring the pipeline to drain completely before starting the next), the total time per instruction is governed by instruction latency $L(k) = 1200 + 30k$. In that dependent scenario, $k=1$ minimizes latency ($1230\text{ ps}$).

   In standard execution (independent stream), throughput dominates, but practical hazards scale proportional to $k$. If we introduce a hazard factor where stall probability scales linearly with stage depth (e.g., $\text{CPI}(k) = 1 + 0.05k$), we find a finite optimal $k$:
   $$T(k) \propto (1 + 0.05k) \left( \frac{1200}{k} + 30 \right) = \frac{1200}{k} + 30 + 60 + 1.5k = \frac{1200}{k} + 1.5k + 90$$

   Differentiating with respect to $k$ and setting to zero:
   $$\frac{d}{dk}\left(\frac{1200}{k} + 1.5k + 90\right) = -\frac{1200}{k^2} + 1.5 = 0 \implies k^2 = \frac{1200}{1.5} = 800 \implies k \approx 28.3$$

**Final Answer:** With standard independent throughput, deeper pipelines increase throughput up to practical limits; when hazard stalls scale with depth, an optimal pipeline depth (in this model, **$k = 28$ stages**) balances stage latency against stall frequency.

## Applications

*   **General-Purpose Microprocessors:** High-performance desktop and server CPUs (such as Intel Core, AMD Zen, and Apple M-series) use deep execution pipelines (typically 10 to 20+ stages) combined with out-of-order execution to maximize instruction throughput at high clock frequencies (4–5+ GHz).
*   **Low-Power Embedded Controllers:** Microcontrollers like the ARM Cortex-M4 utilize shorter 3-stage or 5-stage pipelines. This design minimizes pipeline register power consumption, latch overhead, and hazard branch penalties while delivering high energy efficiency.
*   **Graphics Processing Units (GPUs):** GPUs rely on massively parallel, ultra-deep throughput pipelines. Since graphics and tensor operations exhibit high instruction-level parallelism, pipeline fill times and branch penalties are easily hidden across thousands of concurrent execution threads.
*   **Network Hardware Switches:** High-speed routers use hardware pipeline datapaths to perform packet classification, route lookup, and header modification at line rate (e.g., 400 Gbps), processing one network frame per clock cycle stage.

## Common mistakes

*   **Confusing latency with throughput.** Believing that pipelining speeds up the execution time of a single isolated instruction. Why it is wrong and how to avoid it: Pipelining increases total throughput (instructions per second) by overlapping multiple instructions; individual instruction execution time actually increases slightly due to latch overhead.
*   **Ignoring pipeline register overhead.** Calculating the clock cycle time of a $k$-stage pipeline as simply $\frac{\tau_{\text{unpipe}}}{k}$. Why it is wrong and how to avoid it: Always add the latch overhead delay $d$ to the maximum stage delay, so $\tau_{\text{pipe}} = \max(\tau_i) + d$.
*   **Assuming unbalanced stages operate at different clock speeds.** Expecting fast stages to complete early and output results ahead of the clock. Why it is wrong and how to avoid it: All pipeline stages are synchronized by a single master clock; the clock period is strictly constrained by the slowest stage.
*   **Miscalculating pipeline cycle count.** Using $N \times k$ cycles for executing $N$ instructions on a $k$-stage pipeline. Why it is wrong and how to avoid it: A $k$-stage pipeline takes $k$ cycles for the first instruction to exit, and then 1 cycle for each remaining $N-1$ instruction, making the ideal cycle count $k + N - 1$.
*   **Assuming CPI remains 1.0 in real pipelines.** Neglecting stall cycles caused by hazards. Why it is wrong and how to avoid it: Real workloads experience data dependencies, memory misses, and control branches that insert stall cycles (bubbles), increasing average $\text{CPI}_{\text{pipe}} > 1.0$.

## Revision notes

*   **Pipelining** is an implementation technique that overlaps the execution of multiple instructions to increase instruction throughput.
*   **The Classic 5 RISC Stages:** Instruction Fetch (IF), Instruction Decode (ID), Execute (EX), Memory Access (MEM), Write-Back (WB).
*   **Pipeline Registers** sit between every stage pair (IF/ID, ID/EX, EX/MEM, MEM/WB) to hold intermediate results and control signals.
*   **Clock Cycle Formula:** $\tau_{\text{pipe}} = \max(\tau_1, \tau_2, \dots, \tau_k) + d$, where $d$ is latch delay.
*   **Ideal Execution Cycles:** For $N$ instructions on a $k$-stage pipeline, total cycles $= k + N - 1$.
*   **Ideal Maximum Speedup:** As $N \to \infty$, $S_k \to k$ (assuming balanced stages and zero overhead).
*   **Actual Speedup Equation:**
    $$\text{Speedup} = \frac{\text{CPI}_{\text{unpipe}} \times \tau_{\text{unpipe}}}{\text{CPI}_{\text{pipe}} \times \tau_{\text{pipe}}}$$
*   **Stall Penalty:** Hazards force the insertion of idle cycles (bubbles), raising $\text{CPI}_{\text{pipe}} = 1 + \text{stalls per instruction}$.

## Practice questions

:::question basic
A non-pipelined single-cycle CPU runs at $500\text{ MHz}$. A designer breaks the datapath into an ideal 5-stage pipeline with perfectly balanced stages and zero latch overhead. What is the clock frequency of the new pipelined CPU, and what is the ideal speedup for $100,000$ instructions?
:::answer
The original single-cycle clock period is $\tau_{\text{unpipe}} = \frac{1}{500\text{ MHz}} = 2\text{ ns}$. With 5 perfectly balanced stages and zero latch overhead, the new pipelined clock period is $\tau_{\text{pipe}} = \frac{2\text{ ns}}{5} = 0.4\text{ ns}$, giving a frequency of $\frac{1}{0.4\text{ ns}} = 2.5\text{ GHz}$. The speedup for $N = 100,000$ instructions is $\frac{100,000 \times 5}{5 + 100,000 - 1} = \frac{500,000}{100,004} \approx 4.9998\text{x}$ (which approaches the ideal speedup of $5\text{x}$).
:::

:::question basic
Why are inter-stage pipeline registers required in a pipelined datapath?
:::answer
Pipeline registers are required to save the intermediate results, status flags, and control signals generated by one stage so that the next stage can use them in the following clock cycle. Without inter-stage registers, signals would propagate continuously through the entire datapath, causing instructions behind in the pipeline to overwrite data currently being processed by instructions ahead of them.
:::

:::question intermediate
A 4-stage pipeline has stage delays of $\text{IF} = 150\text{ ps}$, $\text{ID} = 100\text{ ps}$, $\text{EX} = 220\text{ ps}$, and $\text{WB} = 180\text{ ps}$. The setup time for each pipeline register is $20\text{ ps}$. Calculate the pipelined clock cycle time, the instruction latency of a single instruction passing through the pipeline, and the speedup over an unpipelined single-cycle implementation for a large instruction sequence.
:::answer
The unpipelined single-cycle clock time is $\tau_{\text{unpipe}} = 150 + 100 + 220 + 180 = 650\text{ ps}$. The pipelined clock cycle time is determined by the slowest stage plus register overhead: $\tau_{\text{pipe}} = \max(150, 100, 220, 180) + 20 = 220 + 20 = 240\text{ ps}$. The total latency of a single instruction in the pipelined system is $4 \times \tau_{\text{pipe}} = 4 \times 240\text{ ps} = 960\text{ ps}$ (which is larger than the single-cycle time). The speedup for a large instruction sequence ($N \to \infty$) is $\frac{\tau_{\text{unpipe}}}{\tau_{\text{pipe}}} = \frac{650\text{ ps}}{240\text{ ps}} \approx 2.71\text{x}$.
:::

:::question intermediate
A processor executes a program where 30% of the instructions cause a 2-cycle pipeline stall. Assuming no other stalls and a baseline CPI of 1.0 without stalls, what is the processor's average CPI? If the clock cycle time is $0.5\text{ ns}$, how long does it take to execute 1,000,000 instructions (ignoring initial fill time)?
:::answer
The average CPI is calculated as $\text{CPI}_{\text{avg}} = 1.0 + (0.30 \times 2) = 1.6$. The total execution time for $N = 1,000,000$ instructions is $\text{Time} = N \times \text{CPI}_{\text{avg}} \times \tau = 1,000,000 \times 1.6 \times 0.5\text{ ns} = 800,000\text{ ns} = 0.8\text{ ms}$.
:::

:::question advanced
Suppose an unpipelined CPU has a clock cycle time of $10\text{ ns}$. We can divide its datapath into $k$ equal stages, but each pipeline stage adds $1\text{ ns}$ of latch overhead. If branch instructions cause pipeline flushes that add an average stall penalty of $0.1 \times k$ cycles per instruction, write the expression for execution time per instruction as a function of $k$, and find the integer stage count $k$ that maximizes performance.
:::answer
The stage delay without overhead is $\frac{10}{k}\text{ ns}$, so the clock cycle time is $\tau(k) = \frac{10}{k} + 1\text{ ns}$. The average CPI is $\text{CPI}(k) = 1 + 0.1k$. The average execution time per instruction is $T(k) = \text{CPI}(k) \times \tau(k) = (1 + 0.1k)\left(\frac{10}{k} + 1\right) = \frac{10}{k} + 1 + 1 + 0.1k = \frac{10}{k} + 0.1k + 2$. To minimize $T(k)$, set its derivative with respect to $k$ to zero: $-\frac{10}{k^2} + 0.1 = 0 \implies k^2 = 100 \implies k = 10$. Thus, a 10-stage pipeline optimizes performance for this penalty model.
:::

:::question advanced
Explain why adding more pipeline stages eventually results in diminishing returns and degraded performance, even if instructions contain no data or control dependencies.
:::answer
Even in the complete absence of instruction dependencies, deep pipelining suffers from two main factors: pipeline register overhead and stage delay quantization. First, every added stage introduces fixed register delay ($d$), so as $k \to \infty$, the clock cycle time approaches $d$ rather than zero, making register overhead dominate total cycle time. Second, logic gates cannot be divided infinitely fine; unequal stage division means the slowest indivisible logic block sets the minimum stage time. Additionally, memory access delays (such as cache lookups) cannot be arbitrarily segmented without introducing complex multi-cycle synchronization structures.
:::

## Further learning

*   **Next:** *Pipeline Hazards & Forwarding* explores data, structural, and control hazards in depth, along with hardware forwarding and branch prediction techniques to eliminate pipeline stalls.
*   **Related:** *Instruction Cycle & Assembly Language* details how individual machine code instructions are decomposed into control and datapath micro-operations.
*   **Related:** *Cache Performance & AMAT* covers memory hierarchy stalls that occur when memory accesses in the MEM stage miss the instruction or data caches.
*   **Related:** *Instruction-Level & Multicore Parallelism* investigates advanced techniques beyond basic single-issue pipelining, including superscalar design, dynamic scheduling, and out-of-order execution.

**Textbook Reference:** David A. Patterson and John L. Hennessy, *Computer Organization and Design: The Hardware/Software Interface*.
