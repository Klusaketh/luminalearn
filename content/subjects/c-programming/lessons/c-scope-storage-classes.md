---
lesson: c-scope-storage-classes
title: Scope, Linkage & Storage Classes
summary: Where a C identifier can be used (scope), whether it is shared across files (linkage), and how long its object exists (storage duration), with the auto, static, extern, and register keywords.
minutes: 40
type: theory
objectives:
  - Distinguish block scope and file scope, and predict which declaration a name refers to when names are shadowed
  - Explain automatic, static, and allocated storage duration and use static local variables correctly
  - Use extern and static at file level to share or hide variables and functions across source files
review: ai-draft
---
## Introduction

Every name in a C program raises three questions. **Scope:** in which part of the source code can I use this name? **Linkage:** if another file declares the same name, is it the same object? **Storage duration:** when is memory for this object created and destroyed? The keywords `static` and `extern` answer different questions in different places, which makes this topic confusing until the three ideas are separated.

**Before you start:** you should know how to write functions and how separate source files are compiled and linked.

## Core theory

### Scope

- **Block scope:** a name declared inside braces, including function parameters, is visible from its declaration to the end of that block.
- **File scope:** a name declared outside all functions is visible from its declaration to the end of the source file.

An inner declaration can **shadow** an outer one with the same name: inside the inner block, the name refers to the inner object. Shadowing is legal but makes code hard to read; compilers warn about it with `-Wshadow`.

### Storage duration

- **Automatic:** local variables without `static` are created when their block is entered and destroyed when it ends. They are **not** initialised automatically, so reading one before assigning it gives an indeterminate value. The rarely used keyword `auto` names this default.
- **Static:** objects declared at file scope, or declared `static` inside a function, exist for the entire run of the program. They are initialised once, before `main` starts, to zero if no initialiser is given.
- **Allocated:** memory from `malloc` lives until `free` is called.

A **static local variable** keeps its value between calls while remaining visible only inside its function, which makes it ideal for counters and caches.

### Linkage

- **External linkage:** a file-scope function or variable is, by default, visible to the linker, so other files can use it by declaring it with `extern`. `extern int count;` declares without defining; exactly one file must contain the definition `int count = 0;`.
- **Internal linkage:** `static` on a **file-scope** declaration hides it from other files. Use it for helper functions and private state, like making them private to a module.
- **No linkage:** local variables and parameters.

So `static` means "lives for the whole program" inside a function, but "private to this file" at file scope.

### register and const

`register` asks the compiler to keep a variable in a register and forbids taking its address; modern compilers allocate registers better than people, so it is rarely used. `const` is a type qualifier, not a storage class: it makes an object read-only.

## Worked examples

### Example 1: Static locals, automatic locals, and shadowing

```c
#include <stdio.h>

int calls = 100;

int next_id(void) {
    static int id = 0;
    int temp = 0;
    id++;
    temp++;
    printf("id=%d temp=%d\n", id, temp);
    return id;
}

int main(void) {
    next_id();
    next_id();
    next_id();
    int calls = 3;
    {
        int calls = 7;
        printf("inner calls = %d\n", calls);
    }
    printf("main calls = %d\n", calls);
    return 0;
}
```

Output:

```text
id=1 temp=1
id=2 temp=1
id=3 temp=1
inner calls = 7
main calls = 3
```

`id` is created once and remembers its value; `temp` is recreated, and set to 0, on each call. Inside `main`, the local `calls` shadows the global, and the block's `calls` shadows both.

### Example 2: Sharing and hiding across files

Consider a two-file program.

`counter.c`:

```c
static int total = 0;          /* internal linkage: private to this file */
int limit = 10;                /* external linkage: shared */

static void log_change(void) { /* helper hidden from other files */ }

void add(int n) {
    if (total + n <= limit) total += n;
    log_change();
}

int get_total(void) { return total; }
```

`main.c`:

```c
extern int limit;              /* declaration: defined in counter.c */
void add(int n);
int get_total(void);

int main(void) {
    limit = 15;
    add(9); add(9);
    return get_total();        /* 9: the second add would exceed 15 */
}
```

`main.c` can change `limit` because it has external linkage. It cannot touch `total` or call `log_change`: both are `static` at file scope, so a reference to them from `main.c` produces an undefined-reference error at link time. This is how C programs keep module state private.

## Applications

- **Encapsulation in C:** file-level `static` functions and variables form a module's private implementation.
- **Counters and caches:** static locals remember state between calls.
- **Configuration:** a global defined in one file and declared `extern` in a header is shared across a program.
- **Embedded systems:** static storage avoids dynamic allocation in memory-constrained devices.

## Common mistakes

- **Defining a global in a header.** Every file that includes it defines the variable, and linking fails with multiple definitions; put `extern` in the header and the definition in one `.c` file.
- **Reading uninitialised automatic variables.** Their value is indeterminate; initialise every local.
- **Assuming `static` means the same everywhere.** Inside functions it changes lifetime; at file scope it changes linkage.
- **Shadowing by accident.** Turn on `-Wshadow` to catch it.

## Revision notes

- Scope: block (inside braces) or file (outside functions).
- Automatic locals are created per call and are uninitialised; static objects live for the whole run and start at zero.
- `static` local: keeps its value between calls.
- `static` at file scope: internal linkage, private to the file.
- `extern`: declares an object defined elsewhere; define it exactly once.
- `register` forbids `&`; `const` means read-only.

## Practice questions

:::question basic
What value does an uninitialised `static int x;` inside a function start with, and what about an uninitialised `int y;`?
:::answer
`x` starts at 0, because objects with static storage duration are zero-initialised before the program runs. `y` is an automatic variable, so its initial value is indeterminate and must not be read before assignment.
:::

:::question basic
What does `static` do to a function defined at file scope?
:::answer
It gives the function internal linkage, so it can be called only from within the same source file. Other files cannot reference it, even with a prototype.
:::

:::question intermediate
Two files both contain `int count = 0;` at file scope. What happens when you link them, and how do you fix it?
:::answer
The linker reports a multiple definition of `count`, because both files define an object with external linkage. Keep the definition in one file and write `extern int count;` (usually in a shared header) in the other, or make each `static` if they should be separate private variables.
:::

:::question intermediate
Write a function `int fresh_ticket(void)` that returns 1, 2, 3, and so on, on successive calls, without a global variable.
:::answer
`int fresh_ticket(void) { static int last = 0; return ++last; }`. The static local is initialised once and keeps its value between calls, while remaining invisible outside the function.
:::

:::question advanced
Explain the different meanings of `static` in `static int hits;` at file scope and `static int hits;` inside a function, in terms of scope, linkage, and storage duration.
:::answer
Both have static storage duration: they exist for the whole program and are zero-initialised. At file scope, `hits` has file scope and **internal** linkage, so any function in that file can use it but other files cannot. Inside a function, `hits` has block scope and **no** linkage, so only that function can use it. In both cases the value persists across function calls.
:::

## Further learning

- **Next:** *Array Memory Layout & Indexing* shows how arrays are stored in the memory regions described here.
- **Related:** *Preprocessor, Macros & Multi-File Programs* covers header files and how `extern` declarations are shared.
