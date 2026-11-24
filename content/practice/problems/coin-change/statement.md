You have unlimited coins of each value in `coins`. Return the **fewest** coins that add up to exactly `amount`, or `-1` if it cannot be made.

### Examples

- `coins = [1, 2, 5]`, `amount = 11` → `3` (5 + 5 + 1)
- `coins = [2]`, `amount = 3` → `-1`
- `coins = [1]`, `amount = 0` → `0`

### Constraints

- `1 <= len(coins) <= 12`
- `0 <= amount <= 10^4`

**Watch out:** always taking the largest coin that fits (greedy) fails for coins like `[1, 3, 4]` and amount `6`.
