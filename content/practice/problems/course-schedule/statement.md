There are `num_courses` courses labelled `0` to `num_courses - 1`. Each pair `[a, b]` in `prerequisites` means you must finish course `b` before course `a`. Return `True` if you can finish every course, and `False` otherwise.

### Examples

- `num_courses = 2`, `prerequisites = [[1, 0]]` → `True` (take 0, then 1)
- `num_courses = 2`, `prerequisites = [[1, 0], [0, 1]]` → `False` (each waits for the other)

### Constraints

- `1 <= num_courses <= 2000`
- `0 <= len(prerequisites) <= 5000`

**Think of it as a graph:** courses are vertices and prerequisites are directed edges. When is an ordering impossible?
