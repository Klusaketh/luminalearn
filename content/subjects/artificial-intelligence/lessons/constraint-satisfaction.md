---
lesson: constraint-satisfaction
title: Constraint Satisfaction Problems
summary: Constraint satisfaction problems with variables, domains, and constraints; backtracking search; variable and value ordering heuristics (MRV, degree, least constraining value); forward checking and arc consistency with AC-3; and local search with min-conflicts.
minutes: 50
type: theory
objectives:
  - Formulate problems such as map colouring, Sudoku, and scheduling as constraint satisfaction problems
  - Apply backtracking search with MRV, the degree heuristic, least-constraining-value ordering, and forward checking
  - Enforce arc consistency with AC-3 and explain when local search with min-conflicts is preferable
review: ai-draft
---
## Introduction

Many problems are not about finding a path but about finding an assignment that satisfies rules: a timetable where no teacher is in two rooms at once, a Sudoku grid, a map where neighbouring regions have different colours, a seating plan. These are **constraint satisfaction problems** (CSPs). Because their states have a known internal structure, general-purpose CSP algorithms can prune huge parts of the search space by reasoning about the constraints, solving problems far larger than blind search could handle.

**Before you start:** you should know recursion and backtracking, and search from *Problem Formulation & Uninformed Search*.

## Core theory

### Formulating a CSP

A CSP has:

- **Variables** $X_1, \dots, X_n$.
- **Domains** $D_1, \dots, D_n$: the allowed values of each variable.
- **Constraints**: which combinations of values are allowed. **Unary** constraints involve one variable, **binary** constraints two, and **global** constraints any number, such as **Alldiff** (all different).

An assignment is **consistent** if it violates no constraint and **complete** if every variable has a value; a **solution** is a complete, consistent assignment. Binary constraints can be drawn as a **constraint graph** with variables as nodes and constraints as edges. Some problems also have **soft constraints** (preferences) that solutions should satisfy where possible.

### Backtracking search

Backtracking assigns one variable at a time, checks the constraints, and undoes the most recent choice when a variable has no consistent value left. Because assignments commute (the order of assignment does not change the result), only one variable needs to be considered at each level, giving at most $d^n$ leaves for $n$ variables with $d$ values each.

### Ordering heuristics

- **Minimum remaining values (MRV):** choose the variable with the fewest legal values left. This "fail-first" choice detects dead ends early.
- **Degree heuristic:** break ties by choosing the variable involved in the most constraints with unassigned variables.
- **Least constraining value (LCV):** try first the value that rules out the fewest choices for neighbouring variables ("fail-last" for values, since we want a solution).

### Inference: forward checking and arc consistency

- **Forward checking:** after assigning $X = v$, delete $v$ (or any inconsistent value) from the domains of $X$'s unassigned neighbours; if a domain becomes empty, backtrack immediately.
- **Arc consistency:** the arc $X \to Y$ is consistent if every value of $X$ has some compatible value of $Y$. The **AC-3** algorithm keeps a queue of arcs, removes unsupported values, and re-queues arcs into any variable whose domain shrinks. Its cost is $O(cd^3)$ for $c$ binary constraints. Running it during search (maintaining arc consistency) prunes far more than forward checking.

### Local search and structure

The **min-conflicts** heuristic starts from a complete (possibly inconsistent) assignment and repeatedly changes a conflicted variable to the value with the fewest conflicts. It solves the million-queens problem in a few steps on average and is ideal for large scheduling problems, but it can get stuck on plateaus and is not complete. Tree-structured constraint graphs can be solved in $O(nd^2)$ time without backtracking.

## Worked examples

### Example 1: Colouring a map with three and four colours

Seven regions A to G are adjacent as listed in the program. The same backtracking solver runs with and without MRV plus forward checking.

```python
NEIGHBOURS = {
    "A": ["B", "C", "D"], "B": ["A", "C", "E"], "C": ["A", "B", "D", "E", "F"],
    "D": ["A", "C", "F"], "E": ["B", "C", "F", "G"], "F": ["C", "D", "E", "G"],
    "G": ["E", "F"],
}


def solve(colours, smart):
    domains = {region: list(colours) for region in NEIGHBOURS}
    calls = 0

    def backtrack(assignment, domains):
        nonlocal calls
        calls += 1
        if len(assignment) == len(NEIGHBOURS):
            return assignment
        unassigned = [r for r in NEIGHBOURS if r not in assignment]
        # MRV: choose the variable with the fewest remaining values
        var = min(unassigned, key=lambda r: len(domains[r])) if smart else unassigned[0]
        for value in domains[var]:
            if any(assignment.get(n) == value for n in NEIGHBOURS[var]):
                continue
            new_domains = dict(domains)
            new_domains[var] = [value]
            if smart:  # forward checking: remove value from unassigned neighbours
                for n in NEIGHBOURS[var]:
                    if n not in assignment:
                        new_domains[n] = [v for v in domains[n] if v != value]
                if any(not new_domains[n] for n in NEIGHBOURS[var]):
                    continue
            result = backtrack({**assignment, var: value}, new_domains)
            if result:
                return result
        return None

    return backtrack({}, domains), calls


for colours in (["red", "green", "blue"], ["red", "green", "blue", "yellow"]):
    for smart in (False, True):
        result, calls = solve(colours, smart)
        label = "MRV + forward checking" if smart else "plain backtracking"
        answer = " ".join(f"{r}={c}" for r, c in sorted(result.items())) if result else "no solution"
        print(f"{len(colours)} colours, {label:22}: {calls:2} calls -> {answer}")
```

Output:

```text
3 colours, plain backtracking    : 28 calls -> no solution
3 colours, MRV + forward checking: 22 calls -> no solution
4 colours, plain backtracking    :  8 calls -> A=red B=green C=blue D=green E=red F=yellow G=green
4 colours, MRV + forward checking:  8 calls -> A=red B=green C=blue D=green E=red F=yellow G=green
```

With three colours, backtracking exhausts every possibility and proves **no solution exists**. The reason: A, B, and C form a triangle, so they need three different colours; D touches A and C, so it must take B's colour; E touches B and C, so it must take A's colour; and F touches C, D, and E, which now use all three colours. MRV with forward checking reaches that proof with fewer calls (22 instead of 28), and on larger problems the savings grow to many orders of magnitude. With four colours, both versions find a solution immediately: seven assignments plus the initial call.

### Example 2: Arc consistency solves a puzzle without search

Variables $X$, $Y$, $Z$ each have domain $\{1, 2, 3\}$, with constraints $X < Y$ and $Y < Z$. Run AC-3:

1. Arc $X \to Y$: $X = 3$ has no larger $Y$, so remove it. $X \in \{1, 2\}$.
2. Arc $Y \to X$: $Y = 1$ has no smaller $X$, so remove it. $Y \in \{2, 3\}$.
3. Arc $Y \to Z$: $Y = 3$ has no larger $Z$, so remove it. $Y \in \{2\}$.
4. Arc $Z \to Y$: $Z$ must exceed 2, so remove 1 and 2. $Z \in \{3\}$.
5. Because $Y$ shrank, recheck $X \to Y$: $X$ must be less than 2. $X \in \{1\}$.

Every domain now has one value: $X = 1$, $Y = 2$, $Z = 3$. Constraint propagation alone solved the problem with no search at all.

## Applications

- **Timetabling and scheduling:** exams, classes, shifts, and factory jobs.
- **Configuration:** choosing compatible product options and components.
- **Puzzles:** Sudoku, crosswords, and logic puzzles.
- **Hardware and software verification:** SAT and SMT solvers are constraint solvers.
- **Resource allocation:** frequency assignment for radio transmitters is a graph-colouring CSP.

## Common mistakes

- **Treating a CSP as a generic path search.** The path to a solution does not matter, only the final assignment.
- **Confusing MRV and LCV.** MRV picks the next variable (most constrained); LCV picks the order of values (least constraining).
- **Assuming arc consistency always solves the problem.** It prunes domains but can leave several values, so search is usually still needed.
- **Forgetting to restore domains on backtracking.** Inference must be undone when an assignment is undone.
- **Expecting min-conflicts to prove unsolvability.** Local search cannot show that no solution exists.

## Revision notes

- CSP: variables, domains, constraints; solution = complete consistent assignment.
- Backtracking: assign one variable per level, undo on failure; up to $d^n$ leaves.
- MRV (fewest values, fail-first), degree heuristic (tie-breaker), LCV (value ruling out least).
- Forward checking removes values from neighbours' domains; AC-3 enforces arc consistency in $O(cd^3)$.
- Min-conflicts local search scales to huge problems but is incomplete.
- Tree-structured CSPs are solvable in $O(nd^2)$.

## Practice questions

:::question basic
Formulate Sudoku as a CSP.
:::answer
Variables: the 81 cells. Domains: $\{1, \dots, 9\}$ for empty cells and the given digit for filled cells. Constraints: 27 Alldiff constraints, one for each row, each column, and each 3×3 box.
:::

:::question basic
What does the minimum-remaining-values heuristic choose, and why is it called "fail-first"?
:::answer
It chooses the unassigned variable with the fewest legal values left. If a dead end exists, that variable is the most likely to run out of values soon, so choosing it first reveals failures early and prunes the search tree.
:::

:::question intermediate
Regions P, Q, and R are mutually adjacent, with domains {red, green, blue}. After assigning P = red, apply forward checking, then assign Q = green and apply it again.
:::answer
After P = red, red is removed from Q and R: both have {green, blue}. After Q = green, green is removed from R: R has {blue}. R's domain is not empty, so search continues, and MRV would choose R next with its single value blue.
:::

:::question intermediate
Why does backtracking search consider only one variable at each level of the search tree?
:::answer
Variable assignments are commutative: assigning A = red then B = green gives the same state as the reverse order. Branching on every variable at every level would generate $n! \cdot d^n$ leaves for the same $d^n$ assignments, so fixing one variable per level removes the redundancy.
:::

:::question advanced
Describe the min-conflicts algorithm for N-queens and explain why it works well for very large N.
:::answer
Start with one queen per column placed anywhere, typically greedily. Repeatedly pick a queen that is attacked and move it within its column to the row with the fewest conflicts, breaking ties randomly, until no queen is attacked or a step limit is reached. For large N, solutions are densely spread through the space, so a random start is usually only a few moves from one, and the number of steps barely grows with N. It cannot prove that no solution exists, and it can stall on plateaus, which random restarts help with.
:::

## Further learning

- **Next:** *Minimax & Alpha-Beta Pruning* turns to search against an opponent.
- **Related:** *Backtracking* in Data Structures & Algorithms covers the recursive technique in general.
