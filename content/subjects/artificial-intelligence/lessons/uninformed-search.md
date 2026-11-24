---
lesson: uninformed-search
title: Problem Formulation & Uninformed Search
summary: Formulating problems as state spaces, the search tree and frontier, and the uninformed strategies breadth-first, uniform-cost, depth-first, depth-limited, and iterative deepening search, compared by completeness, optimality, time, and space.
minutes: 50
type: theory
objectives:
  - Formulate a problem with states, an initial state, actions, a transition model, a goal test, and action costs
  - Trace breadth-first, depth-first, uniform-cost, and iterative deepening search on a graph
  - Compare uninformed strategies by completeness, cost optimality, and time and space complexity in terms of b, d, and m
review: ai-draft
---
## Introduction

A goal-based agent needs to find a sequence of actions that leads to its goal: a route from home to school, a sequence of moves that solves a puzzle, a series of steps that assembles a product. **Search** algorithms explore the possible sequences systematically. **Uninformed** (blind) strategies use only the problem definition, with no extra knowledge of how close a state is to the goal. They are the foundation that informed methods such as A* build on.

**Before you start:** you should know graphs, queues and stacks, and the agent ideas from *PEAS Model & Agent Taxonomies*.

## Core theory

### Formulating a problem

A search problem is defined by:

- **States:** the possible configurations of the world, abstracted to what matters.
- **Initial state:** where the agent starts.
- **Actions:** ACTIONS(s), the actions applicable in state s.
- **Transition model:** RESULT(s, a), the state reached by doing a in s.
- **Goal test:** whether a state is a goal.
- **Action cost:** c(s, a, s'), the cost of each step.

A **solution** is a sequence of actions from the initial state to a goal; an **optimal** solution has the lowest total cost. The states and transitions form a **state-space graph**. Good **abstraction** removes irrelevant detail: route planning needs cities and roads, not the colour of the car.

### Search trees and the frontier

Search algorithms grow a **search tree** from the initial state. The **frontier** holds generated nodes waiting to be expanded; **expanding** a node generates its children. Because the same state can be reached by different paths, **graph search** keeps a **reached** (explored) set so each state is processed once. The order in which the frontier is processed defines the strategy.

### Measuring performance

- **Completeness:** does it always find a solution if one exists?
- **Cost optimality:** does it find the lowest-cost solution?
- **Time and space complexity:** measured with **b** (branching factor), **d** (depth of the shallowest solution), and **m** (maximum depth of the space).

### The strategies

- **Breadth-first search (BFS):** expands the shallowest node first using a FIFO queue. Complete when b is finite and optimal when all actions cost the same. Time and space are $O(b^d)$: memory is the real limit. BFS can test for the goal when a node is generated.
- **Uniform-cost search (UCS):** expands the node with the lowest path cost $g(n)$ using a priority queue; this is Dijkstra's algorithm. Complete and optimal when every action cost is at least some $\varepsilon > 0$, with complexity $O(b^{1 + \lfloor C^*/\varepsilon \rfloor})$, where $C^*$ is the optimal cost. It must test for the goal when a node is **expanded**, since the first path generated to the goal may not be the cheapest.
- **Depth-first search (DFS):** expands the deepest node first using a stack. Its tree-like version needs only $O(bm)$ memory, but it is not optimal and can get lost in infinite or cyclic spaces. Time is $O(b^m)$.
- **Depth-limited search:** DFS with a depth limit $\ell$, which avoids infinite descent but fails if the solution is deeper than $\ell$.
- **Iterative deepening DFS (IDDFS):** runs depth-limited search with limits 0, 1, 2, ... until a solution appears. It is complete and optimal for equal step costs, with time $O(b^d)$ and space $O(bd)$, combining the strengths of BFS and DFS. It is the preferred uninformed method when the search space is large and the solution depth unknown.
- **Bidirectional search** searches forward from the start and backward from the goal, meeting in the middle in about $O(b^{d/2})$.

## Worked examples

### Example 1: BFS, DFS, and UCS on the same map

The road map has five places, with travel times in minutes on the edges. We search from Home to School.

```python
import heapq
from collections import deque

graph = {
    "Home": {"Library": 4, "Market": 2},
    "Market": {"Home": 2, "Library": 1, "Park": 7},
    "Library": {"Home": 4, "Market": 1, "School": 5},
    "Park": {"Market": 7, "School": 1},
    "School": {"Library": 5, "Park": 1},
}


def cost(path):
    return sum(graph[a][b] for a, b in zip(path, path[1:]))


def bfs(start, goal):
    frontier, reached, expanded = deque([[start]]), {start}, 0
    while frontier:
        path = frontier.popleft()
        expanded += 1
        for nxt in graph[path[-1]]:
            if nxt == goal:
                return path + [nxt], expanded
            if nxt not in reached:
                reached.add(nxt)
                frontier.append(path + [nxt])


def dfs(start, goal):
    frontier, expanded, visited = [[start]], 0, set()
    while frontier:
        path = frontier.pop()
        if path[-1] == goal:
            return path, expanded
        if path[-1] in visited:
            continue
        visited.add(path[-1])
        expanded += 1
        for nxt in reversed(list(graph[path[-1]])):
            if nxt not in visited:
                frontier.append(path + [nxt])


def ucs(start, goal):
    frontier, best, expanded = [(0, [start])], {start: 0}, 0
    while frontier:
        g, path = heapq.heappop(frontier)
        if path[-1] == goal:
            return path, expanded
        if g > best[path[-1]]:
            continue
        expanded += 1
        for nxt, step in graph[path[-1]].items():
            if g + step < best.get(nxt, float("inf")):
                best[nxt] = g + step
                heapq.heappush(frontier, (g + step, path + [nxt]))


for name, search in [("BFS", bfs), ("DFS", dfs), ("UCS", ucs)]:
    path, expanded = search("Home", "School")
    print(f"{name}: {' -> '.join(path):47} cost {cost(path):2}, nodes expanded {expanded}")
```

Output:

```text
BFS: Home -> Library -> School                       cost  9, nodes expanded 2
DFS: Home -> Library -> Market -> Park -> School     cost 13, nodes expanded 4
UCS: Home -> Market -> Library -> School             cost  8, nodes expanded 3
```

BFS finds the path with the **fewest roads** (two), but it costs 9 minutes. DFS dives down the first branch and returns a long four-road route costing 13 minutes, even though a two-road route was already on its stack. UCS is the only one to find the **cheapest** route, 8 minutes via the Market and the Library, because it always expands the cheapest frontier path first. When step costs differ, only cost-aware search guarantees optimality.

### Example 2: Formulating and solving the water-jug puzzle

You have a 4-litre jug and a 3-litre jug, no markings, and a tap. How do you get exactly 2 litres in the 4-litre jug?

- **States:** pairs $(x, y)$ of litres in the 4-litre and 3-litre jugs.
- **Initial state:** $(0, 0)$.
- **Actions:** fill either jug, empty either jug, pour one jug into the other until the source is empty or the destination is full.
- **Goal test:** $x = 2$. **Cost:** 1 per action.

BFS explores level by level. Level 1 reaches $(4, 0)$ and $(0, 3)$; level 2 adds $(1, 3)$, $(4, 3)$, and $(3, 0)$; level 3 adds $(1, 0)$ and $(3, 3)$; level 4 adds $(0, 1)$ and $(4, 2)$; level 5 adds $(4, 1)$ and $(0, 2)$; level 6 reaches the goal. One shortest solution is:

$$(0,0) \to (0,3) \to (3,0) \to (3,3) \to (4,2) \to (0,2) \to (2,0)$$

Fill the small jug, pour it into the large one, fill the small jug again, top up the large jug (leaving 2 litres in the small one), empty the large jug, and pour the 2 litres in: six actions, and BFS proves no shorter solution exists.

## Applications

- **Route finding:** maps, network packet routing, and airline itineraries.
- **Puzzles and games:** solving sliding puzzles and finding shortest move sequences.
- **Robotics:** motion planning in discretised spaces.
- **Web crawling:** BFS explores links level by level from seed pages.
- **Software verification:** model checkers explore program states to find bugs.

## Common mistakes

- **Assuming BFS is always optimal.** It minimises the number of steps, not the total cost.
- **Forgetting the reached set.** Search on graphs with cycles can then loop or repeat work endlessly.
- **Testing the goal on generation in UCS.** This can return a costlier path; test when the node is expanded.
- **Underestimating memory.** BFS at depth 10 with $b = 10$ stores billions of nodes.
- **Including irrelevant detail in states.** It multiplies the state space without changing the solution.

## Revision notes

- Problem: states, initial state, ACTIONS, RESULT, goal test, action costs.
- Frontier holds nodes to expand; reached set avoids repeated states.
- BFS: FIFO, complete, optimal for equal costs, $O(b^d)$ time and space.
- UCS: lowest $g(n)$ first, complete and optimal for positive costs; goal test on expansion.
- DFS: LIFO, $O(bm)$ space, not optimal, may not terminate.
- IDDFS: complete, optimal for equal costs, $O(b^d)$ time, $O(bd)$ space.

## Practice questions

:::question basic
Name the components needed to formulate a search problem.
:::answer
The set of states, the initial state, the actions available in each state, the transition model (the result of each action), the goal test, and the action cost function.
:::

:::question basic
Which uninformed strategy guarantees the cheapest solution when action costs differ?
:::answer
Uniform-cost search, provided every action cost is positive. It always expands the frontier node with the lowest path cost, so the first goal it expands is reached by a cheapest path.
:::

:::question intermediate
With branching factor 10 and the shallowest goal at depth 6, how many nodes can BFS generate, and how much memory is that at 1 KB per node?
:::answer
In the worst case $10 + 10^2 + \cdots + 10^6 = 1{,}111{,}110$ nodes. At 1 KB each, that is about 1.1 GB, which shows why memory, not time, usually limits BFS.
:::

:::question intermediate
Why must uniform-cost search apply the goal test when a node is expanded rather than when it is generated?
:::answer
A goal can first be generated along an expensive path, for example a direct road of cost 10, while a cheaper path through other nodes (cost 2 + 1) is still being explored. Testing on expansion means the goal is accepted only when it is the cheapest node on the frontier, which guarantees optimality.
:::

:::question advanced
Compare the nodes generated by IDDFS and BFS for $b = 10$ and $d = 5$, and explain why the repetition is acceptable.
:::answer
IDDFS generates the nodes at depth $i$ a total of $(d - i + 1)$ times: $5 \times 10 + 4 \times 100 + 3 \times 1{,}000 + 2 \times 10{,}000 + 1 \times 100{,}000 = 123{,}450$. BFS generates $10 + 100 + 1{,}000 + 10{,}000 + 100{,}000 = 111{,}110$. The overhead is only about 11% because most nodes are at the deepest level, and in exchange IDDFS needs only $O(bd)$ memory instead of $O(b^d)$.
:::

## Further learning

- **Next:** *A\* Search & Admissible Heuristics* adds problem knowledge to search far fewer nodes.
- **Related:** *Breadth-First Search & Depth-First Search* in Data Structures & Algorithms covers the underlying graph traversals.
