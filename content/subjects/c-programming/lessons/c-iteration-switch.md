---
lesson: c-iteration-switch
title: Iteration & Switch Statements
summary: C's while, do-while, and for loops, loop control with break and continue, and the switch statement with its case labels, default, and deliberate or accidental fall-through.
minutes: 30
type: theory
objectives:
  - Choose between while, do-while, and for loops and trace their execution precisely
  - Use break and continue correctly, including in nested loops
  - Write switch statements with break and default, and explain fall-through
review: ai-draft
---
## Introduction

Repetition and multi-way decisions are the backbone of every program: reading input until it ends, processing each element of an array, or choosing an action from a menu. C offers three loops and a `switch` statement. They look simple, but small details, such as a missing `break` in a `switch` or an off-by-one loop bound, cause some of the most common bugs in C.

**Before you start:** you should know C variables, expressions, and `if` / `else`.

## Core theory

### while and do-while

`while (condition) { body }` checks the condition **before** each pass, so the body may run zero times. `do { body } while (condition);` checks **after** each pass, so the body always runs at least once; it suits "ask, then check" tasks such as menus and input validation. Note the semicolon after the `do-while` condition.

### for

```c
for (init; condition; update) { body }
```

is equivalent to `init; while (condition) { body; update; }`. Since C99, the loop variable can be declared in `init` (`for (int i = 0; i < n; i++)`), limiting its scope to the loop. Any of the three parts may be empty; `for (;;)` loops forever until a `break`. The idiom `for (int i = 0; i < n; i++)` visits indices 0 to $n - 1$ and runs exactly $n$ times.

### break and continue

`break` leaves the innermost enclosing loop (or `switch`) immediately. `continue` skips the rest of the current pass and goes to the next one; in a `for` loop, the update expression still runs. In nested loops, both affect only the innermost loop; to leave several loops, use a flag variable, put the loops in a function and `return`, or, sparingly, a `goto`.

### switch

```c
switch (expression) {
    case 1:
        ...
        break;
    case 2:
    case 3:
        ...
        break;
    default:
        ...
}
```

The expression must have an integer type (including `char` and enumerations), and each `case` label must be an integer **constant**. Control jumps to the matching label and runs from there **until a `break` or the end of the switch**. Without `break`, execution **falls through** into the next case. Fall-through is useful for grouping labels (`case 2: case 3:`), but an accidental missing `break` is a classic bug; when you intend it, add a comment such as `/* fall through */`. `default` runs when no label matches; it may appear anywhere but usually comes last.

## Worked examples

### Example 1: Tracing loops with break and continue

```c
#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 10; i++) {
        if (i % 3 == 0) continue;
        if (i > 8) break;
        printf("%d ", i);
    }
    printf("\n");

    int n = 0;
    while (n < 0) {
        n++;
    }
    int m = 0;
    do {
        m++;
    } while (m < 0);
    printf("while ran %d times, do-while ran %d time\n", n, m);

    for (int r = 1; r <= 3; r++) {
        for (int c = 1; c <= 3; c++) {
            if (c > r) break;
            printf("%d", r * c);
        }
        printf("\n");
    }
    return 0;
}
```

Output:

```text
1 2 4 5 7 8
while ran 0 times, do-while ran 1 time
1
24
369
```

Multiples of 3 are skipped by `continue`; the loop stops at 10 because `break` triggers when `i` exceeds 8 (9 was already skipped). The inner `break` leaves only the inner loop, producing a triangle.

### Example 2: switch with grouping, default, and fall-through

```c
#include <stdio.h>

const char *kind(char c) {
    switch (c) {
        case 'a': case 'e': case 'i': case 'o': case 'u':
            return "vowel";
        case ' ':
            return "space";
        default:
            return "other";
    }
}

int main(void) {
    const char *word = "hi you";
    for (int i = 0; word[i] != '\0'; i++) {
        printf("%c:%s ", word[i], kind(word[i]));
    }
    printf("\n");

    int level = 2, points = 0;
    switch (level) {
        case 3:
            points += 30;
            /* fall through */
        case 2:
            points += 20;
            /* fall through */
        case 1:
            points += 10;
            break;
        default:
            points = -1;
    }
    printf("points = %d\n", points);
    return 0;
}
```

Output:

```text
h:other i:vowel  :space y:other o:vowel u:vowel
points = 30
```

In `kind`, each `return` leaves the function, so no `break` is needed. In the second switch, entering at `case 2` falls through into `case 1`, adding 20 and then 10.

## Applications

- **Menus and command interpreters:** `do-while` repeats until the user quits; `switch` dispatches commands.
- **State machines:** a `switch` on the current state drives parsers, protocol handlers, and game logic.
- **Array processing:** `for` loops traverse buffers, matrices, and strings.
- **Searching:** `break` stops as soon as the item is found.

## Common mistakes

- **Missing `break` in a switch.** Execution runs into the next case unintentionally.
- **Off-by-one bounds.** `i <= n` with an array of `n` elements reads past the end.
- **A stray semicolon.** `for (i = 0; i < n; i++);` has an empty body, and the block below runs once.
- **Using `=` in a condition.** `while (x = 0)` assigns and is always false; compile with warnings on.

## Revision notes

- `while` tests first (0 or more passes); `do-while` tests last (1 or more passes).
- `for (init; cond; update)` equals `init; while (cond) { body; update; }`.
- `break` exits the innermost loop or switch; `continue` jumps to the next pass (the update still runs).
- `switch` works on integer types with constant `case` labels.
- Without `break`, cases fall through; comment deliberate fall-through.
- `default` handles every unmatched value.

## Practice questions

:::question basic
How many times does the body of `for (int i = 5; i < 5; i++)` run, and how many times does `do { } while (0);` run?
:::answer
The `for` body runs 0 times because the condition is false at the start. The `do-while` body runs exactly once, because its condition is checked only after the first pass.
:::

:::question basic
What does `continue` do inside a `for` loop?
:::answer
It skips the remaining statements of the current pass and jumps to the update expression, then the condition is tested for the next pass. It does not leave the loop.
:::

:::question intermediate
What is printed by: `int x = 1; switch (x) { case 1: printf("A"); case 2: printf("B"); break; case 3: printf("C"); }`?
:::answer
It prints `AB`. Control enters at `case 1`, prints A, and because there is no `break`, falls through to `case 2`, prints B, and then the `break` leaves the switch.
:::

:::question intermediate
Rewrite `for (int i = 0; i < n; i++) sum += a[i];` as a `while` loop.
:::answer
`int i = 0; while (i < n) { sum += a[i]; i++; }`. The initialisation moves before the loop, and the update moves to the end of the body, exactly matching the `for` loop's behaviour.
:::

:::question advanced
You must search a 2-D grid and stop completely when a target is found. Give two clean ways to leave both loops.
:::answer
Put the search in a function and `return` from inside the inner loop as soon as the target is found; this is usually the clearest. Alternatively use a `found` flag: set it before `break` in the inner loop and test it in the outer loop's condition (or after the inner loop with another `break`). A `goto` to a label after both loops also works and is accepted for this specific pattern.
:::

## Further learning

- **Next:** *Function Prototypes & Call Stack* explains what happens when loops call functions.
- **Related:** *Array Memory Layout & Indexing* uses `for` loops to traverse arrays safely.
