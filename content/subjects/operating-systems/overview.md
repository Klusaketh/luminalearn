An operating system is the software layer that turns raw hardware into something programs can use safely and conveniently. It decides which program runs on the processor and for how long, gives every process the illusion of its own private memory, keeps programs from interfering with one another, and hides the details of disks, network cards, and keyboards behind simple abstractions such as files and sockets.

This subject explains how that is done. It begins with the structure of a kernel and the system call boundary between user programs and the kernel. It then covers processes and threads, CPU scheduling, and the synchronization tools (locks, semaphores, and condition variables) that make concurrent programs correct, followed by deadlocks and how to prevent, avoid, or detect them. The second half turns to memory: address translation, paging, segmentation, virtual memory, and page replacement. It closes with file systems, input and output, disk scheduling, and the protection mechanisms that keep a multi-user system secure.

Every lesson pairs the concepts with worked numerical examples and small Python simulations, so you can trace exactly what a scheduler, a page replacement policy, or the banker's algorithm does on a concrete input.

## What you will learn
- Explain the roles of an operating system and compare monolithic, microkernel, and hybrid kernel designs
- Describe how system calls, traps, and interrupts move execution between user mode and kernel mode
- Trace the life cycle of processes and threads and calculate scheduling metrics for FCFS, SJF, SRTF, priority, and round-robin scheduling
- Identify race conditions and solve synchronization problems with mutexes, semaphores, and condition variables
- Characterize deadlocks and apply prevention, the banker's avoidance algorithm, and detection
- Translate logical addresses to physical addresses under paging and segmentation and compute effective access times
- Simulate page replacement policies and explain demand paging, page faults, and thrashing
- Describe file system structures, allocation methods, I/O techniques, disk scheduling, and access control

## Prerequisites
- Programming experience in a language such as Python or C
- Basic data structures: arrays, linked lists, queues, and trees
- An outline of computer organization helps: registers, memory, and how a CPU executes instructions

## Glossary
- **Kernel**: the core of the operating system, running in privileged mode and managing hardware resources
- **System call**: a controlled request from a user program to the kernel for a privileged service
- **Process**: a program in execution, with its own address space and resources
- **Thread**: a unit of execution within a process; threads of one process share its address space
- **Context switch**: saving the state of one process or thread and restoring another's so that it can run
- **Scheduler**: the kernel component that chooses which ready process or thread runs next
- **Race condition**: a bug in which the result depends on the unpredictable timing of concurrent operations
- **Critical section**: a part of a program that accesses shared data and must not be executed concurrently
- **Semaphore**: an integer synchronization variable with atomic wait and signal operations
- **Deadlock**: a state in which a set of processes each wait for a resource held by another member of the set
- **Virtual memory**: a technique that gives each process a large private address space backed partly by disk
- **Page**: a fixed-size block of virtual memory, mapped to a physical frame of the same size
- **Page fault**: the trap raised when a process accesses a page that is not currently in physical memory
- **TLB**: the translation lookaside buffer, a small hardware cache of recent page-table entries
- **Inode**: a file-system record holding a file's metadata and the locations of its data blocks
- **DMA**: direct memory access, in which a device controller transfers data to or from memory without the CPU copying each byte

## Further reading
- Abraham Silberschatz, Peter Baer Galvin, and Greg Gagne, *Operating System Concepts* (Wiley)
- Andrew S. Tanenbaum and Herbert Bos, *Modern Operating Systems* (Pearson)
- Remzi H. Arpaci-Dusseau and Andrea C. Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* (Arpaci-Dusseau Books)
- William Stallings, *Operating Systems: Internals and Design Principles* (Pearson)
