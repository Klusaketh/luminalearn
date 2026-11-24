---
lesson: c-null-terminated-strings
title: Null-Terminated String Manipulation
summary: How C represents strings as character arrays ending in a null byte, the standard string functions (strlen, strcpy, strcat, strcmp), and how to avoid buffer overflows with bounded alternatives.
minutes: 30
type: theory
objectives:
  - Explain the null terminator and the difference between a character array and a string literal
  - Use strlen, strcpy, strncpy, strcat, strcmp, and snprintf correctly and predict their results
  - Identify buffer overflow risks and write string code that always respects buffer sizes
review: ai-draft
---
## Introduction

C has no built-in string type. A string is simply an array of `char` whose end is marked by a **null character**, `'\0'`. Every string function in the standard library depends on finding that terminator. This design is fast and simple, but it puts the burden of memory safety on the programmer: a missing terminator or an oversized copy can overwrite neighbouring memory, a bug that has caused many real security breaches.

**Before you start:** you should know arrays, pointers at a basic level, loops, and functions.

## Core theory

### The null terminator

`char word[6] = "hello";` stores six bytes: `'h' 'e' 'l' 'l' 'o' '\0'`. The terminator is part of the storage but not of the length, so `strlen(word)` is 5 while `sizeof word` is 6. Any buffer that holds a string of length $n$ needs at least $n + 1$ bytes.

A **string literal** such as `"hello"` is stored in read-only memory. `char *p = "hello";` points at it, and modifying it (`p[0] = 'H'`) is undefined behaviour. `char s[] = "hello";` instead creates a modifiable array initialised with a copy. Use `const char *` for pointers to literals.

### Standard functions in string.h

| Function | Effect |
| :--- | :--- |
| `strlen(s)` | number of characters before `'\0'` ($O(n)$: it walks the string) |
| `strcpy(dst, src)` | copies `src` including `'\0'`; `dst` must be large enough |
| `strcat(dst, src)` | appends `src` to the end of `dst` |
| `strcmp(a, b)` | negative, zero, or positive as `a` sorts before, equal to, or after `b` |
| `strchr(s, c)`, `strstr(s, t)` | pointer to the first match, or `NULL` |

Strings must be compared with `strcmp`, not `==`: `a == b` compares addresses.

### Bounded functions and overflow prevention

`strcpy` and `strcat` do not know the destination's size, so a long source overflows the buffer. Safer patterns:

- `snprintf(dst, size, "%s", src)` writes at most `size - 1` characters plus `'\0'`, always terminates, and returns the length it **wanted** to write, so a return value of `size` or more means the text was truncated.
- `strncpy(dst, src, n)` copies at most `n` characters but does **not** add `'\0'` if `src` is too long, so you must terminate manually: `dst[n - 1] = '\0'`.
- For input, `fgets(buf, sizeof buf, stdin)` reads at most `sizeof buf - 1` characters; never use the removed `gets`, which cannot be used safely.

### Character tests

`<ctype.h>` provides `isalpha`, `isdigit`, `isspace`, `toupper`, and `tolower`. Pass them an `unsigned char` value (cast `char` arguments) to avoid undefined behaviour with negative `char` values.

## Worked examples

### Example 1: Lengths, copying, comparison, and searching

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char word[6] = "hello";
    printf("strlen=%zu sizeof=%zu\n", strlen(word), sizeof word);
    char copy[20];
    strcpy(copy, word);
    strcat(copy, ", world");
    printf("%s (%zu)\n", copy, strlen(copy));
    printf("%d %d %d\n", strcmp("apple", "apricot") < 0, strcmp("b", "a") > 0, strcmp(word, "hello") == 0);
    char *comma = strchr(copy, ',');
    printf("comma at index %td, rest '%s'\n", comma - copy, comma + 2);
    printf("%s\n", strstr(copy, "wor"));
    return 0;
}
```

Output:

```text
strlen=5 sizeof=6
hello, world (12)
1 1 1
comma at index 5, rest 'world'
world
```

`"apple"` sorts before `"apricot"` because at the first difference, `'p' < 'r'`. `strchr` returns a pointer into `copy`, and subtracting the base gives the index.

### Example 2: Bounded copying with snprintf, and a manual strlen

```c
#include <stdio.h>
#include <string.h>

size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p != '\0') p++;
    return (size_t)(p - s);
}

int main(void) {
    char small[8];
    int needed = snprintf(small, sizeof small, "%s", "university");
    printf("'%s' needed=%d truncated=%s\n", small, needed, needed >= (int)sizeof small ? "yes" : "no");

    char buf[5];
    strncpy(buf, "overflow", sizeof buf - 1);
    buf[sizeof buf - 1] = '\0';
    printf("'%s'\n", buf);

    printf("%zu %zu\n", my_strlen("C strings"), my_strlen(""));
    return 0;
}
```

Output:

```text
'univers' needed=10 truncated=yes
'over'
9 0
```

`snprintf` stores 7 characters and the terminator in the 8-byte buffer and reports that 10 were needed. `strncpy` copies 4 characters, and the explicit terminator makes the result a valid string. `my_strlen` shows why `strlen` costs $O(n)$.

## Applications

- **Parsing:** command-line arguments, configuration lines, and protocol messages arrive as C strings.
- **Systems programming:** file paths and environment variables are null-terminated strings.
- **Security:** bounded copies prevent buffer-overflow exploits in network-facing code.
- **Embedded displays:** fixed buffers with `snprintf` format readings for small screens.

## Common mistakes

- **Forgetting space for `'\0'`.** A 5-letter word needs a 6-byte buffer.
- **Comparing with `==`.** Use `strcmp`; `==` compares addresses.
- **Modifying a string literal.** Copy it into an array first.
- **Trusting `strncpy` to terminate.** Terminate the buffer yourself, or use `snprintf`.
- **Calling `strlen` in a loop condition.** `for (i = 0; i < strlen(s); i++)` is $O(n^2)$; compute the length once.

## Revision notes

- A string is a `char` array ending with `'\0'`; storage needs length + 1 bytes.
- `strlen` excludes the terminator and is $O(n)$.
- `strcmp` returns <0, 0, >0; never compare strings with `==`.
- String literals are read-only; use `const char *`.
- Prefer `snprintf` and `fgets`; `strncpy` may leave the string unterminated.
- Cast to `unsigned char` before calling `ctype.h` functions.

## Practice questions

:::question basic
How many bytes does `char s[] = "code";` occupy, and what is `strlen(s)`?
:::answer
It occupies 5 bytes: four letters plus the null terminator. `strlen(s)` is 4, because the terminator is not counted.
:::

:::question basic
Why does `if (name == "admin")` not compare the contents of two strings?
:::answer
Both operands decay to pointers, so `==` compares addresses, not characters. Use `strcmp(name, "admin") == 0` to compare the contents.
:::

:::question intermediate
What does `strcmp("Zebra", "apple")` return in sign, and why might that surprise people?
:::answer
It returns a negative value: in ASCII, uppercase letters (65 to 90) come before lowercase letters (97 to 122), so `'Z'` (90) is less than `'a'` (97). Comparing case-insensitively requires converting both strings, for example with `tolower`.
:::

:::question intermediate
A program does `char buf[10]; strcpy(buf, user_input);`. Describe the risk and a safe replacement.
:::answer
If the input is 10 or more characters, `strcpy` writes past the end of `buf`, overwriting neighbouring memory such as other variables or the return address, which can crash the program or be exploited. Use `snprintf(buf, sizeof buf, "%s", user_input);`, which never writes more than `sizeof buf` bytes and always terminates the string, and check its return value for truncation.
:::

:::question advanced
Why is `for (size_t i = 0; i < strlen(s); i++) { ... }` slow for long strings, and how do you fix it?
:::answer
`strlen` scans the whole string each time it is called, and the condition is evaluated on every iteration, so the loop performs about $n$ scans of $n$ characters: $O(n^2)$ work. Compute the length once before the loop, `size_t n = strlen(s);`, or loop until `s[i] != '\0'`, which makes the loop $O(n)$.
:::

## Further learning

- **Next:** *Pointers & Address Arithmetic* explains the pointer operations string functions use internally.
- **Related:** *Undefined Behavior & Common Bugs* covers buffer overflows and the sanitizers that detect them.
