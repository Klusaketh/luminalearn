---
lesson: c-pointers-address-arithmetic
title: Pointers & Address Arithmetic
summary: What pointers are, how the & and * operators work, how pointer arithmetic moves by whole elements, and how void pointers, NULL, and const pointers are used safely.
minutes: 50
type: theory
objectives:
  - Declare pointers, take addresses with &, and read or write through pointers with *
  - Perform pointer arithmetic and comparisons within an array and compute distances between pointers
  - Use NULL, void pointers, pointers to pointers, and const-qualified pointers correctly
review: ai-draft
---
## Introduction

A **pointer** is a variable that holds a memory address. Pointers are what make C both powerful and dangerous: they let functions modify their callers' data, let programs build linked structures and manage memory by hand, and let code walk through arrays efficiently. They also cause most of C's crashes when misused. This lesson builds an exact mental model of pointers so you can use them with confidence.

**Before you start:** you should know variables, arrays, functions, and pass-by-value.

## Core theory

### Addresses, & and *

Every object occupies memory at some address. The **address-of** operator `&x` gives that address, and a pointer variable stores it:

```c
int x = 10;
int *p = &x;   /* p points to x */
*p = 20;       /* x is now 20 */
```

The declaration `int *p` reads "`*p` is an `int`", so `p` is a pointer to `int`. In an expression, the **dereference** operator `*p` refers to the object `p` points to; you can read it or assign to it. The pointer's type tells the compiler how to interpret the bytes at that address and how far pointer arithmetic moves.

### NULL and invalid pointers

`NULL` is a pointer value that points to no object. Functions return it to signal "not found" or "allocation failed", and you must check for it before dereferencing. Dereferencing `NULL`, an uninitialised pointer, or a pointer to an object whose lifetime has ended is undefined behaviour, typically a segmentation fault. Initialise every pointer, either to a valid address or to `NULL`.

### Pointer arithmetic

If `p` points to an element of an array, `p + k` points `k` **elements** further on, not `k` bytes: the compiler multiplies by `sizeof(*p)`. So for `int *p`, `p + 1` is 4 bytes higher on a system with 4-byte `int`s. Rules:

- `p++` and `p--` step one element.
- Subtracting two pointers into the same array gives the number of elements between them, of type `ptrdiff_t` (printed with `%td`).
- Comparing pointers with `<` is meaningful only within the same array (or one past its end).
- Arithmetic that goes outside the array, other than to one past its end, is undefined.

Because `a[i]` is defined as `*(a + i)`, array indexing and pointer arithmetic are two notations for the same operation.

### void pointers, pointers to pointers, and const

A `void *` holds the address of any object type but cannot be dereferenced or used in arithmetic until converted to a specific pointer type. `malloc` returns `void *`, and generic functions such as `qsort` take `void *` arguments.

A **pointer to a pointer**, `int **pp`, stores the address of a pointer. It lets a function change a caller's pointer, for example to allocate memory for it, and it represents arrays of strings (`char **argv`).

`const` placement matters:

| Declaration | Meaning |
| :--- | :--- |
| `const int *p` | cannot change the `int` through `p`; `p` itself can move |
| `int *const p` | `p` always points to the same place; the `int` can change |
| `const int *const p` | neither can change |

Mark pointer parameters `const` when the function only reads the data.

## Worked examples

### Example 1: Basic pointer operations

```c
#include <stdio.h>

int main(void) {
    int x = 10, y = 3;
    int *p = &x;
    *p += 5;
    printf("x=%d *p=%d\n", x, *p);
    p = &y;
    *p = *p * 2;
    printf("x=%d y=%d\n", x, y);
    int **pp = &p;
    **pp = 100;
    printf("y=%d\n", y);
    int *none = NULL;
    printf("%s\n", none == NULL ? "none is NULL, do not dereference" : "valid");
    return 0;
}
```

Output:

```text
x=15 *p=15
x=15 y=6
y=100
none is NULL, do not dereference
```

`p` first points to `x`, then is redirected to `y`. Through `pp`, `**pp` reaches `y` in two steps: `*pp` is `p`, and `*p` is `y`.

### Example 2: Walking an array with pointers

```c
#include <stdio.h>

int sum(const int *begin, const int *end) {
    int total = 0;
    for (const int *p = begin; p != end; p++) total += *p;
    return total;
}

void reverse(int *a, int n) {
    int *lo = a, *hi = a + n - 1;
    while (lo < hi) {
        int t = *lo; *lo = *hi; *hi = t;
        lo++; hi--;
    }
}

int main(void) {
    int a[] = {4, 8, 15, 16, 23, 42};
    int n = sizeof a / sizeof a[0];
    printf("sum=%d\n", sum(a, a + n));
    int *mid = a + 3;
    printf("*mid=%d mid-a=%td bytes=%td\n", *mid, mid - a, (char *)mid - (char *)a);
    reverse(a, n);
    for (int *p = a; p < a + n; p++) printf("%d ", *p);
    printf("\n");
    return 0;
}
```

Output:

```text
sum=108
*mid=16 mid-a=3 bytes=12
42 23 16 15 8 4
```

`a + n` points one past the last element, a legal position to compare against but never to dereference. `mid - a` counts elements (3), while the difference of `char *` pointers counts bytes (12).

## Applications

- **Output parameters:** functions return extra results through pointer arguments.
- **Dynamic data structures:** linked lists and trees connect nodes with pointers.
- **Generic code:** `qsort` and `bsearch` work on any type through `void *`.
- **Performance:** passing a pointer to a large struct avoids copying it.

## Common mistakes

- **Dereferencing an uninitialised or NULL pointer.** Initialise pointers and check for `NULL`.
- **Confusing `*p++` and `(*p)++`.** `*p++` reads the value and moves the pointer; `(*p)++` increments the value.
- **Pointer arithmetic in bytes.** `p + 1` moves one element; cast to `char *` only when you truly need bytes.
- **Returning pointers to local variables.** The object dies when the function returns.

## Revision notes

- `&x` takes an address; `*p` dereferences.
- `int *p` declares a pointer to `int`; always initialise it.
- `p + k` moves `k` elements; `q - p` counts elements (`%td`).
- `a[i]` equals `*(a + i)`; one-past-the-end may be formed, never dereferenced.
- `void *` is generic; convert before dereferencing.
- `const int *p`: read-only data; `int *const p`: fixed pointer.

## Practice questions

:::question basic
After `int a = 5; int *p = &a; *p = 9;`, what is the value of `a`?
:::answer
`a` is 9. `p` holds the address of `a`, so assigning to `*p` writes into `a` itself.
:::

:::question basic
If `double *q` holds address 2000 and `sizeof(double)` is 8, what address does `q + 3` hold?
:::answer
2024. Pointer arithmetic moves in whole elements, so `q + 3` is $2000 + 3 \times 8$.
:::

:::question intermediate
What is the difference between `const char *s` and `char *const s`?
:::answer
With `const char *s`, the characters cannot be modified through `s`, but `s` can be pointed elsewhere. With `char *const s`, the pointer itself cannot change, but the characters it points to can be modified.
:::

:::question intermediate
Write a function that sets a caller's `int *` to `NULL`. Why does it need a pointer to a pointer?
:::answer
`void clear(int **pp) { *pp = NULL; }`, called as `clear(&ptr);`. Arguments are passed by value, so a function receiving `int *` gets a copy of the pointer and cannot change the caller's variable; receiving its address lets the function write the new pointer value into it.
:::

:::question advanced
Given `int a[5]; int *p = a + 5;`, which of these are valid: computing `p`, evaluating `p == a + 5`, evaluating `*p`, computing `p + 1`? Explain.
:::answer
Computing `p` and comparing it with `a + 5` are valid: C allows a pointer one past the end of an array and comparisons with it. Evaluating `*p` is undefined because there is no element there. Computing `p + 1` is also undefined, since it goes beyond the one-past-the-end position, even if it is never dereferenced.
:::

## Further learning

- **Next:** *Struct Alignment & Member Access* uses pointers to structures with the `->` operator.
- **Related:** *Heap Allocation & Memory Leaks* combines pointers with dynamic memory.
