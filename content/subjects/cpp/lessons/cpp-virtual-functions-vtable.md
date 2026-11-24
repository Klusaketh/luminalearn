---
lesson: cpp-virtual-functions-vtable
title: Virtual Functions & VTable Dispatch
summary: Run-time polymorphism in C++: virtual functions and override, abstract classes with pure virtual functions, virtual destructors, object slicing, and how compilers implement dynamic dispatch with vtables.
minutes: 45
type: theory
objectives:
  - Declare virtual functions and overrides and predict which function a call through a base reference or pointer runs
  - Design abstract interfaces with pure virtual functions and explain why base classes need virtual destructors
  - Explain the vtable and vptr mechanism, its costs, and the object slicing problem
review: ai-draft
---
## Introduction

Inheritance alone does not make a program polymorphic: if a function takes a `Shape&` and calls `area()`, C++ normally runs `Shape::area`, whatever the actual object is. Declaring the function **virtual** changes that, so the call runs the version belonging to the object's real type at run time. This **dynamic dispatch** is what lets one loop draw circles, squares, and triangles, and lets frameworks call your code through interfaces they defined long before you wrote it.

**Before you start:** you should know classes, inheritance, constructors and destructors, and references and pointers.

## Core theory

### Static versus dynamic binding

For a non-virtual function, the compiler chooses the function from the **static type** of the expression, the type it is declared as. For a **virtual** function called through a reference or pointer, the function is chosen from the **dynamic type**, the type of the actual object, at run time.

```cpp
class Shape {
public:
    virtual double area() const { return 0; }
    virtual ~Shape() = default;
};
class Circle : public Shape {
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override { return 3.14159 * r_ * r_; }
private:
    double r_;
};
```

`override` asks the compiler to check that the function really overrides a base virtual function; a mismatch, such as forgetting `const`, becomes an error instead of a silently separate function. `final` prevents further overriding.

### Abstract classes

A **pure virtual** function, `virtual double area() const = 0;`, has no implementation in the base. A class with at least one pure virtual function is **abstract**: you cannot create objects of it, only of derived classes that override every pure virtual function. Abstract classes define **interfaces**: code depends on `Shape&`, and new shapes can be added without changing that code.

### Virtual destructors

If a derived object is deleted through a base pointer (`delete shape_ptr;` or a `std::unique_ptr<Shape>`), the base class must have a **virtual destructor**; otherwise only the base part is destroyed and the behaviour is undefined, typically leaking the derived part's resources. Rule: a class meant to be used polymorphically gets `virtual ~Base() = default;`.

### How dispatch works: vtables

Compilers typically implement virtual functions with a **virtual table** (vtable) per class: an array of pointers to that class's implementations of each virtual function. Every object of a class with virtual functions carries a hidden pointer, the **vptr**, to its class's vtable. A virtual call loads the vptr, looks up the function's slot, and calls through that pointer. The costs: one pointer per object, an indirect call that the compiler usually cannot inline, and a vtable per class. These are small, but they are why C++ does not make every function virtual by default.

During construction and destruction, the object's dynamic type is the class whose constructor or destructor is running, so a virtual call inside a base constructor runs the base version, never a derived override.

### Object slicing

Polymorphism needs references or pointers. Copying a derived object into a base **value**, as in `Shape s = circle;` or passing by value to `void f(Shape s)`, copies only the base part: the object is **sliced**, and `s.area()` runs `Shape::area`. Store polymorphic objects as `std::unique_ptr<Base>` in containers and pass them by reference.

## Worked examples

### Example 1: Dynamic dispatch through an abstract interface

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual std::string name() const = 0;
    std::string describe() const { return name() + " with area " + std::to_string(area()); }
};

class Rect : public Shape {
public:
    Rect(double w, double h) : w_(w), h_(h) {}
    double area() const override { return w_ * h_; }
    std::string name() const override { return "rect"; }
private:
    double w_, h_;
};

class Square final : public Rect {
public:
    explicit Square(double s) : Rect(s, s) {}
    std::string name() const override { return "square"; }
};

class Triangle : public Shape {
public:
    Triangle(double b, double h) : b_(b), h_(h) {}
    double area() const override { return 0.5 * b_ * h_; }
    std::string name() const override { return "triangle"; }
private:
    double b_, h_;
};

double total_area(const std::vector<std::unique_ptr<Shape>>& shapes) {
    double sum = 0;
    for (const auto& s : shapes) sum += s->area();
    return sum;
}

int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Rect>(2, 3));
    shapes.push_back(std::make_unique<Square>(4));
    shapes.push_back(std::make_unique<Triangle>(6, 2));
    for (const auto& s : shapes) std::cout << s->describe() << '\n';
    std::cout << "total " << total_area(shapes) << '\n';
    return 0;
}
```

Output:

```text
rect with area 6.000000
square with area 16.000000
triangle with area 6.000000
total 28
```

`describe` is an ordinary base function, but its calls to `name()` and `area()` are virtual, so each object reports its own type. `Square` inherits `area` from `Rect` and overrides only `name`. The `unique_ptr<Shape>` destructors call the right derived destructors because `~Shape` is virtual.

### Example 2: Slicing, constructor calls, and missing override

```cpp
#include <iostream>

struct Animal {
    Animal() { std::cout << "constructing as " << kind() << '\n'; }
    virtual ~Animal() = default;
    virtual const char* kind() const { return "animal"; }
    virtual const char* sound() const { return "..."; }
};

struct Dog : Animal {
    const char* kind() const override { return "dog"; }
    const char* sound() const override { return "woof"; }
};

void by_ref(const Animal& a) { std::cout << "by ref: " << a.sound() << '\n'; }
void by_value(Animal a) { std::cout << "by value: " << a.sound() << '\n'; }

int main() {
    Dog d;
    by_ref(d);
    by_value(d);
    Animal* p = &d;
    std::cout << "through pointer: " << p->kind() << '\n';
    std::cout << "sizeof(Dog) includes a vptr: " << (sizeof(Dog) >= sizeof(void*)) << '\n';
    return 0;
}
```

Output:

```text
constructing as animal
by ref: woof
by value: ...
through pointer: dog
sizeof(Dog) includes a vptr: 1
```

While the `Animal` part is being constructed, the object is still an `Animal`, so `kind()` returns "animal" even though a `Dog` is being built. Passing by reference keeps the dynamic type; passing by value slices the `Dog` down to an `Animal`.

## Applications

- **Plug-in architectures:** applications define interfaces; plug-ins implement them.
- **GUI and game engines:** widgets and entities override `draw()` and `update()`.
- **Testing:** code that depends on an interface can be given a fake implementation.
- **Standard library:** `std::exception::what()` is virtual, so catching by reference reports the real error.

## Common mistakes

- **Forgetting `virtual` in the base.** Calls through base references then run the base version.
- **Missing virtual destructor.** Deleting through a base pointer is undefined behaviour.
- **Signature mismatches without `override`.** A missing `const` creates a new function instead of overriding; always write `override`.
- **Storing polymorphic objects by value.** They are sliced; use pointers or references.
- **Calling virtual functions in constructors expecting derived behaviour.** The base version runs.

## Revision notes

- Virtual + reference/pointer = dispatch on the object's dynamic type.
- `override` checks overriding; `final` stops it.
- `= 0` makes a pure virtual function; a class with one is abstract.
- Polymorphic bases need `virtual ~Base()`.
- Typical implementation: per-class vtable, per-object vptr, indirect call.
- Copying into a base value slices; inside constructors, virtual calls use the class under construction.

## Practice questions

:::question basic
What is the difference between a virtual and a non-virtual member function when called through a base-class reference?
:::answer
A non-virtual call is bound at compile time using the reference's declared (static) type, so the base version runs. A virtual call is bound at run time using the actual object's (dynamic) type, so the derived override runs.
:::

:::question basic
What makes a class abstract, and what can you not do with it?
:::answer
A class with at least one pure virtual function (declared `= 0`) is abstract. You cannot create objects of it directly; you can only use it through references or pointers to objects of derived classes that implement all its pure virtual functions.
:::

:::question intermediate
Why should a polymorphic base class have a virtual destructor?
:::answer
When an object is deleted through a base pointer, the destructor call is dispatched like any other call. If the destructor is not virtual, only the base destructor runs, which is undefined behaviour and in practice leaks or corrupts the derived part. A virtual destructor ensures the derived destructor runs first, then the base destructor.
:::

:::question intermediate
What is object slicing? Give an example.
:::answer
Slicing happens when a derived object is copied into a base-class object by value: only the base part is copied and the derived data and overrides are lost. For example, `void feed(Animal a)` called with a `Dog` receives a plain `Animal`, so `a.sound()` runs `Animal::sound`. Passing `const Animal&` avoids it.
:::

:::question advanced
Explain how a typical compiler executes `shape->area()` when `area` is virtual, and why such calls are usually slightly slower than non-virtual calls.
:::answer
Each object of a class with virtual functions stores a hidden vptr pointing to its class's vtable, an array of function pointers. The call loads the vptr from the object, loads the function pointer from `area`'s slot in the vtable, and calls through it. This adds two memory loads and an indirect call, which the CPU may mispredict, and the compiler usually cannot inline it because the target is unknown until run time; a non-virtual call is a direct, often inlined call.
:::

## Further learning

- **Next:** *Generic Programming with Templates* shows compile-time polymorphism, the alternative to virtual functions.
- **Related:** *Exceptions & Exception Safety* relies on catching exceptions by reference so the virtual `what()` reports the real error.
