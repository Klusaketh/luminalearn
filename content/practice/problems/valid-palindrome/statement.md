Return `True` if `s` reads the same forwards and backwards once you **ignore case** and **ignore every character that is not a letter or digit**.

### Examples

| `s` | Result | Cleaned |
| :--- | :--- | :--- |
| `"A man, a plan, a canal: Panama"` | `True` | `amanaplanacanalpanama` |
| `"race a car"` | `False` | `raceacar` |
| `" "` | `True` | empty string |

### Constraints

- `0 <= len(s) <= 2 * 10^5`

**Challenge:** solve it with two pointers in $O(1)$ extra space, without building a cleaned copy.
