Return the `k`-th largest value in `nums`, counting duplicates: in `[3, 3, 1]` the first and second largest are both `3`.

### Examples

- `nums = [3, 2, 1, 5, 6, 4]`, `k = 2` → `5`
- `nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]`, `k = 4` → `4`

### Constraints

- `1 <= k <= len(nums) <= 10^5`

**Challenge:** sorting costs $O(n \log n)$. A min-heap of size `k` gives $O(n \log k)$.
