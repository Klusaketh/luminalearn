---
lesson: python-memory-model-dynamic-typing
title: Python Memory Model, Dynamic Typing & Primitive Types
summary: Explore Python's object model, reference counts, mutability differences, and primitive types.
minutes: 20
type: theory
objectives:
  - Explain Python's 'everything is an object' paradigm and PyObject memory headers
  - Differentiate mutable collections from immutable primitives
  - Predict variable assignment behavior using identity checks (`id()` and `is`)
---
# Python Memory Model, Dynamic Typing & Primitive Types

## 1. Everything is an Object

In Python, variables do not hold values directly. Instead, variables are **names (pointers/references)** bound to objects residing on the heap.

Every Python object contains a C-level header structure (`PyObject`) storing:
1. **Reference count**: Number of active variables pointing to this object.
2. **Type pointer (`ob_type`)**: Pointer to the object's type descriptor (e.g., `<class 'int'>`).
3. **Value / payload**: The actual data stored.

```python
x = 42
# 'x' is simply a name bound to an integer object with value 42.
```

---

## 2. Mutability vs Immutability

Python data types fall strictly into two categories:

| Category | Types | Behavior |
| :--- | :--- | :--- |
| **Immutable** | `int`, `float`, `bool`, `str`, `tuple`, `frozenset` | Value cannot be modified in-place; modifications create a new object |
| **Mutable** | `list`, `dict`, `set`, custom user classes | Value can be altered in-place without changing object identity |

### Mutability Pitfall Example:
```python
# Immutable strings
s = "lumina"
s_id_before = id(s)
s += "learn"
s_id_after = id(s)
print(s_id_before == s_id_after)  # False: A new string object was created

# Mutable lists
lst = [1, 2, 3]
lst_id_before = id(lst)
lst.append(4)
lst_id_after = id(lst)
print(lst_id_before == lst_id_after)  # True: Mutated in-place
```

---

## 3. The `==` vs `is` Operator

- **`==` (Value Equality)**: Evaluates whether two objects contain the same data by invoking `__eq__()`.
- **`is` (Identity Equality)**: Evaluates whether two references point to the exact same physical memory address (`id(a) == id(b)`).

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)  # True: Same values
print(a is b)  # False: Different heap allocations
```

---

## 4. Key Points to Remember

- Python uses **dynamic typing**: variable types are checked at runtime, not compile-time.
- Integers, floats, strings, and tuples are immutable; modifying them always allocates a new object in memory.
- Default mutable argument values in functions (e.g., `def fn(items=[]):`) persist across invocations and should be avoided.
