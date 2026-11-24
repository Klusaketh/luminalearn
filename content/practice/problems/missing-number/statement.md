`nums` holds `n` **distinct** numbers taken from the range `0` to `n` (inclusive), so exactly one number in that range is missing. Return it.

### Examples

- `nums = [3, 0, 1]` → `2` (n = 3, range 0..3)
- `nums = [0, 1]` → `2`
- `nums = [9, 6, 4, 2, 3, 5, 7, 0, 1]` → `8`

### Constraints

- `1 <= len(nums) <= 10^4`
- All values are distinct and lie in `0..n`.

**Challenge:** a set uses $O(n)$ extra memory. Can you find it with $O(1)$ extra space?
