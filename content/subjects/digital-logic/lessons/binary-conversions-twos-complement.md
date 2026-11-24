---
lesson: binary-conversions-twos-complement
title: Binary Conversions & 2's Complement
summary: Master the representation of signed integers using 2's complement, learn conversion techniques between bases, and understand how digital hardware detects arithmetic overflow in fixed-width registers.
minutes: 35
type: theory
objectives:
  - Convert integers between decimal, binary, octal, and hexadecimal bases
  - Represent signed integers using the 2's complement system
  - Perform 2's complement negation and addition
  - Identify arithmetic overflow conditions in fixed-width binary arithmetic
review: ai-draft
---

## Introduction

Imagine you are designing a simple digital thermometer. The hardware uses 8-bit registers to store the temperature. When the sun is out, it might read $25^\circ\text{C}$, which is easily represented as a standard binary number. But what happens when the temperature drops to $-5^\circ\text{C}$? 

Computers do not have a built-in "minus sign" symbol; they only have bits—0s and 1s. To handle negative numbers, engineers had to develop a mathematical convention that allows the hardware to perform subtraction using the same circuitry it uses for addition. This system is known as **2's complement**.

In this lesson, we will explore how numbers are represented in different bases (binary, octal, and hexadecimal) and how the 2's complement system provides an elegant solution for signed integer arithmetic. We will also learn how to spot **overflow**, a critical error that occurs when a calculation produces a result too large for the computer's memory to hold.

**Before you start:** This is an introductory lesson; no prior knowledge of digital logic is required, though basic familiarity with powers of 2 will be helpful.

## Core theory

### Positional Number Systems

All modern digital systems use **positional notation**. In this system, the value of a digit depends on its position relative to a **radix** (or base) $r$. For any integer, the value is calculated as the sum of its digits $d_i$ multiplied by the base raised to the power of their position $i$:

$$Value = \sum_{i=0}^{n-1} d_i \cdot r^i$$

In our everyday **Decimal (Base 10)** system, $r=10$. In digital logic, we primarily use:
*   **Binary (Base 2):** Digits $\{0, 1\}$. This is the native language of transistors.
*   **Octal (Base 8):** Digits $\{0, 1, 2, 3, 4, 5, 6, 7\}$.
*   **Hexadecimal (Base 16):** Digits $\{0-9, A-F\}$, where $A=10, B=11, \dots, F=15$.

### Converting Between Bases

Converting between binary, octal, and hexadecimal is straightforward because their bases are powers of 2 ($2^3=8$ and $2^4=16$). 

To convert **Binary to Hexadecimal**, group the bits into sets of four (called **nibbles**) starting from the right. To convert **Binary to Octal**, group them into sets of three.

| Decimal | Binary | Hexadecimal | Octal |
| :--- | :--- | :--- | :--- |
| 0 | 0000 | 0 | 0 |
| 5 | 0101 | 5 | 5 |
| 10 | 1010 | A | 12 |
| 15 | 1111 | F | 17 |

For **Decimal to Binary** conversion, we use the method of repeated division by 2. The remainder of each division becomes a bit in the binary number, starting from the **Least Significant Bit (LSB)** and moving toward the **Most Significant Bit (MSB)**.

### Representing Signed Integers

In an **unsigned** system, an $n$-bit number can represent values from $0$ to $2^n - 1$. However, to represent negative numbers, we must sacrifice one bit (the MSB) to act as a sign indicator.

1.  **Sign-Magnitude:** The MSB is the sign (0 for positive, 1 for negative), and the remaining bits are the magnitude. This is intuitive but problematic because it results in two representations for zero ($+0$ and $-0$) and requires complex addition/subtraction hardware.
2.  **1's Complement:** Negative numbers are formed by flipping every bit of the positive counterpart. This still suffers from the "double zero" problem.
3.  **2's Complement:** This is the standard in modern computing. To find the negative of a number, you **invert all bits and add 1**.

The primary advantage of 2's complement is that subtraction $A - B$ can be performed as $A + (-B)$. The CPU does not need a separate "subtractor" circuit; it simply negates $B$ and adds it to $A$.

### The 2's Complement Algorithm

To represent a negative decimal number $-X$ in $n$-bit 2's complement:
1.  Write the binary representation of the positive magnitude $X$.
2.  Ensure it is padded with leading zeros to the required bit-width $n$.
3.  **Invert** all bits (change 0 to 1 and 1 to 0). This is the 1's complement.
4.  **Add 1** to the result.

```mermaid
flowchart TD
    A[Start: Decimal -X] --> B[Convert X to Unsigned Binary]
    B --> C[Pad to n bits]
    C --> D[Invert all bits]
    D --> E[Add 1 to the result]
    E --> F[Result: n-bit 2's Complement]
---
```

### The Weight of the Sign Bit

A powerful way to understand 2's complement is to look at the "weight" of each bit position. In an $n$-bit 2's complement number, the weights are exactly like unsigned binary, except the **MSB has a negative weight**.

For an 8-bit number, the weights are:
$$-2^7, 2^6, 2^5, 2^4, 2^3, 2^2, 2^1, 2^0$$
$$-128, 64, 32, 16, 8, 4, 2, 1$$

If the MSB is 1, the number is negative. If the MSB is 0, the number is positive.

### Range and Overflow

A fixed-width $n$-bit register has a limited **range**. For 2's complement, the range is:
$$[-2^{n-1}, 2^{n-1} - 1]$$

For 8 bits, this is $[-128, 127]$. Note that there is one more negative number than positive because zero takes up one of the "positive" slots (where the MSB is 0).

**Arithmetic Overflow** occurs when the result of an addition or subtraction falls outside this range. In 2's complement addition, overflow occurs if and only if:
*   Two positive numbers are added and the result is negative.
*   Two negative numbers are added and the result is positive.

**Note:** A carry-out from the MSB does *not* necessarily mean overflow has occurred in signed arithmetic.

## Worked examples

### Example 1: Decimal to 8-bit 2's Complement

**Task:** Convert the decimal number $-18$ into 8-bit 2's complement.

1.  **Find the magnitude in binary:**
    $18 = 16 + 2 = 2^4 + 2^1$.
    In binary, this is `10010`.
2.  **Pad to 8 bits:**
    `00010010`
3.  **Invert the bits (1's complement):**
    `11101101`
4.  **Add 1:**
    `11101101 + 1 = 11101110`

**Final Answer:** The 8-bit 2's complement representation of $-18$ is `11101110`.

### Example 2: 2's Complement to Decimal

**Task:** Convert the 8-bit 2's complement number `11111001` to decimal.

**Method A: The "Flip and Add 1" Reverse**
1.  Since the MSB is 1, the number is negative.
2.  Invert the bits: `00000110`.
3.  Add 1: `00000111`.
4.  The magnitude is $4 + 2 + 1 = 7$.
5.  Apply the negative sign: $-7$.

**Method B: Sum of Weights**
Using the weights $-128, 64, 32, 16, 8, 4, 2, 1$:
$$(1 \cdot -128) + (1 \cdot 64) + (1 \cdot 32) + (1 \cdot 16) + (1 \cdot 8) + (0 \cdot 4) + (0 \cdot 2) + (1 \cdot 1)$$
$$-128 + 64 + 32 + 16 + 8 + 1 = -7$$

**Final Answer:** `11111001` is $-7$ in decimal.

### Example 3: Addition and Overflow Detection

**Task:** Perform the addition of $120 + 10$ using 8-bit 2's complement and determine if overflow occurs.

1.  **Convert to binary:**
    $120 = 01111000_2$
    $10 = 00001010_2$
2.  **Perform addition:**
    ```text
      01111000  (120)
    + 00001010  (10)
    ----------
      10000010
    ```
3.  **Analyze the result:**
    The result is `10000010`.
    The MSB is 1, which indicates a negative number.
    However, we added two positive numbers ($120$ and $10$).
    A positive + positive resulting in a negative is the definition of **overflow**.

**Reasoning:** The maximum value for an 8-bit signed integer is $127$. Since $120 + 10 = 130$, the result exceeds the range. In hardware, this would be interpreted as $-126$ (the value of `10000010`).

## Applications

*   **Arithmetic Logic Units (ALUs):** Every CPU contains an ALU that uses 2's complement to perform subtractions using addition logic, significantly reducing the number of transistors required.
*   **Memory Addressing:** In programming languages like C, pointers use signed offsets. To move "backwards" in memory, the system adds a 2's complement negative number to the current memory address.
*   **Digital Signal Processing (DSP):** Audio signals oscillate between positive and negative values. 2's complement allows DSP chips to process these waves using standard integer math.
*   **Network Protocols:** Fields in headers (like the TTL in IP packets or sequence numbers in TCP) are often treated as unsigned, but window size adjustments and offsets frequently rely on signed binary logic.

## Common mistakes

*   **Forgetting to pad bits before negating.** If you want the 8-bit 2's complement of $-5$, you must write $5$ as `00000101` before flipping. If you flip `101` (3 bits) to get `010` and then add 1 to get `011`, you get $3$, not $-5$.
*   **Confusing Carry-out with Overflow.** In unsigned addition, a carry-out from the MSB means the result is too big. In signed 2's complement, a carry-out is often normal and should be ignored; overflow is only detected by checking the signs of the operands and the result.
*   **Incorrect Range Limits.** Students often think an 8-bit signed number goes from $-127$ to $127$. Remember the asymmetry: it is $-128$ to $127$. The value $-128$ (`10000000`) has no positive counterpart in 8 bits.
*   **Applying 2's complement to positive numbers.** 2's complement is a *system* for representing numbers. Positive numbers in this system look exactly like standard unsigned binary (with a 0 in the MSB). You only perform the "invert and add 1" steps when you want to find the negative version of a number.
*   **Sign Extension errors.** When moving a 4-bit signed number to an 8-bit register, you must copy the sign bit into all the new positions. For example, $-3$ in 4 bits is `1101`. In 8 bits, it must be `11111101`, not `00001101`.

## Revision notes

*   **Base-n to Decimal:** Multiply each digit by $n^{position}$.
*   **Hex to Binary:** Each hex digit maps to exactly 4 bits (e.g., $F = 1111$).
*   **Octal to Binary:** Each octal digit maps to exactly 3 bits (e.g., $7 = 111$).
*   **2's Complement Negation:** Invert all bits and add 1.
*   **Sign Bit:** The MSB is 0 for positive, 1 for negative.
*   **Range Formula:** For $n$ bits, the range is $[-2^{n-1}, 2^{n-1}-1]$.
*   **Overflow Rule:** Overflow occurs if $Pos + Pos = Neg$ or $Neg + Neg = Pos$.
*   **Subtraction:** $A - B$ is implemented as $A + (\text{NOT } B + 1)$.

## Practice questions

:::question basic
Convert the hexadecimal number `0x3A` to both binary and decimal.
:::answer
To binary: $3 = 0011$ and $A = 1010$, so `00111010`. To decimal: $(3 \cdot 16^1) + (10 \cdot 16^0) = 48 + 10 = 58$.
:::

:::question basic
What is the 8-bit 2's complement representation of the decimal number $-1$?
:::answer
Start with $+1$ in 8-bit binary: `00000001`. Invert the bits to get `11111110`, then add 1 to get `11111111`. In 2's complement, a sequence of all 1s always represents $-1$.
:::

:::question intermediate
Negate the 8-bit 2's complement number `10000000` and explain the result.
:::answer
Inverting `10000000` gives `01111111`. Adding 1 gives `10000000`. The result is the same as the input because `10000000` is $-128$, and $+128$ cannot be represented in 8 bits; this is a special case where negating the most negative number results in an overflow.
:::

:::question intermediate
Calculate the range of signed integers that can be represented in a 12-bit register using 2's complement.
:::answer
Using the formula $[-2^{n-1}, 2^{n-1}-1]$ with $n=12$: $2^{11} = 2048$. Therefore, the range is $[-2048, 2047]$.
:::

:::question advanced
Perform the 8-bit 2's complement addition: `11000110 + 11111010`. Convert the operands and the result to decimal. Does overflow occur?
:::answer
`11000110` is $-58$. `11111010` is $-6$. Adding them: `11000110 + 11111010 = (1)11000000` (the carry-out is ignored). The result `11000000` is $-64$. Since $-58 + (-6) = -64$, and $-64$ is within the 8-bit range $[-128, 127]$, no overflow occurs.
:::

:::question advanced
A computer designer decides to use 1's complement instead of 2's complement. If the 8-bit ALU adds `00000001` ($+1$) and `11111110` ($-1$ in 1's complement), what is the result in binary, and why is this problematic?
:::answer
Adding `00000001 + 11111110` results in `11111111`. In 1's complement, `11111111` is "negative zero." This is problematic because it requires the hardware to handle two different bit patterns for the value zero, complicating equality comparisons and logic gates.
:::

## Further learning

*   **Next:** *Binary Arithmetic, Overflow & Codes* explores how these representations are used in complex arithmetic circuits and error-detecting codes.
*   **Related:** *Adders & Multiplexers Design* shows the actual logic gate configurations (Half-Adders and Full-Adders) that perform the additions we studied today.
*   **Related:** *Integer Arithmetic & IEEE 754 Floating Point* explains how computers represent non-integers (decimals) using a scientific notation format.
*   **Textbook:** Harris & Harris, *Digital Design and Computer Architecture*.

```python
# Python demonstration of 2's complement behavior
def show_twos_complement(value, bit_width):
    # Mask to simulate fixed bit width
    mask = (1 << bit_width) - 1
    
    if value >= 0:
        binary_str = format(value & mask, f'0{bit_width}b')
    else:
        # 2's complement of a negative number in Python
        # is handled by adding it to 2^bit_width
        binary_str = format((1 << bit_width) + value, f'0{bit_width}b')
        
    return binary_str

# Test cases for 8-bit representation
test_values = [127, -128, 5, -5, -1]
for v in test_values:
    print(f"Decimal: {v:4} | 8-bit Binary: {show_twos_complement(v, 8)}")

# Demonstrating overflow
a = 120
b = 10
result = a + b
print(f"\nOverflow Example: {a} + {b} = {result}")
print(f"Binary result (8-bit): {show_twos_complement(result, 8)}")
```

Output:
```text
Decimal:  127 | 8-bit Binary: 01111111
Decimal: -128 | 8-bit Binary: 10000000
Decimal:    5 | 8-bit Binary: 00000101
Decimal:   -5 | 8-bit Binary: 11111011
Decimal:   -1 | 8-bit Binary: 11111111

Overflow Example: 120 + 10 = 130
Binary result (8-bit): 10000010
```
