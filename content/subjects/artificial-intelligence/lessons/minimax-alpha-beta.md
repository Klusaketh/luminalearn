---
lesson: minimax-alpha-beta
title: Minimax & Alpha-Beta Pruning
summary: Adversarial search in two-player zero-sum games, minimax values and the minimax algorithm, alpha-beta pruning and the effect of move ordering, depth-limited search with evaluation functions, and extensions to games of chance.
minutes: 50
type: theory
objectives:
  - Compute minimax values on a game tree and explain the minimax decision
  - Apply alpha-beta pruning, identify pruned branches, and explain how move ordering affects its efficiency
  - Describe evaluation functions, cutoff search, the horizon effect, and expectiminimax for games with chance
review: ai-draft
---
## Introduction

In a game, the agent is not alone: an opponent works against it, choosing moves to minimise its success. Planning must therefore consider the opponent's best replies, not just the agent's own options. **Minimax** search gives the optimal strategy for two-player, turn-taking, zero-sum games such as tic-tac-toe, chess, and Go, and **alpha-beta pruning** makes it practical by skipping moves that cannot affect the decision. These ideas powered chess programs from the 1950s to Deep Blue.

**Before you start:** you should know depth-first search and recursion from *Problem Formulation & Uninformed Search*.

## Core theory

### Games as search problems

A two-player game is defined by an initial state, PLAYER(s) (whose turn it is), ACTIONS(s), RESULT(s, a), a **terminal test**, and a **utility** function giving the final score, such as +1 for a win, 0 for a draw, and −1 for a loss. In a **zero-sum** game, one player's gain is the other's loss. We call the players MAX and MIN.

### Minimax

The **minimax value** of a state is the utility MAX gets if both players play optimally from there:

$$\text{MINIMAX}(s) = \begin{cases} \text{UTILITY}(s) & \text{if } s \text{ is terminal} \\ \max_a \text{MINIMAX}(\text{RESULT}(s, a)) & \text{if MAX moves} \\ \min_a \text{MINIMAX}(\text{RESULT}(s, a)) & \text{if MIN moves} \end{cases}$$

The minimax algorithm computes these values by depth-first search to the leaves and backs them up the tree; MAX then plays the move with the highest value. With branching factor $b$ and maximum depth $m$, it takes $O(b^m)$ time and $O(bm)$ space. For chess, $b \approx 35$ and games last around 80 plies, so the full tree is astronomically large.

### Alpha-beta pruning

Alpha-beta computes exactly the same decision while skipping branches that cannot matter. It carries two bounds:

- $\alpha$: the best value MAX can already guarantee on the current path (a lower bound).
- $\beta$: the best value MIN can already guarantee (an upper bound).

When a node's possible value falls outside the window, specifically when $\alpha \ge \beta$, the remaining children can be **pruned**: a rational opponent would never let play reach this node. Efficiency depends on **move ordering**. With perfect ordering, alpha-beta examines about $O(b^{m/2})$ nodes, which means it can search **twice as deep** in the same time; with random ordering it is roughly $O(b^{3m/4})$. Programs order moves using captures first, "killer moves" that caused cutoffs elsewhere, and results of shallower searches (iterative deepening).

### Imperfect real-time decisions

Real games cannot be searched to the end, so programs stop at a depth limit and apply an **evaluation function** that estimates the value of a position, often a weighted sum of features (for example material: pawn 1, knight and bishop 3, rook 5, queen 9). Problems include the **horizon effect** (a bad event is pushed just beyond the search depth) and unstable positions, addressed by **quiescence search**, which extends search in positions with pending captures. **Transposition tables** cache values of positions reached by different move orders.

### Games of chance

In backgammon, dice add **chance nodes**. **Expectiminimax** computes the expected value at chance nodes, the probability-weighted average of the children's values, while MAX and MIN nodes behave as before. **Monte Carlo tree search**, which estimates values from simulated playouts, combined with learned evaluation, powered AlphaGo.

## Worked examples

### Example 1: Solving tic-tac-toe

The program runs minimax from the empty board with and without alpha-beta, then evaluates every move in a mid-game position.

```python
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
nodes = 0


def winner(board):
    for a, b, c in LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def minimax(board, player, alpha=None, beta=None):
    """Value for X: +1 X wins, -1 O wins, 0 draw. alpha/beta None = no pruning."""
    global nodes
    nodes += 1
    win = winner(board)
    if win or " " not in board:
        return {"X": 1, "O": -1, None: 0}[win]
    pruning = alpha is not None
    best = -2 if player == "X" else 2
    for i in range(9):
        if board[i] == " ":
            board[i] = player
            value = minimax(board, "O" if player == "X" else "X", alpha, beta)
            board[i] = " "
            if player == "X":
                best = max(best, value)
                if pruning:
                    alpha = max(alpha, best)
            else:
                best = min(best, value)
                if pruning:
                    beta = min(beta, best)
            if pruning and alpha >= beta:
                break  # the opponent will never allow this branch
    return best


for label, args in [("plain minimax", ()), ("alpha-beta", (-2, 2))]:
    nodes = 0
    value = minimax([" "] * 9, "X", *args)
    print(f"{label:13}: value of the empty board = {value}, nodes visited = {nodes:,}")

board = list("XX OO    ")  # X to move: X X _ / O O _ / _ _ _
nodes = 0
scores = {}
for i in range(9):
    if board[i] == " ":
        board[i] = "X"
        scores[i] = minimax(board, "O", -2, 2)
        board[i] = " "
print("X to move in 'XX_/OO_/___': value of each move ->", scores)
```

Output:

```text
plain minimax: value of the empty board = 0, nodes visited = 549,946
alpha-beta   : value of the empty board = 0, nodes visited = 18,297
X to move in 'XX_/OO_/___': value of each move -> {2: 1, 5: 0, 6: -1, 7: -1, 8: -1}
```

Both searches agree that the empty board has value 0: with perfect play, tic-tac-toe is a draw. Plain minimax visits the entire game tree of 549,946 nodes, while alpha-beta, even with the simple left-to-right move order, needs only 18,297, about 30 times fewer, for the same answer. In the position with X on squares 0 and 1 and O on squares 3 and 4, square 2 wins at once (+1), square 5 blocks O's threat and leads to a draw (0), and every other move loses (−1) because O completes the middle row.

### Example 2: Alpha-beta by hand

MAX chooses among three MIN nodes with leaves A = [4, 9, 6], B = [3, 8, 7], C = [10, 2, 5], evaluated left to right.

1. **A:** MIN takes the minimum of 4, 9, 6, so A = 4. At the root, $\alpha = 4$: MAX can guarantee at least 4.
2. **B:** the first leaf is 3, so B ≤ 3. Since $3 \le \alpha = 4$, MAX will never choose B, and the leaves 8 and 7 are **pruned**.
3. **C:** the first leaf 10 gives C ≤ 10, which does not settle anything. The second leaf 2 gives C ≤ 2 ≤ 4, so the last leaf 5 is pruned.

The root value is 4 (move A), the same as full minimax, after examining 6 of the 9 leaves. If C's leaves were ordered [2, 10, 5], only its first leaf would be needed: better move ordering means more pruning.

## Applications

- **Board games:** chess, checkers, and Othello engines use alpha-beta with evaluation functions.
- **Game-playing AI:** Monte Carlo tree search and learned evaluations for Go and video games.
- **Security and economics:** adversarial reasoning about attackers and competitors.
- **Robust planning:** treating nature as an adversary gives worst-case guarantees.

## Common mistakes

- **Mixing up MAX and MIN levels.** Values alternate between maximising and minimising each ply.
- **Thinking alpha-beta can change the result.** It returns the same value as minimax; it only skips irrelevant branches.
- **Pruning with the wrong bound.** Prune at a MIN node when its value is at most $\alpha$, and at a MAX node when its value is at least $\beta$.
- **Ignoring move ordering.** Poor ordering wastes most of alpha-beta's benefit.
- **Using minimax in games with dice.** Chance nodes require expected values (expectiminimax).

## Revision notes

- Minimax value: MAX maximises, MIN minimises, utilities at terminal states.
- Minimax search: $O(b^m)$ time, $O(bm)$ space.
- Alpha-beta: $\alpha$ is MAX's guaranteed lower bound, $\beta$ MIN's upper bound; prune when $\alpha \ge \beta$.
- Perfect ordering gives $O(b^{m/2})$: double the depth.
- Cutoff search with evaluation functions; horizon effect; quiescence search; transposition tables.
- Expectiminimax averages over chance nodes.

## Practice questions

:::question basic
What assumption does minimax make about the opponent?
:::answer
It assumes the opponent plays optimally, always choosing the move that is worst for MAX. Against a weaker opponent, minimax still guarantees at least the minimax value.
:::

:::question basic
A MAX root has two MIN children with leaves [5, 7] and [3, 9]. What is the minimax value, and which leaf can alpha-beta prune?
:::answer
The MIN values are 5 and 3, so the root value is 5. Evaluating left to right, the first child gives $\alpha = 5$; at the second child, the leaf 3 shows its value is at most 3 < 5, so the leaf 9 is pruned.
:::

:::question intermediate
How does perfect move ordering change the cost of alpha-beta, and what does that mean in practice?
:::answer
It reduces the nodes examined from $O(b^m)$ to about $O(b^{m/2})$, so the effective branching factor drops from $b$ to $\sqrt{b}$. In the same time, the program can search roughly twice as deep, which greatly improves playing strength.
:::

:::question intermediate
What is the horizon effect, and how does quiescence search reduce it?
:::answer
With a fixed depth limit, a program may make moves that merely delay an unavoidable loss, such as losing a piece, until it falls beyond the search depth, so the position looks safe. Quiescence search continues searching past the limit in unstable positions, for example while captures are pending, until the position is quiet enough for the evaluation function to be reliable.
:::

:::question advanced
A MAX player chooses between move A, which leads to a chance node where with probability 0.5 the value is 3 and with probability 0.5 it is −1, and move B, which leads to a certain value of 0.5. Which move does expectiminimax choose?
:::answer
The chance node's expected value is $0.5 \times 3 + 0.5 \times (-1) = 1$. Move B is worth 0.5, so expectiminimax chooses move A, whose expected value of 1 is higher, even though it risks a worse outcome.
:::

## Further learning

- **Next:** *Ontologies & Semantic Frameworks* turns from search to representing knowledge.
- **Related:** *Reinforcement Learning Fundamentals* in Machine Learning shows how game-playing agents learn evaluation functions from experience.
