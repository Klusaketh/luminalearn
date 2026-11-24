Return the minimum number of single-character operations that turn `word1` into `word2`. The operations are: **insert** a character, **delete** a character, or **replace** a character.

### Examples

- `word1 = "horse"`, `word2 = "ros"` → `3` (horse → rorse → rose → ros)
- `word1 = "intention"`, `word2 = "execution"` → `5`
- `word1 = ""`, `word2 = "abc"` → `3`

### Constraints

- `0 <= len(word1), len(word2) <= 500`, lowercase letters.

This **Levenshtein distance** powers spell checkers and fuzzy search.
