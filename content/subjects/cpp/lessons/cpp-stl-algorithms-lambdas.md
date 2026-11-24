---
lesson: cpp-stl-algorithms-lambdas
title: STL Algorithms & Lambda Expressions
summary: Using the standard algorithms (sort, find_if, count_if, transform, accumulate, remove_if, binary_search) on iterator ranges, and writing lambda expressions with parameters, captures, and return types.
minutes: 45
type: theory
objectives:
  - Apply standard algorithms to containers instead of writing explicit loops, and state their complexity
  - Write lambda expressions with parameters and value or reference captures, and use them as predicates and comparators
  - Use the erase-remove idiom and sorted-range algorithms correctly
review: ai-draft
---
## Introduction

The `<algorithm>` and `<numeric>` headers contain dozens of well-tested functions for searching, sorting, counting, transforming, and summing. Using them makes code shorter and clearer, since a named algorithm states its intent, and often faster, because library implementations are carefully optimised. Most algorithms take a small function that customises their behaviour, and **lambda expressions** let you write that function inline, right where it is used.

**Before you start:** you should know STL containers, iterators, and function templates.

## Core theory

### Algorithms work on ranges

Algorithms take a half-open iterator range `[first, last)` rather than a container, so the same algorithm works on a `vector`, an `array`, part of a container, or a plain array:

| Algorithm | Purpose | Complexity |
| :--- | :--- | :--- |
| `std::sort(f, l, cmp)` | sort (not stable) | $O(n \log n)$ |
| `std::stable_sort` | sort, keeping equal elements in order | $O(n \log n)$ |
| `std::find(f, l, v)`, `std::find_if(f, l, pred)` | first match, or `l` | $O(n)$ |
| `std::count_if(f, l, pred)` | number of matches | $O(n)$ |
| `std::transform(f, l, out, fn)` | apply `fn` to each element | $O(n)$ |
| `std::accumulate(f, l, init, op)` (in `<numeric>`) | fold into one value | $O(n)$ |
| `std::min_element`, `std::max_element` | iterator to extreme | $O(n)$ |
| `std::binary_search`, `std::lower_bound` | search a **sorted** range | $O(\log n)$ |
| `std::reverse`, `std::unique`, `std::remove_if` | rearrange | $O(n)$ |

### Lambda expressions

```cpp
[capture](parameters) -> return_type { body }
```

A lambda creates an unnamed function object. The return type can usually be omitted and is deduced. The **capture list** says which local variables the lambda can use:

- `[]` captures nothing.
- `[x]` copies `x` when the lambda is created; `[&x]` refers to the original `x`.
- `[=]` copies every used local variable; `[&]` refers to every used local variable.
- `[this]` gives access to the enclosing object's members.

Captured copies are read-only unless the lambda is declared `mutable`. A reference capture must not outlive the variable it refers to: a lambda that captures a local by reference and is stored for later use can end up with a dangling reference. Lambdas can be stored in `auto` variables or in `std::function<R(Args...)>` when the type must be named.

### The erase-remove idiom

`std::remove_if` cannot shrink a container, because it only sees iterators. It moves the elements to keep to the front and returns an iterator to the new logical end; the container's `erase` then deletes the leftover tail:

```cpp
v.erase(std::remove_if(v.begin(), v.end(), pred), v.end());
```

C++20 offers `std::erase_if(v, pred)` as a one-call version.

### Sorted-range algorithms

`binary_search`, `lower_bound`, `upper_bound`, and `equal_range` assume the range is sorted with the **same** ordering they are given; on unsorted data their results are meaningless. `lower_bound` returns the first position whose element is not less than the value, which is also where the value could be inserted to keep the range sorted.

## Worked examples

### Example 1: Replacing loops with algorithms and lambdas

```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

int main() {
    std::vector<int> marks = {72, 45, 91, 38, 66, 85, 59};
    int pass_mark = 50;
    auto passed = std::count_if(marks.begin(), marks.end(), [pass_mark](int m) { return m >= pass_mark; });
    int total = std::accumulate(marks.begin(), marks.end(), 0);
    auto best = std::max_element(marks.begin(), marks.end());
    std::cout << passed << " passed, average " << total / static_cast<double>(marks.size())
              << ", best " << *best << " at index " << (best - marks.begin()) << '\n';

    std::vector<std::string> grades(marks.size());
    std::transform(marks.begin(), marks.end(), grades.begin(),
                   [](int m) { return m >= 85 ? "A" : m >= 65 ? "B" : m >= 50 ? "C" : "F"; });
    for (const auto& g : grades) std::cout << g;
    std::cout << '\n';

    auto first_fail = std::find_if(marks.begin(), marks.end(), [&](int m) { return m < pass_mark; });
    std::cout << "first fail: " << *first_fail << '\n';

    int calls = 0;
    std::sort(marks.begin(), marks.end(), [&calls](int a, int b) { ++calls; return a > b; });
    std::cout << "sorted desc: ";
    for (int m : marks) std::cout << m << ' ';
    std::cout << "(comparator used " << (calls > 0 ? "yes" : "no") << ")\n";
    return 0;
}
```

Output:

```text
5 passed, average 65.1429, best 91 at index 2
BFAFBAC
first fail: 45
sorted desc: 91 85 72 66 59 45 38 (comparator used yes)
```

Each loop became one algorithm call. The first lambda copies `pass_mark`; the `find_if` lambda captures by reference with `[&]`; the comparator captures `calls` by reference so it can count its own calls.

### Example 2: Erase-remove, stable sorting, and binary search

```cpp
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Student { std::string name; int year; };

int main() {
    std::vector<int> v = {5, 0, 3, 0, 0, 8, 1};
    v.erase(std::remove_if(v.begin(), v.end(), [](int x) { return x == 0; }), v.end());
    for (int x : v) std::cout << x << ' ';
    std::cout << "(size " << v.size() << ")\n";

    std::vector<Student> s = {{"Ravi", 2}, {"Asha", 1}, {"John", 2}, {"Meena", 1}};
    std::stable_sort(s.begin(), s.end(), [](const Student& a, const Student& b) { return a.year < b.year; });
    for (const auto& st : s) std::cout << st.name << '(' << st.year << ") ";
    std::cout << '\n';

    std::vector<int> sorted = {2, 4, 4, 4, 7, 9};
    std::cout << std::binary_search(sorted.begin(), sorted.end(), 7) << ' '
              << std::binary_search(sorted.begin(), sorted.end(), 5) << '\n';
    auto lo = std::lower_bound(sorted.begin(), sorted.end(), 4);
    auto hi = std::upper_bound(sorted.begin(), sorted.end(), 4);
    std::cout << "4 occupies [" << (lo - sorted.begin()) << ", " << (hi - sorted.begin()) << "), insert 5 at "
              << (std::lower_bound(sorted.begin(), sorted.end(), 5) - sorted.begin()) << '\n';
    return 0;
}
```

Output:

```text
5 3 8 1 (size 4)
Asha(1) Meena(1) Ravi(2) John(2)
1 0
4 occupies [1, 4), insert 5 at 4
```

`remove_if` compacts the non-zero values to the front and `erase` cuts off the rest. `stable_sort` keeps Asha before Meena and Ravi before John, their original relative order. `lower_bound` and `upper_bound` bracket all copies of 4 in logarithmic time.

## Applications

- **Data processing:** filtering, transforming, and summarising records in a few lines.
- **Leaderboards:** sorting with custom comparators.
- **Search in sorted data:** `lower_bound` answers range and insertion-point queries quickly.
- **Callbacks:** lambdas are passed to threads, timers, and event handlers.

## Common mistakes

- **Forgetting the `erase` in erase-remove.** `remove_if` alone leaves the container's size unchanged.
- **Binary-searching unsorted data.** Sort first, with the same comparator.
- **Dangling reference captures.** A stored lambda must not capture locals by reference if it outlives them.
- **Expecting `std::sort` to be stable.** Use `std::stable_sort` when equal elements must keep their order.
- **`accumulate` with an integer initial value for doubles.** `std::accumulate(v.begin(), v.end(), 0)` sums `double`s as `int`; use `0.0`.

## Revision notes

- Algorithms take iterator ranges `[first, last)`.
- `sort`/`stable_sort` $O(n \log n)$; `find_if`/`count_if`/`transform`/`accumulate` $O(n)$.
- Lambda: `[captures](params) { body }`; `[x]` copy, `[&x]` reference, `[=]`, `[&]`.
- Erase-remove: `v.erase(std::remove_if(...), v.end())`.
- `binary_search`, `lower_bound`, `upper_bound` need sorted ranges and run in $O(\log n)$.
- `accumulate`'s initial value sets the result type.

## Practice questions

:::question basic
Write a lambda that returns true for even numbers, and use it to count the even numbers in `v`.
:::answer
`auto is_even = [](int x) { return x % 2 == 0; };` and then `std::count_if(v.begin(), v.end(), is_even)`. The lambda captures nothing because it uses only its parameter.
:::

:::question basic
What is the difference between capturing `[x]` and `[&x]`?
:::answer
`[x]` copies the value of `x` when the lambda is created, so later changes to `x` are not seen and the lambda cannot modify the original. `[&x]` refers to the original variable, so the lambda sees and can modify its current value.
:::

:::question intermediate
After `std::remove_if(v.begin(), v.end(), pred);` alone, why has `v.size()` not changed?
:::answer
Algorithms only have iterators, so they cannot change a container's size. `remove_if` shifts the elements to keep to the front and returns an iterator to the new logical end; the unwanted tail remains in the container until you call `v.erase(new_end, v.end())`.
:::

:::question intermediate
Why does `std::accumulate(prices.begin(), prices.end(), 0)` give a wrong total for `std::vector<double> prices = {1.5, 2.5}`?
:::answer
The initial value `0` is an `int`, so the accumulator is an `int` and each sum is converted back to `int`: 0 + 1.5 becomes 1, then 1 + 2.5 becomes 3. Passing `0.0` makes the accumulator a `double` and gives 4.0.
:::

:::question advanced
Explain why `std::lower_bound` on a sorted vector is $O(\log n)$ but on a `std::list` it is not, even though both calls compile.
:::answer
`lower_bound` performs a binary search, which needs to jump to the middle of a range. With random-access iterators (`vector`), each jump is $O(1)$, so the search makes $O(\log n)$ comparisons in $O(\log n)$ time. A `list` has only bidirectional iterators, so reaching the middle means stepping node by node; the algorithm still makes $O(\log n)$ comparisons but spends $O(n)$ time advancing iterators.
:::

## Further learning

- **Next:** *Exceptions & Exception Safety* covers what happens when operations inside algorithms throw.
- **Related:** *Algorithmic Patterns in Python* shows the same ideas with `sorted`, `key` functions, and comprehensions.
