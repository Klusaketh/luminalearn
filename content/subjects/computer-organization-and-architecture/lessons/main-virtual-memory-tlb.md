---
lesson: main-virtual-memory-tlb
title: Main Memory, Virtual Memory & TLBs
summary: How DRAM main memory is organised, how virtual addresses are translated to physical addresses with page tables, how the translation lookaside buffer makes translation fast, and how to compute effective access times.
minutes: 50
type: theory
objectives:
  - Describe DRAM organisation into rows, columns, and banks, and explain refresh and row-buffer locality
  - Translate a virtual address into a physical address using page-table entries, page sizes, and multi-level tables
  - Explain the role of the TLB and calculate effective memory access time from TLB hit ratios and memory latencies
review: ai-draft
---
## Introduction

Every load and store a program executes names a **virtual address**. Before the processor can fetch the data, hardware must translate that address into a **physical address** in main memory, and it must do so on every access without slowing the program down. This lesson connects three pieces of hardware: **DRAM**, the main memory itself; **page tables**, the data structure that defines the translation; and the **translation lookaside buffer** (TLB), the small cache that makes translation fast enough to be practical.

**Before you start:** you should know the memory hierarchy, caches, and binary address arithmetic.

## Core theory

### DRAM organisation

Main memory is built from **dynamic RAM**, where each bit is a charge on a tiny capacitor. The charge leaks away, so every row must be **refreshed** periodically (typically every 64 ms). Bits are arranged in two-dimensional arrays of **rows** and **columns**, grouped into several independent **banks**. An access first **activates** a row, copying the entire row into a **row buffer** (row access, about $t_{RCD}$), then reads the requested column from the buffer (column access, CAS latency). Further accesses to the same open row are much faster than accesses to a different row, so memory controllers reorder requests to exploit **row-buffer locality**, and spreading data across banks lets several accesses proceed in parallel. Modern DDR memory transfers data on both clock edges in bursts, so bandwidth is high even though the latency of a random access is tens of nanoseconds, hundreds of processor cycles.

### Virtual memory and paging

Virtual memory gives each process its own address space, protects processes from one another, and lets the operating system keep only the actively used parts of a program in DRAM. The virtual address space is divided into fixed-size **pages** (commonly 4 KiB), and physical memory into **frames** of the same size. A virtual address splits into a **virtual page number** (VPN) and a **page offset**:

$$\text{offset bits} = \log_2(\text{page size}), \qquad \text{VPN bits} = \text{virtual address bits} - \text{offset bits}$$

The **page table** maps each VPN to a **page-table entry** (PTE) holding the **physical frame number** (PFN), a **valid** bit, protection bits (read, write, execute, user), and **dirty** and **referenced** bits used by the OS. The physical address is the PFN followed by the unchanged offset. An access to a page whose PTE is invalid raises a **page fault**, and the OS loads the page from disk or reports an error.

### Multi-level page tables

A flat table for a 48-bit virtual address space with 4 KiB pages would need $2^{36}$ entries per process, far too much. **Multi-level** (hierarchical) page tables split the VPN into several indices; each level is a small table pointing to the next, and tables for unused regions are never allocated. x86-64 uses four levels of 9 bits each ($4 \times 9 + 12 = 48$ bits). The cost: a **page-table walk** needs one memory access per level before the data access itself.

### The translation lookaside buffer

The **TLB** is a small, fast, usually highly associative cache of recent translations (VPN → PFN plus permissions), typically 64 entries at the first level and around a thousand in a second-level TLB. On a **TLB hit**, translation costs essentially nothing extra and can overlap with the cache lookup. On a **TLB miss**, hardware (or, on some architectures, software) walks the page table, then inserts the translation into the TLB. Because programs have locality and each entry covers a whole page, TLB hit ratios are usually well above 99%. **Huge pages** (2 MiB or 1 GiB) let one TLB entry cover far more memory. When the OS switches processes, it must flush the TLB or tag entries with an **address-space identifier** (ASID) so one process cannot use another's translations.

### Effective access time

With TLB lookup time $t$, memory access time $m$, TLB hit ratio $h$, and a single-level page table:

$$\text{EAT} = h(t + m) + (1 - h)(t + 2m)$$

A hit costs the TLB lookup plus one memory access; a miss costs the lookup, one access to read the PTE, and one access for the data. With $k$ levels of page table, a miss costs $t + (k + 1)m$. (Real processors also cache page-table entries in the data caches and in dedicated paging-structure caches, which reduces the miss penalty.)

## Worked examples

### Example 1: Translating an address

A system has 32-bit virtual addresses, 4 KiB pages, and a single-level page table. Translate the virtual address `0x00403A7C`, given that PTE 0x403 contains frame number `0x1F2` and is valid.

1. Offset bits: $\log_2 4096 = 12$, so the low 12 bits (3 hex digits) are the offset: `0xA7C`.
2. VPN: the remaining 20 bits, `0x00403`, which is page 0x403.
3. The PTE gives frame `0x1F2`.
4. Physical address = frame number followed by offset = `0x1F2A7C`.

A short Python check of the same arithmetic:

```python
va = 0x00403A7C
page_size = 4096
offset_bits = page_size.bit_length() - 1
vpn, offset = va >> offset_bits, va & (page_size - 1)
page_table = {0x403: 0x1F2}
pa = (page_table[vpn] << offset_bits) | offset
print(offset_bits, hex(vpn), hex(offset), hex(pa))
entries = 2 ** (32 - offset_bits)
print(entries, "entries,", entries * 4 // 2**20, "MiB with 4-byte PTEs")
```

Output:

```text
12 0x403 0xa7c 0x1f2a7c
1048576 entries, 4 MiB with 4-byte PTEs
```

The last line shows why flat tables are costly: even a 32-bit address space needs a 4 MiB table per process, most of it unused.

### Example 2: Effective access time with a TLB

Memory access takes 100 ns, TLB lookup 5 ns. Compute the effective access time for a single-level table with hit ratios of 80% and 99%, and for a four-level table with 99%.

- Single level, $h = 0.8$: $0.8(5 + 100) + 0.2(5 + 200) = 84 + 41 = 125$ ns, a 25% slowdown over the ideal 100 ns.
- Single level, $h = 0.99$: $0.99 \times 105 + 0.01 \times 205 = 103.95 + 2.05 = 106$ ns.
- Four levels, $h = 0.99$: a miss costs $5 + 5 \times 100 = 505$ ns, so $0.99 \times 105 + 0.01 \times 505 = 103.95 + 5.05 = 109$ ns.

```python
def eat(hit, tlb=5, mem=100, levels=1):
    return hit * (tlb + mem) + (1 - hit) * (tlb + (levels + 1) * mem)

for hit, levels in [(0.80, 1), (0.99, 1), (0.99, 4)]:
    print(f"hit {hit:.2f}, {levels} level(s): {eat(hit, levels=levels):.2f} ns")
```

Output:

```text
hit 0.80, 1 level(s): 125.00 ns
hit 0.99, 1 level(s): 106.00 ns
hit 0.99, 4 level(s): 109.00 ns
```

A high hit ratio hides most of the cost of deep page tables, which is why TLBs are essential.

## Applications

- **Process isolation:** each process sees only its own pages; protection bits stop illegal accesses.
- **Memory over-commitment:** pages not in use stay on disk until a page fault brings them in.
- **Shared libraries and copy-on-write:** several processes map the same physical frames.
- **Database and HPC tuning:** huge pages and NUMA-aware allocation reduce TLB misses and memory latency.

## Common mistakes

- **Translating the offset.** Only the page number is translated; the offset is copied unchanged.
- **Forgetting the extra memory access on a TLB miss.** Each page-table level adds one access.
- **Confusing the TLB with the data cache.** The TLB caches translations, not data.
- **Assuming DRAM latency is constant.** Row-buffer hits are much faster than row misses.

## Revision notes

- DRAM: capacitor cells, refresh, rows and columns in banks, row buffer, CAS latency.
- Virtual address = VPN + offset; offset bits = $\log_2$(page size).
- PTE: frame number, valid, protection, dirty, referenced bits.
- Multi-level tables save space but need one memory access per level on a walk.
- TLB: cache of translations; hits are fast; misses trigger a page-table walk.
- $\text{EAT} = h(t + m) + (1 - h)(t + (k + 1)m)$ for $k$ levels.

## Practice questions

:::question basic
With 8 KiB pages and 32-bit virtual addresses, how many bits are in the page offset and in the VPN?
:::answer
The offset needs $\log_2 8192 = 13$ bits, leaving $32 - 13 = 19$ bits for the virtual page number.
:::

:::question basic
What does the TLB store, and why does it make virtual memory practical?
:::answer
It stores recently used translations from virtual page numbers to physical frame numbers, with their permission bits. Without it, every memory access would need one or more extra memory accesses to read page-table entries; with a high TLB hit ratio, most translations cost almost nothing.
:::

:::question intermediate
Translate virtual address `0x2C3D5` with 4 KiB pages if virtual page `0x2C` maps to frame `0x7`.
:::answer
The offset is the low 12 bits, `0x3D5`, and the VPN is `0x2C`. Replacing the VPN with frame `0x7` gives the physical address `0x73D5`.
:::

:::question intermediate
Memory access takes 80 ns, TLB lookup 2 ns, and the TLB hit ratio is 98% with a two-level page table. What is the effective access time?
:::answer
A hit costs $2 + 80 = 82$ ns; a miss costs $2 + 3 \times 80 = 242$ ns (two page-table accesses and the data access). EAT $= 0.98 \times 82 + 0.02 \times 242 = 80.36 + 4.84 = 85.2$ ns.
:::

:::question advanced
Why do large in-memory databases often enable 2 MiB huge pages, and what is the drawback?
:::answer
One huge-page TLB entry covers 512 times as much memory as a 4 KiB entry, so a TLB of the same size maps far more of the database, sharply reducing TLB misses and page-table walks, and the walks are also one level shorter. The drawbacks are internal fragmentation (a whole 2 MiB page is allocated even for small regions), coarser-grained paging and copy-on-write, and difficulty finding contiguous 2 MiB physical regions on a fragmented system.
:::

## Further learning

- **Next:** *I/O Techniques: Polling, Interrupts & DMA* covers how devices move data into this memory.
- **Related:** *Paging and Page Tables* and *Demand Paging* in Operating Systems explain the software side of virtual memory.
