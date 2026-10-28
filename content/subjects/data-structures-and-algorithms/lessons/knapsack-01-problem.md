---
lesson: knapsack-01-problem
title: The 0/1 Knapsack Problem
summary: Choose whole items to maximise value within a weight limit using a dynamic programming table, recover the chosen items, compress the table to one row, and understand why the running time is pseudo-polynomial.
minutes: 60
type: theory
objectives:
  - Formulate the 0/1 knapsack problem and derive its state-transition recurrence
  - Fill the two-dimensional DP table by hand and in code, and reconstruct the chosen items
  - Reduce the table to one row by iterating capacities downwards, and explain why the direction matters
  - Analyse the O(nW) pseudo-polynomial running time and relate 0/1 knapsack to subset sum, partition, and the unbounded and fractional variants
---

## Introduction

A hiker can carry at most 7 kg and must choose among a tent, a stove, food, and a camera, each with a weight and a usefulness score. Items cannot be split: you take the whole stove or leave it behind. Which items give the greatest total usefulness without exceeding the limit? The same decision appears when a project manager picks projects within a budget, when an investor chooses assets with fixed costs, and when a cloud scheduler packs jobs onto a machine with limited memory.

This is the **0/1 knapsack problem**. The greedy rule that solves the fractional version, best value per kilogram first, fails here, and trying all subsets takes $2^n$ steps. Dynamic programming solves it exactly by building a table of the best value achievable for every prefix of the items and every capacity up to the limit. It is the standard example of a DP over a two-dimensional state, and its techniques (reconstruction, one-row compression, and pseudo-polynomial analysis) carry over to many other problems.

**Before you start:** you should know memoization and tabulation, and the greedy fractional knapsack algorithm.

## Core theory

### The problem

There are $n$ items; item $i$ has weight $w_i$ (a positive integer) and value $v_i$. The capacity is an integer $W$. Choose a subset $S$ of the items to

$$\text{maximise } \sum_{i \in S} v_i \quad \text{subject to} \quad \sum_{i \in S} w_i \le W.$$

"0/1" means each item is taken zero times or once.

### State and recurrence

Let $K(i, c)$ be the **best value achievable using only the first $i$ items with capacity $c$**. Consider item $i$:

- **Skip it:** the best is whatever the first $i - 1$ items achieve with the same capacity, $K(i - 1, c)$.
- **Take it** (only possible if $w_i \le c$): gain $v_i$, and the remaining capacity $c - w_i$ is filled as well as possible by the first $i - 1$ items: $K(i - 1, c - w_i) + v_i$.

$$K(i, c) = \begin{cases} K(i-1, c) & \text{if } w_i > c \\ \max\big(K(i-1, c),\; K(i-1, c - w_i) + v_i\big) & \text{otherwise} \end{cases}$$

with $K(0, c) = 0$ for every $c$ (no items, no value). The answer is $K(n, W)$. This is optimal substructure: an optimal choice either excludes item $i$, leaving an optimal solution for $i - 1$ items, or includes it, leaving an optimal solution for $i - 1$ items and capacity $c - w_i$.

### Filling the table

The table has $n + 1$ rows (items) and $W + 1$ columns (capacities). Row $i$ depends only on row $i - 1$, so filling the rows from top to bottom is a valid order. Each cell takes $O(1)$ time, so the algorithm runs in $\Theta(nW)$ time and $\Theta(nW)$ space.

### Recovering the items

Start at cell $(n, W)$ and walk upwards. At row $i$ with capacity $c$: if $K(i, c) \ne K(i - 1, c)$, item $i$ must have been taken (skipping it would have given the value above), so record it and set $c \leftarrow c - w_i$; otherwise item $i$ was skipped. This takes $O(n)$ time once the table is filled.

### One row is enough

Because row $i$ reads only row $i - 1$, a single array `best[0..W]` can hold the current row, updated in place, if capacities are processed **from $W$ down to $w_i$**:

```text
for each item (w, v):
    for c from W down to w:
        best[c] = max(best[c], best[c - w] + v)
```

Iterating downwards guarantees that `best[c - w]`, a smaller index, has not yet been updated for the current item, so it still holds the previous row's value, and each item is used at most once. Iterating **upwards** would let `best[c - w]` already include the current item, so the item could be taken again and again. That computes the **unbounded knapsack**, where every item has unlimited copies, which is a different problem. The space drops to $\Theta(W)$, but item reconstruction then needs extra bookkeeping.

### Pseudo-polynomial time

$\Theta(nW)$ looks polynomial, but $W$ is a number in the input, written with only about $\log_2 W$ digits. Doubling the number of digits of $W$ squares its value, so the running time is exponential in the **size** of the input. Such algorithms are called **pseudo-polynomial**: fast when the capacity is modest (thousands or millions), useless when $W = 10^{18}$. This is consistent with the fact that the decision version of knapsack is NP-complete, so no truly polynomial algorithm is known.

### Related problems

| Problem | Difference | DP |
| :--- | :--- | :--- |
| Fractional knapsack | items can be split | not needed: greedy by value per weight |
| Unbounded knapsack | unlimited copies of each item | the one-row loop with capacities increasing |
| Subset sum | is there a subset with total exactly $T$? | a Boolean table: `reachable[s]` |
| Partition | can the items be split into two equal-sum halves? | subset sum with $T$ = total / 2 |
| Bounded knapsack | item $i$ has $k_i$ copies | split copies into powers of two, or extend the state |

## Worked examples

### Example 1: The full table

Items as (weight, value): (1, 1), (3, 4), (4, 5), (5, 7), with capacity 7.

```python
def knapsack(items, W):
    n = len(items)
    K = [[0] * (W + 1) for _ in range(n + 1)]          # K[i][c]: first i items, capacity c
    for i in range(1, n + 1):
        w, v = items[i - 1]
        for c in range(W + 1):
            K[i][c] = K[i - 1][c]                      # skip item i
            if w <= c:
                K[i][c] = max(K[i][c], K[i - 1][c - w] + v)   # or take it
    chosen, c = [], W
    for i in range(n, 0, -1):                          # walk back up the table
        if K[i][c] != K[i - 1][c]:
            chosen.append(items[i - 1])
            c -= items[i - 1][0]
    return K, chosen[::-1]

items = [(1, 1), (3, 4), (4, 5), (5, 7)]
K, chosen = knapsack(items, 7)
print("capacity:     ", list(range(8)))
for i, row in enumerate(K):
    label = "no items" if i == 0 else f"+ item {items[i - 1]}"
    print(f"{label:14}", row)
print("best value:", K[-1][-1], "using", chosen)
```

Output:

```text
capacity:      [0, 1, 2, 3, 4, 5, 6, 7]
no items       [0, 0, 0, 0, 0, 0, 0, 0]
+ item (1, 1)  [0, 1, 1, 1, 1, 1, 1, 1]
+ item (3, 4)  [0, 1, 1, 4, 5, 5, 5, 5]
+ item (4, 5)  [0, 1, 1, 4, 5, 6, 6, 9]
+ item (5, 7)  [0, 1, 1, 4, 5, 7, 8, 9]
best value: 9 using [(3, 4), (4, 5)]
```

Read the cell for the third item at capacity 7: skipping it gives the value above, 5; taking it gives 5 plus the best value for the first two items with capacity 3, which is 4, for 9. The last item, (5, 7), has the best value per kilogram, but taking it leaves 2 kg, worth at most 1, so its row stays at 9 for capacity 7. The walk back finds $K(4, 7) = K(3, 7)$, so item 4 was skipped; $K(3, 7) \ne K(2, 7)$, so item 3 was taken, leaving capacity 3; $K(2, 3) \ne K(1, 3)$, so item 2 was taken, leaving 0. Greedy by value per weight would take (5, 7) and then (1, 1), for only 8.

### Example 2: One row, and why the loop runs downwards

```python
def knapsack_one_row(items, W, downwards=True):
    best = [0] * (W + 1)
    for w, v in items:
        capacities = range(W, w - 1, -1) if downwards else range(w, W + 1)
        for c in capacities:
            best[c] = max(best[c], best[c - w] + v)
    return best

items = [(1, 1), (3, 4), (4, 5), (5, 7)]
print("0/1, downwards:     ", knapsack_one_row(items, 7))
print("upwards (unbounded):", knapsack_one_row(items, 7, downwards=False))

single = [(2, 3)]                    # one item: weight 2, value 3
print(knapsack_one_row(single, 6), knapsack_one_row(single, 6, downwards=False))
```

Output:

```text
0/1, downwards:      [0, 1, 1, 4, 5, 7, 8, 9]
upwards (unbounded): [0, 1, 2, 4, 5, 7, 8, 9]
[0, 0, 3, 3, 3, 3, 3] [0, 0, 3, 3, 6, 6, 9]
```

The downward loop reproduces the last row of the full table using a single array of length 8. The upward loop gives `best[2] = 2`, which is impossible in the 0/1 problem: the only item of weight 1 has been counted twice. The single-item test makes the difference plain: with one item of weight 2 and capacity 6, the 0/1 answer is 3, but the upward loop "takes" the item three times and reports 9. Upward iteration is exactly the right algorithm for the unbounded knapsack, so the loop direction decides which problem is being solved.

### Example 3: Subset sum and equal partition

The knapsack table becomes Boolean when we only ask whether a total is reachable. A multiset can be split into two halves with equal sums exactly when some subset reaches half of the total.

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False, None            # an odd total cannot be split evenly
    target = total // 2
    reachable = [True] + [False] * target          # reachable[s]: some subset sums to s
    for x in nums:
        for s in range(target, x - 1, -1):         # downwards: each number used once
            reachable[s] = reachable[s] or reachable[s - x]
    return reachable[target], target

print(can_partition([1, 5, 11, 5]))
print(can_partition([1, 2, 3, 5]))
print(can_partition([3, 1, 1, 2, 2, 1]))
```

Output:

```text
(True, 11)
(False, None)
(True, 5)
```

For `[1, 5, 11, 5]`, the total is 22, and the subset {11} (or {1, 5, 5}) reaches 11, so the split exists. `[1, 2, 3, 5]` has an odd total, 11, and is rejected immediately. For `[3, 1, 1, 2, 2, 1]`, the total is 10, and subsets such as {3, 2} reach 5. The table has only target + 1 Boolean entries, and the running time is $O(n \cdot \text{target})$, again pseudo-polynomial.

## Applications

- **Budgeting and portfolio selection:** choosing projects or investments with fixed costs and expected returns under a budget.
- **Resource allocation in computing:** packing jobs, virtual machines, or cache entries into limited memory or time.
- **Cutting and loading:** deciding which orders to fulfil from a fixed amount of material, or which parcels to load into a vehicle.
- **Subset sum and partition:** balancing workloads between two machines, and splitting payments or teams evenly.
- **Cryptography history:** the Merkle-Hellman knapsack cryptosystem (1978) was based on a subset-sum problem; it was later broken, which illustrates how the special structure of an instance can make a hard problem easy.

## Common mistakes

- **Applying the greedy ratio rule to the 0/1 version,** which can leave capacity unused and miss the optimum, as Example 1 shows.
- **Iterating capacities upwards in the one-row version,** which silently solves the unbounded knapsack instead.
- **Off-by-one table sizes:** the table needs $W + 1$ columns (capacities 0 to $W$) and $n + 1$ rows (including "no items").
- **Mixing up `items[i - 1]` and row `i`** when the table has a "no items" row at index 0.
- **Calling the algorithm polynomial.** $\Theta(nW)$ is pseudo-polynomial; it is impractical when $W$ is huge, and non-integer weights must be scaled to integers first.
- **Trying to reconstruct items from the one-row array alone,** which no longer contains the information; keep the full table or record decisions.

## Revision notes

- 0/1 knapsack: each item whole or not at all; maximise value with total weight at most $W$.
- $K(i, c) = \max(K(i-1, c),\; K(i-1, c - w_i) + v_i)$ when $w_i \le c$; otherwise $K(i-1, c)$. Base: $K(0, c) = 0$.
- $\Theta(nW)$ time and space; pseudo-polynomial in the input size.
- Reconstruction: walk up from $(n, W)$; if $K(i, c) \ne K(i - 1, c)$, item $i$ was taken.
- One row: loop capacities from $W$ down to $w_i$; upwards gives the unbounded knapsack.
- Subset sum and partition are Boolean knapsacks; fractional knapsack needs only greedy.

## Practice questions

:::question basic
Why does the knapsack table need a row for "no items" and a column for capacity 0?
:::answer
They hold the base cases. With no items, the best value is 0 for every capacity, and with capacity 0, nothing can be taken, so the value is 0. The recurrence for row $i$ reads row $i - 1$ and column $c - w_i$, which can be row 0 or column 0, so these entries must exist and be correct for the first real items to be computed properly.
:::

:::question basic
What is the running time of the knapsack DP for 100 items and capacity 10,000, and roughly how many table cells does it fill?
:::answer
It fills $(100 + 1) \times (10{,}000 + 1) \approx 1.01$ million cells, each in constant time, so it runs in $\Theta(nW)$, about a million basic steps, which is very fast. By contrast, checking every subset of 100 items would mean $2^{100} \approx 1.3 \times 10^{30}$ subsets.
:::

:::question intermediate
Fill the knapsack table for items (weight, value) = (2, 3), (3, 4), (4, 6) with capacity 5. What is the best value, and which items achieve it?
:::answer
Row 1, item (2, 3): `[0, 0, 3, 3, 3, 3]`. Row 2, item (3, 4): `[0, 0, 3, 4, 4, 7]`, where capacity 5 takes both items for $3 + 4 = 7$. Row 3, item (4, 6): `[0, 0, 3, 4, 6, 7]`, where capacity 4 takes item 3 alone for 6, and capacity 5 compares 7 with $6 + K(2, 1) = 6$, keeping 7. The best value is 7, using items (2, 3) and (3, 4).
:::

:::question intermediate
In the one-row version, why must the capacity loop run from $W$ down to $w_i$ for the 0/1 problem?
:::answer
The update reads `best[c - w]`, which must still hold the value from before the current item was considered, that is, the previous row. Going downwards, every index smaller than `c` has not been touched for this item yet, so it does. Going upwards, `best[c - w]` would already include the current item, and adding $v_i$ again would count the item twice, which is allowed only in the unbounded knapsack.
:::

:::question intermediate
Explain why $\Theta(nW)$ is called pseudo-polynomial rather than polynomial.
:::answer
Input size is measured by the number of bits needed to write the input. The capacity $W$ takes about $\log_2 W$ bits, so $W$ itself is exponential in its own length: adding 10 bits to $W$ multiplies it by about 1000, and the running time with it. The algorithm is polynomial in the numeric value of $W$ but not in the length of the input, so it is only efficient when $W$ is reasonably small.
:::

:::question advanced
Modify the recurrence to count the number of different subsets of items whose weights sum exactly to $T$. Apply it to weights 1, 2, 3 with $T = 3$.
:::answer
Let $N(i, s)$ be the number of subsets of the first $i$ items with total weight exactly $s$. Then $N(0, 0) = 1$, $N(0, s) = 0$ for $s > 0$, and $N(i, s) = N(i - 1, s) + N(i - 1, s - w_i)$ when $w_i \le s$ (otherwise just $N(i - 1, s)$): every subset either excludes or includes item $i$. Addition replaces the maximum because we count rather than optimise. For weights 1, 2, 3 and $T = 3$, the subsets are {3} and {1, 2}, so $N(3, 3) = 2$.
:::

:::question advanced
For the instance in Example 1, show that greedy by value per weight gives a worse answer than the DP, and explain in terms of the table why the DP is not fooled.
:::answer
The ratios are 1, 1.33, 1.25, and 1.4 per kilogram, so greedy takes (5, 7) first, leaving 2 kg, then takes (1, 1), leaving 1 kg in which nothing else fits: value 8. The DP finds 9 with (3, 4) and (4, 5). In the table, the cell for the last item at capacity 7 compares taking it, $7 + K(3, 2) = 7 + 1 = 8$, with skipping it, $K(3, 7) = 9$. The DP evaluates both options with exact knowledge of what the leftover capacity is worth, while greedy commits to the best ratio without checking whether the leftover capacity can be used well.
:::

## Further learning

- **Next:** this completes the Data Structures & Algorithms core course. Revisit *Asymptotic Notations* to connect the course's analysis tools with the algorithms you have now studied.
- **Related:** *Memoization vs Tabulation* covers the general techniques used here.
- **Related:** *Greedy Choice & Optimal Substructure* explains why the fractional version needs no table at all.
