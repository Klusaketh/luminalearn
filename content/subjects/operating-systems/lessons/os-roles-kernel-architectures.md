---
lesson: os-roles-kernel-architectures
title: Operating System Roles and Kernel Architectures
summary: What an operating system does for programs and users, and how monolithic, layered, microkernel, modular, and hybrid kernels organise that work.
minutes: 30
type: theory
objectives:
  - Describe the three main roles of an operating system - abstraction, resource management, and protection
  - Distinguish the kernel from other system software and explain why it runs in privileged mode
  - Compare monolithic, layered, microkernel, modular, and hybrid kernel designs by performance, reliability, and extensibility
  - Identify the architecture of widely used systems such as Linux, Windows, and macOS
---

## Introduction

When you save a document, your editor does not know which disk sectors to write, how to talk to the disk controller, or how to avoid overwriting another program's files. It simply asks for a file to be written. The **operating system (OS)** does the rest. Between every application and the hardware sits this layer of software that makes the machine usable, shareable, and safe.

At the heart of the OS is the **kernel**, the part that runs with full control of the hardware. How much functionality to put inside the kernel is one of the oldest debates in systems design. Putting everything inside makes the system fast but means a single bug can crash the whole machine. Putting as little as possible inside makes the system more robust but adds overhead every time components talk to each other. This lesson explains what an operating system is for, and how the main kernel architectures balance these forces.

**Before you start:** you should be comfortable with the idea that a CPU executes instructions from memory, and with basic programming.

## Core theory

### Three roles of an operating system

1. **Abstraction (an extended machine).** Hardware is complicated and varied. The OS hides it behind clean, uniform abstractions: **processes** instead of a raw CPU, **address spaces** instead of physical memory chips, **files** instead of disk blocks, **sockets** instead of network interface registers. A program written against these abstractions runs on many different machines.
2. **Resource management (a referee).** Many programs compete for one CPU, a limited amount of memory, and shared devices. The OS allocates these resources, multiplexing them in **time** (taking turns on the CPU) and in **space** (giving each process part of memory), aiming for efficiency and fairness.
3. **Protection and isolation (a guard).** Programs and users must not read or corrupt each other's data, or take over the machine. The OS enforces boundaries between processes and controls access to files and devices.

### The kernel and the rest of the system

The **kernel** is the part of the OS that runs in **kernel mode** (privileged mode), where the CPU allows every instruction, including those that configure memory protection, disable interrupts, or access devices. Everything else runs in **user mode**, where those instructions are forbidden. System libraries (such as the C library), shells, compilers, and graphical desktops are part of the wider system but run in user mode and use the kernel's services through **system calls**.

### Monolithic kernels

A **monolithic kernel** runs all core services in one large program in kernel mode: process management, scheduling, memory management, file systems, network protocols, and device drivers. Components call each other directly, as ordinary functions in a shared address space.

- **Advantages:** fast, because a request such as reading a file is handled by direct function calls with no extra mode switches or message copying.
- **Disadvantages:** a bug in any component, often a third-party device driver, can corrupt kernel memory and crash the entire system; the code base is large and tightly coupled.
- **Examples:** traditional UNIX and Linux.

### Layered kernels

A **layered** design splits the OS into levels, each using only the services of the levels below it: hardware at the bottom, then memory management, then process management, and so on, up to the user interface. Dijkstra's THE system (1968) was an early example. Layering makes each level easier to verify, but strict layers are hard to define (for example, the memory manager may need to schedule processes, while the scheduler needs memory) and each layer crossing adds overhead, so pure layering is rare in practice.

### Microkernels

A **microkernel** keeps only the minimum in kernel mode: typically address-space management, thread scheduling, and **inter-process communication (IPC)**. File systems, device drivers, and network stacks run as separate **user-mode server processes** that communicate by passing messages through the kernel.

- **Advantages:** a crashing driver is just a failed user process that can be restarted; the small kernel is easier to verify and secure; services can be replaced without rebooting.
- **Disadvantages:** every service request becomes several messages and mode switches, which costs performance unless IPC is carefully optimised.
- **Examples:** MINIX 3, QNX (widely used in embedded and automotive systems), and seL4, a microkernel whose implementation has a machine-checked formal proof of correctness.

### Modular kernels

Most modern monolithic kernels are **modular**: they can load and unload code such as drivers and file systems at run time. Linux **loadable kernel modules** are an example. Modules keep the speed of a monolithic kernel and add flexibility, but a loaded module runs in kernel mode with full privileges, so it does not add isolation.

### Hybrid kernels

A **hybrid kernel** combines ideas: a microkernel-inspired structure, with services running in kernel mode for speed.

- **Windows NT** (the basis of current Windows versions) has a layered, object-based design with a small kernel and an executive, but runs its executive services and most drivers in kernel mode.
- **macOS and iOS** use XNU, which combines the Mach microkernel with BSD UNIX components in a single kernel address space.

### Comparison

| Design | What runs in kernel mode | Performance | Fault isolation | Examples |
| :--- | :--- | :--- | :--- | :--- |
| Monolithic | everything | highest | weakest | Linux, traditional UNIX |
| Layered | everything, in strict levels | moderate | moderate | THE (historical) |
| Microkernel | IPC, scheduling, address spaces | lower unless IPC is fast | strongest | MINIX 3, QNX, seL4 |
| Modular | core + loadable modules | high | weak (modules are privileged) | Linux with modules |
| Hybrid | most services, structured internally | high | moderate | Windows NT, macOS (XNU) |

## Worked examples

### Example 1: Reading a file in a monolithic kernel

A program calls `read()` to get data from a file.

| Step | Where it runs | What happens |
| :--- | :--- | :--- |
| 1 | user mode | the C library places the system call number and arguments in registers and executes a trap instruction |
| 2 | kernel mode | the system call handler looks up the file in the process's open-file table |
| 3 | kernel mode | the file system finds the disk blocks; the block cache supplies them or asks the disk driver |
| 4 | kernel mode | data is copied into the program's buffer |
| 5 | user mode | the trap returns, and `read()` returns the number of bytes read |

There is one switch into the kernel and one switch back. Everything inside is ordinary function calls, which is why monolithic kernels are fast.

### Example 2: The same request in a microkernel

In a microkernel, the file system and the disk driver are separate user-mode servers.

| Step | Where it runs | What happens |
| :--- | :--- | :--- |
| 1 | user → kernel | the program sends an IPC message "read file F" to the file-system server |
| 2 | kernel → FS server | the kernel delivers the message and switches to the file-system server |
| 3 | FS server → kernel | the server works out which blocks are needed and sends a message to the disk driver server |
| 4 | kernel → driver | the kernel delivers it; the driver performs the I/O |
| 5 | driver → kernel → FS server | the driver replies with the data |
| 6 | FS server → kernel → program | the file-system server replies to the program |

The work is the same, but it is spread over several protected processes. If the disk driver crashes, the file-system server sees a failed request, and the driver can be restarted; in a monolithic kernel, the same bug could bring down the machine.

### Example 3: Counting the boundary crossings

This toy model counts how many times control crosses the user/kernel boundary in the two designs, assuming each message between two user-mode components passes through the kernel once in each direction.

```python
def crossings(path):
    """path lists the components a request visits in order, ending back at the application."""
    count = 0
    for here, there in zip(path, path[1:]):
        if here.mode != there.mode:
            count += 1                          # one switch between user and kernel mode
    return count

class Component:
    def __init__(self, name, mode):
        self.name, self.mode = name, mode

app = Component("application", "user")
kernel = Component("kernel", "kernel")
fs_server = Component("file-system server", "user")
driver_server = Component("disk driver server", "user")

monolithic = [app, kernel, app]             # the kernel does everything internally
microkernel = [app, kernel, fs_server, kernel, driver_server,
               kernel, fs_server, kernel, app]

print("monolithic: ", crossings(monolithic), "crossings")
print("microkernel:", crossings(microkernel), "crossings")
```

Output:

```text
monolithic:  2 crossings
microkernel: 8 crossings
```

Each crossing costs a mode switch, and in a microkernel each message may also mean a context switch between address spaces and copying data. Early microkernels suffered badly from this overhead; later designs, such as the L4 family, made IPC fast enough that the cost became small for many workloads.

## Applications

- **Desktop and server systems:** Linux (monolithic and modular) dominates servers, supercomputers, and Android phones; Windows and macOS use hybrid kernels.
- **Embedded and safety-critical systems:** QNX runs in car infotainment and industrial controllers, where restarting a failed driver without rebooting matters.
- **High-assurance security:** seL4's formal verification makes it suitable for systems that must resist attack, such as military and aerospace computers.
- **Virtualization:** hypervisors apply the same ideas one level down, multiplexing hardware between whole operating systems.
- **Choosing where code runs:** user-mode drivers (for example, many USB and printer drivers) trade some speed for stability even on monolithic and hybrid systems.

## Common mistakes

- **Equating the operating system with its user interface.** The desktop and shell are user programs; the kernel is the privileged core underneath.
- **Assuming a microkernel is always slow.** Performance depends on the IPC implementation; well-engineered microkernels are fast enough for real-time and embedded use.
- **Believing loadable modules make a monolithic kernel safe.** A module runs in kernel mode; a bad module can still crash the system.
- **Thinking "hybrid" means a microkernel.** Windows and macOS keep most services in kernel mode for speed.
- **Confusing system libraries with system calls.** `printf` is a library function in user mode; it eventually calls `write`, which is a system call.

## Revision notes

- OS roles: abstraction (processes, address spaces, files), resource management (CPU, memory, devices), protection.
- The kernel runs in kernel mode; applications and libraries run in user mode and request services with system calls.
- Monolithic: all services in the kernel; fastest; least isolated (Linux).
- Microkernel: only IPC, scheduling, and address spaces in the kernel; services as user processes; best isolation (MINIX 3, QNX, seL4).
- Modular: monolithic kernel plus loadable modules. Hybrid: structured like a microkernel, but services run in kernel mode (Windows NT, XNU).
- The trade-off: performance (fewer crossings) versus reliability and security (more isolation).

## Practice questions

:::question basic
Name the three main roles of an operating system and give one concrete example of each.
:::answer
Abstraction: a program reads a "file" without knowing the disk's sector layout. Resource management: the scheduler shares one CPU among many processes by giving each a time slice. Protection: the OS prevents one user's process from reading another user's memory or private files.
:::

:::question basic
Why does the kernel need to run in a privileged mode that ordinary programs cannot use?
:::answer
The kernel must execute instructions that control the whole machine, such as configuring memory protection, disabling interrupts, and programming devices. If any program could execute them, it could bypass protection, read other programs' memory, or crash the system. Restricting these instructions to kernel mode means programs can only reach them through system calls that the kernel checks.
:::

:::question intermediate
A faulty network-card driver dereferences an invalid pointer. Describe what is likely to happen in a monolithic kernel and in a microkernel.
:::answer
In a monolithic kernel, the driver runs in kernel mode in the kernel's address space, so the bad access can corrupt kernel data or cause a kernel panic that brings down the whole machine. In a microkernel, the driver is a user-mode process with its own address space; the bad access causes a fault in that process only. The kernel can terminate and restart the driver, and the rest of the system keeps running, perhaps with a brief loss of networking.
:::

:::question intermediate
Explain why a microkernel typically needs more mode switches than a monolithic kernel to serve the same request.
:::answer
In a monolithic kernel, one trap enters the kernel, and the file system, cache, and driver interact by direct function calls before one return to user mode. In a microkernel, these components are separate user-mode servers, so every interaction between them is a message that passes through the kernel: sending enters the kernel, and delivery switches to the receiving server. A request that touches two servers therefore crosses the boundary several times, as Example 3 counts.
:::

:::question intermediate
Linux supports loadable kernel modules. Does this make Linux a microkernel? Explain.
:::answer
No. Modules let Linux add and remove code such as drivers at run time without rebuilding or rebooting, which provides flexibility. But a module, once loaded, runs in kernel mode in the kernel's address space, exactly like built-in kernel code. There is no isolation between it and the rest of the kernel, and components still communicate by function calls rather than messages, so Linux remains a modular monolithic kernel.
:::

:::question advanced
A company is designing the software for a car's braking controller and its entertainment system on one processor. Which kernel architecture would you recommend, and why?
:::answer
A microkernel (or a separation kernel built on similar principles), such as QNX or seL4. The safety-critical braking function must not be affected by bugs in the much larger, frequently updated entertainment software. A microkernel keeps drivers and services in isolated user-mode processes, so a crash in the media player or its drivers cannot corrupt the braking task, and failed components can be restarted. Its small kernel is also easier to certify; seL4 even has a formal correctness proof. The cost in IPC overhead is acceptable for these workloads.
:::

## Further learning

- **Next:** *System Calls & Dual-Mode Execution* shows exactly how a program crosses from user mode into the kernel and back.
- **Related:** *Process Control Block & Lifecycle* covers the process abstraction that the kernel provides.
- **Related:** *Access Control & OS Security Fundamentals* expands on the protection role of the operating system.
