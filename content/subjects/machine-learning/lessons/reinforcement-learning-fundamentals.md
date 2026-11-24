---
lesson: reinforcement-learning-fundamentals
title: Reinforcement Learning Fundamentals
summary: Learning from rewards: the agent-environment loop, Markov decision processes, returns and discounting, policies and value functions, the Bellman equations, value iteration, Q-learning, exploration versus exploitation, and an overview of deep reinforcement learning.
minutes: 55
type: theory
objectives:
  - Model a sequential decision problem as a Markov decision process and compute discounted returns
  - Apply the Bellman optimality equation with value iteration and the Q-learning update rule
  - Explain exploration versus exploitation, on-policy versus off-policy learning, and the challenges of deep reinforcement learning
review: ai-draft
---
## Introduction

How does a robot learn to walk, a program learn to play Go better than any human, or a recommender learn which suggestions keep users satisfied? There is no labelled answer for each situation, only feedback after actions: rewards and penalties, often delayed. **Reinforcement learning** (RL) studies agents that learn to act by trial and error to maximise long-term reward. Its ideas underpin game-playing systems such as AlphaGo, robotics, and the fine-tuning of large language models from human feedback.

**Before you start:** you should know expected values and the agent concepts from *PEAS Model & Agent Taxonomies*.

## Core theory

### The agent-environment loop

At each time step $t$, the agent observes state $s_t$, takes action $a_t$, and the environment returns a reward $r_{t+1}$ and a new state $s_{t+1}$. The agent's goal is to maximise the **return**, the discounted sum of future rewards:

$$G_t = r_{t+1} + \gamma r_{t+2} + \gamma^2 r_{t+3} + \cdots = \sum_{k=0}^{\infty}\gamma^k r_{t+k+1}$$

The **discount factor** $\gamma \in [0, 1)$ makes the sum finite and values sooner rewards more: $\gamma$ near 0 is short-sighted, near 1 far-sighted.

### Markov decision processes

An MDP is a tuple $(S, A, P, R, \gamma)$: states, actions, transition probabilities $P(s' \mid s, a)$, rewards, and the discount. The **Markov property** says the future depends only on the current state and action, not on the history.

### Policies and value functions

A **policy** $\pi(a \mid s)$ chooses actions. Its **state-value function** $V^\pi(s)$ is the expected return from $s$ when following $\pi$, and its **action-value function** $Q^\pi(s, a)$ is the expected return after taking $a$ in $s$ and then following $\pi$. The optimal values satisfy the **Bellman optimality equations**:

$$V^*(s) = \max_a\sum_{s'}P(s' \mid s, a)\left[R(s, a, s') + \gamma V^*(s')\right]$$

$$Q^*(s, a) = \sum_{s'}P(s' \mid s, a)\left[R(s, a, s') + \gamma\max_{a'}Q^*(s', a')\right]$$

An optimal policy acts greedily with respect to $Q^*$: $\pi^*(s) = \arg\max_a Q^*(s, a)$.

### Dynamic programming: when the model is known

**Value iteration** repeatedly applies the Bellman optimality update to every state until the values stop changing. Because the update is a contraction (it shrinks differences by a factor $\gamma$), it converges to $V^*$. **Policy iteration** alternates evaluating the current policy and improving it greedily.

### Learning without a model

Usually the agent does not know $P$ and $R$; it must learn from experience. **Temporal-difference** methods update estimates from single transitions. **Q-learning** updates

$$Q(s, a) \leftarrow Q(s, a) + \alpha\left[r + \gamma\max_{a'}Q(s', a') - Q(s, a)\right]$$

where $\alpha$ is the learning rate and the bracket is the **TD error**. Q-learning is **off-policy**: it learns the optimal policy's values while behaving differently (for example, exploring). **SARSA** is **on-policy**: it uses the action actually taken next, $Q(s', a')$, so it learns the value of the policy it follows, including its exploration.

### Exploration versus exploitation

An agent must **exploit** what it knows to earn reward but also **explore** to discover better actions. The **$\varepsilon$-greedy** strategy takes a random action with probability $\varepsilon$ and the best-known action otherwise, often decaying $\varepsilon$ over time. Multi-armed bandits study this trade-off in its simplest form; methods such as UCB add optimism for uncertain actions.

### Deep reinforcement learning

With huge state spaces (images, game boards), tables are replaced by neural networks: **DQN** learned Atari games from pixels (2015); **policy-gradient** and **actor-critic** methods (such as PPO) optimise policies directly; AlphaGo combined these with tree search. Challenges include sparse and delayed rewards (credit assignment), sample inefficiency, instability, and **reward hacking**, where an agent maximises the reward signal in unintended ways.

## Worked examples

### Example 1: Value iteration and Q-learning in a grid world

A 4×4 grid has a start at the top left, a goal worth +10 at the bottom right, a pit worth −10, a wall, and a cost of −1 for every other move. Moves are deterministic, and $\gamma = 0.9$. The program computes optimal values with value iteration, then lets a Q-learning agent learn from 2,000 episodes of trial and error.

```python
import random

ROWS, COLS = 4, 4
START, GOAL, PIT, WALL = (0, 0), (3, 3), (1, 2), (2, 1)
ACTIONS = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}
GAMMA = 0.9
STATES = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) != WALL]


def step(s, a):
    r, c = s[0] + ACTIONS[a][0], s[1] + ACTIONS[a][1]
    nxt = (r, c) if 0 <= r < ROWS and 0 <= c < COLS and (r, c) != WALL else s
    reward = 10 if nxt == GOAL else -10 if nxt == PIT else -1
    return nxt, reward, nxt in (GOAL, PIT)


def show(grid_fn):
    for r in range(ROWS):
        print("  " + " ".join(grid_fn((r, c)) for c in range(COLS)))


# Value iteration: V(s) <- max_a [ r + gamma * V(s') ]
V = {s: 0.0 for s in STATES}
for sweep in range(1, 100):
    delta = 0.0
    for s in STATES:
        if s in (GOAL, PIT):
            continue
        best = max(r + (0 if done else GAMMA * V[n]) for n, r, done in (step(s, a) for a in ACTIONS))
        delta, V[s] = max(delta, abs(best - V[s])), best
    if delta < 1e-9:
        break
print(f"value iteration converged after {sweep} sweeps; V(start) = {V[START]:.4f}")
show(lambda s: "  ###" if s == WALL else f"{V[s]:5.2f}")


def greedy_path(choose):
    s, path, total = START, [], 0
    while s not in (GOAL, PIT) and len(path) < 20:
        a = choose(s)
        s, r, _ = step(s, a)
        path.append(a)
        total += r
    return "".join(path), total


plan = lambda s: max(ACTIONS, key=lambda a: step(s, a)[1] + (0 if step(s, a)[2] else GAMMA * V[step(s, a)[0]]))  # noqa: E731
print("optimal path from start: %s (total reward %d)" % greedy_path(plan))

# Q-learning: learn from experience without knowing the transition model
random.seed(0)
Q = {(s, a): 0.0 for s in STATES for a in ACTIONS}
for episode in range(2000):
    s = START
    while s not in (GOAL, PIT):
        a = random.choice(list(ACTIONS)) if random.random() < 0.2 else max(ACTIONS, key=lambda b: Q[(s, b)])
        n, r, done = step(s, a)
        target = r if done else r + GAMMA * max(Q[(n, b)] for b in ACTIONS)
        Q[(s, a)] += 0.5 * (target - Q[(s, a)])
        s = n
print("Q-learning greedy path:  %s (total reward %d)" % greedy_path(lambda s: max(ACTIONS, key=lambda b: Q[(s, b)])))
print(f"learned max Q at start = {max(Q[(START, a)] for a in ACTIONS):.4f}")
```

Output:

```text
value iteration converged after 7 sweeps; V(start) = 1.8098
   1.81  3.12  4.58  6.20
   3.12  1.81  0.00  8.00
   4.58   ###  8.00 10.00
   6.20  8.00 10.00  0.00
optimal path from start: vvv>>> (total reward 5)
Q-learning greedy path:  vvv>>> (total reward 5)
learned max Q at start = 1.8098
```

Values grow towards the goal: the squares next to it are worth 10 (stepping in earns +10 immediately), and the start is worth 1.81, the discounted value of five −1 steps followed by the +10 reward: $-1 - 0.9 - 0.81 - 0.729 - 0.6561 + 0.9^5 \times 10 = 1.8098$. The pit and goal show 0 because they are terminal: their rewards are collected on entering them. The optimal path goes down three squares and right three, avoiding the pit, for a total reward of 5. The Q-learning agent never saw the transition rules, yet after 2,000 episodes it follows the same path, and its learned value at the start, 1.8098, matches value iteration exactly.

### Example 2: A return and a Q-learning update by hand

**Return:** rewards $-1, -1, +10$ with $\gamma = 0.9$ give $G = -1 + 0.9(-1) + 0.81(10) = -1 - 0.9 + 8.1 = 6.2$.

**Q-learning update:** suppose $Q(s, a) = 2.0$, the agent receives $r = -1$, the best action value in the next state is 5.0, $\gamma = 0.9$, and $\alpha = 0.5$.

- Target: $r + \gamma\max_{a'}Q(s', a') = -1 + 0.9 \times 5.0 = 3.5$.
- TD error: $3.5 - 2.0 = 1.5$.
- New value: $2.0 + 0.5 \times 1.5 = 2.75$.

The estimate moves halfway towards the target; repeated over many experiences, these updates converge to $Q^*$ under suitable conditions (every state-action pair visited infinitely often and a decaying learning rate).

## Applications

- **Games:** AlphaGo, AlphaZero, and agents for video games.
- **Robotics:** learning locomotion and manipulation, often in simulation first.
- **Recommendation and advertising:** optimising long-term engagement rather than single clicks.
- **Operations:** data-centre cooling, inventory control, and traffic signal timing.
- **Language models:** reinforcement learning from human feedback (RLHF) aligns model outputs with human preferences.

## Common mistakes

- **Confusing reward with return.** The reward is one step's feedback; the return is the discounted sum.
- **Never exploring.** A purely greedy agent can lock onto a poor action forever.
- **Designing rewards carelessly.** Agents exploit loopholes in reward definitions.
- **Using $\gamma = 1$ in continuing tasks.** Returns can become infinite.
- **Mixing up Q-learning and SARSA.** Q-learning uses the best next action; SARSA uses the action actually taken.

## Revision notes

- Loop: state, action, reward, next state; maximise return $G_t = \sum\gamma^k r_{t+k+1}$.
- MDP $(S, A, P, R, \gamma)$; Markov property.
- $V^\pi$, $Q^\pi$; Bellman optimality equations; greedy policy from $Q^*$.
- Value iteration and policy iteration when the model is known.
- Q-learning: $Q \leftarrow Q + \alpha[r + \gamma\max Q(s', \cdot) - Q]$, off-policy; SARSA on-policy.
- $\varepsilon$-greedy exploration; deep RL (DQN, policy gradients, actor-critic); reward hacking.

## Practice questions

:::question basic
Compute the return of the rewards 1, 1, 1 with $\gamma = 0.5$.
:::answer
$G = 1 + 0.5 \times 1 + 0.25 \times 1 = 1.75$.
:::

:::question basic
What is the exploration-exploitation trade-off, and how does $\varepsilon$-greedy handle it?
:::answer
The agent must choose between exploiting the action it currently believes is best and exploring other actions that might turn out better. $\varepsilon$-greedy exploits most of the time but, with probability $\varepsilon$, takes a random action, so every action keeps being tried; $\varepsilon$ is often reduced over time as knowledge improves.
:::

:::question intermediate
$Q(s, a) = 4$, reward $r = 2$, $\max_{a'}Q(s', a') = 6$, $\gamma = 0.9$, $\alpha = 0.1$. Perform the Q-learning update.
:::answer
Target $= 2 + 0.9 \times 6 = 7.4$. TD error $= 7.4 - 4 = 3.4$. New $Q(s, a) = 4 + 0.1 \times 3.4 = 4.34$.
:::

:::question intermediate
What is the difference between on-policy and off-policy learning? Name one algorithm of each kind.
:::answer
An on-policy method learns the value of the policy it is actually following, including its exploratory actions; SARSA is on-policy. An off-policy method learns about a different target policy, usually the greedy optimal one, from data generated by its behaviour policy; Q-learning is off-policy because its update uses the maximum over next actions regardless of what is taken.
:::

:::question advanced
Why does value iteration converge, and what does the discount factor have to do with it?
:::answer
The Bellman optimality update is a contraction in the maximum norm: applying it to two value functions reduces the largest difference between them by at least a factor of $\gamma$. Repeated application therefore shrinks the distance to the unique fixed point $V^*$ geometrically, by $\gamma$ per sweep. With $\gamma$ close to 1, convergence is slower because each sweep shrinks the error less, and with $\gamma = 1$ (in continuing tasks) the guarantee can fail.
:::

## Further learning

- **Next:** *Multilayer Perceptron & Matrix Algebra* in Deep Learning begins the neural networks used in deep reinforcement learning.
- **Related:** *Minimax & Alpha-Beta Pruning* in Artificial Intelligence covers search in two-player games.
