Return the largest sum of any **non-empty contiguous** run of elements in `nums`.

### Examples

- `nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]` → `6` (best run: `[4, -1, 2, 1]`)
- `nums = [1]` → `1` (best run: `[1]`)
- `nums = [-3, -1, -2]` → `-1` (best run: `[-1]`)

### Constraints

- `1 <= len(nums) <= 10^5`

**Challenge:** checking every run is $O(n^2)$. Find an $O(n)$ solution.
