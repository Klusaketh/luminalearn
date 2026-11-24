Place `n` chess queens on an `n × n` board so that no two attack each other: no two share a row, a column, or a diagonal. Return the **number** of distinct arrangements.

### Examples

- `n = 4` → `2`
- `n = 1` → `1`
- `n = 3` → `0`

### Constraints

- `1 <= n <= 9`

Trying all $\binom{n^2}{n}$ placements is hopeless even for `n = 8`. Place one queen per row and abandon a partial board as soon as it breaks a rule.
