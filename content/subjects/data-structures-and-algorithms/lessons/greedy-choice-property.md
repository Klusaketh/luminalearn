---
lesson: greedy-choice-property
title: Greedy Choice and Optimal Substructure
summary: Build a solution by repeatedly taking the locally best option, prove when that is globally optimal with exchange arguments, and recognise when it fails, using interval scheduling, fractional knapsack, and coin change.
minutes: 45
type: theory
objectives:
  - Describe the greedy strategy and the greedy-choice and optimal-substructure properties that make it correct
  - Solve interval scheduling by earliest finish time and prove the rule optimal with an exchange argument
  - Solve the fractional knapsack problem greedily and explain why the same rule fails for the 0/1 knapsack
  - Test a proposed greedy rule with counterexamples, including coin change with non-standard denominations
---

## Introduction

A **greedy algorithm** builds its answer one step at a time and, at every step, takes the option that looks best right now, without ever reconsidering. Making change with the fewest coins by always handing over the largest coin that fits is greedy. So is filling a day with meetings by always picking the meeting that finishes earliest, and so is Kruskal's minimum spanning tree algorithm, which always takes the cheapest remaining edge that does not create a cycle.

Greedy algorithms are attractive because they are simple and fast, usually just a sort followed by a single pass. Their danger is that a locally best choice can lead to a globally poor result, and a plausible-sounding greedy rule is often wrong. The skill this lesson teaches is telling the difference: recognising the two properties that make greed safe, proving optimality with an **exchange argument**, and hunting for **counterexamples** when a rule seems too good to be true.

**Before you start:** you should know sorting, basic proof by contradiction, and the idea of an optimisation problem.

## Core theory

### Two properties

A greedy algorithm is guaranteed to be optimal when the problem has both of these properties:

- **Greedy-choice property:** there is an optimal solution that includes the greedy choice. Committing to it never rules out reaching the best answer.
- **Optimal substructure:** after the greedy choice is made, what remains is a smaller instance of the same problem, and combining the greedy choice with an optimal solution of that smaller instance gives an optimal solution of the original.

Dynamic programming also relies on optimal substructure, but it does not have the greedy-choice property, so it must compare the results of several choices. Greedy algorithms commit to one choice per step and never look back.

### Proof techniques

- **Exchange argument:** take any optimal solution that differs from the greedy one. Show that you can swap one of its choices for the greedy choice without making it worse. Repeating the swap transforms the optimal solution into the greedy solution, so the greedy solution is optimal too.
- **Greedy stays ahead:** show that after every step, the greedy partial solution is at least as good as any other algorithm's partial solution after the same number of steps, measured in a suitable way.

### Interval scheduling

Given a set of time intervals (meetings, jobs, classes), choose as many as possible so that no two overlap. Several greedy rules sound reasonable:

| Rule | Optimal? | Counterexample |
| :--- | :--- | :--- |
| Earliest start time first | no | one long interval that starts first and covers several short ones |
| Shortest interval first | no | a short interval that overlaps two otherwise compatible intervals |
| Fewest conflicts first | no | counterexamples exist, though they are larger |
| **Earliest finish time first** | **yes** | none |

**Why earliest finish works.** Let $g$ be the interval that finishes first, and let $O$ be any optimal schedule. Let $o$ be the interval in $O$ that finishes first. Since $g$ finishes no later than $o$, replacing $o$ with $g$ cannot create an overlap with the rest of $O$, all of which starts after $o$ ends. The result is still a valid schedule with the same number of intervals, and it contains $g$: the greedy-choice property holds. What remains is the same problem restricted to intervals that start after $g$ finishes, so the argument repeats. Sorting dominates the running time: $O(n \log n)$.

### Fractional knapsack

A knapsack holds weight $W$. Each item $i$ has value $v_i$ and weight $w_i$, and you may take **any fraction** of an item, such as part of a sack of rice. Greedy rule: sort by **value per unit weight**, $v_i / w_i$, and take as much as possible of each item in that order. It is optimal by an exchange argument: if an optimal load contains some weight of a lower-ratio item while a higher-ratio item is not fully taken, swapping equal weights of the two increases (or keeps) the value. The cost is $O(n \log n)$.

In the **0/1 knapsack**, each item must be taken whole or not at all, and the same ratio rule fails, because the leftover capacity may be wasted. That version needs dynamic programming.

### Coin change

To pay amount $A$ with the fewest coins, greedy repeatedly takes the largest coin not exceeding what remains. It is optimal for **canonical** coin systems, such as 1, 5, 10, 25 or 1, 2, 5, 10, 20, 50, but not for every system: with coins 1, 3, 4, greedy pays 6 as $4 + 1 + 1$ (three coins), while $3 + 3$ uses two. In general, fewest-coin change needs dynamic programming.

### Greedy algorithms elsewhere in this subject

Dijkstra's shortest paths (settle the closest vertex), Prim's and Kruskal's minimum spanning trees (add the cheapest safe edge), and Huffman coding (merge the two least frequent symbols) are all greedy algorithms with proofs based on these same ideas.

## Worked examples

### Example 1: Earliest finish time

```python
def max_non_overlapping(intervals):
    chosen, last_end = [], float("-inf")
    for start, end in sorted(intervals, key=lambda iv: iv[1]):   # earliest finish first
        if start >= last_end:                # compatible with everything chosen so far
            chosen.append((start, end))
            last_end = end
    return chosen

meetings = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9),
            (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
print(max_non_overlapping(meetings))
```

Output:

```text
[(1, 4), (5, 7), (8, 11), (12, 16)]
```

The algorithm takes (1, 4), the meeting that frees the room soonest. Every meeting that starts before 4 is then skipped. Next it takes (5, 7), skipping (5, 9) and (6, 10) because they start before 7, and so on. Four meetings is the maximum: by the exchange argument, no schedule can do better. An interval that starts exactly when the previous one ends counts as compatible here (`start >= last_end`); that convention should match the problem's rules.

### Example 2: Testing other greedy rules

```python
def greedy_by(intervals, key):
    chosen = []
    for iv in sorted(intervals, key=key):
        if all(iv[1] <= c[0] or iv[0] >= c[1] for c in chosen):   # no overlap with any chosen
            chosen.append(iv)
    return chosen

rules = {
    "earliest finish": lambda iv: iv[1],
    "earliest start": lambda iv: iv[0],
    "shortest first": lambda iv: iv[1] - iv[0],
}
tests = [[(0, 10), (1, 2), (3, 4)], [(0, 5), (4, 7), (6, 11)]]
for intervals in tests:
    print(intervals)
    for name, key in rules.items():
        print(f"  {name:15} -> {len(greedy_by(intervals, key))} chosen")
```

Output:

```text
[(0, 10), (1, 2), (3, 4)]
  earliest finish -> 2 chosen
  earliest start  -> 1 chosen
  shortest first  -> 2 chosen
[(0, 5), (4, 7), (6, 11)]
  earliest finish -> 2 chosen
  earliest start  -> 2 chosen
  shortest first  -> 1 chosen
```

In the first test, "earliest start" grabs the long interval (0, 10), which blocks both short ones. In the second test, "shortest first" grabs (4, 7), which overlaps both of the others. Each wrong rule is defeated by a three-interval counterexample, while earliest finish gets the optimal answer, 2, on both. Small adversarial tests like these are the fastest way to reject a tempting greedy idea.

### Example 3: Fractional versus 0/1 knapsack

```python
from itertools import combinations

def fractional_knapsack(items, capacity):
    total = 0.0
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        take = min(weight, capacity)           # all of it, or whatever fits
        total += value * take / weight
        capacity -= take
        if capacity == 0:
            break
    return total

def greedy_01(items, capacity):                 # the same rule, whole items only
    total = 0
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        if weight <= capacity:
            total += value
            capacity -= weight
    return total

def best_01(items, capacity):                   # brute force over all subsets, for comparison
    return max(sum(v for v, _ in subset)
               for r in range(len(items) + 1)
               for subset in combinations(items, r)
               if sum(w for _, w in subset) <= capacity)

items = [(60, 10), (100, 20), (120, 30)]        # (value, weight)
print("fractional, greedy by ratio:", fractional_knapsack(items, 50))
print("0/1, greedy by ratio:       ", greedy_01(items, 50))
print("0/1, optimal:               ", best_01(items, 50))
```

Output:

```text
fractional, greedy by ratio: 240.0
0/1, greedy by ratio:        160
0/1, optimal:                220
```

The ratios are 6, 5, and 4 per unit of weight. The fractional version takes the first two items whole (weight 30, value 160) and fills the remaining 20 units with two-thirds of the third item, worth 80, for 240, which is optimal. With whole items only, the same rule takes the first two items and then cannot fit the third, leaving 20 units of capacity unused, for 160. The best 0/1 choice skips the highest-ratio item and takes the other two, weight 50 and value 220.

### Example 4: When greedy coin change fails

```python
def greedy_coins(coins, amount):
    used = []
    for c in sorted(coins, reverse=True):
        while amount >= c:
            amount -= c
            used.append(c)
    return used

def min_coins(coins, amount):                   # dynamic programming, for comparison
    best = [0] + [float("inf")] * amount
    for a in range(1, amount + 1):
        best[a] = min((best[a - c] + 1 for c in coins if c <= a), default=float("inf"))
    return best[amount]

print(greedy_coins([1, 5, 10, 25], 63), min_coins([1, 5, 10, 25], 63))
print(greedy_coins([1, 3, 4], 6), min_coins([1, 3, 4], 6))
```

Output:

```text
[25, 25, 10, 1, 1, 1] 6
[4, 1, 1] 2
```

With coins 1, 5, 10, and 25, greedy uses 6 coins for 63, which the dynamic-programming check confirms is the minimum. With coins 1, 3, and 4, greedy commits to the 4 and is then forced to use two 1s, while the optimum is $3 + 3$. The greedy-choice property fails for this coin system: no optimal way to pay 6 uses a 4.

## Applications

- **Scheduling:** booking the most meetings in one room (earliest finish), and minimising the maximum lateness of jobs by processing them in order of deadline (earliest deadline first).
- **Resource allocation:** fractional knapsack models divisible resources such as bandwidth, budget, or bulk goods.
- **Graph algorithms:** Dijkstra's shortest paths, and Prim's and Kruskal's minimum spanning trees.
- **Data compression:** Huffman coding builds optimal prefix codes by repeatedly merging the two least frequent symbols; it is used in formats such as DEFLATE (ZIP, PNG) and JPEG.
- **Approximation:** for hard problems such as set cover, a greedy algorithm often gives a provably good, though not optimal, answer quickly.

## Common mistakes

- **Trusting a greedy rule without proof or counterexample search.** Earliest start, shortest first, and most valuable first all sound reasonable and are all wrong for their problems.
- **Using the fractional knapsack rule on 0/1 knapsack,** which can waste capacity and miss the optimum.
- **Assuming greedy coin change works for every coin system.** It works for canonical systems such as standard currency denominations, not in general.
- **Confusing the two required properties.** Optimal substructure alone is not enough; without the greedy-choice property, dynamic programming is needed.
- **Mishandling ties and boundaries,** such as whether an interval ending at time 5 conflicts with one starting at 5; decide and apply it consistently.

## Revision notes

- Greedy: take the locally best choice at each step and never revisit it; usually sort, then scan in one pass.
- Correct when the problem has the greedy-choice property and optimal substructure.
- Prove with an exchange argument (swap the greedy choice into an optimal solution) or by showing that greedy stays ahead.
- Interval scheduling: earliest finish time is optimal; earliest start and shortest first are not. $O(n \log n)$.
- Fractional knapsack: highest value per weight first is optimal. For 0/1 knapsack the same rule fails; use dynamic programming.
- Coin change: greedy is optimal for canonical systems (1, 5, 10, 25) but fails for 1, 3, 4 at amount 6.

## Practice questions

:::question basic
State the greedy-choice property in your own words.
:::answer
Some optimal solution contains the first choice the greedy algorithm makes. Because of this, committing to that choice is safe: it does not prevent us from reaching an optimal solution, and the problem that remains can be solved the same way.
:::

:::question basic
Apply the earliest-finish rule to the intervals (1, 3), (2, 5), (4, 6), (6, 8), and (5, 9). Which are chosen?
:::answer
Sorted by finish time: (1, 3), (2, 5), (4, 6), (6, 8), (5, 9). Take (1, 3). Skip (2, 5), which starts before 3. Take (4, 6). Take (6, 8), which starts exactly when the previous one ends. Skip (5, 9). The answer is (1, 3), (4, 6), (6, 8): three intervals.
:::

:::question intermediate
Solve the fractional knapsack problem with capacity 10 and items (value, weight) = (30, 5), (24, 4), (18, 6).
:::answer
The ratios are 6, 6, and 3. Take all of (30, 5) and all of (24, 4): weight 9, value 54. One unit of capacity remains, so take $1/6$ of the third item, worth $18/6 = 3$. The maximum value is 57.
:::

:::question intermediate
Show that "take the most valuable item first" is not optimal for the fractional knapsack problem.
:::answer
Use capacity 50 and items (value, weight) = (100, 50) and (60, 10). Most valuable first takes the whole first item and fills the knapsack: value 100. Taking by ratio instead, the second item (ratio 6) goes in whole for 60, and the remaining 40 units take $40/50$ of the first item, worth 80, for a total of 140. The most valuable item has the lower ratio, so filling the knapsack with it first wastes capacity on less value per unit.
:::

:::question intermediate
Write out the exchange argument that proves earliest finish time is optimal for interval scheduling.
:::answer
Let $g$ be the interval with the earliest finish time and $O$ an optimal schedule. If $O$ contains $g$, we are done with the first step. Otherwise, let $o$ be the interval in $O$ with the earliest finish. Every other interval in $O$ starts at or after $o$ finishes, and $g$ finishes no later than $o$, so $O' = O - \{o\} + \{g\}$ has no overlaps and the same size. So some optimal schedule contains $g$. The remaining intervals in $O'$ form an optimal schedule of the intervals that start after $g$ finishes, which is the same problem, smaller; by induction, greedy solves it optimally too.
:::

:::question advanced
A coin system has denominations in which each coin is a multiple of the next smaller one, such as 1, 2, 4, 8 or 1, 5, 25. Explain why greedy coin change is optimal for such systems.
:::answer
Let the coins be $c_1 < c_2 < \dots < c_m$, each dividing the next. In an optimal solution, fewer than $c_{i+1}/c_i$ coins of each denomination $c_i$ (other than the largest) can appear: if there were $c_{i+1}/c_i$ of them, they could be replaced by one coin $c_{i+1}$, using fewer coins. Under this restriction, the coins smaller than $c_{i+1}$ total at most $c_{i+1} - c_1 < c_{i+1}$, so the number of largest coins is forced to be $\lfloor A / c_m \rfloor$, and the same reasoning applies to the remainder. That forced choice is exactly what greedy does, so greedy matches an optimal solution. (Divisibility is sufficient but not necessary; 1, 5, 10, 25 is canonical even though 10 does not divide 25.)
:::

:::question advanced
Lectures with given start and end times must all be held, possibly in several rooms at once. Describe a greedy algorithm that uses the minimum number of rooms, and apply it to (0, 30), (5, 10), (15, 20).
:::answer
Sort the lectures by start time and keep a min-heap of the end times of the rooms in use. For each lecture, if the smallest end time in the heap is at most the lecture's start, that room is free: replace its end time with the new lecture's end. Otherwise open a new room by pushing the end time. The heap's final size is the answer. This is optimal because the number of rooms opened equals the maximum number of lectures in progress at one moment, and no schedule can use fewer rooms than that. For the example: (0, 30) opens room 1; (5, 10) starts before 30, so it opens room 2; (15, 20) starts after room 2 frees up at 10, so it reuses room 2. Two rooms.
:::

## Further learning

- **Next:** *Memoization vs Tabulation* introduces dynamic programming for problems where greedy choices are not safe.
- **Related:** *0/1 Knapsack Problem* solves the knapsack variant on which the greedy rule fails.
- **Related:** *Minimum Spanning Trees & Disjoint Sets* proves two greedy graph algorithms correct with the cut property.
