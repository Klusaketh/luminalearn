`nums` was sorted in increasing order with **distinct** values, then rotated at an unknown point: `[0, 1, 2, 4, 5, 6, 7]` might become `[4, 5, 6, 7, 0, 1, 2]`. Return the index of `target`, or `-1` if it is not present.

### Examples

- `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 0` → `4`
- `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 3` → `-1`
- `nums = [1]`, `target = 1` → `0`

### Constraints

- `1 <= len(nums) <= 5000`, values distinct.

**Challenge:** a linear scan is $O(n)$. Run in $O(\log n)$.
