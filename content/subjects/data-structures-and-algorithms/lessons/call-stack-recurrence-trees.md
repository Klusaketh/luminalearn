---
lesson: call-stack-recurrence-trees
title: The Call Stack and Recurrence Trees
summary: Follow recursive calls on the call stack, write recurrences for recursive algorithms, and solve them with recursion trees and the Master Theorem.
minutes: 45
type: theory
objectives:
  - Trace how recursive calls push and pop stack frames, and predict the recursion depth and stack space of a recursive function
  - Write a recurrence for a recursive algorithm and solve it with the recursion-tree method
  - Apply the Master Theorem to divide-and-conquer recurrences and recognise recurrences it does not cover
  - Rewrite deep or tail recursion as iteration when stack depth becomes a problem
---

## Introduction

Recursion lets a function solve a problem by calling itself on smaller versions of the same problem. It produces some of the shortest and clearest algorithms in computer science (tree traversals, merge sort, quicksort, backtracking), but it raises two questions that loops do not.

The first is **how it runs**. Each pending call needs its own memory, kept on the **call stack**, so a recursive function uses space proportional to how deep the calls go, and too much depth crashes the program. The second is **how long it takes**. The running time of a recursive algorithm is naturally described by a **recurrence**, an equation that defines $T(n)$ in terms of $T$ on smaller inputs. This lesson shows how to see a recursion's execution as a tree, how to read its time and space from that tree, and how to solve the most common recurrences in one step with the **Master Theorem**.

**Before you start:** you should know functions, the stack data structure, and asymptotic notation, including logarithms.

## Core theory

### Anatomy of a recursive function

Every correct recursive function has:

- one or more **base cases** that return without recursing;
- a **recursive case** that calls the function on inputs that are **closer to a base case**.

If some input never reaches a base case, the recursion never stops.

### The call stack

When a function is called, the runtime pushes a **stack frame** holding its arguments, local variables, and the place to return to. When it returns, its frame is popped and the caller continues. For a recursive function, the frames of all pending calls are on the stack at once, each with its own copy of the local variables.

- The **recursion depth** is the largest number of frames that are live at the same time: the length of the longest chain of nested calls.
- The **stack space** is proportional to the depth (times the frame size), not to the total number of calls. Recursive Fibonacci makes an exponential number of calls but never has more than $n$ frames live.
- CPython limits the depth to 1000 frames by default and raises `RecursionError` beyond it, and it does not perform **tail-call optimisation**, even when the recursive call is the very last action of the function.

### The recursion tree

Draw each call as a node, with the calls it makes as its children. The tree's **height** is the recursion depth, so it gives the stack space; the **sum of the work over all nodes** gives the running time. This is the **recursion-tree method** for solving recurrences:

1. Write the cost of the root (the non-recursive work at the top level).
2. Expand level by level: at level $i$, count the nodes and the cost of each.
3. Sum each level, then sum over the levels.

For merge sort, $T(n) = 2T(n/2) + n$: level $i$ has $2^i$ nodes, each costing $n/2^i$, so every level costs $n$. There are $\log_2 n + 1$ levels, so the total is $\Theta(n \log n)$.

### Common recurrences

| Recurrence | Example | Solution |
| :--- | :--- | :--- |
| $T(n) = T(n-1) + O(1)$ | recursive factorial, sum of a list | $\Theta(n)$ |
| $T(n) = T(n-1) + O(n)$ | recursive selection sort | $\Theta(n^2)$ |
| $T(n) = T(n/2) + O(1)$ | binary search | $\Theta(\log n)$ |
| $T(n) = 2T(n/2) + O(n)$ | merge sort | $\Theta(n \log n)$ |
| $T(n) = 2T(n-1) + O(1)$ | Towers of Hanoi | $\Theta(2^n)$ |
| $T(n) = T(n-1) + T(n-2) + O(1)$ | naive Fibonacci | $\Theta(\varphi^n)$, $\varphi \approx 1.618$ |

### The Master Theorem

Many divide-and-conquer algorithms split a problem of size $n$ into $a$ subproblems of size $n/b$ and spend $f(n)$ on dividing and combining:

$$T(n) = a\,T(n/b) + f(n), \qquad a \ge 1,\; b > 1.$$

The recursion tree has $a^{\log_b n} = n^{\log_b a}$ leaves. The theorem compares $f(n)$ with this **critical function** $n^{\log_b a}$:

1. If $f(n) = O(n^{\log_b a - \varepsilon})$ for some $\varepsilon > 0$ (the leaves dominate), then $T(n) = \Theta(n^{\log_b a})$.
2. If $f(n) = \Theta(n^{\log_b a})$ (every level costs the same), then $T(n) = \Theta(n^{\log_b a} \log n)$.
3. If $f(n) = \Omega(n^{\log_b a + \varepsilon})$ for some $\varepsilon > 0$ and $a f(n/b) \le c f(n)$ for some $c < 1$ and all large $n$ (the root dominates), then $T(n) = \Theta(f(n))$.

| Recurrence | $n^{\log_b a}$ | Case | Solution |
| :--- | :--- | :--- | :--- |
| Binary search: $T(n/2) + 1$ | $n^0 = 1$ | 2 | $\Theta(\log n)$ |
| Merge sort: $2T(n/2) + n$ | $n$ | 2 | $\Theta(n \log n)$ |
| Karatsuba multiplication: $3T(n/2) + n$ | $n^{\log_2 3} \approx n^{1.585}$ | 1 | $\Theta(n^{1.585})$ |
| Strassen's matrix multiplication: $7T(n/2) + n^2$ | $n^{\log_2 7} \approx n^{2.807}$ | 1 | $\Theta(n^{2.807})$ |
| $2T(n/2) + n^2$ | $n$ | 3 | $\Theta(n^2)$ |

The theorem does **not** apply when the subproblems shrink by subtraction rather than division ($T(n) = T(n - 1) + n$), when the subproblems have different sizes ($T(n) = T(n/3) + T(2n/3) + n$), or when $f(n)$ falls in a gap between the cases ($T(n) = 2T(n/2) + n \log n$, where $n \log n$ is larger than $n$ but not by a polynomial factor). The recursion-tree method still works for all of them.

### From recursion to iteration

When recursion would be too deep, convert it:

- A **tail-recursive** function, whose recursive call is its final action, becomes a loop that updates its parameters and jumps back to the top.
- Any other recursion can use an explicit stack (a Python list) holding what the call stack would have held, as iterative depth-first traversals do.

## Worked examples

### Example 1: Watching the stack grow and shrink

```python
def factorial(n, depth=0):
    indent = "  " * depth
    print(f"{indent}call factorial({n})")
    if n <= 1:
        result = 1                            # base case
    else:
        result = n * factorial(n - 1, depth + 1)
    print(f"{indent}return {result}")
    return result

factorial(4)
```

Output:

```text
call factorial(4)
  call factorial(3)
    call factorial(2)
      call factorial(1)
      return 1
    return 2
  return 6
return 24
```

The indentation shows the stack depth. At the deepest point, four frames are live, one each for $n = 4, 3, 2, 1$, and each holds its own `n` and `result`. No multiplication happens on the way down; each frame waits for the frame above it to return, then multiplies, so the results are computed on the way back up, in the reverse order of the calls. Time and stack space are both $\Theta(n)$, matching $T(n) = T(n-1) + O(1)$.

### Example 2: Counting calls in a branching recursion

```python
calls = 0

def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)

for n in (10, 20, 25):
    calls = 0
    value = fib(n)
    print(f"fib({n}) = {value}, calls = {calls}")
```

Output:

```text
fib(10) = 55, calls = 177
fib(20) = 6765, calls = 21891
fib(25) = 75025, calls = 242785
```

The number of calls $C(n)$ satisfies $C(n) = C(n-1) + C(n-2) + 1$ with $C(0) = C(1) = 1$, whose solution is $C(n) = 2F(n+1) - 1$, where $F$ is the Fibonacci sequence: $2 \cdot 89 - 1 = 177$ for $n = 10$. Calls grow by a factor of about 1.618 for each increase of $n$ by one. Yet the recursion depth is only $n$, because the tree's longest branch follows $n, n-1, \dots, 1$. Exponential time with linear space is typical of branching recursion, and the remedy is to stop recomputing the same subproblems, which is the topic of dynamic programming.

### Example 3: Checking Master Theorem predictions numerically

Three recurrences, evaluated exactly for powers of two, and divided by the growth rate the Master Theorem predicts:

- $A(n) = 2A(n/2) + n$ with $A(1) = 0$: case 2, predicted $\Theta(n \log n)$.
- $B(n) = 4B(n/2) + n$ with $B(1) = 1$: $n^{\log_2 4} = n^2$ beats $f(n) = n$, case 1, predicted $\Theta(n^2)$.
- $C(n) = C(n/2) + n$ with $C(1) = 1$: $n^{\log_2 1} = 1$ is beaten by $f(n) = n$, case 3, predicted $\Theta(n)$.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def merge_like(n):                 # A(n) = 2A(n/2) + n, A(1) = 0
    return 0 if n == 1 else 2 * merge_like(n // 2) + n

@lru_cache(maxsize=None)
def four_halves(n):                # B(n) = 4B(n/2) + n, B(1) = 1
    return 1 if n == 1 else 4 * four_halves(n // 2) + n

@lru_cache(maxsize=None)
def one_half(n):                   # C(n) = C(n/2) + n, C(1) = 1
    return 1 if n == 1 else one_half(n // 2) + n

print(f"{'n':>6} {'A(n)/(n log n)':>15} {'B(n)/n^2':>9} {'C(n)/n':>7}")
for k in (4, 8, 12, 16):
    n = 2 ** k
    print(f"{n:>6} {merge_like(n) / (n * k):>15.3f} {four_halves(n) / n**2:>9.4f} {one_half(n) / n:>7.4f}")
```

Output:

```text
     n  A(n)/(n log n)  B(n)/n^2  C(n)/n
    16           1.000    1.9375  1.9375
   256           1.000    1.9961  1.9961
  4096           1.000    1.9998  1.9998
 65536           1.000    2.0000  2.0000
```

Every ratio settles to a constant, confirming the three predictions. In fact the exact solutions are $A(n) = n \log_2 n$, $B(n) = 2n^2 - n$, and $C(n) = 2n - 1$. The recursion tree explains each one. For $A$, all $\log_2 n$ levels cost $n$. For $B$, level $i$ costs $4^i \cdot n/2^i = 2^i n$, so the costs double at every level and the leaves dominate. For $C$, level $i$ costs $n/2^i$, a geometric series dominated by the root, $n + n/2 + n/4 + \dots < 2n$.

### Example 4: Removing a tail call

```python
def gcd_recursive(a, b):
    return a if b == 0 else gcd_recursive(b, a % b)   # the recursive call is the last action

def gcd_iterative(a, b):
    while b != 0:                    # the tail call becomes "update the parameters and loop"
        a, b = b, a % b
    return a

def count_down(n):
    return "done" if n == 0 else count_down(n - 1)

def count_down_loop(n):
    while n != 0:
        n -= 1
    return "done"

print(gcd_recursive(1071, 462), gcd_iterative(1071, 462))
try:
    count_down(100_000)
except RecursionError:
    print("count_down(100_000): RecursionError")
print("count_down_loop(100_000):", count_down_loop(100_000))
```

Output:

```text
21 21
count_down(100_000): RecursionError
count_down_loop(100_000): done
```

Euclid's algorithm is tail-recursive: nothing remains to be done after the recursive call returns, so the loop version simply replaces `(a, b)` with `(b, a % b)`. The count-down function shows why the conversion matters in Python: 100,000 nested calls exceed the recursion limit, while the loop runs in constant stack space.

## Applications

- **Analysing divide-and-conquer algorithms** such as merge sort, binary search, Karatsuba multiplication, and Strassen's algorithm with the Master Theorem.
- **Debugging:** stack traces print the chain of live frames, exactly the call stack described here, which shows how a program reached an error.
- **Language runtimes and compilers** manage frames, and some languages (such as Scheme) guarantee tail-call elimination so that tail-recursive loops run in constant space.
- **Choosing between recursive and iterative code:** deep recursion over long linked lists, deep trees, or large graphs is rewritten with explicit stacks to avoid overflow.
- **Performance diagnosis:** recognising an exponential recurrence such as $T(n) = 2T(n-1) + 1$ signals that memoization or a different algorithm is needed.

## Common mistakes

- **A missing or unreachable base case,** such as `factorial(n)` called with a negative `n` when the base case tests only `n == 1`, which recurses until the stack overflows.
- **Confusing the number of calls with the stack depth.** Naive Fibonacci makes exponentially many calls but uses only linear stack space.
- **Applying the Master Theorem to the wrong shape,** such as $T(n) = T(n-1) + n$, which has subtraction rather than division, or forcing a recurrence that falls between the cases.
- **Forgetting the regularity condition** in case 3, or comparing $f(n)$ with $n^{\log_b a}$ only up to constant factors, when the theorem needs a polynomial gap in cases 1 and 3.
- **Expecting Python to optimise tail calls.** CPython keeps every frame, so tail-recursive code still hits the recursion limit.

## Revision notes

- Recursion needs base cases and progress towards them. Each pending call holds a stack frame.
- Stack space is proportional to the recursion depth (the tree's height); time is the total work over all nodes.
- Recursion-tree method: cost per level times number of levels, or the sum of a geometric series.
- Master Theorem for $T(n) = aT(n/b) + f(n)$: compare $f(n)$ with $n^{\log_b a}$. Leaves dominate: $\Theta(n^{\log_b a})$. Balanced: $\Theta(n^{\log_b a} \log n)$. Root dominates (with regularity): $\Theta(f(n))$.
- Not covered: subtractive recurrences, unequal splits, and gaps such as $2T(n/2) + n \log n$, which solves to $\Theta(n \log^2 n)$.
- Tail recursion becomes a loop; other deep recursion can use an explicit stack.

## Practice questions

:::question basic
What is the maximum recursion depth of a recursive binary search on a sorted array of 1024 elements?
:::answer
Each call halves the interval, so the sizes go 1024, 512, 256, ..., 2, 1, which is 11 calls, followed at most by one call on an empty interval. The depth is about $\log_2 1024 + 1 = 11$ or 12 frames, depending on how the base case is written. That is $\Theta(\log n)$ stack space, compared with $O(1)$ for the iterative version.
:::

:::question basic
Write the recurrence for a recursive function that sums a list by adding the first element to the sum of the rest, and solve it.
:::answer
Each call does constant work plus a call on a list one element shorter: $T(n) = T(n - 1) + O(1)$ with $T(0) = O(1)$. Unrolling gives $n$ levels of constant work, so $T(n) = \Theta(n)$. The depth is also $n$, so the function needs $\Theta(n)$ stack space, and in CPython it fails for lists of more than about 1000 elements. (If the "rest" is built by slicing, each call also copies the list, giving $T(n) = T(n-1) + O(n) = \Theta(n^2)$.)
:::

:::question intermediate
Solve $T(n) = 3T(n/2) + n$ with the Master Theorem.
:::answer
Here $a = 3$, $b = 2$, and $f(n) = n$. The critical function is $n^{\log_2 3} \approx n^{1.585}$. Since $f(n) = n = O(n^{1.585 - \varepsilon})$ for, say, $\varepsilon = 0.5$, case 1 applies: $T(n) = \Theta(n^{\log_2 3})$. This is the running time of Karatsuba's multiplication algorithm, which beats the $\Theta(n^2)$ schoolbook method.
:::

:::question intermediate
Solve $T(n) = 2T(n/2) + n^2$ and check the regularity condition.
:::answer
The critical function is $n^{\log_2 2} = n$, and $f(n) = n^2 = \Omega(n^{1 + \varepsilon})$ with $\varepsilon = 1$, so case 3 may apply. Regularity: $a f(n/b) = 2 (n/2)^2 = n^2/2 \le c\, n^2$ with $c = 1/2 < 1$, which holds. Therefore $T(n) = \Theta(n^2)$: the work at the root dominates, and the levels below shrink geometrically ($n^2, n^2/2, n^2/4, \dots$).
:::

:::question intermediate
Use a recursion tree to solve $T(n) = T(n/3) + T(2n/3) + n$.
:::answer
The root costs $n$. Its children cost $n/3$ and $2n/3$, which also sum to $n$, and every full level below sums to $n$ as well (levels near the bottom sum to less, as the shorter branches end). The shortest root-to-leaf path follows the $n/3$ branches and has length $\log_3 n$; the longest follows the $2n/3$ branches and has length $\log_{3/2} n$. So the total is at least $n \log_3 n$ and at most $n \log_{3/2} n$, and $T(n) = \Theta(n \log n)$. The Master Theorem does not apply, because the subproblems have different sizes.
:::

:::question advanced
Explain why the Master Theorem does not apply to $T(n) = 2T(n/2) + n \log n$, and solve it with a recursion tree.
:::answer
The critical function is $n^{\log_2 2} = n$. The function $f(n) = n \log n$ is asymptotically larger than $n$, so case 2 does not hold, but it is not larger by a polynomial factor $n^{\varepsilon}$, because $\log n$ grows more slowly than any $n^{\varepsilon}$; so case 3 does not hold either. In the recursion tree, level $i$ has $2^i$ nodes of size $n/2^i$, each costing $(n/2^i)\log(n/2^i)$, so the level costs $n(\log_2 n - i)$. Summing over $i = 0, \dots, \log_2 n - 1$ gives $n(\log_2 n + (\log_2 n - 1) + \dots + 1) = \Theta(n \log^2 n)$.
:::

:::question advanced
The Towers of Hanoi moves $n$ disks by moving $n - 1$ disks out of the way, moving the largest disk, and moving the $n - 1$ disks back on top. Write and solve the recurrence for the number of moves, and give the recursion depth.
:::answer
The number of moves satisfies $M(n) = 2M(n-1) + 1$ with $M(0) = 0$. Unrolling: $M(n) = 2^k M(n - k) + (2^{k-1} + \dots + 2 + 1)$, and with $k = n$ this gives $M(n) = 2^n - 1$. So 10 disks need 1023 moves and 64 disks need about $1.8 \times 10^{19}$. Despite the exponential number of calls, the recursion depth is only $n$, because each chain of nested calls reduces $n$ by one.
:::

## Further learning

- **Next:** *Backtracking* uses recursion to search systematically through all candidate solutions.
- **Related:** *Merge Sort & QuickSort* provides the divide-and-conquer recurrences analysed here.
- **Related:** *Memoization vs Tabulation* removes the repeated subproblems that make recursions such as naive Fibonacci exponential.
