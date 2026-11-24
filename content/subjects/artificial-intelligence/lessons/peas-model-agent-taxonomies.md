---
lesson: peas-model-agent-taxonomies
title: PEAS Model & Agent Taxonomies
summary: Intelligent agents and rationality, specifying task environments with the PEAS model, the properties that classify environments, and the hierarchy of agent designs from simple reflex agents to learning agents.
minutes: 35
type: theory
objectives:
  - Specify a task environment using Performance measure, Environment, Actuators, and Sensors
  - Classify environments as observable or not, deterministic or stochastic, episodic or sequential, static or dynamic, discrete or continuous, and single- or multi-agent
  - Compare simple reflex, model-based, goal-based, utility-based, and learning agents and choose a design for a given environment
review: ai-draft
---
## Introduction

An **agent** is anything that perceives its environment through **sensors** and acts on it through **actuators**: a robot vacuum, a chess program, a thermostat, a recommendation engine, or a tutoring system. Designing an agent starts with describing its task precisely: what counts as success, what world it lives in, and what it can sense and do. The PEAS model gives that description, and the properties of the environment decide which kind of agent design will work.

**Before you start:** you should know the rational-agent definition of AI from *Foundations of Artificial Intelligence*.

## Core theory

### Agents and rationality

The **agent function** maps every possible percept sequence to an action; the **agent program** implements that function on a physical machine. A **rational agent** chooses, for each percept sequence, the action expected to maximise its **performance measure**, given the evidence from its percepts and its built-in knowledge.

Rationality depends on four things: the performance measure, the agent's prior knowledge, the actions available, and the percepts so far. It is not omniscience: an agent that crosses a road after looking carefully is rational even if an unforeseeable object falls on it. Rational agents also gather information (look before crossing), learn from experience, and become **autonomous** by relying less on their designer's built-in knowledge.

### The PEAS description

- **Performance measure:** the criteria for success, defined in terms of the environment's states, not the agent's opinion of itself.
- **Environment:** the world the agent operates in.
- **Actuators:** the means of acting.
- **Sensors:** the means of perceiving.

Designing the performance measure needs care: a cleaning robot rewarded for "dirt collected" could learn to dump dirt and collect it again. It is better to measure what you actually want, such as a clean floor.

### Properties of environments

- **Fully vs partially observable:** can the sensors see the whole relevant state at each moment?
- **Single-agent vs multi-agent:** are other agents present, and are they competitive (chess) or cooperative (team robots)?
- **Deterministic vs stochastic:** is the next state completely determined by the current state and action?
- **Episodic vs sequential:** are decisions independent (classifying separate images), or do current actions affect future ones (playing a game)?
- **Static vs dynamic:** does the world change while the agent is deciding? It is **semi-dynamic** if only the score changes, as in chess with a clock.
- **Discrete vs continuous:** are states, time, percepts, and actions countable or continuous?
- **Known vs unknown:** does the agent know the rules (the outcomes of its actions)?

The hardest case is partially observable, multi-agent, stochastic, sequential, dynamic, continuous, and unknown, which describes driving a car in city traffic.

### Agent designs

1. **Simple reflex agents** choose actions from the current percept with condition-action rules ("if the car in front brakes, then brake"). They work only when the environment is fully observable.
2. **Model-based reflex agents** keep an **internal state** that tracks the parts of the world they cannot currently see, using a model of how the world evolves and how actions affect it.
3. **Goal-based agents** consider the future: they search or plan for action sequences that reach a goal.
4. **Utility-based agents** use a **utility function** to compare outcomes, handling trade-offs (speed against safety) and uncertainty by maximising **expected utility**.
5. **Learning agents** improve with experience. A **performance element** chooses actions, a **critic** reports how well the agent is doing against a fixed standard, a **learning element** improves the performance element, and a **problem generator** suggests exploratory actions.

## Worked examples

### Example 1: Reflex versus model-based agents in the vacuum world

The world has two squares, A and B, both dirty at the start. The agent senses only its own square and whether it is dirty. The performance measure awards one point per clean square at each time step and subtracts one point for each move, since moving uses energy.

```python
def simple_reflex(percept, memory):
    location, dirty = percept
    if dirty:
        return "Suck"
    return "Right" if location == "A" else "Left"


def model_based(percept, memory):
    location, dirty = percept
    memory[location] = "Clean"          # after this step the square will be clean
    if dirty:
        return "Suck"
    if memory.get("A") == "Clean" and memory.get("B") == "Clean":
        return "NoOp"
    return "Right" if location == "A" else "Left"


def run(agent, steps=8):
    world = {"A": True, "B": True}      # True means the square is dirty
    location, memory, score, actions = "A", {}, 0, []
    for _ in range(steps):
        action = agent((location, world[location]), memory)
        actions.append(action)
        if action == "Suck":
            world[location] = False
        elif action in ("Left", "Right"):
            location = "B" if action == "Right" else "A"
            score -= 1                                   # moving costs energy
        score += sum(not dirty for dirty in world.values())  # +1 per clean square
    return actions, score


for name, agent in [("simple reflex", simple_reflex), ("model-based", model_based)]:
    actions, score = run(agent)
    print(f"{name:13}: {' '.join(actions)}")
    print(f"{'':13}  performance score = {score}")
```

Output:

```text
simple reflex: Suck Right Suck Left Right Left Right Left
               performance score = 8
model-based  : Suck Right Suck NoOp NoOp NoOp NoOp NoOp
               performance score = 13
```

Both agents clean both squares in three steps. The simple reflex agent then shuttles back and forth forever, because its current percept ("this square is clean") never tells it that the other square is clean too. The model-based agent remembers what it has seen, knows both squares are clean, and stops, scoring 13 instead of 8. Memory pays off because the environment is **partially observable**. If dirt could reappear, stopping for ever would be wrong, and a good design would revisit squares occasionally: the right agent depends on the environment.

### Example 2: PEAS and environment properties

**An AI tutor for programming students:**

- **Performance:** improvement in assessment scores, correctness of explanations, time to mastery, student engagement.
- **Environment:** students, the curriculum and problem bank, the learning platform.
- **Actuators:** displaying explanations, hints, questions, and feedback; scheduling reviews.
- **Sensors:** typed questions, submitted code and answers, time on task, clicks.

Its environment is partially observable (a student's understanding is hidden), multi-agent (many students), stochastic (students respond unpredictably), sequential (today's hint affects tomorrow's learning), dynamic, and mostly discrete.

**Classifying familiar tasks:**

| Task | Observable | Agents | Deterministic | Episodic | Static | Discrete |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Crossword puzzle | Fully | Single | Yes | Sequential | Static | Yes |
| Chess with a clock | Fully | Multi | Yes | Sequential | Semi | Yes |
| Poker | Partially | Multi | No | Sequential | Static | Yes |
| Classifying X-ray images | Fully | Single | Yes | Episodic | Static | No |
| Driving a taxi | Partially | Multi | No | Sequential | Dynamic | No |

## Applications

- **Robotics:** warehouse robots and robot vacuums are model-based or goal-based agents.
- **Game AI:** non-player characters range from reflex rules to utility-based planners.
- **Recommendation systems:** learning agents that adapt to user feedback.
- **Autonomous vehicles:** utility-based agents in the hardest kind of environment.
- **Software agents:** trading bots, email filters, and tutoring systems.

## Common mistakes

- **Defining performance by the agent's own opinion.** Measure outcomes in the environment.
- **Rewarding the wrong thing.** A badly chosen performance measure leads to clever but useless behaviour.
- **Assuming rational means perfect.** Rationality maximises expected performance with the information available.
- **Using a reflex agent in a partially observable world.** Without memory, it can loop forever.
- **Confusing deterministic with fully observable.** A deterministic world can still be partially observable, and vice versa.

## Revision notes

- Agent: perceives through sensors, acts through actuators; agent function maps percept sequences to actions.
- Rational: maximises expected performance given percepts and knowledge; not omniscient.
- PEAS: Performance measure, Environment, Actuators, Sensors.
- Properties: observable, agents, deterministic, episodic, static, discrete, known.
- Designs: simple reflex, model-based reflex, goal-based, utility-based, learning agents.
- Learning agent parts: performance element, critic, learning element, problem generator.

## Practice questions

:::question basic
Give a PEAS description for an email spam filter.
:::answer
Performance: few legitimate emails marked as spam, most spam caught. Environment: the user's inbox and the stream of incoming email and senders. Actuators: moving messages to spam or inbox, flagging, notifying. Sensors: the incoming messages, including headers, text, links, attachments, and the user's corrections.
:::

:::question basic
What is the key difference between a simple reflex agent and a model-based reflex agent?
:::answer
A simple reflex agent decides using only the current percept. A model-based reflex agent maintains an internal state, updated by a model of how the world changes and how its actions affect it, so it can act sensibly when the current percept does not reveal everything relevant.
:::

:::question intermediate
Classify the task environment of an agent that plays poker against other players.
:::answer
Partially observable (opponents' cards are hidden), multi-agent and competitive, stochastic (card dealing is random), sequential (earlier bets affect later options), static during each decision unless there is a time limit, and discrete (cards, chips, and actions are countable).
:::

:::question intermediate
Why might a goal-based agent be insufficient for a delivery drone, so that a utility-based design is needed?
:::answer
A goal only distinguishes "delivered" from "not delivered". The drone must trade off speed, battery use, safety margins, and weather risks, and outcomes are uncertain. A utility function can rank different successful plans and, combined with probabilities, choose the plan with the highest expected utility.
:::

:::question advanced
An agent cleans a floor and is rewarded for "amount of dirt sucked up per hour". Explain what could go wrong and propose a better performance measure.
:::answer
A rational agent maximising this measure could learn to spill dirt and suck it up again, scoring highly while the floor never gets cleaner. The measure rewards activity instead of the outcome we care about. A better measure scores the state of the environment, for example the average cleanliness of the floor over time, with penalties for energy used and noise.
:::

## Further learning

- **Next:** *Problem Formulation & Uninformed Search* gives goal-based agents a way to plan.
- **Related:** *Reinforcement Learning Fundamentals* in Machine Learning studies learning agents that improve from rewards.
