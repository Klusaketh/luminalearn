---
lesson: functions-scope-and-closures
title: Function Signatures, Scope Resolution & First-Class Functions
summary: Master the LEGB scoping rule, *args/**kwargs parameter binding, closures, and higher-order functions.
minutes: 25
type: theory
objectives:
  - Trace variable resolution using the LEGB (Local, Enclosing, Global, Built-in) rule
  - Construct flexible signatures using *args and **kwargs
  - Build closures and understand higher-order functions
---
# Function Signatures, Scope Resolution & First-Class Functions

## 1. First-Class Functions

In Python, functions are **first-class citizens**:
- Functions can be assigned to variables.
- Functions can be passed as arguments into other functions.
- Functions can be returned from other functions.

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

say_hi = greet  # Function assigned to variable
print(say_hi("Alice"))
```

---

## 2. Variable Scope and the LEGB Rule

When Python resolves a variable name, it searches four scopes sequentially:

1. **L — Local**: Names assigned inside the current function body.
2. **E — Enclosing**: Names defined in outer enclosing functions (closures).
3. **G — Global**: Names defined at the top level of the current module.
4. **B — Built-in**: Names preloaded into Python (e.g., `len`, `range`, `print`).

If a variable is not found in any of the four scopes, a `NameError` is raised.

---

## 3. Closures and Function Factories

A **closure** occurs when a nested function retains access to variables in its enclosing scope even after the outer function has finished executing:

```python
def make_multiplier(factor: int):
    # Enclosing scope variable: factor
    def multiply(n: int) -> int:
        return n * factor  # 'factor' is captured by the closure
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # Outputs: 10
print(triple(5))  # Outputs: 15
```

---

## 4. Variadic Arguments (`*args` and `**kwargs`)

- `*args`: Collects extra positional arguments into an immutable `tuple`.
- `**kwargs`: Collects extra keyword arguments into a mutable `dict`.

```python
def configure_agent(agent_name: str, *tags: str, **settings: int | str):
    print(f"Agent: {agent_name}")
    print(f"Tags tuple: {tags}")
    print(f"Settings dict: {settings}")

configure_agent("Socrates", "ai", "tutor", temperature=0.7, max_tokens=500)
```

---

## 5. Key Points to Remember

- The LEGB rule guarantees deterministic variable lookup order from innermost to outermost scope.
- Use `global` and `nonlocal` sparingly, as mutability across scopes makes code harder to reason about and test.
- Closures form the underlying mechanics of Python **decorators**.
