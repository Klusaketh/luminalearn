---
lesson: java-extending-classes
title: Extending Classes & Super Keyword
summary: Inheritance in Java with extends, calling superclass constructors and methods with super, constructor chaining order, method overriding rules, protected access, and final classes and methods.
minutes: 35
type: theory
objectives:
  - Create subclasses with extends and call superclass constructors and methods with super
  - Predict the order of constructor execution and field initialisation in a class hierarchy
  - Apply overriding rules, protected access, and final to design safe inheritance hierarchies
review: ai-draft
---
## Introduction

Inheritance lets a new class reuse and specialise an existing one: a `SavingsAccount` extends `Account`, a `Manager` extends `Employee`. Java supports **single inheritance** of classes, where every class has exactly one superclass, ultimately `java.lang.Object`. The keyword `super` reaches the superclass's constructors and methods, and `final` lets a designer forbid extension where it would be unsafe. This lesson covers the mechanics; the next covers polymorphism.

**Before you start:** you should know how to define Java classes, constructors, and methods.

## Core theory

### extends and the Object class

`class Savings extends Account { ... }` makes `Savings` a subclass. It inherits all accessible fields and methods of `Account` and can add new ones. Every class that does not say otherwise extends `Object`, which supplies `toString`, `equals`, `hashCode`, and `getClass`. A class can extend only one class, although it can implement many interfaces.

### Constructors and super(...)

Constructors are **not** inherited. Every constructor's first action is a call to a superclass constructor: either an explicit `super(args)` as the first statement, or an implicit call to the no-argument `super()`. If the superclass has no no-argument constructor, the subclass must call `super(...)` explicitly, or it will not compile. The chain runs all the way up to `Object`, so construction happens **top-down**: the `Object` part first, then each class's field initialisers and constructor body, ending with the subclass.

### Overriding and super.method()

A subclass **overrides** an instance method by declaring one with the same name and parameter types. Rules:

- The return type must be the same or a subtype (a **covariant** return).
- Access cannot be more restrictive (a `public` method cannot become `protected`).
- It cannot throw broader checked exceptions.
- `static`, `private`, and `final` methods cannot be overridden (static methods are **hidden** instead).

Always annotate overrides with `@Override`, so the compiler reports a mistake such as a misspelt name or wrong parameter type. Inside the override, `super.method(...)` calls the superclass version, which lets the subclass extend behaviour rather than replace it.

### protected access

| Modifier | Same class | Same package | Subclass elsewhere | Everyone |
| :--- | :--- | :--- | :--- | :--- |
| `private` | yes | no | no | no |
| (none) | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

`protected` members are designed for subclasses. Many designs still keep fields `private` and expose `protected` methods, so the superclass keeps control of its invariants.

### final

A `final` class cannot be extended (`String`, `Integer`); a `final` method cannot be overridden; a `final` variable cannot be reassigned. Declaring a class `final` is a deliberate design choice when subclassing could break its guarantees, such as immutability.

### Inheritance or composition?

Use inheritance only for a genuine **"is a"** relationship where the subclass can be used anywhere the superclass is expected. When one class merely uses another, store it as a field (**composition**, "has a"), which is more flexible and does not expose the other class's methods.

## Worked examples

### Example 1: Constructor chaining and initialisation order

```java
public class Main {
    static class Vehicle {
        protected final String id;
        private int trace = log("Vehicle field initialiser");

        Vehicle(String id) {
            this.id = id;
            log("Vehicle constructor for " + id);
        }
        String describe() { return "vehicle " + id; }
        static int log(String msg) { System.out.println(msg); return 0; }
    }

    static class Car extends Vehicle {
        private final int seats;
        private int trace2 = log("Car field initialiser");

        Car(String id, int seats) {
            super(id);
            this.seats = seats;
            log("Car constructor, seats " + seats);
        }
        @Override
        String describe() { return super.describe() + " (car with " + seats + " seats)"; }
    }

    static final class SportsCar extends Car {
        SportsCar(String id) { super(id, 2); log("SportsCar constructor"); }
        @Override
        String describe() { return "fast " + super.describe(); }
    }

    public static void main(String[] args) {
        SportsCar s = new SportsCar("KA-01");
        System.out.println(s.describe());
        System.out.println(s instanceof Vehicle);
        System.out.println(s.getClass().getSimpleName() + " extends " + s.getClass().getSuperclass().getSimpleName());
    }
}
```

Output:

```text
Vehicle field initialiser
Vehicle constructor for KA-01
Car field initialiser
Car constructor, seats 2
SportsCar constructor
fast vehicle KA-01 (car with 2 seats)
true
SportsCar extends Car
```

Each constructor first calls its superclass constructor, so construction proceeds from `Vehicle` down to `SportsCar`; a class's field initialisers run after its superclass constructor finishes and before its own constructor body. Each `describe` calls `super.describe()` and adds to it.

### Example 2: Overriding rules and a missing super() call

```java
public class Main {
    static class Shape {
        protected String name() { return "shape"; }
        Shape copy() { return new Shape(); }
        static String kind() { return "static Shape"; }
    }

    static class Circle extends Shape {
        @Override
        public String name() { return "circle"; }
        @Override
        Circle copy() { return new Circle(); }
        static String kind() { return "static Circle"; }
    }

    static class Account {
        final double balance;
        Account(double opening) { balance = opening; }
    }

    static class Savings extends Account {
        Savings() { super(500); }
    }

    public static void main(String[] args) {
        Shape s = new Circle();
        System.out.println(s.name() + " " + s.copy().name());
        System.out.println(Shape.kind() + " / " + Circle.kind());
        System.out.println(new Savings().balance);
    }
}
```

Output:

```text
circle circle
static Shape / static Circle
500.0
```

`Circle.name()` widens access from `protected` to `public`, which is allowed, and `copy()` uses a covariant return type. Static methods are hidden rather than overridden, so each class's `kind()` is chosen by the class name used in the call. If `Savings()` omitted `super(500)`, compilation would fail, because `Account` has no no-argument constructor for the implicit `super()` to call.

## Applications

- **Frameworks:** applications extend framework classes such as servlets, activities, or test cases.
- **Specialised models:** `Manager extends Employee` adds fields and overrides pay calculations.
- **Template methods:** a superclass defines an algorithm and subclasses override individual steps.
- **Library safety:** `final` classes such as `String` prevent subclasses from breaking immutability.

## Common mistakes

- **Forgetting `super(...)` when the superclass lacks a no-argument constructor.** The subclass does not compile.
- **Missing `@Override`.** A typo creates a new method instead of overriding.
- **Overriding with weaker access.** Making a public method protected is a compile error.
- **Calling overridable methods from constructors.** The subclass override runs before the subclass's fields are initialised.
- **Using inheritance for "has a" relationships.** Prefer composition.

## Revision notes

- `class B extends A`: single inheritance; every class extends `Object`.
- Constructors are not inherited; each starts with `super(...)` (explicit or implicit).
- Construction runs top-down: superclass first, then field initialisers, then the constructor body.
- Overriding: same signature, same or covariant return, not weaker access; use `@Override`.
- `super.method()` calls the superclass version; static methods are hidden, not overridden.
- `protected` = package + subclasses; `final` stops extension or overriding.

## Practice questions

:::question basic
What is the first thing every Java constructor does?
:::answer
It calls a superclass constructor, either explicitly with `super(...)` as its first statement or implicitly with `super()`. (A constructor may instead call another constructor of the same class with `this(...)`, which in turn calls `super`.)
:::

:::question basic
What does the `@Override` annotation do?
:::answer
It tells the compiler the method is meant to override a superclass or interface method. If no such method exists, for example because of a typo or wrong parameter type, compilation fails instead of silently creating a new, unrelated method.
:::

:::question intermediate
A subclass constructor does not call `super(...)`, and the superclass only has `Account(double opening)`. What happens and why?
:::answer
Compilation fails. Without an explicit call, Java inserts `super()`, but the superclass has no no-argument constructor to call. The subclass must call `super(someValue)` explicitly.
:::

:::question intermediate
Can a subclass override a `public` method with a `protected` one? Can it override a method returning `Shape` with one returning `Circle`?
:::answer
It cannot make the method `protected`, because an override may not reduce access; code using the superclass type expects to call it publicly. It can return `Circle` if `Circle` is a subclass of `Shape`, since covariant return types are allowed.
:::

:::question advanced
Why is it risky for a superclass constructor to call a method that subclasses override?
:::answer
The superclass constructor runs before the subclass's field initialisers and constructor body. If it calls an overridden method, the subclass version runs while the subclass's fields still hold default values (`null`, 0), which can cause wrong results or a `NullPointerException`. Constructors should call only `private`, `static`, or `final` methods.
:::

## Further learning

- **Next:** *Runtime Polymorphism & Dynamic Binding* shows how overridden methods are chosen at run time.
- **Related:** *Inheritance Models & Base Classes* in C++ compares constructor chaining and multiple inheritance.
