---
lesson: bfs-dfs-traversals
title: Breadth-First Search and Depth-First Search
summary: Explore graphs layer by layer with a queue or path by path with a stack, and use the two searches for shortest paths, components, cycle detection, and topological sorting.
minutes: 60
type: theory
objectives:
  - Implement breadth-first search with a queue and use it to find shortest paths in unweighted graphs
  - Implement depth-first search and record the order in which vertices are discovered and finished
  - Find connected components, detect cycles in undirected and directed graphs, and compute a topological order of a DAG
  - Analyse both searches as O(n + m) with adjacency lists and choose the right one for a problem
---

## Introduction

Almost every graph algorithm starts by answering a simple question: starting from one vertex, what can I reach, and how? There are two fundamental strategies.

**Breadth-first search (BFS)** explores like a ripple in a pond. It visits the start, then every vertex one edge away, then every vertex two edges away, and so on. Because it explores in order of distance, it finds the shortest route (in number of edges) to every reachable vertex.

**Depth-first search (DFS)** explores like a person in a maze who always takes an unexplored passage and backtracks only at dead ends. It follows one path as deep as possible before trying alternatives. The order in which DFS finishes vertices reveals a graph's structure: its cycles, its components, and a valid order for tasks with dependencies.

Both searches visit each vertex and edge once, so they run in linear time. Together they are the building blocks for shortest paths, spanning trees, network flow, and much more.

**Before you start:** you should know graph representations, stacks, queues, and recursion.

## Core theory

### The visited set

Graphs, unlike trees, can contain cycles and multiple routes to the same vertex. Without care, a search would loop forever or revisit vertices many times. Both searches therefore keep a **visited** (or discovered) set and never process a vertex twice.

### Breadth-first search

1. Mark the source as visited with distance 0 and put it in a queue.
2. Repeatedly remove the vertex $u$ at the front of the queue. For each neighbour $v$ of $u$ that has not been visited, mark it visited, set $\text{dist}[v] = \text{dist}[u] + 1$ and $\text{parent}[v] = u$, and add it to the back of the queue.

The queue holds vertices in non-decreasing order of distance, with at most two distinct distances present at any time. So all vertices at distance $d$ are processed before any vertex at distance $d + 1$, and the first time BFS reaches a vertex, it has found a path with the **fewest possible edges**. The parent pointers form a **BFS tree**; following them back from any vertex gives a shortest path to the source.

Mark a vertex as visited **when it is added to the queue**, not when it is removed. Otherwise the same vertex can be queued many times before it is processed.

### Depth-first search

```text
visit(u):
    mark u visited                (u is discovered)
    for each neighbour v of u:
        if v is not visited:
            visit(v)
    (u is finished)
```

A vertex is **discovered** when the search first reaches it and **finished** when every vertex reachable from it through unvisited vertices has been explored. In a directed graph, DFS classifies each edge $(u, v)$:

- **Tree edge:** $v$ was discovered from $u$.
- **Back edge:** $v$ is an ancestor of $u$ that is still unfinished, on the current path. A back edge closes a cycle.
- **Forward edge** or **cross edge:** $v$ is already finished.

A directed graph has a cycle **if and only if** DFS finds a back edge. A common way to track this is with three colours: white (not yet discovered), grey (discovered but not finished, so on the current path), and black (finished). An edge to a grey vertex is a back edge.

### Undirected cycles and components

In an undirected graph, every edge appears in both directions, so the edge back to a vertex's own parent must not count as a cycle. A cycle exists exactly when DFS reaches an already visited vertex other than the parent.

To find **connected components**, start a new search from every vertex that is still unvisited after the previous searches. Each search marks exactly one component.

### Topological sorting

A **topological order** of a DAG lists the vertices so that every edge goes from an earlier vertex to a later one: every task appears after the tasks it depends on. One exists if and only if the graph has no directed cycle. Two standard methods:

- **DFS:** list vertices in **reverse finishing order**. When $u$ finishes, every vertex reachable from $u$ has already finished, so $u$ ends up before all of them.
- **Kahn's algorithm:** repeatedly remove a vertex with in-degree 0, output it, and decrease the in-degree of its neighbours. If vertices remain but none has in-degree 0, the graph has a cycle.

### Cost

With adjacency lists, each vertex is queued or visited once and each adjacency list is scanned once, so both searches take $\Theta(n + m)$ time and $O(n)$ extra space. With an adjacency matrix, scanning a vertex's neighbours costs $\Theta(n)$, so the searches take $\Theta(n^2)$.

| | BFS | DFS |
| :--- | :--- | :--- |
| Frontier structure | queue | stack (often the call stack) |
| Shortest paths in unweighted graphs | yes | no |
| Cycle detection and topological sort | possible (Kahn's algorithm) | natural (back edges, finishing order) |
| Memory | the widest layer | the longest path explored |

## Worked examples

### Example 1: BFS shortest paths

```python
from collections import deque

graph = {
    "A": ["B", "C"], "B": ["A", "D", "E"], "C": ["A", "F"], "D": ["B"],
    "E": ["B", "F"], "F": ["C", "E", "G"], "G": ["F"],
}

def bfs(graph, source):
    dist, parent = {source: 0}, {source: None}
    order, queue = [], deque([source])
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            if v not in dist:                # mark when discovered, not when dequeued
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.append(v)
    return order, dist, parent

def path_to(parent, target):
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return path[::-1]

order, dist, parent = bfs(graph, "A")
print("order:", " ".join(order))
print("dist: ", dist)
print("path A->G:", " -> ".join(path_to(parent, "G")))
```

Output:

```text
order: A B C D E F G
dist:  {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 2, 'G': 3}
path A->G: A -> C -> F -> G
```

The vertices come out in layers: A at distance 0; B and C at 1; D, E, and F at 2; G at 3. When E is processed, its neighbour F has already been discovered from C, so F keeps parent C. Following parents back from G gives the three-edge path through C and F; no path with fewer edges exists.

### Example 2: DFS order and connected components

```python
def dfs_all(graph):
    visited, discovered, finished, components = set(), [], [], []

    def visit(u):
        visited.add(u)
        discovered.append(u)
        for v in graph[u]:
            if v not in visited:
                visit(v)
        finished.append(u)                   # every vertex reachable from u is done

    for u in graph:
        if u not in visited:                 # a new component starts here
            start = len(discovered)
            visit(u)
            components.append(discovered[start:])
    return discovered, finished, components

graph = {
    1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3],
    5: [6], 6: [5],
    7: [],
}
discovered, finished, components = dfs_all(graph)
print("discovered:", discovered)
print("finished:  ", finished)
print("components:", components)
```

Output:

```text
discovered: [1, 2, 4, 3, 5, 6, 7]
finished:   [3, 4, 2, 1, 6, 5, 7]
components: [[1, 2, 4, 3], [5, 6], [7]]
```

From vertex 1, DFS goes to 2, then to 4, then to 3, before backtracking: it reaches 3 through the long way round rather than directly from 1. Vertex 3 finishes first because it has nowhere new to go. When DFS finally returns to 1 and looks at its neighbour 3, it is already visited, an edge to a visited vertex other than the parent, which reveals the cycle 1, 2, 4, 3. The outer loop then starts fresh searches at 5 and at 7, finding the other two components.

### Example 3: Topological order and cycle detection

Course prerequisites form a directed graph: an edge from $u$ to $v$ means $u$ must be taken before $v$.

```python
WHITE, GREY, BLACK = 0, 1, 2

def topological_order(graph):
    color = {u: WHITE for u in graph}
    order = []

    def visit(u):
        color[u] = GREY                      # on the current path
        for v in graph[u]:
            if color[v] == GREY:             # back edge: v is an unfinished ancestor
                raise ValueError(f"cycle through {u} -> {v}")
            if color[v] == WHITE:
                visit(v)
        color[u] = BLACK
        order.append(u)                      # finishing order

    for u in graph:
        if color[u] == WHITE:
            visit(u)
    return order[::-1]                       # reverse finishing order

prereqs = {
    "programming": ["data structures", "discrete math"],
    "discrete math": ["algorithms"],
    "data structures": ["algorithms", "databases"],
    "algorithms": [],
    "databases": [],
}
print(topological_order(prereqs))

prereqs["algorithms"].append("programming")  # introduce a circular requirement
try:
    topological_order(prereqs)
except ValueError as error:
    print(error)
```

Output:

```text
['programming', 'discrete math', 'data structures', 'databases', 'algorithms']
cycle through algorithms -> programming
```

The finishing order is algorithms, databases, data structures, discrete math, programming; reversed, it puts every course after all of its prerequisites. Notice that when discrete math is explored, algorithms is already black (finished), so that edge is harmless. After the circular requirement is added, the search reaches algorithms while programming is still grey, on the current path, and reports the back edge.

## Applications

- **Shortest routes in unweighted settings:** BFS finds the fewest moves in a maze or puzzle, the fewest hops in a network, and the "degrees of separation" between people in a social network.
- **Web crawlers** discover pages breadth-first from seed URLs, which reaches nearby, usually more relevant, pages first.
- **Garbage collectors** run a reachability search (the mark phase) from program roots; unreached objects are garbage.
- **Build systems and package managers** order tasks and dependencies topologically and report circular dependencies as errors.
- **Deadlock detection** looks for a cycle in a wait-for graph, and **flood fill** in image editors is a BFS or DFS over neighbouring pixels.

## Common mistakes

- **Marking vertices visited when dequeued rather than when enqueued** in BFS, which lets a vertex enter the queue several times.
- **Using DFS to find shortest paths.** The first path DFS finds is not necessarily the shortest; use BFS for unweighted graphs and Dijkstra's algorithm for non-negative weights.
- **Using the undirected cycle test on a directed graph.** In a directed graph, reaching a visited (black) vertex is not a cycle; only an edge to a grey vertex on the current path is.
- **Treating the edge back to the parent as a cycle** in an undirected graph.
- **Searching only from one vertex** when the graph may be disconnected; components, cycle checks, and topological sorts must start from every unvisited vertex.
- **Deep recursion on large graphs,** which can exceed the recursion limit; use an explicit stack for graphs with long paths.

## Revision notes

- Both searches keep a visited set and run in $\Theta(n + m)$ time with adjacency lists ($\Theta(n^2)$ with a matrix).
- BFS: queue; processes vertices in order of distance; parent pointers give shortest paths in unweighted graphs.
- DFS: recursion or a stack; records discovery and finishing order.
- Directed cycle ⇔ back edge, an edge to a grey vertex on the current path. Undirected cycle: an edge to a visited vertex that is not the parent.
- Topological order: reverse DFS finishing order, or Kahn's algorithm with in-degrees. It exists only for DAGs.
- Components: restart the search from each unvisited vertex.

## Practice questions

:::question basic
Run BFS from A on the undirected graph with edges A-B, A-C, B-D, C-D, and D-E, visiting neighbours in alphabetical order. Give the visiting order and the distance of each vertex.
:::answer
Order: A, B, C, D, E. Distances: A 0, B 1, C 1, D 2, E 3. D is discovered from B (the first of B and C to be processed), so its parent is B; C later finds D already visited. E is discovered from D at distance 3.
:::

:::question basic
Why does BFS find shortest paths in unweighted graphs but not in weighted ones?
:::answer
BFS processes vertices in order of the number of edges from the source, so it minimises the edge count. When all edges count equally, that is the path length. With weights, a path with more edges can be lighter: if A-B costs 10, and A-C and C-B cost 1 each, BFS reaches B directly with total weight 10, but the two-edge route costs 2. Weighted graphs need Dijkstra's algorithm (non-negative weights) or Bellman-Ford.
:::

:::question intermediate
Apply Kahn's algorithm to the prerequisite graph in Example 3 (before the circular requirement is added). Process tied vertices alphabetically.
:::answer
In-degrees: programming 0, data structures 1, discrete math 1, algorithms 2, databases 1. Output programming; data structures and discrete math drop to 0. Output data structures (alphabetically first); algorithms drops to 1 and databases to 0. Output databases, then discrete math, which drops algorithms to 0, then algorithms. Order: programming, data structures, databases, discrete math, algorithms. It differs from the DFS order, which shows that a DAG can have several valid topological orders.
:::

:::question intermediate
What is the time complexity of BFS on a graph stored as an adjacency matrix, and why?
:::answer
$\Theta(n^2)$. Each of the $n$ vertices is dequeued once, and finding its neighbours requires scanning its entire row of $n$ cells, whether or not they are edges. With adjacency lists, the scans cost $\deg(u)$ instead, which totals $\Theta(n + m)$.
:::

:::question intermediate
In a directed graph, DFS from A explores the edges A→B and B→C, then finds the edge A→C. Is A→C a sign of a cycle? Explain using colours.
:::answer
No. When the search returns to A and examines A→C, the vertex C is already black (finished), because it was fully explored through B. An edge to a black vertex is a forward or cross edge, which does not close a cycle. Only an edge to a grey vertex, an unfinished ancestor on the current path, is a back edge and implies a cycle.
:::

:::question advanced
Prove that if DFS on a directed graph finds no back edge, then listing the vertices in reverse finishing order gives a valid topological order.
:::answer
Take any edge $(u, v)$. We show $v$ finishes before $u$, so $u$ comes first in the reversed list. When DFS examines this edge, $u$ is grey. If $v$ is white, it is visited and finished during the exploration from $u$, before $u$ finishes. If $v$ is black, it has already finished. The remaining case, $v$ grey, would make $(u, v)$ a back edge, which we assumed does not occur. So in every case $v$ finishes before $u$, and every edge points from earlier to later in reverse finishing order.
:::

:::question advanced
A grid maze has walls, several exits, and one starting cell. Explain how to find the distance from the start to the nearest exit, and how to compute the distance from every cell to its nearest exit in a single pass.
:::answer
For the first task, run BFS from the start over open cells, with the four neighbouring open cells as edges, and stop at the first exit dequeued; BFS order guarantees it is the nearest. For the second task, use **multi-source BFS**: put all the exits in the queue at distance 0 at the beginning, then run BFS as usual. The search expands from all exits at once, so each cell is first reached from its nearest exit, and one $\Theta(n + m)$ pass labels every cell with its distance, instead of running one search per cell.
:::

## Further learning

- **Next:** *Shortest Paths: Dijkstra & Bellman-Ford* extends BFS to weighted graphs.
- **Related:** *Binary Tree Traversals* shows the same breadth-first and depth-first ideas on trees, where no visited set is needed.
- **Related:** *Backtracking* uses depth-first search over a tree of partial solutions.
