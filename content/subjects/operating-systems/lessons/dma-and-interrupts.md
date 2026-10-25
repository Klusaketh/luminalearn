---
lesson: dma-and-interrupts
title: Direct Memory Access (DMA) and Interrupts
summary: Three ways for the CPU to move data to and from devices - programmed I/O with polling, interrupt-driven I/O, and direct memory access - and how interrupt handling, deferred work, and coalescing keep I/O efficient.
minutes: 35
type: theory
objectives:
  - Compare programmed I/O with polling, interrupt-driven I/O, and DMA by CPU involvement and suitability
  - Describe how an interrupt is raised, dispatched through the interrupt vector, handled, and acknowledged
  - Explain the steps of a DMA transfer, including bus mastering, cycle stealing, and scatter-gather
  - Calculate the CPU overhead of different I/O methods and the trade-off made by interrupt coalescing
---

## Introduction

A modern solid-state drive can deliver several gigabytes per second, a network card can receive millions of packets per second, and a keyboard produces a few characters per second when someone types quickly. The CPU must work with all of them, yet it cannot afford to spend its time babysitting devices: every cycle spent checking whether a device is ready, or copying bytes one at a time, is a cycle not spent on applications.

Operating systems use three techniques, in order of sophistication. With **programmed I/O**, the CPU itself checks device status and moves every byte. With **interrupt-driven I/O**, the device tells the CPU when it needs attention. With **direct memory access (DMA)**, a separate controller moves whole blocks of data between the device and memory, and the CPU hears about it only when the transfer is finished. This lesson explains each technique, what happens inside the CPU when an interrupt arrives, and how to estimate which technique a device needs.

**Before you start:** you should know what system calls and interrupts are, and the basic idea of a device driver.

## Core theory

### Device controllers and registers

Each device is connected through a **controller** with a few registers: a **status** register (busy, ready, error), a **command** register, and **data** registers. The CPU accesses them with special I/O instructions or, more commonly today, through **memory-mapped I/O**, in which device registers appear at physical addresses and are read and written with ordinary memory instructions.

### Programmed I/O and polling

The CPU repeatedly reads the status register until the device is ready (**polling**, or busy-waiting), then transfers one unit of data, and repeats.

- Simple, and the fastest response for a device that becomes ready almost immediately.
- Wasteful when the device is slow: the CPU spins doing nothing useful.

Polling makes sense when the expected wait is shorter than the cost of an interrupt, which is why very high-speed devices (some network and storage stacks) switch to polling under heavy load.

### Interrupt-driven I/O

The CPU starts an operation and goes on with other work. When the device finishes or needs attention, it raises a signal on an **interrupt request (IRQ)** line.

1. At the end of the current instruction, the CPU notices the pending interrupt (if interrupts are enabled and the request's priority is high enough).
2. It saves the minimum state (program counter, flags) and switches to kernel mode.
3. It uses the interrupt number to index the **interrupt vector table**, which holds the address of the **interrupt service routine (ISR)**, the handler for that device.
4. The ISR acknowledges the device, does the urgent work, and returns, restoring the interrupted code.

Interrupts have **priorities**, and handling a high-priority interrupt may itself be interrupted only by higher-priority ones; low-priority requests can be **masked** (temporarily disabled). Some interrupts, such as hardware failure warnings, are **non-maskable**.

Because interrupt handlers run with other interrupts held off, they must be short. Kernels split the work into a **top half**, which runs immediately and does only what cannot wait (acknowledge the device, copy data out of a small buffer), and a **bottom half**, which does the rest later with interrupts enabled. Linux calls its deferred work softirqs, tasklets, and work queues; Windows uses deferred procedure calls (DPCs).

Interrupt-driven I/O is ideal for devices that are slow relative to the CPU and transfer small amounts of data, such as keyboards and mice. For a fast device transferring data one word at a time, it fails: the interrupt overhead per word overwhelms the CPU.

### Direct memory access

For block transfers, the CPU hands the work to a **DMA controller** (or to a device that can act as a **bus master** itself):

1. The driver writes a **descriptor** to the controller: the memory address of the buffer, the number of bytes, the direction (to or from the device), and the device.
2. The controller transfers the data directly between the device and memory, using the memory bus.
3. When the whole block is done, the controller raises **one interrupt**.

The CPU is free during the transfer. It may run slightly slower when the controller and CPU compete for the memory bus (historically called **cycle stealing**), but most of the time it works out of its caches. **Scatter-gather DMA** accepts a list of buffers, so data spread over many pages can be transferred in one operation. Because DMA writes memory behind the CPU's back, systems must keep caches consistent with memory, and an **IOMMU** restricts which memory each device may access, protecting the system from faulty or malicious devices.

### Comparison

| | Programmed I/O | Interrupt-driven I/O | DMA |
| :--- | :--- | :--- | :--- |
| Who moves the data | CPU | CPU (in the handler) | DMA controller |
| CPU time while waiting | busy polling | free | free |
| Interrupts | none | one per unit (byte or word) | one per block |
| Best for | very short waits, simple hardware | slow devices, small transfers | disks, SSDs, network cards, graphics |

### Interrupt coalescing

Even with DMA, a network card receiving a million small packets per second would raise a million interrupts per second. **Interrupt coalescing** makes the device wait until several packets have arrived, or a short timer expires, before interrupting. Fewer interrupts mean less CPU overhead, at the cost of extra latency for the first packet in each batch. Linux's network stack goes further: under heavy load it disables the card's interrupts and polls it (the NAPI design), returning to interrupts when traffic drops.

## Worked examples

### Example 1: CPU overhead of three I/O methods

A 1 GHz CPU reads from a device delivering 100 MB per second. Handling an interrupt costs 500 cycles, and setting up a DMA transfer costs another 1000.

```python
CPU_HZ = 1_000_000_000
RATE = 100_000_000                       # bytes per second from the device

def report(name, events_per_second, cycles_per_event):
    used = events_per_second * cycles_per_event / CPU_HZ
    print(f"{name:28} {events_per_second:>12,.0f} events/s  CPU {used:8.1%}")

report("interrupt per 4-byte word", RATE / 4, 500)
report("DMA, interrupt per 4 KiB", RATE / 4096, 500 + 1000)
report("DMA, interrupt per 64 KiB", RATE / 65536, 500 + 1000)
```

Output:

```text
interrupt per 4-byte word      25,000,000 events/s  CPU  1250.0%
DMA, interrupt per 4 KiB           24,414 events/s  CPU     3.7%
DMA, interrupt per 64 KiB           1,526 events/s  CPU     0.2%
```

Interrupting once per 4-byte word would need 12.5 times the CPU's entire capacity, so it is impossible. DMA with 4 KiB blocks costs under 4% of the CPU, and larger blocks reduce this further, because the cost is per transfer rather than per byte. This is why every high-throughput device uses DMA.

### Example 2: Coalescing network interrupts

A network card receives 1,000,000 packets per second, and each interrupt costs 2 µs of CPU time. The card can interrupt after every packet or after a batch of packets.

```python
for batch in (1, 16, 64, 256):
    interrupts = 1_000_000 / batch
    cpu = interrupts * 2e-6               # seconds of CPU time per second
    print(f"coalesce {batch:>3} packets: {interrupts:>9,.0f} interrupts/s, CPU {cpu:6.1%}, "
          f"extra delay up to {batch - 1} us")
```

Output:

```text
coalesce   1 packets: 1,000,000 interrupts/s, CPU 200.0%, extra delay up to 0 us
coalesce  16 packets:    62,500 interrupts/s, CPU  12.5%, extra delay up to 15 us
coalesce  64 packets:    15,625 interrupts/s, CPU   3.1%, extra delay up to 63 us
coalesce 256 packets:     3,906 interrupts/s, CPU   0.8%, extra delay up to 255 us
```

One interrupt per packet would need two whole CPUs just to take the interrupts. Batching 64 packets cuts the overhead to about 3%, but the first packet of each batch may wait up to 63 µs (at one packet per microsecond) before the system notices it. Latency-sensitive applications, such as high-frequency trading, choose small batches or polling; bulk-transfer servers choose larger batches.

### Example 3: Tracing a disk read with DMA

A process calls `read` on a file whose block is not cached.

| Step | Who | Action |
| :--- | :--- | :--- |
| 1 | process | system call `read`; traps into the kernel |
| 2 | kernel | file system finds the block's disk address; driver builds a DMA descriptor pointing at a page-cache buffer |
| 3 | kernel | the process is put in the waiting state; the scheduler runs another process |
| 4 | disk controller | reads the sector and transfers it into memory by DMA; the CPU runs other work |
| 5 | disk controller | raises an interrupt when the transfer completes |
| 6 | ISR (top half) | acknowledges the controller; schedules deferred completion work |
| 7 | bottom half | marks the buffer valid and wakes the waiting process, which moves to the ready state |
| 8 | kernel | when the process runs, copies the data to its buffer and returns from `read` |

The CPU spends its time only in steps 1 to 3 and 6 to 8; during the slow part, the disk access, it runs other processes. This overlap of computation and I/O is the reason multiprogramming improves throughput.

## Applications

- **Storage:** SATA, NVMe, and USB storage controllers all move data by DMA; NVMe drives use queues of descriptors in memory shared with the host.
- **Networking:** network cards use DMA into rings of receive buffers, plus coalescing and polling under load.
- **Graphics and sound:** GPUs and audio hardware fetch textures, commands, and sample buffers from memory by DMA.
- **Embedded systems:** microcontrollers use DMA to stream data from sensors and to drive displays without CPU involvement.
- **Security:** IOMMUs block DMA attacks, in which a malicious device connected to a high-speed port tries to read or overwrite system memory.

## Common mistakes

- **Assuming interrupts are always better than polling.** For very frequent events or very short waits, the interrupt overhead can exceed the cost of polling.
- **Thinking the CPU is completely idle during DMA.** It runs other work, but the DMA controller still competes for memory bandwidth.
- **Doing slow work inside an interrupt handler,** which delays other interrupts; defer it to a bottom half.
- **Forgetting that DMA needs physical (or IOMMU-translated) addresses** and that the buffer must stay in memory (pinned) during the transfer.
- **Ignoring cache coherence:** without hardware support, the CPU might read stale cached data instead of what the device wrote to memory.

## Revision notes

- Device controllers expose status, command, and data registers, often memory-mapped.
- Programmed I/O: the CPU polls and moves every unit; simple but wasteful for slow devices.
- Interrupt-driven I/O: the device signals readiness; the CPU dispatches through the interrupt vector to an ISR. Priorities, masking, top and bottom halves.
- DMA: the driver programs a descriptor; the controller moves the whole block; one interrupt at the end. Scatter-gather, bus mastering, IOMMU.
- Overhead per event × events per second / CPU frequency = fraction of CPU used.
- Interrupt coalescing trades extra latency for fewer interrupts; heavy loads may switch to polling.

## Practice questions

:::question basic
What is the main advantage of interrupt-driven I/O over polling for a keyboard?
:::answer
A keyboard produces data rarely compared with the CPU's speed. With polling, the CPU would waste enormous numbers of cycles checking a status register that almost never changes. With interrupts, the CPU runs other work and is notified only when a key is actually pressed, so the only cost is a short handler per keystroke.
:::

:::question basic
What information does a driver give a DMA controller to start a transfer?
:::answer
The memory address of the buffer (or a list of buffers, for scatter-gather), the number of bytes to transfer, the direction (device to memory or memory to device), and which device or channel to use. The controller then performs the transfer and raises an interrupt when it is complete.
:::

:::question intermediate
Why are interrupt handlers split into a top half and a bottom half?
:::answer
While the top half runs, other interrupts at the same or lower priority are typically blocked, so long handlers would delay other devices and increase latency across the system. The top half therefore does only the urgent minimum, such as acknowledging the device and saving incoming data, and schedules the bottom half to finish the work (such as protocol processing or waking processes) later, with interrupts enabled and at a lower priority.
:::

:::question intermediate
A 2 GHz CPU uses DMA to read 500 MB per second in 16 KiB blocks. Each block costs 2000 cycles of setup and interrupt handling. What fraction of the CPU does this use?
:::answer
The number of blocks per second is $500 \times 10^6 / 16384 \approx 30{,}518$. They cost $30{,}518 \times 2000 \approx 6.1 \times 10^7$ cycles per second, out of $2 \times 10^9$ available: about 3.1% of the CPU.
:::

:::question intermediate
Under very heavy network traffic, Linux switches some network cards from interrupts to polling. Why can polling be more efficient in that situation?
:::answer
At high packet rates, packets are almost always waiting, so each poll finds useful work, and the CPU can process many packets per poll without the fixed cost of entering and leaving an interrupt handler for each one. With interrupts, the CPU can spend most of its time servicing interrupts and have little left to process the packets themselves, a condition called receive livelock. When traffic falls, polling would waste cycles finding nothing, so the system returns to interrupts.
:::

:::question advanced
Explain why an IOMMU is needed when devices can perform DMA, and what problems it solves.
:::answer
Without one, a device that performs DMA can read or write any physical memory address, bypassing the CPU's page tables and the OS's protection. A buggy driver or device could then corrupt the kernel, and a malicious device, for example one plugged into a high-speed external port, could read secrets or inject code. An IOMMU translates and checks device addresses through tables controlled by the OS, so each device can access only the buffers assigned to it. It also lets devices use virtual-like addresses for scattered physical pages and lets virtual machines be given direct access to devices safely.
:::

## Further learning

- **Next:** *Disk Scheduling Algorithms* decides the order in which queued disk requests are served.
- **Related:** *System Calls & Dual-Mode Execution* explains how interrupts and traps enter the kernel.
- **Related:** *Process Control Block & Lifecycle* shows the waiting and ready states that I/O moves processes between.
