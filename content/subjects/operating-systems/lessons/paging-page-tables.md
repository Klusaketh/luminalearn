---
lesson: paging-page-tables
title: Paging and Page Tables
summary: Divide memory into fixed-size pages and frames, translate addresses through a page table, speed translation with a TLB, and keep page tables small with multi-level and inverted designs.
minutes: 45
type: theory
objectives:
  - Split a logical address into a page number and an offset and translate it through a page table
  - Describe the fields of a page-table entry and how they support protection and virtual memory
  - Calculate effective memory access time with a translation lookaside buffer
  - Compute page-table sizes and explain how multi-level, hashed, and inverted page tables reduce them
---

## Introduction

Base-and-limit relocation gives each process one contiguous block of physical memory. That is simple, but it causes a serious problem: as processes come and go, free memory breaks into scattered holes, and a new process may not fit anywhere even when plenty of memory is free in total. Moving processes around to merge the holes is slow.

**Paging** removes the need for contiguity altogether. Physical memory is divided into small fixed-size **frames**, each process's logical memory into **pages** of the same size, and any page can be placed in any free frame. A per-process **page table** records where each page went. Paging is the foundation of memory management in virtually every modern operating system, from phones to supercomputers, and it is what makes virtual memory, copy-on-write, and shared libraries possible.

**Before you start:** you should know logical and physical addresses and how a base register relocates a process.

## Core theory

### Pages, frames, and address translation

If the page size is $2^n$ bytes and logical addresses have $m$ bits, a logical address splits into:

- a **page number** $p$: the high $m - n$ bits, used as an index into the page table;
- a **page offset** $d$: the low $n$ bits, the position within the page.

$$p = \left\lfloor \frac{a}{2^n} \right\rfloor, \qquad d = a \bmod 2^n$$

The page table maps $p$ to a **frame number** $f$, and the physical address is

$$\text{physical} = f \times 2^n + d.$$

Because page sizes are powers of two, the split is just a matter of taking bits, and the hardware does it in every memory access. Page sizes of 4 KiB are typical, and many processors also support large pages of 2 MiB or 1 GiB.

### What a page-table entry holds

| Bit or field | Purpose |
| :--- | :--- |
| Frame number | where the page is in physical memory |
| Valid (present) bit | is the page in memory and part of the process's address space? |
| Protection bits | read, write, and execute permissions |
| Dirty (modified) bit | set by hardware when the page is written; dirty pages must be written back before eviction |
| Referenced (accessed) bit | set by hardware when the page is used; guides page replacement |
| User/supervisor bit | whether user-mode code may access the page |

An access to an invalid page or one that violates the protection bits causes a trap to the kernel.

### Fragmentation under paging

Paging has no **external** fragmentation: any free frame can hold any page. It does have **internal** fragmentation: the last page of a region is usually only partly used. On average half a page per region is wasted, which argues for small pages; smaller pages, however, mean larger page tables and more translation overhead.

### The translation lookaside buffer

The page table lives in memory, so a naive implementation needs **two** memory accesses per data access: one to read the page-table entry and one to read the data. The fix is a small, fast, associative hardware cache of recent translations, the **translation lookaside buffer (TLB)**, typically with tens to a few thousand entries.

- On a **TLB hit**, the frame number comes straight from the TLB.
- On a **TLB miss**, the page table is read from memory (by hardware or by the OS), and the translation is added to the TLB.

If a memory access takes $m$ time and the TLB hit ratio is $h$, ignoring the tiny TLB lookup time:

$$\text{EAT} = h \cdot m + (1 - h) \cdot 2m.$$

Programs typically show strong **locality**, so hit ratios above 99% are common. Some TLBs tag entries with an **address-space identifier (ASID)**, so they need not be flushed on every context switch.

### The size problem and its solutions

A 32-bit logical address with 4 KiB pages ($2^{12}$) has $2^{20}$ pages, so a flat page table has about a million entries; at 4 bytes per entry, that is 4 MiB **per process**, mostly describing unused addresses. With 64-bit addresses, a flat table would be impossibly large. Three designs address this:

- **Hierarchical (multi-level) page tables:** page the page table itself. A 32-bit address can be split into 10 + 10 + 12 bits: an outer table of 1024 entries points to inner tables of 1024 entries, and inner tables for unused regions are simply not allocated. x86-64 uses four levels (9 + 9 + 9 + 9 + 12 bits for 48-bit addresses), and newer processors support five.
- **Hashed page tables:** hash the virtual page number into a table of chains; useful for sparse 64-bit address spaces.
- **Inverted page tables:** one entry per **physical frame** rather than per virtual page, recording which process and page occupy it. Memory use is proportional to physical memory, but lookups need a search, usually through a hash table.

Multi-level tables save space but make a TLB miss more expensive, since each level is another memory access; this is why the TLB matters so much.

### Sharing pages

Two page tables can map pages to the same frame. This lets processes share the read-only code of a program or library, and lets the kernel set up shared-memory regions between processes. **Copy-on-write**, used by `fork`, maps the parent's pages into the child read-only and copies a page only when one of them writes to it.

## Worked examples

### Example 1: Translating addresses by hand

Page size 4 KiB = 4096 bytes. The page table of a process maps page 0 → frame 5, page 1 → frame 9, page 2 → frame 2, page 3 → invalid.

| Logical address | Page $p = \lfloor a/4096 \rfloor$ | Offset $d = a \bmod 4096$ | Frame | Physical $f \cdot 4096 + d$ |
| :--- | :--- | :--- | :--- | :--- |
| 100 | 0 | 100 | 5 | 20580 |
| 5000 | 1 | 904 | 9 | 37768 |
| 8195 | 2 | 3 | 2 | 8195 |
| 13000 | 3 | 712 | invalid | trap |

For 5000: $5000 = 1 \times 4096 + 904$, so page 1, offset 904, physical $9 \times 4096 + 904 = 36864 + 904 = 37768$. For 8195, the page happens to sit in frame 2, so the physical address equals the logical one, a coincidence.

### Example 2: Translation with bit operations and a TLB

```python
PAGE_BITS = 12                                   # 4 KiB pages
page_table = {0: 5, 1: 9, 2: 2}                  # page -> frame; page 3 is not valid
tlb, stats = {}, {"hits": 0, "misses": 0}

def translate(address):
    page, offset = address >> PAGE_BITS, address & ((1 << PAGE_BITS) - 1)
    if page in tlb:
        stats["hits"] += 1
        frame = tlb[page]
    else:
        stats["misses"] += 1
        if page not in page_table:
            raise MemoryError(f"page fault or invalid access at {address}")
        frame = page_table[page]
        tlb[page] = frame                        # cache the translation
    return (frame << PAGE_BITS) | offset

for address in (100, 5000, 8195, 104, 5004, 4200):
    print(address, "->", translate(address))
print(stats)
try:
    translate(13000)
except MemoryError as error:
    print(error)
```

Output:

```text
100 -> 20580
5000 -> 37768
8195 -> 8195
104 -> 20584
5004 -> 37772
4200 -> 36968
{'hits': 3, 'misses': 3}
page fault or invalid access at 13000
```

Shifting right by 12 bits divides by 4096, and masking with $4095$ (twelve 1 bits) keeps the remainder, exactly the split the hardware performs. The first access to each page misses the TLB; the later accesses to pages 0 and 1 hit. Locality is what makes the TLB effective: consecutive accesses tend to fall in the same few pages.

### Example 3: Effective access time and page-table size

```python
def eat(memory_ns, hit_ratio, levels=1):
    # a hit needs one memory access; a miss walks `levels` page-table levels first
    return hit_ratio * memory_ns + (1 - hit_ratio) * (levels + 1) * memory_ns

for h in (0.80, 0.99):
    print(f"hit ratio {h:.0%}: one-level {eat(100, h):.1f} ns, four-level {eat(100, h, 4):.1f} ns")

pages = 2 ** 32 // 2 ** 12
print("flat 32-bit table:", pages, "entries =", pages * 4 // 2 ** 20, "MiB per process")
```

Output:

```text
hit ratio 80%: one-level 120.0 ns, four-level 180.0 ns
hit ratio 99%: one-level 101.0 ns, four-level 104.0 ns
flat 32-bit table: 1048576 entries = 4 MiB per process
```

With a 100 ns memory and an 80% hit ratio, a one-level table adds 20% to every access, and a four-level table, whose misses cost five memory accesses, adds 80%. At a 99% hit ratio, the overheads shrink to 1% and 4%. A flat page table for a 32-bit address space takes 4 MiB per process, which is why systems with many processes need hierarchical tables that omit unused regions.

## Applications

- **Every mainstream OS** (Linux, Windows, macOS, Android, iOS) manages memory with paging on hardware that supports it.
- **Process isolation:** each process has its own page table, so it cannot even name another process's memory.
- **Efficient process creation:** `fork` with copy-on-write shares pages until they are modified.
- **Memory-mapped files:** `mmap` maps a file's pages into a process's address space, loading them on demand.
- **Large pages** reduce TLB misses for databases and virtual machines with very large memory footprints.

## Common mistakes

- **Mixing up page numbers and frame numbers.** The page number indexes the page table; the frame number comes out of it.
- **Forgetting that the offset is copied unchanged** into the physical address.
- **Believing paging eliminates all fragmentation.** It removes external fragmentation, but internal fragmentation remains in the last page.
- **Counting a TLB miss as one memory access.** It costs one page-table access per level plus the data access.
- **Assuming a page table must cover the whole address space densely.** Multi-level tables allocate only the parts in use.

## Revision notes

- Logical address = page number (high bits) + offset (low bits). Physical = frame × page size + offset.
- Page-table entries hold the frame number plus valid, protection, dirty, referenced, and user/supervisor bits.
- Paging: no external fragmentation, some internal fragmentation (on average half a page per region).
- TLB caches translations. $\text{EAT} = h \cdot m + (1 - h)(k + 1)m$ for a $k$-level table.
- A flat 32-bit table with 4 KiB pages has $2^{20}$ entries (4 MiB at 4 bytes each).
- Multi-level, hashed, and inverted page tables reduce page-table memory; shared frames enable shared code and copy-on-write.

## Practice questions

:::question basic
With 1 KiB pages, what are the page number and offset of logical address 2500?
:::answer
A page holds 1024 bytes. $2500 = 2 \times 1024 + 452$, so the page number is 2 and the offset is 452.
:::

:::question basic
Why does paging have no external fragmentation?
:::answer
Every frame is the same size as every page, so any free frame can hold any page, and a process's pages do not need to be next to each other in physical memory. There is never a situation where enough memory is free in total but cannot be used because it is split into pieces that are too small, which is what external fragmentation means.
:::

:::question intermediate
A system has 32-bit logical addresses and 8 KiB pages. How many bits are in the page number and the offset, and how many entries does a flat page table have?
:::answer
8 KiB is $2^{13}$ bytes, so the offset has 13 bits and the page number has $32 - 13 = 19$ bits. A flat page table has $2^{19} = 524{,}288$ entries; at 4 bytes per entry, that is 2 MiB per process.
:::

:::question intermediate
Memory access takes 50 ns and the TLB hit ratio is 95%, with a single-level page table. What is the effective access time? What hit ratio is needed to keep the slowdown below 2%?
:::answer
EAT $= 0.95 \times 50 + 0.05 \times 100 = 47.5 + 5 = 52.5$ ns, a 5% slowdown. In general EAT $= 50(1 + (1 - h))$, so a slowdown below 2% needs $1 - h < 0.02$, that is a hit ratio above 98%.
:::

:::question intermediate
What do the dirty bit and the referenced bit record, and who sets them?
:::answer
The hardware sets the dirty bit when the page is written and the referenced bit when the page is read or written. The OS reads and clears them. The dirty bit tells the OS whether a page must be written back to disk before its frame is reused (a clean page can simply be discarded); the referenced bit tells the page-replacement algorithm which pages have been used recently.
:::

:::question advanced
A 48-bit virtual address space uses 4 KiB pages and 8-byte page-table entries. How many levels are needed if each level's table must fit in one page, and why does x86-64 use four levels?
:::answer
A 4 KiB page holds $4096 / 8 = 512 = 2^9$ entries, so each level resolves 9 bits of the page number. The page number has $48 - 12 = 36$ bits, and $36 / 9 = 4$, so four levels are needed. This is exactly the x86-64 design: 9 + 9 + 9 + 9 bits of page number and 12 bits of offset. Each table is one page, tables for unused regions are never allocated, and the cost is up to four memory accesses on a TLB miss.
:::

## Further learning

- **Next:** *Segmentation & Fragmentation* compares paging with variable-sized segments and allocation strategies.
- **Related:** *Demand Paging & Page Fault Handling* uses the valid bit to load pages only when they are needed.
- **Related:** *Address Binding & Dynamic Relocation* describes the simpler MMU that paging replaces.
