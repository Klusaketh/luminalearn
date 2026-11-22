Group the words in `words` that are **anagrams** of each other (the same letters in a different order).

So that the answer is unique, return the groups in this form:
- sort the words **inside each group** alphabetically, and
- sort **the groups** by their first word.

### Examples

| `words` | Result |
| :--- | :--- |
| `["eat", "tea", "tan", "ate", "nat", "bat"]` | `[["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]` |
| `[""]` | `[[""]]` |

### Constraints

- `1 <= len(words) <= 10^4`; words contain lowercase letters only.
