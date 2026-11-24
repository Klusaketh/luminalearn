---
lesson: java-class-definitions-memory
title: Class Definitions & Memory Allocation
summary: Defining Java classes with fields, constructors, and methods, how objects are allocated on the heap and referenced, method overloading, static members, and how garbage collection decides when objects can be reclaimed.
minutes: 40
type: theory
objectives:
  - Define classes with private fields, constructors, getters, methods, and overloaded methods
  - Explain object creation, references, aliasing, null, and the difference between static and instance members
  - Describe reachability from garbage-collection roots and predict when an object becomes eligible for collection
review: ai-draft
---
## Introduction

Java is built around **classes** and **objects**. A class describes a kind of thing, its data (fields) and behaviour (methods); each object is one instance living on the heap. Unlike C++, you never decide where an object lives or when it is freed: every object is created with `new` on the heap and reclaimed automatically by the garbage collector once nothing can reach it. Understanding references and reachability is the key to reasoning about Java programs.

**Before you start:** you should know Java syntax, types, methods, and strings.

## Core theory

### Fields, constructors, and methods

```java
public class Student {
    private final String name;
    private int marks;

    public Student(String name, int marks) {
        this.name = name;
        this.marks = marks;
    }
    public String getName() { return name; }
    public void addBonus(int points) { marks += points; }
}
```

Fields are usually `private`, exposed through methods, so the class controls its own state (**encapsulation**). A **constructor** has the class's name and no return type; `this` refers to the current object and distinguishes fields from parameters with the same name. If you write no constructor, Java supplies a no-argument default constructor; writing any constructor removes it. One constructor can call another with `this(...)` as its first statement. A `final` field must be assigned exactly once, in its declaration or in every constructor.

Uninitialised fields get default values (`0`, `false`, `null`), but local variables get none and must be assigned before use.

### Objects and references

`new Student("Asha", 80)` allocates an object on the heap, runs the constructor, and returns a **reference**. Variables of class type hold references, so `Student t = s;` makes `t` and `s` refer to the **same** object (an **alias**); changing it through one is visible through the other. A reference can be `null`, and calling a method on `null` throws `NullPointerException`. `==` on references tests whether two references point to the same object; logical equality needs an `equals` method.

### Overloading

Methods in a class can share a name if their parameter lists differ: `area(int side)`, `area(int w, int h)`, `area(double r)`. The compiler chooses the most specific applicable method at compile time, considering exact matches first, then widening conversions, then boxing, then variable arguments (`int... values`). Overloads cannot differ only in return type.

### Static members

A `static` field belongs to the class, with one copy shared by all objects, such as a counter of objects created. A `static` method has no `this` and cannot access instance fields directly. Static members are initialised when the class is initialised. Constants are typically `public static final` with uppercase names.

### Garbage collection and reachability

The garbage collector reclaims an object when it is no longer **reachable** from any **GC root**: local variables in active stack frames, static fields, active threads, and a few JVM-internal references. Reachability is transitive, so an object referenced only by another reachable object stays alive. An object becomes **eligible** for collection when its last reachable reference disappears: the variable goes out of scope, is reassigned, or is set to `null`. Two objects referring only to each other are collected together, since the collector traces from roots rather than counting references. When the collector actually runs is up to the JVM. `finalize()` is deprecated; use try-with-resources to release files and sockets, because memory is the only resource the GC manages.

## Worked examples

### Example 1: Constructors, overloading, aliasing, and statics

```java
public class Main {
    static class Point {
        private static int created = 0;
        private final int x, y;

        Point(int x, int y) { this.x = x; this.y = y; created++; }
        Point() { this(0, 0); }

        double distance() { return Math.sqrt(x * x + y * y); }
        double distance(Point other) {
            int dx = x - other.x, dy = y - other.y;
            return Math.sqrt(dx * dx + dy * dy);
        }
        static int created() { return created; }
        public String toString() { return "(" + x + ", " + y + ")"; }
    }

    static class Counter { int value; }

    static void bump(Counter c) { c.value++; }
    static void replace(Counter c) { c = new Counter(); c.value = 100; }

    public static void main(String[] args) {
        Point a = new Point(3, 4);
        Point origin = new Point();
        System.out.println(a + " is " + a.distance() + " from " + origin);
        System.out.println(a.distance(new Point(6, 8)));
        System.out.println("points created: " + Point.created());

        Counter c1 = new Counter();
        Counter alias = c1;
        bump(alias);
        replace(c1);
        System.out.println("c1.value = " + c1.value + ", same object: " + (c1 == alias));
        Counter none = null;
        try {
            bump(none);
        } catch (NullPointerException e) {
            System.out.println("calling through null throws NullPointerException");
        }
    }
}
```

Output:

```text
(3, 4) is 5.0 from (0, 0)
5.0
points created: 3
c1.value = 1, same object: true
calling through null throws NullPointerException
```

The no-argument constructor delegates with `this(0, 0)`, so every point increments the shared static counter. `bump` changes the object that both `c1` and `alias` refer to; `replace` only rebinds its own parameter, so the caller's object keeps the value 1.

### Example 2: When objects become eligible for collection

Consider this method:

```java
static void process() {
    Student a = new Student("Asha", 80);   // object A
    Student b = new Student("Ravi", 70);   // object B
    a = b;                                  // (1)
    Student[] team = { b };                 // (2) the array also refers to B
    b = null;                               // (3)
}                                           // (4)
```

- After line (1), nothing refers to object A, so **A is eligible** for collection.
- After line (2), object B is reachable through both `a` and the array.
- After line (3), B is still reachable through `a` and `team[0]`, so it is **not** eligible.
- At (4), the method returns, its frame disappears, and the local variables `a` and `team` stop being roots, so B and the array become eligible.

Eligibility is about reachability, not about how many variables were set to `null`. The JVM may reclaim eligible objects at any later time, or never if the program ends first.

## Applications

- **Domain models:** classes such as `Order`, `Customer`, and `Invoice` encapsulate business data.
- **Memory tuning:** understanding reachability explains leaks through caches and listeners.
- **APIs:** overloads such as `println(int)`, `println(String)` give convenient interfaces.
- **Shared configuration:** static constants and counters belong to the class, not instances.

## Common mistakes

- **Shadowing fields.** `name = name;` assigns the parameter to itself; write `this.name = name;`.
- **Assuming assignment copies objects.** It copies references; both variables see changes.
- **Accessing instance fields from static methods.** There is no `this` in a static context.
- **Relying on `finalize` or `System.gc()`.** Release non-memory resources explicitly with try-with-resources.
- **Holding references in long-lived collections.** Reachable objects are never collected.

## Revision notes

- Classes have fields, constructors, and methods; keep fields private.
- `this(...)` chains constructors; writing any constructor removes the default one.
- Class-type variables hold references; assignment creates aliases; `null` dereference throws.
- Overloading: same name, different parameters, chosen at compile time.
- `static`: one copy per class; no `this` in static methods.
- An object is eligible for GC when unreachable from roots (stack locals, statics, threads).

## Practice questions

:::question basic
What happens to the default no-argument constructor when you write a constructor that takes parameters?
:::answer
Java no longer provides it. If code calls `new Student()` without arguments, you must write a no-argument constructor yourself, otherwise the call does not compile.
:::

:::question basic
After `Student s1 = new Student("A", 1); Student s2 = s1; s2.addBonus(5);`, has `s1` changed?
:::answer
Yes. `s2 = s1` copies the reference, so both variables refer to the same object, and the bonus added through `s2` is visible through `s1`.
:::

:::question intermediate
Why can a `static` method not read an instance field directly?
:::answer
A static method belongs to the class and is called without any particular object, so there is no `this` reference identifying whose field to read. It can access instance fields only through an object reference passed in or created inside the method.
:::

:::question intermediate
Two objects reference each other but nothing else references either. Will they be garbage collected? Why?
:::answer
Yes. Java's collectors trace reachability from GC roots instead of counting references. Since neither object is reachable from any root, both are unreachable and eligible for collection, even though they refer to each other.
:::

:::question advanced
An app registers a listener object with a long-lived event bus and never unregisters it. Why does memory keep growing, and what are two fixes?
:::answer
The event bus is reachable for the application's whole life and holds references to every registered listener, so each listener, and everything it references, stays reachable and can never be collected. Fixes: unregister listeners when their owner is closed, or have the bus hold listeners through weak references (for example a `WeakHashMap` or `WeakReference`), so that listeners with no other references can be collected.
:::

## Further learning

- **Next:** *Extending Classes & Super Keyword* builds class hierarchies from these classes.
- **Related:** *JVM Architecture & Bytecode* explains the heap, stacks, and garbage collector in more depth.
