---
lesson: file-system-structure-inodes
title: File System Structure and Inodes
summary: How a file system is layered and laid out on disk, what an inode stores, how direct and indirect block pointers determine maximum file size, and how directories, hard links, and open-file tables connect names to data.
minutes: 40
type: theory
objectives:
  - Describe the layers of a file system and the main on-disk structures, including the superblock and inode table
  - List the metadata an inode stores and explain why the file name is not part of it
  - Compute the maximum file size and the number of disk reads needed to reach a byte, given an inode's direct and indirect pointers
  - Explain hard links, symbolic links, link counts, and the per-process and system-wide open-file tables
---

## Introduction

To a user, a file is a named document: `report.pdf`, `photo.jpg`. To a disk, there are only numbered blocks of bytes. A **file system** bridges the two. It must record which blocks belong to which file and in what order, how large each file is, who may read or change it, and when it was last modified, and it must find all of this quickly, for files of a few bytes and for files of many gigabytes.

UNIX-family file systems, including Linux's ext4, organise this information around a structure called the **inode** (index node), one per file. An inode holds everything about a file except its name: names live in **directories**, which map names to inode numbers. This separation is what makes hard links, cheap renames, and deleting an open file possible. This lesson explains the layout of a file system, the inode and its block pointers, and the tables the kernel keeps for open files.

**Before you start:** you should know what system calls are and the difference between memory and disk.

## Core theory

### Layers of a file system

| Layer | Responsibility |
| :--- | :--- |
| Logical file system | directories, file names, metadata, permissions; implements `open`, `read`, `write` |
| File-organization module | maps a file's logical blocks to physical blocks; manages free space |
| Basic file system | issues generic block reads and writes; manages the block cache |
| I/O control (device drivers) | translates block requests into device-specific commands |
| Devices | disks and SSDs |

Layering lets one block layer and driver serve many file systems (ext4, XFS, FAT, NTFS), and a **virtual file system (VFS)** layer above them gives applications one interface for all of them.

### On-disk layout

A typical UNIX-style volume contains:

- a **boot block**, with code to start the operating system, if the volume is bootable;
- a **superblock** (volume control block): the file system's size, block size, number of inodes, free counts, and other parameters;
- **free-space structures**, such as bitmaps of free blocks and free inodes;
- the **inode table**: a fixed array of inodes, each identified by its **inode number**;
- **data blocks**, holding file contents and directory contents.

### What an inode contains

- file type (regular file, directory, symbolic link, device, and so on) and **permission bits**;
- owner (user ID) and group;
- size in bytes;
- timestamps: last access, last modification of contents, last change of metadata;
- **link count**: how many directory entries refer to this inode;
- **block pointers** locating the file's data.

The inode does **not** contain the file's name. A **directory** is a special file whose contents are a list of entries, each pairing a name with an inode number. Opening `/home/ana/notes.txt` means reading the root directory to find `home`'s inode, reading that directory to find `ana`, and so on, one component at a time.

### Direct and indirect pointers

The classic UNIX inode, used by ext2 and ext3, has 15 block pointers:

- **12 direct pointers**, each giving the address of a data block;
- **1 single indirect pointer**, to a block filled with pointers to data blocks;
- **1 double indirect pointer**, to a block of pointers to single-indirect blocks;
- **1 triple indirect pointer**, one more level.

With block size $B$ and pointer size $q$, a block holds $k = B / q$ pointers, and the maximum file size is

$$(12 + k + k^2 + k^3) \times B.$$

Small files, which are the majority, are reached through the direct pointers with no extra disk reads, while huge files are still possible. Reaching a byte through the double indirect pointer needs two extra reads of pointer blocks (unless they are cached). Modern file systems such as ext4 replace most of this scheme with **extents**, records saying "the next $n$ blocks start at block $b$", which describe large contiguous files compactly.

### Hard links and symbolic links

- A **hard link** is simply another directory entry pointing to the **same inode**. Both names are equally real; the file's data is freed only when the link count drops to zero **and** no process has it open. Hard links cannot cross file systems (inode numbers are only unique within one) and normally cannot point to directories.
- A **symbolic (soft) link** is a small file whose contents are a **path**. Opening it makes the kernel follow the path. It can cross file systems and point to directories, but it **dangles** if the target is deleted or moved.

### Open-file tables

When a process calls `open`, the kernel:

1. resolves the path to an inode and checks permissions;
2. creates an entry in the **system-wide open-file table**, holding the current **file offset**, the access mode, and a pointer to the in-memory copy of the inode;
3. puts a pointer to that entry in the process's **per-process file-descriptor table** and returns its index, the **file descriptor**.

Two separate `open` calls on the same file create two entries with **independent offsets**. `dup` and `fork` create descriptors that **share** one entry, and so share the offset; this is how a shell's redirections work. Because the inode stays in use while it is open, a file deleted while open keeps its data until the last descriptor is closed.

## Worked examples

### Example 1: Maximum file size and where a byte lives

```python
def max_file_size(block_size, pointer_size, direct=12):
    k = block_size // pointer_size                 # pointers per indirect block
    return (direct + k + k**2 + k**3) * block_size

def locate(offset, block_size, pointer_size, direct=12):
    """Which pointer reaches this byte, and how many pointer blocks must be read first?"""
    k = block_size // pointer_size
    block = offset // block_size                   # logical block number within the file
    index = block
    for name, count, extra_reads in (("direct", direct, 0), ("single indirect", k, 1),
                                     ("double indirect", k**2, 2), ("triple indirect", k**3, 3)):
        if index < count:
            return f"file block {block}: {name} (entry {index}), {extra_reads} pointer-block reads"
        index -= count                             # skip the blocks this pointer covers
    return "beyond the maximum file size"

size = max_file_size(4096, 4)
print(f"4 KiB blocks: {size:,} bytes = {size / 2**40:.2f} TiB")
size = max_file_size(1024, 4)
print(f"1 KiB blocks: {size:,} bytes = {size / 2**30:.2f} GiB")
for offset in (10_000, 100_000, 10_000_000, 10_000_000_000):
    print(f"byte {offset:,}:", locate(offset, 4096, 4))
```

Output:

```text
4 KiB blocks: 4,402,345,721,856 bytes = 4.00 TiB
1 KiB blocks: 17,247,252,480 bytes = 16.06 GiB
byte 10,000: file block 2: direct (entry 2), 0 pointer-block reads
byte 100,000: file block 24: single indirect (entry 12), 1 pointer-block reads
byte 10,000,000: file block 2441: double indirect (entry 1405), 2 pointer-block reads
byte 10,000,000,000: file block 2441406: triple indirect (entry 1391794), 3 pointer-block reads
```

With 4 KiB blocks and 4-byte pointers, each indirect block holds 1024 pointers, and the triple indirect pointer alone covers $1024^3$ blocks, so the maximum is about 4 TiB. With 1 KiB blocks, $k$ is only 256 and the limit drops to about 16 GiB. Byte 100,000 lies in the file's block 24; the first 12 blocks use the direct pointers, so block 24 is entry 12 of the single indirect block. Byte 10,000,000 lies beyond the $12 + 1024 = 1036$ blocks covered by the direct and single indirect pointers, so two pointer blocks must be read before the data block, and a 10 GB offset needs three.

### Example 2: Names, links, and offsets in a real file system

```python
import os

with open("notes.txt", "w") as f:
    f.write("abcdef")

os.link("notes.txt", "copy-name.txt")              # a second directory entry for the same inode
same = os.stat("notes.txt").st_ino == os.stat("copy-name.txt").st_ino
print("links:", os.stat("notes.txt").st_nlink, "same inode:", same)
os.remove("notes.txt")                             # removes one name, not the file
with open("copy-name.txt") as f:
    print("after removing the first name:", f.read(), "| links:", os.stat("copy-name.txt").st_nlink)

flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
fd1 = os.open("copy-name.txt", flags)              # two opens: two independent offsets
fd2 = os.open("copy-name.txt", flags)
fd3 = os.dup(fd1)                                  # dup: shares fd1's offset
print(os.read(fd1, 2), os.read(fd2, 3), os.read(fd3, 2), os.read(fd1, 2))
for fd in (fd1, fd2, fd3):
    os.close(fd)
os.remove("copy-name.txt")
```

Output:

```text
links: 2 same inode: True
after removing the first name: abcdef | links: 1
b'ab' b'abc' b'cd' b'ef'
```

After `os.link`, both names lead to the same inode, whose link count is 2. Removing `notes.txt` only deletes a directory entry and decrements the count; the data survives under the other name. `fd1` and `fd2` come from separate `open` calls, so each has its own offset: both start at the beginning. `fd3` is a duplicate of `fd1` and shares its open-file-table entry, so after `fd1` reads `ab`, `fd3` continues with `cd`, and then `fd1` continues with `ef`.

### Example 3: Resolving a path

Opening `/home/ana/notes.txt` with nothing cached requires:

| Step | Read | Learn |
| :--- | :--- | :--- |
| 1 | inode 2 (the root directory, by convention) | where the root directory's data blocks are |
| 2 | root directory's data | `home` is inode 131 |
| 3 | inode 131 | where `home`'s data is; check search permission |
| 4 | `home` directory's data | `ana` is inode 4410 |
| 5 | inode 4410 | where `ana`'s data is |
| 6 | `ana` directory's data | `notes.txt` is inode 9872 |
| 7 | inode 9872 | permissions, size, block pointers |

(The inode numbers other than the root's are illustrative.) Seven disk reads before any file data is read is why the kernel caches directory entries and inodes aggressively; in practice most path lookups are answered from the **dentry cache** in memory.

## Applications

- **Linux and other UNIX-like systems** use inode-based file systems (ext4, XFS, Btrfs, APFS on macOS); `ls -i` shows inode numbers and `stat` shows an inode's metadata.
- **Backup and deduplication tools** use hard links to store unchanged files once across many snapshots.
- **Package managers and configuration** use symbolic links to point stable names at versioned files, such as a `python3` link to a specific interpreter.
- **Log rotation** relies on open-file semantics: a program keeps writing to a log file that has been renamed or deleted until it reopens the file.
- **Running out of inodes:** a disk can report "no space left" while bytes are free if it has used every inode, for example by storing millions of tiny files.

## Common mistakes

- **Thinking the file name is stored in the inode.** Names live in directory entries; one inode can have many names.
- **Believing that deleting a file name always frees its data.** Data is freed only when the link count is zero and no process holds the file open.
- **Confusing hard and symbolic links.** A hard link is another name for the same inode; a symbolic link is a separate file containing a path, which can dangle.
- **Forgetting the direct blocks when locating a byte,** or miscounting the pointers per block ($B / q$).
- **Assuming two descriptors for the same file share an offset.** Only descriptors created by `dup` or inherited across `fork` share one.

## Revision notes

- Layers: logical file system, file-organization module, basic file system, I/O control, devices; VFS unifies file systems.
- On disk: boot block, superblock, free-space bitmaps, inode table, data blocks.
- Inode: type, permissions, owner, size, timestamps, link count, block pointers; no name.
- Classic pointers: 12 direct, single, double, triple indirect; maximum size $(12 + k + k^2 + k^3)B$ with $k = B/q$.
- Hard link: another entry for the same inode; symbolic link: a file containing a path.
- Per-process descriptor table → system-wide open-file table (offset, mode) → in-memory inode.

## Practice questions

:::question basic
Name five pieces of information stored in an inode, and one that is not.
:::answer
Stored: file type and permission bits, owner and group, size, timestamps (access, modification, change), link count, and pointers to the data blocks. Not stored: the file's name, which belongs to the directory entries that point to the inode.
:::

:::question basic
A file has a link count of 3. What does that mean, and what happens to the file when one of its names is deleted?
:::answer
Three directory entries, possibly in different directories, refer to the same inode. Deleting one name removes that directory entry and decreases the link count to 2; the file's data and the other two names are unaffected. The data is freed only when the count reaches zero and no process has the file open.
:::

:::question intermediate
An inode has 10 direct pointers, one single indirect, and one double indirect pointer. Blocks are 2 KiB and pointers are 4 bytes. What is the maximum file size?
:::answer
Each block holds $2048 / 4 = 512$ pointers. The file can have $10 + 512 + 512^2 = 10 + 512 + 262{,}144 = 262{,}666$ blocks, so the maximum size is $262{,}666 \times 2048 = 537{,}939{,}968$ bytes, about 513 MiB.
:::

:::question intermediate
With 4 KiB blocks, 4-byte pointers, and 12 direct pointers, how many disk reads are needed to read the byte at offset 8,000,000, assuming the inode is already in memory and nothing else is cached?
:::answer
The byte is in logical block $\lfloor 8{,}000{,}000 / 4096 \rfloor = 1953$. The first 12 blocks are direct, and the single indirect pointer covers the next 1024 (blocks 12 to 1035), so block 1953 is in the double indirect range. Reaching it takes one read of the double indirect block, one read of a single indirect block, and one read of the data block: 3 disk reads.
:::

:::question intermediate
Explain the difference in behaviour between a hard link and a symbolic link when the original file is deleted.
:::answer
With a hard link, the "original" name and the link are equal directory entries for one inode; deleting either name leaves the inode with a nonzero link count, so the file remains fully accessible through the other name. A symbolic link contains only the path of the target; when the target is deleted, the path leads nowhere, and opening the symbolic link fails, a dangling link.
:::

:::question advanced
A process opens a large log file, and then an administrator deletes the file with `rm`, but the disk space is not freed. Explain why, and how the space can be recovered.
:::answer
`rm` removes the directory entry and decrements the link count to zero, but the process still holds an open file descriptor that refers, through the open-file table, to the in-memory inode. The kernel does not free the inode and data blocks while any open reference remains, and the process can keep writing to the file. The space is recovered when the process closes the descriptor or exits; restarting the process, or making it reopen its log (many daemons do this on a signal), releases it. Tools such as `lsof` list deleted files that are still open.
:::

## Further learning

- **Next:** *File Allocation & Directory Structures* compares contiguous, linked, and indexed allocation and directory organisations.
- **Related:** *Access Control & OS Security Fundamentals* explains the permission bits stored in the inode.
- **Related:** *Disk Scheduling Algorithms* shows why the number of disk reads per lookup matters.
