---
lesson: java-generic-types-wildcards
title: Generic Types & Wildcard Bounds
summary: Writing generic classes and methods in Java, bounded type parameters, how type erasure works and what it forbids, and using wildcards with the PECS rule (producer extends, consumer super).
minutes: 40
type: theory
objectives:
  - Write generic classes and methods with type parameters and bounded types
  - Explain type erasure and its consequences, such as no generic arrays and no instanceof on parameterised types
  - Use ? extends and ? super wildcards correctly by applying the PECS rule
review: ai-draft
---
## Introduction

Before generics, a Java `List` held plain `Object`s, so every read needed a cast and a wrong element caused a `ClassCastException` far from where it was added. **Generics** let you write `List<String>`, and the compiler guarantees that only strings go in and comes out without casts. Generics also let you write reusable classes and algorithms, but Java implements them with **type erasure**, which explains several surprising rules, and **wildcards** add flexibility that confuses many learners until the PECS rule makes it clear.

**Before you start:** you should know classes, interfaces, inheritance, and the collections framework.

## Core theory

### Generic classes and methods

```java
class Box<T> {
    private T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}

static <T> T firstOf(List<T> items) { return items.get(0); }
```

`T` is a **type parameter**; `Box<String>` and `Box<Integer>` supply type arguments. A generic method declares its type parameters before the return type, and the compiler usually **infers** them from the arguments. The **diamond** `new Box<>("hi")` lets the compiler infer the type arguments of a constructor. Type arguments must be reference types, so you write `List<Integer>`, not `List<int>`.

### Bounded type parameters

`<T extends Comparable<T>>` restricts `T` to types that can be compared with themselves, which lets the method call `compareTo`:

```java
static <T extends Comparable<T>> T max(List<T> items) { ... }
```

`extends` is used for both classes and interfaces in bounds, and several bounds combine with `&`: `<T extends Number & Comparable<T>>`.

### Type erasure

Java generics exist only at **compile time**. The compiler checks types and inserts casts, then **erases** type parameters: `T` becomes its bound (or `Object`), so `List<String>` and `List<Integer>` are both just `List` at run time. Consequences:

- `new T()` and `new T[10]` are not allowed: the runtime does not know `T`.
- `obj instanceof List<String>` is not allowed; only `instanceof List<?>`.
- You cannot overload `void f(List<String>)` and `void f(List<Integer>)`: they erase to the same signature.
- Static fields are shared by all parameterisations: `Box<String>` and `Box<Integer>` are the same class.
- **Raw types** (`List` without arguments) disable checking and exist only for compatibility with old code; avoid them.

### Invariance and wildcards

Generic types are **invariant**: even though `Integer` is a subtype of `Number`, `List<Integer>` is **not** a subtype of `List<Number>`. If it were, you could add a `Double` to a list that must hold only integers. **Wildcards** express the flexibility you need safely:

- `List<? extends Number>`: a list of **some** subtype of `Number`. You can **read** elements as `Number`, but you cannot add anything except `null`, because you do not know the exact element type.
- `List<? super Integer>`: a list of `Integer` or some supertype. You can **add** `Integer`s, but reading gives only `Object`.
- `List<?>`: a list of unknown type; read as `Object`, add nothing.

### PECS: Producer Extends, Consumer Super

If a parameter **produces** values for your method (you read from it), use `? extends T`. If it **consumes** values from your method (you write into it), use `? super T`. If it does both, use plain `T`. The standard library's `Collections.copy(List<? super T> dest, List<? extends T> src)` follows this rule exactly.

## Worked examples

### Example 1: Generic class, generic bounded method, and erasure

```java
import java.util.ArrayList;
import java.util.List;

public class Main {
    static class Pair<A, B> {
        private final A first;
        private final B second;
        Pair(A first, B second) { this.first = first; this.second = second; }
        A first() { return first; }
        B second() { return second; }
        <C> Pair<A, C> withSecond(C newSecond) { return new Pair<>(first, newSecond); }
        public String toString() { return "(" + first + ", " + second + ")"; }
    }

    static <T extends Comparable<T>> T max(List<T> items) {
        T best = items.get(0);
        for (T item : items) if (item.compareTo(best) > 0) best = item;
        return best;
    }

    public static void main(String[] args) {
        Pair<String, Integer> p = new Pair<>("Asha", 91);
        Pair<String, String> q = p.withSecond("A grade");
        System.out.println(p + " " + q + " " + p.second().getClass().getSimpleName());

        System.out.println(max(List.of(3, 17, 9)) + " " + max(List.of("pear", "apple", "zucchini")));

        List<String> words = new ArrayList<>();
        List<Integer> numbers = new ArrayList<>();
        System.out.println("same runtime class: " + (words.getClass() == numbers.getClass()));

        List raw = words;
        raw.add(42);
        try {
            String s = words.get(0);
            System.out.println(s);
        } catch (ClassCastException e) {
            System.out.println("raw type let an Integer into a List<String>: ClassCastException on read");
        }
    }
}
```

Output:

```text
(Asha, 91) (Asha, A grade) Integer
17 zucchini
same runtime class: true
raw type let an Integer into a List<String>: ClassCastException on read
```

`max` works for any type that can compare itself, here `Integer` and `String`. After erasure, `ArrayList<String>` and `ArrayList<Integer>` share one runtime class. The raw-type assignment bypasses compile-time checks (the compiler only warns), so the error surfaces later, at the compiler-inserted cast when the element is read.

### Example 2: Wildcards and PECS

```java
import java.util.ArrayList;
import java.util.List;

public class Main {
    static double sum(List<? extends Number> numbers) {
        double total = 0;
        for (Number n : numbers) total += n.doubleValue();
        return total;
    }

    static void addSquares(List<? super Integer> sink, int n) {
        for (int i = 1; i <= n; i++) sink.add(i * i);
    }

    static <T> void copyInto(List<? super T> dest, List<? extends T> src) {
        for (T item : src) dest.add(item);
    }

    public static void main(String[] args) {
        List<Integer> ints = List.of(1, 2, 3);
        List<Double> doubles = List.of(0.5, 1.5);
        System.out.println(sum(ints) + " " + sum(doubles));

        List<Number> numbers = new ArrayList<>();
        List<Object> objects = new ArrayList<>();
        addSquares(numbers, 3);
        addSquares(objects, 2);
        System.out.println(numbers + " " + objects);

        List<Object> all = new ArrayList<>();
        copyInto(all, ints);
        copyInto(all, List.of("x", "y"));
        System.out.println(all);
    }
}
```

Output:

```text
6.0 2.0
[1, 4, 9] [1, 4]
[1, 2, 3, x, y]
```

`sum` only reads, so `? extends Number` lets it accept lists of `Integer`, `Double`, or any other `Number`. `addSquares` only writes `Integer`s, so `? super Integer` accepts lists of `Integer`, `Number`, or `Object`. `copyInto` combines both: the source produces (`extends`) and the destination consumes (`super`).

## Applications

- **Collections and streams:** every collection and stream signature is generic.
- **Reusable utilities:** `max`, `sort`, and `binarySearch` work for any comparable type.
- **APIs:** wildcards let library methods accept the widest safe range of argument types.
- **Type-safe containers:** `Optional<T>`, `Map<K, V>`, `Future<V>` carry exact types.

## Common mistakes

- **Using raw types.** They disable checking and move errors to run time.
- **Expecting `List<Integer>` to be a `List<Number>`.** Generics are invariant; use `List<? extends Number>`.
- **Trying to add to a `List<? extends T>`.** Only `null` can be added; use `? super T` for writing.
- **Creating generic arrays.** `new T[n]` is illegal; use an `ArrayList<T>`.
- **Overloading methods that differ only in type arguments.** They clash after erasure.

## Revision notes

- `class Box<T>`, `static <T> T f(List<T>)`; the diamond `<>` infers type arguments.
- Bounds: `<T extends Comparable<T>>`, multiple with `&`.
- Erasure: generics are compile-time only; no `new T`, no `instanceof List<String>`, one runtime class.
- Generics are invariant: `List<Integer>` is not a `List<Number>`.
- `? extends T`: read as `T`; `? super T`: write `T`; `?`: read `Object`.
- PECS: Producer Extends, Consumer Super.

## Practice questions

:::question basic
What advantage does `List<String>` have over a raw `List`?
:::answer
The compiler checks that only strings are added and inserts casts automatically when reading, so type errors are caught at compile time instead of causing `ClassCastException` at run time, and code needs no explicit casts.
:::

:::question basic
Why can you not write `new T()` inside a generic class?
:::answer
Because of type erasure, the type argument for `T` is not available at run time, so the JVM cannot know which constructor to call. A common workaround is to pass a factory such as `Supplier<T>` into the class.
:::

:::question intermediate
Why does the compiler reject passing a `List<Integer>` to `void printAll(List<Number> nums)`, and how should the method be declared?
:::answer
Generics are invariant: `List<Integer>` is not a subtype of `List<Number>`, because otherwise the method could add a `Double` to a list of integers. Since the method only reads the elements, declare it as `void printAll(List<? extends Number> nums)`.
:::

:::question intermediate
State the PECS rule and apply it to a method that moves all elements from one list into another.
:::answer
Producer Extends, Consumer Super: use `? extends T` for parameters you read from and `? super T` for parameters you write to. For moving elements: `static <T> void moveAll(List<? extends T> from, List<? super T> to)`.
:::

:::question advanced
Why can you not overload `void process(List<String> s)` and `void process(List<Integer> n)` in one class?
:::answer
After type erasure both methods have the same signature, `process(List)`, so the JVM would see two identical methods. The compiler reports a name clash. Use different method names or a single generic method instead.
:::

## Further learning

- **Next:** *File I/O with java.nio* uses generic types such as `List<String>` and `Stream<Path>`.
- **Related:** *Generic Programming with Templates* in C++ compares templates, which are instantiated per type, with erased generics.
