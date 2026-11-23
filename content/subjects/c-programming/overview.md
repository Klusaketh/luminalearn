C is a small, fast, procedural language that gives the programmer direct control over memory. It was created to write the Unix operating system, and it still runs much of the world's infrastructure: operating system kernels, embedded devices, databases, language runtimes such as CPython, and network software. Learning C shows you what higher-level languages do for you behind the scenes.

This subject starts with how a C program becomes an executable, through preprocessing, compilation, assembly, and linking, and then covers types, operators, bitwise manipulation, and control flow. It explains functions and the call stack, scope and storage classes, and how arrays and strings are laid out in memory. The central topic is pointers: addresses, pointer arithmetic, and how they connect arrays, strings, and functions. Later modules cover structures, unions, and enumerations, dynamic memory with `malloc` and `free`, linked data structures, file streams, the preprocessor and multi-file programs, and finally the undefined behaviour and common bugs that make C both powerful and unforgiving.

Lessons emphasise reasoning about memory: what is stored where, how large it is, and who is responsible for freeing it.

## What you will learn
- Describe the stages that turn C source code into an executable program
- Use C's data types, operators, and bitwise masks, and predict the result of mixed-type expressions
- Write structured programs with loops, switch statements, and functions, and explain the call stack
- Explain scope, linkage, and storage classes such as static and extern
- Work with arrays and null-terminated strings and reason about their memory layout
- Use pointers and pointer arithmetic correctly, including pointers to arrays, strings, and structures
- Define structures, unions, and enumerations, and explain alignment and padding
- Allocate and free heap memory, build linked data structures, and avoid memory leaks
- Read and write text and binary files with standard I/O streams
- Organise code across multiple files with headers and macros, and recognise undefined behaviour

## Prerequisites
- Basic programming experience in any language, such as variables, loops, and functions
- Familiarity with binary numbers helps for bitwise operators and memory layout
- Access to a C compiler such as GCC or Clang

## Glossary
- **Compiler**: a program that translates C source code into machine code
- **Linker**: the tool that combines compiled object files and libraries into one executable
- **Pointer**: a variable that holds the memory address of another object
- **Dereference**: accessing the object a pointer points to, using the * operator
- **Array**: a fixed-size block of consecutive elements of one type
- **Null-terminated string**: a character array that marks its end with the character '\0'
- **Stack**: the memory region holding function call frames and local variables
- **Heap**: the memory region for dynamically allocated objects managed with malloc and free
- **Memory leak**: heap memory that is never freed after the program stops using it
- **Struct**: a user-defined type grouping named members of possibly different types
- **Header file**: a .h file of declarations shared between source files
- **Macro**: a preprocessor definition that is textually substituted before compilation
- **Undefined behaviour**: an operation the C standard places no requirements on, such as reading past the end of an array

## Further reading
- Brian W. Kernighan and Dennis M. Ritchie, *The C Programming Language* (Prentice Hall)
- K. N. King, *C Programming: A Modern Approach* (W. W. Norton)
- Jens Gustedt, *Modern C* (Manning)
- Robert C. Seacord, *Effective C* (No Starch Press)
