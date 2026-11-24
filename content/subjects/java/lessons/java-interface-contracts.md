---
lesson: java-interface-contracts
title: Interface Contracts & Default Methods
summary: Java interfaces as contracts: implementing several interfaces, default and static methods, resolving default-method conflicts, functional interfaces, and coding to an interface rather than an implementation.
minutes: 35
type: theory
objectives:
  - Define and implement interfaces, including multiple interfaces on one class
  - Use default and static interface methods and resolve conflicts between inherited defaults
  - Identify functional interfaces and implement them with lambdas, and explain the benefits of programming to interfaces
review: ai-draft
---
## Introduction

An **interface** describes what an object can do without saying how. `Comparable` means "can be ordered", `Runnable` means "can be run", `List` means "behaves like a list". A class can implement many interfaces, so interfaces give Java a safe form of multiple inheritance: of **type** and, since Java 8, of **behaviour** through default methods. Most well-designed Java code depends on interfaces rather than concrete classes, which keeps it flexible and testable.

**Before you start:** you should know classes, inheritance, overriding, and abstract classes.

## Core theory

### Declaring and implementing interfaces

```java
interface Payable {
    double amountDue();
}

class Invoice implements Payable {
    public double amountDue() { return 1200.0; }
}
```

Interface methods without a body are implicitly `public abstract`; fields are implicitly `public static final` constants. A class lists its interfaces after `implements` and must implement all abstract methods, as `public` methods, unless the class is abstract. A class can `extend` one class and `implement` any number of interfaces; an interface can `extend` other interfaces.

### Default and static methods

A **default method** has a body and is inherited by implementing classes, which may override it:

```java
interface Greeter {
    String name();
    default String greet() { return "Hello, " + name(); }
}
```

Default methods let interfaces evolve: adding a new method with a default implementation does not break existing implementers. This is how `List.sort` and `Iterable.forEach` were added in Java 8. **Static methods** in interfaces are utilities called through the interface name (`Comparator.naturalOrder()`) and are not inherited. Java 9 also allows `private` interface methods to share code between defaults.

### Resolving conflicts

If a class inherits the same default method from two interfaces, the compiler requires the class to override it. Inside the override, `InterfaceName.super.method()` calls a specific interface's version. Rules of precedence: a method from a superclass always wins over interface defaults ("class wins"), and a more specific interface's default wins over the one it extends.

### Functional interfaces and lambdas

An interface with exactly **one abstract method** is a **functional interface** and can be implemented by a **lambda expression** or method reference. `@FunctionalInterface` asks the compiler to enforce the single-method rule. The standard ones in `java.util.function` include `Function<T, R>` (`apply`), `Predicate<T>` (`test`), `Consumer<T>` (`accept`), `Supplier<T>` (`get`), and `BinaryOperator<T>`; older ones include `Runnable`, `Comparator<T>`, and `Callable<V>`.

### Programming to interfaces

Declare variables, parameters, and return types with interface types (`List<String> names = new ArrayList<>();`, `void save(Repository repo)`). Code then works with any implementation: a `LinkedList`, an in-memory repository in tests, or a database-backed one in production. This **dependency on abstractions** is the foundation of testable, loosely coupled designs.

## Worked examples

### Example 1: Multiple interfaces, defaults, and conflict resolution

```java
public class Main {
    interface Flyer {
        default String move() { return "flying"; }
        int maxAltitude();
    }

    interface Swimmer {
        default String move() { return "swimming"; }
        static String describe(Swimmer s) { return "a swimmer that is " + s.move(); }
    }

    static class Duck implements Flyer, Swimmer {
        @Override public String move() { return Flyer.super.move() + " and " + Swimmer.super.move(); }
        @Override public int maxAltitude() { return 1000; }
    }

    static class Penguin implements Swimmer {}

    public static void main(String[] args) {
        Duck d = new Duck();
        System.out.println("duck: " + d.move() + ", up to " + d.maxAltitude() + " m");
        System.out.println(Swimmer.describe(new Penguin()));
        Flyer f = d;
        Swimmer s = d;
        System.out.println(f.move().equals(s.move()));
        System.out.println(d instanceof Flyer && d instanceof Swimmer);
    }
}
```

Output:

```text
duck: flying and swimming, up to 1000 m
a swimmer that is swimming
true
true
```

`Duck` inherits two conflicting `move` defaults, so it must override `move`, and it combines both with `Flyer.super.move()` and `Swimmer.super.move()`. `Penguin` implements no methods at all and simply inherits the default. The static method `describe` is called through the interface name.

### Example 2: Functional interfaces with lambdas and programming to an interface

```java
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.function.Predicate;

public class Main {
    @FunctionalInterface
    interface Discount {
        double apply(double price);
        default Discount then(Discount next) { return p -> next.apply(apply(p)); }
    }

    interface Repository {
        void save(String item);
        List<String> all();
    }

    static class MemoryRepository implements Repository {
        private final List<String> items = new ArrayList<>();
        public void save(String item) { items.add(item); }
        public List<String> all() { return items; }
    }

    static int store(Repository repo, List<String> items, Predicate<String> keep) {
        int saved = 0;
        for (String it : items) if (keep.test(it)) { repo.save(it); saved++; }
        return saved;
    }

    public static void main(String[] args) {
        Discount tenPercent = p -> p * 0.9;
        Discount flat50 = p -> Math.max(0, p - 50);
        System.out.println(tenPercent.then(flat50).apply(1000));
        System.out.println(flat50.then(tenPercent).apply(1000));

        Function<String, Integer> length = String::length;
        System.out.println(length.apply("interface"));

        Repository repo = new MemoryRepository();
        int n = store(repo, List.of("apple", "kiwi", "banana", "fig"), s -> s.length() > 3);
        System.out.println(n + " saved: " + repo.all());
    }
}
```

Output:

```text
850.0
855.0
9
3 saved: [apple, kiwi, banana]
```

`Discount` has one abstract method, so lambdas implement it; its default method `then` composes two discounts, and the order matters. `store` depends only on the `Repository` interface and a `Predicate`, so a test can pass an in-memory repository while production passes a database-backed one.

## Applications

- **Collections:** code written against `List`, `Set`, and `Map` works with every implementation.
- **Sorting:** `Comparable` and `Comparator` let any class be sorted.
- **Callbacks and streams:** lambdas implement `Runnable`, `Predicate`, and `Function`.
- **Dependency injection:** frameworks such as Spring wire interface-typed dependencies to concrete classes.

## Common mistakes

- **Implementing interface methods with weaker access.** They must be `public`.
- **Expecting interfaces to hold per-object state.** Interface fields are constants; use an abstract class for state.
- **Ignoring default-method conflicts.** A class inheriting the same default from two interfaces must override it.
- **Declaring variables with concrete types everywhere.** Use interface types to keep code flexible.

## Revision notes

- Interface methods are `public abstract` by default; fields are `public static final`.
- A class implements many interfaces; an interface can extend many interfaces.
- `default` methods have bodies and help interfaces evolve; `static` methods are called via the interface.
- Conflicting defaults must be overridden; `X.super.m()` selects one.
- Functional interface = one abstract method; implement with a lambda or method reference.
- Program to interfaces for flexibility and testing.

## Practice questions

:::question basic
Why must a class's implementations of interface methods be `public`?
:::answer
Interface methods are implicitly `public`, and an implementation cannot reduce access, just as an override cannot. Declaring the implementation with package or protected access is a compile error.
:::

:::question basic
What makes an interface a functional interface?
:::answer
It has exactly one abstract method (default and static methods do not count). Such an interface can be implemented with a lambda expression or a method reference, and `@FunctionalInterface` makes the compiler check the rule.
:::

:::question intermediate
A class implements interfaces `A` and `B`, both with `default String hello()`. What must the class do, and how can it reuse `A`'s version?
:::answer
It must override `hello()`, because the compiler cannot choose between the two defaults. Inside the override it can call `A.super.hello()` to reuse `A`'s implementation, optionally combining it with `B.super.hello()`.
:::

:::question intermediate
Why were default methods added to Java interfaces in Java 8?
:::answer
They allow new methods to be added to existing interfaces without breaking every class that already implements them, because implementers inherit the default body. This let the core library add methods such as `forEach`, `sort`, and `stream` to interfaces like `Iterable`, `List`, and `Collection`.
:::

:::question advanced
Explain how depending on a `Repository` interface instead of a `MySqlRepository` class makes a service easier to test.
:::answer
If the service's constructor accepts a `Repository`, a test can pass a lightweight in-memory implementation that needs no database, runs in milliseconds, and lets the test inspect exactly what was saved. With a hard-coded `MySqlRepository`, every test would need a running database and would be slower and more fragile. The same interface also allows swapping the production storage later without changing the service.
:::

## Further learning

- **Next:** *Checked vs Runtime Exceptions* covers `AutoCloseable`, an interface used by try-with-resources.
- **Related:** *Lambdas & the Streams API* builds pipelines from functional interfaces.
