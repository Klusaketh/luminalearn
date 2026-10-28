---
lesson: graph-representations
title: Graph Representations
summary: Model relationships as graphs and store them as adjacency matrices, adjacency lists, or edge lists, choosing by density and by the operations an algorithm needs.
minutes: 45
type: theory
objectives:
  - Define graphs and their variants, including directed, weighted, simple, dense, and sparse graphs
  - Build adjacency matrix, adjacency list, and edge list representations of the same graph and convert between them
  - Compare the representations by memory use and by the cost of edge tests, neighbour iteration, and edge insertion
  - Choose a representation that suits a given algorithm and graph density
---

## Introduction

Many problems are really about relationships: which people know each other, which web pages link to which, which roads join which junctions, which tasks must finish before others can start. A **graph** captures all of them with two ingredients: a set of **vertices** (the things) and a set of **edges** (the relationships between pairs of things).

Before running any graph algorithm, you must decide how to store the graph in memory, and that decision changes the running time of everything afterwards. The same breadth-first search takes $O(n + m)$ time with one representation and $O(n^2)$ with another. This lesson defines the vocabulary of graphs and compares the three standard representations: the adjacency matrix, the adjacency list, and the edge list.

**Before you start:** you should know arrays, linked lists or dynamic arrays, and hash maps.

## Core theory

### Vocabulary

A graph $G = (V, E)$ has $n = |V|$ vertices and $m = |E|$ edges.

- In an **undirected** graph, an edge $\{u, v\}$ joins $u$ and $v$ symmetrically (friendship). In a **directed** graph, an edge $(u, v)$ goes from $u$ to $v$ (a link from one page to another).
- In a **weighted** graph, each edge has a number $w(u, v)$, such as a distance, cost, or capacity.
- The **degree** of a vertex in an undirected graph is its number of edges. In a directed graph, the **out-degree** counts edges leaving a vertex and the **in-degree** counts edges arriving.
- A **simple** graph has no self-loops (edges from a vertex to itself) and no parallel edges.
- A **path** is a sequence of vertices joined by edges; a **cycle** is a path that returns to its start. A graph is **connected** if every pair of vertices is joined by a path. A directed graph with no cycles is a **DAG** (directed acyclic graph).

Two counting facts are used constantly:

- **Handshake lemma:** in an undirected graph, the degrees add up to $2m$, because each edge contributes 1 to the degree of both of its ends.
- A simple undirected graph has at most $\binom{n}{2} = n(n-1)/2$ edges; a simple directed graph has at most $n(n-1)$.

A graph is **dense** if $m$ is close to the maximum, $\Theta(n^2)$, and **sparse** if $m$ is much smaller, often $O(n)$. Most large real graphs are sparse: a road junction meets a handful of roads, and a social network user has hundreds of friends among billions of accounts.

### The three representations

**Adjacency matrix.** An $n \times n$ array $A$ with $A[u][v] = 1$ (or the weight) if there is an edge from $u$ to $v$, and 0 (or $\infty$) otherwise. For an undirected graph, $A$ is symmetric.

**Adjacency list.** For each vertex, a list of its neighbours (with weights, if any). An undirected edge appears twice: $v$ in $u$'s list and $u$ in $v$'s list. In Python, a list of lists or a dictionary mapping each vertex to a list, set, or dictionary of neighbours.

**Edge list.** A plain list of the edges, such as $(u, v, w)$ triples. It is the natural input format and suits algorithms that process edges in bulk, such as Kruskal's minimum spanning tree algorithm and Bellman-Ford shortest paths.

### Comparing costs

| Operation | Adjacency matrix | Adjacency list | Edge list |
| :--- | :--- | :--- | :--- |
| Memory | $\Theta(n^2)$ | $\Theta(n + m)$ | $\Theta(m)$ |
| Is $(u, v)$ an edge? | $O(1)$ | $O(\deg u)$, or $O(1)$ expected with sets | $O(m)$ |
| Iterate over neighbours of $u$ | $\Theta(n)$ | $\Theta(\deg u)$ | $O(m)$ |
| Iterate over all edges | $\Theta(n^2)$ | $\Theta(n + m)$ | $\Theta(m)$ |
| Add an edge | $O(1)$ | $O(1)$ | $O(1)$ |

Most graph algorithms, including breadth-first search, depth-first search, and Dijkstra's algorithm, spend their time iterating over neighbours. Summed over all vertices, that costs $\Theta(n + m)$ with adjacency lists but $\Theta(n^2)$ with a matrix. For sparse graphs, that difference is enormous, so **adjacency lists are the default**. Matrices win for dense graphs, for algorithms that ask "is there an edge?" constantly, and for algorithms phrased in linear algebra, such as Floyd-Warshall all-pairs shortest paths.

### Other representations worth knowing

- **Adjacency sets or dictionaries** (a hash set or dictionary per vertex) keep list-like memory while giving $O(1)$ expected edge tests and deletions.
- **Compressed sparse row (CSR)** stores all neighbour lists back to back in one array, with an offsets array marking where each vertex's neighbours begin. It is compact and cache-friendly but expensive to modify, so it is used for large static graphs.
- **Implicit graphs** are never stored at all: a grid maze, a chessboard, or the states of a puzzle define each vertex's neighbours by a rule computed on demand.

### Matrix powers count walks

The adjacency matrix connects graphs to linear algebra. For an unweighted graph, the entry $(A^k)[u][v]$ equals the number of **walks** of length $k$ from $u$ to $v$ (a walk may repeat vertices). For $k = 2$, $(A^2)[u][v] = \sum_x A[u][x] \, A[x][v]$ counts the vertices $x$ that are a neighbour of $u$ and have an edge to $v$, which is exactly the number of two-step walks.

## Worked examples

### Example 1: One graph, two representations

An undirected graph with vertices 0 to 4 and edges 0-1, 0-2, 1-2, 1-3, and 3-4:

```python
n = 5
edges = [(0, 1), (0, 2), (1, 2), (1, 3), (3, 4)]

matrix = [[0] * n for _ in range(n)]
adjacency = [[] for _ in range(n)]
for u, v in edges:
    matrix[u][v] = matrix[v][u] = 1          # undirected: store both directions
    adjacency[u].append(v)
    adjacency[v].append(u)

for row in matrix:
    print(row)
for u in range(n):
    print(u, "->", adjacency[u])

degrees = [len(adjacency[u]) for u in range(n)]
print("degrees:", degrees, "sum:", sum(degrees), "edges:", len(edges))
```

Output:

```text
[0, 1, 1, 0, 0]
[1, 0, 1, 1, 0]
[1, 1, 0, 0, 0]
[0, 1, 0, 0, 1]
[0, 0, 0, 1, 0]
0 -> [1, 2]
1 -> [0, 2, 3]
2 -> [0, 1]
3 -> [1, 4]
4 -> [3]
degrees: [2, 3, 2, 2, 1] sum: 10 edges: 5
```

The matrix is symmetric because the graph is undirected, and it has 25 cells to describe 5 edges. The adjacency list stores each edge twice, 10 entries in total, which is exactly what the handshake lemma predicts: the degrees sum to $2m = 10$.

### Example 2: A directed, weighted graph

A dictionary of dictionaries is a convenient adjacency structure for weighted graphs: `graph[u][v]` is the weight of the edge from `u` to `v`.

```python
graph = {
    "A": {"B": 4, "C": 1},
    "B": {"D": 1},
    "C": {"B": 2, "D": 5},
    "D": {},
}

edge_list = [(u, v, w) for u, nbrs in graph.items() for v, w in nbrs.items()]
print(edge_list)

out_degree = {u: len(nbrs) for u, nbrs in graph.items()}
in_degree = {u: 0 for u in graph}
for _, v, _ in edge_list:
    in_degree[v] += 1
print("out:", out_degree)
print("in: ", in_degree)

reverse = {u: {} for u in graph}             # the transpose: every edge turned around
for u, v, w in edge_list:
    reverse[v][u] = w
print("reversed:", reverse)
print("weight A->C:", graph["A"].get("C"), "| edge D->A exists:", "A" in graph["D"])
```

Output:

```text
[('A', 'B', 4), ('A', 'C', 1), ('B', 'D', 1), ('C', 'B', 2), ('C', 'D', 5)]
out: {'A': 2, 'B': 1, 'C': 2, 'D': 0}
in:  {'A': 0, 'B': 2, 'C': 1, 'D': 2}
reversed: {'A': {}, 'B': {'A': 4, 'C': 2}, 'C': {'A': 1}, 'D': {'B': 1, 'C': 5}}
weight A->C: 1 | edge D->A exists: False
```

Converting to an edge list and back takes $\Theta(n + m)$ time. The in-degrees show that A is a **source** (nothing points to it) and D is a **sink** (it points to nothing). The reversed graph answers "who links to me?" efficiently, which is needed by algorithms such as Kosaraju's strongly connected components and by search engines analysing incoming links. Because every vertex maps to a dictionary, the edge test `"A" in graph["D"]` takes expected $O(1)$ time.

### Example 3: Why sparse graphs need adjacency lists

A 100 × 100 grid, where each cell is joined to the cells above, below, left, and right, resembles a small city's street network.

```python
rows = cols = 100
n = rows * cols
adjacency = [[] for _ in range(n)]
for r in range(rows):
    for c in range(cols):
        u = r * cols + c                     # number the cells row by row
        if c + 1 < cols:
            adjacency[u].append(u + 1)
            adjacency[u + 1].append(u)
        if r + 1 < rows:
            adjacency[u].append(u + cols)
            adjacency[u + cols].append(u)

m = sum(len(nbrs) for nbrs in adjacency) // 2
print("vertices:", n, "edges:", m)
print("matrix cells:", n * n)
print("list entries:", 2 * m)
print("density:", round(m / (n * (n - 1) / 2), 6))
```

Output:

```text
vertices: 10000 edges: 19800
matrix cells: 100000000
list entries: 39600
density: 0.000396
```

The graph has fewer than 0.04% of the possible edges. An adjacency matrix would need 100 million cells, 100 MB even at one byte per cell, almost all of them zeros, and every neighbour scan would read 10,000 cells to find at most 4 neighbours. The adjacency list needs 39,600 entries. Road networks, the web, and social networks are all sparse in this way, which is why graph software defaults to adjacency lists.

## Applications

- **Social networks** store each user's friends or followers as adjacency lists (or sets), because each user is connected to a tiny fraction of all users.
- **Maps and navigation** model junctions as vertices and road segments as weighted directed edges (one-way streets are directed).
- **The web graph**, with pages as vertices and links as directed edges, is the input to link-analysis algorithms such as PageRank.
- **Dependency graphs** in build tools, package managers, spreadsheets, and course prerequisites are DAGs, processed in topological order.
- **Dense problems** such as all-pairs distance tables or small complete graphs use adjacency matrices, often processed with matrix operations.

## Common mistakes

- **Adding only one direction of an undirected edge,** which makes the graph behave as if it were directed and breaks traversals.
- **Using an adjacency matrix for a large sparse graph,** which wastes $\Theta(n^2)$ memory and makes every neighbour scan cost $\Theta(n)$.
- **Testing edges with `v in adjacency[u]` on long lists,** which is $O(\deg u)$ each time; use sets when edge tests are frequent.
- **Mixing up 0-based and 1-based vertex labels** when reading input, which leaves a phantom vertex 0 or causes an index error at vertex $n$.
- **Forgetting isolated vertices** when building from an edge list: a vertex with no edges never appears in the list, so create entries for all $n$ vertices first.

## Revision notes

- $G = (V, E)$, $n$ vertices, $m$ edges. Directed or undirected, weighted or not.
- Handshake lemma: the degrees of an undirected graph sum to $2m$. Simple graphs: $m \le n(n-1)/2$ undirected, $n(n-1)$ directed.
- Adjacency matrix: $\Theta(n^2)$ memory, $O(1)$ edge test, $\Theta(n)$ to list neighbours. Best for dense graphs.
- Adjacency list: $\Theta(n + m)$ memory, $\Theta(\deg u)$ to list neighbours. The default for sparse graphs.
- Edge list: $\Theta(m)$ memory; suits algorithms that scan all edges (Kruskal, Bellman-Ford).
- Traversals cost $\Theta(n + m)$ with lists and $\Theta(n^2)$ with a matrix.
- $(A^k)[u][v]$ counts walks of length $k$ from $u$ to $v$.

## Practice questions

:::question basic
A simple undirected graph has six vertices with degrees 3, 3, 2, 2, 1, and 1. How many edges does it have?
:::answer
The degrees sum to $3 + 3 + 2 + 2 + 1 + 1 = 12$. By the handshake lemma, this equals $2m$, so the graph has $m = 6$ edges.
:::

:::question basic
What is the maximum number of edges in a simple graph with 10 vertices if it is (a) undirected and (b) directed?
:::answer
(a) Each unordered pair of distinct vertices can have one edge: $\binom{10}{2} = 45$. (b) Each ordered pair of distinct vertices can have one edge: $10 \times 9 = 90$. Self-loops are excluded in both cases because the graph is simple.
:::

:::question intermediate
Write the adjacency list and the adjacency matrix of the directed graph with vertices 0 to 3 and edges 0→1, 0→2, 2→0, and 2→3.
:::answer
Adjacency list: 0 → [1, 2], 1 → [], 2 → [0, 3], 3 → []. Adjacency matrix, rows as "from" and columns as "to": row 0 is `[0, 1, 1, 0]`, row 1 is `[0, 0, 0, 0]`, row 2 is `[1, 0, 0, 1]`, row 3 is `[0, 0, 0, 0]`. The matrix is not symmetric because the graph is directed: there is an edge 0→1 but not 1→0.
:::

:::question intermediate
A graph has one million vertices and five million edges. Estimate the memory for an adjacency matrix and for an adjacency list, and say which you would use for breadth-first search.
:::answer
A matrix has $10^{12}$ cells: even at one bit per cell that is about 125 GB, and at one byte per cell 1 TB. An adjacency list stores $n + m$ items for a directed graph, or $n + 2m$ for an undirected one, about $1.1 \times 10^7$ entries, which is tens of megabytes. Breadth-first search with the list costs $\Theta(n + m)$, about $10^7$ steps, while the matrix would cost $\Theta(n^2) = 10^{12}$ steps. Use the adjacency list.
:::

:::question intermediate
How long does it take to list every edge of a graph stored as (a) an adjacency matrix and (b) an adjacency list? Why can the answers differ so much?
:::answer
(a) $\Theta(n^2)$, because every cell must be inspected whether or not it holds an edge. (b) $\Theta(n + m)$, because each vertex's list is read once and holds only real edges. For a sparse graph with $m = O(n)$, the list takes linear time while the matrix takes quadratic time; the matrix spends almost all of its time reading zeros.
:::

:::question advanced
For the graph in Example 1, compute $(A^2)[0][3]$ and $(A^2)[1][1]$, and explain what each number counts.
:::answer
$(A^2)[0][3] = \sum_x A[0][x] A[x][3]$. Vertex 0's neighbours are 1 and 2; only 1 is adjacent to 3, so the sum is 1. It counts the one walk of length 2 from 0 to 3, namely 0, 1, 3. $(A^2)[1][1] = \sum_x A[1][x]^2$, which is the degree of vertex 1, namely 3: the walks 1, 0, 1 and 1, 2, 1 and 1, 3, 1. In general, the diagonal of $A^2$ lists the degrees of an undirected simple graph.
:::

:::question advanced
Design a representation for a graph that must support fast edge insertion, edge deletion, edge tests, and neighbour iteration. State the cost of each operation.
:::answer
Use a dictionary that maps each vertex to a hash set (or a dictionary, if edges carry weights) of its neighbours. Inserting an edge adds to one set (two for an undirected edge), deleting removes from it, and testing is a set lookup, all $O(1)$ expected time. Iterating over a vertex's neighbours takes $\Theta(\deg u)$, as with an adjacency list, and memory stays $\Theta(n + m)$, although each hash set uses more memory per entry than a plain list.
:::

## Further learning

- **Next:** *Breadth-First Search & Depth-First Search* uses adjacency lists to explore graphs in $\Theta(n + m)$ time.
- **Related:** *Hash Functions & Collision Handling* explains the hash sets that make adjacency-set edge tests constant time on average.
- **Related:** *Minimum Spanning Trees & Disjoint Sets* processes an edge list in sorted order.
