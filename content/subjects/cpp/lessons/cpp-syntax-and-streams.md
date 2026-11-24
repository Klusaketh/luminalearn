---
lesson: cpp-syntax-and-streams
title: C++ Modern Syntax & Streams
summary: The first steps from C to modern C++: iostream input and output, namespaces, references, auto type inference, range-based for loops, and the std::string type.
minutes: 35
type: theory
objectives:
  - Write and compile a C++17 program that reads and writes with std::cin and std::cout
  - Use namespaces, references, and auto correctly, and explain how a reference differs from a pointer
  - Use range-based for loops and std::string instead of C-style loops and character arrays
review: ai-draft
---
## Introduction

C++ began as "C with classes" and has grown into a language that keeps C's speed while adding safer, more expressive tools. Modern C++ (C++11 and later) lets you write code that is shorter than the equivalent C and much less error-prone: streams instead of format strings, references instead of many pointers, `std::string` instead of character arrays, and the compiler deducing types for you. This lesson covers the everyday syntax you will use in every C++ program.

**Before you start:** you should know C basics: types, functions, loops, arrays, and pointers. Knowing another programming language is enough to follow most of it.

## Core theory

### Hello, C++

```cpp
#include <iostream>

int main() {
    std::cout << "Hello, C++!" << '\n';
    return 0;
}
```

`<iostream>` provides the standard streams: `std::cout` (output), `std::cin` (input), and `std::cerr` (errors). The **insertion operator** `<<` sends values to a stream and can be chained; the **extraction operator** `>>` reads whitespace-separated values from `std::cin` into variables, converting them to the variable's type. Streams know the types of their values, so there are no format specifiers to get wrong. `std::endl` writes a newline **and** flushes the buffer; `'\n'` is usually preferred because flushing is slow. Compile with `g++ -std=c++17 -Wall -Wextra main.cpp -o main`.

### Namespaces

Standard library names live in the **namespace** `std`, so you write `std::cout` and `std::string`. Namespaces prevent clashes between libraries that use the same names. `using std::cout;` brings one name into scope; `using namespace std;` brings in everything and is acceptable in small programs but should never appear in header files, where it would leak into every file that includes them. You can define your own: `namespace geometry { double area(double r); }`, used as `geometry::area(2.0)`.

### References

A **reference** is another name for an existing object: `int x = 5; int& r = x; r = 10;` sets `x` to 10. Unlike a pointer, a reference must be initialised, cannot be null, cannot be reseated to refer to something else, and needs no `*` to use. References are mainly used for function parameters: `void inc(int& n) { n++; }` changes the caller's variable, and `const std::string& s` passes a large object without copying it while promising not to modify it.

### auto and range-based for

`auto` asks the compiler to deduce a variable's type from its initialiser: `auto total = 0.0;` is a `double`, and `auto it = names.begin();` saves writing a long iterator type. The **range-based for loop** visits each element of a container: `for (int x : values)` copies each element; `for (int& x : values)` lets you modify them; `for (const auto& s : names)` reads without copying.

### std::string

`std::string` manages its own memory, grows as needed, and supports `+` for concatenation, `==` and `<` for comparison, `.size()`, indexing, `.substr(pos, len)`, and `.find(text)` (which returns `std::string::npos` when not found). `std::getline(std::cin, line)` reads a whole line including spaces. There is no buffer to overflow and no terminator to forget.

## Worked examples

### Example 1: Streams, strings, references, and auto

```cpp
#include <cctype>
#include <iostream>
#include <sstream>
#include <string>

void shout(std::string& s) {
    for (char& c : s) c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    s += "!";
}

int main() {
    std::istringstream input("Asha 19 3.75");
    std::string name;
    int age;
    double gpa;
    input >> name >> age >> gpa;

    auto next_year = age + 1;
    std::string greeting = "hello " + name;
    shout(greeting);
    std::cout << greeting << '\n';
    std::cout << name << " will be " << next_year << ", gpa " << gpa << '\n';
    std::cout << "length " << greeting.size() << ", 'ASHA' at " << greeting.find("ASHA") << '\n';

    int x = 5;
    int& r = x;
    r *= 3;
    std::cout << "x = " << x << '\n';
    return 0;
}
```

Output:

```text
HELLO ASHA!
Asha will be 20, gpa 3.75
length 11, 'ASHA' at 6
x = 15
```

An `istringstream` reads from a string exactly as `std::cin` reads from the keyboard, which makes the example repeatable. `shout` takes a reference, so it modifies the caller's `greeting`; the loop uses `char&` to change each character in place.

### Example 2: Range-based loops and a namespace

```cpp
#include <iostream>
#include <string>
#include <vector>

namespace stats {
    double mean(const std::vector<double>& xs) {
        double sum = 0;
        for (double x : xs) sum += x;
        return xs.empty() ? 0.0 : sum / xs.size();
    }
}

int main() {
    std::vector<double> marks = {72, 85, 91, 64};
    for (double& m : marks) m += 5;
    for (const auto& m : marks) std::cout << m << ' ';
    std::cout << '\n';
    std::cout << "mean " << stats::mean(marks) << '\n';

    std::vector<std::string> names = {"Ravi", "Meena", "Asha"};
    std::string joined;
    for (const auto& n : names) joined += (joined.empty() ? "" : ", ") + n;
    std::cout << joined << '\n';
    return 0;
}
```

Output:

```text
77 90 96 69
mean 83
Ravi, Meena, Asha
```

`double& m` modifies each mark in place, while `const auto& n` reads each name without copying it. `stats::mean` is qualified by its namespace, and `const std::vector<double>&` passes the vector without a copy.

## Applications

- **Systems and games:** C++ powers game engines, browsers, and databases where speed matters.
- **Competitive programming:** streams, strings, and vectors make solutions short and fast.
- **Embedded and robotics:** C++ offers abstraction with predictable performance.
- **Large codebases:** namespaces keep names from different teams and libraries apart.

## Common mistakes

- **`using namespace std;` in headers.** It pollutes every including file; qualify names instead.
- **Using `std::endl` everywhere.** It flushes on each use; `'\n'` is faster.
- **Mixing `std::cin >> x` with `std::getline`.** `>>` leaves the newline in the buffer, so the next `getline` reads an empty line; skip it with `std::cin >> std::ws`.
- **Copying in loops by accident.** `for (auto s : names)` copies every string; use `const auto&`.

## Revision notes

- `std::cout << a << b;` writes, `std::cin >> x;` reads, `std::getline` reads a line.
- Standard names are in `std`; never put `using namespace std;` in a header.
- A reference is an alias: must be initialised, never null, never reseated.
- `const T&` parameters avoid copies without allowing modification.
- `auto` deduces a type from the initialiser.
- `for (const auto& x : c)` reads; `for (auto& x : c)` modifies.

## Practice questions

:::question basic
What is the difference between `std::cout << x << std::endl;` and `std::cout << x << '\n';`?
:::answer
Both print `x` followed by a newline. `std::endl` also flushes the output buffer, forcing a write to the device, which is slower when done repeatedly; `'\n'` only adds the newline.
:::

:::question basic
After `int a = 1; int& r = a; r = 7;`, what is the value of `a`?
:::answer
`a` is 7. `r` is a reference, another name for `a`, so assigning to `r` assigns to `a`.
:::

:::question intermediate
Why is `void print(const std::string& s)` preferred over `void print(std::string s)` for a function that only displays text?
:::answer
Passing by value copies the whole string, allocating memory for long strings on every call. A `const` reference passes the original without copying, and `const` guarantees the function will not modify it.
:::

:::question intermediate
What type does `auto` deduce in `auto a = 3;`, `auto b = 3.0;`, and `auto c = 'x';`?
:::answer
`a` is an `int`, `b` is a `double`, and `c` is a `char`. `auto` takes the type of the initialising expression.
:::

:::question advanced
List three differences between a C++ reference and a pointer, and say when you would still choose a pointer.
:::answer
A reference must be initialised when declared, cannot be null, and cannot be made to refer to a different object, and it is used without dereference syntax; a pointer can be null, can be reassigned, and supports arithmetic. You still choose a pointer when "no object" is a valid state, when the target must change during the object's life, or when interfacing with C APIs; for owned heap objects, prefer smart pointers.
:::

## Further learning

- **Next:** *Overloading & Pass-By-Reference* builds on references and functions.
- **Related:** *Standard Containers (vector & string)* explores `std::vector` and `std::string` in depth.
