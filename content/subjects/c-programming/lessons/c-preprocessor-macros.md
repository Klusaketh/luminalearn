---
lesson: c-preprocessor-macros
title: Preprocessor, Macros & Multi-File Programs
summary: What the C preprocessor does before compilation: #include, object-like and function-like macros, conditional compilation, header guards, and how header and source files divide a program into separately compiled modules.
minutes: 45
type: theory
objectives:
  - Write object-like and function-like macros safely, and recognise the pitfalls of textual substitution
  - Use conditional compilation and header guards to control what code is compiled
  - Split a program into headers and source files, and explain what belongs in each
review: ai-draft
---
## Introduction

Before the compiler sees your code, the **preprocessor** rewrites it. It copies header files in, replaces macro names with their definitions, and keeps or deletes blocks of code depending on conditions. These text-level tools are how C programs share declarations between files, adapt to different platforms, and switch debugging code on and off. Because the preprocessor knows nothing about C's types or syntax, its features must be used carefully.

**Before you start:** you should know how C programs are compiled and linked, and the meaning of `extern` and `static`.

## Core theory

### #include

`#include <stdio.h>` searches the system include directories; `#include "shapes.h"` searches the current file's directory first. Either way, the directive is replaced by the entire contents of the file. Headers therefore contain **declarations** that many files need: function prototypes, type definitions, macros, and `extern` variable declarations. **Definitions** of functions and variables belong in `.c` files; defining them in a header causes multiple-definition link errors once two files include it.

### Object-like macros

`#define MAX_STUDENTS 60` replaces every later occurrence of the token `MAX_STUDENTS` with `60`. Such constants have no type and no scope, and they do not exist in the debugger; `const` variables or enumerations are often better, but macros remain common for array sizes and configuration.

### Function-like macros and their pitfalls

`#define SQUARE(x) ((x) * (x))` looks like a function but is pure text substitution. Two rules prevent most bugs:

1. **Parenthesise every parameter and the whole body.** Without them, `#define BAD(x) x * x` turns `BAD(a + 1)` into `a + 1 * a + 1`.
2. **Never pass arguments with side effects.** `SQUARE(i++)` expands to `((i++) * (i++))`, which modifies `i` twice: undefined behaviour.

Multi-statement macros are wrapped in `do { ... } while (0)` so they behave as a single statement after `if`. The operator `#` turns a parameter into a string literal, and `##` pastes tokens together. Where possible, prefer `static inline` functions, which are type-checked and evaluate arguments once.

### Conditional compilation

```c
#ifdef DEBUG
    fprintf(stderr, "x = %d\n", x);
#endif
```

`#if`, `#ifdef`, `#ifndef`, `#elif`, `#else`, and `#endif` keep or drop code before compilation. Definitions can come from the command line: `gcc -DDEBUG main.c`. Typical uses are debug logging, platform-specific code (`#ifdef _WIN32`), and feature switches. Predefined macros such as `__FILE__`, `__LINE__`, and `__STDC_VERSION__` describe the build.

### Header guards

If a header is included twice in one translation unit, directly or through other headers, its type definitions are duplicated and compilation fails. A **header guard** prevents this:

```c
#ifndef SHAPES_H
#define SHAPES_H
/* declarations */
#endif
```

The first inclusion defines `SHAPES_H`; later inclusions find it defined and skip the contents. Many compilers also accept the non-standard `#pragma once`.

### Separate compilation

A module `shapes` has an interface, `shapes.h` (guarded, with prototypes and types), and an implementation, `shapes.c` (which includes its own header and defines the functions). Other files include `shapes.h`, each `.c` file is compiled separately, and the linker joins the object files: `gcc main.c shapes.c -o app`.

## Worked examples

### Example 1: Macro expansion pitfalls and fixes

```c
#include <stdio.h>

#define BAD_SQUARE(x) x * x
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define SHOW(expr) printf(#expr " = %d\n", (expr))

static inline int max_fn(int a, int b) { return a > b ? a : b; }

int main(void) {
    int a = 3;
    SHOW(BAD_SQUARE(a + 1));
    SHOW(SQUARE(a + 1));
    SHOW(100 / SQUARE(2));
    int i = 5, j = 5;
    int m1 = MAX(i++, 2);
    int m2 = max_fn(j++, 2);
    printf("macro: m=%d i=%d   function: m=%d j=%d\n", m1, i, m2, j);
    return 0;
}
```

Output:

```text
BAD_SQUARE(a + 1) = 7
SQUARE(a + 1) = 16
100 / SQUARE(2) = 25
macro: m=6 i=7   function: m=5 j=6
```

`BAD_SQUARE(a + 1)` becomes `a + 1 * a + 1`, which is 3 + 3 + 1 = 7. `MAX(i++, 2)` evaluates `i++` twice, once in the comparison and once to produce the result, so it returns 6 and leaves `i` at 7; the inline function evaluates its argument once. `#expr` turned each expression into the label text.

### Example 2: Conditional compilation and build information

```c
#include <stdio.h>

#define VERSION_MAJOR 2
#define VERSION_MINOR 1
#define STR(x) #x
#define XSTR(x) STR(x)
#define VERSION XSTR(VERSION_MAJOR) "." XSTR(VERSION_MINOR)

#ifndef LOG_LEVEL
#define LOG_LEVEL 1
#endif

#if LOG_LEVEL >= 2
#define LOG_DEBUG(msg) printf("[debug] %s\n", msg)
#else
#define LOG_DEBUG(msg) do { } while (0)
#endif

int main(void) {
    printf("app version %s\n", VERSION);
    LOG_DEBUG("this line is compiled only when LOG_LEVEL >= 2");
    printf("log level %d, C standard %ld\n", LOG_LEVEL, (long)__STDC_VERSION__);
    return 0;
}
```

Output:

```text
app version 2.1
log level 1, C standard 201112
```

The two-step `XSTR` macro expands `VERSION_MAJOR` to 2 before turning it into a string; a single `STR(VERSION_MAJOR)` would produce the text `"VERSION_MAJOR"`. Compiling with `-DLOG_LEVEL=2` would include the debug message. `201112` identifies the C11 standard.

## Applications

- **Portable libraries:** conditional compilation selects code for Windows, Linux, or microcontrollers.
- **Debug builds:** logging and assertions are compiled in only when needed.
- **Large projects:** guarded headers declare each module's interface.
- **Configuration:** `-D` flags set buffer sizes or features at build time.

## Common mistakes

- **Unparenthesised macro parameters.** Always wrap parameters and the whole body in parentheses.
- **Arguments with side effects.** `MAX(i++, j)` may increment `i` twice.
- **Defining variables or functions in headers.** Put definitions in one `.c` file.
- **Missing header guards.** Double inclusion redefines types and breaks compilation.
- **Ending a macro definition with a semicolon.** `#define N 10;` inserts the semicolon everywhere `N` is used.

## Revision notes

- The preprocessor performs text substitution before compilation.
- `#include <...>` for system headers, `"..."` for project headers.
- Function-like macros: parenthesise everything, avoid side-effect arguments, prefer `static inline`.
- `#` stringises a parameter; `##` pastes tokens; stringise a macro's value with a two-level macro.
- `#if`/`#ifdef`/`#ifndef` select code; `-DNAME=value` defines macros from the command line.
- Header guards: `#ifndef X_H` / `#define X_H` / ... / `#endif`.

## Practice questions

:::question basic
What does `#include "shapes.h"` do?
:::answer
The preprocessor replaces the directive with the full text of `shapes.h`, searching the current file's directory first. The compiler then sees the header's declarations as if they were written in the file.
:::

:::question basic
Why is `#define DOUBLE(x) ((x) + (x))` safer than `#define DOUBLE(x) x + x`?
:::answer
With the unparenthesised version, `3 * DOUBLE(2)` expands to `3 * 2 + 2`, which is 8 rather than 12. Parentheses around the body and each parameter keep the expansion grouped as intended, giving `3 * ((2) + (2))` = 12.
:::

:::question intermediate
What problem does a header guard solve? Write one for `stack.h`.
:::answer
It prevents the header's contents from being processed twice in one translation unit, which would redefine its types and fail to compile. `#ifndef STACK_H` / `#define STACK_H` / (declarations) / `#endif`.
:::

:::question intermediate
How would you include extra checking code only in debug builds, and how do you turn it on?
:::answer
Wrap the code in `#ifdef DEBUG` ... `#endif` and compile with `gcc -DDEBUG file.c` to define the macro. Without the flag, the preprocessor removes the code entirely, so release builds pay no cost.
:::

:::question advanced
A team puts `int counter = 0;` and the full definition of `void log_msg(const char *m) { ... }` in `util.h`, included by three `.c` files. Linking fails. Explain why and restructure the module.
:::answer
Each `.c` file that includes the header gets its own definition of `counter` and `log_msg`, so the linker sees three definitions of each external symbol and reports multiple definitions. Put declarations in the header, `extern int counter;` and `void log_msg(const char *m);`, inside a header guard, and put the single definitions in `util.c`, which is compiled and linked once.
:::

## Further learning

- **Next:** *Undefined Behavior & Common Bugs* explains why macros with side effects and other subtle code are dangerous.
- **Related:** *C Syntax & Compilation Stages* shows where preprocessing fits in the build pipeline.
