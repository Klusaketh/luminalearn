---
lesson: java-runtime-polymorphism
title: Runtime Polymorphism & Dynamic Binding
summary: How Java chooses which overridden method to run at run time (dynamic binding), upcasting and downcasting, instanceof checks, and why fields and static methods are not polymorphic.
minutes: 35
type: theory
objectives:
  - Explain static (compile-time) and dynamic (run-time) binding and predict which method a call executes
  - Use upcasting, downcasting, and instanceof safely, avoiding ClassCastException
  - Distinguish overriding from overloading and recognise that fields and static methods are resolved by declared type
review: ai-draft
---
## Introduction

**Polymorphism** means "many forms": one variable of type `Shape` may refer to a circle, a square, or a triangle, and calling `area()` runs the right code for whichever object it is. In Java this happens automatically for every overridable instance method, through **dynamic binding**. It is the mechanism that lets a payroll system pay employees, managers, and contractors with one loop, and lets frameworks call methods you wrote years after they were designed.

**Before you start:** you should know how to extend classes and override methods.

## Core theory

### Declared type and actual type

Every reference has a **declared (static) type**, the type written in the declaration, and refers to an object with an **actual (dynamic) type**, the class used with `new`. In `Animal a = new Dog();`, the declared type is `Animal` and the actual type is `Dog`.

- The **compiler** uses the declared type to decide which methods may be called: `a.fetch()` does not compile if `Animal` has no `fetch` method, even though the object is a `Dog`.
- At **run time**, the JVM uses the actual type to decide which implementation of an overridden instance method runs: `a.speak()` runs `Dog.speak()`.

This run-time choice is **dynamic binding** (late binding). In Java, every non-`static`, non-`private`, non-`final` instance method is bound dynamically, unlike C++, where you must write `virtual`.

### Overloading versus overriding

**Overloading** (same name, different parameters) is resolved at **compile time** from the declared types of the arguments. **Overriding** (same signature in a subclass) is resolved at **run time** from the actual type of the receiver. So with overloads `feed(Animal)` and `feed(Dog)`, the call `feed(a)` for `Animal a = new Dog()` picks `feed(Animal)`, because overload resolution looks only at the declared type.

### What is not polymorphic

- **Fields** are resolved by the declared type: if both classes declare a field `name`, `a.name` reads `Animal`'s field. (Declaring the same field in a subclass, called field hiding, is confusing and should be avoided.)
- **Static methods** are hidden, not overridden, and are chosen by the declared type.
- **Private** and **final** methods cannot be overridden, so the call is bound statically.

### Upcasting and downcasting

**Upcasting**, converting a subclass reference to a superclass type, is always safe and implicit: `Animal a = new Dog();`. **Downcasting**, converting back, needs an explicit cast, `Dog d = (Dog) a;`, and is checked at run time: if the object is not actually a `Dog`, the JVM throws `ClassCastException`. Guard downcasts with `instanceof`:

```java
if (a instanceof Dog) {
    Dog d = (Dog) a;
    d.fetch();
}
```

Java 16 added pattern matching, `if (a instanceof Dog d) { d.fetch(); }`, which combines the test and the cast. Frequent downcasting is often a design smell: a polymorphic method in the superclass usually expresses the behaviour better.

## Worked examples

### Example 1: Dynamic binding in a payroll loop

```java
import java.util.List;

public class Main {
    static class Employee {
        protected final String name;
        protected final double base;
        Employee(String name, double base) { this.name = name; this.base = base; }
        double pay() { return base; }
        String role() { return "employee"; }
        String payslip() { return name + " (" + role() + "): " + pay(); }
    }

    static class Manager extends Employee {
        private final double bonus;
        Manager(String name, double base, double bonus) { super(name, base); this.bonus = bonus; }
        @Override double pay() { return base + bonus; }
        @Override String role() { return "manager"; }
    }

    static class Intern extends Employee {
        Intern(String name, double base) { super(name, base); }
        @Override double pay() { return base * 0.5; }
        @Override String role() { return "intern"; }
    }

    public static void main(String[] args) {
        List<Employee> staff = List.of(
            new Employee("Asha", 50000), new Manager("Ravi", 70000, 15000), new Intern("Meena", 20000));
        double total = 0;
        for (Employee e : staff) {
            System.out.println(e.payslip());
            total += e.pay();
        }
        System.out.println("total payroll: " + total);
    }
}
```

Output:

```text
Asha (employee): 50000.0
Ravi (manager): 85000.0
Meena (intern): 10000.0
total payroll: 145000.0
```

`payslip` is defined once in `Employee`, yet its calls to `role()` and `pay()` dispatch on the actual object, so each line is correct. Adding a new kind of employee requires no change to the loop.

### Example 2: Overloading, fields, static methods, and safe downcasting

```java
public class Main {
    static class Animal {
        String name = "animal";
        String speak() { return "..."; }
        static String category() { return "Animal.category"; }
    }

    static class Dog extends Animal {
        String name = "dog";
        @Override String speak() { return "woof"; }
        static String category() { return "Dog.category"; }
        String fetch() { return "fetching the ball"; }
    }

    static class Cat extends Animal {
        @Override String speak() { return "meow"; }
    }

    static String feed(Animal a) { return "feeding an animal"; }
    static String feed(Dog d) { return "feeding a dog"; }

    public static void main(String[] args) {
        Animal a = new Dog();
        System.out.println(a.speak() + " | " + a.name + " | " + ((Dog) a).name);
        System.out.println(feed(a) + " | " + feed((Dog) a));
        System.out.println(Animal.category() + " | " + Dog.category());

        Animal[] pets = { new Dog(), new Cat() };
        for (Animal p : pets) {
            if (p instanceof Dog) {
                Dog d = (Dog) p;
                System.out.println(d.speak() + ", " + d.fetch());
            } else {
                System.out.println(p.speak() + ", no fetching");
            }
        }
        try {
            Dog wrong = (Dog) pets[1];
            System.out.println(wrong.fetch());
        } catch (ClassCastException e) {
            System.out.println("ClassCastException: a Cat is not a Dog");
        }
    }
}
```

Output:

```text
woof | animal | dog
feeding an animal | feeding a dog
Animal.category | Dog.category
woof, fetching the ball
meow, no fetching
ClassCastException: a Cat is not a Dog
```

`a.speak()` is bound dynamically to `Dog.speak`, but the field `a.name` and the overload `feed(a)` are chosen from the declared type `Animal`. The downcast of the `Cat` compiles, since a `Cat` is an `Animal` that might be a `Dog`, but fails at run time.

## Applications

- **Plug-in designs:** code depends on a superclass or interface, and new subclasses add behaviour.
- **GUI frameworks:** a container calls `paint()` on every component, each drawing itself.
- **Collections:** `List<Shape>` holds many shape types processed uniformly.
- **Testing:** a fake subclass overrides methods to simulate databases or networks.

## Common mistakes

- **Expecting overload resolution to use the actual type.** Overloads are chosen at compile time.
- **Expecting fields to be polymorphic.** Use getter methods, which are dynamically bound.
- **Downcasting without checking.** Use `instanceof` or redesign with a polymorphic method.
- **Calling subclass-only methods through a superclass reference.** The compiler checks the declared type.

## Revision notes

- Declared type: what the compiler allows. Actual type: what runs for overridden methods.
- Java instance methods are dynamically bound unless `static`, `private`, or `final`.
- Overloading: compile time, declared argument types. Overriding: run time, actual receiver type.
- Fields and static methods use the declared type.
- Upcasting is implicit and safe; downcasting is explicit and can throw `ClassCastException`.
- Guard downcasts with `instanceof` (pattern matching from Java 16).

## Practice questions

:::question basic
In `Shape s = new Circle(2);`, what are the declared and actual types of `s`?
:::answer
The declared (static) type is `Shape`, fixed by the declaration. The actual (dynamic) type is `Circle`, the class of the object created with `new`.
:::

:::question basic
Why does `Animal a = new Dog(); a.fetch();` fail to compile when only `Dog` has `fetch()`?
:::answer
The compiler checks method calls against the declared type, `Animal`, which has no `fetch` method. Even though the object is a `Dog`, you must downcast, `((Dog) a).fetch()`, after checking with `instanceof`.
:::

:::question intermediate
Given `void print(Object o)` and `void print(String s)`, which runs for `Object x = "hi"; print(x);`, and why?
:::answer
`print(Object)` runs. Overload resolution happens at compile time using the declared type of the argument, which is `Object`, even though the actual object is a `String`.
:::

:::question intermediate
When does a downcast throw `ClassCastException`, and how do you prevent it?
:::answer
It throws at run time when the object's actual type is not the target type or a subclass of it, for example casting a `Cat` referenced as `Animal` to `Dog`. Check first with `instanceof`, or better, move the behaviour into an overridden method so no downcast is needed.
:::

:::question advanced
A superclass `Report` has `String header()` and `String render()`, where `render` calls `header()`. A subclass overrides `header()`. What does `new SalesReport().render()` produce, and which design pattern is this?
:::answer
`render` runs the inherited superclass code, but its call to `header()` is dynamically bound to `SalesReport.header()`, so the result uses the subclass's header inside the superclass's layout. This is the Template Method pattern: the superclass fixes the algorithm and subclasses customise individual steps by overriding them.
:::

## Further learning

- **Next:** *Abstract Classes & Method Contracts* forces subclasses to provide certain methods.
- **Related:** *Virtual Functions & VTable Dispatch* in C++ explains how dynamic dispatch is implemented.
