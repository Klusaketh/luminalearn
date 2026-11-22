`intervals` is a list of `[start, end]` pairs. Merge every group of overlapping intervals and return the result **sorted by start**.

Intervals that only touch, such as `[1, 4]` and `[4, 5]`, count as overlapping.

### Examples

| `intervals` | Result |
| :--- | :--- |
| `[[1, 3], [2, 6], [8, 10], [15, 18]]` | `[[1, 6], [8, 10], [15, 18]]` |
| `[[1, 4], [4, 5]]` | `[[1, 5]]` |
| `[[1, 4], [0, 2], [3, 5]]` | `[[0, 5]]` |

### Constraints

- `0 <= len(intervals) <= 10^4`, and `start <= end` in every interval.
