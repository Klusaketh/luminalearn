---
lesson: mst-disjoint-sets
title: Minimum Spanning Trees and Disjoint Sets
summary: Connect every vertex of a weighted graph at minimum total cost with Kruskal's and Prim's algorithms, and build the union-find structure that makes Kruskal's algorithm fast.
minutes: 60
type: theory
objectives:
  - Define spanning trees and minimum spanning trees, and state the cut and cycle properties
  - Implement a disjoint-set (union-find) structure with union by size and path compression
  - Implement and trace Kruskal's algorithm and Prim's algorithm, and compare their costs
  - Distinguish a minimum spanning tree from a shortest-path tree and apply MSTs to network design and clustering
---

## Introduction

Suppose you must connect a set of towns with fibre-optic cable. Each possible link has a cost, you want every town connected (directly or indirectly), and you want to spend as little as possible. You would never build a link that closes a loop, because removing the most expensive link on a loop keeps everything connected and saves money. So the cheapest network is a tree, and the problem is to find the **minimum spanning tree (MST)**.

Two greedy algorithms solve it exactly. **Kruskal's algorithm** (Joseph Kruskal, 1956) considers links from cheapest to most expensive and keeps every link that does not create a loop. **Prim's algorithm** (Robert Prim, 1957, with earlier work by Vojtěch Jarník) grows a single tree outward, always adding the cheapest link that reaches a new town. Kruskal's algorithm needs a fast way to ask "are these two towns already connected?", which is the job of the **disjoint-set**, or **union-find**, data structure, one of the most elegant structures in computer science.

**Before you start:** you should know graph representations, priority queues, and sorting.

## Core theory

### Spanning trees

Let $G$ be a connected, undirected, weighted graph with $n$ vertices. A **spanning tree** is a subset of edges that connects all $n$ vertices and contains no cycle. Every spanning tree has exactly $n - 1$ edges: fewer cannot connect $n$ vertices, and any more would create a cycle. A **minimum spanning tree** is a spanning tree with the smallest possible total weight. If all edge weights are distinct, the MST is unique. If the graph is not connected, the same algorithms produce a **minimum spanning forest**, one tree per component.

### Two properties that justify greed

A **cut** splits the vertices into two non-empty groups, $S$ and $V \setminus S$. An edge **crosses** the cut if it has one end in each group.

- **Cut property:** for any cut, a lightest edge crossing it belongs to some MST. (If it is the unique lightest, it belongs to every MST.)
- **Cycle property:** for any cycle, an edge that is strictly heavier than every other edge on the cycle belongs to no MST.

**Why the cut property holds** (an exchange argument). Let $e$ be a lightest edge crossing a cut, and let $T$ be an MST that does not contain $e$. Adding $e$ to $T$ creates a cycle, and that cycle must cross the cut a second time through some other edge $f$. Removing $f$ gives another spanning tree whose weight is $w(T) + w(e) - w(f) \le w(T)$, because $w(e) \le w(f)$. So that tree is also an MST, and it contains $e$.

Both algorithms below repeatedly add an edge that the cut property guarantees is safe.

### Kruskal's algorithm

1. Sort the edges by weight.
2. Start with every vertex in its own component.
3. For each edge $(u, v)$ in order: if $u$ and $v$ are in different components, add the edge and merge the two components; otherwise skip it, because it would close a cycle.
4. Stop after $n - 1$ edges have been added.

Each added edge is a lightest edge crossing the cut between its component and the rest of the graph, so it is safe. Sorting costs $O(m \log m) = O(m \log n)$, which dominates the running time when the component checks use union-find.

### Disjoint sets (union-find)

The structure maintains a partition of elements into disjoint sets, with two operations:

- `find(x)`: return a representative (the root) of the set containing `x`. Two elements are in the same set exactly when they have the same root.
- `union(a, b)`: merge the sets containing `a` and `b`.

Each set is stored as a tree of parent pointers whose root is the representative. Two improvements make the trees very shallow:

- **Union by size (or rank):** attach the root of the smaller tree under the root of the larger one, so a tree's height grows only when it at least doubles in size. On its own, this bounds the height by $\log_2 n$.
- **Path compression:** during `find`, make every node on the path point directly at the root, so later finds on those nodes take one step.

With both, any sequence of $m$ operations on $n$ elements takes $O(m \, \alpha(n))$ time, where $\alpha$ is the inverse Ackermann function, a result due to Robert Tarjan. The function $\alpha(n)$ grows so slowly that it is at most 4 for any input that could fit in a computer, so each operation is effectively constant time.

### Prim's algorithm

1. Start the tree with any vertex.
2. Repeatedly add the lightest edge that joins a tree vertex to a non-tree vertex, together with that new vertex.
3. Stop when every vertex is in the tree.

Each chosen edge is a lightest edge crossing the cut between the tree and the rest, so it is safe. With a binary heap of candidate edges (or vertices keyed by their cheapest connection), Prim's algorithm runs in $O(m \log n)$; with an adjacency matrix and an array, it runs in $O(n^2)$, which suits dense graphs.

| | Kruskal | Prim |
| :--- | :--- | :--- |
| Grows | a forest that merges into one tree | a single tree |
| Main structure | sorted edge list + union-find | priority queue + adjacency list |
| Time | $O(m \log n)$ | $O(m \log n)$ with a heap, $O(n^2)$ with an array |
| Good for | sparse graphs, edges already sorted, spanning forests | dense graphs, adjacency-list input |

### MST is not shortest paths

An MST minimises the **total** weight of the network. A shortest-path tree from a source minimises each **individual** distance from the source. They are usually different trees, and the path between two vertices inside an MST can be much longer than their shortest path in the graph.

## Worked examples

### Example 1: Union-find with union by size and path compression

```python
class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))           # every element starts as its own root
        self.size = [1] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                       # already in the same set
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                   # smaller tree goes under the larger root
        self.size[ra] += self.size[rb]
        return True

ds = DisjointSet(6)
for a, b in [(0, 1), (2, 3), (1, 3)]:
    ds.union(a, b)
print("parents:", ds.parent)
print("union(0, 2):", ds.union(0, 2))
print("3 and 0 together:", ds.find(3) == ds.find(0))
print("parents:", ds.parent)
print("number of sets:", len({ds.find(x) for x in range(6)}))
```

Output:

```text
parents: [0, 0, 0, 2, 4, 5]
union(0, 2): False
3 and 0 together: True
parents: [0, 0, 0, 0, 4, 5]
number of sets: 3
```

After the three unions, element 3 is two steps from the root: 3 points to 2, which points to 0. `union(0, 2)` returns `False` because both already have root 0. The call `find(3)` walks 3 → 2 → 0 and then compresses the path, so the second line of parents shows 3 pointing straight at 0. The six elements now form three sets: {0, 1, 2, 3}, {4}, and {5}.

### Example 2: Kruskal's algorithm

```python
def kruskal(vertices, edges):
    parent = {v: v for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]      # path halving, a simple form of compression
            x = parent[x]
        return x

    tree, total = [], 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru == rv:
            print(f"skip {u}-{v} ({w}): would form a cycle")
            continue
        parent[ru] = rv                        # merge the two components
        tree.append((u, v, w))
        total += w
        if len(tree) == len(vertices) - 1:
            break
    return tree, total

vertices = "ABCDEFG"
edges = [("A", "B", 7), ("A", "D", 5), ("B", "C", 8), ("B", "D", 9), ("B", "E", 7),
         ("C", "E", 5), ("D", "E", 15), ("D", "F", 6), ("E", "F", 8), ("E", "G", 9),
         ("F", "G", 11)]
tree, total = kruskal(vertices, edges)
print("MST:", tree)
print("total weight:", total)
```

Output:

```text
skip B-C (8): would form a cycle
skip E-F (8): would form a cycle
skip B-D (9): would form a cycle
MST: [('A', 'D', 5), ('C', 'E', 5), ('D', 'F', 6), ('A', 'B', 7), ('B', 'E', 7), ('E', 'G', 9)]
total weight: 39
```

The first five edges (A-D, C-E, D-F, A-B, B-E) all join different components; after B-E, the vertices A to F form a single component and only G is separate. The next three edges in sorted order have both ends in that component and are skipped. E-G, weight 9, connects G, giving $n - 1 = 6$ edges, and the loop stops without looking at F-G or D-E. Python's `sorted` is stable, so edges with equal weights are considered in their input order.

### Example 3: Prim's algorithm on the same graph

```python
import heapq

def prim(graph, start):
    in_tree, tree, total = {start}, [], 0
    heap = [(w, start, v) for v, w in graph[start].items()]
    heapq.heapify(heap)
    while heap and len(in_tree) < len(graph):
        w, u, v = heapq.heappop(heap)
        if v in in_tree:
            continue                           # both ends already in the tree
        in_tree.add(v)
        tree.append((u, v, w))
        total += w
        for x, wx in graph[v].items():
            if x not in in_tree:
                heapq.heappush(heap, (wx, v, x))
    return tree, total

edges = [("A", "B", 7), ("A", "D", 5), ("B", "C", 8), ("B", "D", 9), ("B", "E", 7),
         ("C", "E", 5), ("D", "E", 15), ("D", "F", 6), ("E", "F", 8), ("E", "G", 9),
         ("F", "G", 11)]
graph = {}
for u, v, w in edges:
    graph.setdefault(u, {})[v] = w
    graph.setdefault(v, {})[u] = w

tree, total = prim(graph, "A")
print(tree)
print(total)
```

Output:

```text
[('A', 'D', 5), ('D', 'F', 6), ('A', 'B', 7), ('B', 'E', 7), ('E', 'C', 5), ('E', 'G', 9)]
39
```

Prim's algorithm finds the same six edges in a different order, because it always extends one connected tree. From A it takes A-D (5), then D-F (6), the cheapest edge leaving {A, D}, then A-B (7) and B-E (7). Only once E is in the tree does the cheap edge E-C (5) become available. The total, 39, matches Kruskal's, as it must: with these weights, both algorithms find a minimum spanning tree.

## Applications

- **Network design:** laying cable, pipes, or roads to connect sites at minimum total cost is the MST problem directly.
- **Clustering:** removing the $k - 1$ heaviest edges of an MST splits the points into $k$ clusters; this is single-linkage clustering.
- **Approximation algorithms:** walking around an MST gives a tour at most twice the optimal length for the travelling salesperson problem when distances obey the triangle inequality.
- **Image segmentation:** graph-based methods treat pixels as vertices and merge regions in order of edge weight with a union-find structure, in the style of Kruskal's algorithm.
- **Union-find on its own** tracks connected components as edges arrive, for example in network connectivity monitoring, percolation simulations, and detecting equivalent variables in compilers.

## Common mistakes

- **Using union-find without union by size or rank,** which can build a tall chain and make `find` linear.
- **Comparing elements instead of roots,** such as merging when `parent[u] != parent[v]` rather than `find(u) != find(v)`.
- **Assuming the MST contains the shortest path between two vertices.** It minimises total weight, not individual distances.
- **Running Prim's or Kruskal's algorithm on a directed graph.** These algorithms are for undirected graphs; the directed analogue (minimum arborescence) needs a different algorithm.
- **Forgetting that a disconnected graph has no spanning tree.** Kruskal's algorithm then returns fewer than $n - 1$ edges, a spanning forest, and the code should check for this.

## Revision notes

- A spanning tree has $n - 1$ edges and no cycles; an MST has minimum total weight; distinct weights make it unique.
- Cut property: a lightest edge crossing any cut is safe. Cycle property: the unique heaviest edge on a cycle is in no MST.
- Kruskal: sort edges, add each edge that joins two components; $O(m \log n)$.
- Prim: grow one tree, always adding the lightest edge leaving it; $O(m \log n)$ with a heap, $O(n^2)$ with an array.
- Union-find: parent-pointer trees; union by size plus path compression gives $O(\alpha(n))$ amortized per operation.
- MST ≠ shortest-path tree.

## Practice questions

:::question basic
A connected graph has 12 vertices and 30 edges. How many edges does each of its spanning trees have, and why?
:::answer
Eleven, that is $n - 1$. A tree on $n$ vertices always has $n - 1$ edges: starting from $n$ separate vertices, each edge that joins two components reduces the number of components by one, and $n - 1$ such edges reduce $n$ components to one. Any additional edge would join two vertices that are already connected and form a cycle. The number of edges in the original graph does not matter.
:::

:::question basic
Starting from six singleton sets {0} to {5}, perform union(0, 1), union(2, 3), union(4, 5), union(1, 3). How many sets remain, and which elements does each contain?
:::answer
Three unions of distinct sets reduce six sets to three: {0, 1}, {2, 3}, {4, 5}. union(1, 3) merges {0, 1} and {2, 3}. Two sets remain: {0, 1, 2, 3} and {4, 5}.
:::

:::question intermediate
Run Kruskal's algorithm on the graph with edges A-B 1, B-C 4, A-C 3, C-D 2, B-D 5. Which edges are chosen, and what is the total weight?
:::answer
Sorted: A-B 1, C-D 2, A-C 3, B-C 4, B-D 5. Take A-B (1) and C-D (2), which join separate vertices. Take A-C (3), which joins {A, B} with {C, D}. Now all four vertices are connected with three edges, so the algorithm stops; B-C and B-D would both close cycles. The MST is {A-B, C-D, A-C} with total weight 6.
:::

:::question intermediate
Use the cut property to explain why the first edge Kruskal's algorithm adds is always safe.
:::answer
The first edge $(u, v)$ is a lightest edge in the entire graph. Consider the cut that separates $\{u\}$ from all other vertices. The edge crosses this cut, and no edge crossing it can be lighter than the lightest edge of the whole graph, so it is a lightest crossing edge. By the cut property, some MST contains it.
:::

:::question intermediate
When would you prefer Prim's algorithm with an array over Kruskal's algorithm?
:::answer
For dense graphs, where $m$ is close to $n^2$. Kruskal's algorithm must sort all $m$ edges, costing $O(m \log n) = O(n^2 \log n)$. Prim's algorithm with an adjacency matrix and an array of each vertex's cheapest connection to the tree does $n$ rounds of an $O(n)$ scan and update, $O(n^2)$ in total, with no sorting and no heap.
:::

:::question advanced
Give a small example where the path between two vertices in the MST is longer than the shortest path between them in the graph.
:::answer
Take a triangle with edges A-B 2, B-C 2, and A-C 3. The MST is {A-B, B-C}, with total weight 4, because it omits the heaviest edge. In the MST, the only route from A to C is A, B, C, which costs 4, while the direct edge A-C costs 3. The MST minimises the sum of all chosen edges, not the distance between any particular pair.
:::

:::question advanced
If every edge weight in a graph is increased by the same constant $c$, does the minimum spanning tree change? Contrast this with shortest paths.
:::answer
No. Every spanning tree has exactly $n - 1$ edges, so each tree's total weight increases by exactly $(n - 1)c$, and the ordering of trees by weight is unchanged. The same holds for any strictly increasing transformation of the weights, because Kruskal's algorithm depends only on the sorted order of the edges. Shortest paths behave differently: paths with more edges gain more weight, so adding a constant can change which path is shortest.
:::

## Further learning

- **Next:** *Binary Search & Invariants* begins the searching module, using invariants to reason about correctness.
- **Related:** *Greedy Choice & Optimal Substructure* explains when greedy algorithms such as Kruskal's and Prim's are guaranteed to be optimal.
- **Related:** *Shortest Paths: Dijkstra & Bellman-Ford* solves the different problem of minimising individual distances.
