---
lesson: c-file-streams
title: Binary & Text File Streams
summary: Reading and writing files with C's buffered stream functions: fopen modes, formatted and line-based text I/O, binary fread and fwrite, detecting end-of-file correctly, and checking for errors.
minutes: 35
type: theory
objectives:
  - Open, read, write, and close text and binary files with fopen, fprintf, fgets, fread, fwrite, and fclose
  - Detect end-of-file and errors correctly using the return values of I/O functions rather than feof alone
  - Explain stream buffering and the portability limits of writing raw structures in binary
review: ai-draft
---
## Introduction

Programs need to keep data after they exit and to read data prepared elsewhere. C does this through **streams**: a `FILE *` returned by `fopen` represents an open file with a buffer in memory, and the standard library moves data between the buffer and the disk. The same functions handle the keyboard (`stdin`) and the screen (`stdout`). This lesson covers text and binary files and, just as important, how to detect the end of a file and errors correctly.

**Before you start:** you should know strings, structures, pointers, and `printf`.

## Core theory

### Opening and closing

`FILE *f = fopen("data.txt", "r");` opens a file and returns `NULL` on failure, for example when the file does not exist; `perror("data.txt")` prints the reason. Modes mirror those of other languages:

| Mode | Meaning |
| :--- | :--- |
| `"r"` | read; file must exist |
| `"w"` | write; create or truncate |
| `"a"` | append to the end |
| `"r+"`, `"w+"`, `"a+"` | read and write variants |
| add `b` (`"rb"`, `"wb"`) | binary: no newline translation on Windows |

`fclose(f)` flushes any buffered output and releases the file; it returns `EOF` if the flush fails.

### Text I/O

- `fprintf(f, ...)` and `fscanf(f, ...)` are the file versions of `printf` and `scanf`. `fscanf` returns the number of items successfully converted, or `EOF`.
- `fgets(buf, size, f)` reads one line, including its `'\n'`, up to `size - 1` characters, and returns `NULL` at end of file or on error. It is the safe way to read lines.
- `fputs(s, f)` writes a string; `fgetc` and `fputc` work one character at a time. `fgetc` returns an `int` so it can return `EOF` (a negative value) as well as every possible byte.

### Binary I/O

`fwrite(ptr, size, count, f)` writes `count` items of `size` bytes from memory exactly as they are, and `fread(ptr, size, count, f)` reads them back; both return the number of **complete items** transferred. Binary files are compact and fast to load, but a raw structure includes padding and uses the machine's byte order, so such files are portable only between programs built the same way on the same kind of machine.

### End-of-file done right

`feof(f)` becomes true only **after** a read has already failed because the end was reached. The common loop `while (!feof(f)) { fgets(...); ... }` therefore processes the last line twice or processes garbage. Loop on the read function's return value instead:

```c
while (fgets(line, sizeof line, f) != NULL) { ... }
```

After the loop, `ferror(f)` tells you whether the loop stopped because of an error rather than the end of the file.

### Buffering

Streams are buffered: output collects in memory and is written in large blocks, which is much faster than one system call per character. `stdout` is usually line-buffered on a terminal; `fflush(f)` forces the buffer out, and `fclose` flushes automatically. If a program crashes, unflushed output is lost.

## Worked examples

### Example 1: Writing and reading a text file

```c
#include <stdio.h>

int main(void) {
    FILE *out = fopen("scores.txt", "w");
    if (out == NULL) { perror("scores.txt"); return 1; }
    fprintf(out, "Asha 91\nRavi 78\nMeena 85\n");
    fclose(out);

    FILE *in = fopen("scores.txt", "r");
    if (in == NULL) { perror("scores.txt"); return 1; }
    char name[32];
    int mark, count = 0, total = 0;
    while (fscanf(in, "%31s %d", name, &mark) == 2) {
        printf("%-6s %d\n", name, mark);
        total += mark;
        count++;
    }
    if (ferror(in)) printf("read error\n");
    fclose(in);
    printf("average %.1f over %d students\n", (double)total / count, count);

    FILE *missing = fopen("no_such_file.txt", "r");
    printf("missing file: %s\n", missing == NULL ? "fopen returned NULL" : "opened");
    return 0;
}
```

Output:

```text
Asha   91
Ravi   78
Meena  85
average 84.7 over 3 students
missing file: fopen returned NULL
```

The loop stops when `fscanf` can no longer convert two items, which happens exactly at the end of the data. `%31s` limits the name to the buffer size.

### Example 2: Binary records with fwrite and fread

```c
#include <stdio.h>

typedef struct {
    int id;
    double balance;
} Account;

int main(void) {
    Account out[3] = {{1, 250.0}, {2, 1200.5}, {3, 75.25}};
    FILE *f = fopen("accounts.bin", "wb");
    if (!f) return 1;
    size_t written = fwrite(out, sizeof out[0], 3, f);
    fclose(f);
    printf("wrote %zu records\n", written);

    f = fopen("accounts.bin", "rb");
    if (!f) return 1;
    Account a;
    double sum = 0;
    while (fread(&a, sizeof a, 1, f) == 1) {
        printf("id %d: %.2f\n", a.id, a.balance);
        sum += a.balance;
    }
    printf("total %.2f, stopped at %s\n", sum, feof(f) ? "end of file" : "error");
    fclose(f);
    return 0;
}
```

Output:

```text
wrote 3 records
id 1: 250.00
id 2: 1200.50
id 3: 75.25
total 1525.75, stopped at end of file
```

`fread` returns 1 for each complete record and 0 when no full record remains. Only then is `feof` used, to explain why reading stopped.

## Applications

- **Configuration and logs:** text files are human-readable and easy to inspect.
- **Game saves and caches:** binary files load quickly.
- **Data pipelines:** programs read standard input and write standard output, so they can be chained in a shell.
- **Embedded logging:** buffered writes reduce wear on flash storage.

## Common mistakes

- **Not checking `fopen` for `NULL`.** Using a `NULL` stream crashes the program.
- **`while (!feof(f))` loops.** They run once too often; test the read function's result.
- **Storing `fgetc`'s result in a `char`.** `EOF` cannot be told apart from a real byte; use `int`.
- **Forgetting `fclose`.** Buffered data may never reach the disk.
- **Treating raw binary structures as a portable format.** Padding and byte order differ between systems.

## Revision notes

- `fopen` returns `NULL` on failure; `perror` explains why.
- Text: `fprintf`, `fscanf` (returns items converted), `fgets` (returns `NULL` at end), `fputs`.
- Binary: `fwrite` / `fread` return complete items transferred; use `"rb"` / `"wb"`.
- Loop on the read function's return value; use `feof` / `ferror` afterwards.
- Streams are buffered; `fflush` and `fclose` write the buffer out.
- `fgetc` returns `int` so `EOF` is distinguishable.

## Practice questions

:::question basic
What does `fopen` return if the file cannot be opened, and how do you report the reason?
:::answer
It returns `NULL`. Calling `perror("filename")` prints a message describing the error stored in `errno`, such as "No such file or directory".
:::

:::question basic
Why should the result of `fgetc` be stored in an `int` rather than a `char`?
:::answer
`fgetc` returns every possible byte value (0 to 255) as well as `EOF`, a negative value. A `char` cannot hold all 257 distinct results, so `EOF` could be confused with a real byte or never detected.
:::

:::question intermediate
What is wrong with `while (!feof(f)) { fgets(line, 100, f); printf("%s", line); }`?
:::answer
`feof` becomes true only after a read fails at the end of the file. After the last line is read, `feof` is still false, so the loop runs once more: `fgets` fails, `line` keeps the previous contents, and the last line is printed twice. Loop on `fgets(...) != NULL` instead.
:::

:::question intermediate
`fread(buf, 8, 10, f)` returns 6. What does that mean?
:::answer
Only 6 complete items of 8 bytes were read, fewer than the 10 requested. Either the end of the file was reached or an error occurred; check `feof(f)` and `ferror(f)` to tell which.
:::

:::question advanced
A program writes `struct { char tag; int value; }` records with `fwrite` on one machine and reads them with `fread` on a different system, getting garbage. Give two possible causes and a robust fix.
:::answer
The two systems may lay out the structure differently, with different padding after `tag`, so field offsets do not match. They may also use different byte orders, so the four bytes of `value` are interpreted in reverse. A robust format writes each field separately with a fixed size and byte order, for example `tag` as one byte and `value` as four bytes in big-endian order assembled with shifts, or uses a text format.
:::

## Further learning

- **Next:** *Preprocessor, Macros & Multi-File Programs* covers structuring larger programs that do I/O.
- **Related:** *File I/O & Context Managers* in Python shows the same ideas with automatic clean-up.
