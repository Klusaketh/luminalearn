---
lesson: cpp-generic-templates
title: Generic Programming with Templates
summary: Writing generic code with function and class templates, how the compiler deduces template arguments and instantiates code, non-type parameters, specialisation, and compile-time checks with static_assert and if constexpr.
minutes: 45
type: theory
objectives:
  - Write function and class templates and explain template argument deduction and instantiation
  - Use non-type template parameters, explicit specialisation, and static_assert
  - Compare compile-time polymorphism with templates to run-time polymorphism with virtual functions
review: ai-draft
---
## Introduction

Without generics you would write `max_int`, `max_double`, and `max_string`, three copies of the same logic. **Templates** let you write the logic once with a placeholder type, and the compiler generates a correct, fully optimised version for each type you use. The whole standard library, `std::vector<T>`, `std::sort`, `std::map<K, V>`, is built from templates. Understanding them lets you read library code, interpret long error messages, and write reusable components of your own.

**Before you start:** you should know functions, classes, overloading, and operator overloading.

## Core theory

### Function templates

```cpp
template <typename T>
T largest(const T& a, const T& b) {
    return (a < b) ? b : a;
}
```

`T` is a **template parameter**. Calling `largest(3, 7)` makes the compiler **deduce** `T = int` from the arguments and **instantiate** `largest<int>`, a real function compiled just like hand-written code. Deduction requires the arguments to agree: `largest(3, 7.5)` fails because `T` cannot be both `int` and `double`; write `largest<double>(3, 7.5)` to specify it explicitly. A template places **requirements** on its types: `largest` needs `T` to support `<`, and using it with a type that does not causes a compile error at the point of instantiation.

### Class templates

```cpp
template <typename T>
class Stack {
public:
    void push(const T& x) { items_.push_back(x); }
    T pop() { T top = items_.back(); items_.pop_back(); return top; }
    bool empty() const { return items_.empty(); }
private:
    std::vector<T> items_;
};
```

`Stack<int>` and `Stack<std::string>` are two distinct classes generated from one template. Since C++17, **class template argument deduction** lets you write `std::vector v = {1, 2, 3};`. Member functions of a class template are instantiated only if they are used. Template definitions normally live entirely in header files, because the compiler needs the full definition wherever an instantiation is created.

### Non-type parameters and specialisation

Template parameters can also be compile-time values: `template <typename T, std::size_t N> class FixedArray { T data_[N]; };`, as in `std::array<int, 5>`. An **explicit specialisation** supplies a different implementation for one particular type, for example `template <> struct TypeName<int> { ... };`, which is how `std::vector<bool>` is packed into bits.

### Compile-time checks

- `static_assert(condition, "message")` stops compilation with a clear message when a requirement fails, for example `static_assert(std::is_arithmetic_v<T>, "T must be a number");`.
- `if constexpr (condition)` (C++17) discards the branch that does not apply at compile time, so each instantiation contains only valid code.
- C++20 **concepts** (`template <std::integral T>`) state requirements directly and produce much shorter error messages.

### Templates versus virtual functions

Templates give **compile-time polymorphism**: the type is fixed when the code is compiled, calls can be inlined, and there is no run-time dispatch, at the cost of larger binaries (one copy per type) and longer compile times. Virtual functions give **run-time polymorphism**: one compiled function handles any derived type chosen at run time, for example from user input, at the cost of an indirect call. Use templates when the types are known at compile time and speed matters; use virtual functions when the type is decided while the program runs or when you need a heterogeneous collection.

## Worked examples

### Example 1: Function templates and deduction

```cpp
#include <iostream>
#include <string>
#include <vector>

template <typename T>
T largest(const T& a, const T& b) { return (a < b) ? b : a; }

template <typename Container>
auto sum_all(const Container& c) {
    typename Container::value_type total{};
    for (const auto& x : c) total += x;
    return total;
}

template <typename T, std::size_t N>
constexpr std::size_t length_of(const T (&)[N]) { return N; }

int main() {
    std::cout << largest(3, 7) << ' ' << largest(2.5, -1.0) << ' ' << largest(std::string("pear"), std::string("apple")) << '\n';
    std::cout << largest<double>(3, 7.5) << '\n';
    std::vector<int> v = {1, 2, 3, 4};
    std::vector<std::string> words = {"tem", "pla", "tes"};
    std::cout << sum_all(v) << ' ' << sum_all(words) << '\n';
    int raw[] = {5, 6, 7};
    static_assert(length_of(raw) == 3, "deduced at compile time");
    std::cout << "length " << length_of(raw) << '\n';
    return 0;
}
```

Output:

```text
7 2.5 pear
7.5
10 templates
length 3
```

`largest` is instantiated three times, for `int`, `double`, and `std::string`. `sum_all` works for any container whose elements support `+=`, including strings, where `+=` concatenates. `length_of` deduces the array size `N` as a non-type template parameter, so the `static_assert` is checked during compilation.

### Example 2: A class template with a specialisation and if constexpr

```cpp
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

template <typename T>
class Stack {
public:
    void push(const T& x) { items_.push_back(x); }
    T pop() { T top = items_.back(); items_.pop_back(); return top; }
    bool empty() const { return items_.empty(); }
    std::size_t size() const { return items_.size(); }
private:
    std::vector<T> items_;
};

template <typename T>
struct TypeName { static const char* get() { return "something"; } };
template <>
struct TypeName<int> { static const char* get() { return "int"; } };

template <typename T>
std::string describe(const T& value) {
    if constexpr (std::is_arithmetic_v<T>) {
        return std::string(TypeName<T>::get()) + " number " + std::to_string(value);
    } else {
        return std::string(TypeName<T>::get()) + " of size " + std::to_string(value.size());
    }
}

int main() {
    Stack<int> s;
    for (int i = 1; i <= 3; i++) s.push(i * 10);
    std::cout << s.pop() << ' ' << s.pop() << " left " << s.size() << '\n';
    Stack<std::string> names;
    names.push("Ada");
    std::cout << names.pop() << ' ' << names.empty() << '\n';
    std::cout << describe(42) << '\n';
    std::cout << describe(std::string("hello")) << '\n';
    return 0;
}
```

Output:

```text
30 20 left 1
Ada 1
int number 42
something of size 5
```

`Stack<int>` and `Stack<std::string>` are separate classes generated from one template. The specialisation `TypeName<int>` overrides the general version for `int`. In `describe`, `if constexpr` removes the branch that does not apply, so `value.size()` is never compiled for `int`, which has no `size()`.

## Applications

- **The standard library:** containers, algorithms, smart pointers, and `std::function` are templates.
- **Numeric libraries:** one matrix template serves `float`, `double`, and complex numbers.
- **Zero-overhead abstractions:** templates let generic code run as fast as hand-specialised code.
- **Compile-time computation:** `constexpr` and templates compute values and check rules during compilation.

## Common mistakes

- **Putting template definitions in a `.cpp` file.** Other files cannot instantiate them; keep templates in headers.
- **Conflicting deduction.** `largest(3, 7.5)` fails; give the type explicitly or use two parameters.
- **Unstated requirements.** Document or check (`static_assert`, concepts) what operations `T` must support.
- **Using `typename` incorrectly.** Dependent types such as `Container::value_type` need `typename` in front.

## Revision notes

- `template <typename T>` declares a type parameter; the compiler deduces and instantiates.
- All deduced arguments must agree; otherwise specify `f<T>(...)`.
- Class templates generate one class per argument list; define them in headers.
- Non-type parameters: `template <typename T, std::size_t N>`.
- Explicit specialisation: `template <> struct X<int> { ... };`.
- `static_assert` and `if constexpr` work at compile time; templates are compile-time polymorphism.

## Practice questions

:::question basic
What does the compiler do when it sees `largest(4, 9)` for the template `template <typename T> T largest(const T&, const T&)`?
:::answer
It deduces `T = int` from both arguments and instantiates `largest<int>`, generating and compiling a real function for `int`, which the call then uses.
:::

:::question basic
Why does `largest(3, 4.5)` fail to compile, and how can you call it?
:::answer
The first argument deduces `T = int` and the second `T = double`, which conflict, so deduction fails. Specify the type explicitly, `largest<double>(3, 4.5)`, so that 3 is converted to `double`.
:::

:::question intermediate
Why are class templates usually defined entirely in header files?
:::answer
The compiler generates a template's code only when it is instantiated with specific arguments, and it needs the complete definition at that point. A file that includes only a declaration cannot instantiate it, so the definitions must be visible in every file that uses the template, which in practice means the header.
:::

:::question intermediate
What does `if constexpr` do that an ordinary `if` cannot inside a template?
:::answer
The condition is evaluated at compile time, and the branch not taken is discarded for that instantiation, so it is never compiled. Code that would be invalid for some types, such as calling `size()` on an `int`, can therefore live in a branch that is discarded for those types.
:::

:::question advanced
You need a function that processes a collection of shapes whose exact types are read from a file at run time. Should you use templates or virtual functions? Justify the choice.
:::answer
Use virtual functions. The concrete types are only known while the program runs and the collection mixes several types, so the dispatch decision must happen at run time, for example with `std::vector<std::unique_ptr<Shape>>` and a virtual `area()`. Templates require the type at compile time and would generate a separate function per type, which cannot hold a mixed collection in one container.
:::

## Further learning

- **Next:** *STL Containers & Iterators* tours the template containers of the standard library.
- **Related:** *Virtual Functions & VTable Dispatch* covers the run-time alternative to templates.
