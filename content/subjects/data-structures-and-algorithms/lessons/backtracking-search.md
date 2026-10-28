---
lesson: backtracking-search
title: Backtracking
summary: Build solutions one choice at a time, undo choices that lead nowhere, and prune the search tree early; applied to subsets, permutations, combination sums, and N-Queens.
minutes: 50
type: theory
objectives:
  - Describe backtracking as depth-first search over a tree of partial solutions using choose, explore, and unchoose steps
  - Generate all subsets, permutations, and combinations, and count the size of each search space
  - Solve constraint problems such as N-Queens with pruning and measure how much pruning saves
  - Estimate the cost of a backtracking algorithm and recognise when a different technique is needed
---

## Introduction

Some problems ask for every arrangement that satisfies a set of rules, or for one arrangement among an astronomically large number of possibilities: place eight queens on a chessboard so that none attacks another, fill in a Sudoku grid, choose items that add up to an exact total, or schedule exams so that no student has two at once. There is often no clever formula. We have to search.

Generating every complete candidate and testing it is called **brute force**, and it is usually hopeless: there are $8^8 = 16{,}777{,}216$ ways to put one queen in each row of a chessboard. **Backtracking** is a smarter search. It builds a solution one decision at a time and checks the rules after every decision. As soon as a partial solution breaks a rule, it abandons that whole branch, undoes the last decision, and tries the next alternative. For the eight queens, backtracking examines only about two thousand partial placements to find all 92 solutions.

**Before you start:** you should know recursion, the call stack, and depth-first search.

## Core theory

### The state-space tree

Picture every partial solution as a node in a tree:

- the **root** is the empty partial solution;
- each **edge** is one decision (include this item, place a queen in this column);
- the **leaves** at full depth are complete candidates.

Backtracking is a **depth-first search** of this tree. Because the tree is explored depth-first, only the current path is in memory, so the space used is proportional to the depth, not to the size of the tree.

### The template

```text
backtrack(partial):
    if partial is a complete solution:
        record it
        return
    for each choice available at this point:
        if the choice keeps partial valid:      # pruning
            make the choice                     # choose
            backtrack(partial)                  # explore
            undo the choice                     # unchoose
```

The **unchoose** step restores the state exactly as it was before the choice, so that the next choice starts from the same partial solution. Forgetting it is the most common backtracking bug.

### Sizes of common search spaces

| Problem | Decisions | Leaves of the full tree |
| :--- | :--- | :--- |
| All subsets of $n$ items | include or exclude each item | $2^n$ |
| All permutations of $n$ items | which unused item goes next | $n!$ |
| Combinations of $k$ from $n$ | which items, in increasing order | $\binom{n}{k}$ |
| One queen per row on an $n \times n$ board | which column in each row | $n^n$ |

These numbers grow explosively: $2^{30}$ is about a billion and $15!$ is over a trillion. Backtracking is practical only when **pruning** cuts away most of the tree, or when the output itself is that large and must be listed anyway.

### Pruning

- **Feasibility pruning:** stop as soon as a partial solution violates a constraint. Two queens in the same column already guarantee failure, however the remaining rows are filled.
- **Bound pruning (branch and bound):** in optimisation problems, stop when even the best possible completion of the partial solution cannot beat the best solution found so far.
- **Ordering:** sort the candidates or choose the most constrained decision first (in Sudoku, the cell with the fewest legal digits). Good ordering makes failures happen early, near the root, where pruning removes the largest subtrees.

### N-Queens constraints

Place one queen per row, so rows never clash. Track which columns and diagonals are already attacked:

- Squares on the same **diagonal** (running down to the right) have the same value of $r - c$.
- Squares on the same **anti-diagonal** (running down to the left) have the same value of $r + c$.

Keeping three sets (columns, $r - c$ values, $r + c$ values) makes each safety check $O(1)$.

### Cost

The running time is roughly the number of tree nodes visited times the work per node. With little pruning, this is exponential or factorial; for example, generating all permutations costs $\Theta(n \cdot n!)$ when each permutation of length $n$ is copied out. Pruning does not usually change the worst-case class, but it can reduce the actual work by orders of magnitude. When the same partial states are reached again and again by different paths, dynamic programming, which remembers results, may be the better tool.

## Worked examples

### Example 1: Subsets and permutations

```python
def subsets(items):
    result, chosen = [], []

    def backtrack(i):
        if i == len(items):
            result.append(chosen[:])         # copy: chosen keeps changing
            return
        chosen.append(items[i])              # choose items[i] ...
        backtrack(i + 1)
        chosen.pop()                         # ... unchoose it, then explore without it
        backtrack(i + 1)

    backtrack(0)
    return result

def permutations(items):
    result, current, used = [], [], [False] * len(items)

    def backtrack():
        if len(current) == len(items):
            result.append("".join(current))
            return
        for i, item in enumerate(items):
            if not used[i]:
                used[i] = True               # choose
                current.append(item)
                backtrack()                  # explore
                current.pop()                # unchoose
                used[i] = False

    backtrack()
    return result

print(subsets(["a", "b", "c"]))
print(permutations("abc"))
print(len(subsets(list(range(10)))), len(permutations("abcdef")))
```

Output:

```text
[['a', 'b', 'c'], ['a', 'b'], ['a', 'c'], ['a'], ['b', 'c'], ['b'], ['c'], []]
['abc', 'acb', 'bac', 'bca', 'cab', 'cba']
1024 720
```

The subset tree makes a two-way decision at each of the 3 levels, giving $2^3 = 8$ leaves; the order of the output follows the tree from left (include) to right (exclude). The permutation tree has 3 choices at the first level, 2 at the second, and 1 at the third, so $3! = 6$ leaves. The last line confirms the counts $2^{10} = 1024$ and $6! = 720$. Note `chosen[:]`: appending `chosen` itself would store one list object that is emptied again by later `pop` calls.

### Example 2: Pruning a sum search

Find every multiset of numbers from a list (each number usable any number of times) that adds up to a target.

```python
def combination_sum(candidates, target):
    candidates = sorted(candidates)
    result, chosen = [], []

    def backtrack(start, remaining):
        if remaining == 0:
            result.append(chosen[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                         # prune: every later candidate is larger still
            chosen.append(c)
            backtrack(i, remaining - c)       # i, not i + 1: c may be used again
            chosen.pop()

    backtrack(0, target)
    return result

print(combination_sum([2, 3, 5], 8))
print(len(combination_sum([7, 3, 2], 18)))
```

Output:

```text
[[2, 2, 2, 2], [2, 3, 3], [3, 5]]
7
```

Two ideas keep this search small and free of duplicates. Each recursive call starts at index `i`, so numbers are chosen in non-decreasing order and `[2, 3, 3]` is generated once, not also as `[3, 2, 3]` and `[3, 3, 2]`. And because the candidates are sorted, the moment one candidate exceeds the remaining amount, the loop can stop, cutting off that candidate and every larger one.

### Example 3: N-Queens

```python
def n_queens(n):
    cols, diag, anti = set(), set(), set()
    placement, solutions, nodes = [], [], 0

    def place(row):
        nonlocal nodes
        nodes += 1
        if row == n:
            solutions.append(placement[:])
            return
        for col in range(n):
            if col in cols or row - col in diag or row + col in anti:
                continue                      # attacked: prune this branch
            cols.add(col); diag.add(row - col); anti.add(row + col)
            placement.append(col)
            place(row + 1)
            placement.pop()
            cols.remove(col); diag.remove(row - col); anti.remove(row + col)

    place(0)
    return solutions, nodes

solutions, nodes = n_queens(4)
print(solutions)
for row in range(4):
    print(" ".join("Q" if solutions[0][row] == c else "." for c in range(4)))
for n in (6, 8):
    solutions, nodes = n_queens(n)
    print(f"n={n}: {len(solutions)} solutions, {nodes} partial placements, {n ** n} brute-force placements")
```

Output:

```text
[[1, 3, 0, 2], [2, 0, 3, 1]]
. Q . .
. . . Q
Q . . .
. . Q .
n=6: 4 solutions, 153 partial placements, 46656 brute-force placements
n=8: 92 solutions, 2057 partial placements, 16777216 brute-force placements
```

Each solution lists the column of the queen in each row; `[1, 3, 0, 2]` is drawn as a board. For $n = 8$, backtracking visits 2,057 nodes of the state-space tree (counting the empty board), compared with nearly 17 million complete placements that brute force would test. Most branches die within a few rows, because every queen placed rules out a column and two diagonals for all later rows.

## Applications

- **Puzzles and games:** Sudoku, crosswords, and other constraint puzzles are solved by backtracking with careful ordering; game-tree search with alpha-beta pruning is a close relative.
- **Constraint satisfaction:** timetabling, exam scheduling, and graph colouring (assign colours so that adjacent vertices differ), usually with heuristics such as "most constrained variable first".
- **Combinatorial generation:** listing all subsets, permutations, or combinations for testing, enumeration, or exhaustive verification of small cases.
- **SAT solvers:** the DPLL algorithm and its modern descendants decide Boolean satisfiability by backtracking with powerful pruning and learning, and are used in hardware and software verification.
- **Parsing and pattern matching:** regular-expression engines that support backreferences try alternatives and backtrack on failure.

## Common mistakes

- **Forgetting to unchoose,** for example not popping the last element or not removing a column from the attacked set, so later branches inherit a corrupted state.
- **Recording a reference instead of a copy,** such as `result.append(chosen)`, so every recorded solution ends up as the same, finally empty, list.
- **Generating duplicates** by allowing the same combination in different orders; enforce an order (non-decreasing indices) or skip equal candidates at the same level.
- **Checking constraints only at the leaves,** which turns backtracking back into brute force; check after every choice.
- **Using backtracking where subproblems repeat.** If the same remaining state is reached by many paths, memoization or dynamic programming avoids redoing the work.

## Revision notes

- Backtracking = depth-first search over partial solutions: choose, explore, unchoose.
- Memory is proportional to the depth; time is proportional to the nodes visited.
- Search spaces: subsets $2^n$, permutations $n!$, combinations $\binom{n}{k}$, N-Queens brute force $n^n$.
- Prune early: feasibility (constraint broken), bounds (cannot beat the best), ordering (fail near the root).
- N-Queens: one queen per row; track columns, $r - c$ diagonals, and $r + c$ anti-diagonals in sets.
- Copy solutions when recording them; restore state exactly when backtracking.

## Practice questions

:::question basic
How many leaves does the full state-space tree for the subsets of a 5-element set have, and how many nodes in total?
:::answer
Each of the 5 levels doubles the number of nodes, so there are $2^5 = 32$ leaves, one per subset. Counting all levels, the tree has $1 + 2 + 4 + 8 + 16 + 32 = 63 = 2^6 - 1$ nodes.
:::

:::question basic
What does the unchoose step do in the permutation generator of Example 1, and what would go wrong without it?
:::answer
After exploring all permutations that start with the current choice, it removes the item from `current` and marks it unused again, restoring the state from before the choice. Without it, the item would stay in `current` and stay marked as used, so the next iteration of the loop would build on a wrong prefix, the lengths would be wrong, and most permutations would never be generated.
:::

:::question intermediate
Explain why the N-Queens solver uses $r - c$ and $r + c$ to identify diagonals. Are the squares (1, 3) and (3, 1) on a common diagonal?
:::answer
Moving one step down and one step right changes both $r$ and $c$ by 1, so $r - c$ stays the same along a down-right diagonal; moving down and left increases $r$ and decreases $c$, so $r + c$ stays the same along a down-left anti-diagonal. For (1, 3) and (3, 1), $r - c$ is $-2$ and $2$, so they are not on a common diagonal, but $r + c = 4$ for both, so they share an anti-diagonal and the queens would attack each other.
:::

:::question intermediate
Modify the idea of `combination_sum` so that each number may be used at most once. What does `combination_sum([2, 3, 5], 8)` return then?
:::answer
Pass `i + 1` instead of `i` to the recursive call, so that after choosing a candidate the search continues only with later candidates. (If the input could contain duplicate values, also skip a candidate equal to the previous one at the same level.) With each of 2, 3, and 5 usable once, the only combination summing to 8 is `[3, 5]`, since $2 + 3 = 5$, $2 + 5 = 7$, and $2 + 3 + 5 = 10$.
:::

:::question intermediate
Write a backtracking outline that generates all combinations of $k$ items from $n$, and describe a pruning rule.
:::answer
Use `backtrack(start, chosen)`: if `len(chosen) == k`, record a copy and return; otherwise, for each index `i` from `start` to `n - 1`, append item `i`, call `backtrack(i + 1, chosen)`, and pop. Pruning rule: if the number of items left, `n - i`, is smaller than the number still needed, `k - len(chosen)`, stop the loop, because no completion can reach size $k$. This avoids exploring branches that cannot produce any combination.
:::

:::question advanced
A Sudoku solver picks the empty cell with the fewest legal digits at each step instead of the next cell in reading order. Why does this usually speed up the search dramatically?
:::answer
A cell with only one legal digit forces a choice, so it creates no branching at all, and a cell with zero legal digits reveals immediately that the current partial grid is a dead end. Choosing the most constrained cell therefore keeps the branching factor small and discovers contradictions near the root of the search tree, where pruning removes the largest subtrees. Filling cells in reading order may make many unconstrained choices first and discover the contradiction only much deeper, after exploring a huge number of doomed branches.
:::

:::question advanced
Estimate the running time of generating all permutations of $n$ items with the generator in Example 1, and explain why no algorithm that outputs every permutation can be asymptotically faster.
:::answer
The tree has $n!$ leaves and fewer than $e \cdot n!$ nodes in total, each node doing $O(n)$ work in its loop, and each leaf copies a permutation of length $n$. So the running time is $\Theta(n \cdot n!)$. Any algorithm that writes out all $n!$ permutations, each of length $n$, must produce $n \cdot n!$ symbols of output, so $\Omega(n \cdot n!)$ is unavoidable and the generator is asymptotically optimal. (Algorithms such as Heap's algorithm that change one permutation into the next with a single swap reach $O(1)$ amortized work per permutation only if they do not copy each permutation out.)
:::

## Further learning

- **Next:** *Greedy Choice & Optimal Substructure* covers problems where a single well-chosen decision at each step suffices, with no backtracking at all.
- **Related:** *Breadth-First Search & Depth-First Search* explains the depth-first exploration that backtracking is built on.
- **Related:** *Memoization vs Tabulation* handles search problems whose subproblems repeat.
