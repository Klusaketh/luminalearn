---
lesson: cpp-smart-pointers-raii
title: Smart Pointers & RAII Paradigm
summary: The RAII idiom, in which objects acquire resources in constructors and release them in destructors, and the smart pointers unique_ptr, shared_ptr, and weak_ptr that make manual delete unnecessary.
minutes: 45
type: theory
objectives:
  - Explain RAII and why destructors make resource clean-up automatic and exception-safe
  - Use std::unique_ptr and std::make_unique for exclusive ownership and move ownership between objects
  - Use std::shared_ptr and std::weak_ptr for shared ownership, and explain reference counting and cycles
review: ai-draft
---
## Introduction

In C, every `malloc` needs a matching `free`, every `fopen` a matching `fclose`, and a single early `return` or error can skip the clean-up. C++ solves this with a simple, powerful idea called **RAII**, Resource Acquisition Is Initialization: tie each resource to the lifetime of an object whose destructor releases it. Because destructors run automatically, clean-up can no longer be forgotten. **Smart pointers** apply RAII to heap memory, which is why modern C++ code almost never calls `delete`.

**Before you start:** you should know classes at a basic level, references, and how heap memory works.

## Core theory

### Destructors and RAII

A class's **destructor**, written `~ClassName()`, runs automatically when an object's lifetime ends: when a local variable goes out of scope, when a containing object is destroyed, or when the stack is **unwound** by an exception. RAII puts the release of a resource in the destructor:

```cpp
class File {
    std::FILE* f;
public:
    explicit File(const char* path) : f(std::fopen(path, "w")) {}
    ~File() { if (f) std::fclose(f); }
};
```

Whatever path leaves the scope, normal end, `return`, or exception, the file is closed. `std::vector`, `std::string`, `std::fstream`, and `std::lock_guard` all work this way.

### std::unique_ptr: exclusive ownership

`std::unique_ptr<T>` owns a heap object and deletes it in its destructor. Create one with `auto p = std::make_unique<T>(args...);`. It cannot be copied, since two owners would delete the object twice, but it can be **moved**: `auto q = std::move(p);` transfers ownership, leaving `p` empty (null). Functions return `unique_ptr` to hand ownership to the caller. It has no overhead compared with a raw pointer, so it is the default choice for owning heap objects.

### std::shared_ptr: shared ownership

`std::shared_ptr<T>`, created with `std::make_shared<T>(...)`, allows several owners. A **reference count** in a control block tracks how many `shared_ptr`s point to the object; copying increments it, destroying a `shared_ptr` decrements it, and when it reaches zero the object is deleted. `use_count()` reports the count. Shared ownership costs a little more (the count is updated atomically) and should be used only when ownership is genuinely shared.

### std::weak_ptr and cycles

If two objects hold `shared_ptr`s to each other, their counts never reach zero and both leak: a **reference cycle**. A `std::weak_ptr` observes an object owned by `shared_ptr`s without increasing the count. To use it, call `lock()`, which returns a `shared_ptr` that is empty if the object has already been destroyed. Typical use: a child holds a `weak_ptr` to its parent.

### Raw pointers today

Raw pointers and references are still fine for **non-owning** access, for example passing an object to a function that just uses it. The rule of thumb: own with smart pointers or containers, observe with references or raw pointers, and never write `delete` yourself.

## Worked examples

### Example 1: Destructors run automatically, even with exceptions

```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

struct Tracker {
    std::string name;
    explicit Tracker(std::string n) : name(std::move(n)) { std::cout << "acquire " << name << '\n'; }
    ~Tracker() { std::cout << "release " << name << '\n'; }
};

void risky(bool fail) {
    Tracker local("local");
    auto heap = std::make_unique<Tracker>("heap");
    if (fail) throw std::runtime_error("something failed");
    std::cout << "work done\n";
}

int main() {
    risky(false);
    try {
        risky(true);
    } catch (const std::exception& e) {
        std::cout << "caught: " << e.what() << '\n';
    }
    return 0;
}
```

Output:

```text
acquire local
acquire heap
work done
release heap
release local
acquire local
acquire heap
release heap
release local
caught: something failed
```

Objects are destroyed in reverse order of construction. When the exception is thrown, stack unwinding still runs both destructors before the `catch` block executes, so nothing leaks.

### Example 2: unique_ptr moves and shared_ptr counts

```cpp
#include <iostream>
#include <memory>
#include <vector>

struct Doc {
    int id;
    explicit Doc(int i) : id(i) {}
    ~Doc() { std::cout << "doc " << id << " freed\n"; }
};

std::unique_ptr<Doc> open_doc(int id) { return std::make_unique<Doc>(id); }

int main() {
    auto a = open_doc(1);
    auto b = std::move(a);
    std::cout << "a empty: " << (a == nullptr) << ", b owns doc " << b->id << '\n';

    auto shared = std::make_shared<Doc>(2);
    std::weak_ptr<Doc> watcher = shared;
    {
        std::vector<std::shared_ptr<Doc>> owners = {shared, shared};
        std::cout << "count with vector: " << shared.use_count() << '\n';
    }
    std::cout << "count after vector: " << shared.use_count() << '\n';
    shared.reset();
    std::cout << "watcher expired: " << watcher.expired() << '\n';
    std::cout << "end of main\n";
    return 0;
}
```

Output:

```text
a empty: 1, b owns doc 1
count with vector: 3
count after vector: 1
doc 2 freed
watcher expired: 1
end of main
doc 1 freed
```

Moving transfers doc 1 to `b`. The vector's two copies raise doc 2's count to 3, and destroying the vector drops it back to 1. `reset()` releases the last owner, so doc 2 is freed at once and the `weak_ptr` reports it as expired. Doc 1 is freed when `b` goes out of scope at the end of `main`.

## Applications

- **Memory safety:** owning heap objects through `unique_ptr` removes leaks and double deletes.
- **Locks:** `std::lock_guard` releases a mutex when the scope ends, even on exceptions.
- **Caches and graphs:** `shared_ptr` and `weak_ptr` model shared and observing relationships.
- **Factories:** functions return `unique_ptr` to hand ownership to the caller clearly.

## Common mistakes

- **Writing `new` and `delete` by hand.** Use `make_unique`, `make_shared`, or containers.
- **Copying a `unique_ptr`.** It does not compile; use `std::move` to transfer ownership.
- **Using `shared_ptr` everywhere.** It costs more and hides who owns what; prefer `unique_ptr`.
- **Creating `shared_ptr` cycles.** Break them with `weak_ptr`.
- **Using a pointer after `std::move`.** The moved-from `unique_ptr` is null.

## Revision notes

- RAII: acquire in the constructor, release in the destructor.
- Destructors run on scope exit and during exception unwinding, in reverse order.
- `unique_ptr`: sole owner, move-only, zero overhead; create with `make_unique`.
- `shared_ptr`: reference-counted shared ownership; `use_count()`; create with `make_shared`.
- `weak_ptr`: non-owning observer; `lock()` or `expired()`; breaks cycles.
- Own with smart pointers; observe with references or raw pointers.

## Practice questions

:::question basic
What does RAII stand for, and what is the core idea?
:::answer
Resource Acquisition Is Initialization. Each resource is owned by an object: the constructor acquires it and the destructor releases it, so the resource's lifetime matches the object's scope and clean-up happens automatically.
:::

:::question basic
Why can a `std::unique_ptr` not be copied?
:::answer
It represents exclusive ownership. A copy would create two owners, and both would delete the same object, causing a double delete. Ownership can only be transferred with a move, which leaves the source empty.
:::

:::question intermediate
After `auto p = std::make_shared<int>(5); auto q = p; auto r = q;`, what is `p.use_count()`, and what happens when `q.reset()` is called?
:::answer
`use_count()` is 3, because `p`, `q`, and `r` all share ownership. `q.reset()` releases `q`'s share and the count falls to 2; the integer stays alive because `p` and `r` still own it.
:::

:::question intermediate
Why does code that throws an exception between `new` and `delete` leak memory, while the `make_unique` version does not?
:::answer
When an exception is thrown, control jumps straight to the handler and the `delete` statement is skipped, so the object is never freed. A `unique_ptr` is a local object whose destructor runs during stack unwinding, and that destructor deletes the object.
:::

:::question advanced
A `Parent` holds `std::vector<std::shared_ptr<Child>>`, and each `Child` holds `std::shared_ptr<Parent>`. Explain the leak and fix it.
:::answer
Parent and children own each other, so each object's reference count stays at least 1 even after all outside owners are gone; nothing reaches zero and no destructor runs. Make the back-pointer non-owning: `std::weak_ptr<Parent> parent;` in `Child`. Children then do not keep the parent alive, and a child that needs the parent calls `parent.lock()` and checks the result.
:::

## Further learning

- **Next:** *Class Encapsulation & Constructors* shows how to write classes with constructors and destructors.
- **Related:** *Copy Control, Move Semantics & the Rule of Five* explains moves in depth.
