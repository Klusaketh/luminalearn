---
lesson: java-abstract-classes
title: Abstract Classes & Method Contracts
summary: Abstract classes and abstract methods in Java: declaring contracts that subclasses must fulfil, mixing implemented and abstract methods, constructors in abstract classes, and when to choose an abstract class over an interface.
minutes: 30
type: theory
objectives:
  - Declare abstract classes and abstract methods and explain why abstract classes cannot be instantiated
  - Use abstract classes to share state and implementation while requiring subclasses to implement key steps
  - Decide between an abstract class and an interface for a given design
review: ai-draft
---
## Introduction

Some classes exist only to be extended. A generic `Shape` has no meaningful area, and a generic `PaymentMethod` cannot actually pay; only concrete subclasses such as `Circle` or `CardPayment` can. Java's **abstract classes** capture this: they define what every subclass must be able to do, provide the code all subclasses share, and refuse to be instantiated themselves. The compiler then guarantees that every concrete subclass fulfils the contract.

**Before you start:** you should know inheritance, overriding, and polymorphism in Java.

## Core theory

### Abstract methods and classes

An **abstract method** has a signature but no body:

```java
abstract double area();
```

A class that declares or inherits an abstract method without implementing it must itself be declared `abstract`. An abstract class:

- **cannot be instantiated**: `new Shape()` is a compile error;
- can have **fields**, **constructors**, **concrete methods**, and **static members**, like any class;
- is used through references to its concrete subclasses: `Shape s = new Circle(2);`.

A **concrete** subclass must implement every inherited abstract method, otherwise it too must be declared `abstract`. A class may also be declared abstract with no abstract methods, simply to prevent direct instantiation.

### Constructors in abstract classes

Although you cannot create an abstract class directly, its constructor runs as part of creating each subclass object, through `super(...)`. It initialises the shared state, such as a name or an ID, so every subclass object starts valid.

### The template method pattern

Abstract classes shine when an algorithm's overall steps are fixed but some steps vary. A concrete, often `final`, method in the abstract class defines the sequence and calls abstract "hook" methods that subclasses implement. Subclasses customise the steps without being able to change the overall procedure.

### Abstract class or interface?

| Abstract class | Interface |
| :--- | :--- |
| a class can extend only one | a class can implement many |
| can have instance fields and constructors | no instance fields (only constants) |
| can have any access level for members | methods are public |
| models "is a kind of" with shared state | models a capability ("can be compared", "can be closed") |

Since Java 8, interfaces can contain `default` methods with bodies, so the remaining reasons to choose an abstract class are **shared mutable state**, **constructors**, and non-public members. A common design combines both: an interface defines the type, and an abstract class implements it partially to reduce duplication for implementers (as `AbstractList` does for `List`).

## Worked examples

### Example 1: An abstract shape hierarchy

```java
import java.util.ArrayList;
import java.util.List;

public class Main {
    static abstract class Shape {
        private static int count = 0;
        protected final String label;

        Shape(String label) { this.label = label; count++; }

        abstract double area();
        abstract double perimeter();

        String summary() {
            return String.format("%s: area %.2f, perimeter %.2f", label, area(), perimeter());
        }
        static int count() { return count; }
    }

    static class Circle extends Shape {
        private final double r;
        Circle(double r) { super("circle"); this.r = r; }
        @Override double area() { return Math.PI * r * r; }
        @Override double perimeter() { return 2 * Math.PI * r; }
    }

    static class Rectangle extends Shape {
        private final double w, h;
        Rectangle(double w, double h) { super("rectangle"); this.w = w; this.h = h; }
        @Override double area() { return w * h; }
        @Override double perimeter() { return 2 * (w + h); }
    }

    public static void main(String[] args) {
        List<Shape> shapes = new ArrayList<>();
        shapes.add(new Circle(1));
        shapes.add(new Rectangle(3, 4));
        double total = 0;
        for (Shape s : shapes) {
            System.out.println(s.summary());
            total += s.area();
        }
        System.out.printf("total area %.2f from %d shapes%n", total, Shape.count());
    }
}
```

Output:

```text
circle: area 3.14, perimeter 6.28
rectangle: area 12.00, perimeter 14.00
total area 15.14 from 2 shapes
```

`Shape` holds the shared label and counter and implements `summary` once; every concrete subclass must supply `area` and `perimeter`. The abstract class's constructor runs through each subclass's `super(...)` call.

### Example 2: The template method pattern for data export

```java
import java.util.List;

public class Main {
    static abstract class Exporter {
        public final String export(List<String[]> rows) {
            StringBuilder out = new StringBuilder();
            out.append(header());
            for (String[] row : rows) out.append(formatRow(row));
            out.append(footer());
            return out.toString();
        }
        protected abstract String formatRow(String[] row);
        protected String header() { return ""; }
        protected String footer() { return ""; }
    }

    static class CsvExporter extends Exporter {
        @Override protected String header() { return "name,marks\n"; }
        @Override protected String formatRow(String[] row) { return String.join(",", row) + "\n"; }
    }

    static class JsonExporter extends Exporter {
        private boolean first = true;
        @Override protected String header() { return "["; }
        @Override protected String formatRow(String[] row) {
            String item = (first ? "" : ",") + "{\"name\":\"" + row[0] + "\",\"marks\":" + row[1] + "}";
            first = false;
            return item;
        }
        @Override protected String footer() { return "]\n"; }
    }

    public static void main(String[] args) {
        List<String[]> rows = List.of(new String[] {"Asha", "91"}, new String[] {"Ravi", "78"});
        System.out.print(new CsvExporter().export(rows));
        System.out.print(new JsonExporter().export(rows));
    }
}
```

Output:

```text
name,marks
Asha,91
Ravi,78
[{"name":"Asha","marks":91},{"name":"Ravi","marks":78}]
```

`export` is `final`, so the overall procedure (header, every row, footer) cannot be changed. Subclasses must implement `formatRow` and may override the optional `header` and `footer` hooks, which have default empty implementations.

## Applications

- **Frameworks:** base classes such as `HttpServlet` or `AbstractList` implement common logic and leave key methods abstract.
- **Games:** an abstract `Entity` holds position and health; subclasses implement `update()`.
- **Report and export pipelines:** template methods fix the workflow and vary the formats.
- **Domain models:** an abstract `Account` with shared balance logic and abstract interest rules.

## Common mistakes

- **Trying to instantiate an abstract class.** Create a concrete subclass instead.
- **Forgetting to implement an inherited abstract method.** The subclass must then be abstract, or compilation fails.
- **Declaring an abstract method `private` or `final`.** Subclasses could then never implement it, so it is a compile error.
- **Using an abstract class purely as a type with no shared code.** An interface is more flexible.

## Revision notes

- `abstract` methods have no body; a class containing one must be `abstract`.
- Abstract classes cannot be instantiated but can have fields, constructors, and concrete methods.
- Concrete subclasses must implement every abstract method.
- Template method: a `final` algorithm in the abstract class calls abstract hooks.
- Choose an abstract class for shared state and constructors; an interface for capabilities and multiple inheritance of type.
- Abstract methods cannot be `private`, `static`, or `final`.

## Practice questions

:::question basic
Can you write `new Shape()` if `Shape` is abstract? What can you write instead?
:::answer
No, abstract classes cannot be instantiated. You create an object of a concrete subclass and may refer to it through the abstract type, for example `Shape s = new Circle(2);`.
:::

:::question basic
Can an abstract class have a constructor? When does it run?
:::answer
Yes. It runs whenever an object of a concrete subclass is created, through the subclass constructor's `super(...)` call, and it initialises the state that the abstract class declares.
:::

:::question intermediate
A subclass of an abstract class implements only one of its two abstract methods. What must be true of the subclass?
:::answer
It must itself be declared `abstract`, because it still has an unimplemented abstract method. Only a class that implements every inherited abstract method can be concrete and instantiated.
:::

:::question intermediate
Why is the template method in the export example declared `final`?
:::answer
Making `export` final prevents subclasses from overriding the overall algorithm, so every exporter always writes the header, every row, and the footer in that order. Subclasses can only customise the individual steps that the abstract class deliberately exposes as hooks.
:::

:::question advanced
You are designing a library of payment methods. All of them need a transaction log and an ID assigned at creation, and some classes must also be serialisable and comparable. How would you combine an interface and an abstract class?
:::answer
Define an interface `PaymentMethod` with methods such as `pay(amount)` and `refund(id)`, so any class can be used as a payment method. Provide an abstract class `AbstractPaymentMethod implements PaymentMethod` that holds the ID and the transaction log, assigns the ID in its constructor, and implements shared logging, leaving `pay` abstract. Concrete classes extend the abstract class and additionally implement `Comparable` or `Serializable` as needed, since a class can implement many interfaces but extend only one class.
:::

## Further learning

- **Next:** *Interface Contracts & Default Methods* covers the other way to define contracts.
- **Related:** *Runtime Polymorphism & Dynamic Binding* explains how calls to abstract methods reach the right implementation.
