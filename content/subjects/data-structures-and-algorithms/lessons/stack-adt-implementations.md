---
lesson: stack-adt-implementations
title: The Stack ADT and Its Implementations
summary: The last-in, first-out stack, its array and linked-list implementations, and its role in function calls, undo, and expression evaluation.
minutes: 45
type: theory
objectives:
  - Define the stack abstract data type and its operations with their preconditions
  - Implement a stack with a dynamic array and with a linked list, and compare the two
  - Explain how the call stack implements function calls and recursion
  - Use a stack to evaluate postfix expressions and to convert infix expressions to postfix
---

## Introduction

A **stack** is a collection where the last item added is the first one removed, like a pile of plates: you add plates to the top and take plates from the top. This rule is called **LIFO**, last in, first out.

The stack is one of the simplest data structures, yet it is everywhere. Every running program uses a **call stack** to remember which function to return to. Text editors use stacks for undo. Compilers use them to parse expressions and check that brackets balance. Depth-first search uses one to remember where to backtrack. Understanding the stack well pays off throughout computer science.

**Before you start:** you should know dynamic arrays and linked lists.

## Core theory

### The abstract data type

An **abstract data type (ADT)** specifies what operations a structure supports and how they behave, without saying how it is built. The stack ADT has:

| Operation | Effect | Precondition |
| :--- | :--- | :--- |
| `push(x)` | place `x` on top | none (or "not full" for a fixed-capacity stack) |
| `pop()` | remove and return the top item | stack is not empty |
| `peek()` (or `top()`) | return the top item without removing it | stack is not empty |
| `is_empty()` | report whether the stack has no items | none |
| `size()` | number of items | none |

Calling `pop` or `peek` on an empty stack is an error called **underflow**. Pushing onto a full fixed-capacity stack is **overflow**. A good implementation raises a clear exception rather than returning a misleading value.

All of these operations should take $O(1)$ time; that is the point of a stack.

### Array-based implementation

Store items in a dynamic array, with the top of the stack at the **end** of the array. Then `push` is an append and `pop` removes the last element, neither of which shifts anything.

- `push`: amortized $O(1)$ (an occasional resize copies everything).
- `pop`, `peek`, `is_empty`, `size`: $O(1)$.

Putting the top at the **front** of the array would be a mistake: every push and pop would shift all other elements, costing $O(n)$.

In Python, a plain `list` with `append` and `pop` is an efficient stack.

### Linked-list implementation

Store items in a singly linked list, with the top of the stack at the **head**. `push` inserts a new head node; `pop` removes the head.

- Every operation is worst-case $O(1)$, with no resizing.
- Each item costs an extra pointer, and nodes are scattered in memory.

| | Dynamic array | Linked list |
| :--- | :--- | :--- |
| Push | amortized $O(1)$, occasional $O(n)$ resize | worst-case $O(1)$ |
| Memory per item | value (plus spare capacity) | value + pointer + node overhead |
| Cache behaviour | good | poor |
| Typical choice | yes, most of the time | when worst-case time matters or nodes already exist |

### The call stack

When a function is called, the runtime pushes a **stack frame** holding its parameters, local variables, and the return address. When the function returns, its frame is popped and execution continues at the return address of the frame below. Recursion works because each recursive call gets its own frame, so each call has its own copy of its local variables.

The call stack has a limited size. Unbounded recursion pushes frames until that limit is reached, causing a **stack overflow** (in Python, a `RecursionError`).

### Expression notation

People write arithmetic in **infix** notation, with operators between operands: `3 + 4 * 2`. Infix needs precedence rules and parentheses to be unambiguous. **Postfix** notation (also called reverse Polish notation) puts each operator after its operands: `3 4 2 * +`. Postfix needs no parentheses and no precedence rules, and a stack evaluates it in one left-to-right pass:

1. Read tokens left to right.
2. Push each number.
3. For an operator, pop the right operand, then the left operand, apply the operator, and push the result.
4. At the end, the stack holds exactly one value: the answer.

The order of the two pops matters for non-commutative operators: for `a b -`, the first value popped is `b`.

### Converting infix to postfix: the shunting-yard algorithm

Edsger Dijkstra's shunting-yard algorithm converts infix to postfix using a stack of operators:

1. Numbers go straight to the output.
2. For an operator `o`: while the top of the operator stack is an operator with higher precedence than `o`, or equal precedence with `o` left-associative, pop it to the output. Then push `o`.
3. A left parenthesis is pushed.
4. A right parenthesis pops operators to the output until the matching left parenthesis, which is discarded.
5. At the end, pop all remaining operators to the output.

## Worked examples

### Example 1: A stack class with clear errors

```python
class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)          # top is the end of the list

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

s = Stack()
for x in ("a", "b", "c"):
    s.push(x)
print(s.pop(), s.peek(), len(s))
s.pop(); s.pop()
try:
    s.pop()
except IndexError as error:
    print("Error:", error)
```

Output:

```text
c b 2
Error: pop from empty stack
```

Wrapping the list hides operations that would break the stack discipline (such as inserting in the middle) and gives a meaningful error on underflow.

### Example 2: Evaluating a postfix expression

```python
def eval_postfix(expression):
    stack = []
    operations = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
    }
    for token in expression.split():
        if token in operations:
            right = stack.pop()             # popped first
            left = stack.pop()
            stack.append(operations[token](left, right))
        else:
            stack.append(float(token))
    if len(stack) != 1:
        raise ValueError("malformed expression")
    return stack[0]

print(eval_postfix("3 4 2 * +"))
print(eval_postfix("5 1 2 + 4 * + 3 -"))
```

Output:

```text
11.0
14.0
```

Trace of `5 1 2 + 4 * + 3 -`:

| Token | Stack after |
| :--- | :--- |
| 5 | [5] |
| 1 | [5, 1] |
| 2 | [5, 1, 2] |
| + | [5, 3] |
| 4 | [5, 3, 4] |
| * | [5, 12] |
| + | [17] |
| 3 | [17, 3] |
| - | [14] |

The expression corresponds to the infix `5 + (1 + 2) * 4 - 3`.

### Example 3: Infix to postfix

```python
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}

def to_postfix(tokens):
    output, ops = [], []
    for token in tokens:
        if token in PRECEDENCE:
            while ops and ops[-1] in PRECEDENCE and PRECEDENCE[ops[-1]] >= PRECEDENCE[token]:
                output.append(ops.pop())    # left-associative: pop equal precedence too
            ops.append(token)
        elif token == "(":
            ops.append(token)
        elif token == ")":
            while ops[-1] != "(":
                output.append(ops.pop())
            ops.pop()                       # discard "("
        else:
            output.append(token)
    while ops:
        output.append(ops.pop())
    return " ".join(output)

print(to_postfix("3 + 4 * 2".split()))
print(to_postfix("( 3 + 4 ) * 2".split()))
print(to_postfix("8 - 3 - 2".split()))
```

Output:

```text
3 4 2 * +
3 4 + 2 *
8 3 - 2 -
```

In the first expression, `*` has higher precedence than `+`, so `+` stays on the operator stack until the end. Parentheses in the second force the addition first. The third shows left associativity: `8 - 3 - 2` means `(8 - 3) - 2 = 3`, so the first `-` is output before the second is pushed.

## Applications

- **Function calls and recursion** in every programming language rely on the call stack.
- **Undo and redo** in editors keep actions on a stack; undo pops the most recent action (and pushes it onto a redo stack).
- **Compilers and calculators** parse and evaluate expressions with operator stacks; the Java Virtual Machine and Python's bytecode interpreter are stack machines whose instructions push and pop operands.
- **Browser history**: the back button behaves like popping a stack of visited pages.
- **Backtracking algorithms** such as depth-first search and maze solving push choices and pop them to backtrack.

## Common mistakes

- **Putting the top of an array-based stack at index 0,** which makes push and pop $O(n)$.
- **Popping operands in the wrong order** for subtraction and division in postfix evaluation.
- **Ignoring underflow.** Popping an empty stack should raise an error, not silently return a sentinel value.
- **Popping equal-precedence operators inconsistently** in shunting-yard, which breaks left associativity (and right-associative operators like exponentiation need the opposite rule).
- **Treating recursion depth as free.** Each call consumes stack space; very deep recursion overflows.

## Revision notes

- Stack = LIFO. Operations: push, pop, peek, is_empty, size; all $O(1)$.
- Array implementation: top at the end; push amortized $O(1)$. Linked implementation: top at the head; worst-case $O(1)$.
- Underflow = pop/peek on empty; overflow = push on a full fixed stack.
- Call stack: one frame per active call; unbounded recursion causes stack overflow.
- Postfix evaluation: push numbers; on an operator pop right then left, push the result.
- Shunting-yard converts infix to postfix with an operator stack and precedence rules.

## Practice questions

:::question basic
Starting with an empty stack, perform push 4, push 7, pop, push 1, push 9, pop, pop. What is returned by each pop, and what remains?
:::answer
The pops return 7, then 9, then 1. After those operations the stack holds only 4. Each pop removes the most recently pushed item that is still present.
:::

:::question basic
Why should an array-based stack keep its top at the end of the array rather than the beginning?
:::answer
Appending and removing at the end of a dynamic array touch only the last slot, so they are $O(1)$ (append is amortized $O(1)$). Inserting or removing at index 0 shifts every other element, which is $O(n)$ per operation.
:::

:::question intermediate
Evaluate the postfix expression `6 2 / 3 1 - *` and show the stack after each token.
:::answer
6: [6]. 2: [6, 2]. /: pop 2 and 6, push 6/2 = 3, giving [3]. 3: [3, 3]. 1: [3, 3, 1]. -: pop 1 and 3, push 3 - 1 = 2, giving [3, 2]. *: pop 2 and 3, push 6, giving [6]. The result is 6, matching the infix `(6 / 2) * (3 - 1)`.
:::

:::question intermediate
Convert `a * ( b + c ) - d / e` to postfix using the shunting-yard algorithm.
:::answer
`a b c + * d e / -`. Step by step: output `a`; push `*`; push `(`; output `b`; push `+`; output `c`; at `)` pop `+` to output and discard `(`; at `-` pop `*` (higher precedence) and push `-`; output `d`; push `/` (higher than `-`, so nothing is popped); output `e`; at the end pop `/` then `-`.
:::

:::question intermediate
A recursive function on a list of length $n$ calls itself on a list one element shorter until the list is empty. Approximately how many stack frames are live at the deepest point, and what happens if $n$ is 100,000 in standard Python?
:::answer
About $n + 1$ frames are live at the deepest point, one for each pending call. Standard CPython limits the recursion depth to around 1000 by default, so for $n = 100{,}000$ the program raises `RecursionError` long before finishing. Rewriting the function with a loop (or an explicit stack) avoids the problem.
:::

:::question advanced
Implement a stack that supports `push`, `pop`, and `get_min` (return the smallest element) all in $O(1)$ time. Describe the idea and the extra space it uses.
:::answer
Keep a second stack of minimums alongside the main stack. On `push(x)`, push `x` onto the main stack and push `min(x, current_min)` onto the min stack (or just `x` if it is empty). On `pop`, pop both stacks. `get_min` returns the top of the min stack. Each operation does a constant amount of work. The min stack has the same length as the main stack, so the extra space is $O(n)$. (A space-saving variant pushes onto the min stack only when `x` is less than or equal to the current minimum, and pops it only when the popped value equals the current minimum.)
:::

## Further learning

- **Next:** *Monotonic Stacks & Parentheses* uses stacks to check bracket balance and to solve next-greater-element problems in linear time.
- **Related:** *Call Stack & Recurrence Trees* explores how recursive calls unfold on the call stack.
- **Related:** *Breadth-First Search & Depth-First Search* shows depth-first search driven by an explicit stack.
