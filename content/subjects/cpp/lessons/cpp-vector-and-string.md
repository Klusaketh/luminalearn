---
lesson: cpp-vector-and-string
title: Standard Containers (vector & string)
summary: std::vector as a self-managing dynamic array, the difference between size and capacity, how growth and reallocation work, bounds-checked access, and the most useful std::string operations.
minutes: 35
type: theory
objectives:
  - Create, access, grow, and shrink std::vector objects and explain the cost of each operation
  - Distinguish size from capacity and explain why push_back is amortized constant time and invalidates iterators on reallocation
  - Use std::string member functions and conversions to process text safely
review: ai-draft
---
## Introduction

`std::vector` is the container you should reach for first in C++. It is a dynamic array that manages its own memory: it grows when you add elements, frees its storage automatically when it goes out of scope, and still offers the same constant-time indexing as a raw array. `std::string` is essentially a vector of characters with text-specific operations. Together they replace almost all uses of `new[]`, `malloc`, and character arrays.

**Before you start:** you should know C++ basic syntax, references, and range-based `for` loops.

## Core theory

### Creating and using vectors

```cpp
std::vector<int> a;              // empty
std::vector<int> b(5, 0);        // five zeros
std::vector<int> c = {3, 1, 4};  // initializer list
```

- Access: `c[i]` (no bounds check), `c.at(i)` (throws `std::out_of_range` if `i` is invalid), `c.front()`, `c.back()`.
- Grow and shrink: `push_back(x)`, `emplace_back(args...)` (constructs in place), `pop_back()`, `insert(pos, x)`, `erase(pos)`, `clear()`, `resize(n)`.
- Query: `size()`, `empty()`.

### Size versus capacity

The **size** is the number of elements stored; the **capacity** is how many fit in the memory already allocated. When `push_back` is called with `size() == capacity()`, the vector allocates a larger block (typically 1.5 or 2 times larger, depending on the library), moves the elements across, and frees the old block. Because capacity grows geometrically, the total cost of $n$ `push_back` calls is $O(n)$, so each is **amortized** $O(1)$. If you know the final size, `reserve(n)` allocates once and avoids repeated reallocations. `shrink_to_fit()` asks the vector to release unused capacity.

### Costs of vector operations

| Operation | Cost |
| :--- | :--- |
| `v[i]`, `v.at(i)`, `back()` | $O(1)$ |
| `push_back`, `pop_back` | amortized $O(1)$ |
| `insert` / `erase` at position `p` | $O(n - p)$: later elements shift |
| search for a value | $O(n)$ |

### Iterator invalidation

An **iterator** is a pointer-like object that marks a position in a container; `v.begin()` points to the first element and `v.end()` one past the last. When a vector reallocates, all its elements move, so every iterator, pointer, and reference into it becomes **invalid**. Inserting or erasing also invalidates iterators at and after the position. Using an invalidated iterator is undefined behaviour. The classic bug is calling `push_back` while looping over the same vector with iterators or a range-based `for`.

### std::string operations

Strings support `+`, `+=`, comparison operators, `size()`, indexing, `substr(pos, len)`, `find(text)` (returning `std::string::npos` when absent), `replace`, `insert`, and `erase`. Conversions: `std::to_string(42)` gives `"42"`, and `std::stoi("17")` and `std::stod("2.5")` parse numbers, throwing `std::invalid_argument` on bad input. `std::string_view` (C++17) gives a cheap read-only view of characters without copying.

## Worked examples

### Example 1: Growing a vector and checking bounds

```cpp
#include <iostream>
#include <stdexcept>
#include <vector>

int main() {
    std::vector<int> squares;
    squares.reserve(10);
    for (int i = 1; i <= 6; i++) squares.push_back(i * i);
    std::cout << "size " << squares.size() << ", capacity >= size: " << (squares.capacity() >= squares.size()) << '\n';

    squares.erase(squares.begin() + 1);
    squares.insert(squares.begin(), 0);
    for (int x : squares) std::cout << x << ' ';
    std::cout << '\n';

    try {
        std::cout << squares.at(10) << '\n';
    } catch (const std::out_of_range&) {
        std::cout << "at(10) is out of range\n";
    }
    squares.resize(3);
    std::cout << "after resize: " << squares.size() << " elements, back = " << squares.back() << '\n';
    return 0;
}
```

Output:

```text
size 6, capacity >= size: 1
0 1 9 16 25 36
at(10) is out of range
after resize: 3 elements, back = 9
```

`erase` removes the 4 at index 1 and `insert` places 0 at the front, shifting the others. `at` throws instead of silently reading invalid memory, which `squares[10]` would do.

### Example 2: Processing text with std::string

```cpp
#include <iostream>
#include <string>
#include <vector>

std::vector<std::string> split(const std::string& s, char sep) {
    std::vector<std::string> parts;
    std::size_t start = 0, pos;
    while ((pos = s.find(sep, start)) != std::string::npos) {
        parts.push_back(s.substr(start, pos - start));
        start = pos + 1;
    }
    parts.push_back(s.substr(start));
    return parts;
}

int main() {
    std::string record = "Meena,85,CSE";
    auto fields = split(record, ',');
    int marks = std::stoi(fields[1]) + 5;
    std::string summary = fields[0] + " (" + fields[2] + ") now has " + std::to_string(marks);
    std::cout << summary << '\n';
    std::cout << "fields: " << fields.size() << ", summary length: " << summary.size() << '\n';
    summary.replace(summary.find("now has"), 7, "scored");
    std::cout << summary << '\n';
    std::cout << (std::string("apple") < std::string("banana")) << '\n';
    return 0;
}
```

Output:

```text
Meena (CSE) now has 90
fields: 3, summary length: 22
Meena (CSE) scored 90
1
```

`find` returns each comma's position, and `substr` extracts the text between them; the final field is everything after the last comma. `std::stoi` and `std::to_string` convert between text and numbers.

## Applications

- **General-purpose storage:** vectors hold lists of records, coordinates, or samples.
- **Graphs:** `std::vector<std::vector<int>>` is the standard adjacency list.
- **Text processing:** parsing CSV lines and building reports with `std::string`.
- **Performance:** contiguous storage gives excellent cache behaviour.

## Common mistakes

- **Modifying a vector while iterating over it.** `push_back` may reallocate and invalidate the loop's iterator.
- **Using `[]` with untrusted indices.** Use `at()` or check the index first.
- **Calling `reserve` and then indexing.** `reserve` changes capacity, not size; `v[0]` is still invalid until elements are added.
- **Ignoring `npos`.** Check `find` results before using them as positions.

## Revision notes

- `std::vector` is a growable array with automatic memory management.
- `size()` counts elements; `capacity()` counts allocated slots; `reserve` sets capacity.
- `push_back` is amortized $O(1)$; middle `insert`/`erase` is $O(n)$.
- Reallocation invalidates all iterators, pointers, and references.
- `at()` checks bounds and throws `std::out_of_range`.
- `find` returns `npos` when absent; `stoi`/`to_string` convert numbers.

## Practice questions

:::question basic
What is the difference between `v.size()` and `v.capacity()`?
:::answer
`size()` is the number of elements currently stored. `capacity()` is the number of elements the currently allocated memory can hold before the vector must reallocate; it is always at least the size.
:::

:::question basic
What happens when you call `v.at(i)` with an invalid index, compared with `v[i]`?
:::answer
`v.at(i)` throws a `std::out_of_range` exception, which you can catch. `v[i]` performs no check, so an invalid index is undefined behaviour that may read or corrupt unrelated memory.
:::

:::question intermediate
Why is calling `push_back` $n$ times $O(n)$ in total even though some calls copy every element?
:::answer
The capacity grows by a constant factor, so reallocations become rarer as the vector grows. With doubling, the elements copied over all reallocations total $1 + 2 + 4 + \dots + n < 2n$, which spread over $n$ calls is a constant amount per call: amortized $O(1)$.
:::

:::question intermediate
What is wrong with `for (int x : v) if (x > 0) v.push_back(-x);`?
:::answer
The range-based loop uses iterators into `v`. `push_back` can reallocate the vector, invalidating those iterators, after which the loop reads freed memory: undefined behaviour. Collect the new values in a separate vector and append them after the loop.
:::

:::question advanced
You will read exactly one million integers into a vector. Compare doing it with plain `push_back` and with `reserve(1000000)` first.
:::answer
With plain `push_back`, the vector reallocates about 20 times (with doubling, $2^{20} \approx 10^6$), each time allocating a new block and moving all existing elements, which costs extra time and temporarily needs memory for two copies. With `reserve`, a single allocation of the right size happens up front, there are no moves, and no iterators are invalidated during the loop; the total work is the same order, $O(n)$, but with a smaller constant and lower peak memory.
:::

## Further learning

- **Next:** *Smart Pointers & RAII Paradigm* explains the automatic clean-up that vector relies on.
- **Related:** *Static and Dynamic Arrays* in Data Structures & Algorithms analyses dynamic array growth.
