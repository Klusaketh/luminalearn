---
lesson: c-data-types-expressions
title: Data Types, Operators & Expressions
summary: C's integer and floating-point types, how values are converted in mixed expressions, integer division and overflow, and the operator precedence rules that decide how expressions are evaluated.
minutes: 45
type: theory
objectives:
  - Choose appropriate integer and floating-point types and print them with the correct printf formats
  - Predict the result of mixed-type expressions, integer division, casts, and the usual arithmetic conversions
  - Apply operator precedence and associativity, and avoid unsequenced side effects
review: ai-draft
---
## Introduction

In C, the type of a value decides how many bytes it occupies, what range it can hold, and how arithmetic on it behaves. `7 / 2` is 3 but `7.0 / 2` is 3.5; adding 1 to the largest `unsigned int` gives 0. These rules are precise, and C programs depend on them. This lesson covers the basic types, conversions, and how expressions are evaluated.

**Before you start:** you should know how a C program is compiled and run, and the idea of a variable.

## Core theory

### Integer types

C provides `char`, `short`, `int`, `long`, and `long long`, each in **signed** and **unsigned** forms. The standard fixes only minimum ranges; on today's common desktop and server systems `char` is 8 bits, `short` 16, `int` 32, and `long long` 64. A signed $n$-bit integer in two's complement holds $-2^{n-1}$ to $2^{n-1} - 1$, so a 32-bit `int` covers about $\pm 2.1 \times 10^9$. An unsigned $n$-bit integer holds $0$ to $2^n - 1$. When you need an exact width, `<stdint.h>` provides `int32_t`, `uint8_t`, and friends. `sizeof(type)` gives a size in bytes.

### Floating-point types

`float` (usually 32-bit, about 7 significant decimal digits) and `double` (64-bit, about 15 to 16 digits) follow IEEE 754. Most decimal fractions, such as 0.1, have no exact binary representation, so compare floating values with a tolerance rather than `==`. Prefer `double` unless memory is tight.

### printf formats

| Type | Format |
| :--- | :--- |
| `int` | `%d` |
| `unsigned int` | `%u` |
| `long` / `long long` | `%ld` / `%lld` |
| `double` | `%f`, `%.2f`, `%e`, `%g` |
| `char` | `%c` |
| `size_t` (from `sizeof`) | `%zu` |

A mismatched format, such as printing a `double` with `%d`, is undefined behaviour.

### Conversions

In an expression mixing types, C applies the **usual arithmetic conversions**: small types (`char`, `short`) are first promoted to `int`, then the operand of the "lower" type is converted to the "higher" one, roughly `int` < `unsigned int` < `long` < ... < `float` < `double`. So `7 / 2` is integer division (3, the fraction is discarded towards zero) while `7 / 2.0` is 3.5. A **cast** converts explicitly: `(double)a / b`. Assigning a `double` to an `int` truncates towards zero.

Mixing signed and unsigned values is a classic trap: in `-1 < 1u`, the `-1` is converted to `unsigned int`, becoming 4294967295, so the comparison is false.

### Overflow

Unsigned arithmetic wraps around modulo $2^n$, which is well defined. **Signed** overflow, such as adding 1 to `INT_MAX`, is **undefined behaviour**: the program is not required to do anything sensible. Use a wider type, or check before the operation.

### Precedence and associativity

Precedence decides grouping: `*`, `/`, `%` bind tighter than `+` and `-`, which bind tighter than comparisons, then `&&`, then `||`, then assignment. Operators of equal precedence associate left to right (`a - b - c` is `(a - b) - c`), except assignment and unary operators, which associate right to left (`a = b = 0`). Precedence does not fix the order in which operands are evaluated, so `i = i++ + 1;` or `f(i, i++)` is undefined: never modify a variable twice, or read and modify it, without a sequence point between.

## Worked examples

### Example 1: Integer and floating division, casts, and formats

```c
#include <stdio.h>

int main(void) {
    int a = 7, b = 2;
    printf("%d %d\n", a / b, a % b);
    printf("%.2f\n", a / b * 1.0);
    printf("%.2f\n", (double)a / b);
    printf("%d\n", -7 / 2);
    double price = 19.99;
    int whole = (int)price;
    printf("%d %.1f\n", whole, price - whole);
    printf("%zu %zu\n", sizeof(char), sizeof(double));
    return 0;
}
```

Output:

```text
3 1
3.00
3.50
-3
19 1.0
1 8
```

`a / b * 1.0` performs `a / b` first in integer arithmetic (3), then converts to 3.0. Casting `a` before dividing makes the whole division floating point. Integer division truncates towards zero, so `-7 / 2` is -3.

### Example 2: Unsigned wrap-around and signed/unsigned comparison

```c
#include <stdio.h>
#include <limits.h>

int main(void) {
    unsigned int u = UINT_MAX;
    u = u + 1;
    printf("%u\n", u);
    unsigned char small = 250;
    small += 10;
    printf("%d\n", small);
    if (-1 < 1u) {
        printf("expected\n");
    } else {
        printf("surprise: -1 became %u\n", (unsigned int)-1);
    }
    printf("%d\n", 2 + 3 * 4 > 10 && 1);
    return 0;
}
```

Output:

```text
0
4
surprise: -1 became 4294967295
1
```

Unsigned values wrap modulo $2^n$: 255 + 1 for 8 bits is 0, so 250 + 10 is 4. In the comparison, `-1` is converted to unsigned. In the last line, `3 * 4` is computed first, then the addition, the comparison, and finally `&&`.

## Applications

- **Embedded code:** exact-width types such as `uint8_t` match hardware registers.
- **Financial calculations:** integers counting the smallest currency unit avoid floating-point rounding.
- **Hashing and checksums:** unsigned wrap-around is used deliberately.
- **Scientific code:** `double` and careful conversion rules keep precision.

## Common mistakes

- **Expecting `5 / 2` to be 2.5.** Both operands are integers; cast one to `double`.
- **Comparing signed and unsigned values.** The signed value is converted; compile with `-Wall -Wextra` to get warnings.
- **Relying on signed overflow to wrap.** It is undefined behaviour and optimisers exploit that.
- **Using the wrong printf format.** Use `%zu` for `sizeof`, `%lld` for `long long`, `%f` for `double`.

## Revision notes

- Common sizes: `char` 1 byte, `int` 4, `long long` 8, `double` 8 (check with `sizeof`).
- Integer division truncates towards zero; `%` gives the remainder with the sign of the dividend.
- Usual arithmetic conversions promote the "lower" operand; casts convert explicitly.
- Unsigned overflow wraps; signed overflow is undefined.
- `*` `/` `%` > `+` `-` > comparisons > `&&` > `||` > `=`.
- Never modify and read a variable without a sequence point between.

## Practice questions

:::question basic
What are the values of `17 / 5` and `17 % 5` in C?
:::answer
`17 / 5` is 3 and `17 % 5` is 2. Both operands are integers, so division discards the fractional part, and the remainder satisfies $17 = 5 \times 3 + 2$.
:::

:::question basic
Which printf format prints a `double` with three decimal places?
:::answer
`%.3f`. The `f` conversion prints fixed-point notation and the `.3` sets the number of digits after the decimal point.
:::

:::question intermediate
What does `int x = 3.99;` store, and what does `(int)-3.99` evaluate to?
:::answer
`x` stores 3, and `(int)-3.99` is -3. Converting a floating value to an integer truncates towards zero, discarding the fractional part rather than rounding.
:::

:::question intermediate
Why is `if (strlen(s) - 1 >= 0)` always true, and how should it be written?
:::answer
`strlen` returns `size_t`, an unsigned type, so `strlen(s) - 1` is unsigned and can never be negative; for an empty string it wraps to a huge value. Write `if (strlen(s) >= 1)` or `if (s[0] != '\0')` instead.
:::

:::question advanced
Two `int` variables hold 50,000 each. Explain why `int area = w * h;` is dangerous and give a safe alternative.
:::answer
The product is 2,500,000,000, which exceeds `INT_MAX` (2,147,483,647 for 32-bit `int`), so the multiplication overflows a signed type: undefined behaviour. Convert before multiplying so the arithmetic happens in a wider type: `long long area = (long long)w * h;`, and print it with `%lld`.
:::

## Further learning

- **Next:** *Bitwise Operators & Masks* works directly with the bits of integer types.
- **Related:** *Undefined Behavior & Common Bugs* explains why signed overflow and unsequenced side effects are so dangerous.
