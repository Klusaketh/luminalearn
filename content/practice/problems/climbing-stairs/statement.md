A staircase has `n` steps. Each move climbs either **1** or **2** steps. In how many distinct ways can you reach the top?

### Examples

- `n = 2` → `2` (ways: 1+1, 2)
- `n = 3` → `3` (ways: 1+1+1, 1+2, 2+1)
- `n = 4` → `5` (ways: 1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2)

### Constraints

- `1 <= n <= 45`

**Watch out:** a plain recursive solution recomputes the same subproblems and becomes far too slow for `n = 45`.
