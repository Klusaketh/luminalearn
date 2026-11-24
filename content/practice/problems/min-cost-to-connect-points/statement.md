`points[i] = [x, y]` is a point on a grid. Connecting two points costs their **Manhattan distance** $|x_1 - x_2| + |y_1 - y_2|$. Return the minimum total cost to connect all points so that every pair is joined by some path.

### Examples

- `points = [[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]` → `20`
- `points = [[3, 12], [-2, 5], [-4, 1]]` → `18`
- `points = [[0, 0]]` → `0`

### Constraints

- `1 <= len(points) <= 1000`

This is a **minimum spanning tree** problem on a complete graph.
