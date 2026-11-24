function numIslands(grid) {
  const rows = grid.length, cols = rows ? grid[0].length : 0;
  const seen = new Set();
  const key = (r, c) => r * cols + c;
  let islands = 0;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] !== "1" || seen.has(key(r, c))) continue;
      islands += 1;
      const stack = [[r, c]];
      seen.add(key(r, c));
      while (stack.length) {  // flood-fill this island
        const [y, x] = stack.pop();
        for (const [ny, nx] of [[y + 1, x], [y - 1, x], [y, x + 1], [y, x - 1]]) {
          if (ny >= 0 && ny < rows && nx >= 0 && nx < cols && grid[ny][nx] === "1" && !seen.has(key(ny, nx))) {
            seen.add(key(ny, nx));
            stack.push([ny, nx]);
          }
        }
      }
    }
  }
  return islands;
}
