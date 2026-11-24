A network has `n` nodes labelled `1` to `n`. Each `times[i] = [u, v, w]` is a **directed** link: a signal sent from `u` reaches `v` after `w` milliseconds. A signal starts at node `k`. Return how long it takes until **every** node has received it, or `-1` if some node never does.

### Examples

- `times = [[2, 1, 1], [2, 3, 1], [3, 4, 1]]`, `n = 4`, `k = 2` → `2`
- `times = [[1, 2, 1]]`, `n = 2`, `k = 2` → `-1` (node 1 is unreachable from 2)

### Constraints

- `1 <= n <= 100`, `1 <= len(times) <= 6000`, `0 <= w <= 100`

The answer is the **largest** shortest-path distance from `k`.
