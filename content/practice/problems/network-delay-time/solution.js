function networkDelayTime(times, n, k) {
  const graph = Array.from({ length: n + 1 }, () => []);
  for (const [u, v, w] of times) graph[u].push([v, w]);
  // n <= 100, so picking the earliest unsettled node by a linear scan is fast enough (O(n^2) Dijkstra).
  const dist = new Array(n + 1).fill(Infinity);
  const settled = new Array(n + 1).fill(false);
  dist[k] = 0;
  for (let round = 0; round < n; round++) {
    let node = -1;
    for (let v = 1; v <= n; v++) if (!settled[v] && (node === -1 || dist[v] < dist[node])) node = v;
    if (dist[node] === Infinity) break;
    settled[node] = true;
    for (const [next, w] of graph[node]) dist[next] = Math.min(dist[next], dist[node] + w);
  }
  const worst = Math.max(...dist.slice(1));
  return worst === Infinity ? -1 : worst;
}
