---
lesson: c-array-memory-layout
title: Array Memory Layout & Indexing
summary: How C arrays occupy one contiguous block of memory, how indexing is address arithmetic on the base address, how two-dimensional arrays are stored in row-major order, and why arrays decay to pointers.
minutes: 35
type: theory
objectives:
  - Compute the address of an array element from the base address, index, and element size
  - Compute row-major offsets for two-dimensional arrays and traverse them efficiently
  - Explain array-to-pointer decay, its effect on sizeof, and how to pass arrays to functions safely
review: ai-draft
---
## Introduction

An array is the simplest data structure in C and the one closest to the hardware: a row of equally sized elements placed side by side in memory. Because the layout is so regular, the address of any element can be computed in one multiplication and one addition, which is why array access takes constant time. This lesson explains that address arithmetic, the row-major layout of multi-dimensional arrays, and the decay rule that makes arrays behave like pointers.

**Before you start:** you should know C's basic types, `sizeof`, loops, and functions.

## Core theory

### One contiguous block

`int a[5];` reserves `5 * sizeof(int)` bytes, usually 20, in one block. Elements are numbered from 0, and element `i` sits at

$$\text{address}(a[i]) = \text{base} + i \times \text{sizeof(element)}$$

where the base is the address of `a[0]`. This formula is why indexing is $O(1)$ and why indices start at 0: the index is an offset from the base. C performs **no bounds checking**: `a[5]` or `a[-1]` computes an address outside the array, and using it is undefined behaviour.

An array can be initialised with a brace list: `int a[5] = {1, 2};` sets the rest to 0, and `int b[] = {4, 5, 6};` lets the compiler count three elements. The number of elements is `sizeof a / sizeof a[0]`, which works only where `a` is a real array, not a pointer.

### Two-dimensional arrays: row-major order

`int m[3][4];` is an array of 3 rows, each an array of 4 `int`s. C stores it in **row-major order**: all of row 0, then all of row 1, then row 2. The element `m[i][j]` is at offset

$$(i \times \text{COLS} + j) \times \text{sizeof(element)}$$

from the start. Consequently, a loop that walks along a row (inner loop over `j`) visits consecutive memory addresses, which is far friendlier to the CPU cache than walking down columns. When a 2-D array is passed to a function, every dimension except the first must be given, as in `void print(int m[][4], int rows)`, because the compiler needs `COLS` to compute offsets.

### Array-to-pointer decay

In most expressions, the name of an array is converted to a pointer to its first element. Indexing is defined in terms of pointers: `a[i]` means `*(a + i)`. When you pass an array to a function, the function receives only this pointer, so inside the function `sizeof` gives the size of a pointer, not of the array, and the length must be passed separately. The exceptions are `sizeof a` and `&a`, where the array does not decay.

### Variable-length and dynamic arrays

The size of an ordinary array must be known when it is created. C99 added variable-length arrays (`int v[n];`), but they live on the stack and can overflow it with large `n`; for large or long-lived arrays, use `malloc`.

## Worked examples

### Example 1: Address arithmetic on a 1-D array

```c
#include <stdio.h>

int main(void) {
    int a[5] = {10, 20, 30};
    size_t count = sizeof a / sizeof a[0];
    printf("count=%zu bytes=%zu\n", count, sizeof a);
    for (size_t i = 0; i < count; i++) printf("%d ", a[i]);
    printf("\n");
    int *p = a;
    printf("%d %d %d\n", *(p + 1), p[2], *(a + 4));
    printf("offset of a[3] in bytes: %td\n", (char *)&a[3] - (char *)&a[0]);
    printf("elements between a[1] and a[4]: %td\n", &a[4] - &a[1]);
    return 0;
}
```

Output:

```text
count=5 bytes=20
10 20 30 0 0
20 30 0
offset of a[3] in bytes: 12
elements between a[1] and a[4]: 3
```

The unlisted elements are zero. `a[3]` is 12 bytes from the base because each `int` takes 4 bytes. Subtracting two element pointers gives a distance in elements, not bytes.

### Example 2: Row-major layout of a 2-D array

```c
#include <stdio.h>

#define ROWS 3
#define COLS 4

int sum_row(int m[][COLS], int row) {
    int s = 0;
    for (int j = 0; j < COLS; j++) s += m[row][j];
    return s;
}

int main(void) {
    int m[ROWS][COLS];
    for (int i = 0; i < ROWS; i++)
        for (int j = 0; j < COLS; j++)
            m[i][j] = i * 10 + j;
    int *flat = &m[0][0];
    printf("m[2][1]=%d flat[2*COLS+1]=%d\n", m[2][1], flat[2 * COLS + 1]);
    printf("flat[5]=%d is m[1][1]\n", flat[5]);
    printf("row sums: %d %d %d\n", sum_row(m, 0), sum_row(m, 1), sum_row(m, 2));
    return 0;
}
```

Output:

```text
m[2][1]=21 flat[2*COLS+1]=21
flat[5]=11 is m[1][1]
row sums: 6 46 86
```

Viewing the 2-D array as one flat block shows the row-major rule directly: element `(i, j)` is at flat index $i \times 4 + j$, so flat index 5 is row 1, column 1.

## Applications

- **Images:** a grey-scale image is a 2-D array of pixels stored row by row.
- **Matrices:** numerical libraries rely on row-major (C) or column-major (Fortran) layouts for speed.
- **Buffers:** network and file data are read into byte arrays.
- **Lookup tables:** constant arrays give $O(1)$ answers indexed by a small integer.

## Common mistakes

- **Off-by-one bounds.** Valid indices are 0 to $n - 1$; `i <= n` reads one past the end.
- **Using `sizeof` on an array parameter.** It gives the pointer size; pass the length separately.
- **Iterating column-by-column over large 2-D arrays.** It works but wastes cache; loop over rows outside and columns inside.
- **Returning a local array from a function.** It disappears with the stack frame.

## Revision notes

- `&a[i] = base + i * sizeof(element)`; `a[i]` is `*(a + i)`.
- No bounds checking: out-of-range access is undefined behaviour.
- Element count: `sizeof a / sizeof a[0]` (only on a real array).
- Row-major: `m[i][j]` at offset `(i * COLS + j) * size`.
- Functions taking 2-D arrays need every dimension but the first.
- Arrays decay to pointers when passed; pass the length too.

## Practice questions

:::question basic
An `int` array starts at address 1000 and `int` is 4 bytes. At what address is `a[6]`?
:::answer
At $1000 + 6 \times 4 = 1024$. The address of element $i$ is the base address plus $i$ times the element size.
:::

:::question basic
Why does `void f(int a[]) { printf("%zu", sizeof a); }` not print the array's size?
:::answer
Inside the function, `a` is a pointer, because arrays decay to pointers when passed. `sizeof a` therefore gives the size of a pointer, typically 8 bytes on a 64-bit system, regardless of the array's length.
:::

:::question intermediate
For `double g[10][20];`, what is the byte offset of `g[3][7]` from `g[0][0]`, given 8-byte doubles?
:::answer
Row-major offset in elements is $3 \times 20 + 7 = 67$, so the byte offset is $67 \times 8 = 536$ bytes.
:::

:::question intermediate
Why does summing a large 2-D array row by row usually run faster than column by column?
:::answer
Row by row visits consecutive addresses, so each cache line loaded from memory supplies several useful elements and the hardware prefetcher can predict the next ones. Column by column jumps `COLS * size` bytes each step, touching a new cache line almost every time, which causes many more cache misses.
:::

:::question advanced
Explain why `a[i]`, `*(a + i)`, `*(i + a)`, and `i[a]` all access the same element.
:::answer
C defines `a[i]` as `*(a + i)`. Pointer addition is commutative, so `a + i` equals `i + a`, and therefore `*(i + a)`, which by the same definition is written `i[a]`, is the same element. The last form is legal but should never appear in real code.
:::

## Further learning

- **Next:** *Null-Terminated String Manipulation* treats strings as character arrays.
- **Related:** *Static vs Dynamic Arrays* in Data Structures & Algorithms compares fixed arrays with growable ones.
