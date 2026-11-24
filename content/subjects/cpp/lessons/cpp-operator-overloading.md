---
lesson: cpp-operator-overloading
title: Operator Overloading
summary: Giving user-defined types natural syntax by overloading arithmetic, comparison, subscript, stream, and compound-assignment operators, and the guidelines that keep overloaded operators unsurprising.
minutes: 45
type: theory
objectives:
  - Overload arithmetic and compound-assignment operators as member or non-member functions and explain the choice
  - Overload comparison, subscript, and stream insertion operators with correct parameter and return types
  - Follow the conventions that make overloaded operators behave like their built-in counterparts
review: ai-draft
---
## Introduction

Built-in types let you write `a + b`, `a == b`, and `std::cout << a`. **Operator overloading** gives your own types the same natural syntax: `v1 + v2` for vectors, `m * n` for matrices, `price * 3` for money, and `std::cout << date`. Done well, it makes code read like mathematics. Done badly, with `+` meaning something other than addition, it makes code baffling. This lesson shows the standard patterns.

**Before you start:** you should know classes, constructors, references, and `const` member functions.

## Core theory

### How overloading works

An overloaded operator is a function named `operator@` for some operator `@`. `a + b` calls either the member function `a.operator+(b)` or the non-member function `operator+(a, b)`. You cannot create new operators, change precedence or the number of operands, or overload operators for built-in types only. A few operators (`::`, `.`, `.*`, `?:`) cannot be overloaded at all.

### Member or non-member?

- Operators that modify the left operand, such as `+=`, `-=`, `=`, `[]`, and `()`, are written as **members**, and `=`, `[]`, `()`, and `->` must be.
- Symmetric binary operators such as `+`, `-`, `*`, `==`, and `<` are best written as **non-members**, so that conversions apply to both operands equally; `2 * v` can only work as a non-member, because `2` is not a class object.
- The stream operators `<<` and `>>` must be non-members, because the left operand is a stream.

A common pattern implements `+` in terms of `+=`: `Vec operator+(Vec a, const Vec& b) { a += b; return a; }`.

### Conventions

| Operator | Usual signature | Notes |
| :--- | :--- | :--- |
| `a += b` | `T& operator+=(const T& b)` | modifies `*this`, returns `*this` |
| `a + b` | `T operator+(T a, const T& b)` | returns a new value |
| `a == b` | `bool operator==(const T&, const T&)` | define `!=` consistently |
| `a < b` | `bool operator<(const T&, const T&)` | must be a strict weak ordering for sorting |
| `a[i]` | `T& operator[](size_t)` plus a `const` overload | no bounds check by convention |
| `os << a` | `std::ostream& operator<<(std::ostream&, const T&)` | return the stream for chaining |
| `-a` | `T operator-() const` | unary minus |

C++20 can generate all six comparisons from a defaulted `operator<=>` and `operator==`; in C++17 you write them yourself.

### Keep operators unsurprising

An overloaded operator should do what a reader expects from its built-in meaning: `+` should not modify its operands, `==` should be symmetric and consistent with `!=`, and `<` must be consistent so that `std::sort` and `std::map` work. If no operator has an obvious meaning for an operation, use a named function instead.

## Worked examples

### Example 1: A 2-D vector type

```cpp
#include <cmath>
#include <iostream>

class Vec2 {
public:
    Vec2(double x = 0, double y = 0) : x_(x), y_(y) {}
    double x() const { return x_; }
    double y() const { return y_; }
    Vec2& operator+=(const Vec2& o) { x_ += o.x_; y_ += o.y_; return *this; }
    Vec2& operator*=(double k) { x_ *= k; y_ *= k; return *this; }
    Vec2 operator-() const { return {-x_, -y_}; }
    double length() const { return std::sqrt(x_ * x_ + y_ * y_); }
private:
    double x_, y_;
};

Vec2 operator+(Vec2 a, const Vec2& b) { a += b; return a; }
Vec2 operator*(Vec2 v, double k) { v *= k; return v; }
Vec2 operator*(double k, Vec2 v) { v *= k; return v; }
bool operator==(const Vec2& a, const Vec2& b) { return a.x() == b.x() && a.y() == b.y(); }
bool operator!=(const Vec2& a, const Vec2& b) { return !(a == b); }
std::ostream& operator<<(std::ostream& os, const Vec2& v) { return os << '(' << v.x() << ", " << v.y() << ')'; }

int main() {
    Vec2 a(3, 4), b(1, -2);
    Vec2 c = a + b;
    std::cout << a << " + " << b << " = " << c << '\n';
    std::cout << "2 * a = " << 2 * a << ", a * 0.5 = " << a * 0.5 << '\n';
    std::cout << "-b = " << -b << ", |a| = " << a.length() << '\n';
    c += Vec2(1, 1);
    std::cout << "c after += : " << c << ", equal to (5, 3)? " << (c == Vec2(5, 3)) << '\n';
    return 0;
}
```

Output:

```text
(3, 4) + (1, -2) = (4, 2)
2 * a = (6, 8), a * 0.5 = (1.5, 2)
-b = (-1, 2), |a| = 5
c after += : (5, 3), equal to (5, 3)? 1
```

The compound operators are members that modify the object; `+` and `*` are non-members built from them. Writing `2 * a` works because there is a non-member overload taking `double` on the left.

### Example 2: Subscript, comparison for sorting, and streaming

```cpp
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Student {
    std::string name;
    int marks;
};

bool operator<(const Student& a, const Student& b) {
    if (a.marks != b.marks) return a.marks > b.marks;
    return a.name < b.name;
}

std::ostream& operator<<(std::ostream& os, const Student& s) { return os << s.name << '(' << s.marks << ')'; }

class Roster {
public:
    void add(Student s) { list_.push_back(std::move(s)); }
    Student& operator[](std::size_t i) { return list_[i]; }
    const Student& operator[](std::size_t i) const { return list_[i]; }
    std::size_t size() const { return list_.size(); }
    void sort() { std::sort(list_.begin(), list_.end()); }
private:
    std::vector<Student> list_;
};

int main() {
    Roster r;
    r.add({"Ravi", 78});
    r.add({"Asha", 91});
    r.add({"John", 78});
    r[0].marks += 2;
    r.sort();
    for (std::size_t i = 0; i < r.size(); i++) std::cout << r[i] << ' ';
    std::cout << '\n';
    const Roster& view = r;
    std::cout << "top: " << view[0] << '\n';
    return 0;
}
```

Output:

```text
Asha(91) Ravi(80) John(78)
top: Asha(91)
```

`operator<` defines "comes first" as higher marks, then alphabetical name, so `std::sort` ranks the roster without a separate comparator. The `const` overload of `operator[]` lets a `const` roster be read but not modified.

## Applications

- **Mathematics:** vectors, matrices, complex numbers, and big integers use arithmetic operators.
- **Containers:** `operator[]` gives custom containers array-like access.
- **Sorting and maps:** `operator<` lets types be sorted and used as `std::map` keys.
- **Debugging and logging:** `operator<<` prints objects with `std::cout`.

## Common mistakes

- **Making `+` modify its left operand.** Return a new value; let `+=` modify.
- **Returning a stream by value from `operator<<`.** Streams cannot be copied; return `std::ostream&`.
- **Defining `==` without `!=` (in C++17).** Users expect both; define one in terms of the other.
- **An inconsistent `operator<`.** If `a < b` and `b < a` can both be true, sorting misbehaves.
- **Overloading operators with surprising meanings.** Use named functions instead.

## Revision notes

- `a @ b` calls `a.operator@(b)` or `operator@(a, b)`.
- Members: `=`, `[]`, `()`, `->`, compound assignments. Non-members: symmetric binary operators and `<<`/`>>`.
- Implement `+` with `+=`; return `*this` by reference from compound assignments.
- `operator<<(std::ostream&, const T&)` returns the stream.
- Provide `const` and non-`const` `operator[]`.
- Keep the built-in meaning; `operator<` must be a strict weak ordering.

## Practice questions

:::question basic
Why must `operator<<` for printing be a non-member function?
:::answer
In `std::cout << obj`, the left operand is a `std::ostream`, not your class. A member function would need to be a member of `std::ostream`, which you cannot modify, so it must be a non-member taking the stream as its first parameter.
:::

:::question basic
What should `operator+=` return, and why?
:::answer
It should return `*this` by reference (`T&`). That matches the built-in behaviour, allows chaining such as `(a += b) += c`, and avoids an unnecessary copy.
:::

:::question intermediate
Why is `Vec2 operator+(Vec2 a, const Vec2& b)` a good signature?
:::answer
Taking the left operand by value gives the function its own copy to modify with `+=`, and that copy can be moved from when the caller passes a temporary. Taking the right operand by `const` reference avoids a copy and guarantees it is not changed. The function returns a new value, leaving the caller's objects untouched.
:::

:::question intermediate
Why does `2 * v` fail to compile if multiplication is only defined as a member `Vec2 Vec2::operator*(double)`?
:::answer
A member operator is called on the left operand, so `2 * v` would need `2.operator*(v)`, which is impossible for a `double`. A non-member overload `Vec2 operator*(double, Vec2)` handles a number on the left.
:::

:::question advanced
What properties must `operator<` have for `std::sort` and `std::map` to work, and give an example of a broken one?
:::answer
It must be a strict weak ordering: irreflexive (`a < a` is false), asymmetric (if `a < b` then not `b < a`), transitive, and with transitive equivalence. Defining `a < b` as `a.marks <= b.marks` is broken, because it makes `a < a` true for every object; `std::sort` may then read out of bounds or loop incorrectly, and `std::map` may fail to find keys.
:::

## Further learning

- **Next:** *Inheritance Models & Base Classes* combines classes into hierarchies.
- **Related:** *STL Containers & Iterators* relies on `operator<` and `operator==` for ordered and unordered containers.
