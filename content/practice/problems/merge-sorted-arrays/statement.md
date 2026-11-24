`a` and `b` are each sorted in non-decreasing order. Return **one** sorted list containing every value from both, including duplicates.

### Examples

- `a = [1, 3, 5]`, `b = [2, 4, 6]` → `[1, 2, 3, 4, 5, 6]`
- `a = []`, `b = [0]` → `[0]`
- `a = [1, 1]`, `b = [1]` → `[1, 1, 1]`

### Constraints

- `0 <= len(a), len(b) <= 10^4`

**Challenge:** do not call a sort function. This merge step is the heart of merge sort and runs in $O(n + m)$.
