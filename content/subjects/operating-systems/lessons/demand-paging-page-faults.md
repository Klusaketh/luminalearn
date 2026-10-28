---
lesson: demand-paging-page-faults
title: Demand Paging and Page Fault Handling
summary: Load pages only when they are used, handle the page faults this causes, measure the effect of the fault rate on access time, and understand copy-on-write, swap space, thrashing, and the working-set model.
minutes: 45
type: theory
objectives:
  - Explain demand paging and how the valid bit lets the hardware detect non-resident pages
  - List the steps the operating system takes to service a page fault
  - Calculate the effective access time for a given page-fault rate and the fault rate a target slowdown allows
  - Explain copy-on-write, thrashing, and the working-set model, and compute working sets for a reference string
---

## Introduction

Most programs never use all of their code. A word processor contains routines for mail merge, macros, and rare file formats that a typical session never calls, and an array may be declared far larger than any input ever needs. Loading all of that into memory before the program starts wastes memory and slows startup.

**Demand paging** loads a page only when the program first touches it. A program can start running with almost nothing in memory, and the logical address space can be far larger than physical memory, because only the pages actually in use need frames. This is the heart of **virtual memory**. Its cost is the **page fault**, a trap that occurs whenever the program touches a page that is not in memory, and a page fault is enormously slow compared with a memory access. This lesson explains how page faults are handled, quantifies their cost, and describes what happens when a system has too little memory for its workload.

**Before you start:** you should know paging, page tables, and the valid bit.

## Core theory

### The valid bit and lazy loading

Every page-table entry has a **valid (present) bit**. In demand paging:

- a **valid** entry means the page is in memory, in the frame given by the entry;
- an **invalid** entry means either the page is not part of the address space at all, or it is legal but currently on disk.

Initially, most or all entries are invalid. The first access to a page finds the bit clear, and the hardware raises a **page fault**. A system that brings in pages only when they fault, never in advance, is doing **pure demand paging**. Programs tolerate this well because of **locality of reference**: in any short period, they use only a small set of pages.

### Servicing a page fault

1. The MMU finds the valid bit clear and traps to the kernel, saving the process's state.
2. The kernel checks whether the address is legal for the process. If not, the process receives a segmentation fault and is usually terminated.
3. It finds a **free frame**. If none is free, a **page-replacement algorithm** chooses a victim page; if the victim is **dirty**, it is written to disk first.
4. It schedules a disk read of the needed page into the frame. The process is blocked, and the CPU runs other processes while the read completes.
5. When the read finishes (a disk interrupt), the kernel updates the page table: frame number in, valid bit set.
6. The process becomes ready again. When it runs, the **faulting instruction is restarted** from the beginning, and this time it succeeds.

The hardware must be able to restart any instruction after a fault, including instructions that touch several memory locations, which places real constraints on processor design.

### The cost of page faults

If $m$ is the memory access time, $s$ the page-fault service time, and $p$ the page-fault rate (the probability that an access faults):

$$\text{EAT} = (1 - p)\, m + p\, s.$$

Servicing a fault from a hard disk takes milliseconds (dominated by the disk's seek and rotation), while a memory access takes about a hundred nanoseconds, a ratio of tens of thousands. Even a tiny fault rate therefore slows the whole system dramatically. With a solid-state drive the service time is much shorter, but still thousands of times longer than a memory access.

### Copy-on-write

When a process calls `fork`, copying all its pages would be wasteful, especially since the child often calls `exec` immediately and discards them. With **copy-on-write (COW)**, parent and child initially **share** every page, marked read-only. When either one writes to a shared page, the write causes a protection fault; the kernel then copies just that page, gives the writer its own private copy, and lets the write proceed. Pages that are only read are never copied.

### Swap space

Pages that are evicted, and have no other copy on disk (such as heap and stack pages), are written to **swap space**, a disk area reserved for the purpose. Pages of program code need no swap space: they can be re-read from the executable file. Systems often zero-fill new heap and stack pages on first use (**zero-fill-on-demand**) instead of reading anything from disk.

### Thrashing

If a process does not have enough frames to hold the pages it is actively using, it faults, evicts a page it will soon need, faults again to get that page back, and so on. It spends more time paging than executing. This is **thrashing**. Across a whole system, it causes a vicious circle: CPU utilization drops because processes are waiting for the disk, a naive scheduler responds by admitting more processes to raise utilization, and each process gets even fewer frames.

### The working-set model

The **working set** of a process at time $t$, with window $\Delta$, is the set of distinct pages referenced in the most recent $\Delta$ references:

$$WS(t, \Delta) = \{\text{pages referenced in } (t - \Delta, t]\}.$$

It approximates the process's current locality. If $D = \sum_i |WS_i|$ is the total demand of all processes and $D$ exceeds the number of available frames, thrashing will occur; the OS should then **suspend** (swap out) a process rather than let them all thrash. A simpler control, the **page-fault frequency** scheme, gives a process more frames when its fault rate rises above an upper bound and takes frames away when it falls below a lower bound.

## Worked examples

### Example 1: Effective access time

Memory access takes 200 ns and servicing a page fault takes 8 ms.

```python
def eat_ns(memory_ns, fault_service_ms, p):
    return (1 - p) * memory_ns + p * fault_service_ms * 1_000_000

for p in (0, 1e-6, 1e-5, 1e-4, 1e-3):
    t = eat_ns(200, 8, p)
    print(f"fault rate {p:<7g} EAT {t:9.1f} ns, slowdown x{t / 200:.2f}")

p_max = (220 - 200) / (8_000_000 - 200)       # solve EAT = 220 ns for p
print(f"for at most 10% slowdown: p < {p_max:.2e}, about 1 fault per {round(1 / p_max):,} accesses")
```

Output:

```text
fault rate 0       EAT     200.0 ns, slowdown x1.00
fault rate 1e-06   EAT     208.0 ns, slowdown x1.04
fault rate 1e-05   EAT     280.0 ns, slowdown x1.40
fault rate 0.0001  EAT    1000.0 ns, slowdown x5.00
fault rate 0.001   EAT    8199.8 ns, slowdown x41.00
for at most 10% slowdown: p < 2.50e-06, about 1 fault per 399,990 accesses
```

One fault per thousand accesses makes the machine 41 times slower. To keep the slowdown under 10%, fewer than one access in about 400,000 may fault. Demand paging works in practice only because locality keeps real fault rates extremely low.

### Example 2: Copy-on-write after fork

```python
class Frame:
    def __init__(self, data):
        self.data, self.sharers = data, 1

copies = []

def fork(parent_table):
    child_table = dict(parent_table)          # copy the page table, not the pages
    for frame in parent_table.values():
        frame.sharers += 1                    # every frame is now shared, read-only
    return child_table

def write(table, page, value):
    frame = table[page]
    if frame.sharers > 1:                     # protection fault on a shared page
        frame.sharers -= 1
        frame = Frame(frame.data)             # copy just this page
        table[page] = frame
        copies.append(page)
    frame.data = value

parent = {page: Frame(f"data{page}") for page in range(4)}
child = fork(parent)
write(child, 2, "child's new data")
write(parent, 0, "parent's new data")
write(child, 2, "written again")              # already private: no further copy

print("pages copied:", copies)
print("still shared:", [p for p in range(4) if parent[p] is child[p]])
print(parent[2].data, "|", child[2].data)
```

Output:

```text
pages copied: [2, 0]
still shared: [1, 3]
data2 | written again
```

Forking cost nothing but a page-table copy. Only the two pages that were written got private copies, and the second write to page 2 needed no copy because the child already owned it. Pages 1 and 3, never written, remain shared, and if the child now called `exec`, they would never be copied at all.

### Example 3: Computing working sets

A process references pages in this order, and the working-set window is $\Delta = 10$ references:

`2 6 1 5 7 7 7 7 5 1 | 6 2 3 4 1 2 3 4 4 4 | 3 4 3 4 4 4 1 3 2 3 | 4 4 4 3 4 4 4`

```python
refs = [2, 6, 1, 5, 7, 7, 7, 7, 5, 1, 6, 2, 3, 4, 1, 2, 3, 4, 4, 4,
        3, 4, 3, 4, 4, 4, 1, 3, 2, 3, 4, 4, 4, 3, 4, 4, 4]

def working_set(refs, t, delta):
    return sorted(set(refs[max(0, t - delta + 1):t + 1]))   # the last delta references up to t

print("after reference 10:", working_set(refs, 9, 10))
print("after reference 26:", working_set(refs, 25, 10))
sizes = [len(working_set(refs, t, 10)) for t in range(len(refs))]
print("largest working set:", max(sizes), "smallest after warm-up:", min(sizes[9:]))
```

Output:

```text
after reference 10: [1, 2, 5, 6, 7]
after reference 26: [3, 4]
largest working set: 7 smallest after warm-up: 2
```

Early on, the process works with pages 1, 2, 5, 6, and 7; later its locality shrinks to pages 3 and 4. A process given 5 frames would fault rarely in both phases, while one given 2 frames would thrash in the first phase. During the transition between the two localities, the working set briefly grows to 7 pages, because the window still contains pages from the old locality as the new one starts.

## Applications

- **Fast program startup:** executables and libraries are mapped into memory and loaded page by page as code is first executed.
- **Memory-mapped files** (`mmap` on UNIX, file mapping on Windows) use demand paging to read file data only where it is accessed.
- **Efficient `fork`:** copy-on-write makes creating processes cheap, which shells and servers rely on.
- **Overcommitment:** systems can promise processes more virtual memory than physically exists, betting that not all of it will be touched.
- **Performance diagnosis:** tools such as `vmstat` on Linux report page-fault and swap rates, and a sudden rise in swapping is a classic sign of thrashing.

## Common mistakes

- **Treating every page fault as an error.** Most faults are a normal part of demand paging; only faults on illegal addresses are errors.
- **Forgetting that the faulting instruction is restarted** rather than skipped.
- **Ignoring the dirty bit** when computing fault service time: evicting a dirty page adds a disk write.
- **Underestimating how small the fault rate must be;** a rate that sounds tiny, such as one in a thousand, is catastrophic.
- **Responding to thrashing by adding processes.** Low CPU utilization caused by thrashing requires reducing the multiprogramming level.
- **Thinking copy-on-write copies pages at fork time.** It copies each page only on its first write.

## Revision notes

- Demand paging loads a page on first use; invalid entries trap with a page fault.
- Fault handling: trap, check legality, find or free a frame (write back a dirty victim), read the page, update the table, restart the instruction.
- $\text{EAT} = (1 - p)m + ps$; with $m = 200$ ns and $s = 8$ ms, $p$ must be below about $2.5 \times 10^{-6}$ for under 10% slowdown.
- Copy-on-write shares pages after `fork` and copies a page only when it is written.
- Thrashing: too few frames for the active pages, so the process pages constantly.
- Working set $WS(t, \Delta)$: distinct pages in the last $\Delta$ references; if total demand exceeds frames, suspend a process.

## Practice questions

:::question basic
What happens when a process accesses a page whose valid bit is clear but which belongs to its address space?
:::answer
The MMU raises a page fault, trapping to the kernel. The kernel confirms the address is legal, finds a free frame (evicting a page if necessary), reads the page from disk into the frame, updates the page-table entry with the frame number and sets the valid bit, and then restarts the instruction that faulted. The process sees only a delay.
:::

:::question basic
Why is copy-on-write particularly effective when `fork` is followed immediately by `exec`?
:::answer
`exec` replaces the child's entire address space with a new program, so any pages copied from the parent would be thrown away at once. With copy-on-write, `fork` only duplicates the page table and marks pages shared; if the child calls `exec` before writing, no page is ever copied, so creating the process is very cheap.
:::

:::question intermediate
Memory access takes 100 ns, and a page fault takes 10 ms to service when the victim page is clean and 20 ms when it is dirty. Dirty victims occur 70% of the time. What fault rate keeps the effective access time below 200 ns?
:::answer
The average service time is $0.3 \times 10 + 0.7 \times 20 = 17$ ms $= 17{,}000{,}000$ ns. We need $(1 - p) \cdot 100 + p \cdot 17{,}000{,}000 < 200$, so $p \cdot (17{,}000{,}000 - 100) < 100$, giving $p < 100 / 16{,}999{,}900 \approx 5.9 \times 10^{-6}$: about one fault per 170,000 accesses.
:::

:::question intermediate
Describe the vicious circle that makes thrashing worse in a system whose scheduler raises the degree of multiprogramming when CPU utilization is low.
:::answer
A process without enough frames faults constantly, so it spends most of its time waiting for the paging disk, and CPU utilization falls. Seeing low utilization, the scheduler admits more processes to keep the CPU busy. The new processes take frames from the existing ones, which then fault even more, so utilization falls further, prompting the scheduler to admit still more processes. The system ends up doing almost nothing but paging.
:::

:::question intermediate
For the reference string `1 2 3 1 2 4 5 4 5 4` and a window of $\Delta = 4$, what is the working set after the last reference?
:::answer
The last four references are 5, 4, 5, 4, so the working set is {4, 5}, of size 2. The process has moved from an early locality of pages 1, 2, and 3 to a new locality of pages 4 and 5.
:::

:::question advanced
Why must the hardware be able to restart an instruction after a page fault, and what problem arises for an instruction that copies a block of memory that may span page boundaries?
:::answer
A fault can occur partway through an instruction, and after the page is loaded the instruction must behave as if the fault never happened, so the processor must be able to re-execute it from the start, or resume it, with the correct result. A block-copy instruction may already have modified part of the destination before faulting on a later page. If the source and destination overlap, restarting from the beginning would read already-modified data and produce a wrong result. Hardware designs solve this by touching both ends of the source and destination before modifying anything, so any fault happens before the first write, or by saving intermediate state in registers so the instruction can resume where it stopped.
:::

## Further learning

- **Next:** *Page Replacement Algorithms* decides which page to evict when no frame is free.
- **Related:** *Paging & Page Tables* describes the valid and dirty bits used here.
- **Related:** *Process Control Block & Lifecycle* explains `fork`, which copy-on-write makes cheap.
