---
lesson: c-bitwise-operators
title: Bitwise Operators & Masks
summary: The bitwise operators AND, OR, XOR, NOT, and shifts, and how masks set, clear, toggle, and test individual bits in flags, permissions, and hardware registers.
minutes: 30
type: theory
objectives:
  - Evaluate expressions using &, |, ^, ~, <<, and >> on binary values
  - Build masks to set, clear, toggle, and test bits, and to extract bit fields
  - Explain the rules for shifts, including the dangers of shifting signed or negative values
review: ai-draft
---
## Introduction

Integers are stored as bits, and C lets you work on those bits directly. Bitwise operations pack eight true/false flags into one byte, read status bits from hardware, compute fast multiplications by powers of two, and power hash functions, compression, and graphics. They are also among the most frequently examined topics in C because their results are exact and easy to get wrong.

**Before you start:** you should know binary and hexadecimal notation and C's integer types.

## Core theory

### The six operators

For each bit position independently:

| Operator | Name | Result bit is 1 when |
| :--- | :--- | :--- |
| `a & b` | AND | both bits are 1 |
| `a \| b` | OR | at least one bit is 1 |
| `a ^ b` | XOR | the bits differ |
| `~a` | NOT | the bit of `a` is 0 |

Shifts move all bits: `a << n` shifts left by `n` places, filling with zeros, which multiplies by $2^n$ when no bits are lost; `a >> n` shifts right, which divides an unsigned value by $2^n$, rounding down.

Do not confuse `&` and `|` with the **logical** operators `&&` and `||`: `6 & 1` is 0 but `6 && 1` is 1.

### Masks

A **mask** is a value with 1s in the positions you care about. With `1u << k` as the mask for bit $k$ (counting from 0 at the right):

| Task | Expression |
| :--- | :--- |
| Set bit $k$ | `x \|= 1u << k` |
| Clear bit $k$ | `x &= ~(1u << k)` |
| Toggle bit $k$ | `x ^= 1u << k` |
| Test bit $k$ | `(x >> k) & 1u` or `(x & (1u << k)) != 0` |
| Lowest $n$ bits | `x & ((1u << n) - 1)` |

To **extract a field** of $n$ bits starting at bit $k$, shift right by $k$ then mask: `(x >> k) & ((1u << n) - 1)`.

### Useful identities

- `x & (x - 1)` clears the lowest set bit; a positive `x` is a power of two exactly when this is 0.
- `x ^ x` is 0 and `x ^ 0` is `x`, so XOR-ing every number in a list where all but one appear twice leaves the single one.
- `x & -x` (for unsigned arithmetic) isolates the lowest set bit.

### Shift rules

Shifting by a negative amount or by at least the width of the type is undefined behaviour. Left-shifting a negative signed value, or shifting a 1 into the sign bit, is also undefined, and right-shifting a negative value is implementation-defined (usually an arithmetic shift that copies the sign bit). Using **unsigned** types for bit manipulation avoids all of these traps.

## Worked examples

### Example 1: Evaluating operators by hand and in code

Let `a = 12` (binary `1100`) and `b = 10` (binary `1010`).

- `a & b` = `1000` = 8
- `a | b` = `1110` = 14
- `a ^ b` = `0110` = 6
- `a << 2` = `110000` = 48, and `a >> 2` = `11` = 3

```c
#include <stdio.h>

int main(void) {
    unsigned a = 12, b = 10;
    printf("%u %u %u\n", a & b, a | b, a ^ b);
    printf("%u %u\n", a << 2, a >> 2);
    printf("%u\n", ~a & 0xFu);
    printf("%d %d\n", 6 & 1, 6 && 1);
    return 0;
}
```

Output:

```text
8 14 6
48 3
3
0 1
```

`~a` flips all 32 bits; masking with `0xF` keeps only the low four, `0011`, which is 3.

### Example 2: File permissions as flags

```c
#include <stdio.h>

#define READ  (1u << 2)
#define WRITE (1u << 1)
#define EXEC  (1u << 0)

void show(unsigned p) {
    printf("%c%c%c\n", (p & READ) ? 'r' : '-', (p & WRITE) ? 'w' : '-', (p & EXEC) ? 'x' : '-');
}

int main(void) {
    unsigned perms = READ | WRITE;
    show(perms);
    perms |= EXEC;
    show(perms);
    perms &= ~WRITE;
    show(perms);
    perms ^= READ;
    show(perms);
    unsigned mode = 0754;
    printf("%u %u %u\n", (mode >> 6) & 7u, (mode >> 3) & 7u, mode & 7u);
    return 0;
}
```

Output:

```text
rw-
rwx
r-x
--x
7 5 4
```

Each permission is one bit. The octal mode `0754` stores three 3-bit fields; shifting and masking with 7 (binary `111`) extracts each one.

## Applications

- **Operating systems:** UNIX permissions and open-file flags (`O_RDONLY | O_CREAT`) are bit sets.
- **Embedded systems:** device registers are read and written bit by bit.
- **Networking:** IP subnet masks select the network part of an address with AND.
- **Algorithms:** bitmasks represent subsets in dynamic programming, and XOR tricks find unique elements.

## Common mistakes

- **Using `&&` instead of `&`.** Logical AND returns 0 or 1, not a combined mask.
- **Forgetting parentheses.** `x & 1 == 0` parses as `x & (1 == 0)` because `==` binds tighter than `&`; write `(x & 1) == 0`.
- **Shifting signed values.** Use unsigned types for bit work.
- **Clearing with `&= 1u << k`.** That clears every **other** bit; clearing needs the inverted mask `~(1u << k)`.

## Revision notes

- `&` both, `|` either, `^` differ, `~` flip, `<<` and `>>` shift.
- Set `x |= m`, clear `x &= ~m`, toggle `x ^= m`, test `x & m`.
- `x << n` multiplies by $2^n$; `x >> n` divides unsigned values by $2^n$.
- Field extraction: `(x >> k) & ((1u << n) - 1)`.
- `x & (x - 1)` clears the lowest set bit.
- Use unsigned types; shifting by the type width or more is undefined.

## Practice questions

:::question basic
Compute `9 | 6` and `9 & 6`.
:::answer
In binary 9 is `1001` and 6 is `0110`. They share no 1 bits, so `9 & 6` is 0 and `9 | 6` is `1111`, which is 15.
:::

:::question basic
Write an expression that is true when bit 3 of `flags` is set.
:::answer
`(flags & (1u << 3)) != 0`, or equivalently `(flags >> 3) & 1u`. The mask `1u << 3` is `1000` in binary, so the AND keeps only bit 3.
:::

:::question intermediate
Why does `if (x & 1 == 0)` not test whether `x` is even, and how do you fix it?
:::answer
`==` has higher precedence than `&`, so the condition is `x & (1 == 0)`, which is `x & 0`, always 0. Parenthesise the bitwise part: `if ((x & 1) == 0)`.
:::

:::question intermediate
Explain why `n > 0 && (n & (n - 1)) == 0` tests whether `n` is a power of two.
:::answer
A power of two has exactly one 1 bit. Subtracting 1 turns that bit into 0 and every lower bit into 1, so `n & (n - 1)` is 0. Any other positive number has at least two 1 bits, and subtracting 1 leaves the highest of them unchanged, so the AND is non-zero. The `n > 0` check excludes 0, which would otherwise pass.
:::

:::question advanced
A 16-bit sensor register stores temperature in bits 4 to 13 (10 bits). Write code to read the field from `reg` and to write a new value `t` into it without changing other bits.
:::answer
Read with `(reg >> 4) & 0x3FFu`, since `0x3FF` has ten 1 bits. To write, clear the field and insert the new value: `reg = (reg & ~(0x3FFu << 4)) | ((t & 0x3FFu) << 4);`. Masking `t` first prevents a too-large value from overwriting neighbouring bits.
:::

## Further learning

- **Next:** *Iteration & Switch Statements* covers the loops you will use to process bits and arrays.
- **Related:** *Data Types, Operators & Expressions* explains the integer types and promotions that bitwise operators work on.
