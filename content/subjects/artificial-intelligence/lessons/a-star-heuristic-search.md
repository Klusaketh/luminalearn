---
lesson: a-star-heuristic-search
title: A* Search & Admissible Heuristics
summary: Informed search with heuristic functions, greedy best-first search, A* search with f = g + h, admissible and consistent heuristics and why they guarantee optimal solutions, dominance between heuristics, and designing heuristics from relaxed problems.
minutes: 50
type: theory
objectives:
  - Apply greedy best-first search and A* search and explain why A* with an admissible heuristic is optimal
  - Check heuristics for admissibility and consistency and compare heuristics by dominance
  - Design heuristics from relaxed problems, using the 8-puzzle's misplaced-tiles and Manhattan-distance heuristics as models
review: ai-draft
---
## Introduction

Uninformed search explores blindly, so it wastes effort on paths that lead away from the goal. A map app does not consider driving north when your destination is south. **Informed search** uses a **heuristic**: an estimate of the remaining cost from a state to the goal. The A* algorithm combines this estimate with the cost already paid, and with a well-designed heuristic it finds optimal solutions while exploring a tiny fraction of the space. It is the standard algorithm for pathfinding in games, robotics, and navigation.

**Before you start:** you should know uniform-cost search from *Problem Formulation & Uninformed Search* and priority queues.

## Core theory

### Heuristic functions

A heuristic $h(n)$ estimates the cost of the cheapest path from node $n$ to a goal, with $h(\text{goal}) = 0$. For route finding, the straight-line distance to the destination is a natural heuristic.

### Greedy best-first search

Greedy search expands the node with the smallest $h(n)$: whatever looks closest to the goal. It is often fast, but it ignores the cost already paid, so it is **not optimal**, and in tree-like form it can loop.

### A* search

A* expands the node with the smallest

$$f(n) = g(n) + h(n)$$

where $g(n)$ is the cost from the start to $n$. So $f(n)$ estimates the cost of the cheapest solution that passes through $n$. With $h = 0$, A* is uniform-cost search.

### Admissibility and consistency

- A heuristic is **admissible** if it never overestimates: $h(n) \le h^*(n)$, the true remaining cost. With an admissible heuristic, A* tree search is **cost-optimal**: an optimal goal's $f$ value is $C^*$, while any suboptimal goal has $f > C^*$, so the optimal path is expanded first.
- A heuristic is **consistent** (monotone) if for every node $n$ and successor $n'$ via an action of cost $c$:
$$h(n) \le c(n, a, n') + h(n')$$
This is a triangle inequality. Every consistent heuristic is admissible. With consistency, $f$ never decreases along a path, so the first time A* graph search expands a state it has found the cheapest path to it.

### Comparing heuristics

If $h_2(n) \ge h_1(n)$ for every $n$ and both are admissible, $h_2$ **dominates** $h_1$, and A* with $h_2$ never expands more nodes (apart from ties). The larger an admissible heuristic, the better. The maximum of several admissible heuristics is admissible and dominates each of them.

The quality of a heuristic can be summarised by the **effective branching factor** $b^*$: the branching factor a uniform tree of depth $d$ would need to contain the $N$ nodes A* generated. Good heuristics give $b^*$ close to 1.

### Inventing heuristics with relaxed problems

The exact cost of a **relaxed problem**, one with fewer restrictions on actions, is an admissible heuristic for the original, because the relaxation only adds shortcuts. In the 8-puzzle a tile can move to an adjacent blank square:

- If a tile could move **anywhere** in one step, each misplaced tile needs one move: $h_1$ = number of **misplaced tiles**.
- If a tile could move to any **adjacent** square, even an occupied one, each tile needs its grid distance: $h_2$ = sum of **Manhattan distances**.

Since every misplaced tile is at least one square away, $h_2 \ge h_1$: Manhattan distance dominates.

A* keeps every generated node in memory, which limits it on large problems; variants such as **IDA\*** (iterative deepening on $f$) and memory-bounded A* reduce memory, and **weighted A\*** ($f = g + w \cdot h$ with $w > 1$) trades optimality for speed.

## Worked examples

### Example 1: Three searches on the 8-puzzle

The program solves the same 8-puzzle with uniform-cost search ($h = 0$), A* with misplaced tiles, and A* with Manhattan distance.

```python
import heapq

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)          # 0 is the blank


def neighbours(state):
    i = state.index(0)
    row, col = divmod(i, 3)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            j = 3 * r + c
            s = list(state)
            s[i], s[j] = s[j], s[i]
            yield tuple(s)


def h_zero(state):
    return 0


def h_misplaced(state):
    return sum(1 for i, tile in enumerate(state) if tile and tile != GOAL[i])


def h_manhattan(state):
    total = 0
    for i, tile in enumerate(state):
        if tile:
            goal_index = tile - 1
            total += abs(i // 3 - goal_index // 3) + abs(i % 3 - goal_index % 3)
    return total


def astar(start, h):
    frontier = [(h(start), 0, 0, start)]
    best_g, expanded, counter = {start: 0}, 0, 0
    while frontier:
        f, g, _, state = heapq.heappop(frontier)
        if state == GOAL:
            return g, expanded
        if g > best_g[state]:
            continue
        expanded += 1
        for nxt in neighbours(state):
            if g + 1 < best_g.get(nxt, float("inf")):
                best_g[nxt] = g + 1
                counter += 1
                heapq.heappush(frontier, (g + 1 + h(nxt), g + 1, counter, nxt))


start = (4, 1, 2, 0, 8, 7, 6, 3, 5)
print("h values of start: misplaced =", h_misplaced(start), "| manhattan =", h_manhattan(start))
for name, h in [("UCS (h = 0)", h_zero), ("A* misplaced tiles", h_misplaced), ("A* Manhattan", h_manhattan)]:
    moves, expanded = astar(start, h)
    print(f"{name:19}: solution {moves} moves, {expanded:6} nodes expanded")
```

Output:

```text
h values of start: misplaced = 8 | manhattan = 15
UCS (h = 0)        : solution 17 moves,  19963 nodes expanded
A* misplaced tiles : solution 17 moves,    883 nodes expanded
A* Manhattan       : solution 17 moves,    113 nodes expanded
```

All three find the optimal 17-move solution, because all three heuristics are admissible. The difference is effort: misplaced tiles expands about 23 times fewer nodes than uniform-cost search, and Manhattan distance about 177 times fewer. At the start, Manhattan distance estimates 15 moves against misplaced tiles' 8, much closer to the true 17, so it steers the search far more precisely.

### Example 2: Tracing A* and seeing greedy search fail

Edges: S→A cost 1, S→B cost 4, A→B cost 2, A→G cost 12, B→G cost 3. Heuristic: $h(S) = 5$, $h(A) = 4$, $h(B) = 2$, $h(G) = 0$. The true remaining costs are $h^*(S) = 6$, $h^*(A) = 5$, $h^*(B) = 3$, so $h$ is admissible (and you can check it is consistent).

| Step | Expand | New frontier entries ($f = g + h$) |
| :--- | :--- | :--- |
| 1 | S ($f = 5$) | A: $1 + 4 = 5$; B: $4 + 2 = 6$ |
| 2 | A ($f = 5$) | B via A: $3 + 2 = 5$ (better than 6); G via A: $13 + 0 = 13$ |
| 3 | B ($f = 5$) | G via B: $6 + 0 = 6$ (better than 13) |
| 4 | G ($f = 6$) | goal: path S→A→B→G, cost 6 |

A* returns the optimal cost 6. **Greedy best-first** search with the same $h$ expands S, then B (since $h(B) = 2 < h(A) = 4$), then reaches G: path S→B→G with cost 7, which is not optimal. And if the heuristic overestimated, say $h(A) = 10$, A* would rank A at $f = 11$, expand B and then G at $f = 7$ first, and also return the suboptimal cost 7: admissibility matters.

## Applications

- **Navigation:** map routing uses A* with straight-line or precomputed landmark heuristics.
- **Video games:** characters find paths across grids and navigation meshes with A*.
- **Robotics:** motion planners search configuration spaces with heuristics.
- **Puzzle solving and scheduling:** heuristics guide search in huge combinatorial spaces.
- **Natural language processing:** A*-style search decodes parses and translations.

## Common mistakes

- **Using an overestimating heuristic and expecting optimal answers.** Inadmissible heuristics can return worse solutions.
- **Using Manhattan distance when diagonal moves are allowed.** It can then overestimate; use a heuristic that matches the moves.
- **Stopping when the goal is generated.** A* must stop when the goal is expanded (removed from the frontier).
- **Forgetting memory.** A* stores every generated node, which can exhaust memory on large problems.
- **Thinking a bigger heuristic is always better.** Bigger is better only while it stays admissible.

## Revision notes

- Heuristic $h(n)$: estimated cost to the goal; $h(\text{goal}) = 0$.
- Greedy: expand lowest $h$; fast but not optimal.
- A*: expand lowest $f = g + h$; with $h = 0$ it is UCS.
- Admissible: $h \le h^*$, so A* is optimal; consistent: $h(n) \le c + h(n')$, implies admissible.
- Dominance: larger admissible heuristics expand fewer nodes; max of admissible heuristics is admissible.
- Relaxed problems give admissible heuristics: misplaced tiles and Manhattan distance for the 8-puzzle.

## Practice questions

:::question basic
A node has path cost $g = 7$ and heuristic estimate $h = 5$. What is its A* priority, and what does it mean?
:::answer
$f = g + h = 12$. It is the estimated total cost of the cheapest solution that passes through this node.
:::

:::question basic
Is straight-line distance an admissible heuristic for travel distance by road? Why?
:::answer
Yes. A straight line is the shortest possible distance between two points, so no road route can be shorter; the heuristic never overestimates.
:::

:::question intermediate
For the 8-puzzle state with rows 8 1 3 / 4 _ 2 / 7 6 5 and goal 1 2 3 / 4 5 6 / 7 8 _, compute the misplaced-tiles and Manhattan-distance heuristics.
:::answer
Misplaced tiles: 8, 1, 2, 6, and 5 are out of place, so $h_1 = 5$. Manhattan distances: tile 8 is 3 moves from its goal, tile 1 is 1, tile 2 is 2, tile 6 is 2, and tile 5 is 2, so $h_2 = 10$.
:::

:::question intermediate
Explain why Manhattan distance dominates misplaced tiles in the 8-puzzle.
:::answer
Both are admissible. Every misplaced tile is at least one square from its goal, so its Manhattan distance is at least 1, which is its contribution to the misplaced-tiles count; correctly placed tiles contribute 0 to both. So $h_2(n) \ge h_1(n)$ for every state, and A* with $h_2$ never expands more nodes.
:::

:::question advanced
Show that with a consistent heuristic, the $f$ values along any path in A* never decrease.
:::answer
Let $n'$ be a successor of $n$ reached by an action of cost $c$. Then $f(n') = g(n') + h(n') = g(n) + c + h(n')$. Consistency gives $c + h(n') \ge h(n)$, so $f(n') \ge g(n) + h(n) = f(n)$. Because $f$ never decreases, A* expands nodes in non-decreasing order of $f$, so the first expansion of any state is along a cheapest path to it.
:::

## Further learning

- **Next:** *Constraint Satisfaction Problems* exploits the structure of states for even more efficient search.
- **Related:** *Shortest Paths: Dijkstra & Bellman-Ford* in Data Structures & Algorithms covers the uninformed special case.
