---
lesson: datapath-register-organization
title: Datapath & Register Organization
summary: Explore how the ALU, register file, internal buses, and multiplexers combine to form a single-cycle datapath that executes arithmetic, memory, and control-flow instructions.
minutes: 50
type: theory
objectives:
  - Identify the primary structural components of a processor datapath and their connections
  - Explain how multi-ported register files enable simultaneous operand reads and result writes
  - Trace data flow and control signals through a single-cycle datapath for R-type, memory, and branch instructions
  - Compute the critical path delay and maximum clock frequency of a single-cycle CPU
review: ai-draft
---

## Introduction

When a processor executes an assembly instruction such as `add t0, t1, t2`, the operation feels immediate to a software programmer. Underneath the abstraction of assembly language, however, binary signals must physically travel across millions of transistors. Electrical charge flows out of storage cells, passes through multiplexers, routes along copper traces into logic gates that compute sums, and finally settles back into a destination storage cell before the next clock tick.

The hardware responsible for this movement and manipulation of data is called the datapath. Designing an efficient datapath requires organizing internal storage (registers), functional compute blocks (the Arithmetic Logic Unit), interconnects (buses), and steering logic (multiplexers) into a cohesive structure.

In this lesson, you will learn how register files are organized to support multi-ported access, how internal buses connect compute elements, and how control signals direct data through a single-cycle datapath to execute instructions.

**Before you start:** You should be familiar with *RISC vs CISC & Instruction Formats*, standard *Addressing Modes*, basic binary arithmetic, and standard digital logic components such as multiplexers and D flip-flops.

## Core theory

### Structural elements of a datapath

A central processing unit (CPU) is divided into two primary functional sections: the control unit and the datapath. The **datapath** comprises the hardware components that store, route, and process data. It includes the register file, the Arithmetic Logic Unit (ALU), program counter, memory interfaces, multiplexers, and internal interconnect lines. The **control unit** acts as the director, taking the current instruction bit pattern as input and issuing electrical control signals that command the datapath on how to process that instruction.

```mermaid
flowchart LR
    PC[Program Counter] --> IMEM[Instruction Memory]
    IMEM --> RegFile[Register File]
    RegFile --> ALU[Arithmetic Logic Unit]
    ALU --> DMEM[Data Memory]
    DMEM --> RegFile
```

Every processing element within the datapath has a specific structural responsibility:

| Component | Primary Function | Input Signals | Output Signals |
| :--- | :--- | :--- | :--- |
| **Program Counter (PC)** | Holds the memory address of the current instruction | Next PC address, Clock | Current PC address |
| **Instruction Memory** | Stores executable program machine code | Read Address (from PC) | Instruction word (32-bit/64-bit) |
| **Register File** | High-speed internal storage array | Read Reg Numbers, Write Reg Number, Write Data, Write Enable | Read Data 1, Read Data 2 |
| **ALU** | Executes arithmetic and boolean logic operations | Operand A, Operand B, ALU Control code | Operation Result, Status Flags ($Z, N, C, V$) |
| **Data Memory** | Stores program heap, stack, and global data | Address, Write Data, MemRead, MemWrite | Read Data |
| **Multiplexers** | Selects one data path out of multiple inputs | Input channels, Selector control signal | Selected Data output |

### Register file organization and multi-porting

Registers provide the fastest storage mechanism within the CPU hierarchy. A collection of registers grouped together is known as a **register file**. To execute instructions in a single clock cycle, a processor must read two source operands and write one destination operand simultaneously.

A standard single-ported Static RAM (SRAM) cell allows only one read or write operation per clock cycle. To support execution requirements, a register file uses **multi-ported** architecture:

1. **Dual Read Ports:** Two independent read addresses are supplied concurrently ($RS1$ and $RS2$). Internal decoding logic routes the contents of the two requested registers to output ports `Read Data 1` and `Read Data 2` without waiting for a clock edge. Reads are purely combinational operations.
2. **Single Write Port:** A write address line ($RD$), a `Write Data` line, and a control signal named `RegWrite` (Write Enable) control register updates. Unlike reads, writes are sequential operations. The write occurs strictly on the active edge (rising edge) of the system clock when `RegWrite` is asserted.

```
       +-----------------------------------+
RS1 -->| Read Register 1                   |
RS2 -->| Read Register 2   Register File   |--> Read Data 1
RD  -->| Write Register    (e.g., 32x64)   |--> Read Data 2
WD  -->| Write Data                        |
WE  -->| Write Enable (RegWrite)           |
CLK -->| Clock Input                       |
       +-----------------------------------+
```

In RISC architectures such as RISC-V or MIPS, register `x0` (or `$zero`) is hardwired to logic ground ($0$). Any read from register `0` returns $0$, and any write to register `0` is ignored by hardware logic.

### Internal bus architectures and the ALU

Data moves between registers and processing units over copper signal traces called an **internal bus**. Microarchitectures select between single-bus, dual-bus, and triple-bus configurations based on performance and area constraints:

- **Single-Bus Architecture:** All register outputs and inputs share a single common parallel data line. Only one data transfer can take place at any given instant. A two-operand ALU operation requires multiple clock sub-cycles to sequentially buffer operands into temporary latches before executing.
- **Triple-Bus Architecture:** Three separate buses (Bus A, Bus B, and Bus C) exist in parallel. Bus A and Bus B simultaneously transport two source operands from the register file to the ALU inputs. Bus C routes the ALU result back to the register file destination port within the same clock period.

The **Arithmetic Logic Unit (ALU)** is a purely combinational circuit designed to process data supplied by internal buses. The ALU receives two $n$-bit binary inputs ($A$ and $B$) and an $m$-bit control selection code that selects the desired operation (e.g., `ADD`, `SUB`, `AND`, `OR`, `SLT`).

In addition to the main computation output, the ALU generates individual status flag bits stored in a status register:

- **Zero Flag ($Z$):** Set to $1$ if all bits of the output result are $0$; otherwise $0$.
- **Negative Flag ($N$):** Set to $1$ if the most significant bit (MSB) of the result is $1$ (indicating a negative value in 2's complement representation).
- **Carry Flag ($C$):** Set to $1$ if an unsigned arithmetic operation produced a carry-out from the MSB.
- **Overflow Flag ($V$):** Set to $1$ if a signed arithmetic operation resulted in a value outside the representable range of the $n$-bit word.

Signed overflow for addition is detected using the MSB of inputs $A_{n-1}$, $B_{n-1}$ and result $R_{n-1}$:

$$V = (A_{n-1} \cdot B_{n-1} \cdot \overline{R_{n-1}}) + (\overline{A_{n-1}} \cdot \overline{B_{n-1}} \cdot R_{n-1})$$

### Tracing a single-cycle datapath

In a **single-cycle datapath**, every instruction completes its entire execution sequence—fetch, decode, register read, execution, memory access, and register write-back—within exactly one clock period.

To route data correctly for different instruction types, multiplexers placed at critical junctions are driven by control signals:

```
Instruction Types and Data Flow:

1. R-Type (e.g., add rd, rs1, rs2):
   PC -> Fetch Instr -> Read RS1 & RS2 -> ALU Ops RS1, RS2 -> Write ALU Result to RD

2. Load (e.g., lw rd, offset(rs1)):
   PC -> Fetch Instr -> Read RS1 & Sign-Ext Offset -> ALU Computes Address (RS1 + Offset) -> Read Memory -> Write Mem Data to RD

3. Store (e.g., sw rs2, offset(rs1)):
   PC -> Fetch Instr -> Read RS1 & RS2 & Sign-Ext Offset -> ALU Computes Address (RS1 + Offset) -> Write RS2 Data to Memory

4. Branch (e.g., beq rs1, rs2, label):
   PC -> Fetch Instr -> Read RS1 & RS2 -> ALU Subtracts (RS1 - RS2) -> If Z=1, PC = PC + (Offset << 1)
```

The table below lists the active states of key control signals for each standard RISC instruction type:

| Instruction Type | `RegWrite` | `ALUSrc` | `ALUOp` | `MemRead` | `MemWrite` | `MemtoReg` | `PCSrc` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R-Type** (`add`, `sub`) | 1 | 0 (Reg) | Func-decided | 0 | 0 | 0 (ALU) | 0 (PC+4) |
| **Load** (`lw`) | 1 | 1 (Imm) | Add | 1 | 0 | 1 (Mem) | 0 (PC+4) |
| **Store** (`sw`) | 0 | 1 (Imm) | Add | 0 | 1 | X (Don't care) | 0 (PC+4) |
| **Branch** (`beq`) | 0 | 0 (Reg) | Subtract | 0 | 0 | X (Don't care) | $Z$ flag |

### Datapath delay and critical path analysis

The maximum operating frequency of a CPU depends on signal propagation delays through physical transistors and interconnect wires. The **critical path** is the longest sequence of dependent logic gates and components that a signal must traverse from the start of a clock cycle to the point where all signals stabilize.

Because every instruction in a single-cycle design must execute within a single clock period $T_{\text{clock}}$, the clock period must be set long enough to accommodate the worst-case path among all supported instructions.

Typically, the load instruction (`lw`) establishes the critical path because it involves reading instruction memory, reading the register file, computing an address in the ALU, reading data memory, and routing data back to be stored in the register file.

The formula for calculating the minimum allowable clock period $T_{\text{clock}}$ is:

$$T_{\text{clock}} \ge t_{\text{PC}} + t_{\text{IMEM}} + t_{\text{RegRead}} + t_{\text{ALU}} + t_{\text{DMEM}} + t_{\text{Mux}} + t_{\text{RegSetup}}$$

Where:
- $t_{\text{PC}}$ is the propagation delay of the Program Counter register.
- $t_{\text{IMEM}}$ is the access time of Instruction Memory.
- $t_{\text{RegRead}}$ is the time taken to output data from the Register File after address lines stabilize.
- $t_{\text{ALU}}$ is the operational delay of the ALU.
- $t_{\text{DMEM}}$ is the read access time of Data Memory.
- $t_{\text{Mux}}$ is the combined delay of steering multiplexers along the path.
- $t_{\text{RegSetup}}$ is the required setup time of the destination register before the clock edge.

The maximum attainable clock frequency $f_{\text{max}}$ is the reciprocal of the minimum clock period:

$$f_{\text{max}} = \frac{1}{T_{\text{clock}}}$$

## Worked examples

### Example 1: Calculating Maximum Clock Frequency

A digital designer is evaluating a 32-bit single-cycle processor datapath. Semiconductor timing analysis yields the following component delays:

- Program Counter propagation delay ($t_{\text{PC}}$): $30\text{ ps}$
- Instruction Memory access delay ($t_{\text{IMEM}}$): $220\text{ ps}$
- Register File read access time ($t_{\text{RegRead}}$): $120\text{ ps}$
- ALU operational delay ($t_{\text{ALU}}$): $180\text{ ps}$
- Data Memory read/write delay ($t_{\text{DMEM}}$): $240\text{ ps}$
- Single multiplexer delay ($t_{\text{Mux}}$): $20\text{ ps}$
- Register File setup time ($t_{\text{RegSetup}}$): $15\text{ ps}$
- Sign-extension logic delay ($t_{\text{Ext}}$): $10\text{ ps}$

Calculate the execution latency for R-type, Store, Branch, and Load instructions. Identify the critical path and compute the maximum achievable clock frequency $f_{\text{max}}$.

**Step 1: Calculate the total latency for each instruction path.**

- **R-Type Instruction (`add`):**
  $$\text{Path} = t_{\text{PC}} + t_{\text{IMEM}} + t_{\text{RegRead}} + t_{\text{ALU}} + t_{\text{Mux}} + t_{\text{RegSetup}}$$
  $$\text{Latency} = 30 + 220 + 120 + 180 + 20 + 15 = 585\text{ ps}$$

- **Store Instruction (`sw`):**
  $$\text{Path} = t_{\text{PC}} + t_{\text{IMEM}} + t_{\text{RegRead}} + t_{\text{Mux}} + t_{\text{ALU}} + t_{\text{DMEM}}$$
  *(Note: ALUSrc Mux selects between Register Read 2 and Sign-Extended Immediate)*
  $$\text{Latency} = 30 + 220 + 120 + 20 + 180 + 240 = 810\text{ ps}$$

- **Branch Instruction (`beq`):**
  $$\text{Path} = t_{\text{PC}} + t_{\text{IMEM}} + t_{\text{RegRead}} + t_{\text{ALU}} + t_{\text{Mux\_PCSrc}}$$
  $$\text{Latency} = 30 + 220 + 120 + 180 + 20 = 570\text{ ps}$$

- **Load Instruction (`lw`):**
  $$\text{Path} = t_{\text{PC}} + t_{\text{IMEM}} + t_{\text{RegRead}} + t_{\text{Mux\_ALUSrc}} + t_{\text{ALU}} + t_{\text{DMEM}} + t_{\text{Mux\_MemToReg}} + t_{\text{RegSetup}}$$
  $$\text{Latency} = 30 + 220 + 120 + 20 + 180 + 240 + 20 + 15 = 845\text{ ps}$$

**Step 2: Determine the critical path.**

Comparing the computed latencies:
- R-Type: $585\text{ ps}$
- Store: $810\text{ ps}$
- Branch: $570\text{ ps}$
- Load: $845\text{ ps}$

The Load instruction (`lw`) requires the longest propagation time ($845\text{ ps}$) and represents the critical path of the datapath.

**Step 3: Compute maximum clock frequency.**

Set $T_{\text{clock}} = 845\text{ ps} = 845 \times 10^{-12}\text{ s}$.

$$f_{\text{max}} = \frac{1}{T_{\text{clock}}} = \frac{1}{845 \times 10^{-12}\text{ s}} \approx 1,183,431,952\text{ Hz} \approx 1.183\text{ GHz}$$

The maximum clock frequency supported by this single-cycle processor is **$1.183\text{ GHz}$**.

---

### Example 2: Control Signal Tracing

Consider the single-cycle execution of the following two instructions:
1. `Instruction 1: add x5, x6, x7`
2. `Instruction 2: sw x8, 32(x9)`

Determine the logic signal values ($0$, $1$, or $X$ for don't care) for all six main control lines (`RegWrite`, `ALUSrc`, `MemRead`, `MemWrite`, `MemtoReg`, `PCSrc`) for both instructions.

**Step 1: Analyze `Instruction 1: add x5, x6, x7`**

- `RegWrite`: Must be **1** because the result calculated by the ALU must be written back to register `x5`.
- `ALUSrc`: Must be **0** because operand B of the ALU must come from read port 2 of the register file (register `x7`), not an immediate value.
- `MemRead`: Must be **0** because data memory is not accessed for reading.
- `MemWrite`: Must be **0** because no data is written to memory.
- `MemtoReg`: Must be **0** because the value written back to `x5` is the output of the ALU.
- `PCSrc`: Must be **0** because the next instruction address is standard sequential PC update ($\text{PC} + 4$).

**Step 2: Analyze `Instruction 2: sw x8, 32(x9)`**

- `RegWrite`: Must be **0** because a store instruction modifies memory, not register values.
- `ALUSrc`: Must be **1** because operand B of the ALU must be the sign-extended immediate displacement value ($32$).
- `MemRead`: Must be **0** because data memory is being written to, not read.
- `MemWrite`: Must be **1** because data from register `x8` is being written into memory.
- `MemtoReg`: Must be **X (Don't Care)** because `RegWrite` is disabled ($0$), so the output of the MemtoReg multiplexer is ignored.
- `PCSrc`: Must be **0** because execution continues sequentially to $\text{PC} + 4$.

**Final Control Signal Table:**

| Signal Name | Instruction 1 (`add`) | Instruction 2 (`sw`) |
| :--- | :--- | :--- |
| `RegWrite` | 1 | 0 |
| `ALUSrc` | 0 | 1 |
| `MemRead` | 0 | 0 |
| `MemWrite` | 0 | 1 |
| `MemtoReg` | 0 | X |
| `PCSrc` | 0 | 0 |

---

### Example 3: Simulating Register Read and Write Logic in C

The following C program simulates a 32-entry multi-ported register file to demonstrate combinational dual-port reading, edge-triggered writing with write-enable, and the hardwired zero register `x0`.

```c
#include <stdio.h>
#include <stdint.h>

typedef struct {
    uint32_t registers[32];
} RegisterFile;

// Initialize register file (x0 is hardwired to 0)
void rf_init(RegisterFile *rf) {
    for (int i = 0; i < 32; i++) {
        rf->registers[i] = 0;
    }
}

// Combinational Dual-Port Read Operation
void rf_read(const RegisterFile *rf, uint8_t rs1, uint8_t rs2, uint32_t *read_data1, uint32_t *read_data2) {
    *read_data1 = (rs1 == 0) ? 0 : rf->registers[rs1];
    *read_data2 = (rs2 == 0) ? 0 : rf->registers[rs2];
}

// Clock-Edge Triggered Write Operation
void rf_write_clock_edge(RegisterFile *rf, uint8_t rd, uint32_t write_data, uint8_t reg_write) {
    // Write occurs only if Write Enable is active and target is not x0
    if (reg_write && (rd != 0)) {
        rf->registers[rd] = write_data;
    }
}

int main(void) {
    RegisterFile rf;
    rf_init(&rf);

    uint32_t data1, data2;

    // Cycle 1: Write values into x5 and x6
    rf_write_clock_edge(&rf, 5, 0xABCDEF00, 1);
    rf_write_clock_edge(&rf, 6, 0x00001234, 1);

    // Attempt to write into hardwired register x0
    rf_write_clock_edge(&rf, 0, 0xFFFFFFFF, 1);

    // Attempt write with RegWrite disabled (0)
    rf_write_clock_edge(&rf, 7, 0x99999999, 0);

    // Perform dual-port read of x5 and x6
    rf_read(&rf, 5, 6, &data1, &data2);
    printf("Read Port 1 (x5): 0x%08X\n", data1);
    printf("Read Port 2 (x6): 0x%08X\n", data2);

    // Perform dual-port read of x0 and x7
    rf_read(&rf, 0, 7, &data1, &data2);
    printf("Read Port 1 (x0): 0x%08X\n", data1);
    printf("Read Port 2 (x7): 0x%08X\n", data2);

    return 0;
}
```

Output:

```text
Read Port 1 (x5): 0xABCDEF00
Read Port 2 (x6): 0x00001234
Read Port 1 (x0): 0x00000000
Read Port 2 (x7): 0x00000000
```

## Applications

- **Microcontroller Core Design:** Simple microcontrollers (such as ARM Cortex-M0+ or basic RISC-V cores in embedded systems) use single-cycle or basic multi-cycle datapaths to minimize silicon area and gate count.
- **FPGA Soft Processors:** Field-Programmable Gate Array (FPGA) soft core designs (like Xilinx MicroBlaze or Altera Nios II) allow developers to customize datapath bus widths and multi-ported register files based on target resource constraints.
- **Instruction Set Simulators:** Functional software emulators (such as QEMU or SPIM) model CPU datapaths in software by maintaining register state structs and routing simulated control logic.
- **Hardware Description Language (HDL) Synthesis:** Datapath elements serve as the fundamental module building blocks when writing synthesizable Verilog or VHDL models for modern application-specific integrated circuits (ASICs).

## Common mistakes

- **Assuming register reads depend on a clock edge.** Why it is wrong and how to avoid it: Register reads are combinational operations. Providing a register number address instantly propagates data to the read port outputs regardless of the clock. Register writes are sequential and take effect only on the active clock edge when write enable is high.
- **Including unused hardware units in timing delay calculations.** Why it is wrong and how to avoid it: An instruction only experiences delay along its active path. For example, R-type instructions do not pass through data memory, so adding $t_{\text{DMEM}}$ to an R-type path timing calculation is incorrect.
- **Omitting setup times in critical path analysis.** Why it is wrong and how to avoid it: Signals must arrive at destination registers early enough to satisfy setup time ($t_{\text{RegSetup}}$) constraints before the clock edge occurs. Always add setup time to the sum of physical component propagation delays.
- **Confusing multiplexer control lines with data lines.** Why it is wrong and how to avoid it: Data lines carry processing words (e.g., 32-bit integers), whereas control lines are single-bit or few-bit signals generated by decoding the opcode to select multiplexer paths.
- **Believing single-cycle datapaths yield optimal CPU performance.** Why it is wrong and how to avoid it: While a single-cycle datapath completes every instruction in 1 clock cycle (CPI = 1), the clock frequency is limited by the slowest instruction (`lw`). Fast instructions (`add`, `beq`) are forced to wait for the long clock period, making overall throughput lower than pipelined architectures.

## Revision notes

- The **datapath** comprises functional units (PC, Register File, ALU, Memory, Muxes) processing data; the **control unit** directs them.
- A **register file** uses multi-ported SRAM cells enabling concurrent unclocked reads and clock-edge triggered writes driven by `RegWrite`.
- In RISC architectures, register `x0` is hardwired to logic ground ($0$) to simplify instruction encoding.
- **Triple-bus datapaths** allow reading two source operands and writing one destination operand within a single cycle.
- The **ALU** computes values and updates status flags ($Z, N, C, V$) based on arithmetic logic operations.
- Control signals (`RegWrite`, `ALUSrc`, `MemRead`, `MemWrite`, `MemtoReg`, `PCSrc`) steer data through multiplexers based on opcode decoding.
- The **critical path** represents the maximum signal delay path in the circuit and is typically dominated by the load (`lw`) instruction.
- The minimum clock period $T_{\text{clock}}$ must exceed the sum of critical path component propagation delays and setup times.
- Maximum operational clock frequency is given by $f_{\text{max}} = 1 / T_{\text{clock}}$.

## Practice questions

:::question basic
A register file has 32 registers, each 64 bits wide. How many address lines are required for each read port, and how many parallel data lines are required for each write port?
:::answer
Selecting 1 out of 32 registers requires $\log_2(32) = 5$ address bits per read port. A 64-bit wide register file requires 64 parallel data lines for the write port to write a full word simultaneously. Therefore, 5 address lines and 64 write data lines are required.
:::

:::question basic
During the execution of a `sw` (store word) instruction, what are the values of `RegWrite` and `MemWrite`? Explain why.
:::answer
`RegWrite` is set to 0 and `MemWrite` is set to 1. This is because a store instruction transfers data from a source register into memory; it must modify memory content (`MemWrite` = 1) while leaving internal register file contents completely unchanged (`RegWrite` = 0).
:::

:::question intermediate
Explain why reading from a register file in a standard datapath is combinational, while writing to a register file is synchronous (sequential).
:::answer
Reading is combinational so that read data becomes available to the ALU immediately in the middle of the clock cycle as soon as the instruction bit fields are decoded. Writing is synchronous to prevent timing races; the destination register must store the calculated ALU or memory result strictly at the clock edge to ensure stability for the next clock period.
:::

:::question intermediate
A designer modifies a single-cycle datapath by replacing instruction memory with a faster module that reduces $t_{\text{IMEM}}$ by $100\text{ ps}$. If the critical path for `lw` was $900\text{ ps}$ and the second-longest path (`sw`) was $750\text{ ps}$, what is the new minimum clock period $T_{\text{clock}}$?
:::answer
The new delay for the load instruction path becomes $900\text{ ps} - 100\text{ ps} = 800\text{ ps}$. The delay for the store instruction path also decreases by $100\text{ ps}$ to $750\text{ ps} - 100\text{ ps} = 650\text{ ps}$. Since the load path remains the longest path at $800\text{ ps}$, the new minimum clock period $T_{\text{clock}}$ is $800\text{ ps}$.
:::

:::question advanced
In a single-cycle CPU datapath, why is the `MemtoReg` control signal treated as a "Don't Care" ($X$) during a branch instruction (`beq`), and what would happen if hardware accidentally set it to $1$?
:::answer
`MemtoReg` is a don't care because the `RegWrite` control signal is set to $0$ during a branch instruction, disabling any write operations to the register file. If hardware accidentally sets `MemtoReg` to 1 while `RegWrite` remains correctly at 0, no error occurs because the disabled `RegWrite` signal prevents register modification regardless of multiplexer output selection.
:::

:::question advanced
Consider a single-cycle datapath where $t_{\text{PC}} = 20\text{ ps}$, $t_{\text{IMEM}} = 200\text{ ps}$, $t_{\text{RegRead}} = 100\text{ ps}$, $t_{\text{ALU}} = 150\text{ ps}$, $t_{\text{DMEM}} = 200\text{ ps}$, $t_{\text{Mux}} = 15\text{ ps}$, and $t_{\text{RegSetup}} = 10\text{ ps}$. Calculate the percentage increase in maximum clock frequency if the datapath is converted from single-cycle execution to an ideal multi-cycle execution where each component delay is split across separate equal-duration clock cycles.
:::answer
In the single-cycle design, the critical load path latency is $T_{\text{single}} = 20 + 200 + 100 + 15 + 150 + 200 + 15 + 10 = 720\text{ ps}$, giving $f_{\text{single}} = 1 / 720\text{ ps} \approx 1.389\text{ GHz}$. In an ideal multi-cycle processor, the clock period is dictated by the longest single component stage delay, which is $t_{\text{IMEM}} = t_{\text{DMEM}} = 200\text{ ps}$ plus register setup/propagation ($200 + 10 = 210\text{ ps}$). This yields a multi-cycle clock period $T_{\text{multi}} = 210\text{ ps}$ and frequency $f_{\text{multi}} = 1 / 210\text{ ps} \approx 4.762\text{ GHz}$. The percentage increase in maximum clock frequency is $((4.762 - 1.389) / 1.389) \times 100\% \approx 242.8\%$.
:::

## Further learning

- **Next:** *Hardwired vs Microprogrammed Control* explores how state machines and microcode generate the control signals that direct datapath operations.
- **Next:** *Pipelining Fundamentals & Speedup* explains how overlap execution across datapath stages dramatically increases throughput over single-cycle implementations.
- **Related:** *Pipeline Hazards & Forwarding* covers how data pathways are modified with bypass multiplexers to solve register dependencies in high-performance processors.
- **Textbook:** David A. Patterson and John L. Hennessy, Computer Organization and Design RISC-V Edition.
