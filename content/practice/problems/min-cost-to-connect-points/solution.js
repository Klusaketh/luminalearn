function minCostConnectPoints(points) {
  const n = points.length;
  const parent = Array.from({ length: n }, (_, i) => i);
  const find = (x) => {  // union-find root with path halving
    while (parent[x] !== x) {
      parent[x] = parent[parent[x]];
      x = parent[x];
    }
    return x;
  };
  const edges = [];
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      edges.push([Math.abs(points[i][0] - points[j][0]) + Math.abs(points[i][1] - points[j][1]), i, j]);
    }
  }
  edges.sort((a, b) => a[0] - b[0]);
  let total = 0, links = 0;
  for (const [cost, i, j] of edges) {  // Kruskal: cheapest edge that joins two trees
    if (links === n - 1) break;
    const ri = find(i), rj = find(j);
    if (ri !== rj) {
      parent[ri] = rj;
      total += cost;
      links += 1;
    }
  }
  return total;
}
