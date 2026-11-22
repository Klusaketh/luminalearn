`grid` is a map of `"1"` (land) and `"0"` (water). An **island** is a group of land cells connected **horizontally or vertically** (not diagonally). Return the number of islands.

### Example

```text
1 1 0 0 0
1 1 0 0 0
0 0 1 0 0
0 0 0 1 1
```

This grid has **3** islands: the 2×2 block at the top left, the single cell in the middle, and the pair at the bottom right.

### Constraints

- `0 <=` rows, columns `<= 300`
- Each cell is the string `"1"` or `"0"`.
