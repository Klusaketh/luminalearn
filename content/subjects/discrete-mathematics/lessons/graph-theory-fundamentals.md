---
lesson: graph-theory-fundamentals
title: Graph Theory Fundamentals
summary: Graphs and their terminology, the handshaking lemma, paths, cycles and connectivity, trees and their properties, bipartite graphs, and Euler and Hamilton paths and circuits.
minutes: 50
type: theory
objectives:
  - Use graph terminology precisely and apply the handshaking lemma to degrees and edges
  - Determine connectivity, recognise trees, and use the property that a tree with n vertices has n - 1 edges
  - Decide whether a graph has an Euler path or circuit, and explain why Hamilton circuits are harder to decide
review: ai-draft
---
## Introduction

A **graph** is a set of objects with connections between them: cities and roads, people and friendships, web pages and links, computers and cables, tasks and dependencies. Graph theory began in 1736 when Leonhard Euler showed that no walk through the city of Königsberg could cross each of its seven bridges exactly once. Today graphs model networks of every kind, and their properties decide whether routes exist, how robust a network is, and how hard a problem is to solve.

**Before you start:** you should know sets, relations, and proof by induction.

## Core theory

### Terminology

A graph $G = (V, E)$ has a set of **vertices** V and a set of **edges** E, each edge joining two vertices. In an **undirected** graph edges have no direction; in a **directed** graph (digraph) they do. A **simple** graph has no loops (edges from a vertex to itself) and no multiple edges between the same pair. Two vertices joined by an edge are **adjacent**; the **degree** $\deg(v)$ is the number of edges at $v$ (a loop counts twice). Special graphs: the **complete graph** $K_n$ (every pair adjacent, $\binom{n}{2}$ edges), the **cycle** $C_n$, and the **complete bipartite graph** $K_{m,n}$.

### The handshaking lemma

Every edge contributes 2 to the total degree, so

$$\sum_{v \in V} \deg(v) = 2|E|$$

Consequently, every graph has an **even number of odd-degree vertices**. For example, there is no group of 5 people in which each person knows exactly 3 others, since the degree sum would be 15, which is odd.

### Paths, cycles, and connectivity

A **walk** is a sequence of vertices joined by edges; a **path** repeats no vertices; a **cycle** is a closed path of length at least 3. A graph is **connected** if every pair of vertices is joined by a path; otherwise it splits into **connected components**. Breadth-first or depth-first search finds the components in $O(|V| + |E|)$ time.

### Trees

A **tree** is a connected graph with no cycles. For a graph with $n$ vertices, the following are equivalent:

- it is a tree;
- it is connected and has exactly $n - 1$ edges;
- it has no cycles and has exactly $n - 1$ edges;
- there is exactly one path between every pair of vertices.

Every tree with at least two vertices has at least two **leaves** (vertices of degree 1). A **spanning tree** of a connected graph is a subgraph that is a tree containing every vertex; it is the cheapest way to keep a network connected.

### Bipartite graphs

A graph is **bipartite** if its vertices split into two sets with every edge going between the sets, as with students and courses. A graph is bipartite **if and only if** it has no cycle of odd length. BFS can test this by 2-colouring the vertices level by level.

### Euler paths and circuits

An **Euler circuit** uses every **edge** exactly once and returns to its start; an **Euler path** uses every edge exactly once but may end elsewhere. Euler's theorem gives an easy test for a connected graph (ignoring isolated vertices):

- an Euler circuit exists if and only if **every vertex has even degree**;
- an Euler path (not a circuit) exists if and only if **exactly two vertices have odd degree**, and the path starts at one and ends at the other.

The Königsberg graph has four vertices of odd degree, so no such walk exists. Euler paths can be found in linear time (Hierholzer's algorithm).

### Hamilton paths and circuits

A **Hamilton circuit** visits every **vertex** exactly once and returns to the start. Despite the similar definition, no simple test is known: deciding whether a Hamilton circuit exists is **NP-complete**. Sufficient conditions exist, such as **Dirac's theorem**: a simple graph with $n \ge 3$ vertices in which every vertex has degree at least $n/2$ has a Hamilton circuit. The famous travelling salesperson problem asks for the cheapest Hamilton circuit.

## Worked examples

### Example 1: Degrees, connectivity, and trees in code

```python
from collections import deque

edges = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D"), ("D", "E"), ("F", "G")]
vertices = sorted({v for e in edges for v in e})
adj = {v: [] for v in vertices}
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)

degrees = {v: len(adj[v]) for v in vertices}
print(degrees, "sum =", sum(degrees.values()), "= 2 *", len(edges))
print("odd-degree vertices:", [v for v in vertices if degrees[v] % 2])

def components():
    seen, comps = set(), []
    for start in vertices:
        if start in seen:
            continue
        comp, queue = [], deque([start])
        seen.add(start)
        while queue:
            u = queue.popleft()
            comp.append(u)
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    queue.append(w)
        comps.append(sorted(comp))
    return comps

comps = components()
print("components:", comps)
for comp in comps:
    m = sum(1 for u, v in edges if u in comp)
    print(comp, "is a tree" if m == len(comp) - 1 else f"is not a tree ({m} edges, {len(comp)} vertices)")
```

Output:

```text
{'A': 2, 'B': 3, 'C': 3, 'D': 3, 'E': 1, 'F': 1, 'G': 1} sum = 14 = 2 * 7
odd-degree vertices: ['B', 'C', 'D', 'E', 'F', 'G']
components: [['A', 'B', 'C', 'D', 'E'], ['F', 'G']]
['A', 'B', 'C', 'D', 'E'] is not a tree (6 edges, 5 vertices)
['F', 'G'] is a tree
```

The degree sum, 14, is twice the number of edges, and there are six odd-degree vertices, an even number, exactly as the handshaking lemma requires. The graph has two components. The first has 6 edges on 5 vertices, one more than a tree allows, and indeed it contains the cycle A-B-C. The second, F-G, has 1 edge on 2 vertices and is a tree.

### Example 2: Applying Euler's theorem

Which of these connected graphs has an Euler circuit or path?

1. The cycle $C_6$: every vertex has degree 2, which is even, so it has an **Euler circuit** (go around the cycle).
2. $K_5$: every vertex has degree 4, so it has an **Euler circuit**.
3. $K_4$: every vertex has degree 3, so there are four odd vertices and **neither** exists.
4. A "house" shape: a square A-B-C-D plus a roof vertex E joined to A and B, with edges AB, BC, CD, DA, AE, EB. Degrees: A 3, B 3, C 2, D 2, E 2. Exactly two odd vertices, A and B, so an **Euler path** exists from A to B, for example A-E-B-A-D-C-B, and there is no Euler circuit.
5. Königsberg: land masses with degrees 5, 3, 3, 3, all odd, so no Euler path or circuit exists.

Checking the house path: it uses the edges AE, EB, BA, AD, DC, CB, which are all six edges, each exactly once.

## Applications

- **Networks and routing:** connectivity, shortest paths, and spanning trees keep networks working.
- **Scheduling:** bipartite matching assigns workers to jobs and students to slots.
- **Route planning:** Euler paths plan snow-plough and mail routes that cover every street.
- **Complexity theory:** Hamilton circuit and graph colouring are canonical NP-complete problems.

## Common mistakes

- **Confusing Euler and Hamilton.** Euler covers every edge; Hamilton visits every vertex.
- **Forgetting connectivity in Euler's theorem.** Even degrees are not enough if the graph has two separate parts with edges.
- **Counting a loop's degree as 1.** A loop adds 2 to its vertex's degree.
- **Assuming n - 1 edges means a tree.** The graph must also be connected (or acyclic).
- **Assuming a bipartite test by colouring arbitrarily.** Use BFS or DFS and check for an edge within a colour class.

## Revision notes

- $G = (V, E)$; degree = edges at a vertex; $\sum \deg(v) = 2|E|$; odd-degree vertices come in an even number.
- $K_n$ has $\binom{n}{2}$ edges.
- Connected: a path between every pair; BFS/DFS finds components in $O(|V| + |E|)$.
- Tree: connected and acyclic; $n$ vertices and $n - 1$ edges; unique paths; at least two leaves.
- Bipartite if and only if there is no odd cycle.
- Euler circuit: connected and all degrees even; Euler path: exactly two odd vertices. Hamilton: NP-complete.

## Practice questions

:::question basic
A graph has 6 vertices with degrees 1, 2, 2, 3, 3, 5. How many edges does it have?
:::answer
The degrees sum to $1 + 2 + 2 + 3 + 3 + 5 = 16$, and by the handshaking lemma this equals twice the number of edges, so there are 8 edges.
:::

:::question basic
How many edges does a tree with 25 vertices have?
:::answer
24. Every tree with $n$ vertices has exactly $n - 1$ edges.
:::

:::question intermediate
Can a simple graph have degree sequence 3, 3, 3, 1? Can it have 3, 3, 3, 3, 1?
:::answer
3, 3, 3, 1 sums to 10, which is even, but it is impossible for a simple graph: the three degree-3 vertices must each be adjacent to all other three vertices, which would give the last vertex degree 3, not 1. The sequence 3, 3, 3, 3, 1 sums to 13, which is odd, so it violates the handshaking lemma and is impossible.
:::

:::question intermediate
Does $K_{2,4}$ have an Euler circuit? Does $K_{3,3}$?
:::answer
In $K_{2,4}$ the two vertices on one side have degree 4 and the four on the other side have degree 2; all are even and the graph is connected, so it has an Euler circuit. In $K_{3,3}$ every vertex has degree 3, so all six vertices are odd and it has neither an Euler circuit nor an Euler path.
:::

:::question advanced
Prove that every tree with $n \ge 2$ vertices has at least two leaves.
:::answer
Take a longest path $v_1, v_2, \dots, v_k$ in the tree (it exists because the tree is finite, and $k \ge 2$ because the tree is connected with at least two vertices). If the endpoint $v_1$ had another neighbour $w$ besides $v_2$, then either $w$ is on the path, creating a cycle, which a tree cannot have, or $w$ is not, giving a longer path $w, v_1, \dots, v_k$, contradicting maximality. So $v_1$ has degree 1, and by the same argument so does $v_k$: the tree has at least two leaves.
:::

## Further learning

- **Next:** *Modular Arithmetic, GCD & Primes* moves from structures to number theory.
- **Related:** *Graph Representations* and *BFS and DFS Traversals* in Data Structures & Algorithms implement these ideas.
