---
lesson: java-lambdas-streams
title: Lambdas & the Streams API
summary: Lambda expressions, method references, and the core functional interfaces, and how to build Stream pipelines with filter, map, sorted, reduce, and collectors such as groupingBy, with lazy evaluation explained.
minutes: 50
type: theory
objectives:
  - Write lambda expressions and method references for standard functional interfaces
  - Build stream pipelines with intermediate and terminal operations and explain lazy evaluation
  - Summarise data with reduce and collectors such as toList, joining, groupingBy, and counting
review: ai-draft
---
## Introduction

Before Java 8, processing a collection meant writing loops: create a result list, iterate, test, transform, add. **Lambdas** made it possible to pass behaviour as a value, and the **Streams API** uses them to describe *what* to compute, such as "the names of students with marks above 80, sorted", as a pipeline of operations. Stream code is often shorter and clearer than loops, and it can be parallelised with one method call.

**Before you start:** you should know interfaces, functional interfaces, generics such as `List<String>`, and the collections framework.

## Core theory

### Lambdas and method references

A lambda is an anonymous implementation of a functional interface: `(a, b) -> a + b`, `s -> s.length() > 3`, or with a block body, `x -> { int y = x * 2; return y + 1; }`. Parameter types are usually inferred. A lambda may use local variables from the enclosing scope only if they are **effectively final** (never reassigned).

A **method reference** is a shorthand for a lambda that just calls an existing method:

| Form | Example | Equivalent lambda |
| :--- | :--- | :--- |
| static method | `Integer::parseInt` | `s -> Integer.parseInt(s)` |
| instance method of a particular object | `System.out::println` | `x -> System.out.println(x)` |
| instance method of an arbitrary object | `String::toUpperCase` | `s -> s.toUpperCase()` |
| constructor | `ArrayList::new` | `() -> new ArrayList<>()` |

Core functional interfaces: `Predicate<T>` (T → boolean), `Function<T, R>` (T → R), `Consumer<T>` (T → nothing), `Supplier<T>` (nothing → T), `BinaryOperator<T>` ((T, T) → T), plus primitive versions such as `IntPredicate`.

### Stream pipelines

A pipeline has three parts:

1. A **source**: `list.stream()`, `Arrays.stream(array)`, `Stream.of(...)`, `IntStream.range(0, n)`.
2. Zero or more **intermediate operations**, each returning a new stream: `filter`, `map`, `mapToInt`, `flatMap`, `distinct`, `sorted`, `limit`, `skip`, `peek`.
3. One **terminal operation**, which produces a result or side effect: `collect`, `forEach`, `reduce`, `count`, `sum`, `average`, `min`, `max`, `anyMatch`, `allMatch`, `findFirst`.

Streams are **lazy**: intermediate operations do nothing until a terminal operation runs, and then elements flow through the whole pipeline one at a time. That allows **short-circuiting**: `filter(...).findFirst()` stops at the first match without examining the rest. A stream can be consumed **only once**, and streams do not modify their source.

### Reducing and collecting

`reduce(identity, accumulator)` folds elements into one value: `stream.reduce(0, Integer::sum)`. Numeric streams (`IntStream`, `DoubleStream`) offer `sum()`, `average()` (an `OptionalDouble`), and `summaryStatistics()`. `Optional<T>` results such as from `max` or `findFirst` represent "maybe a value": use `orElse`, `ifPresent`, or `map` instead of calling `get()` blindly.

`collect` with **collectors** builds results:

- `Collectors.toList()`, `toSet()`, `toMap(keyFn, valueFn)`
- `Collectors.joining(", ")` concatenates strings
- `Collectors.groupingBy(classifier)` builds a `Map<K, List<T>>`, optionally with a downstream collector: `groupingBy(f, counting())`, `groupingBy(f, averagingInt(g))`
- `Collectors.partitioningBy(predicate)` splits into `true` and `false` groups

`groupingBy` produces a `HashMap` by default; pass `TreeMap::new` as the map factory when sorted keys are wanted.

### When to prefer loops

Streams suit transformations and aggregations. Plain loops remain clearer for complex control flow, early exits with several conditions, or modifying local state. Avoid side effects inside stream operations, such as adding to an external list in `map`; collect results instead. `parallelStream()` can speed up large CPU-bound pipelines but adds overhead and requires operations without shared mutable state.

## Worked examples

### Example 1: A student-report pipeline

```java
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Main {
    static class Student {
        final String name, dept;
        final int marks;
        Student(String name, String dept, int marks) { this.name = name; this.dept = dept; this.marks = marks; }
        String getName() { return name; }
        String getDept() { return dept; }
        int getMarks() { return marks; }
    }

    public static void main(String[] args) {
        List<Student> students = List.of(
            new Student("Asha", "CSE", 91), new Student("Ravi", "ECE", 78), new Student("Meena", "CSE", 85),
            new Student("John", "ME", 64), new Student("Sara", "ECE", 88));

        List<String> top = students.stream()
            .filter(s -> s.getMarks() >= 80)
            .sorted(Comparator.comparingInt(Student::getMarks).reversed())
            .map(Student::getName)
            .collect(Collectors.toList());
        System.out.println("80+: " + top);

        double avg = students.stream().mapToInt(Student::getMarks).average().orElse(0);
        System.out.printf("average %.1f%n", avg);

        Map<String, Long> perDept = students.stream()
            .collect(Collectors.groupingBy(Student::getDept, TreeMap::new, Collectors.counting()));
        System.out.println("per department: " + perDept);

        Map<String, Double> deptAvg = students.stream()
            .collect(Collectors.groupingBy(Student::getDept, TreeMap::new, Collectors.averagingInt(Student::getMarks)));
        System.out.println("department averages: " + deptAvg);

        String names = students.stream().map(Student::getName).map(String::toUpperCase)
            .collect(Collectors.joining(", ", "[", "]"));
        System.out.println(names);
        System.out.println("anyone below 60? " + students.stream().anyMatch(s -> s.getMarks() < 60));
    }
}
```

Output:

```text
80+: [Asha, Sara, Meena]
average 81.2
per department: {CSE=2, ECE=2, ME=1}
department averages: {CSE=88.0, ECE=83.0, ME=64.0}
[ASHA, RAVI, MEENA, JOHN, SARA]
anyone below 60? false
```

Each pipeline reads as a sentence. `TreeMap::new` makes the grouped results print in key order. The average of 91, 78, 85, 64, and 88 is 81.2.

### Example 2: Laziness, short-circuiting, and reduce

```java
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class Main {
    public static void main(String[] args) {
        Stream<Integer> pipeline = Stream.of(5, 12, 8, 21, 3)
            .filter(n -> { System.out.println("  testing " + n); return n > 10; });
        System.out.println("pipeline built, nothing tested yet");
        Optional<Integer> first = pipeline.findFirst();
        System.out.println("first > 10: " + first.orElse(-1));

        int sumOfSquares = IntStream.rangeClosed(1, 5).map(i -> i * i).sum();
        int product = Stream.of(1, 2, 3, 4).reduce(1, (a, b) -> a * b);
        System.out.println(sumOfSquares + " " + product);

        List<List<String>> nested = List.of(List.of("a", "b"), List.of("c"), List.of());
        List<String> flat = nested.stream().flatMap(List::stream).collect(Collectors.toList());
        System.out.println(flat);

        Optional<String> longest = Stream.of("kiwi", "banana", "fig").max((x, y) -> x.length() - y.length());
        System.out.println(longest.map(String::toUpperCase).orElse("none"));
        System.out.println(Stream.<String>empty().findAny().isPresent());
    }
}
```

Output:

```text
pipeline built, nothing tested yet
  testing 5
  testing 12
first > 10: 12
55 24
[a, b, c]
BANANA
false
```

Building the pipeline prints nothing: the `filter` runs only when `findFirst` pulls elements, and it stops after 12, so 8, 21, and 3 are never tested. `flatMap` turns a stream of lists into one stream of their elements, and `Optional` handles the "maybe empty" result cleanly.

## Applications

- **Reporting:** grouping, counting, and averaging records from databases or files.
- **Data cleaning:** filtering invalid rows and transforming fields.
- **Event handling:** lambdas as listeners and callbacks.
- **Parallel processing:** `parallelStream` for large, independent computations.

## Common mistakes

- **Reusing a stream.** A stream can be traversed only once; create a new one.
- **Side effects inside `map` or `filter`.** Collect results instead of mutating external collections.
- **Calling `Optional.get()` without checking.** Use `orElse`, `orElseThrow`, or `ifPresent`.
- **Expecting `groupingBy` results in sorted order.** Pass `TreeMap::new` if order matters.
- **Capturing a variable that is later reassigned.** Lambdas require effectively final locals.

## Revision notes

- Lambda: `(params) -> expression` implements a functional interface.
- Method references: `Class::staticMethod`, `obj::method`, `Class::instanceMethod`, `Class::new`.
- Pipeline: source → intermediate (lazy) → terminal (triggers execution).
- `filter`, `map`, `flatMap`, `sorted`, `distinct`, `limit`; `collect`, `reduce`, `count`, `anyMatch`, `findFirst`.
- `Collectors.toList`, `joining`, `groupingBy` (+ `counting`, `averagingInt`), `partitioningBy`.
- Streams are single-use and do not modify their source; prefer `Optional` handling over `get()`.

## Practice questions

:::question basic
Rewrite `s -> s.toUpperCase()` as a method reference.
:::answer
`String::toUpperCase`. It is a reference to an instance method of an arbitrary object: the stream element becomes the object on which `toUpperCase` is called.
:::

:::question basic
What is the difference between an intermediate and a terminal stream operation?
:::answer
An intermediate operation, such as `filter` or `map`, returns a new stream and is lazy: it does no work by itself. A terminal operation, such as `collect`, `count`, or `forEach`, produces a result or side effect and triggers the whole pipeline to run.
:::

:::question intermediate
Write a pipeline that returns the lengths of the distinct words in a list, sorted in ascending order.
:::answer
`words.stream().distinct().map(String::length).sorted().collect(Collectors.toList())`. `distinct` removes repeated words first; mapping to lengths may still produce duplicate lengths, which is fine because the requirement concerns distinct words.
:::

:::question intermediate
Why does `Stream.of(1, 2, 3).peek(System.out::println);` print nothing?
:::answer
`peek` is an intermediate operation, and streams are lazy, so without a terminal operation no element ever flows through the pipeline. Adding a terminal operation such as `.count()` or `.collect(...)` would run it (although `count` may skip `peek` when it can compute the size directly).
:::

:::question advanced
Use `groupingBy` to count how many words of each length appear in a list, with lengths in ascending order. Explain each part.
:::answer
`Map<Integer, Long> byLength = words.stream().collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));`. `String::length` is the classifier giving each word's group key; `TreeMap::new` supplies a sorted map so lengths iterate in ascending order; `Collectors.counting()` is the downstream collector that turns each group's list into its count.
:::

## Further learning

- **Next:** *Generic Types & Wildcard Bounds* explains the type parameters seen in stream signatures.
- **Related:** *STL Algorithms & Lambda Expressions* in C++ shows the same ideas with iterators.
