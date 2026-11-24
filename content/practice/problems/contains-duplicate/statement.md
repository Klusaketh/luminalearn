Return `True` (`true` in JavaScript) if any value appears **at least twice** in `nums`, and `False` if every value is distinct.

### Examples

- `nums = [1, 2, 3, 1]` → `True` (1 appears twice)
- `nums = [1, 2, 3, 4]` → `False`
- `nums = []` → `False`

### Constraints

- `0 <= len(nums) <= 10^5`
- Values may be negative.

**Challenge:** sorting first gives $O(n \log n)$. Can you do it in $O(n)$ expected time?
