---
lesson: cpp-rule-of-five
title: Copy Control, Move Semantics & the Rule of Five
summary: The five special member functions that control copying, moving, and destruction, how move semantics transfer resources instead of copying them, and the rules of zero, three, and five.
minutes: 55
type: theory
objectives:
  - Identify the destructor, copy constructor, copy assignment, move constructor, and move assignment, and when each is called
  - Explain lvalues, rvalues, std::move, and how a move constructor steals resources and leaves the source valid
  - Apply the rule of zero, three, and five to decide which special members a class should declare
review: ai-draft
---
## Introduction

When a C++ object is copied, assigned, moved, or destroyed, one of five **special member functions** runs. For most classes, the versions the compiler writes are exactly right. For a class that directly owns a resource, such as raw heap memory, a file handle, or a socket, the defaults are wrong and can cause double frees or leaks. **Move semantics**, added in C++11, also let objects hand their resources to another object cheaply instead of copying them, which is why returning a large `std::vector` from a function is fast.

**Before you start:** you should know classes, constructors and destructors, references, and RAII.

## Core theory

### The five special members

```cpp
class Buffer {
public:
    ~Buffer();                                // destructor
    Buffer(const Buffer& other);              // copy constructor
    Buffer& operator=(const Buffer& other);   // copy assignment
    Buffer(Buffer&& other) noexcept;          // move constructor
    Buffer& operator=(Buffer&& other) noexcept; // move assignment
};
```

Copy operations make the target an independent duplicate of the source. Move operations transfer the source's resources to the target and leave the source in a **valid but unspecified** state, typically empty, which must still be safe to destroy or assign to.

### lvalues, rvalues, and std::move

An **lvalue** has a name and an identity, such as a variable. An **rvalue** is a temporary, such as the result of `a + b` or a function returning by value. An **rvalue reference**, `T&&`, binds to rvalues, so overload resolution sends temporaries to the move operations and named objects to the copy operations. `std::move(x)` does not move anything by itself: it is a cast that says "treat `x` as an rvalue; I no longer need its value", which makes the move overload eligible. After `b = std::move(a);`, do not rely on `a`'s contents.

### What a move does

For a class owning a raw pointer, the move constructor copies the pointer and size from the source and sets the source's pointer to `nullptr`, an $O(1)$ operation, instead of allocating and copying every element, an $O(n)$ operation. Marking move operations `noexcept` matters: `std::vector` moves its elements during reallocation only if the move constructor cannot throw; otherwise it copies them to keep its strong exception guarantee.

### The rules of zero, three, and five

- **Rule of zero:** design classes so that every member manages itself (`std::string`, `std::vector`, `std::unique_ptr`). Then declare **none** of the five; the compiler-generated versions are correct. This should be your default.
- **Rule of three (pre-C++11):** if a class needs a user-written destructor, copy constructor, or copy assignment, it almost certainly needs all three.
- **Rule of five:** in modern C++, a class that manages a resource directly should declare all five, adding the two move operations, or explicitly `= delete` the ones that make no sense (for example, a non-copyable file handle).

Declaring a destructor or copy operation suppresses the implicit move operations, so a class that writes only a destructor silently falls back to copying when moved.

### Copy-and-swap

A simple way to write a correct, exception-safe assignment operator is to take the parameter **by value** and swap with it: `Buffer& operator=(Buffer other) noexcept { swap(*this, other); return *this; }`. The parameter is copy-constructed or move-constructed from the argument as appropriate, and the old contents are destroyed with `other`.

## Worked examples

### Example 1: A resource-owning class with all five members

```cpp
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <utility>

class Buffer {
public:
    explicit Buffer(std::size_t n) : size_(n), data_(new int[n]()) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& other) : size_(other.size_), data_(new int[other.size_]) {
        std::copy(other.data_, other.data_ + size_, data_);
        std::cout << "copy " << size_ << " ints\n";
    }
    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            Buffer temp(other);
            swap(temp);
        }
        return *this;
    }
    Buffer(Buffer&& other) noexcept : size_(other.size_), data_(other.data_) {
        other.size_ = 0;
        other.data_ = nullptr;
        std::cout << "move " << size_ << " ints\n";
    }
    Buffer& operator=(Buffer&& other) noexcept {
        Buffer temp(std::move(other));
        swap(temp);
        return *this;
    }
    void swap(Buffer& o) noexcept { std::swap(size_, o.size_); std::swap(data_, o.data_); }
    std::size_t size() const { return size_; }
    int& operator[](std::size_t i) { return data_[i]; }

private:
    std::size_t size_;
    int* data_;
};

Buffer make_buffer() {
    Buffer b(1000);
    b[0] = 7;
    return b;
}

int main() {
    Buffer a(3);
    a[0] = 42;
    Buffer b = a;
    b[0] = 99;
    std::cout << "a[0]=" << a[0] << " b[0]=" << b[0] << '\n';
    Buffer c = std::move(a);
    std::cout << "a size " << a.size() << ", c size " << c.size() << ", c[0]=" << c[0] << '\n';
    Buffer d = make_buffer();
    std::cout << "d size " << d.size() << ", d[0]=" << d[0] << '\n';
    return 0;
}
```

Output:

```text
copy 3 ints
a[0]=42 b[0]=99
move 3 ints
a size 0, c size 3, c[0]=42
d size 1000, d[0]=7
```

Copying allocates new memory, so changing `b` leaves `a` unchanged. Moving steals `a`'s pointer and leaves `a` empty but safe to destroy. Returning `b` from `make_buffer` printed neither "copy" nor "move": the compiler constructed the object directly in `d` (named return value optimisation), and if it could not, it would have moved, never copied.

### Example 2: The rule of zero

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

class Playlist {
public:
    explicit Playlist(std::string name) : name_(std::move(name)) {}
    void add(std::string song) { songs_.push_back(std::move(song)); }
    std::size_t size() const { return songs_.size(); }
    const std::string& name() const { return name_; }
private:
    std::string name_;
    std::vector<std::string> songs_;
};

int main() {
    Playlist p("road trip");
    p.add("song A");
    p.add("song B");
    Playlist copy = p;
    copy.add("song C");
    Playlist moved = std::move(p);
    std::cout << copy.name() << ": " << copy.size() << " songs\n";
    std::cout << moved.name() << ": " << moved.size() << " songs\n";
    std::unique_ptr<int> owner = std::make_unique<int>(5);
    auto taken = std::move(owner);
    std::cout << "owner empty: " << (owner == nullptr) << ", taken = " << *taken << '\n';
    return 0;
}
```

Output:

```text
road trip: 3 songs
road trip: 2 songs
owner empty: 1, taken = 5
```

`Playlist` declares none of the special members, yet copying and moving work correctly because `std::string` and `std::vector` already implement them. That is the rule of zero.

## Applications

- **Containers:** `std::vector` moves elements during growth when their move constructors are `noexcept`.
- **Returning large objects:** functions return vectors and strings by value at no copying cost.
- **Unique resources:** file handles and sockets are movable but not copyable.
- **Performance tuning:** `std::move` into containers avoids needless string copies.

## Common mistakes

- **Writing a destructor but not copy operations for a raw owning pointer.** Copies double-delete.
- **Forgetting to null out the source in a move.** Both objects then free the same memory.
- **Using an object after moving from it.** Only assign to it or destroy it.
- **Omitting `noexcept` on move operations.** Containers then copy instead of move.
- **Writing special members that the compiler would generate correctly.** Prefer the rule of zero.

## Revision notes

- Five special members: destructor, copy constructor, copy assignment, move constructor, move assignment.
- `T&&` binds to rvalues; `std::move` is a cast to rvalue.
- Moves transfer resources in $O(1)$ and leave the source valid but unspecified.
- Mark moves `noexcept`.
- Rule of zero by default; rule of five when directly managing a resource; `= delete` what makes no sense.
- Copy-and-swap gives simple, exception-safe assignment.

## Practice questions

:::question basic
What does `std::move(x)` actually do?
:::answer
It is a cast that turns `x` into an rvalue reference. It does not move anything itself, but it allows overload resolution to choose a move constructor or move assignment operator, which then transfers `x`'s resources.
:::

:::question basic
What is the rule of zero?
:::answer
Design a class so that all of its members manage their own resources, for example `std::string`, `std::vector`, and smart pointers, and declare none of the five special member functions. The compiler-generated versions then copy, move, and destroy correctly.
:::

:::question intermediate
Why should a move constructor set the source object's pointer to `nullptr`?
:::answer
After the move, the target owns the memory. If the source kept the same pointer, its destructor would delete the memory too, causing a double delete, or later use would modify the target's data. Nulling the pointer leaves the source empty and safe to destroy.
:::

:::question intermediate
A class defines only a destructor. What happens when an object of this class is moved?
:::answer
Declaring a destructor suppresses the implicitly generated move operations, so a "move" falls back to the copy constructor. The program still works if the copy is correct, but it silently copies instead of moving, and if the class owns a raw pointer, the default copy causes a double delete.
:::

:::question advanced
Why does `std::vector<T>` copy elements during reallocation when `T`'s move constructor is not `noexcept`?
:::answer
`push_back` promises the strong exception guarantee: if it throws, the vector is unchanged. If elements were moved into the new block and a later move threw, the already-moved elements could not be restored, breaking that promise. Copying leaves the original elements intact, so the vector moves only when moves are guaranteed not to throw (`std::move_if_noexcept`).
:::

## Further learning

- **Next:** *Operator Overloading* covers the assignment operators alongside other operators.
- **Related:** *Smart Pointers & RAII Paradigm* shows move-only ownership with `std::unique_ptr`.
