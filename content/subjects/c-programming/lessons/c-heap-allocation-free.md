---
lesson: c-heap-allocation-free
title: Heap Allocation & Memory Leaks
summary: Allocating memory at run time with malloc, calloc, and realloc, releasing it with free, and avoiding leaks, double frees, and dangling pointers with disciplined ownership and tools.
minutes: 45
type: theory
objectives:
  - Allocate, resize, and free heap memory correctly, checking every allocation for failure
  - Explain memory leaks, dangling pointers, double frees, and use-after-free, and how each arises
  - Apply ownership rules and use tools such as Valgrind and AddressSanitizer to find memory bugs
review: ai-draft
---
## Introduction

Arrays declared in a function have a fixed size and vanish when the function returns. Real programs often need memory whose size is known only at run time, such as a file's contents or a list that grows as data arrives, and that outlives the function that created it. C provides this through the **heap**, managed by hand with `malloc` and `free`. Manual management is fast and flexible, but every allocation must be freed exactly once, and mistakes cause leaks, crashes, and security holes.

**Before you start:** you should know pointers, `sizeof`, arrays, and structures.

## Core theory

### Allocating and freeing

All four functions are declared in `<stdlib.h>`:

- `malloc(n)` reserves `n` bytes and returns a pointer to them, or `NULL` on failure. The contents are **uninitialised**.
- `calloc(count, size)` reserves `count * size` bytes, sets them to zero, and checks the multiplication for overflow.
- `realloc(p, n)` resizes the block at `p` to `n` bytes, possibly moving it; the old contents are preserved up to the smaller size. It returns the new pointer or `NULL` on failure, in which case the original block is untouched.
- `free(p)` returns the block to the allocator. `free(NULL)` does nothing.

The idiomatic allocation names the type through the pointer: `int *a = malloc(n * sizeof *a);`. Always check the result for `NULL` before use.

### Growing an array safely with realloc

```c
int *bigger = realloc(a, new_cap * sizeof *a);
if (bigger == NULL) { /* a is still valid: handle the error */ }
else a = bigger;
```

Writing `a = realloc(a, ...)` directly loses the only pointer to the old block if `realloc` fails, which leaks it. Growing the capacity by a constant factor (for example doubling) keeps the total cost of $n$ appends at $O(n)$, the amortized analysis behind dynamic arrays.

### The four classic memory bugs

1. **Memory leak:** allocated memory is never freed, usually because the last pointer to it was overwritten or went out of scope. Long-running programs slowly consume all memory.
2. **Dangling pointer / use-after-free:** a pointer still refers to a block after `free`. Reading or writing through it is undefined behaviour and a common source of exploitable vulnerabilities.
3. **Double free:** freeing the same block twice corrupts the allocator's bookkeeping.
4. **Buffer overflow on the heap:** writing past the end of a block corrupts neighbouring allocations.

Setting a pointer to `NULL` right after freeing it turns a later accidental use into an obvious crash and makes a second `free` harmless.

### Ownership discipline and tools

Decide for every allocation who **owns** it, meaning who is responsible for freeing it, and document it: "the caller must free the returned string". Pair each allocating function with a matching release function (`list_create` / `list_destroy`). Tools catch what discipline misses: **Valgrind** (`valgrind --leak-check=full ./prog`) reports leaks and invalid accesses, and **AddressSanitizer** (`gcc -fsanitize=address -g`) stops the program at the first invalid access with a precise report.

## Worked examples

### Example 1: A growable array with malloc, realloc, and free

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t cap = 2, len = 0;
    int *a = malloc(cap * sizeof *a);
    if (a == NULL) return 1;
    for (int v = 1; v <= 10; v++) {
        if (len == cap) {
            size_t new_cap = cap * 2;
            int *bigger = realloc(a, new_cap * sizeof *a);
            if (bigger == NULL) { free(a); return 1; }
            a = bigger;
            cap = new_cap;
            printf("grew to %zu\n", cap);
        }
        a[len++] = v * v;
    }
    printf("len=%zu cap=%zu last=%d\n", len, cap, a[len - 1]);
    free(a);
    a = NULL;
    return 0;
}
```

Output:

```text
grew to 4
grew to 8
grew to 16
len=10 cap=16 last=100
```

Doubling means only three reallocations are needed for ten items. The temporary `bigger` protects the original block if `realloc` fails, and the block is freed exactly once at the end.

### Example 2: calloc, ownership, and returning heap memory

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Returns a new string; the caller owns it and must free it. */
char *repeat(const char *word, int times) {
    size_t n = strlen(word);
    char *out = malloc(n * (size_t)times + 1);
    if (out == NULL) return NULL;
    out[0] = '\0';
    for (int i = 0; i < times; i++) strcat(out, word);
    return out;
}

int main(void) {
    int *counts = calloc(5, sizeof *counts);
    if (counts == NULL) return 1;
    counts[2] += 3;
    for (int i = 0; i < 5; i++) printf("%d ", counts[i]);
    printf("\n");
    free(counts);

    char *s = repeat("ab", 3);
    if (s != NULL) {
        printf("%s (%zu chars)\n", s, strlen(s));
        free(s);
    }
    return 0;
}
```

Output:

```text
0 0 3 0 0
ababab (6 chars)
```

`calloc` zeroes the counters, while `malloc` would leave them unpredictable. `repeat` returns heap memory, which survives the function's return, and its comment states that the caller must free it.

## Applications

- **Dynamic collections:** vectors, hash tables, and trees grow and shrink on the heap.
- **Reading files:** a buffer sized from the file length holds its contents.
- **Long-running servers:** careful freeing keeps memory use flat for months of uptime.
- **Libraries:** create/destroy function pairs make ownership explicit for users.

## Common mistakes

- **Not checking for `NULL`.** Allocation can fail, especially for large sizes.
- **`p = realloc(p, n)`.** On failure the original block leaks; use a temporary.
- **Using memory after `free`.** Set pointers to `NULL` after freeing them.
- **Forgetting the `+ 1` for a string's terminator.** The copy then overflows the block.
- **Freeing memory not obtained from `malloc`.** Never `free` a stack array or a string literal.

## Revision notes

- `malloc` (uninitialised), `calloc` (zeroed), `realloc` (resize, may move), `free`.
- Idiom: `T *p = malloc(n * sizeof *p); if (!p) { handle error }`.
- Grow by doubling for amortized $O(1)$ appends; keep the old pointer until `realloc` succeeds.
- Bugs: leak, use-after-free, double free, heap overflow.
- Free exactly once; set the pointer to `NULL` afterwards.
- Valgrind and `-fsanitize=address` find memory errors.

## Practice questions

:::question basic
What is the difference between `malloc(10 * sizeof(int))` and `calloc(10, sizeof(int))`?
:::answer
Both allocate space for 10 integers. `malloc` leaves the contents uninitialised, whereas `calloc` sets every byte to zero and also checks that the multiplication does not overflow.
:::

:::question basic
What is a memory leak, and why does it matter more in a server than in a short command-line tool?
:::answer
A leak is allocated memory that is never freed after the program loses every pointer to it. A short tool exits soon and the operating system reclaims everything, but a server runs for weeks, so a small leak per request steadily grows until the process runs out of memory.
:::

:::question intermediate
Why is `buf = realloc(buf, bigger_size);` considered unsafe?
:::answer
If `realloc` fails it returns `NULL` but leaves the original block allocated. Assigning the result straight to `buf` overwrites the only pointer to that block, so it leaks and the data is lost. Assign to a temporary, check it, and only then update `buf`.
:::

:::question intermediate
After `free(p);`, the code later runs `if (p != NULL) printf("%d", *p);`. What is wrong, and what habit prevents it?
:::answer
Freeing does not change `p`, so it still holds the old address and the check passes; dereferencing it is a use-after-free, which is undefined behaviour. Setting `p = NULL;` immediately after `free(p)` makes the check work and turns accidental uses into clear failures.
:::

:::question advanced
A dynamic array grows by adding 10 slots each time it is full, instead of doubling. What is the total copying cost of appending $n$ items, and why is doubling better?
:::answer
With a fixed increment of 10, a reallocation happens every 10 appends and may copy all existing items, so the total copying is about $10 + 20 + 30 + \dots + n \approx n^2/20$, which is $O(n^2)$. With doubling, the copies total $1 + 2 + 4 + \dots + n < 2n$, which is $O(n)$, so each append costs $O(1)$ amortized.
:::

## Further learning

- **Next:** *Linked Data Structures in C* uses `malloc` and `free` to build lists and stacks.
- **Related:** *Amortized Analysis* in Data Structures & Algorithms proves why doubling gives constant amortized cost.
