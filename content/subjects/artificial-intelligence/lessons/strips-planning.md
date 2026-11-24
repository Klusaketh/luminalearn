---
lesson: strips-planning
title: STRIPS & Forward/Backward State Search
summary: Classical planning with STRIPS and PDDL: states as sets of facts, action schemas with preconditions and add and delete lists, forward (progression) and backward (regression) state-space search, domain-independent heuristics, and the Sussman anomaly.
minutes: 40
type: theory
objectives:
  - Represent planning problems with STRIPS action schemas and compute the result of applying an action
  - Apply forward progression search and backward regression search to find plans
  - Explain domain-independent heuristics such as ignoring delete lists, and why the Sussman anomaly defeats goal-by-goal planning
review: ai-draft
---
## Introduction

A robot asked to stack blocks, a logistics system routing parcels, and a game character assembling a toolkit all need **plans**: sequences of actions that achieve goals. Planning could be treated as ordinary search, but planning problems have structure: states are collections of facts, and actions change only a few of them. **STRIPS**, introduced in 1971 for the Shakey robot at the Stanford Research Institute, exploits that structure, and its descendant **PDDL** is the standard language of today's automated planners.

**Before you start:** you should know state-space search from *Problem Formulation & Uninformed Search* and heuristics from *A\* Search & Admissible Heuristics*.

## Core theory

### Representing states and goals

Classical planning assumes a fully observable, deterministic, static, discrete world. A **state** is a set of ground facts (atoms), such as $\{On(C, A), OnTable(A), OnTable(B), Clear(C), Clear(B)\}$. Under the **closed-world assumption**, any fact not listed is false. A **goal** is a set of facts that must all hold, such as $\{On(A, B), On(B, C)\}$; any state containing them satisfies it.

### Action schemas

An action schema has parameters, **preconditions** that must hold to apply it, and **effects** split into an **add list** and a **delete list**. For the blocks world:

```text
Move(b, x, y)          move block b from block x onto block y
  PRE: On(b, x), Clear(b), Clear(y)
  ADD: On(b, y), Clear(x)
  DEL: On(b, x), Clear(y)

MoveToTable(b, x)      move block b from block x onto the table
  PRE: On(b, x), Clear(b)
  ADD: OnTable(b), Clear(x)
  DEL: On(b, x)

MoveFromTable(b, y)    move block b from the table onto block y
  PRE: OnTable(b), Clear(b), Clear(y)
  ADD: On(b, y)
  DEL: OnTable(b), Clear(y)
```

An action is **applicable** in state $s$ if its preconditions are a subset of $s$, and the new state is

$$\text{RESULT}(s, a) = (s - \text{DEL}(a)) \cup \text{ADD}(a)$$

PDDL extends this with types, negative preconditions, conditional effects, and numeric quantities.

### Forward (progression) search

Start from the initial state, apply applicable actions, and search with any algorithm until a state satisfies the goal. Forward search is simple and sound, but it can be swamped by **irrelevant actions**: in a real warehouse, thousands of actions are applicable but have nothing to do with the goal. Good heuristics are essential.

### Backward (regression) search

Start from the goal and work backwards through **relevant** actions: those that add at least one goal fact and delete none of them. Regressing goal $g$ through action $a$ gives the subgoal

$$g' = (g - \text{ADD}(a)) \cup \text{PRE}(a)$$

Search succeeds when the initial state satisfies a subgoal. Backward search considers only relevant actions, which keeps the branching factor low, but its states are sets of facts describing many possible worlds.

### Heuristics for planning

Planning heuristics come from relaxed problems, automatically derived from the action schemas:

- **Ignore preconditions:** every action is always applicable, so the estimate is roughly the number of unsatisfied goal facts.
- **Ignore delete lists:** facts once achieved are never lost. The optimal relaxed plan length $h^+$ is admissible, but computing it is NP-hard, so planners such as FF approximate it quickly (the approximation is not admissible but guides search well).
- **Planning graphs** (as in GraphPlan) estimate the level at which goals first become reachable.

Other approaches compile planning into satisfiability (**SATPlan**), build **partial-order plans** that commit to an ordering only where necessary, or use **hierarchical task networks** that refine high-level tasks into primitive actions.

### The Sussman anomaly

Goals often interact. Achieving goals one at a time in a fixed order, and never undoing a goal once achieved, can fail even on tiny problems. The classic example uses three blocks and is described below.

## Worked examples

### Example 1: Breadth-first planning in the blocks world

Initially C is on A, and A and B are on the table; the goal is A on B and B on C. For brevity, the program stores only the "on" facts and derives which blocks are clear; the table counts as always clear.

```python
from collections import deque

BLOCKS = ["A", "B", "C"]


def actions(state):
    """STRIPS-style Move(block, from, to): precondition clear(block), clear(to)."""
    on = dict(state)
    clear = [b for b in BLOCKS if b not in on.values()]
    for block in clear:
        for target in clear + ["Table"]:
            if target != block and on[block] != target:
                new = dict(on)
                new[block] = target  # delete On(block, from), add On(block, to)
                yield f"Move({block}, {on[block]}, {target})", frozenset(new.items())


def plan(initial, goal):
    frontier, seen = deque([(initial, [])]), {initial}
    while frontier:
        state, steps = frontier.popleft()
        if goal <= state:
            return steps, len(seen)
        for name, nxt in actions(state):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append((nxt, steps + [name]))


initial = frozenset({("A", "Table"), ("B", "Table"), ("C", "A")})
goal = {("A", "B"), ("B", "C")}
steps, states = plan(initial, goal)
print("initial: C on A, A and B on the table | goal: A on B and B on C")
for i, step in enumerate(steps, 1):
    print(f"  {i}. {step}")
print(f"breadth-first forward search generated {states} distinct states")

# Solving the goals one at a time (stack A on B first) gets stuck
s1, _ = plan(initial, {("A", "B")})
print("achieving On(A, B) alone:", ", ".join(s1), "-> then B must move, undoing On(A, B)")
```

Output:

```text
initial: C on A, A and B on the table | goal: A on B and B on C
  1. Move(C, A, Table)
  2. Move(B, Table, C)
  3. Move(A, Table, B)
breadth-first forward search generated 13 distinct states
achieving On(A, B) alone: Move(C, A, Table), Move(A, Table, B) -> then B must move, undoing On(A, B)
```

Forward breadth-first search finds the shortest plan: clear A by moving C to the table, put B on C, then put A on B. With three blocks there are only 13 possible arrangements, and the search generated all of them. The last line shows the **Sussman anomaly**: achieving On(A, B) first (by clearing A and stacking it on B) leaves B buried under A, so achieving On(B, C) means taking A off again and undoing the first goal. Achieving On(B, C) first also fails: putting B on C while C still sits on A builds the tower A, C, B, and freeing A means unstacking B again. Neither goal order works without interleaving steps, which is why planners must consider goals together.

### Example 2: Regression by hand

Regress the goal $g = \{On(A, B), On(B, C)\}$ using the schemas above.

1. $MoveFromTable(A, B)$ adds $On(A, B)$ and deletes nothing in $g$ (it deletes $OnTable(A)$ and $Clear(B)$). Its preconditions are $OnTable(A), Clear(A), Clear(B)$:
$$g_1 = \{On(B, C), OnTable(A), Clear(A), Clear(B)\}$$
2. $MoveFromTable(B, C)$ adds $On(B, C)$, with preconditions $OnTable(B), Clear(B), Clear(C)$:
$$g_2 = \{OnTable(A), Clear(A), Clear(B), OnTable(B), Clear(C)\}$$
3. $MoveToTable(C, A)$ adds $Clear(A)$ (and $OnTable(C)$), with preconditions $On(C, A), Clear(C)$:
$$g_3 = \{OnTable(A), Clear(B), OnTable(B), Clear(C), On(C, A)\}$$

Every fact in $g_3$ is true in the initial state, so the plan, read forwards, is MoveToTable(C, A), MoveFromTable(B, C), MoveFromTable(A, B): the same three steps found by forward search.

## Applications

- **Logistics and manufacturing:** scheduling deliveries and assembly operations.
- **Robotics:** task planning for mobile manipulators.
- **Space missions:** NASA's planners schedule spacecraft and rover activities.
- **Games:** goal-oriented action planning gives characters believable behaviour.
- **Cybersecurity:** attack-graph planning finds paths an intruder could take.

## Common mistakes

- **Forgetting the delete list.** Without it, facts such as "B is clear" stay true after something is stacked on B.
- **Regressing through actions that delete a goal fact.** Only relevant, non-conflicting actions may be used backwards.
- **Assuming goals can be achieved independently.** The Sussman anomaly shows they interact.
- **Expecting forward search to scale without heuristics.** Irrelevant actions blow up the search.
- **Confusing the closed-world state with the open goal.** States list every true fact; goals list only required facts.

## Revision notes

- STRIPS: state = set of ground facts (closed world); goal = set of facts.
- Action schema: preconditions, add list, delete list; $\text{RESULT}(s, a) = (s - \text{DEL}) \cup \text{ADD}$.
- Forward progression: from the initial state; needs heuristics because of irrelevant actions.
- Backward regression: $g' = (g - \text{ADD}(a)) \cup \text{PRE}(a)$ for relevant actions.
- Heuristics: ignore preconditions, ignore delete lists ($h^+$), planning graphs.
- Sussman anomaly: goals interact; solving them one at a time fails.

## Practice questions

:::question basic
What are the three parts of a STRIPS action schema besides its name and parameters?
:::answer
Its preconditions (facts that must hold before the action), its add list (facts that become true), and its delete list (facts that become false).
:::

:::question basic
Apply MoveToTable(C, A) to the state $\{On(C, A), OnTable(A), OnTable(B), Clear(C), Clear(B)\}$.
:::answer
The preconditions $On(C, A)$ and $Clear(C)$ hold. Delete $On(C, A)$ and add $OnTable(C)$ and $Clear(A)$, giving $\{OnTable(A), OnTable(B), OnTable(C), Clear(A), Clear(B), Clear(C)\}$: all three blocks on the table.
:::

:::question intermediate
Why is forward state-space search often inefficient for realistic planning problems?
:::answer
In each state many actions are applicable, but most are irrelevant to the goal: for example, in a warehouse with thousands of items, almost every pick-and-place action is applicable at every step. Without a good heuristic the branching factor is huge and search explores useless states; domain-independent heuristics such as ignoring delete lists make forward search practical.
:::

:::question intermediate
Describe the ignore-delete-lists heuristic and state whether it is admissible.
:::answer
It relaxes the problem by removing all delete lists, so facts never become false once achieved; the heuristic value is the length of a plan for this relaxed problem. The optimal relaxed plan length $h^+$ is admissible, since removing deletions cannot make a problem harder, but computing it is NP-hard; practical planners use fast approximations that are not admissible but are highly informative.
:::

:::question advanced
Explain the Sussman anomaly and what it shows about planning.
:::answer
Initially C is on A and B is on the table; the goal is A on B and B on C. Achieving On(A, B) first buries B, so achieving On(B, C) then requires removing A, undoing the first goal. Achieving On(B, C) first puts B on C while C still sits on A, so A cannot be freed without unstacking again. A correct plan must interleave work on the two goals: clear A, stack B on C, then stack A on B. It shows that goals cannot always be solved independently and in sequence, motivating planners that reason about all goals together, such as partial-order planners or heuristic state-space search.
:::

## Further learning

- **Next:** *Bias, Fairness & Explainability in AI* looks at the impact of AI decisions on people.
- **Related:** *A\* Search & Admissible Heuristics* explains the heuristic search that modern planners use.
