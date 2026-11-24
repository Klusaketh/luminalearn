`nums` holds **distinct** integers. Return every subset (the power set), including the empty subset and `nums` itself. Write each subset with its values in **increasing order**; the subsets themselves may come in any order.

### Examples

- `nums = [1, 2, 3]` → `[[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]`
- `nums = [0]` → `[[], [0]]`

### Constraints

- `1 <= len(nums) <= 10`, values distinct.

**Count check:** a list of $n$ values has $2^n$ subsets.
