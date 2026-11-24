---
lesson: jvm-architecture-bytecode
title: JVM Architecture & Bytecode
summary: How Java source becomes bytecode and runs on the Java Virtual Machine: class loading, bytecode verification, the interpreter and JIT compiler, the runtime memory areas, and garbage collection.
minutes: 35
type: theory
objectives:
  - Trace a Java program from source file through javac, class files, and class loading to execution
  - Describe the JVM runtime data areas, including the heap, stacks, and method area, and what each holds
  - Explain how interpretation, JIT compilation, and garbage collection affect a program's performance
review: ai-draft
---
## Introduction

"Write once, run anywhere" was Java's founding promise. Instead of compiling to machine code for one processor, the Java compiler produces **bytecode**, instructions for an abstract machine called the **Java Virtual Machine** (JVM). Any computer with a JVM can run the same `.class` files. Knowing what the JVM does with your code explains Java's start-up time, why it gets faster as it runs, where your objects live, and why you never call `free`.

**Before you start:** you should know what a compiler does and have written a small program in any language.

## Core theory

### From source to bytecode

`javac Main.java` compiles source into `Main.class`, one class file per class. A class file contains the class's bytecode, a **constant pool** of names and literals it uses, and metadata about fields and methods. Bytecode is a compact stack-based instruction set: `iload_1` pushes a local variable, `iadd` adds the top two values, `invokevirtual` calls a method. `javap -c Main` disassembles a class file so you can read its bytecode. Running `java Main` starts a JVM and asks it to execute `Main.main`.

### Class loading

The JVM loads classes **lazily**, the first time they are needed, through a hierarchy of **class loaders**: the bootstrap loader for core classes (`java.lang.*`), the platform loader for other JDK modules, and the application loader for classes on your class path. Loading a class has three phases:

1. **Loading:** find the class file and read its bytes.
2. **Linking:** **verify** the bytecode (so that, for example, it cannot jump outside a method or misuse types), **prepare** static fields with default values, and resolve symbolic references.
3. **Initialisation:** run static initialisers and assign static fields, exactly once.

Verification is a key security feature: bytecode that would corrupt memory is rejected before it runs.

### Runtime data areas

| Area | Shared? | Holds |
| :--- | :--- | :--- |
| Heap | all threads | every object and array |
| Method area (Metaspace) | all threads | class metadata, bytecode, static fields, constant pools |
| JVM stack | one per thread | a frame per method call: local variables, operand stack |
| PC register | one per thread | the current bytecode instruction |
| Native method stack | one per thread | frames of native (C/C++) methods |

A local variable of a primitive type lives in the stack frame; a local variable of a reference type holds a reference on the stack while the object itself lives on the heap. Deep recursion exhausts a thread's stack and throws `StackOverflowError`; filling the heap throws `OutOfMemoryError`.

### Execution engine: interpreter and JIT

The JVM starts by **interpreting** bytecode, which begins quickly but runs slowly. It counts how often methods and loops run; **hot** code is compiled to native machine code by the **just-in-time (JIT) compiler**, using profiling information gathered while interpreting, such as which branch is usually taken or which class a virtual call usually reaches. HotSpot uses a fast C1 compiler first and an optimising C2 compiler for the hottest code. This is why Java programs often speed up after a "warm-up" period, and why benchmarks must run code many times before measuring.

### Garbage collection

Objects are allocated on the heap with `new` and never freed by hand. The **garbage collector** (GC) finds objects that are no longer **reachable** from the **GC roots** (local variables on stacks, static fields, and a few others) and reclaims their memory. Most collectors are **generational**: most objects die young, so new objects are allocated in a young generation that is collected often and cheaply, and long-lived objects are promoted to an old generation collected less often. Modern collectors such as G1 and ZGC do much of their work concurrently to keep pauses short. Garbage collection prevents dangling pointers and double frees, but objects still reachable through forgotten references, such as an ever-growing static list, still leak.

## Worked examples

### Example 1: Static initialisation runs once, on first use

```java
public class Main {
    static class Config {
        static final long LOADED_AT;
        static int requests = 0;
        static {
            System.out.println("Config class initialised");
            LOADED_AT = 42;
        }
        static void hit() { requests++; }
    }

    public static void main(String[] args) {
        System.out.println("main started");
        Config.hit();
        Config.hit();
        System.out.println("requests = " + Config.requests + ", loaded marker = " + Config.LOADED_AT);
        int depth = recurse(0);
        System.out.println("recursion reached depth " + depth);
    }

    static int recurse(int n) {
        return n == 1000 ? n : recurse(n + 1);
    }
}
```

Output:

```text
main started
Config class initialised
requests = 2, loaded marker = 42
recursion reached depth 1000
```

`Config` is loaded and initialised only when `main` first uses it, after "main started" has been printed, and its static block runs exactly once. Each of the 1,000 recursive calls gets its own frame on the thread's JVM stack; a much deeper recursion would throw `StackOverflowError`.

### Example 2: Reading bytecode

For the method

```java
static int addTwice(int a, int b) {
    int c = a + b;
    return c + c;
}
```

`javap -c` shows bytecode similar to this:

```text
0: iload_0      // push a
1: iload_1      // push b
2: iadd         // a + b
3: istore_2     // c = result
4: iload_2      // push c
5: iload_2      // push c
6: iadd         // c + c
7: ireturn      // return the top of the stack
```

Arguments and locals occupy numbered slots in the frame (`a` is slot 0, `b` slot 1, `c` slot 2), and every operation works on the **operand stack**: push operands, apply the instruction, and the result replaces them. If this method becomes hot, the JIT compiles it to a few native instructions that keep the values in registers.

## Applications

- **Portability:** the same JAR runs on Windows, Linux, macOS, and servers of any architecture.
- **Other languages:** Kotlin, Scala, and Clojure compile to JVM bytecode and share its libraries.
- **Performance tuning:** heap size flags (`-Xmx`), GC choice, and JIT warm-up matter for servers.
- **Diagnostics:** heap dumps and GC logs explain memory problems in production.

## Common mistakes

- **Benchmarking without warm-up.** Early measurements include interpretation and JIT compilation time.
- **Assuming garbage collection prevents all leaks.** Reachable but unused objects are never collected.
- **Confusing stack and heap.** References live in stack frames; the objects they point to live on the heap.
- **Calling `System.gc()` to "fix" memory.** It is only a request and rarely helps; remove the references instead.

## Revision notes

- `javac` produces bytecode in `.class` files; `java` runs it on the JVM.
- Class loading: load, link (verify, prepare, resolve), initialise; lazy and once per class.
- Heap (objects) and method area are shared; each thread has its own JVM stack and PC.
- Bytecode is stack-based; `javap -c` disassembles it.
- Interpreter first, then the JIT compiles hot code using profiling data.
- GC reclaims objects unreachable from roots; generational collectors exploit short object lifetimes.

## Practice questions

:::question basic
What does `javac` produce, and what runs it?
:::answer
`javac` compiles Java source into bytecode stored in `.class` files. The Java Virtual Machine loads those class files and executes the bytecode, by interpretation and by JIT-compiling hot code to native instructions.
:::

:::question basic
Where does an object created with `new` live, and where does a local reference variable that points to it live?
:::answer
The object lives on the heap, which is shared by all threads. The local reference variable lives in the current method's frame on the thread's JVM stack and holds the object's reference.
:::

:::question intermediate
Why does bytecode verification matter for security?
:::answer
The verifier checks that bytecode is type-safe and well formed before it runs: stack operations have the right types, jumps stay inside the method, and objects are used according to their classes. This prevents malicious or corrupted class files from reading or writing arbitrary memory, which the JVM would otherwise have to trust.
:::

:::question intermediate
Why do Java programs often run faster after they have been running for a while?
:::answer
The JVM first interprets bytecode while profiling it. Frequently executed methods and loops are then compiled by the JIT compiler into optimised native code, using the profile to make good decisions such as inlining. Once the hot code is compiled, it runs much faster than interpreted bytecode.
:::

:::question advanced
A server stores every request object in a static `List` "for debugging" and eventually throws `OutOfMemoryError`, even though Java has garbage collection. Explain why.
:::answer
Garbage collection only reclaims objects that are unreachable from GC roots. Static fields are roots, so every request added to the static list stays reachable forever and can never be collected. The heap fills until allocation fails. The fix is to stop retaining the objects, for example by bounding the list or removing entries when they are no longer needed.
:::

## Further learning

- **Next:** *Syntax, Types & Control Flow* starts writing the programs the JVM runs.
- **Related:** *Class Definitions & Memory Allocation* looks closer at objects on the heap and garbage collection roots.
