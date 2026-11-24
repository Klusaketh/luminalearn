---
lesson: cpp-overloading-references
title: Overloading & Pass-By-Reference
summary: Function overloading and how the compiler chooses between overloads, passing by value, reference, and const reference, default arguments, inline functions, and name mangling.
minutes: 35
type: theory
objectives:
  - Write overloaded functions and predict which overload a call selects
  - Choose between pass-by-value, pass-by-reference, and pass-by-const-reference for each parameter
  - Explain name mangling, default arguments, and what the inline keyword means today
review: ai-draft
---
## Introduction

In C, every function needs a unique name, so a library ends up with `abs`, `labs`, `fabs`, and `llabs`. C++ lets several functions share one name as long as their parameter lists differ, which is called **overloading**. Together with references, overloading lets you write natural, efficient interfaces: one `print` for every type, and parameters that avoid copying large objects. This lesson covers how overloads are chosen, how to pass arguments well, and what the compiler does behind the scenes.

**Before you start:** you should know C++ basic syntax, references, and `std::string`.

## Core theory

### Function overloading

Functions may share a name if their **parameter lists** differ in number or types:

```cpp
int area(int side);
double area(double radius);
int area(int w, int h);
```

The return type alone cannot distinguish overloads. For each call, the compiler performs **overload resolution**: it ranks the candidates by how well the arguments match, preferring an **exact match**, then a **promotion** (such as `char` to `int` or `float` to `double`), then a standard **conversion** (such as `int` to `double`), then user-defined conversions. If two candidates tie for best, the call is **ambiguous** and does not compile; `area(5L)` with `int` and `double` overloads is ambiguous because `long` converts to both equally well.

### Name mangling

The linker needs a unique symbol for each function, so the compiler **mangles** names by encoding the parameter types, for example turning `area(double)` into a symbol such as `_Z4aread`. That is how two functions named `area` coexist in one program. It is also why C++ code calling a C library declares the C functions inside `extern "C" { ... }`, which turns off mangling so the names match the C object files.

### Passing arguments

| Style | Syntax | Use when |
| :--- | :--- | :--- |
| By value | `void f(int x)` | small, cheap-to-copy types; the function needs its own copy |
| By reference | `void f(int& x)` | the function must modify the caller's object |
| By const reference | `void f(const std::string& s)` | large objects read without modification |
| By pointer | `void f(int* p)` | "no object" (`nullptr`) is a meaningful option |

A non-const reference cannot bind to a temporary or a literal: `inc(5)` fails for `void inc(int&)`, which protects you from modifying a value that disappears immediately. A `const` reference can bind to temporaries, so `print("hello")` works for `void print(const std::string&)`.

### Default arguments

`void greet(const std::string& name, int times = 1);` lets callers omit trailing arguments. Defaults are written once, in the declaration, and must be at the end of the parameter list. Overloading and default arguments can clash: `f(int)` together with `f(int, int = 0)` makes `f(3)` ambiguous.

### inline

Originally `inline` was a hint to replace calls with the function body, saving call overhead. Modern compilers decide inlining themselves. Today `inline` mainly means "this function may be defined in a header included by many files without causing multiple-definition errors". Functions defined inside a class body are implicitly inline.

## Worked examples

### Example 1: Overload resolution in action

```cpp
#include <iostream>
#include <string>

void show(int x)                { std::cout << "int " << x << '\n'; }
void show(double x)             { std::cout << "double " << x << '\n'; }
void show(const std::string& s) { std::cout << "string " << s << '\n'; }
void show(char c, int times)    { std::cout << "char x" << times << ' ' << std::string(times, c) << '\n'; }

int main() {
    show(42);
    show(3.5);
    show(2.5f);
    show('A');
    show(std::string("hi"));
    show("literal");
    show('*', 3);
    return 0;
}
```

Output:

```text
int 42
double 3.5
double 2.5
int 65
string hi
string literal
char x3 ***
```

`2.5f` promotes from `float` to `double`. `'A'` promotes from `char` to `int`, printing its character code 65. The string literal converts to `std::string` through a user-defined conversion because no better match exists.

### Example 2: Value, reference, and const reference parameters

```cpp
#include <iostream>
#include <string>
#include <vector>

void add_bonus_copy(int marks)    { marks += 10; }
void add_bonus_ref(int& marks)    { marks += 10; }
int count_long(const std::vector<std::string>& words, std::size_t min_len = 5) {
    int n = 0;
    for (const auto& w : words) if (w.size() >= min_len) n++;
    return n;
}

int main() {
    int m = 70;
    add_bonus_copy(m);
    std::cout << "after copy: " << m << '\n';
    add_bonus_ref(m);
    std::cout << "after ref: " << m << '\n';
    std::vector<std::string> words = {"array", "map", "pointer", "list", "vector"};
    std::cout << count_long(words) << ' ' << count_long(words, 4) << '\n';
    return 0;
}
```

Output:

```text
after copy: 70
after ref: 80
3 4
```

Only the reference version changes `m`. `count_long` reads a vector of strings without copying it, and its default argument lets the caller omit the minimum length.

## Applications

- **Libraries:** `std::abs`, `std::to_string`, and `std::max` are overloaded for many types.
- **Math types:** one `distance` function for 2-D and 3-D points.
- **Efficient interfaces:** `const&` parameters pass strings, vectors, and objects without copies.
- **Mixed C/C++ projects:** `extern "C"` links C++ code with C libraries.

## Common mistakes

- **Overloading only on return type.** It is not allowed; the parameters must differ.
- **Passing large objects by value.** Use `const T&` unless the function needs its own copy.
- **Expecting `T&` to accept literals.** Non-const references cannot bind to temporaries.
- **Ambiguous overloads with defaults.** Do not combine overloads and default arguments that cover the same calls.

## Revision notes

- Overloads share a name and differ in parameter types or count.
- Resolution order: exact match, promotion, conversion, user-defined conversion; ties are ambiguous.
- Mangled names encode parameter types; `extern "C"` disables mangling.
- Value for small types, `T&` to modify, `const T&` for large read-only inputs.
- Default arguments go at the end, written once in the declaration.
- `inline` today mainly permits definitions in headers.

## Practice questions

:::question basic
Can two functions `int parse(const std::string&)` and `double parse(const std::string&)` coexist? Why?
:::answer
No. They have identical parameter lists and differ only in return type, which overloading cannot use to choose between them, so the second declaration is an error.
:::

:::question basic
Given `void f(double)` and `void f(long)`, why is `f(5)` ambiguous?
:::answer
The argument `5` is an `int`. Converting it to `double` and to `long` are both standard conversions of equal rank, and neither is an exact match or a promotion, so the compiler cannot prefer one and reports an ambiguous call.
:::

:::question intermediate
Why does `void inc(int& x); inc(3);` fail to compile, while `void show(const int& x); show(3);` works?
:::answer
A non-const reference must bind to a modifiable object, and the literal `3` is a temporary value, so binding is refused to prevent changes that would be lost immediately. A `const` reference may bind to a temporary because the function promises not to modify it.
:::

:::question intermediate
What is name mangling, and why is it needed for overloading?
:::answer
The compiler encodes each function's parameter types (and namespace or class) into its symbol name. Overloads share a source name, so without mangling they would produce identical symbols that the linker could not tell apart; mangling gives each overload a unique symbol.
:::

:::question advanced
Design overloads or defaults for a `log_message` function that accepts a message, an optional severity (default "INFO"), and either an `int` or a `std::string` error code. Explain your choices.
:::answer
Use a default for the severity and overloads for the code type: `void log_message(const std::string& msg, const std::string& level = "INFO");`, `void log_message(const std::string& msg, int code, const std::string& level = "INFO");`, and `void log_message(const std::string& msg, const std::string& code, const std::string& level);` without a default on `level`. Strings are passed by `const&` to avoid copies. Giving the string-code version a defaulted `level` would make `log_message("x", "y")` ambiguous with the first overload, so its `level` must stay explicit; alternatively, wrap the code in a small type to keep calls unambiguous.
:::

## Further learning

- **Next:** *Standard Containers (vector & string)* passes containers efficiently with these techniques.
- **Related:** *Operator Overloading* extends overloading to operators such as `+` and `<<`.
