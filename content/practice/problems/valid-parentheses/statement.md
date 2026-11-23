Given a string `s` containing only the characters `()[]{}`, return `True` if the brackets are balanced and `False` otherwise.

A string is balanced when every opening bracket is closed by the **same type** of bracket, and brackets close **in the correct order**. The empty string is balanced.

### Examples

- `s = "()[]{}"` → `True`
- `s = "([{}])"` → `True`
- `s = "(]"` → `False`
- `s = "([)]"` → `False`

### Constraints

- `0 <= len(s) <= 10^4`
