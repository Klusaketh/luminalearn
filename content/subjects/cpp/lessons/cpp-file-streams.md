---
lesson: cpp-file-streams
title: Modern File Streams
summary: Reading and writing files with C++ file streams: RAII opening and closing, checking stream state, formatted and line-based text I/O, string streams for parsing, and binary I/O with read and write.
minutes: 30
type: theory
objectives:
  - Open files with ifstream, ofstream, and fstream, check for failure, and rely on RAII to close them
  - Read text by lines and by formatted extraction, and parse fields with stringstreams
  - Write and read binary data with write and read, and explain stream state flags and portability limits
review: ai-draft
---
## Introduction

C++ file streams use the same `<<` and `>>` operators as `std::cout` and `std::cin`, so everything you know about console I/O carries over to files. Because the stream classes follow RAII, a file is closed automatically when its stream object goes out of scope, even if an exception is thrown. This lesson covers opening files safely, reading text in the ways real programs need, parsing with string streams, and binary I/O.

**Before you start:** you should know iostream basics, `std::string`, `std::vector`, and RAII.

## Core theory

### The stream classes

From `<fstream>`: `std::ifstream` reads, `std::ofstream` writes, and `std::fstream` does both. Construct a stream with a file name to open it:

```cpp
std::ofstream out("scores.txt");               // truncates or creates
std::ofstream log("app.log", std::ios::app);   // appends
std::ifstream in("scores.txt");
if (!in) { /* could not open */ }
```

Open modes combine with `|`: `std::ios::in`, `out`, `app` (append), `trunc` (truncate), and `binary`. A stream converts to `false` when it is in a failed state, so `if (!in)` checks whether opening succeeded. The destructor closes the file; call `close()` only if you need to close it early.

### Stream state

Each stream has state flags: `good()` (all fine), `eof()` (end of input reached), `fail()` (an operation failed, such as a format error or end of input), and `bad()` (a serious I/O error). After a failure, the stream ignores further operations until you call `clear()`. As with C, do not loop on `eof()`; loop on the read operation itself, which returns the stream and converts to `false` when it fails:

```cpp
while (std::getline(in, line)) { ... }
while (in >> name >> marks) { ... }
```

### Text reading strategies

- `in >> x` skips whitespace and reads one value, converting it to `x`'s type.
- `std::getline(in, line)` reads a whole line, including spaces, without the newline.
- For structured lines, read the line with `getline` and then parse it with a `std::istringstream`, which treats a string as an input stream. `std::getline(ss, field, ',')` splits on a delimiter, which is the standard way to parse simple CSV.

`std::ostringstream` builds strings with `<<` and returns them with `str()`; `<iomanip>` manipulators such as `std::setw`, `std::setprecision`, `std::fixed`, and `std::left` format output.

### Binary I/O

Open with `std::ios::binary` and use `out.write(reinterpret_cast<const char*>(&value), sizeof value)` and `in.read(reinterpret_cast<char*>(&value), sizeof value)`. `in.gcount()` reports how many bytes the last read obtained. As in C, raw binary dumps of structures depend on padding, type sizes, and byte order, so they are fast for files your own program reads back but are not a portable exchange format. Write only trivially copyable types this way, never objects containing pointers such as `std::string`.

## Worked examples

### Example 1: Writing, appending, and parsing a CSV file

```cpp
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

int main() {
    {
        std::ofstream out("marks.csv");
        out << "name,maths,physics\n" << "Asha,91,84\n" << "Ravi,78,69\n";
    }
    {
        std::ofstream more("marks.csv", std::ios::app);
        more << "Meena,85,92\n";
    }

    std::ifstream in("marks.csv");
    if (!in) { std::cerr << "cannot open\n"; return 1; }
    std::string line;
    std::getline(in, line);
    std::cout << std::left << std::setw(8) << "Name" << "Average\n";
    while (std::getline(in, line)) {
        std::istringstream fields(line);
        std::string name, a, b;
        std::getline(fields, name, ',');
        std::getline(fields, a, ',');
        std::getline(fields, b, ',');
        double avg = (std::stoi(a) + std::stoi(b)) / 2.0;
        std::cout << std::setw(8) << name << std::fixed << std::setprecision(1) << avg << '\n';
    }
    std::ifstream missing("nope.csv");
    std::cout << "missing file opened? " << std::boolalpha << static_cast<bool>(missing) << '\n';
    return 0;
}
```

Output:

```text
Name    Average
Asha    87.5
Ravi    73.5
Meena   88.5
missing file opened? false
```

Each output stream is created in its own block, so the file is closed (and flushed) at the closing brace before it is reopened. The header line is read once and skipped; then each line is split on commas with a string stream.

### Example 2: Formatted extraction with error recovery, and binary data

```cpp
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main() {
    std::istringstream data("10 20 abc 30 40");
    std::vector<int> values;
    int x;
    while (true) {
        if (data >> x) {
            values.push_back(x);
        } else if (data.eof()) {
            break;
        } else {
            data.clear();
            std::string junk;
            data >> junk;
            std::cout << "skipped '" << junk << "'\n";
        }
    }
    std::cout << "read " << values.size() << " numbers\n";

    {
        std::ofstream bin("values.bin", std::ios::binary);
        for (int v : values) bin.write(reinterpret_cast<const char*>(&v), sizeof v);
    }
    std::ifstream bin("values.bin", std::ios::binary);
    int v, sum = 0, count = 0;
    while (bin.read(reinterpret_cast<char*>(&v), sizeof v)) {
        sum += v;
        ++count;
    }
    std::cout << count << " ints from binary file, sum " << sum << '\n';
    return 0;
}
```

Output:

```text
skipped 'abc'
read 4 numbers
4 ints from binary file, sum 100
```

When `>>` meets `abc`, the stream enters the fail state; `clear()` resets it so the bad token can be read as a string and skipped. The binary loop stops when `read` cannot obtain a full `int`, which happens at the end of the 16-byte file.

## Applications

- **Data import:** CSV and log files are parsed line by line with `getline` and string streams.
- **Reports:** `<iomanip>` aligns columns in text output.
- **Caching:** binary files store numeric arrays compactly for the same program.
- **Testing:** string streams stand in for files, making I/O code easy to test.

## Common mistakes

- **Not checking whether the file opened.** All later reads silently fail.
- **Looping on `eof()`.** Loop on the read operation itself.
- **Mixing `>>` and `getline`.** `>>` leaves the newline behind; use `std::ws` or read whole lines.
- **Forgetting `std::ios::binary`.** On Windows, text mode translates newline bytes and corrupts binary data.
- **Writing `std::string` or pointers in binary.** Only the pointer value is written, not the text.

## Revision notes

- `ifstream` reads, `ofstream` writes, `fstream` both; the destructor closes the file.
- `if (!stream)` detects failure to open or a failed operation.
- Loop with `while (std::getline(in, line))` or `while (in >> a >> b)`.
- `istringstream` parses a string; `getline(ss, field, ',')` splits on a delimiter.
- `clear()` resets a failed stream; flags: `good`, `eof`, `fail`, `bad`.
- Binary: `std::ios::binary`, `write`, `read`, `gcount`; not portable across platforms.

## Practice questions

:::question basic
How do you open a file for appending with an `ofstream`?
:::answer
Pass the append mode: `std::ofstream log("app.log", std::ios::app);`. New output is added at the end of the file instead of truncating it.
:::

:::question basic
Why is it unnecessary to call `close()` on a stream that goes out of scope?
:::answer
File streams follow RAII: the destructor flushes the buffer and closes the file automatically when the object is destroyed, including when an exception causes the scope to exit.
:::

:::question intermediate
What happens if `in >> number` meets the text "abc", and how can a program continue reading?
:::answer
The extraction fails and the stream enters the fail state, after which all further reads do nothing. Call `in.clear()` to reset the state, then remove the bad input, for example by reading it into a string or with `in.ignore(...)`, and continue.
:::

:::question intermediate
Write the loop that reads a file of "name marks" pairs until the input ends.
:::answer
`std::string name; int marks; while (in >> name >> marks) { /* use name and marks */ }`. The extraction expression returns the stream, which converts to `false` as soon as a read fails, including at end of input.
:::

:::question advanced
Why does writing a `std::vector<std::string>` to a file with `out.write(reinterpret_cast<const char*>(&vec), sizeof vec)` not save the strings?
:::answer
`sizeof vec` is just the size of the vector object, which holds pointers to heap memory and a size, not the elements themselves. Writing it saves those pointer values, which are meaningless in another run. Strings must be serialised explicitly, for example by writing each string's length followed by its characters, or by using a text format.
:::

## Further learning

- **Next:** *Generic Programming with Templates* lets you write one serialisation function for many types.
- **Related:** *Binary & Text File Streams* in C Programming shows the same ideas with `FILE *`.
