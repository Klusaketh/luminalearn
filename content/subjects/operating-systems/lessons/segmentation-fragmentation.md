---
lesson: segmentation-fragmentation
title: Segmentation and Fragmentation
summary: Divide a process into variable-sized logical segments, translate segment-offset addresses with a segment table, and compare internal and external fragmentation, first-fit, best-fit, and worst-fit allocation, and compaction.
minutes: 45
type: theory
objectives:
  - Explain segmentation as a programmer's view of memory and translate segment-offset addresses with a segment table
  - Distinguish internal fragmentation from external fragmentation and identify which schemes suffer from each
  - Simulate first-fit, best-fit, and worst-fit allocation and compare their results
  - Evaluate compaction and paged segmentation as remedies for external fragmentation
---

## Introduction

Programmers do not think of a program as a flat array of bytes. They think of it as a collection of parts: the code, the global variables, the heap, the stack, perhaps a table of constants or a shared library. Each part has a natural size and a natural purpose, and it would be convenient for the hardware to treat each one as a separate unit, with its own size and its own permissions: code executable but not writable, data writable but not executable.

**Segmentation** is a memory-management scheme built on exactly this view. A process's memory is a set of **segments** of different lengths, and every address names a segment and a position within it. Segmentation makes protection and sharing natural, but because segments vary in size, placing them in physical memory runs into **external fragmentation**, the problem of free memory broken into unusable scraps. This lesson covers segmentation, the two kinds of fragmentation, the classic allocation strategies, and the remedies.

**Before you start:** you should know base-and-limit relocation and paging.

## Core theory

### Segments and segment-offset addresses

A logical address under segmentation is a pair $\langle s, d \rangle$: a **segment number** $s$ and an **offset** $d$ within that segment. A compiler might create segments for the code, the global data, the heap, each thread's stack, and the standard library.

The **segment table** has one entry per segment, each with:

- a **base**: the starting physical address of the segment;
- a **limit**: the length of the segment;
- **protection bits**, such as read, write, and execute, and often a valid bit.

Translation:

$$\text{if } d < \text{limit}[s]: \quad \text{physical} = \text{base}[s] + d; \qquad \text{otherwise: trap (segmentation fault).}$$

This is base-and-limit relocation applied separately to each segment. The CPU locates the segment table through a **segment-table base register** and checks the segment number against a **segment-table length register**.

### Advantages of segmentation

- **Protection by purpose:** the code segment can be marked execute-only and the data segment non-executable, catching many bugs and attacks.
- **Sharing:** two processes can share a segment, such as library code, by pointing their segment-table entries at the same physical memory.
- **Natural growth:** a segment such as the stack or heap can grow independently, as long as there is room.

### Two kinds of fragmentation

- **Internal fragmentation** is wasted space **inside** an allocated block, because the allocator hands out memory in fixed units larger than the request. Paging has it: a 5000-byte region needs two 4096-byte pages, wasting 3192 bytes in the second.
- **External fragmentation** is free memory **between** allocated blocks, in pieces too small or too scattered to satisfy a request, even though the total free memory would suffice. Segmentation, and any variable-sized contiguous allocation, has it.

| Scheme | Internal fragmentation | External fragmentation |
| :--- | :--- | :--- |
| Fixed-size partitions | yes | no (but partitions limit sizes) |
| Variable-size contiguous allocation | no | yes |
| Segmentation | no | yes |
| Paging | yes (last page) | no |

### Allocation strategies

With variable-sized allocation, free memory is a list of **holes**. To place a block of size $n$:

- **First fit:** use the first hole that is large enough. Fast, because the search stops early.
- **Best fit:** use the smallest hole that is large enough. Leaves the smallest leftover, but must search the whole list (unless it is sorted by size) and tends to create many tiny useless holes.
- **Worst fit:** use the largest hole, hoping the leftover is still useful. In simulations it generally does worse than the other two.

Simulation studies have found first fit and best fit better than worst fit in both speed and storage use, with first fit usually faster. Statistical analysis of first fit gives the **50-percent rule**: with $N$ allocated blocks, about $0.5N$ blocks' worth of memory is lost to external fragmentation, so roughly one third of memory may be unusable.

### Remedies

- **Compaction:** move allocated blocks together so that the free holes merge into one large hole. It is possible only with execution-time binding (the moved processes' base registers are updated), and it is expensive, because large amounts of memory must be copied.
- **Paging** removes external fragmentation by using fixed-size units, at the cost of some internal fragmentation.
- **Paged segmentation:** each segment is itself paged. The programmer keeps the segment view (and its protection), and physical memory is allocated in frames. Intel's 32-bit x86 architecture supported this combination; in 64-bit mode, segmentation is largely disabled and the flat address space is simply paged.

## Worked examples

### Example 1: Translating segment-offset addresses

A process has this segment table:

| Segment | Base | Limit |
| :---: | :---: | :---: |
| 0 | 1400 | 1000 |
| 1 | 6300 | 400 |
| 2 | 4300 | 400 |
| 3 | 3200 | 1100 |
| 4 | 4700 | 1000 |

```python
segment_table = {0: (1400, 1000), 1: (6300, 400), 2: (4300, 400), 3: (3200, 1100), 4: (4700, 1000)}

def translate(segment, offset):
    if segment not in segment_table:
        return "trap: invalid segment"
    base, limit = segment_table[segment]
    if offset >= limit:
        return f"trap: offset {offset} beyond limit {limit}"
    return base + offset

for s, d in [(2, 53), (3, 852), (0, 1222), (1, 399), (4, 1000), (5, 10)]:
    print(f"<{s}, {d}> ->", translate(s, d))
```

Output:

```text
<2, 53> -> 4353
<3, 852> -> 4052
<0, 1222> -> trap: offset 1222 beyond limit 1000
<1, 399> -> 6699
<4, 1000> -> trap: offset 1000 beyond limit 1000
<5, 10> -> trap: invalid segment
```

Byte 53 of segment 2 is at $4300 + 53 = 4353$. Segment 0 is only 1000 bytes long, so offset 1222 is a segmentation fault, as is offset 1000 in segment 4, one past its last byte. Notice that the segments are not stored in order in physical memory: segment 3 (from 3200) sits below segment 2 (from 4300), and nothing requires the segments of one process to be next to each other.

### Example 2: First fit, best fit, and worst fit

Memory has free holes of 100, 500, 200, 300, and 600 KB, in that order. Processes request 212, 417, 112, and 426 KB, in that order.

```python
def allocate(holes, requests, strategy):
    holes, placements = list(holes), []
    for size in requests:
        fits = [i for i, h in enumerate(holes) if h >= size]
        if not fits:
            placements.append(f"{size}K waits")
            continue
        if strategy == "first":
            i = fits[0]
        elif strategy == "best":
            i = min(fits, key=lambda k: holes[k])
        else:
            i = max(fits, key=lambda k: holes[k])
        placements.append(f"{size}K->{holes[i]}K")
        holes[i] -= size                   # the leftover stays a (smaller) hole
    return placements, holes

for strategy in ("first", "best", "worst"):
    placements, holes = allocate([100, 500, 200, 300, 600], [212, 417, 112, 426], strategy)
    print(f"{strategy:5}: {', '.join(placements)}; holes left {holes}, total {sum(holes)}K")
```

Output:

```text
first: 212K->500K, 417K->600K, 112K->288K, 426K waits; holes left [100, 176, 200, 300, 183], total 959K
best : 212K->300K, 417K->500K, 112K->200K, 426K->600K; holes left [100, 83, 88, 88, 174], total 533K
worst: 212K->600K, 417K->500K, 112K->388K, 426K waits; holes left [100, 83, 200, 300, 276], total 959K
```

Here best fit is the only strategy that places all four processes, because it keeps the 600 KB hole intact for the largest request. Under first fit and worst fit, the 426 KB process must wait even though 959 KB is free in total; no single hole is big enough. That is external fragmentation. The result depends on the request sequence: a different sequence can favour first fit, which is why the strategies are compared by simulation over many workloads.

### Example 3: Compaction

After the first-fit allocation above, the free holes are 100, 176, 200, 300, and 183 KB, scattered between allocated blocks. Compaction slides every allocated block towards one end of memory, combining the holes into a single hole of $100 + 176 + 200 + 300 + 183 = 959$ KB, and the waiting 426 KB process can be placed. The cost is copying every block that moves; if 1 GB of allocated memory had to move at 10 GB per second, compaction would take about 0.1 seconds, during which the moved processes cannot run. This is why systems prefer paging, which never needs compaction, to frequent compaction.

## Applications

- **Protection in modern paging systems** follows the segmentation idea, with per-region permissions: Linux and Windows mark code pages executable and data pages non-executable (the NX bit).
- **Memory regions:** an operating system's description of a process's address space (code, heap, stack, mapped libraries, as listed in Linux's `/proc/<pid>/maps`) is a segment-like view implemented on top of paging.
- **Memory allocators** such as `malloc` face the same fit decisions and fragmentation inside a process's heap, using size classes and free lists to limit them.
- **File systems** suffer external fragmentation when files are stored contiguously, and defragmentation tools perform compaction on disks.
- **Historical systems:** segmentation was prominent in the Burroughs B5000 and Multics, and Intel processors supported segments from the 8086 onwards.

## Common mistakes

- **Comparing the offset with the base instead of the limit.** The check is offset < limit; only then is the base added.
- **Confusing internal and external fragmentation.** Internal is waste inside allocated blocks; external is unusable space between them.
- **Assuming best fit always wins.** It leaves the smallest leftovers, which can accumulate into many tiny unusable holes; results depend on the workload.
- **Forgetting that compaction requires execution-time binding,** because the moved processes' addresses change.
- **Thinking segmentation and paging are mutually exclusive.** They can be combined, with each segment paged.

## Revision notes

- Segmentation: logical address $\langle s, d \rangle$; segment table entries hold base, limit, and protection.
- Translation: trap unless $d < \text{limit}[s]$; physical = base[s] + d.
- Segmentation supports protection and sharing by purpose, but suffers external fragmentation.
- Internal fragmentation: waste inside blocks (paging). External: free space split into unusable holes (segmentation, contiguous allocation).
- First fit (fast), best fit (smallest leftover), worst fit (largest leftover; generally worst). 50-percent rule for first fit.
- Remedies: compaction (costly, needs run-time binding), paging, or paged segmentation.

## Practice questions

:::question basic
What is the difference between internal and external fragmentation? Give one memory-management scheme that suffers from each.
:::answer
Internal fragmentation is unused memory inside an allocated block, because the block is larger than requested; paging suffers from it in the last page of each region. External fragmentation is free memory split into many separate holes, none large enough for a request even though the total would be; segmentation and variable-sized contiguous allocation suffer from it.
:::

:::question basic
Using the segment table from Example 1, translate ⟨3, 1099⟩ and ⟨2, 400⟩.
:::answer
Segment 3 has base 3200 and limit 1100. Offset 1099 is less than 1100, so the physical address is $3200 + 1099 = 4299$. Segment 2 has limit 400, and offset 400 is not less than 400, so the access traps as a segmentation fault.
:::

:::question intermediate
Holes of 300, 600, 350, 200, 750, and 125 KB are free, in that order. Where would first fit and best fit place a request for 115 KB, and a later request for 500 KB?
:::answer
First fit places 115 KB in the first hole that fits, the 300 KB hole, leaving 185 KB; it then places 500 KB in the first hole of at least 500 KB, the 600 KB hole, leaving 100 KB. Best fit places 115 KB in the smallest adequate hole, the 125 KB hole, leaving 10 KB; it then places 500 KB in the 600 KB hole, the smallest that is at least 500 KB, leaving 100 KB.
:::

:::question intermediate
Why is compaction possible only with execution-time address binding?
:::answer
Compaction moves processes to new physical locations. If addresses were bound at compile or load time, the programs would contain physical addresses that would all become wrong after the move, and they cannot be found and fixed in general. With execution-time binding, programs use logical addresses, and the OS only has to update each moved process's base register (or segment-table entries) to point at the new location.
:::

:::question intermediate
A process needs 10,300 bytes, and the system uses 4 KiB pages. How much memory is lost to internal fragmentation? How would the answer differ with 1 KiB pages?
:::answer
With 4096-byte pages, the process needs $\lceil 10300 / 4096 \rceil = 3$ pages = 12,288 bytes, wasting $12288 - 10300 = 1988$ bytes. With 1024-byte pages, it needs $\lceil 10300 / 1024 \rceil = 11$ pages = 11,264 bytes, wasting 964 bytes. Smaller pages reduce internal fragmentation but require more page-table entries.
:::

:::question advanced
Explain how paged segmentation combines the advantages of both schemes, and describe the steps of translating an address under it.
:::answer
Each segment keeps its own length and protection, so the programmer's view of separate code, data, and stack regions, with different permissions, is preserved. But each segment is divided into pages stored in arbitrary frames, so physical memory is allocated in fixed-size units and there is no external fragmentation. To translate ⟨s, d⟩: check $d$ against segment $s$'s limit and permissions; split $d$ into a page number $p$ and a page offset $o$; look up page $p$ in segment $s$'s page table to get frame $f$; the physical address is $f \times \text{page size} + o$. The costs are more complex hardware and an extra lookup, mitigated by the TLB.
:::

## Further learning

- **Next:** *Demand Paging & Page Fault Handling* loads pages only when they are first used.
- **Related:** *Paging & Page Tables* removes external fragmentation with fixed-size frames.
- **Related:** *File Allocation & Directory Structures* faces the same contiguous-allocation trade-offs on disk.
