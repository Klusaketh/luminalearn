---
lesson: java-syntax-types-control
title: Syntax, Types & Control Flow
summary: Java's primitive and reference types, operators and type conversion, conditionals, loops, the switch statement, and how to write static methods.
minutes: 45
type: theory
objectives:
  - Choose among Java's eight primitive types and distinguish primitive values from object references
  - Predict the result of expressions involving integer division, casts, compound assignment, and overflow
  - Write programs with if, switch, for, enhanced for, while, and do-while, and organise code into static methods
review: ai-draft
---
## Introduction

Java's syntax will look familiar to anyone who knows C or C++, but its rules are stricter and more predictable: every primitive type has the same size on every platform, integer overflow is well defined, and the compiler refuses to read a local variable before it is assigned. This lesson covers the building blocks you will use in every Java program: types, operators, control flow, and methods.

**Before you start:** you should understand variables, conditions, and loops in some language, and know what the JVM is.

## Core theory

### Program structure

Every Java program is made of classes. Execution starts at `public static void main(String[] args)`. Statements end with semicolons, blocks use braces, and the file `Main.java` must contain the public class `Main`.

### Primitive types

| Type | Size | Range / precision |
| :--- | :--- | :--- |
| `byte` | 8 bits | -128 to 127 |
| `short` | 16 bits | -32,768 to 32,767 |
| `int` | 32 bits | about $\pm 2.1 \times 10^9$ |
| `long` | 64 bits | about $\pm 9.2 \times 10^{18}$ (literal suffix `L`) |
| `float` | 32 bits | about 7 decimal digits (suffix `f`) |
| `double` | 64 bits | about 15 to 16 decimal digits |
| `char` | 16 bits | a UTF-16 code unit, 0 to 65,535 |
| `boolean` | n/a | `true` or `false` |

These sizes are fixed by the language, unlike in C. `boolean` is not a number: `if (x)` with an `int` does not compile.

### Primitive values versus references

A primitive variable holds its value directly. Every other type, including `String`, arrays, and your own classes, is a **reference type**: the variable holds a reference to an object on the heap, or `null`. Assigning a reference copies the reference, not the object, so two variables can refer to the same object.

### Operators and conversions

- Integer division truncates towards zero (`7 / 2` is 3, `-7 / 2` is -3); `%` gives a remainder with the sign of the dividend.
- **Widening** conversions (`int` to `long`, `int` to `double`) happen automatically; **narrowing** ones need a cast: `(int) 3.99` is 3.
- In arithmetic, `byte`, `short`, and `char` are promoted to `int`, so `byte b = a + 1;` fails without a cast, yet compound assignment `b += 1` compiles because it includes an implicit cast.
- Integer overflow **wraps around** silently in two's complement: `Integer.MAX_VALUE + 1` is `Integer.MIN_VALUE`. Use `long`, or `Math.addExact`, which throws on overflow.
- `&&` and `||` short-circuit; `==` on primitives compares values, but on references compares identity.

### Control flow

`if` / `else if` / `else`; `while`, `do-while`, and `for` loops; the **enhanced for** loop `for (int x : array)`; and `break` / `continue`, which can take a **label** to leave an outer loop. The classic `switch` statement works on `int`-like types, `char`, `String`, and enums, with `case` labels and fall-through unless you `break`. Java 14 added switch **expressions** with arrow labels (`case 1 -> "one";`) that never fall through.

### Static methods and variables

A `static` method belongs to the class and is called as `ClassName.method(...)` or just `method(...)` inside the class. Parameters are passed **by value**: for a primitive, the value is copied; for a reference, the reference is copied, so the method can change the object it refers to but cannot make the caller's variable refer to a different object. Local variables must be definitely assigned before use, and `var` (Java 10) lets the compiler infer a local variable's type.

## Worked examples

### Example 1: Types, division, casts, and overflow

```java
public class Main {
    public static void main(String[] args) {
        int a = 7, b = 2;
        System.out.println(a / b + " " + a % b + " " + (-7 / 2) + " " + (-7 % 2));
        System.out.println((double) a / b);
        System.out.println((int) 3.99 + " " + Math.round(3.5) + " " + Math.round(-3.5));

        byte small = 120;
        small += 10;
        System.out.println(small);

        int max = Integer.MAX_VALUE;
        System.out.println(max + 1);
        long big = (long) max + 1;
        System.out.println(big);
        try {
            Math.addExact(max, 1);
        } catch (ArithmeticException e) {
            System.out.println("addExact: " + e.getMessage());
        }
        char c = 'A';
        System.out.println(c + 1);
        System.out.println((char) (c + 1));
        System.out.println(0.1 + 0.2);
    }
}
```

Output:

```text
3 1 -3 -1
3.5
3 4 -3
-126
-2147483648
2147483648
addExact: integer overflow
66
B
0.30000000000000004
```

`small += 10` silently casts 130 back to a `byte`, which wraps to -126. `Math.round(-3.5)` rounds towards positive infinity on a tie, giving -3. `c + 1` is an `int` (66) until it is cast back to `char`.

### Example 2: Control flow and static methods

```java
public class Main {
    static boolean isPrime(int n) {
        if (n < 2) return false;
        for (int d = 2; (long) d * d <= n; d++) {
            if (n % d == 0) return false;
        }
        return true;
    }

    static String grade(int marks) {
        switch (marks / 10) {
            case 10:
            case 9:
                return "A";
            case 8:
                return "B";
            case 7:
            case 6:
                return "C";
            default:
                return "F";
        }
    }

    public static void main(String[] args) {
        StringBuilder primes = new StringBuilder();
        for (int i = 1; i <= 30; i++) if (isPrime(i)) primes.append(i).append(' ');
        System.out.println(primes.toString().trim());

        int[] marks = {95, 82, 67, 40, 100};
        for (int m : marks) System.out.print(grade(m));
        System.out.println();

        outer:
        for (int r = 1; r <= 3; r++) {
            for (int c = 1; c <= 3; c++) {
                if (r * c == 4) {
                    System.out.println("first product 4 at row " + r + ", col " + c);
                    break outer;
                }
            }
        }
        int n = 0;
        do { n++; } while (n < 0);
        System.out.println("do-while ran " + n + " time");
    }
}
```

Output:

```text
2 3 5 7 11 13 17 19 23 29
ABCFA
first product 4 at row 2, col 2
do-while ran 1 time
```

The labelled `break outer` leaves both loops at once. In `grade`, cases 10 and 9 share one `return`, an intentional fall-through. Writing `(long) d * d` avoids overflow for large `n`.

## Applications

- **Every Java program:** these rules underlie Android apps, web services, and enterprise systems.
- **Financial code:** knowing overflow and floating-point behaviour avoids costly errors; money uses `long` cents or `BigDecimal`.
- **Algorithms:** loops and static helper methods are the core of coding interviews.
- **Portability:** fixed type sizes make numeric results identical on every platform.

## Common mistakes

- **Expecting `5 / 2` to be 2.5.** Cast one operand to `double`.
- **Silent overflow.** Use `long` or `Math.addExact` when values can exceed 2 billion.
- **Comparing strings or other objects with `==`.** It compares references; use `equals`.
- **Forgetting `break` in a classic switch.** Execution falls through to the next case.
- **Comparing doubles with `==`.** Compare with a tolerance.

## Revision notes

- 8 primitives with fixed sizes: `byte short int long float double char boolean`.
- Reference variables hold references or `null`; assignment copies the reference.
- Integer division truncates towards zero; overflow wraps silently.
- Narrowing needs a cast; compound assignment casts implicitly.
- Enhanced for, labelled break, `do-while`, and `switch` on `String`/enum.
- Java passes everything by value, including references.

## Practice questions

:::question basic
What are the values of `17 / 4` and `17 % 4` in Java?
:::answer
`17 / 4` is 4, because integer division discards the fraction, and `17 % 4` is 1, since $17 = 4 \times 4 + 1$.
:::

:::question basic
Why does `int x = 5; if (x) { ... }` not compile in Java?
:::answer
Java's `if` requires a `boolean` expression and does not convert numbers to booleans. Write an explicit comparison such as `if (x != 0)`.
:::

:::question intermediate
Why does `byte b = 10; b = b + 1;` fail to compile while `b += 1;` compiles?
:::answer
In `b + 1`, the `byte` is promoted to `int`, so the result is an `int`, and assigning an `int` to a `byte` is a narrowing conversion that needs an explicit cast. The compound assignment `b += 1` is defined to include an implicit cast back to the variable's type, so it compiles.
:::

:::question intermediate
What does `Integer.MAX_VALUE + 1` evaluate to, and how can you detect overflow instead?
:::answer
It wraps around to `Integer.MIN_VALUE`, -2147483648, because Java integer arithmetic is two's complement modulo $2^{32}$. `Math.addExact(Integer.MAX_VALUE, 1)` throws an `ArithmeticException` instead, and computing in `long` avoids the overflow.
:::

:::question advanced
A method `void reset(int[] arr) { arr = new int[arr.length]; }` does not clear the caller's array, but `void reset(int[] arr) { java.util.Arrays.fill(arr, 0); }` does. Explain using Java's parameter-passing rule.
:::answer
Java passes the reference by value: `arr` is a copy of the caller's reference. Assigning a new array to `arr` changes only the local copy, so the caller still refers to the old array. `Arrays.fill` follows the copied reference to the same array object and modifies its elements, which the caller sees.
:::

## Further learning

- **Next:** *Strings, Arrays & Wrapper Classes* covers the reference types used everywhere in Java.
- **Related:** *Data Types, Operators & Expressions* in C Programming compares the same ideas where sizes are not fixed.
