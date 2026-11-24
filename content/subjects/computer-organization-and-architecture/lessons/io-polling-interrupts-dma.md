---
lesson: io-polling-interrupts-dma
title: I/O Techniques: Polling, Interrupts & DMA
summary: How processors communicate with input/output devices through memory-mapped and port-mapped registers, and how programmed I/O (polling), interrupt-driven I/O, and direct memory access compare in CPU cost and throughput.
minutes: 45
type: theory
objectives:
  - Explain device registers and the difference between memory-mapped and port-mapped I/O
  - Describe polling, interrupt-driven I/O, and DMA, including the steps of interrupt handling
  - Calculate and compare the CPU overhead of polling, interrupts, and DMA for a given device
review: ai-draft
---
## Introduction

A processor that cannot exchange data with keyboards, disks, network cards, and displays is useless, but devices are slow, unpredictable, and vary enormously in speed. How should the CPU find out that a device is ready, and who should move the data? There are three classic answers: the CPU keeps checking (**polling**), the device signals the CPU when it needs attention (**interrupts**), or a separate controller moves blocks of data by itself (**direct memory access**). Choosing well determines whether a system wastes its processor waiting or spends it doing useful work.

**Before you start:** you should know the instruction cycle, buses, and the memory hierarchy.

## Core theory

### Device registers and addressing

A device controller exposes a few **registers**: a **status** register (ready, busy, error bits), a **control** register (commands such as start or enable interrupts), and **data** registers for transfers. The CPU reaches them in one of two ways:

- **Memory-mapped I/O:** device registers occupy addresses in the normal physical address space, and ordinary load and store instructions access them. This is used by ARM, RISC-V, and most modern devices. The memory system must not cache these addresses.
- **Port-mapped (isolated) I/O:** devices have a separate address space reached by special instructions, such as `in` and `out` on x86.

### Programmed I/O with polling

In **programmed I/O**, the CPU itself moves every word. With **polling**, it repeatedly reads the status register until the device is ready, then transfers the data:

```c
while ((STATUS & READY) == 0) { }   /* busy-wait */
DATA = value;
```

Polling is simple and has very low latency once the device becomes ready, but every check costs CPU cycles. For slow or rarely active devices, nearly all of those checks find nothing to do.

### Interrupt-driven I/O

With **interrupts**, the CPU starts an operation and goes on with other work; the device raises an **interrupt request** when it is ready or finished. The CPU then:

1. finishes the current instruction and checks for pending interrupts;
2. saves the program counter and status (and later other registers);
3. identifies the source, often through an **interrupt vector** supplied by the device or an interrupt controller, and jumps to the **interrupt service routine** (ISR);
4. runs the ISR, which services the device and acknowledges the interrupt;
5. restores the saved state and resumes the interrupted program.

Interrupts eliminate busy-waiting, but each one has a fixed **overhead** (saving state, dispatching, returning, cache disruption), often hundreds to thousands of cycles. **Priorities** and **masking** decide which interrupts may preempt others. For devices that produce a word at a time very quickly, the overhead per interrupt can exceed the useful work.

### Direct memory access

A **DMA controller** transfers whole blocks between a device and memory without the CPU moving each word. The CPU programs it with the memory address, the byte count, and the direction, then continues; the controller takes control of the bus, transfers the block, and raises **one interrupt** when the whole transfer is complete. Modern devices are usually **bus masters** with their own DMA engines and work through **descriptor rings** in memory.

DMA competes with the CPU for the memory bus. In **burst mode** it holds the bus for a whole block; in **cycle-stealing** mode it takes one bus cycle at a time between CPU cycles. Because DMA writes memory behind the CPU's back, hardware or software must keep caches **coherent** with DMA buffers, and an **IOMMU** translates and restricts device addresses so a faulty or malicious device cannot overwrite arbitrary memory.

### Choosing a technique

| Technique | CPU involvement | Best for |
| :--- | :--- | :--- |
| Polling | constant checking and every transfer | very fast devices, very low latency needs, simple embedded loops |
| Interrupts | one interrupt per transfer unit | slow or sporadic devices (keyboard, mouse, timers) |
| DMA | set-up plus one interrupt per block | high-bandwidth block devices (disks, network, audio, GPUs) |

High-speed network cards combine ideas: **interrupt coalescing** raises one interrupt for many packets, and under heavy load drivers switch to polling (as Linux NAPI does).

## Worked examples

### Example 1: The cost of polling

A 1 GHz processor polls a mouse 30 times per second, and each poll costs 400 cycles. What fraction of the CPU does this use? What if it polls a disk that transfers 4-byte words at 40 MB/s, without missing data?

**Mouse:** $30 \times 400 = 12{,}000$ cycles per second, which is $12{,}000 / 10^9 = 0.0012\%$ of the CPU, negligible.

**Disk:** the disk delivers $40 \times 10^6 / 4 = 10^7$ words per second, so the CPU must poll $10^7$ times per second: $10^7 \times 400 = 4 \times 10^9$ cycles per second, which is 400% of a 1 GHz CPU. Polling cannot keep up at all.

```python
clock = 1e9
for name, polls in [("mouse", 30), ("disk", 40e6 / 4)]:
    fraction = polls * 400 / clock
    print(f"{name}: {fraction:.4%} of the CPU")
```

Output:

```text
mouse: 0.0012% of the CPU
disk: 400.0000% of the CPU
```

### Example 2: Interrupts versus DMA for the same disk

The same disk transfers data in 16 KiB blocks. With interrupt-driven I/O, each 4-byte word causes an interrupt costing 500 cycles. With DMA, setting up a transfer costs 1,000 cycles and the completion interrupt 500 cycles. Compare the CPU load while the disk transfers continuously at 40 MB/s.

**Interrupt per word:** $10^7$ interrupts per second $\times$ 500 cycles $= 5 \times 10^9$ cycles per second: 500% of the CPU, worse than polling, because every word now carries the full interrupt overhead.

**DMA:** blocks per second $= 40 \times 10^6 / 16{,}384 \approx 2{,}441$. Each costs $1{,}000 + 500 = 1{,}500$ cycles, so the total is about $3.66 \times 10^6$ cycles per second, roughly 0.37% of the CPU.

```python
words_per_s = 40e6 / 4
blocks_per_s = 40e6 / 16384
print(f"interrupt per word: {words_per_s * 500 / 1e9:.0%} of CPU")
print(f"DMA: {blocks_per_s:.0f} blocks/s, {blocks_per_s * 1500 / 1e9:.2%} of CPU")
```

Output:

```text
interrupt per word: 500% of CPU
DMA: 2441 blocks/s, 0.37% of CPU
```

DMA reduces the CPU cost by more than a thousand times, because the per-transfer overhead is paid once per block instead of once per word.

## Applications

- **Operating systems:** device drivers combine interrupts and DMA; timer interrupts drive scheduling.
- **Embedded systems:** simple firmware often polls sensors in a main loop; real-time code uses interrupts.
- **Networking:** NICs use DMA descriptor rings, interrupt coalescing, and adaptive polling.
- **Storage:** NVMe drives use DMA with many queues to reach millions of operations per second.

## Common mistakes

- **Assuming interrupts are always better than polling.** For very high-rate events, interrupt overhead dominates.
- **Forgetting that DMA still interrupts the CPU.** It raises one interrupt per completed block, not per word.
- **Caching memory-mapped device registers.** Reads must reach the device; those regions are uncached.
- **Ignoring cache coherence with DMA.** Stale cached data or unflushed writes corrupt transfers.

## Revision notes

- Device registers: status, control, data; memory-mapped (loads/stores) or port-mapped (special instructions).
- Polling: CPU busy-waits on status; low latency, high wasted CPU for slow devices.
- Interrupts: device signals; save state, vector to ISR, service, restore; overhead per interrupt.
- DMA: controller moves blocks; CPU sets up and gets one completion interrupt.
- CPU load = events per second × cycles per event ÷ clock rate.
- Modern NICs mix DMA, interrupt coalescing, and polling under load.

## Practice questions

:::question basic
What is the difference between memory-mapped I/O and port-mapped I/O?
:::answer
In memory-mapped I/O, device registers occupy addresses in the normal address space and are accessed with ordinary load and store instructions. In port-mapped I/O, devices have a separate address space reached only through special instructions such as x86's `in` and `out`.
:::

:::question basic
List the main steps the CPU takes when it accepts an interrupt.
:::answer
It completes the current instruction, saves the program counter and status (and other needed registers), identifies the interrupting device (for example through an interrupt vector), runs the interrupt service routine, which services and acknowledges the device, and then restores the saved state and resumes the interrupted program.
:::

:::question intermediate
A keyboard produces at most 15 characters per second. Would you use polling, interrupts, or DMA, and why?
:::answer
Interrupts. Keystrokes are rare and unpredictable, so polling would waste cycles checking an idle device, and DMA is designed for large blocks, not single characters. An interrupt per keystroke costs very little at 15 per second and gives a prompt response.
:::

:::question intermediate
A 2 GHz CPU handles a device with interrupts costing 1,000 cycles each. At what interrupt rate does interrupt handling consume 10% of the CPU?
:::answer
10% of the CPU is $0.1 \times 2 \times 10^9 = 2 \times 10^8$ cycles per second. Dividing by 1,000 cycles per interrupt gives $2 \times 10^5$, that is, 200,000 interrupts per second.
:::

:::question advanced
Why do high-speed network drivers switch from interrupts to polling under heavy load, and what does interrupt coalescing achieve?
:::answer
At millions of packets per second, an interrupt per packet would spend most of the CPU on interrupt overhead, and the system can even livelock, never finishing useful work. Under load, drivers disable the device's interrupts and poll the receive ring, processing many packets per check with no per-packet interrupt cost, and re-enable interrupts when traffic drops. Interrupt coalescing makes the NIC wait until several packets or a short time has passed before raising one interrupt, trading a little latency for far fewer interrupts.
:::

## Further learning

- **Next:** *Instruction-Level & Multicore Parallelism* looks at how processors keep busy while I/O proceeds.
- **Related:** *Main Memory, Virtual Memory & TLBs* explains the memory system that DMA writes into.
