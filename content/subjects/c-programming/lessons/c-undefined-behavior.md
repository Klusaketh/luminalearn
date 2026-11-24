---
lesson: c-undefined-behavior
title: Undefined Behavior & Common Bugs
summary: What undefined behaviour means in C, the most common sources (out-of-bounds access, uninitialised reads, signed overflow, invalid pointers, unsequenced modifications), and the compiler warnings and sanitizers that catch them.
minutes: 45
type: theory
objectives:
  - Explain undefined, unspecified, and implementation-defined behaviour and why undefined behaviour can break code far from the bug
  - Recognise common undefined-behaviour bugs in C code and rewrite them safely
  - Use compiler warnings, sanitizers, and Valgrind to detect memory and arithmetic errors
review: ai-draft
---
## Introduction

C trusts the programmer. When code breaks certain rules, such as reading past the end of an array or overflowing a signed integer, the language standard says the behaviour is **undefined**: the program may crash, may print nonsense, may appear to work, or may behave differently with optimisation turned on. Undefined behaviour is the root of many security vulnerabilities and of bugs that disappear when you add a `printf`. Writing robust C means knowing these rules and using tools that enforce them.

**Before you start:** you should know arrays, pointers, heap allocation, and integer types.

## Core theory

### Three kinds of "not fully specified"

- **Implementation-defined:** each compiler must choose and document a behaviour, such as the size of `int` or the result of right-shifting a negative number.
- **Unspecified:** the standard allows several behaviours and the compiler need not document which, such as the order in which function arguments are evaluated.
- **Undefined:** the standard imposes **no requirements at all**.

### Why undefined behaviour is so dangerous

Compilers optimise on the assumption that undefined behaviour never happens. If code computes `x + 1 > x` for a signed `x`, the compiler may simplify it to "always true", because overflow "cannot happen". If a pointer is dereferenced and then checked for `NULL`, the compiler may delete the check, reasoning that the pointer was already used and therefore cannot be `NULL`. So undefined behaviour can change code that runs **before** or **far away from** the faulty line, and the bug may appear only in optimised builds.

### Common sources

| Bug | Example | Safe version |
| :--- | :--- | :--- |
| Out-of-bounds access | `a[n]` for an array of `n` | loop `i < n`; check indices |
| Uninitialised read | `int sum; sum += x;` | initialise: `int sum = 0;` |
| Signed overflow | `INT_MAX + 1` | check before adding; use wider types |
| Null or dangling pointer | `*p` after `free(p)` | set to `NULL`; check before use |
| Unsequenced modification | `i = i++ + 1;` | separate statements |
| Invalid shift | `1 << 32` for 32-bit `int` | shift unsigned values by less than the width |
| Division by zero | `x / 0`, `INT_MIN / -1` | check the divisor first |
| Modifying a string literal | `char *s = "hi"; s[0] = 'H';` | use `char s[] = "hi";` |

### Detecting bugs with tools

- **Warnings:** `gcc -Wall -Wextra -Wpedantic` flags uninitialised variables, format mismatches, signed/unsigned comparisons, and more. Treat warnings as errors with `-Werror`.
- **AddressSanitizer:** `-fsanitize=address -g` adds checks for out-of-bounds accesses, use-after-free, and double frees, stopping at the first one with a report naming the line.
- **UndefinedBehaviorSanitizer:** `-fsanitize=undefined` reports signed overflow, invalid shifts, misaligned access, and null dereferences while the program runs.
- **Valgrind:** runs the unmodified program and reports invalid reads, writes, uninitialised values, and leaks.
- **Static analysers** such as `clang --analyze` and `cppcheck` find some bugs without running the code.

Tools find bugs only on the paths your tests execute, so combine them with tests that cover edge cases.

## Worked examples

### Example 1: Checking for overflow before it happens

```c
#include <stdio.h>
#include <limits.h>

int safe_add(int a, int b, int *result) {
    if ((b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b)) return 0;
    *result = a + b;
    return 1;
}

int safe_index(const int *arr, int n, int i, int *out) {
    if (i < 0 || i >= n) return 0;
    *out = arr[i];
    return 1;
}

int main(void) {
    int r;
    printf("%d\n", safe_add(2000000000, 100000000, &r) ? r : -1);
    printf("%d\n", safe_add(2000000000, 200000000, &r) ? r : -1);
    printf("%d\n", safe_add(INT_MIN, -1, &r) ? r : -1);
    long long wide = (long long)INT_MAX + 1;
    printf("%lld\n", wide);
    int data[3] = {7, 8, 9}, v;
    printf("%s\n", safe_index(data, 3, 3, &v) ? "ok" : "index 3 rejected");
    unsigned u = 1u << 31;
    printf("%u\n", u);
    return 0;
}
```

Output:

```text
2100000000
-1
-1
2147483648
index 3 rejected
2147483648
```

The checks compare against the limits **before** adding, so the overflowing addition never executes. Converting to `long long` before adding computes the true sum. Shifting an unsigned 1 into bit 31 is well defined, whereas `1 << 31` on a signed 32-bit `int` is not.

### Example 2: What a sanitizer reports

Compile this off-by-one bug with `gcc -fsanitize=address -g bug.c` and run it:

```c
#include <stdlib.h>

int main(void) {
    int *a = malloc(4 * sizeof *a);
    for (int i = 0; i <= 4; i++) a[i] = i;
    free(a);
    return 0;
}
```

Without the sanitizer the program usually runs silently, which is the danger. With it, the program stops at the first invalid write with a report like this (addresses vary):

```text
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x502000000020
WRITE of size 4 at 0x502000000020 thread T0
    #0 0x55d1c2a1b2c3 in main bug.c:5
0x502000000020 is located 0 bytes after 16-byte region
```

The report names the kind of error, the size of the write, the source line (`bug.c:5`), and that the address lies just after a 16-byte block: the loop condition should be `i < 4`.

## Applications

- **Security:** most memory-corruption exploits begin with undefined behaviour such as buffer overflows.
- **Continuous integration:** test suites run under sanitizers to catch bugs before release.
- **Safety-critical code:** standards such as MISRA C restrict the language to avoid undefined behaviour.
- **Compiler optimisation:** knowing what the compiler may assume explains surprising optimised builds.

## Common mistakes

- **"It works on my machine."** Undefined behaviour can appear to work until the compiler, flags, or input change.
- **Checking for overflow after it happened.** `if (a + b < a)` relies on the overflow itself; check against the limits first.
- **Ignoring warnings.** Many warnings point directly at undefined behaviour.
- **Testing only with optimisation off.** Some bugs appear only at `-O2`; test both builds, with sanitizers.

## Revision notes

- Undefined behaviour: the standard places no requirements; optimisers assume it never happens.
- Implementation-defined: documented choice; unspecified: any allowed choice.
- Common causes: out-of-bounds, uninitialised reads, signed overflow, invalid pointers, unsequenced modifications, bad shifts, division by zero.
- Check limits **before** arithmetic; use unsigned or wider types where appropriate.
- Tools: `-Wall -Wextra`, `-fsanitize=address`, `-fsanitize=undefined`, Valgrind.
- Sanitizers only check executed paths; test edge cases.

## Practice questions

:::question basic
What is the difference between undefined and implementation-defined behaviour?
:::answer
Implementation-defined behaviour must be chosen and documented by each compiler, so it is predictable on a given platform, such as the size of `int`. Undefined behaviour has no requirements at all: the program may do anything, and the result can change between compilers, flags, or runs.
:::

:::question basic
Which compiler flag adds run-time detection of out-of-bounds heap accesses?
:::answer
`-fsanitize=address` (AddressSanitizer), ideally together with `-g` so reports show source lines. It stops the program at the first invalid access and prints a detailed report.
:::

:::question intermediate
Why can `if (x + 1 < x) { /* overflow */ }` fail to detect overflow for a signed `int x`?
:::answer
Signed overflow is undefined, so the compiler may assume `x + 1` never overflows and that `x + 1 < x` is always false, and remove the whole branch. Check against the limit before adding instead: `if (x == INT_MAX)`.
:::

:::question intermediate
Identify the undefined behaviour in `int total; for (int i = 0; i < n; i++) total += a[i];`.
:::answer
`total` is an automatic variable that is never initialised, so the first `total += a[i]` reads an indeterminate value. Initialise it with `int total = 0;`. Depending on how `a` and `n` were set up, the loop could also read out of bounds if `n` exceeds the array length.
:::

:::question advanced
A function dereferences `p->len` and only afterwards checks `if (p == NULL) return;`. With optimisation on, the check disappears. Explain why, and how to write the function correctly.
:::answer
Dereferencing a null pointer is undefined, so once the code has executed `p->len`, the compiler may assume `p` is not `NULL` and treat the later check as always false, deleting it. If `p` really is `NULL`, the program crashes or worse at the dereference. Move the check before any use: `if (p == NULL) return; size_t n = p->len;`.
:::

## Further learning

- **Next:** *Pointers & Address Arithmetic* revisits the rules for valid pointer operations.
- **Related:** *Heap Allocation & Memory Leaks* covers use-after-free and double free in detail.
