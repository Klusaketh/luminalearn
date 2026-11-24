---
lesson: c-unions-enums-typedef
title: Unions, Enumerations & typedef
summary: Unions that let several members share the same storage, enumerations that give names to integer constants, typedef aliases, and the tagged-union pattern that combines them safely.
minutes: 40
type: theory
objectives:
  - Explain how a union's members overlap in memory and determine its size
  - Define enumerations and use them in switch statements to make code self-documenting
  - Use typedef to create clear type names and build a tagged union that records which member is valid
review: ai-draft
---
## Introduction

Structures place their members side by side. Sometimes you need the opposite: one storage area that holds **either** an integer **or** a floating-point value **or** a string, depending on the situation, such as a token in a parser or a value in a spreadsheet cell. C's **union** provides that. Two related tools make such code readable: **enumerations** give names to the possible cases, and **typedef** gives types short, meaningful names.

**Before you start:** you should know structures, `sizeof`, and `switch` statements.

## Core theory

### Unions

```c
union number {
    int i;
    float f;
    char bytes[4];
};
```

All members of a union start at the same address and **overlap**. A union is large enough for its largest member, rounded up for alignment. Writing one member and then reading another reinterprets the same bytes; for anything other than inspecting raw bytes, read only the member you last wrote. Unions save memory when only one of several alternatives is needed at a time.

### Enumerations

```c
enum color { RED, GREEN, BLUE };
```

An enumeration defines named integer constants. By default the first is 0 and each next one is one more, so `RED` is 0, `GREEN` 1, and `BLUE` 2. You can assign values explicitly: `enum http { OK = 200, NOT_FOUND = 404 };`, and later names continue counting from the last explicit value. Enumerations make code self-documenting (`if (state == RUNNING)` instead of `if (state == 2)`) and work naturally with `switch`; compilers can even warn when a `switch` misses an enumeration value. In C, enumeration values are plain integers, so the compiler does not stop you from storing other numbers in an enum variable.

### typedef

`typedef` creates an **alias** for an existing type; it does not create a new type:

```c
typedef unsigned char byte;
typedef struct { double x, y; } Point;
```

Now `byte b;` and `Point p;` work without the `struct` keyword. Aliases clarify intent (`size_t`, `uint32_t`, and `FILE` are all typedefs from the standard library) and simplify complicated declarations such as function pointers: `typedef int (*compare_fn)(const void *, const void *);`.

### Tagged unions

Because a union does not remember which member is valid, it is usually wrapped in a structure with an enumeration **tag**:

```c
typedef enum { INT_VAL, REAL_VAL, TEXT_VAL } Kind;
typedef struct {
    Kind kind;
    union { int i; double r; char text[16]; } as;
} Value;
```

Code checks `kind` before reading the union, typically with a `switch`. This **tagged union** (also called a variant or sum type) is how interpreters, JSON libraries, and message protocols represent "one of several types" in C.

## Worked examples

### Example 1: Union size and overlapping storage

```c
#include <stdio.h>
#include <string.h>

union data {
    int i;
    double d;
    char text[12];
};

int main(void) {
    union data u;
    printf("sizeof union = %zu\n", sizeof u);
    u.i = 42;
    printf("i = %d\n", u.i);
    strcpy(u.text, "hello");
    printf("text = %s\n", u.text);
    u.d = 2.5;
    printf("d = %.1f\n", u.d);
    union { unsigned int whole; unsigned char part[4]; } w = { .whole = 0x01020304u };
    printf("lowest-address byte: %u\n", (unsigned)w.part[0]);
    return 0;
}
```

Output:

```text
sizeof union = 16
i = 42
text = hello
d = 2.5
lowest-address byte: 4
```

On typical systems the union is 16 bytes: the largest member, `text`, needs 12, rounded up to a multiple of 8 for the `double`. Each assignment overwrites the previous member. The last line shows the machine's byte order: on little-endian processors such as x86 and most ARM systems, the lowest address holds the least significant byte, 4.

### Example 2: A tagged union with an enum and typedef

```c
#include <stdio.h>
#include <string.h>

typedef enum { INT_VAL, REAL_VAL, TEXT_VAL } Kind;

typedef struct {
    Kind kind;
    union { int i; double r; char text[16]; } as;
} Value;

void print_value(const Value *v) {
    switch (v->kind) {
        case INT_VAL:  printf("int %d\n", v->as.i); break;
        case REAL_VAL: printf("real %.3f\n", v->as.r); break;
        case TEXT_VAL: printf("text \"%s\"\n", v->as.text); break;
    }
}

int main(void) {
    Value cells[3];
    cells[0].kind = INT_VAL;  cells[0].as.i = 7;
    cells[1].kind = REAL_VAL; cells[1].as.r = 3.14159;
    cells[2].kind = TEXT_VAL; strcpy(cells[2].as.text, "total");
    for (int k = 0; k < 3; k++) print_value(&cells[k]);
    printf("REAL_VAL = %d\n", REAL_VAL);
    return 0;
}
```

Output:

```text
int 7
real 3.142
text "total"
REAL_VAL = 1
```

The tag records which member is valid, and the `switch` reads only that member. The enumeration constants are ordinary integers, 0, 1, and 2.

## Applications

- **Interpreters and spreadsheets:** values that can be numbers, strings, or booleans are tagged unions.
- **Network protocols:** a message header's type field selects which union member describes the body.
- **State machines:** enumerations name states and events.
- **Portable code:** typedefs such as `uint32_t` hide platform-specific type choices.

## Common mistakes

- **Reading a union member other than the last one written.** Track the active member with a tag.
- **Assuming enum variables are type-checked.** C allows any integer; validate input values.
- **Thinking typedef creates a distinct type.** It is only an alias; the compiler treats both names as the same type.
- **Forgetting that a union is as large as its largest member.** A union with a 1 KB array member is 1 KB even when it holds an `int`.

## Revision notes

- Union members share storage; size is the largest member, aligned.
- Enumerations name integer constants, counting from 0 by default.
- `typedef existing_type NewName;` makes an alias.
- Tagged union = struct { enum tag; union { ... } }.
- Use `switch` on the tag; read only the active member.
- Byte order shows when a union reinterprets an integer's bytes.

## Practice questions

:::question basic
What is the size of `union { char c; int i; double d; }` on a typical 64-bit system, and why?
:::answer
It is 8 bytes. All members overlap starting at the same address, so the union needs only enough space for its largest member, the 8-byte `double`, which also sets its alignment.
:::

:::question basic
In `enum level { LOW, MEDIUM = 5, HIGH };`, what are the values of `LOW` and `HIGH`?
:::answer
`LOW` is 0 because the first constant defaults to 0. `MEDIUM` is set to 5, and `HIGH` continues from it, so `HIGH` is 6.
:::

:::question intermediate
What does `typedef struct node Node;` allow you to write, and does it create a new type?
:::answer
It lets you write `Node` instead of `struct node` in declarations, such as `Node *head;`. It does not create a new type: `Node` and `struct node` are two names for the same type.
:::

:::question intermediate
Why is a tag field needed when storing different kinds of values in a union?
:::answer
A union does not record which member was last written, and reading a different member reinterprets the bytes as the wrong type. The tag stores which member is valid, so code can check it, typically with a `switch`, before reading.
:::

:::question advanced
Design a tagged union `Shape` for circles (radius), rectangles (width, height), and triangles (three sides), and write the area calculation for each case.
:::answer
`typedef enum { CIRCLE, RECT, TRIANGLE } ShapeKind; typedef struct { ShapeKind kind; union { double r; struct { double w, h; } rect; struct { double a, b, c; } tri; } as; } Shape;`. In `area`, switch on `kind`: a circle returns $\pi r^2$; a rectangle returns $w \times h$; a triangle uses Heron's formula with $s = (a + b + c)/2$ and area $\sqrt{s(s - a)(s - b)(s - c)}$.
:::

## Further learning

- **Next:** *Heap Allocation & Memory Leaks* shows how to allocate structures and unions dynamically.
- **Related:** *Struct Alignment & Member Access* explains the alignment rules that set a union's size.
