Return the length of the longest **subsequence** shared by strings `a` and `b`. A subsequence keeps the original order but may skip characters: `"ace"` is a subsequence of `"abcde"`.

### Examples

- `a = "abcde"`, `b = "ace"` → `3` (`"ace"`)
- `a = "abc"`, `b = "abc"` → `3`
- `a = "abc"`, `b = "def"` → `0`

### Constraints

- `1 <= len(a), len(b) <= 1000`, lowercase letters.

This is the comparison behind `diff` tools and DNA alignment.
