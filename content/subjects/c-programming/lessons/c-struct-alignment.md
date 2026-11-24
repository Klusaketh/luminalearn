---
lesson: c-struct-alignment
title: Struct Alignment & Member Access
summary: Defining and using structures in C, accessing members with the dot and arrow operators, and how alignment rules insert padding that affects a structure's size and layout.
minutes: 40
type: theory
objectives:
  - Define structures, initialise them, and access members with . and -> correctly
  - Predict the size and member offsets of a structure from alignment rules, and reduce padding by reordering members
  - Pass structures to functions by value or by pointer and choose between the two
review: ai-draft
---
## Introduction

Real data has several parts: a student has a name, a roll number, and a grade; a point has an x and a y coordinate. A **structure** (`struct`) groups such related values into one type. Structures are the foundation of every data structure in C, from linked lists to file headers. Their layout in memory is not always the simple sum of their members, because of **alignment** and **padding**, and understanding that layout matters for memory use, file formats, and network protocols.

**Before you start:** you should know C types, `sizeof`, arrays, and pointers.

## Core theory

### Defining and using structures

```c
struct student {
    char name[20];
    int roll;
    double gpa;
};

struct student s = {"Asha", 17, 8.9};
s.roll = 18;
```

A structure type is declared once; variables of that type each have their own members. Members are accessed with the **dot operator** `s.roll`. Designated initialisers, `{.roll = 17, .gpa = 8.9}`, name the members being set, and unnamed members become zero. Structures can be assigned (`t = s;` copies every member) but not compared with `==`; compare members individually.

### Pointers to structures and the arrow operator

For a pointer `struct student *p = &s;`, the member is `(*p).roll`. Because that is awkward, C provides the **arrow operator**: `p->roll`. The parentheses matter, since `.` binds tighter than `*`, so `*p.roll` would be wrong.

### Passing structures to functions

A structure argument is passed **by value**: the whole structure is copied. That is safe but costs time for large structures, and changes inside the function do not affect the caller. Passing a pointer (`const struct student *` when only reading) avoids the copy and allows modification.

### Alignment and padding

Processors read memory most efficiently when an object of size $k$ starts at an address that is a multiple of its **alignment**, typically its size for basic types: `char` 1, `short` 2, `int` 4, `double` 8. To satisfy this for every member, the compiler inserts unused **padding** bytes between members, and adds **tail padding** so that the structure's size is a multiple of its largest member alignment, which keeps every element aligned in an array of structures.

On typical desktop and server systems:

| Layout | Members (offset) | sizeof |
| :--- | :--- | :--- |
| `char a; int b; char c;` | a 0, pad 1-3, b 4, c 8, pad 9-11 | 12 |
| `int b; char a; char c;` | b 0, a 4, c 5, pad 6-7 | 8 |
| `char a; double d;` | a 0, pad 1-7, d 8 | 16 |

Ordering members from largest to smallest alignment usually minimises padding. The `offsetof(type, member)` macro from `<stddef.h>` gives a member's offset. Because padding varies between compilers and platforms, never write a structure's raw bytes to a file or network and expect another system to read them correctly; serialise each field explicitly.

## Worked examples

### Example 1: Members, arrow operator, and passing by pointer

```c
#include <stdio.h>
#include <string.h>

struct student {
    char name[20];
    int roll;
    double gpa;
};

void promote(struct student *p, double bonus) {
    p->gpa += bonus;
    if (p->gpa > 10.0) p->gpa = 10.0;
}

void show(const struct student *p) {
    printf("%-6s roll=%d gpa=%.1f\n", p->name, p->roll, p->gpa);
}

int main(void) {
    struct student a = {"Asha", 17, 8.9};
    struct student b = {.roll = 21, .gpa = 9.6};
    strcpy(b.name, "Ravi");
    struct student copy = a;
    promote(&a, 0.5);
    promote(&b, 0.5);
    show(&a);
    show(&b);
    show(&copy);
    return 0;
}
```

Output:

```text
Asha   roll=17 gpa=9.4
Ravi   roll=21 gpa=10.0
Asha   roll=17 gpa=8.9
```

`copy` was made before the promotion, so struct assignment produced an independent copy. `promote` changes the caller's structures because it receives their addresses.

### Example 2: Measuring padding

```c
#include <stdio.h>
#include <stddef.h>

struct loose { char a; int b; char c; };
struct tight { int b; char a; char c; };
struct mixed { char tag; double value; short code; };

int main(void) {
    printf("loose: size %zu, b at %zu, c at %zu\n", sizeof(struct loose), offsetof(struct loose, b), offsetof(struct loose, c));
    printf("tight: size %zu, a at %zu, c at %zu\n", sizeof(struct tight), offsetof(struct tight, a), offsetof(struct tight, c));
    printf("mixed: size %zu, value at %zu, code at %zu\n", sizeof(struct mixed), offsetof(struct mixed, value), offsetof(struct mixed, code));
    struct loose arr[100];
    printf("100 loose structs: %zu bytes\n", sizeof arr);
    return 0;
}
```

Output:

```text
loose: size 12, b at 4, c at 8
tight: size 8, a at 4, c at 5
mixed: size 24, value at 8, code at 16
100 loose structs: 1200 bytes
```

The same three members take 12 or 8 bytes depending on order. In `mixed`, the `double` forces 8-byte alignment, so the structure is padded to 24 bytes although its members need only 11. These figures are for typical 64-bit systems; the rules are the same everywhere, but sizes can differ on unusual platforms.

## Applications

- **Records:** database rows, game entities, and configuration settings are structures.
- **Linked data structures:** nodes are structures holding data and pointers.
- **Systems interfaces:** operating-system calls such as `stat` fill structures for you.
- **Memory optimisation:** reordering members shrinks large arrays of structures.

## Common mistakes

- **Using `.` on a pointer.** Use `p->member` or `(*p).member`.
- **Comparing structures with `==`.** It is not allowed; compare members.
- **Assuming `sizeof` equals the sum of members.** Padding usually makes it larger.
- **Writing raw structures to files for other systems.** Layout and byte order may differ; serialise fields.

## Revision notes

- `struct name { members };` defines a type; `s.member` accesses a member.
- `p->member` is `(*p).member`.
- Assignment copies the whole structure; `==` is not defined for structures.
- Members are aligned to multiples of their alignment; padding fills the gaps.
- `sizeof` is a multiple of the largest member alignment.
- Order members from largest to smallest alignment; use `offsetof` to check.

## Practice questions

:::question basic
Given `struct point *p`, write two equivalent ways to read its `x` member.
:::answer
`p->x` and `(*p).x`. The parentheses are needed in the second form because the dot operator binds more tightly than the dereference operator.
:::

:::question basic
Why might `sizeof(struct { char c; int i; })` be 8 rather than 5?
:::answer
The `int` must start at a multiple of 4 on typical systems, so the compiler places 3 padding bytes after the `char`. The structure then occupies 4 + 4 = 8 bytes.
:::

:::question intermediate
Reorder `struct r { char a; double b; char c; int d; };` to reduce its size, and give the sizes before and after on a typical 64-bit system.
:::answer
Before: `a` at 0, padding to 8, `b` at 8, `c` at 16, padding to 20, `d` at 20, giving 24 bytes. Ordering by alignment, `struct r { double b; int d; char a; char c; };`, puts `b` at 0, `d` at 8, `a` at 12, `c` at 13, plus 2 bytes of tail padding: 16 bytes.
:::

:::question intermediate
When should a function take `const struct big *p` rather than `struct big b`?
:::answer
When the structure is large and the function only reads it. Passing a pointer avoids copying the whole structure on every call, and `const` documents and enforces that the function will not modify the caller's data.
:::

:::question advanced
Why is `fwrite(&rec, sizeof rec, 1, f)` an unreliable way to save records that another program on a different machine will read?
:::answer
The bytes include compiler-chosen padding, whose amount and position can differ between compilers and platforms, and multi-byte numbers are stored in the machine's byte order (endianness), which may differ too. Another program may therefore misread every field. A portable format writes each field explicitly in a defined size and byte order, or uses text such as CSV or JSON.
:::

## Further learning

- **Next:** *Unions, Enumerations & typedef* introduces types that share storage and named constants.
- **Related:** *Linked Data Structures in C* builds lists from structures connected by pointers.
