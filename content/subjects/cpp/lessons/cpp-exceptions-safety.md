---
lesson: cpp-exceptions-safety
title: Exceptions & Exception Safety
summary: Signalling and handling errors with throw, try, and catch, the standard exception hierarchy, stack unwinding with RAII, noexcept, and the basic, strong, and no-throw exception-safety guarantees.
minutes: 45
type: theory
objectives:
  - Throw and catch exceptions, catching by reference and ordering handlers from specific to general
  - Explain stack unwinding and why RAII makes code exception-safe without explicit clean-up
  - Classify functions by the basic, strong, and no-throw guarantees and use noexcept appropriately
review: ai-draft
---
## Introduction

Some errors cannot be handled where they are detected: a parser finds bad input deep inside a call chain, a constructor cannot acquire a resource, an allocation fails. C++ **exceptions** carry such errors up the call stack to code that knows what to do, without every function checking error codes. Exceptions only work well together with RAII, because when an exception is thrown, the functions it passes through end abruptly. This lesson covers the mechanics and the guarantees good C++ code provides.

**Before you start:** you should know classes, destructors, RAII, and smart pointers.

## Core theory

### throw, try, catch

```cpp
double divide(double a, double b) {
    if (b == 0) throw std::invalid_argument("division by zero");
    return a / b;
}

try {
    divide(1, 0);
} catch (const std::invalid_argument& e) {
    std::cerr << e.what() << '\n';
}
```

`throw` creates an exception object and starts searching outward for a matching `catch`. Handlers are tried in order and the first whose type matches (including base classes) wins, so order them from **specific to general**. Always **catch by reference** (`const T&`): catching by value copies the exception and slices derived types. `catch (...)` catches anything. Inside a handler, `throw;` rethrows the current exception unchanged. If no handler is found, `std::terminate` ends the program.

### The standard exception hierarchy

`std::exception` (with the virtual `what()`) is the root. `std::logic_error` covers bugs that could be detected in advance (`std::invalid_argument`, `std::out_of_range`, `std::domain_error`); `std::runtime_error` covers conditions only detectable at run time (`std::overflow_error`, `std::range_error`). `std::bad_alloc` signals failed allocation. Custom exceptions usually derive from `std::runtime_error` or `std::logic_error` and pass a message to the base constructor.

### Stack unwinding and RAII

As an exception propagates, every function it leaves is exited, and **every fully constructed local object is destroyed** in reverse order: this is **stack unwinding**. Resources held by RAII objects (smart pointers, containers, file streams, lock guards) are therefore released automatically. Resources held by raw pointers or manual `lock()`/`unlock()` pairs are not, which is why RAII is essential for exception-safe code. Destructors must not throw: throwing during unwinding calls `std::terminate`. Destructors are `noexcept` by default.

### Exception-safety guarantees

Every function should offer one of these:

| Guarantee | Promise |
| :--- | :--- |
| **No-throw** | never throws (destructors, swaps, moves marked `noexcept`) |
| **Strong** | if an exception is thrown, the program state is exactly as before the call ("commit or roll back") |
| **Basic** | if an exception is thrown, no resources leak and all objects remain valid, but their values may have changed |

The strong guarantee is often achieved with **copy-and-swap**: do all work that might throw on a copy, then swap it in with a no-throw operation. `std::vector::push_back` offers the strong guarantee.

### noexcept

`noexcept` declares that a function will not throw; if it does, `std::terminate` is called. It documents intent and enables optimisations, most importantly letting containers move elements instead of copying them. Mark move constructors, move assignments, swaps, and destructors `noexcept` when they truly cannot throw.

### When not to use exceptions

Exceptions are for exceptional conditions that a caller far away must handle, not for normal control flow such as "item not found", where a return value (`std::optional`, `end()` iterator, `bool`) is clearer and cheaper.

## Worked examples

### Example 1: Handlers, hierarchy, and unwinding

```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

struct Guard {
    std::string name;
    explicit Guard(std::string n) : name(std::move(n)) {}
    ~Guard() { std::cout << "  release " << name << '\n'; }
};

class InsufficientFunds : public std::runtime_error {
public:
    explicit InsufficientFunds(double needed)
        : std::runtime_error("insufficient funds, short by " + std::to_string(static_cast<int>(needed))) {}
};

void withdraw(double balance, double amount) {
    Guard g("account lock");
    auto log = std::make_unique<Guard>("log buffer");
    if (amount <= 0) throw std::invalid_argument("amount must be positive");
    if (amount > balance) throw InsufficientFunds(amount - balance);
    std::cout << "  withdrew " << amount << '\n';
}

int main() {
    for (double amount : {50.0, 500.0, -5.0}) {
        std::cout << "try " << amount << '\n';
        try {
            withdraw(100, amount);
        } catch (const InsufficientFunds& e) {
            std::cout << "  declined: " << e.what() << '\n';
        } catch (const std::exception& e) {
            std::cout << "  error: " << e.what() << '\n';
        }
    }
    return 0;
}
```

Output:

```text
try 50
  withdrew 50
  release log buffer
  release account lock
try 500
  release log buffer
  release account lock
  declined: insufficient funds, short by 400
try -5
  release log buffer
  release account lock
  error: amount must be positive
```

In every case both resources are released, in reverse order, before the handler runs, because the `Guard` objects and the `unique_ptr` are destroyed during stack unwinding. The specific `InsufficientFunds` handler comes before the general `std::exception` handler, which catches `std::invalid_argument` through its base class.

### Example 2: The strong guarantee with copy-and-swap

```cpp
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

class Roster {
public:
    void add_all(const std::vector<std::string>& names) {
        std::vector<std::string> updated = names_;
        for (const auto& n : names) {
            if (n.empty()) throw std::invalid_argument("empty name in batch");
            updated.push_back(n);
        }
        names_.swap(updated);
    }
    std::size_t size() const noexcept { return names_.size(); }
private:
    std::vector<std::string> names_;
};

int main() {
    Roster r;
    r.add_all({"Asha", "Ravi"});
    std::cout << "size " << r.size() << '\n';
    try {
        r.add_all({"Meena", "", "John"});
    } catch (const std::invalid_argument& e) {
        std::cout << "rejected batch: " << e.what() << '\n';
    }
    std::cout << "size still " << r.size() << '\n';
    std::cout << "size() is noexcept: " << noexcept(r.size()) << '\n';
    return 0;
}
```

Output:

```text
size 2
rejected batch: empty name in batch
size still 2
size() is noexcept: 1
```

The batch is built on a copy; if any name is invalid the copy is thrown away and the roster is untouched, giving the strong guarantee. Only after all checks pass does the no-throw `swap` commit the change. The `noexcept` operator confirms at compile time that `size()` cannot throw.

## Applications

- **Constructors:** throwing is the only way a constructor can report failure.
- **Libraries:** `std::vector::at`, `std::stoi`, and `new` report errors with exceptions.
- **Transactions:** copy-and-swap gives all-or-nothing updates.
- **Servers:** a top-level handler logs unexpected exceptions and keeps serving other requests.

## Common mistakes

- **Catching by value.** It copies and slices; catch by `const&`.
- **General handlers first.** `catch (const std::exception&)` before a derived handler hides the derived one.
- **Manual resource management.** Raw `new` or `lock()` without RAII leaks when an exception passes.
- **Throwing from destructors.** During unwinding it terminates the program.
- **Using exceptions for ordinary results.** Return `std::optional` or a status instead.

## Revision notes

- `throw` an object; `try`/`catch` by `const&`; specific handlers first; `throw;` rethrows.
- `std::exception` → `logic_error` / `runtime_error` / `bad_alloc`; `what()` gives the message.
- Stack unwinding destroys locals in reverse order; RAII makes clean-up automatic.
- Guarantees: no-throw, strong (unchanged on failure), basic (valid and leak-free).
- Copy-and-swap achieves the strong guarantee.
- Mark moves, swaps, and destructors `noexcept`; never throw from destructors.

## Practice questions

:::question basic
Why should exceptions be caught by reference, as in `catch (const std::exception& e)`?
:::answer
Catching by reference avoids copying the exception and preserves its dynamic type, so the virtual `what()` reports the derived exception's message. Catching by value would copy only the base part (slicing), losing the derived information.
:::

:::question basic
What happens to local objects in a function when an exception passes through it?
:::answer
They are destroyed during stack unwinding, in reverse order of construction, and their destructors run. This is why resources owned by RAII objects are released automatically even when a function exits through an exception.
:::

:::question intermediate
What is the difference between the basic and the strong exception-safety guarantee?
:::answer
Both guarantee no leaks and valid objects after an exception. The strong guarantee additionally promises that the operation either completes fully or leaves the program state exactly as it was before the call; the basic guarantee allows the state to have changed, as long as it is still valid.
:::

:::question intermediate
Why is it important to mark a class's move constructor `noexcept`?
:::answer
Containers such as `std::vector` move elements during reallocation only if the move constructor is `noexcept`, because a throwing move could leave elements half-moved and break the strong guarantee. Without `noexcept`, the container copies elements instead, which is slower.
:::

:::question advanced
A function does `mutex.lock(); process(data); mutex.unlock();`, and `process` can throw. Explain the bug and fix it.
:::answer
If `process` throws, `unlock()` is never reached, so the mutex stays locked forever and other threads deadlock. Use RAII: `std::lock_guard<std::mutex> guard(mutex); process(data);`. The guard's destructor unlocks the mutex during stack unwinding as well as on normal exit.
:::

## Further learning

- **Next:** *Modern File Streams* applies RAII and exceptions to file handling.
- **Related:** *Try-Except Blocks & Custom Exceptions* in Python compares exception handling in a garbage-collected language.
