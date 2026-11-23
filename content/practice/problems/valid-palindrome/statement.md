Return `True` if `s` reads the same forwards and backwards once you **ignore case** and **ignore every character that is not a letter or digit**.

### Examples

- `s = "A man, a plan, a canal: Panama"` → `True` (cleaned: `amanaplanacanalpanama`)
- `s = "race a car"` → `False` (cleaned: `raceacar`)
- `s = " "` → `True` (cleaned: empty string)

### Constraints

- `0 <= len(s) <= 2 * 10^5`

**Challenge:** solve it with two pointers in $O(1)$ extra space, without building a cleaned copy.
