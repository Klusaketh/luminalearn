---
lesson: cpp-class-encapsulation
title: Class Encapsulation & Constructors
summary: Designing C++ classes: public and private access, constructors with member initializer lists, const member functions, the copy constructor, and invariants that keep objects valid.
minutes: 45
type: theory
objectives:
  - Define classes with private data, public member functions, and constructors that establish invariants
  - Use member initializer lists, default member initializers, and const member functions correctly
  - Explain when the copy constructor runs and what the compiler-generated version does
review: ai-draft
---
## Introduction

A **class** bundles data with the operations that act on it, and **encapsulation** hides the data behind those operations so that the rest of the program cannot put an object into an invalid state. A `BankAccount` whose balance can only change through `deposit` and `withdraw` can guarantee that the balance is never negative. This lesson covers how C++ expresses classes: access control, constructors, initializer lists, `const` member functions, and copying.

**Before you start:** you should know C++ basic syntax, references, `std::string`, and `std::vector`.

## Core theory

### Access control

```cpp
class Account {
public:
    void deposit(double amount);
    double balance() const;
private:
    double balance_ = 0;
};
```

Members after `public:` can be used by any code; members after `private:` only by the class's own member functions (and friends). A `struct` is the same as a `class` except that its members are public by default. The usual design makes data private and exposes a small set of member functions that maintain the class's **invariant**, a condition that is always true for a valid object, such as "the balance is never negative".

### Constructors and initializer lists

A **constructor** has the class's name and no return type; it runs when an object is created and should leave it valid. The **member initializer list** initialises members directly, before the constructor body runs:

```cpp
Account(std::string owner, double opening)
    : owner_(std::move(owner)), balance_(opening) {
    if (balance_ < 0) throw std::invalid_argument("negative opening balance");
}
```

Initializer lists are required for `const` members, reference members, and members without a default constructor, and they avoid default-constructing a member and then assigning to it. Members are initialised in the order they are **declared** in the class, not the order in the list. **Default member initializers** (`double balance_ = 0;`) supply values when a constructor does not. Mark single-argument constructors `explicit` to prevent surprising implicit conversions.

### const member functions

A member function declared with `const` after its parameter list promises not to modify the object: `double balance() const;`. Only `const` member functions can be called on a `const` object or through a `const` reference, so getters and other read-only operations should always be `const`.

### this and static members

Inside a member function, `this` is a pointer to the current object; `return *this;` lets calls be chained. A `static` data member is shared by all objects of the class, and a `static` member function has no `this`.

### Copying objects

The **copy constructor**, `Account(const Account& other)`, creates a new object as a copy of an existing one. It runs when you initialise from another object (`Account b = a;`), pass by value, or return by value (though compilers often elide such copies). If you do not write one, the compiler generates a copy constructor that copies each member. That is correct when every member manages itself (`std::string`, `std::vector`, numbers) and wrong when a member is a raw owning pointer, because both copies would point to the same memory. The **copy assignment operator** (`b = a;` for existing objects) follows the same rules.

## Worked examples

### Example 1: An encapsulated account with an invariant

```cpp
#include <iostream>
#include <stdexcept>
#include <string>

class Account {
public:
    Account(std::string owner, double opening) : owner_(std::move(owner)), balance_(opening) {
        if (balance_ < 0) throw std::invalid_argument("negative opening balance");
        ++count_;
    }
    Account& deposit(double amount) {
        if (amount <= 0) throw std::invalid_argument("deposit must be positive");
        balance_ += amount;
        return *this;
    }
    bool withdraw(double amount) {
        if (amount <= 0 || amount > balance_) return false;
        balance_ -= amount;
        return true;
    }
    double balance() const { return balance_; }
    const std::string& owner() const { return owner_; }
    static int count() { return count_; }

private:
    std::string owner_;
    double balance_ = 0;
    static inline int count_ = 0;
};

int main() {
    Account a("Asha", 100);
    a.deposit(50).deposit(25);
    std::cout << a.owner() << ": " << a.balance() << '\n';
    std::cout << "withdraw 500: " << a.withdraw(500) << ", withdraw 75: " << a.withdraw(75) << '\n';
    std::cout << "balance " << a.balance() << '\n';
    try {
        Account bad("Zed", -10);
    } catch (const std::invalid_argument& e) {
        std::cout << "rejected: " << e.what() << '\n';
    }
    const Account& view = a;
    std::cout << "via const ref: " << view.balance() << ", accounts created: " << Account::count() << '\n';
    return 0;
}
```

Output:

```text
Asha: 175
withdraw 500: 0, withdraw 75: 1
balance 100
rejected: negative opening balance
via const ref: 100, accounts created: 1
```

Outside code cannot change `balance_` directly, so the only paths are checked member functions and the balance can never go negative. Returning `*this` from `deposit` allows chaining. The constructor that throws never increments the counter, because the object was never successfully created.

### Example 2: When the copy constructor runs

```cpp
#include <iostream>
#include <string>

class Label {
public:
    explicit Label(std::string text) : text_(std::move(text)) { std::cout << "construct " << text_ << '\n'; }
    Label(const Label& other) : text_(other.text_ + "-copy") { std::cout << "copy " << text_ << '\n'; }
    const std::string& text() const { return text_; }
private:
    std::string text_;
};

void by_value(Label l) { std::cout << "by value: " << l.text() << '\n'; }
void by_ref(const Label& l) { std::cout << "by ref: " << l.text() << '\n'; }

int main() {
    Label a("title");
    Label b = a;
    by_ref(a);
    by_value(a);
    std::cout << b.text() << '\n';
    return 0;
}
```

Output:

```text
construct title
copy title-copy
by ref: title
copy title-copy
by value: title-copy
title-copy
```

Initialising `b` from `a` and passing `a` by value both call the copy constructor; passing by `const` reference does not. The custom copy constructor here appends a suffix only to make each copy visible.

## Applications

- **Domain modelling:** classes like `Account`, `Matrix`, and `Date` keep data valid through their interfaces.
- **Libraries:** encapsulation lets implementations change without breaking users.
- **Resource wrappers:** classes own files, sockets, and buffers safely.
- **Value types:** small classes with correct copying behave like built-in types.

## Common mistakes

- **Making data public.** Any code can then break the invariant; expose operations instead.
- **Forgetting `const` on getters.** They then cannot be called on `const` objects or references.
- **Relying on initializer-list order.** Members are initialised in declaration order; keep both orders the same.
- **Default copying of owning raw pointers.** Two objects then share and both delete the same memory; use smart pointers or write copy operations.

## Revision notes

- `private` data, `public` operations; a class maintains its invariant.
- Constructors establish the invariant; throw if they cannot.
- Initializer lists initialise members directly, in declaration order.
- `const` member functions do not modify the object and work on `const` objects.
- `explicit` single-argument constructors prevent implicit conversions.
- Copy constructor runs on copy-initialisation and pass/return by value; the default copies member by member.

## Practice questions

:::question basic
What is the difference between `class` and `struct` in C++?
:::answer
They are identical except for default access: members and base classes of a `class` are private by default, while those of a `struct` are public by default.
:::

:::question basic
Why should a getter such as `double balance()` be declared `const`?
:::answer
A `const` member function promises not to modify the object, so it can be called on `const` objects and through `const` references, which is how objects are often passed. Without `const`, `view.balance()` on a `const Account& view` would not compile.
:::

:::question intermediate
Which members must be initialised in the member initializer list rather than in the constructor body?
:::answer
`const` data members, reference members, and members of class types without a default constructor. They cannot be default-constructed and then assigned later, so they must be initialised directly in the list.
:::

:::question intermediate
Name three situations in which a copy constructor may be called.
:::answer
Initialising a new object from an existing one (`Label b = a;`), passing an object to a function by value, and returning an object by value (although the compiler often elides this copy). Assigning to an already existing object uses the copy assignment operator instead.
:::

:::question advanced
A class stores `int* data` allocated with `new int[n]` and frees it in its destructor, but has no user-defined copy constructor. What happens when an object is copied and both copies go out of scope?
:::answer
The compiler-generated copy constructor copies the pointer value, so both objects point to the same array. When the first is destroyed it deletes the array; the second then holds a dangling pointer and deletes the same memory again, which is undefined behaviour (a double delete). The fix is to use `std::vector<int>` or `std::unique_ptr<int[]>`, or to implement correct copy operations (the rule of three or five).
:::

## Further learning

- **Next:** *Copy Control, Move Semantics & the Rule of Five* explains when you must write copy and move operations.
- **Related:** *Operator Overloading* gives classes natural syntax such as `a + b` and `std::cout << a`.
