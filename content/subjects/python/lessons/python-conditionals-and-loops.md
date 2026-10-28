---
lesson: conditional-branching-and-iteration
title: Conditional Branching and Iteration Mechanisms
summary: Understand Python truthy/falsy semantics, short-circuit boolean evaluation, and for-else loops.
minutes: 20
type: theory
objectives:
  - Evaluate truthiness of empty collections, zeros, and None
  - Utilize short-circuit evaluation in boolean expressions
  - Implement for-else search patterns effectively
---
# Conditional Branching and Iteration Mechanisms

## 1. Truth Value Testing (Truthy & Falsy)

In Python, every object has an inherent boolean truth value.

The following values evaluate to **Falsy**:
- Constants: `None`, `False`
- Numeric zeros: `0`, `0.0`, `0j`
- Empty sequences and collections: `""`, `()`, `[]`, `{}`, `set()`

Everything else evaluates to **Truthy** by default.

```python
users = []
if not users:
    print("No users found.")  # Idiomatic Python check instead of len(users) == 0
```

---

## 2. Short-Circuit Evaluation

Logical operators `and` and `or` use short-circuit evaluation and return the actual operand value, not just a plain boolean:
- **`A and B`**: Returns $A$ if $A$ is falsy; otherwise returns $B$.
- **`A or B`**: Returns $A$ if $A$ is truthy; otherwise returns $B$.

```python
# Provide default fallback value
display_name = user_input or "Anonymous Student"
```

---

## 3. The `for...else` Loop Construct

Python possesses a unique `else` block on loops. The `else` block executes **only if the loop completed naturally** without encountering a `break` statement:

```python
def find_prime(numbers: list[int]) -> int | None:
    for n in numbers:
        if n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1)):
            print(f"Found prime: {n}")
            break
    else:
        print("No prime number was found in the sequence.")
        return None
```

---

## 4. Key Points to Remember

- Rely on implicit truthiness testing (`if items:`) rather than comparing lengths (`if len(items) > 0:`).
- `for...else` blocks eliminate the need for boolean flag variables when searching through sequences.
