---
lesson: java-strings-arrays-wrappers
title: Strings, Arrays & Wrapper Classes
summary: Java's immutable String class and the string pool, StringBuilder for efficient construction, arrays and the Arrays utility class, wrapper classes with autoboxing, and the equality pitfalls of == versus equals.
minutes: 45
type: theory
objectives:
  - Use String methods correctly and explain immutability, the string pool, and why equals must be used for comparison
  - Build strings efficiently with StringBuilder and work with one- and two-dimensional arrays and java.util.Arrays
  - Explain autoboxing and unboxing, the Integer cache, and the NullPointerException risks of wrapper types
review: ai-draft
---
## Introduction

Strings, arrays, and wrapper classes are the reference types you meet first in Java, and they hide the language's most famous pitfalls: `==` that "sometimes works" for strings and `Integer` values, string concatenation in loops that runs slowly, and a `NullPointerException` from a line that seems to contain no objects at all. This lesson explains how each type behaves so those surprises disappear.

**Before you start:** you should know Java primitive and reference types, loops, and static methods.

## Core theory

### String is immutable

A `String` object never changes after it is created. Methods such as `toUpperCase`, `replace`, `trim`, `substring`, and `concat` return **new** strings. Immutability makes strings safe to share between threads, to cache, and to use as `HashMap` keys. Useful methods: `length()`, `charAt(i)`, `indexOf(s)` (-1 if absent), `contains`, `startsWith`, `split(regex)`, `String.join(sep, parts)`, `equalsIgnoreCase`, `compareTo`, `isEmpty`, and `strip`.

### The string pool and equality

String **literals** are interned: identical literals in a program refer to one object in the **string pool**. Strings created at run time, for example with `new String("hi")` or by concatenating non-constant values, are separate objects. Therefore `==`, which compares references, may be `true` for two literals and `false` for equal strings built at run time. Always compare contents with `a.equals(b)`; write `"yes".equals(input)` to avoid a `NullPointerException` when `input` is `null`.

### StringBuilder

Because strings are immutable, `s += x` inside a loop creates a new string each time and copies all the characters so far, which is $O(n^2)$ overall. `StringBuilder` keeps a growable character buffer: `append`, `insert`, `reverse`, `deleteCharAt`, and `setCharAt` modify it in place, and `toString()` produces the final string. The compiler already uses a builder for a single expression like `a + b + c`; write one explicitly for loops.

### Arrays

An array has a fixed length set at creation: `int[] a = new int[5];` fills it with zeros (`false` or `null` for other types), and `int[] b = {3, 1, 2};` lists values. `a.length` is a field, not a method. Indexing is bounds-checked: `a[5]` throws `ArrayIndexOutOfBoundsException`. A two-dimensional array is an array of arrays, so rows can have different lengths (**jagged** arrays). `java.util.Arrays` provides `toString`, `deepToString`, `sort`, `binarySearch`, `fill`, `copyOf`, and `equals`; printing an array directly with `System.out.println(a)` shows only a type code and hash, not the contents.

### Wrapper classes and autoboxing

Each primitive has a wrapper class: `Integer`, `Long`, `Double`, `Boolean`, `Character`, and so on. Collections store objects only, so a `List<Integer>` holds `Integer` objects. **Autoboxing** converts `int` to `Integer` automatically, and **unboxing** converts back. Two traps follow:

- **Equality:** `Integer.valueOf` caches values from -128 to 127, so `==` between two boxed 100s is `true` but between two boxed 1000s is usually `false`. Use `equals` or compare unboxed `int`s.
- **null:** unboxing a `null` `Integer` throws `NullPointerException`, for example `int count = map.get("missing");`.

`Integer.parseInt("42")` parses text to an `int` and throws `NumberFormatException` on bad input; `String.valueOf(42)` and `Integer.toString(42)` convert back.

## Worked examples

### Example 1: String equality, immutability, and StringBuilder

```java
public class Main {
    public static void main(String[] args) {
        String a = "java";
        String b = "java";
        String c = new String("java");
        String d = "ja" + "va";
        String part = "ja";
        String e = part + "va";
        System.out.println((a == b) + " " + (a == c) + " " + (a == d) + " " + (a == e));
        System.out.println(a.equals(c) + " " + a.equals(e) + " " + (a == e.intern()));

        String s = "  Hello World  ";
        s.trim();
        System.out.println("[" + s + "]");
        s = s.trim().toUpperCase().replace('O', '0');
        System.out.println("[" + s + "]");
        System.out.println(s.indexOf("W") + " " + s.substring(6) + " " + s.length());

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= 5; i++) sb.append(i).append(i < 5 ? "," : "");
        sb.reverse();
        System.out.println(sb + " (" + sb.length() + " chars)");
        String[] words = "red,green,,blue".split(",");
        System.out.println(words.length + " " + String.join("|", words));
    }
}
```

Output:

```text
true false true false
true true true
[  Hello World  ]
[HELL0 W0RLD]
6 W0RLD 11
5,4,3,2,1 (9 chars)
4 red|green||blue
```

`a`, `b`, and `d` are the same pooled object, because `"ja" + "va"` is a compile-time constant. `c` and `e` are new objects with equal contents, so only `equals` (or `intern`) recognises them as equal. Calling `s.trim()` without assigning the result changes nothing.

### Example 2: Arrays, wrappers, and the Integer cache

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) {
        int[] nums = {42, 7, 19, 3};
        Arrays.sort(nums);
        System.out.println(Arrays.toString(nums) + " index of 19: " + Arrays.binarySearch(nums, 19));
        int[][] triangle = new int[4][];
        for (int r = 0; r < 4; r++) {
            triangle[r] = new int[r + 1];
            triangle[r][0] = triangle[r][r] = 1;
            for (int c = 1; c < r; c++) triangle[r][c] = triangle[r - 1][c - 1] + triangle[r - 1][c];
        }
        System.out.println(Arrays.deepToString(triangle));

        Integer x = 100, y = 100, p = 1000, q = 1000;
        System.out.println((x == y) + " " + (p == q) + " " + p.equals(q) + " " + (p.intValue() == q));

        List<Integer> list = new ArrayList<>(List.of(5, 10, 15));
        int total = 0;
        for (int v : list) total += v;
        System.out.println("total " + total);

        Map<String, Integer> stock = new HashMap<>();
        stock.put("pens", 12);
        Integer maybe = stock.get("ink");
        System.out.println("ink -> " + maybe);
        try {
            int count = stock.get("ink");
            System.out.println(count);
        } catch (NullPointerException ex) {
            System.out.println("unboxing null threw NullPointerException");
        }
        System.out.println(Integer.parseInt("-250") + 1);
    }
}
```

Output:

```text
[3, 7, 19, 42] index of 19: 2
[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1]]
true false true true
total 30
ink -> null
unboxing null threw NullPointerException
-249
```

`triangle` is a jagged array whose rows grow by one, filled with Pascal's triangle. Boxed 100s come from the shared cache, so `==` happens to be `true`; boxed 1000s are distinct objects. Unboxing the `null` returned by `get` throws.

## Applications

- **Input parsing:** `split`, `parseInt`, and `strip` turn text into data.
- **Report generation:** `StringBuilder` assembles large outputs efficiently.
- **Collections:** wrappers let primitives live in `List`, `Set`, and `Map`.
- **Algorithms:** arrays and `Arrays.sort` are the workhorses of coding problems.

## Common mistakes

- **Comparing strings or `Integer`s with `==`.** Use `equals`.
- **Ignoring a String method's return value.** Strings never change in place.
- **Concatenating in a loop.** Use `StringBuilder`.
- **Printing an array directly.** Use `Arrays.toString` or `Arrays.deepToString`.
- **Unboxing possible nulls.** Check `map.get` results or use `getOrDefault`.

## Revision notes

- `String` is immutable; methods return new strings.
- Literals are pooled; `==` compares references, `equals` compares contents.
- `StringBuilder` for repeated modification; `toString()` at the end.
- Arrays: fixed length, `.length`, bounds-checked, default values; `Arrays` utilities.
- Autoboxing converts between primitives and wrappers; `Integer` caches -128 to 127.
- Unboxing `null` throws `NullPointerException`.

## Practice questions

:::question basic
Why should strings be compared with `equals` rather than `==`?
:::answer
`==` compares references, so it is `true` only when both variables refer to the same object. Equal strings created at run time are usually different objects, so `==` can be `false` even though the contents match. `equals` compares the characters.
:::

:::question basic
What does `"a,b,,c".split(",").length` evaluate to?
:::answer
It is 4: the pieces are `"a"`, `"b"`, `""`, and `"c"`. The empty string between the two adjacent commas is kept (only trailing empty strings are removed by `split`).
:::

:::question intermediate
Why does building a long string with `result += line;` inside a loop of 100,000 iterations run slowly, and what should you use instead?
:::answer
Each `+=` creates a new `String` and copies every character accumulated so far, so the total copying grows with the square of the output size. A `StringBuilder` appends into a growable buffer in amortized constant time per character; call `toString()` once at the end.
:::

:::question intermediate
Explain why `Integer a = 127, b = 127;` gives `a == b` true but `Integer c = 128, d = 128;` usually gives `c == d` false.
:::answer
Autoboxing uses `Integer.valueOf`, which returns cached objects for values from -128 to 127, so `a` and `b` refer to the same object. 128 is outside the cache, so `c` and `d` are separate objects and `==`, which compares references, is false. Use `equals` to compare the values.
:::

:::question advanced
`int n = counts.get(word) + 1;` sometimes throws `NullPointerException` although no variable is visibly null. Explain and fix it.
:::answer
`counts.get(word)` returns `null` when the word is not in the map. Adding 1 requires unboxing the `Integer` to an `int`, and unboxing `null` throws `NullPointerException`. Use `counts.getOrDefault(word, 0) + 1`, or `counts.merge(word, 1, Integer::sum)` to update the count in one call.
:::

## Further learning

- **Next:** *Class Definitions & Memory Allocation* explains how objects like these are created and collected.
- **Related:** *Java Collections Framework Core* stores wrapper objects in lists, sets, and maps.
