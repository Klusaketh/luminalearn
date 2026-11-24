For each day in `temperatures`, return how many days you must wait until a **strictly warmer** day. If no warmer day comes, use `0`.

### Examples

- `temperatures = [73, 74, 75, 71, 69, 72, 76, 73]` → `[1, 1, 4, 2, 1, 1, 0, 0]`
- `temperatures = [30, 40, 50, 60]` → `[1, 1, 1, 0]`
- `temperatures = [30, 20, 10]` → `[0, 0, 0]`

### Constraints

- `1 <= len(temperatures) <= 10^5`

**Challenge:** checking every later day is $O(n^2)$. A stack gets it to $O(n)$.
