Computer organization and architecture explains how a processor actually runs a program. Architecture is the programmer's view of the machine: its instructions, registers, and addressing modes. Organization is how that view is implemented in hardware: the datapath, the control unit, pipelines, caches, and buses. Together they explain why some programs run many times faster than others on the same machine.

This subject starts with the von Neumann model and the performance metrics used to compare machines, including CPI, clock rate, and Amdahl's law. It covers computer arithmetic, from integer addition and multiplication to IEEE 754 floating point. It then examines instruction set design: RISC and CISC, instruction formats, addressing modes, the instruction cycle, and assembly language. The datapath and control modules show how instructions flow through registers and functional units under hardwired or microprogrammed control. The second half covers pipelining and its hazards, the memory hierarchy with cache mapping and average memory access time, virtual memory and TLBs, input and output with polling, interrupts, and DMA, and instruction-level and multicore parallelism.

Lessons are built on worked numerical problems: speedups, cache hit rates, address breakdowns, and pipeline timing diagrams.

## What you will learn
- Describe the von Neumann architecture and compare machines using CPI, execution time, and Amdahl's law
- Perform integer arithmetic in hardware and represent real numbers in IEEE 754 format
- Compare RISC and CISC designs, instruction formats, and addressing modes
- Trace the instruction cycle and read simple assembly language
- Explain how a datapath executes instructions and compare hardwired and microprogrammed control
- Calculate pipeline speedup and resolve data, control, and structural hazards with forwarding and stalls
- Map addresses into direct-mapped and set-associative caches and calculate average memory access time
- Explain virtual memory and the role of the TLB
- Compare polling, interrupts, and DMA, and describe instruction-level and multicore parallelism

## Prerequisites
- Digital logic: gates, multiplexers, registers, and binary arithmetic (see the Digital Logic subject)
- Programming experience, ideally in C
- Comfort with binary and hexadecimal numbers

## Glossary
- **Instruction set architecture (ISA)**: the interface between software and hardware, defining instructions, registers, and addressing
- **RISC**: reduced instruction set computer; simple, fixed-length instructions designed for pipelining
- **CISC**: complex instruction set computer; richer, variable-length instructions
- **Datapath**: the registers, ALU, and connections through which data moves during execution
- **Control unit**: the logic that generates the signals directing the datapath
- **CPI**: cycles per instruction, an average measure of processor efficiency
- **Pipelining**: overlapping the stages of several instructions to raise throughput
- **Hazard**: a situation that prevents the next instruction in a pipeline from executing on time
- **Forwarding**: passing a result directly between pipeline stages before it is written back
- **Cache**: a small, fast memory holding copies of recently used data
- **Hit rate**: the fraction of memory accesses satisfied by the cache
- **TLB**: translation lookaside buffer; a cache of recent virtual-to-physical address translations
- **DMA**: direct memory access; a device transfers data to memory without the CPU copying each word

## Further reading
- David A. Patterson and John L. Hennessy, *Computer Organization and Design* (Morgan Kaufmann)
- John L. Hennessy and David A. Patterson, *Computer Architecture: A Quantitative Approach* (Morgan Kaufmann)
- William Stallings, *Computer Organization and Architecture* (Pearson)
- Randal E. Bryant and David R. O'Hallaron, *Computer Systems: A Programmer's Perspective* (Pearson)
