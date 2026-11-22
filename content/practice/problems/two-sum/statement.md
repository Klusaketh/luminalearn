Given a list of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`.

Exactly one pair adds up to the target, and you may not use the same element twice. Return the two indices **in increasing order**.

### Examples

- `nums = [2, 7, 11, 15]`, `target = 9` → `[0, 1]` (2 + 7 = 9)
- `nums = [3, 2, 4]`, `target = 6` → `[1, 2]` (2 + 4 = 6)
- `nums = [3, 3]`, `target = 6` → `[0, 1]` (The same value may appear twice)

### Constraints

- `2 <= len(nums) <= 10^4`
- Exactly one valid answer exists.

**Challenge:** a nested loop checks every pair in $O(n^2)$ time. Can you do it in one pass, $O(n)$?
