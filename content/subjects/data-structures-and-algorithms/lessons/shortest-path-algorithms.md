---
lesson: shortest-path-algorithms
title: "Shortest Paths: Dijkstra and Bellman-Ford"
summary: Find single-source shortest paths in weighted graphs with Dijkstra's greedy algorithm for non-negative weights and Bellman-Ford for negative weights and negative-cycle detection.
minutes: 60
type: theory
objectives:
  - Define the single-source shortest-path problem and the relaxation step shared by both algorithms
  - Implement Dijkstra's algorithm with a binary heap and explain why it requires non-negative edge weights
  - Implement Bellman-Ford, explain why n - 1 rounds suffice, and use it to detect negative cycles
  - Reconstruct paths from predecessor pointers and choose the right algorithm for a given graph
---

## Introduction

Breadth-first search finds the route with the fewest edges, which is the shortest route only when every edge costs the same. Real networks are weighted: road segments have lengths and travel times, network links have latencies, and currency exchanges have rates. The **single-source shortest-path problem** asks for the cheapest path from one source vertex to every other vertex, where the cost of a path is the sum of its edge weights.

Two classic algorithms solve it. **Dijkstra's algorithm** (Edsger Dijkstra, published in 1959) greedily settles the closest unsettled vertex, one at a time, and is fast, but it requires every weight to be non-negative. **Bellman-Ford** (named after Richard Bellman and Lester Ford Jr.) is slower but handles negative weights and can detect a **negative cycle**, a loop whose total weight is negative and which makes "shortest" meaningless. Both are built on one simple operation called relaxation.

**Before you start:** you should know graph representations, breadth-first search, and priority queues.

## Core theory

### The problem

Let $G$ be a directed graph with edge weights $w(u, v)$ and a source $s$. The **shortest-path distance** $\delta(s, v)$ is the minimum total weight of a path from $s$ to $v$; it is $\infty$ if $v$ is unreachable. (An undirected edge is treated as two directed edges.)

If a cycle with negative total weight is reachable from $s$, going around it repeatedly makes paths arbitrarily cheap, so the distances to vertices reachable from the cycle are undefined. Without negative cycles, shortest paths can be taken to be **simple** (no repeated vertices), so they have at most $n - 1$ edges.

Shortest paths have **optimal substructure**: every part of a shortest path is itself a shortest path between its endpoints. If a cheaper route existed for some part, swapping it in would give a cheaper whole path.

### Relaxation

Both algorithms keep an estimate $d[v]$, initially $0$ for the source and $\infty$ for every other vertex, and a predecessor $\text{pred}[v]$. To **relax** an edge $(u, v)$ is to test whether going through $u$ improves the best known route to $v$:

```text
relax(u, v):
    if d[u] + w(u, v) < d[v]:
        d[v] = d[u] + w(u, v)
        pred[v] = u
```

Each estimate is always the weight of some real path (or $\infty$), so it can only be too high, never too low, and relaxation only ever lowers it. The algorithms differ in **which edges they relax, and in what order**.

### Dijkstra's algorithm

Keep the unsettled vertices in a min-priority queue keyed by $d$. Repeatedly remove the vertex $u$ with the smallest estimate, declare it **settled** (its estimate is final), and relax every edge leaving $u$.

**Why it is correct (non-negative weights).** Assume every vertex settled so far has its correct distance, and let $u$ be the unsettled vertex with the smallest estimate. Take a true shortest path from $s$ to $u$, and let $y$ be the first unsettled vertex on it. The vertex just before $y$ is settled, and its edge to $y$ was relaxed when it was settled, so $d[y] = \delta(s, y)$. Then

$$\delta(s, u) \ge \delta(s, y) = d[y] \ge d[u] \ge \delta(s, u).$$

The first inequality holds because the rest of the path from $y$ to $u$ has non-negative weight; the second because $u$ was chosen with the smallest estimate; the third because estimates never fall below true distances. So $d[u] = \delta(s, u)$, and settling $u$ is safe. With a negative edge, the first inequality fails: the path could become cheaper after passing $y$.

**Cost.** Each vertex is settled once and each edge relaxed once. With a binary heap and lazy deletion (push a new entry on every improvement and skip stale entries when they are popped), the running time is $O((n + m) \log n)$. With a simple array scanned for the minimum, it is $O(n^2)$, which is better for dense graphs where $m \approx n^2$. A Fibonacci heap gives $O(m + n \log n)$ in theory.

### Bellman-Ford

Relax **every** edge, and repeat for $n - 1$ rounds:

1. Set $d[s] = 0$ and $d[v] = \infty$ for every other vertex.
2. Repeat $n - 1$ times: for every edge $(u, v)$, relax it.
3. Check every edge once more. If any edge can still be relaxed, a negative cycle is reachable from $s$.

**Why $n - 1$ rounds suffice.** By induction, after round $i$ every vertex whose shortest path uses at most $i$ edges has its correct distance: the last edge of that path is relaxed during round $i$, after its other end was already correct. Simple shortest paths have at most $n - 1$ edges, so after $n - 1$ rounds all distances are correct, unless a negative cycle exists, in which case some edge can always be relaxed further.

**Cost.** $O(nm)$ time. If a full round changes nothing, the distances are final and the algorithm can stop early.

### Choosing an algorithm

| Situation | Algorithm | Time |
| :--- | :--- | :--- |
| Unweighted (or all weights equal) | BFS | $O(n + m)$ |
| Non-negative weights | Dijkstra with a binary heap | $O((n + m) \log n)$ |
| Negative weights allowed, or negative cycles must be detected | Bellman-Ford | $O(nm)$ |
| DAG, any weights | relax edges in topological order | $O(n + m)$ |
| All pairs, dense graph | Floyd-Warshall | $O(n^3)$ |

## Worked examples

### Example 1: Dijkstra with a binary heap

```python
import heapq

def dijkstra(graph, source):
    dist, pred = {source: 0}, {source: None}
    heap, settled, order = [(0, source)], set(), []
    while heap:
        d, u = heapq.heappop(heap)
        if u in settled:
            continue                          # a stale entry: u was settled earlier
        settled.add(u)
        order.append(u)
        for v, w in graph[u].items():
            if v not in settled and (v not in dist or d + w < dist[v]):
                dist[v], pred[v] = d + w, u   # relax
                heapq.heappush(heap, (d + w, v))
    return dist, pred, order

def path(pred, v):
    route = []
    while v is not None:
        route.append(v)
        v = pred[v]
    return " -> ".join(reversed(route))

graph = {
    "s": {"a": 4, "b": 1},
    "a": {"c": 1},
    "b": {"a": 2, "c": 5},
    "c": {"d": 3},
    "d": {},
}
dist, pred, order = dijkstra(graph, "s")
for v in order:
    print(v, dist[v], path(pred, v))
```

Output:

```text
s 0 s
b 1 s -> b
a 3 s -> b -> a
c 4 s -> b -> a -> c
d 7 s -> b -> a -> c -> d
```

Settling s sets the estimates a = 4 and b = 1. The closest unsettled vertex is b, and relaxing its edges improves a to 3 and sets c to 6. Settling a then improves c to 4. Each improvement pushes a new heap entry, and the old entries for a (distance 4) and c (distance 6) are skipped as stale when they are eventually popped. Vertices are settled in increasing order of distance, the defining behaviour of Dijkstra's algorithm.

### Example 2: A negative edge breaks Dijkstra; Bellman-Ford copes

```python
import heapq

def dijkstra(graph, source):
    dist, settled, heap = {source: 0}, set(), [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in settled:
            continue
        settled.add(u)
        for v, w in graph[u].items():
            if v not in settled and (v not in dist or d + w < dist[v]):
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist

def bellman_ford(graph, source):
    dist = {v: float("inf") for v in graph}
    dist[source] = 0
    edges = [(u, v, w) for u in graph for v, w in graph[u].items()]
    for _ in range(len(graph) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break                             # a quiet round: distances are final
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            raise ValueError("negative cycle reachable from the source")
    return dist

graph = {"A": {"B": 2, "C": 3}, "B": {}, "C": {"B": -2}}
print("Dijkstra:    ", dijkstra(graph, "A"))
print("Bellman-Ford:", bellman_ford(graph, "A"))
```

Output:

```text
Dijkstra:     {'A': 0, 'B': 2, 'C': 3}
Bellman-Ford: {'A': 0, 'B': 1, 'C': 3}
```

Dijkstra settles B at distance 2 before it has looked at C, because 2 is less than 3. The path A → C → B costs $3 + (-2) = 1$, but by the time C is settled, B is already final. Bellman-Ford makes no such commitment: it relaxes every edge in every round, and the edge C → B lowers B to 1. Note that there is no negative cycle here; a single negative edge is enough to break Dijkstra.

### Example 3: Detecting a negative cycle (currency arbitrage)

If exchanging currency $u$ for $v$ multiplies your money by a rate $r(u, v)$, a sequence of trades multiplies it by the product of the rates. Setting each edge weight to $-\ln r(u, v)$ turns products into sums: a cycle of trades whose rates multiply to more than 1 becomes a cycle of negative total weight. The rates below are invented for the example.

```python
import math

def has_negative_cycle(vertices, edges, source):
    dist = {v: math.inf for v in vertices}
    dist[source] = 0.0
    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return any(dist[u] + w < dist[v] for u, v, w in edges)

def check(rates):
    edges = [(u, v, -math.log(r)) for (u, v), r in rates.items()]
    product = rates[("USD", "EUR")] * rates[("EUR", "GBP")] * rates[("GBP", "USD")]
    found = has_negative_cycle(["USD", "EUR", "GBP"], edges, "USD")
    print(f"round trip multiplies money by {product:.3f}; negative cycle: {found}")

check({("USD", "EUR"): 0.90, ("EUR", "GBP"): 0.80, ("GBP", "USD"): 1.40})
check({("USD", "EUR"): 0.90, ("EUR", "GBP"): 0.80, ("GBP", "USD"): 1.35})
```

Output:

```text
round trip multiplies money by 1.008; negative cycle: True
round trip multiplies money by 0.972; negative cycle: False
```

In the first market, converting 1000 dollars around the loop returns 1008 dollars, an arbitrage opportunity, and Bellman-Ford's extra check finds an edge that can still be relaxed after $n - 1$ rounds. In the second market, the loop loses money, the weights around the cycle sum to a positive number, and the distances settle.

## Applications

- **Internet routing:** link-state protocols such as OSPF have each router run Dijkstra's algorithm over a map of the network, while distance-vector protocols such as RIP are distributed versions of Bellman-Ford.
- **Navigation systems** compute fastest routes on road graphs weighted by travel time, using Dijkstra's algorithm together with speed-ups such as A* search and precomputed shortcuts.
- **Game AI and robotics** plan movement across grids and maps with Dijkstra's algorithm and A*.
- **Finance:** negative-cycle detection on logarithmic weights detects arbitrage among exchange rates.
- **Scheduling with DAGs:** project-planning methods find the longest (critical) path in a task DAG by relaxing edges in topological order.

## Common mistakes

- **Running Dijkstra's algorithm on a graph with negative edges.** It can return wrong distances even without a negative cycle, as Example 2 shows.
- **Adding a constant to every weight to remove negatives.** This penalises paths with many edges more than paths with few edges, so it changes which path is shortest.
- **Processing stale heap entries.** With lazy deletion, skip any popped vertex that is already settled; otherwise vertices are processed repeatedly.
- **Using BFS on a weighted graph,** which minimises the number of edges rather than the total weight.
- **Running too few Bellman-Ford rounds** or omitting the final check, which misses either correct distances or negative cycles.
- **Overflow with "infinity"** in fixed-width integer languages: adding a weight to `INT_MAX` wraps around to a negative number. Skip relaxations from unreached vertices.

## Revision notes

- Relaxation: if $d[u] + w(u, v) < d[v]$, update $d[v]$ and $\text{pred}[v]$. Estimates only ever decrease and never fall below the true distance.
- Dijkstra: settle the closest unsettled vertex, relax its edges. Requires $w \ge 0$. $O((n + m) \log n)$ with a binary heap; $O(n^2)$ with an array.
- Bellman-Ford: relax all edges $n - 1$ times; an improvement in round $n$ means a reachable negative cycle. $O(nm)$.
- Shortest simple paths have at most $n - 1$ edges; after round $i$, paths with up to $i$ edges are correct.
- Paths are rebuilt by following predecessor pointers back from the target.
- BFS for unweighted graphs, topological-order relaxation for DAGs, Floyd-Warshall for all pairs in dense graphs.

## Practice questions

:::question basic
The current estimates are $d[u] = 7$ and $d[v] = 12$, and the edge $(u, v)$ has weight 3. What does relaxing the edge do? What if its weight were 6?
:::answer
With weight 3, the route through $u$ costs $7 + 3 = 10 < 12$, so relaxation sets $d[v] = 10$ and $\text{pred}[v] = u$. With weight 6, the route costs $13$, which is not better than 12, so nothing changes.
:::

:::question basic
Which algorithm would you use for (a) the fewest train changes between two stations, (b) the fastest driving route on a road network, and (c) cheapest paths in a graph where some edges are rebates with negative cost?
:::answer
(a) BFS, because each change counts equally, so the graph is effectively unweighted. (b) Dijkstra's algorithm, because travel times are non-negative. (c) Bellman-Ford, because negative weights break Dijkstra's algorithm, and Bellman-Ford can also report a negative cycle if one exists.
:::

:::question intermediate
Run Dijkstra's algorithm from A on the undirected graph with edges A-B 1, A-C 4, B-C 2, B-D 6, and C-D 3. Give the order in which vertices are settled and their final distances.
:::answer
Settle A (0): B = 1, C = 4. Settle B (1): C improves to $1 + 2 = 3$, D = $1 + 6 = 7$. Settle C (3): D improves to $3 + 3 = 6$. Settle D (6). Order: A, B, C, D, with distances 0, 1, 3, 6. The shortest path to D is A, B, C, D.
:::

:::question intermediate
Explain why Bellman-Ford needs exactly $n - 1$ rounds of relaxation in the worst case.
:::answer
In a graph without negative cycles, some shortest path to each vertex is simple and so has at most $n - 1$ edges. After round $i$, every vertex whose shortest path has at most $i$ edges is correct, because that path's last edge is relaxed in round $i$ after its start was already correct. So $n - 1$ rounds always suffice. They can be necessary: on a path graph $s, v_1, \dots, v_{n-1}$ whose edges happen to be listed in reverse order, each round fixes only one more vertex.
:::

:::question intermediate
Compare Dijkstra's algorithm with a binary heap and with an unsorted array on a dense graph with $m \approx n^2$ edges.
:::answer
With a binary heap, the cost is $O((n + m) \log n) = O(n^2 \log n)$ for a dense graph, because each of the roughly $n^2$ relaxations may push onto the heap. With an array, each of the $n$ minimum-selections scans $O(n)$ entries and each relaxation is an $O(1)$ update, so the total is $O(n^2 + m) = O(n^2)$. On dense graphs, the simple array version is asymptotically faster.
:::

:::question advanced
A graph has a negative edge but no negative cycle. A student proposes adding a large constant $c$ to every edge so that all weights are non-negative and then running Dijkstra's algorithm. Give an example where this gives the wrong answer.
:::answer
Take edges A→B with weight 1, A→C with weight 2, and C→B with weight $-2$. The shortest path from A to B is A, C, B with weight 0. Adding $c = 2$ gives weights 3, 4, and 0. Now the direct edge A→B costs 3 while A, C, B costs $4 + 0 = 4$, so the "shortest" path has changed. A path with $k$ edges gains $kc$, so paths with more edges are penalised more. (Johnson's algorithm reweights edges correctly using vertex potentials computed by Bellman-Ford.)
:::

:::question advanced
Show how to find single-source shortest paths in a DAG with arbitrary (possibly negative) weights in $O(n + m)$ time, and explain why it is correct.
:::answer
Compute a topological order, then process the vertices in that order, relaxing every edge leaving each vertex. Correctness: when a vertex $u$ is processed, every edge into $u$ comes from a vertex earlier in the order, which has already been processed, so every path into $u$ has had all its edges relaxed in order and $d[u]$ is final. Negative weights cause no trouble, because a DAG has no cycles at all. Topological sorting is $O(n + m)$, and each edge is relaxed once, so the total is $O(n + m)$.
:::

## Further learning

- **Next:** *Minimum Spanning Trees & Disjoint Sets* uses a similar greedy idea to connect all vertices as cheaply as possible.
- **Related:** *Priority Queues Overview* explains the heap and lazy deletion used by Dijkstra's algorithm.
- **Related:** *Memoization vs Tabulation* shows that Bellman-Ford is a dynamic programming algorithm over the number of edges used.
