---
lesson: system-calls-dual-mode
title: System Calls and Dual-Mode Execution
summary: How the CPU's user and kernel modes protect the system, how traps and interrupts enter the kernel, and how a system call travels from a library function to a kernel handler and back.
minutes: 30
type: theory
objectives:
  - Explain dual-mode operation, the mode bit, and why privileged instructions must be restricted
  - Distinguish system calls, exceptions, and hardware interrupts as ways of entering the kernel
  - Trace a system call from the library wrapper through the trap, dispatch table, and return
  - Classify common system calls and explain why buffering reduces their cost
---

## Introduction

If every program could talk to the disk controller directly, a single buggy program could erase every file on the machine. If every program could change the memory-protection settings, any program could read your passwords from another program's memory. Operating systems prevent this with help from the hardware: the processor has (at least) two **modes of execution**, and the instructions that control the machine work only in the privileged one.

User programs therefore cannot do anything dangerous by themselves. When a program needs a privileged service, such as opening a file, allocating memory, creating a process, or sending a network packet, it asks the kernel through a **system call**, a carefully controlled doorway into kernel mode. This lesson explains how the doorway works, what it costs, and why programs try to pass through it as rarely as possible.

**Before you start:** you should know the roles of an operating system and the idea of a kernel.

## Core theory

### Dual-mode operation

The CPU keeps a **mode bit** (on x86 processors, the current privilege level, with ring 0 for the kernel and ring 3 for applications):

- **Kernel mode (supervisor mode):** every instruction is allowed.
- **User mode:** **privileged instructions** are forbidden. Examples include instructions that perform I/O directly, change the page tables or memory-protection registers, disable interrupts, halt the CPU, or modify the mode bit itself.

If a user-mode program attempts a privileged instruction, the CPU does not execute it. Instead it raises an **exception** and transfers control to the kernel, which typically terminates the program.

The mode changes in only two directions:

- **User → kernel** happens only through a **trap or interrupt**, which jumps to an address the kernel chose in advance (the interrupt vector or system call entry point). A program cannot jump into the middle of the kernel.
- **Kernel → user** happens when the kernel executes a special return instruction (such as `sysret` or `iret` on x86) after it has finished the requested work.

### Three ways into the kernel

| Event | Caused by | Synchronous? | Examples |
| :--- | :--- | :--- | :--- |
| System call (trap) | the program, deliberately | yes | `read`, `write`, `fork`, `open` |
| Exception (fault) | the program, by accident | yes | division by zero, invalid memory access, page fault |
| Hardware interrupt | a device or timer | no | key pressed, disk transfer finished, timer tick |

The **timer interrupt** is what lets the kernel regain control from a program that never makes a system call, for example one stuck in an infinite loop. The kernel programs the timer before running a process; when it fires, the scheduler can switch to another process. Without it, the OS could not enforce time sharing.

### Anatomy of a system call

On Linux running on x86-64, a call to `read(fd, buf, n)` proceeds as follows:

1. The program calls the C library function `read`, an ordinary user-mode function (the **wrapper**).
2. The wrapper places the **system call number** for `read` in register `rax` and the arguments in `rdi`, `rsi`, and `rdx`, then executes the `syscall` instruction.
3. The CPU switches to kernel mode and jumps to the kernel's system call entry point, saving the user program's instruction pointer.
4. The kernel saves the user registers, checks the system call number, and uses it as an index into the **system call table** to find the handler.
5. The handler validates the arguments. In particular, it checks that `buf` really points into the caller's own memory, because the kernel must never trust a pointer supplied by user code. Then it does the work.
6. The kernel places the return value in `rax` (a negative value signals an error, which the wrapper turns into `-1` and sets `errno`) and returns to user mode just after the `syscall` instruction.

Programmers usually use an **API** such as the POSIX C library or the Windows API rather than invoking system calls directly. The API is portable and convenient; one API function may make zero, one, or several system calls.

### Categories of system calls

| Category | POSIX examples | Windows examples |
| :--- | :--- | :--- |
| Process control | `fork`, `exec`, `exit`, `wait` | `CreateProcess`, `ExitProcess`, `WaitForSingleObject` |
| File management | `open`, `read`, `write`, `close` | `CreateFile`, `ReadFile`, `WriteFile`, `CloseHandle` |
| Device management | `ioctl`, `read`, `write` | `DeviceIoControl` |
| Information maintenance | `getpid`, `time`, `sleep` | `GetCurrentProcessId`, `Sleep` |
| Communication | `pipe`, `socket`, `mmap`, `shmget` | `CreatePipe`, `CreateFileMapping` |
| Protection | `chmod`, `chown`, `umask` | `SetFileSecurity` |

### The cost of crossing

A system call is much more expensive than a function call. The CPU must switch modes and stacks, the kernel must save and restore registers and validate arguments, and the switch disturbs caches and the translation lookaside buffer. On modern hardware a trivial system call typically costs from around a hundred nanoseconds to a microsecond or more, depending on the processor and on security mitigations, compared with a few nanoseconds for a function call.

For this reason, libraries **batch** work: the C library's `printf` and Python's file objects collect output in a **user-space buffer** and issue one `write` system call when the buffer fills, instead of one per character. Interfaces such as `readv`/`writev` (several buffers per call) and Linux's `io_uring` (queues of requests shared with the kernel) exist to reduce the number of crossings further.

## Worked examples

### Example 1: Following one call through the layers

A Python program executes `f.write("hello\n")` on a file opened in text mode.

| Layer | Mode | Action |
| :--- | :--- | :--- |
| Python text wrapper | user | encodes the string to bytes |
| Python buffered writer | user | copies the 6 bytes into a buffer; no system call yet |
| buffer fills or the file is flushed/closed | user | calls the operating system's write function |
| C library wrapper (on Linux) | user | puts the call number and arguments in registers; executes `syscall` |
| kernel | kernel | validates the descriptor and buffer, copies the data into the page cache, returns the byte count |
| back in Python | user | the buffer is cleared |

Most `write` calls in a Python program never reach the kernel individually. The data usually is not on the disk yet either: the kernel's page cache holds it until it decides to write it back, or until the program calls `os.fsync`.

### Example 2: Measuring the effect of buffering

The class below stands in for a raw file descriptor and counts how often it is asked to write, which is how often a real program would make a `write` system call.

```python
import io

class CountingRaw(io.RawIOBase):
    """Stands in for a file descriptor: every write() call here would be one system call."""
    def __init__(self):
        self.calls, self.data = 0, bytearray()

    def writable(self):
        return True

    def write(self, b):
        self.calls += 1
        self.data += b
        return len(b)

unbuffered = CountingRaw()
for _ in range(10_000):
    unbuffered.write(b"x")             # one "system call" per byte

raw = CountingRaw()
buffered = io.BufferedWriter(raw, buffer_size=4096)
for _ in range(10_000):
    buffered.write(b"x")               # collected in a 4096-byte user-space buffer
buffered.flush()

print("unbuffered:", len(unbuffered.data), "bytes in", unbuffered.calls, "calls")
print("buffered:  ", len(raw.data), "bytes in", raw.calls, "calls")
```

Output:

```text
unbuffered: 10000 bytes in 10000 calls
buffered:   10000 bytes in 3 calls
```

The same 10,000 bytes cost 10,000 crossings without buffering but only 3 with a 4096-byte buffer: two full buffers and one final flush of the remaining 1808 bytes. If each real crossing cost 0.5 microseconds, the unbuffered version would spend about 5 milliseconds just entering and leaving the kernel, while the buffered one would spend about 1.5 microseconds.

### Example 3: Telling the three entry mechanisms apart

Classify each event as a system call, an exception, or an interrupt:

| Event | Classification | Reason |
| :--- | :--- | :--- |
| A program calls `getpid()` | system call | deliberate request for a kernel service |
| A program divides an integer by zero | exception | caused by the current instruction, not requested |
| The network card receives a packet | interrupt | asynchronous, caused by a device |
| A program touches a page that is on disk | exception (page fault) | caused by the instruction; the kernel loads the page and resumes it |
| The timer fires while a program loops forever | interrupt | lets the scheduler regain control |
| A user program executes an instruction that disables interrupts | exception (protection fault) | privileged instruction in user mode |

Note that a page fault is an exception the kernel can repair: after loading the page, it re-executes the faulting instruction, and the program never knows anything happened.

## Applications

- **Isolation in every modern OS:** dual-mode operation is what keeps one process from crashing others or the kernel.
- **Debugging and tracing:** tools such as `strace` on Linux and Process Monitor on Windows list the system calls a program makes, which often reveals why it fails (for example, a missing file returned as an `ENOENT` error).
- **Sandboxing:** Linux's `seccomp` filters restrict which system calls a process may make, used by browsers and container runtimes to shrink the attack surface.
- **Performance engineering:** buffering, batching, and memory-mapped files reduce the number of system calls in I/O-heavy programs.
- **Virtualization:** hypervisors use an additional, more privileged CPU mode so that guest kernels can run in kernel mode without controlling the real hardware.

## Common mistakes

- **Thinking a library function and a system call are the same thing.** `printf` and Python's `print` are user-mode functions that may or may not make a `write` system call.
- **Believing a program can switch itself into kernel mode.** It can only trap to fixed entry points chosen by the kernel.
- **Forgetting the timer interrupt** when explaining how the OS regains control from a program that never makes system calls.
- **Trusting user pointers in kernel code.** A kernel handler must verify that every user-supplied address is valid and belongs to the caller before using it.
- **Assuming `write` means the data is on disk.** It usually reaches only the kernel's page cache; durability requires `fsync` or an equivalent.

## Revision notes

- The mode bit separates kernel mode (all instructions) from user mode (no privileged instructions).
- Privileged instructions include direct I/O, changing memory protection, disabling interrupts, and changing the mode.
- Entering the kernel: system calls (deliberate), exceptions (faults caused by an instruction), interrupts (asynchronous device or timer events).
- System call path: library wrapper → call number and arguments in registers → trap instruction → system call table → handler → return value → return to user mode.
- System calls cost far more than function calls; buffering and batching reduce how many are made.
- The timer interrupt guarantees the kernel can regain the CPU.

## Practice questions

:::question basic
Which of these should be privileged instructions: reading the time of day, setting the timer, disabling interrupts, adding two registers, changing the page-table base register?
:::answer
Setting the timer, disabling interrupts, and changing the page-table base register must be privileged, because each would let a program take control of the CPU or bypass memory protection. Adding two registers is harmless and is not privileged. Reading the time of day is normally safe to allow (many systems let user code read a clock directly), whereas setting the system clock is privileged.
:::

:::question basic
What is the difference between an exception and an interrupt?
:::answer
An exception is synchronous: it is caused by the instruction currently executing, such as a division by zero, an invalid memory access, or a page fault, and it happens at the same point every time the program runs with the same input. An interrupt is asynchronous: it comes from outside the running program, from a device or the timer, and can occur between any two instructions.
:::

:::question intermediate
Why must the kernel check a buffer pointer passed to `read`, even though the program passing it is the one that will be harmed if it is wrong?
:::answer
The kernel writes into the buffer while running in kernel mode, where it can access any memory. If a malicious program passed the address of kernel data or of another process's memory, an unchecked `read` would overwrite that memory with file data under the program's control, which is a classic way to take over a system. The kernel must confirm that the whole buffer lies in the caller's own writable address space, and it uses special copy routines that fail safely if the address is invalid.
:::

:::question intermediate
A program writes a 1 MB file one byte at a time using unbuffered `write` calls. Estimate the overhead if each system call costs 0.5 microseconds, and suggest a fix.
:::answer
One megabyte is 1,048,576 bytes, so there are about $1.05 \times 10^6$ system calls, costing about $1.05 \times 10^6 \times 0.5\,\mu\text{s} \approx 0.52$ seconds just in crossings. Buffering in user space, for example with a 64 KB buffer, needs only 16 calls, costing about 8 microseconds. In C, use `fwrite` or a buffered `FILE*` stream; in Python, use the default buffered file object.
:::

:::question intermediate
A program contains `while True: pass` and never makes a system call. How does the operating system still manage to run other programs?
:::answer
Before giving the CPU to a process, the kernel programs a hardware timer. When the timer expires, it raises an interrupt, which forces a switch into kernel mode regardless of what the program is doing. The kernel's interrupt handler then calls the scheduler, which can save the looping program's state and run another process. The program cannot block this, because disabling interrupts and reprogramming the timer are privileged instructions.
:::

:::question advanced
List the steps of a page fault and explain why, unlike most exceptions, it does not usually terminate the program.
:::answer
The program accesses an address whose page-table entry is marked not present. The CPU raises a page-fault exception, switches to kernel mode, and records the faulting address. The kernel checks whether the address is valid for the process. If it is, the page is simply not in memory yet: the kernel finds a free frame (evicting a page if necessary), reads the page from disk or zero-fills it, updates the page-table entry, and returns. The CPU then re-executes the faulting instruction, which now succeeds. The fault was part of normal demand paging, not an error, so the program continues. Only when the address is invalid (outside every mapped region, or violating permissions) does the kernel deliver a segmentation fault and usually terminate the program.
:::

## Further learning

- **Next:** *Process Control Block & Lifecycle* describes the process structures the kernel manages behind system calls such as `fork` and `exit`.
- **Related:** *Direct Memory Access (DMA) & Interrupts* covers device interrupts in more depth.
- **Related:** *Demand Paging & Page Fault Handling* explains the page-fault exception in detail.
