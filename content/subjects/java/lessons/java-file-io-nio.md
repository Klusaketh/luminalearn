---
lesson: java-file-io-nio
title: File I/O with java.nio
summary: Working with files using java.nio.file: Path objects, the Files utility class for reading and writing, buffered readers and writers, directory listing, character encodings, and safe clean-up with try-with-resources.
minutes: 40
type: theory
objectives:
  - Build and manipulate paths with Path and Paths, and check, create, copy, move, and delete files with Files
  - Read and write text files with Files.readAllLines, Files.writeString, BufferedReader, and BufferedWriter using explicit encodings
  - Process large files line by line and list directories safely with try-with-resources
review: ai-draft
---
## Introduction

Every real application reads configuration, imports data, or writes logs. Java's modern file API, **NIO.2** in the package `java.nio.file` (Java 7 and later), replaces the old `java.io.File` class with clearer, safer tools: `Path` represents a location, and the static methods of `Files` do the work. Combined with try-with-resources, they let you handle files in a few lines while closing everything correctly, even when errors occur.

**Before you start:** you should know exceptions, try-with-resources, strings, and collections.

## Core theory

### Paths

A `Path` represents a file-system location, which need not exist:

```java
Path dir = Paths.get("data");            // or Path.of("data") in Java 11+
Path file = dir.resolve("scores.csv");   // data/scores.csv
```

Useful methods: `getFileName()`, `getParent()`, `resolve(other)` (join paths), `toAbsolutePath()`, `normalize()` (removes `.` and `..`), and `relativize`. Paths use the platform's separator automatically, so code written on Windows works on Linux.

### The Files class

| Task | Method |
| :--- | :--- |
| Check | `Files.exists(p)`, `Files.isDirectory(p)`, `Files.size(p)` |
| Create | `Files.createDirectories(dir)`, `Files.createFile(p)` |
| Small text files | `Files.readAllLines(p)`, `Files.readString(p)` (11+), `Files.write(p, lines)`, `Files.writeString(p, text)` (11+) |
| Large text files | `Files.newBufferedReader(p)`, `Files.newBufferedWriter(p)`, `Files.lines(p)` |
| Bytes | `Files.readAllBytes(p)`, `Files.write(p, bytes)` |
| Copy, move, delete | `Files.copy(a, b, REPLACE_EXISTING)`, `Files.move`, `Files.delete`, `Files.deleteIfExists` |
| Directories | `Files.list(dir)`, `Files.walk(dir)`, `Files.newDirectoryStream(dir, "*.csv")` |

Writing methods take **open options**: by default they create the file or truncate it; `StandardOpenOption.APPEND` appends instead. Almost every method throws the checked `IOException` (or a subclass such as `NoSuchFileException`), which you must handle or declare.

### Encodings

Text is stored as bytes in some **character encoding**. NIO methods default to UTF-8 (`readAllLines`, `newBufferedReader`, `writeString`), but it is good practice to pass `StandardCharsets.UTF_8` explicitly so behaviour never depends on the machine's default.

### Buffered and streaming I/O

`readAllLines` loads the whole file into memory, which is fine for small files but not for a multi-gigabyte log. For large files, read line by line with a `BufferedReader` (`readLine()` returns `null` at the end) or with `Files.lines(p)`, which returns a lazy `Stream<String>`. A buffered writer collects output in memory and writes it in large blocks; its `close()` (via try-with-resources) flushes the remaining data. Streams returned by `Files.lines`, `Files.list`, and `Files.walk` hold open file handles, so they must also be closed with try-with-resources.

## Worked examples

### Example 1: Writing, appending, reading, and summarising a CSV

```java
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.List;

public class Main {
    public static void main(String[] args) throws IOException {
        Path dir = Paths.get("reports");
        Files.createDirectories(dir);
        Path csv = dir.resolve("marks.csv");

        Files.write(csv, List.of("name,marks", "Asha,91", "Ravi,78"), StandardCharsets.UTF_8);
        try (BufferedWriter w = Files.newBufferedWriter(csv, StandardCharsets.UTF_8, StandardOpenOption.APPEND)) {
            w.write("Meena,85");
            w.newLine();
        }

        int total = 0, count = 0;
        String best = null;
        int bestMarks = -1;
        try (BufferedReader r = Files.newBufferedReader(csv, StandardCharsets.UTF_8)) {
            String line = r.readLine();
            while ((line = r.readLine()) != null) {
                String[] parts = line.split(",");
                int m = Integer.parseInt(parts[1]);
                total += m;
                count++;
                if (m > bestMarks) { bestMarks = m; best = parts[0]; }
            }
        }
        System.out.println(csv.getFileName() + " in " + csv.getParent() + ": " + Files.readAllLines(csv).size() + " lines");
        System.out.printf("average %.1f, best %s (%d)%n", (double) total / count, best, bestMarks);
        System.out.println("exists: " + Files.exists(csv) + ", missing.txt exists: " + Files.exists(dir.resolve("missing.txt")));
    }
}
```

Output:

```text
marks.csv in reports: 4 lines
average 84.7, best Asha (91)
exists: true, missing.txt exists: false
```

`Files.write` creates the file with three lines, and the buffered writer in append mode adds a fourth. The reader skips the header with the first `readLine()` and then processes each record until `readLine()` returns `null`.

### Example 2: Streams of lines, directory listing, and error handling

```java
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Main {
    public static void main(String[] args) throws IOException {
        Path logs = Files.createDirectories(Paths.get("logs"));
        Files.write(logs.resolve("app.log"), List.of("INFO start", "ERROR disk full", "INFO retry", "ERROR timeout"), StandardCharsets.UTF_8);
        Files.write(logs.resolve("notes.txt"), List.of("not a log"), StandardCharsets.UTF_8);
        Files.copy(logs.resolve("app.log"), logs.resolve("app-backup.log"), StandardCopyOption.REPLACE_EXISTING);

        try (Stream<String> lines = Files.lines(logs.resolve("app.log"), StandardCharsets.UTF_8)) {
            List<String> errors = lines.filter(l -> l.startsWith("ERROR")).map(l -> l.substring(6)).collect(Collectors.toList());
            System.out.println("errors: " + errors);
        }

        try (Stream<Path> entries = Files.list(logs)) {
            List<String> logFiles = entries.map(p -> p.getFileName().toString())
                .filter(name -> name.endsWith(".log")).sorted().collect(Collectors.toList());
            System.out.println("log files: " + logFiles);
        }

        try {
            Files.readAllLines(logs.resolve("archive.log"));
        } catch (NoSuchFileException e) {
            System.out.println("no such file: " + Paths.get(e.getFile()).getFileName());
        }
        System.out.println(Paths.get("a/b/../c/./d.txt").normalize());
    }
}
```

Output:

```text
errors: [disk full, timeout]
log files: [app-backup.log, app.log]
no such file: archive.log
a/c/d.txt
```

`Files.lines` streams the file lazily, and try-with-resources closes the underlying file handle. `Files.list` returns directory entries in no guaranteed order, so the names are sorted before printing. A missing file raises `NoSuchFileException`, a subclass of `IOException`. (On Windows the last line would use backslashes.)

## Applications

- **Configuration loading:** read small settings files with `readAllLines` or `readString`.
- **Log analysis:** stream huge logs line by line with `Files.lines`.
- **Data import and export:** CSV processing with buffered readers and writers.
- **File management tools:** copying, moving, and cleaning directories with `Files`.

## Common mistakes

- **Reading huge files with `readAllLines`.** Stream them instead.
- **Forgetting to close streams from `Files.lines`, `list`, or `walk`.** Use try-with-resources.
- **Relying on the platform's default encoding.** Pass `StandardCharsets.UTF_8`.
- **Overwriting by accident.** Write methods truncate by default; use `APPEND` when needed.
- **Hard-coding separators.** Build paths with `resolve`, not string concatenation with `"/"` or `"\\"`.

## Revision notes

- `Path` represents a location; `Paths.get` / `Path.of`, `resolve`, `getFileName`, `getParent`, `normalize`.
- `Files` does the work: `exists`, `createDirectories`, `write`, `readAllLines`, `copy`, `move`, `delete`.
- Small files: read all at once; large files: `BufferedReader` or `Files.lines`.
- Default truncate; `StandardOpenOption.APPEND` to append.
- Most methods throw `IOException` (for example `NoSuchFileException`).
- Close readers, writers, and file streams with try-with-resources.

## Practice questions

:::question basic
How do you build the path `data/2026/report.txt` portably from a base path `data`?
:::answer
`Paths.get("data").resolve("2026").resolve("report.txt")`, or `Paths.get("data", "2026", "report.txt")`. These use the platform's separator automatically, unlike concatenating strings with `"/"`.
:::

:::question basic
What does `Files.write(path, lines)` do if the file already exists?
:::answer
By default it truncates the existing file and writes the new lines, replacing the old contents. Pass `StandardOpenOption.APPEND` (and `CREATE` if needed) to add to the end instead.
:::

:::question intermediate
Why should the stream returned by `Files.lines(path)` be used inside try-with-resources?
:::answer
The stream keeps the underlying file open while elements are read lazily. It is not closed automatically when the terminal operation finishes, so without try-with-resources the file handle leaks; repeated leaks can exhaust the operating system's limit on open files.
:::

:::question intermediate
When would you choose `BufferedReader` over `Files.readAllLines`?
:::answer
For large files, or when you can stop early. `readAllLines` loads every line into a list in memory at once, while a `BufferedReader` reads one line at a time, so memory use stays small regardless of file size and processing can begin immediately.
:::

:::question advanced
Write the core of a method that counts the lines containing "ERROR" in a possibly huge log, handling a missing file gracefully.
:::answer
`static long countErrors(Path log) { try (Stream<String> lines = Files.lines(log, StandardCharsets.UTF_8)) { return lines.filter(l -> l.contains("ERROR")).count(); } catch (NoSuchFileException e) { return 0; } catch (IOException e) { throw new UncheckedIOException(e); } }`. The stream processes the file lazily with constant memory, try-with-resources closes the file, a missing file returns 0, and other I/O errors are rethrown with their cause.
:::

## Further learning

- **Next:** *Thread Synchronization & Concurrency* covers running file and network work in parallel.
- **Related:** *Checked vs Runtime Exceptions* explains the `IOException` handling used throughout this lesson.
