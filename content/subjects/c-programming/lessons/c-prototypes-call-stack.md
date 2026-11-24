---
lesson: c-prototypes-call-stack
title: Function Prototypes & Call Stack
summary: How C functions are declared and defined, how arguments are passed by value, and how the call stack creates a frame for every call, including recursive ones.
minutes: 35
type: theory
objectives:
  - Write function prototypes and definitions, and explain why the compiler needs a declaration before a call
  - Explain pass-by-value and use pointers when a function must change the caller's variables
  - Describe what a stack frame holds, trace a recursive call stack, and explain stack overflow
review: ai-draft
---
## Introduction

Functions let you name a piece of work, reuse it, and reason about it separately. In C, calling a function is a precise mechanical process: the arguments are copied, a new **stack frame** is created, the function runs, its return value is handed back, and the frame disappears. Understanding that process explains why a function cannot change your variables unless you pass their address, why recursion uses memory, and why returning a pointer to a local variable is a serious bug.

**Before you start:** you should know C types, expressions, loops, and how a program is compiled and linked.

## Core theory

### Declarations and definitions

A **definition** gives the function's body:

```c
double average(int total, int count) {
    return (double)total / count;
}
```

A **declaration** (prototype) gives only the interface: `double average(int total, int count);`. The compiler checks every call against the declaration: the number of arguments, their types (converting them where allowed), and the return type. A function must be declared before it is called, so programs either define helpers above `main` or put prototypes at the top or in a header file. A function with no parameters is declared `int f(void)`; in C, `int f()` historically meant "unspecified parameters".

### Pass by value

C always passes arguments **by value**: the parameter is a new local variable initialised with a copy of the argument. Changing the parameter changes only the copy. To let a function modify a caller's variable, pass its **address** and dereference it inside the function:

```c
void swap(int *a, int *b) {
    int t = *a; *a = *b; *b = t;
}
```

Arrays look like an exception, but they are not: an array argument decays to a pointer to its first element, so the pointer is copied and the function works on the caller's elements.

### The call stack

Each call creates a **stack frame** (activation record) on the **call stack**, a region of memory that grows and shrinks as functions are called and return. A frame typically holds:

- the function's parameters and local variables,
- the **return address**, where execution continues in the caller,
- saved registers, including the caller's frame pointer.

On common 64-bit systems the first few arguments travel in registers and the return value comes back in a register (`rax` on x86-64), but conceptually each call has its own frame. When the function returns, its frame is discarded, so its local variables no longer exist. Returning a pointer to a local variable therefore creates a **dangling pointer**.

### Recursion and stack overflow

A **recursive** function calls itself; every active call has its own frame with its own copy of the locals. A recursion needs a **base case** that stops it. The stack is limited (often 8 MB on Linux), so very deep recursion, or infinite recursion from a missing base case, exhausts it and the program crashes with a **stack overflow**, usually a segmentation fault. Each level of a recursion of depth $d$ uses one frame, so memory use is $O(d)$.

## Worked examples

### Example 1: Pass by value versus pass by address

```c
#include <stdio.h>

void try_double(int x) {
    x = x * 2;
}

void really_double(int *x) {
    *x = *x * 2;
}

void fill(int arr[], int n, int value) {
    for (int i = 0; i < n; i++) arr[i] = value;
}

int main(void) {
    int n = 5;
    try_double(n);
    printf("after try_double: %d\n", n);
    really_double(&n);
    printf("after really_double: %d\n", n);
    int a[3] = {0, 0, 0};
    fill(a, 3, 7);
    printf("%d %d %d\n", a[0], a[1], a[2]);
    return 0;
}
```

Output:

```text
after try_double: 5
after really_double: 10
7 7 7
```

`try_double` changes its private copy. `really_double` receives the address of `n` and writes through it. `fill` receives a pointer to the array's first element, so it changes the caller's array.

### Example 2: Tracing a recursive call stack

```c
#include <stdio.h>

int factorial(int n, int depth) {
    printf("%*scall factorial(%d)\n", depth * 2, "", n);
    if (n <= 1) {
        printf("%*sreturn 1\n", depth * 2, "");
        return 1;
    }
    int result = n * factorial(n - 1, depth + 1);
    printf("%*sreturn %d\n", depth * 2, "", result);
    return result;
}

int main(void) {
    printf("4! = %d\n", factorial(4, 0));
    return 0;
}
```

Output:

```text
call factorial(4)
  call factorial(3)
    call factorial(2)
      call factorial(1)
      return 1
    return 2
  return 6
return 24
4! = 24
```

Four frames are on the stack at the deepest point, each with its own `n`. The calls return in reverse order, last in, first out, which is why the structure is called a stack.

## Applications

- **Modular programs:** prototypes in header files let many source files call the same functions.
- **Output parameters:** functions such as `scanf` take addresses so they can store results in your variables.
- **Recursive algorithms:** tree traversals, quicksort, and parsers rely on the call stack.
- **Debugging:** a debugger's backtrace is a listing of the current stack frames.

## Common mistakes

- **Calling a function before it is declared.** Add a prototype or move the definition above the call.
- **Expecting a function to change a non-pointer argument.** Only the copy changes.
- **Returning the address of a local variable.** The frame is gone after the return; use a static, a caller-provided buffer, or heap memory.
- **Recursion without a reachable base case.** It recurses until the stack overflows.

## Revision notes

- Declare (prototype) before use; define exactly once.
- `int f(void)` takes no parameters.
- C passes arguments by value; pass `&x` and use `*p` to modify the caller's data.
- Arrays decay to pointers when passed.
- A stack frame holds parameters, locals, the return address, and saved registers.
- Locals vanish on return; deep or infinite recursion overflows the stack.

## Practice questions

:::question basic
What is the difference between a function declaration and a function definition?
:::answer
A declaration (prototype) states the function's name, parameter types, and return type so calls can be checked. A definition also supplies the body. A function may be declared many times but must be defined exactly once in the program.
:::

:::question basic
Why does `void inc(int x) { x++; }` not change the variable passed to it?
:::answer
C passes arguments by value, so `x` is a separate local copy of the argument. Incrementing it changes only the copy, which disappears when the function returns.
:::

:::question intermediate
Write a function that returns both the minimum and maximum of an array.
:::answer
Use output parameters: `void min_max(const int a[], int n, int *lo, int *hi) { *lo = *hi = a[0]; for (int i = 1; i < n; i++) { if (a[i] < *lo) *lo = a[i]; if (a[i] > *hi) *hi = a[i]; } }`. The caller passes `&lo` and `&hi`, and the function writes the results through the pointers.
:::

:::question intermediate
What is wrong with `int *make(void) { int x = 42; return &x; }`?
:::answer
`x` lives in `make`'s stack frame, which is discarded when the function returns, so the returned pointer refers to memory that no longer holds `x`. Using it is undefined behaviour. Return the value itself, use a `static` variable, or allocate with `malloc`.
:::

:::question advanced
A recursive function on a linked list of one million nodes crashes, but the iterative version works. Explain why, and estimate the memory involved.
:::answer
The recursive version uses one stack frame per node, so it needs a million frames at the deepest point. Even at a modest 48 bytes per frame that is about 48 MB, far more than a typical 8 MB stack, so the stack overflows and the program crashes. The loop reuses a single frame and needs $O(1)$ stack space.
:::

## Further learning

- **Next:** *Scope, Linkage & Storage Classes* explains how long variables live and where they can be seen.
- **Related:** *Call Stack and Recurrence Trees* in Data Structures & Algorithms analyses the cost of recursion.
