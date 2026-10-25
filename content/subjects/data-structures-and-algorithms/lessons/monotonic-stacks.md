---
lesson: monotonic-stacks
title: Monotonic Stacks and Bracket Matching
summary: Check balanced brackets with a stack, and solve next-greater-element, stock-span, and histogram problems in linear time with monotonic stacks.
minutes: 45
type: theory
objectives:
  - Check whether a string of mixed brackets is balanced using a stack, and explain each failure case
  - Define a monotonic stack and maintain its invariant while scanning an array
  - Solve next-greater-element and stock-span problems in linear time and justify the amortized bound
  - Compute the largest rectangle in a histogram using a monotonic stack
---

## Introduction

Stacks are natural whenever the most recent unfinished item is the one that must be dealt with first. Two families of problems show this especially clearly.

The first is **bracket matching**. In `{[()]}`, the most recently opened bracket must be the first one closed, exactly the stack discipline. Compilers, editors, and data-format validators all perform this check.

The second family asks, for each element of an array, about the **nearest element to the left or right that is larger or smaller**: the next warmer day for each day's temperature, how many consecutive days a stock price has been at or below today's, or the widest bar of a histogram that a rectangle can span. A brute-force search for each element costs $\Theta(n^2)$. A **monotonic stack**, a stack kept in sorted order as you scan, answers all of them in $\Theta(n)$.

**Before you start:** you should know the stack ADT and amortized analysis.

## Core theory

### Balanced brackets

A string of brackets is **balanced** if every opening bracket has a matching closing bracket of the same type, and pairs are properly nested. The algorithm:

1. Scan left to right.
2. Push every opening bracket.
3. On a closing bracket, the stack must be non-empty and its top must be the matching opener; pop it. Otherwise the string is unbalanced.
4. At the end, the stack must be empty.

There are exactly three ways to fail:

| Failure | Example | Detected when |
| :--- | :--- | :--- |
| Wrong type | `(]` | closing bracket does not match the top |
| Extra closing bracket | `())` | closing bracket arrives with the stack empty |
| Unclosed opening bracket | `(()` | stack is non-empty at the end |

Time $\Theta(n)$, space $O(n)$ in the worst case (all openers).

For a single bracket type, a counter that never goes negative and ends at zero is enough; mixing types requires the stack to remember the order.

### The monotonic stack

A **monotonic stack** keeps its elements in increasing or decreasing order from bottom to top. As each new element arrives, you **pop every element that would violate the order**, then push the new one. The key insight is that the popped elements have just found their answer: the new element is the first one, to their right, that broke their order.

For "next greater element to the right", keep a **decreasing** stack (of indices). When `a[i]` arrives:

- while the top of the stack has a value **less than** `a[i]`, pop it: its next greater element is `a[i]`;
- push `i`.

Elements left on the stack at the end have no greater element to their right.

### Why it is linear

The loop contains a `while` loop, so it can look quadratic. But every index is **pushed exactly once and popped at most once**. Across the whole scan there are at most $n$ pushes and $n$ pops, so the total work is $\Theta(n)$. This is an aggregate amortized argument: a single step can pop many elements, but only because many earlier steps pushed them.

### Choosing the variant

| Question | Stack order (bottom to top) | Pop while top is |
| :--- | :--- | :--- |
| Next greater to the right | decreasing | less than current |
| Next smaller to the right | increasing | greater than current |
| Previous greater to the left | decreasing | less than or equal to current (then the top is the answer) |
| Previous smaller to the left | increasing | greater than or equal to current |

Whether to pop on strict or non-strict comparison decides how equal values are handled; choose it deliberately for each problem.

### Largest rectangle in a histogram

Given bar heights, find the largest rectangle that fits under the bars. A rectangle that uses bar $i$ as its shortest bar can extend left and right until it meets a bar shorter than $h_i$. So for each bar we need the previous smaller and next smaller bars: exactly what an increasing monotonic stack provides. When a bar is popped because a shorter bar arrived, its right boundary is the current index and its left boundary is the new top of the stack. The width is the gap between them, and the area is the height times that width.

## Worked examples

### Example 1: Balanced brackets

```python
PAIRS = {")": "(", "]": "[", "}": "{"}

def is_balanced(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack

for s in ("{[()()]}", "([)]", "(()", "())", "print(a[0])"):
    print(f"{s!r:16} {is_balanced(s)}")
```

Output:

```text
'{[()()]}'       True
'([)]'           False
'(()'            False
'())'            False
'print(a[0])'    True
```

`([)]` fails because `)` arrives while the top is `[`. Other characters are ignored, so the same function checks brackets in source code.

### Example 2: Next greater element

```python
def next_greater(values):
    result = [-1] * len(values)
    stack = []                       # indices; their values decrease bottom to top
    for i, v in enumerate(values):
        while stack and values[stack[-1]] < v:
            result[stack.pop()] = v
        stack.append(i)
    return result

print(next_greater([2, 1, 2, 4, 3]))
print(next_greater([73, 74, 75, 71, 69, 72, 76, 73]))
```

Output:

```text
[4, 2, 4, -1, -1]
[74, 75, 76, 72, 72, 76, -1, -1]
```

Trace of the first array:

| i | value | pops (index: answer) | stack after |
| :---: | :---: | :--- | :--- |
| 0 | 2 | none | [0] |
| 1 | 1 | none | [0, 1] |
| 2 | 2 | 1: 2 | [0, 2] |
| 3 | 4 | 2: 4, 0: 4 | [3] |
| 4 | 3 | none | [3, 4] |

Indices 3 and 4 remain, so they have no greater element (-1). Storing indices rather than values lets us write each answer into the right position.

### Example 3: Stock span

The **span** of a stock's price on day $i$ is the number of consecutive days ending on day $i$ on which the price was at most today's price.

```python
def stock_span(prices):
    spans, stack = [], []            # stack of indices with decreasing prices
    for i, p in enumerate(prices):
        while stack and prices[stack[-1]] <= p:
            stack.pop()
        spans.append(i + 1 if not stack else i - stack[-1])
        stack.append(i)
    return spans

print(stock_span([100, 80, 60, 70, 60, 75, 85]))
```

Output:

```text
[1, 1, 1, 2, 1, 4, 6]
```

After popping every earlier day with a price at most today's, the top of the stack is the previous **strictly greater** day, so the span is the distance to it. On day 5 (price 75), days 4, 3, and 2 are popped and the top is day 1 (price 80), so the span is $5 - 1 = 4$.

### Example 4: Largest rectangle in a histogram

```python
def largest_rectangle(heights):
    stack, best = [], 0              # indices with increasing heights
    for i, h in enumerate(heights + [0]):        # sentinel 0 flushes the stack
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best

print(largest_rectangle([2, 1, 5, 6, 2, 3]))
```

Output:

```text
10
```

When the bar of height 2 at index 4 arrives, it pops height 6 (width 1, area 6) and then height 5 (its left boundary is index 1, so width $4 - 1 - 1 = 2$, area 10). The appended sentinel of height 0 forces every remaining bar to be popped at the end. Each bar is pushed and popped once: $\Theta(n)$ time.

## Applications

- **Compilers, linters, and editors** check bracket balance and highlight the matching bracket as you type.
- **Data validation**: JSON and XML parsers track nested structures with stacks.
- **Finance and weather analytics** compute stock spans and "days until a warmer temperature" with monotonic stacks.
- **Image processing and computational geometry**: the maximal-rectangle-in-a-binary-matrix problem reduces to a histogram per row.
- **Algorithm design**: monotonic stacks and queues speed up dynamic programming and sliding-window maximum computations.

## Common mistakes

- **Using a counter for multiple bracket types.** `([)]` has balanced counts of each type but is not properly nested.
- **Popping an empty stack** when a closing bracket arrives first; always check emptiness before popping.
- **Forgetting the final emptiness check,** which lets `((` pass as balanced.
- **Storing values instead of indices** when the answer depends on positions (distances, widths, or writing results in place).
- **Mixing up strict and non-strict comparisons,** which changes how equal elements are treated and can produce wrong spans or widths.

## Revision notes

- Balanced brackets: push openers; a closer must match the top; the stack must end empty. Three failure modes.
- Monotonic stack: pop elements that break the order, then push. Popped elements find their answer in the current element.
- Each index is pushed once and popped at most once, so the scan is $\Theta(n)$ amortized.
- Next greater to the right: decreasing stack. Next smaller: increasing stack.
- Stock span: after popping smaller-or-equal prices, the top is the previous greater day.
- Histogram: increasing stack; width = current index minus new top minus one.

## Practice questions

:::question basic
Is `{[]()}[` balanced? If not, which failure case applies?
:::answer
No. All the closing brackets match correctly, but the final `[` is never closed, so the stack is not empty at the end. This is the "unclosed opening bracket" failure.
:::

:::question basic
Why is a single counter enough to check `(()())` but not `([)]`?
:::answer
With one bracket type, the only requirement is that the number of `)` never exceeds the number of `(` so far and that they are equal at the end, which a counter tracks. With several types, the order also matters: `([)]` has one of each type opened and closed, so counters would accept it, but the `)` closes while `[` is the most recently opened bracket. A stack remembers that order.
:::

:::question intermediate
Compute the next greater element for every position in `[4, 5, 2, 25]` and show the stack after each step.
:::answer
i=0 (4): stack [0]. i=1 (5): pop 0 (answer 5), stack [1]. i=2 (2): stack [1, 2]. i=3 (25): pop 2 (answer 25), pop 1 (answer 25), stack [3]. Index 3 has no greater element. Result: `[5, 25, 25, -1]`.
:::

:::question intermediate
Explain why the next-greater-element algorithm is $\Theta(n)$ even though it has a `while` loop inside a `for` loop.
:::answer
Count operations across the whole run rather than per iteration. Each index is pushed exactly once, when the `for` loop reaches it, and can be popped at most once. So the `while` loop body executes at most $n$ times in total over all iterations. Together with the $n$ pushes, the total work is $O(n)$, and since every element must be read, it is $\Theta(n)$.
:::

:::question intermediate
Find the largest rectangle in the histogram `[2, 4]` and the histogram `[6, 2, 5, 4, 5, 1, 6]`.
:::answer
For `[2, 4]`: the candidates are 4 (bar 2 alone), 2 × 2 = 4 (both bars at height 2), so the answer is 4. For `[6, 2, 5, 4, 5, 1, 6]`: the best is height 4 across the three bars `5, 4, 5`, giving $4 \times 3 = 12$. Other candidates are smaller: height 2 across the five bars from index 0 to 4 gives 10, and the single tall bars give 6.
:::

:::question advanced
Design an $O(n)$ algorithm that, for an array of daily temperatures, returns for each day the number of days you must wait for a warmer temperature (0 if none). Explain how it differs from next greater element.
:::answer
Use the same decreasing monotonic stack of indices. When day $i$ arrives, pop every index $j$ whose temperature is less than day $i$'s, and set `wait[j] = i - j`; then push $i$. Days left on the stack get 0. The only difference from next greater element is what is recorded: the distance between indices instead of the greater value itself. Each index is pushed and popped at most once, so the total time is $\Theta(n)$.
:::

## Further learning

- **Next:** *Circular Queues & Deque* introduces the first-in, first-out queue and the double-ended queue.
- **Related:** *Sliding Window & Two-Pointers* combines with a monotonic deque to find the maximum of every window in linear time.
- **Related:** *Amortized Analysis* formalises the "each element is pushed and popped once" argument.
