function totalNQueens(n) {
  const cols = new Set(), diag = new Set(), anti = new Set();
  const place = (row) => {
    if (row === n) return 1;
    let count = 0;
    for (let col = 0; col < n; col++) {
      if (cols.has(col) || diag.has(row - col) || anti.has(row + col)) continue;
      cols.add(col); diag.add(row - col); anti.add(row + col);
      count += place(row + 1);
      cols.delete(col); diag.delete(row - col); anti.delete(row + col);  // backtrack
    }
    return count;
  };
  return place(0);
}
