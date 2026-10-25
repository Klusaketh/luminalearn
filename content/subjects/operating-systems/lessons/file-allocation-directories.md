---
lesson: file-allocation-directories
title: File Allocation and Directory Structures
summary: How file systems place file data on disk with contiguous, linked (FAT), and indexed allocation, track free space with bitmaps and lists, and organise names in single-level, two-level, tree, and graph directories.
minutes: 45
type: theory
objectives:
  - Compare contiguous, linked, and indexed allocation by sequential access, random access, fragmentation, and overhead
  - Trace a file through a file allocation table and compute the cost of reaching a given block
  - Describe bitmap, linked-list, grouping, and counting methods of free-space management and size a bitmap
  - Compare single-level, two-level, tree-structured, acyclic-graph, and general-graph directories, and linear-list and hash-table implementations
---

## Introduction

A disk offers millions of numbered blocks. A file system must decide which blocks each file occupies, remember that decision, find any byte of any file quickly, and keep track of which blocks are still free, while files are constantly created, extended, shrunk, and deleted. The **allocation method** chosen for this has large effects on performance: how fast a video can be streamed, how quickly a database can jump to the middle of a file, and how much space is lost to bookkeeping and fragmentation.

There are three classic methods, **contiguous**, **linked**, and **indexed** allocation, and each still appears in real systems: contiguous extents in modern Linux and Windows file systems, linked allocation in the FAT file system used on USB drives and memory cards, and indexed allocation in the inodes of UNIX. This lesson compares them, explains how free space is tracked, and looks at how directories organise file names.

**Before you start:** you should know inodes, blocks, and the idea of external fragmentation.

## Core theory

### Contiguous allocation

Each file occupies a run of consecutive blocks; the directory records the **start block** and **length**.

- **Sequential access** is excellent: the disk reads one run with minimal head movement.
- **Random access** is trivial: block $i$ of a file starting at $s$ is block $s + i$.
- **External fragmentation**: as files are deleted, free space breaks into holes, and a new file may not fit in any one hole. Allocation uses first fit or best fit, and occasional **defragmentation** (compaction) is needed.
- **Growth** is hard: a file cannot grow if the next block is in use, so its final size must be guessed in advance.

Modern file systems use a variant, **extents**: a file is a list of contiguous runs, each recorded as (start, length), combining most of the speed of contiguity with the ability to grow.

### Linked allocation and the FAT

Each file is a linked list of blocks, scattered anywhere; each block holds a pointer to the next, and the directory records the first (and often the last) block.

- **No external fragmentation**: any free block can be used, and files can grow freely.
- **Sequential access** works, but **random access** is slow: reaching block $i$ means following $i$ pointers, each potentially a disk read.
- **Overhead and fragility**: pointers use space in every block, and one damaged pointer loses the rest of the file.

The **file allocation table (FAT)** keeps all the pointers together in a table at the start of the volume, with one entry per disk block holding the number of the next block in the file, an end-of-file marker, or a free marker. Because the table can be cached in memory, following a chain no longer costs a disk read per block, which makes random access acceptable. FAT (in its FAT12, FAT16, FAT32, and exFAT forms) was the file system of MS-DOS and early Windows and remains the standard for removable media because almost every device can read it.

### Indexed allocation

Each file has an **index block** listing the addresses of all its data blocks; entry $i$ is block $i$ of the file.

- **Random access is direct**: one index lookup gives any block.
- **No external fragmentation**, and files can grow until the index block is full.
- **Overhead**: even a tiny file needs a whole index block.

Large files need more than one index block: **linked** index blocks, a **multilevel** index, or the **combined** scheme of the UNIX inode (direct pointers for small files, plus single, double, and triple indirect blocks).

| | Contiguous | Linked (FAT) | Indexed |
| :--- | :--- | :--- | :--- |
| Sequential access | fastest | good | good |
| Random access | $O(1)$ arithmetic | follow $i$ links (fast if the FAT is cached) | $O(1)$ index lookup (plus indirect levels) |
| External fragmentation | yes | no | no |
| Growing files | hard | easy | easy, up to the index size |
| Space overhead | none | one pointer per block | index blocks |

### Free-space management

- **Bitmap (bit vector):** one bit per block, set for free (or for used, by convention). Finding a free block or a run of free blocks is fast with word-sized bit operations. A 1 TiB disk with 4 KiB blocks has $2^{28}$ blocks, so its bitmap takes $2^{28}$ bits $= 32$ MiB.
- **Linked list:** free blocks are chained together; no extra space is needed, but finding many free blocks means following many links.
- **Grouping:** the first free block stores the addresses of $n$ free blocks, the last of which stores the next $n$, and so on.
- **Counting:** store (start, count) pairs for runs of free blocks, which is compact when free space comes in large runs; such pairs are often kept in a balanced tree.

SSDs add a twist: deleted blocks should be reported to the drive with a **TRIM** command so that it can erase them in the background.

### Directory structures

| Structure | Description | Weakness |
| :--- | :--- | :--- |
| Single-level | one directory for all files of all users | name clashes; impossible to organise |
| Two-level | one directory per user | no grouping within a user's files |
| Tree | directories inside directories; absolute and relative path names | a file has exactly one parent, so sharing needs copies |
| Acyclic graph | a tree plus links, so a file or directory can appear in several places | deletion and traversal must handle multiple paths |
| General graph | links may create cycles | traversals may loop; cycles can leave unreachable garbage, needing garbage collection |

UNIX file systems are trees with hard links to files (an acyclic graph) and symbolic links, and they forbid hard links to directories precisely to avoid the general-graph problems.

A directory itself can be implemented as a **linear list** of (name, inode) entries, simple but $O(n)$ to search, or as a **hash table** or **B-tree** keyed by name, which makes lookups fast even in directories with many thousands of files. ext4 uses hashed B-tree directory indexes, and NTFS uses B+ trees.

## Worked examples

### Example 1: Contiguous allocation and external fragmentation

A tiny 20-block disk receives five files, and then two are deleted.

```python
disk = ["."] * 20                                 # "." marks a free block

def allocate_contiguous(name, size):
    run = 0
    for i, cell in enumerate(disk):                # first fit
        run = run + 1 if cell == "." else 0
        if run == size:
            start = i - size + 1
            disk[start:i + 1] = [name] * size
            return start
    return None

def delete(name):
    for i, cell in enumerate(disk):
        if cell == name:
            disk[i] = "."

for name, size in [("A", 4), ("B", 3), ("C", 5), ("D", 2), ("E", 4)]:
    print(name, size, "-> start", allocate_contiguous(name, size), "".join(disk))
delete("B")
delete("D")
print("after deleting B and D:", "".join(disk), "free blocks:", disk.count("."))
print("F needs 5 -> start", allocate_contiguous("F", 5))
```

Output:

```text
A 4 -> start 0 AAAA................
B 3 -> start 4 AAAABBB.............
C 5 -> start 7 AAAABBBCCCCC........
D 2 -> start 12 AAAABBBCCCCCDD......
E 4 -> start 14 AAAABBBCCCCCDDEEEE..
after deleting B and D: AAAA...CCCCC..EEEE.. free blocks: 7
F needs 5 -> start None
```

Seven blocks are free, but they form holes of 3, 2, and 2 blocks, so the 5-block file F cannot be stored contiguously: external fragmentation. Defragmenting would move C and E down to make one 7-block hole; linked or indexed allocation would simply use any five free blocks.

### Example 2: Following a FAT chain

A file occupies blocks 9, 3, 12, and 6, in that order. Its directory entry records only the first block.

```python
EOF_MARK = -1
fat = [None] * 16                                  # None marks a free block

def store_linked(blocks):
    for here, nxt in zip(blocks, blocks[1:]):
        fat[here] = nxt
    fat[blocks[-1]] = EOF_MARK
    return blocks[0]                               # the directory stores the first block

def chain(start):
    blocks, b = [], start
    while b != EOF_MARK:
        blocks.append(b)
        b = fat[b]
    return blocks

start = store_linked([9, 3, 12, 6])
print("FAT:", fat)
print("chain from directory entry (start 9):", chain(start))
print("reaching logical block 3 follows", chain(start).index(6), "FAT entries")
free_blocks = [b for b, entry in enumerate(fat) if entry is None]
print("free blocks:", free_blocks[:5], "...", len(free_blocks), "in total")
```

Output:

```text
FAT: [None, None, None, 12, None, None, -1, None, None, 3, None, None, 6, None, None, None]
chain from directory entry (start 9): [9, 3, 12, 6]
reaching logical block 3 follows 3 FAT entries
free blocks: [0, 1, 2, 4, 5] ... 12 in total
```

Entry 9 of the FAT says the block after 9 is 3, entry 3 says 12, entry 12 says 6, and entry 6 marks the end of the file. Reaching the file's last block means following three entries; for block $i$ in general it is $i$ entries. If the FAT is cached in memory, that costs microseconds; if each step required reading a pointer from the data block itself, as in plain linked allocation, it would cost $i$ disk reads. The FAT also doubles as the free-space map: unused entries mark free blocks.

### Example 3: Choosing an allocation method

| Workload | Best fit | Reason |
| :--- | :--- | :--- |
| Read-only media such as a DVD | contiguous | file sizes are known when the disc is written, and nothing is ever deleted |
| A camera's memory card | linked (FAT/exFAT) | simple, robust, readable by almost every device |
| A database file with random reads | indexed (or extents) | any block can be found with one or two lookups |
| A general-purpose disk | extents with an index (ext4, NTFS, APFS) | fast sequential I/O for large files, flexibility for growth |

A bitmap for the general-purpose disk, at 4 KiB per block, costs one bit per 32,768 bits of data, about 0.003% of the disk.

## Applications

- **ext4, NTFS, XFS, and APFS** use extents, indexed through tree structures, for file data, and B-trees or hashed indexes for large directories.
- **FAT32 and exFAT** remain standard on SD cards, USB drives, and cameras, and the UEFI boot partition of PCs uses FAT.
- **Defragmentation tools** compact contiguous and extent-based layouts on hard disks; on SSDs, defragmentation is generally unnecessary because there is no seek penalty.
- **Databases** preallocate large files and manage their own space inside them with page-level indexes.
- **Path names** in every operating system reflect tree-structured directories; shortcuts, aliases, and symbolic links turn them into graphs.

## Common mistakes

- **Saying linked allocation suffers external fragmentation.** It does not: any free block can be used. It suffers slow random access instead.
- **Forgetting that FAT random access is fast only when the table is cached.** Without the cache, each link costs a disk read.
- **Assuming indexed allocation is free for small files.** Each file needs at least one index block (the UNIX inode's direct pointers reduce this cost).
- **Getting bitmap sizes wrong** by mixing bits and bytes: the number of bits equals the number of blocks, and the bytes are one eighth of that.
- **Allowing hard links to directories,** which can create cycles that confuse traversal and deletion.

## Revision notes

- Contiguous: start + length; fastest access; external fragmentation; hard to grow. Extents generalise it.
- Linked: chains of blocks; no external fragmentation; slow random access; the FAT keeps the chains in one cacheable table.
- Indexed: an index block maps logical to physical blocks; direct random access; index overhead; multilevel or combined schemes for large files.
- Free space: bitmap (one bit per block), linked list, grouping, counting (runs).
- Directories: single-level, two-level, tree, acyclic graph (links), general graph (cycles need garbage collection).
- Directory lookup: linear list ($O(n)$) versus hash table or B-tree (fast for large directories).

## Practice questions

:::question basic
Which allocation method gives the fastest sequential access, and why?
:::answer
Contiguous allocation. All of a file's blocks are next to each other on the disk, so reading the file sequentially needs little or no head movement between blocks, and the file system needs no pointer lookups to find the next block.
:::

:::question basic
How large is the free-space bitmap of a 2 TiB disk with 4 KiB blocks?
:::answer
The disk has $2^{41} / 2^{12} = 2^{29} = 536{,}870{,}912$ blocks, so the bitmap has that many bits, which is $2^{29} / 8 = 2^{26}$ bytes $= 64$ MiB.
:::

:::question intermediate
A file uses linked allocation with the pointer stored in each data block, and no FAT. How many disk reads are needed to read only block 100 of the file, and how does a cached FAT change this?
:::answer
Without a FAT, the file system must read block 0 to find block 1, block 1 to find block 2, and so on: 100 reads to learn where block 100 is, plus one read of block 100 itself, 101 reads in total. With the FAT cached in memory, the 100 pointer lookups are memory operations, and only one disk read, of block 100, is needed.
:::

:::question intermediate
Why does contiguous allocation make it hard for files to grow, and how do extents address this?
:::answer
A contiguous file must occupy consecutive blocks, so it can grow only if the blocks after its end happen to be free. If another file sits there, the whole file must be moved to a larger hole, or the creator must have reserved extra space in advance, which wastes space if unused. With extents, a file is a list of contiguous runs, so when the current run cannot be extended, the file system simply starts a new extent elsewhere, keeping most of the benefit of contiguity.
:::

:::question intermediate
What problem does a general-graph directory structure create when files are deleted, and how can it be solved?
:::answer
With cycles, a group of directories can reference one another while no longer being reachable from the root. Their reference counts never fall to zero, so counting references cannot detect that they are garbage, and the space they use would never be freed. Solutions are to prevent cycles (for example, forbidding hard links to directories) or to run a garbage collector that marks everything reachable from the root and frees the rest, which is expensive on a large disk.
:::

:::question advanced
A file system uses indexed allocation with 4 KiB blocks and 4-byte block addresses, and a single index block per file. What is the largest file it can store, and what two designs remove the limit?
:::answer
An index block holds $4096 / 4 = 1024$ addresses, so a file can have at most 1024 blocks, $1024 \times 4\text{ KiB} = 4$ MiB. Linked index blocks remove the limit by reserving the last entry of each index block as a pointer to the next index block, at the cost of slower random access for blocks far into the file. A multilevel index, or the combined UNIX inode scheme, uses index blocks that point to further index blocks, so two levels allow $1024^2$ blocks (4 GiB) and three allow $1024^3$ (4 TiB), with a bounded number of lookups per access.
:::

## Further learning

- **Next:** *Direct Memory Access (DMA) & Interrupts* explains how blocks actually move between the disk and memory.
- **Related:** *File System Structure & Inodes* details the combined index scheme of UNIX inodes.
- **Related:** *Segmentation & Fragmentation* discusses the same fit strategies and fragmentation in memory.
