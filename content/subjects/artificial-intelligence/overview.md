Artificial intelligence is the study of building agents that perceive their environment and act to achieve goals. Long before today's large language models, AI developed a toolkit of ideas that are still in daily use: search algorithms that plan routes and solve puzzles, logic that lets programs reason from facts, probabilistic models that reason under uncertainty, and planners that sequence actions. This subject teaches that classical foundation.

It begins with the history and goals of AI and the agent framework, including the PEAS description of a task environment and the main types of agent. The search modules formulate problems as state spaces and compare uninformed strategies such as breadth-first and depth-first search with informed A* search and its admissible heuristics, then cover constraint satisfaction problems. Adversarial search explains minimax and alpha-beta pruning for games. The reasoning modules cover knowledge representation and ontologies, propositional logic, first-order logic, and resolution, followed by Bayesian networks for reasoning under uncertainty. The subject closes with classical planning with STRIPS and with the ethics of AI: bias, fairness, and explainability.

Lessons trace algorithms step by step on small problems, so you can see exactly which node is expanded and why.

## What you will learn
- Explain the goals and history of AI and describe tasks with the PEAS framework
- Classify agents as reflex, model-based, goal-based, utility-based, or learning agents
- Formulate problems as state spaces and compare uninformed search strategies by completeness, optimality, and cost
- Apply A* search and prove when a heuristic is admissible and consistent
- Solve constraint satisfaction problems with backtracking, constraint propagation, and heuristics
- Play two-player games optimally with minimax and speed it up with alpha-beta pruning
- Represent knowledge with ontologies and logic, and draw conclusions with inference and resolution
- Model uncertain domains with Bayesian networks and compute probabilistic queries
- Represent planning problems in STRIPS and search for plans forwards and backwards
- Identify sources of bias in AI systems and explain approaches to fairness and explainability

## Prerequisites
- Programming experience, ideally in Python
- Data structures: queues, stacks, priority queues, trees, and graphs
- Basic probability, such as conditional probability and Bayes' theorem

## Glossary
- **Agent**: anything that perceives its environment through sensors and acts through actuators
- **PEAS**: Performance measure, Environment, Actuators, Sensors; a description of a task
- **State space**: the set of all states reachable from the initial state by actions
- **Heuristic**: an estimate of the cost from a state to the nearest goal
- **Admissible heuristic**: a heuristic that never overestimates the true cost
- **A* search**: best-first search ordered by path cost plus heuristic estimate
- **Constraint satisfaction problem**: a problem of assigning values to variables subject to constraints
- **Minimax**: a decision rule for two-player games that assumes the opponent plays optimally
- **Alpha-beta pruning**: skipping branches of a game tree that cannot affect the minimax decision
- **First-order logic**: logic with objects, predicates, functions, and quantifiers
- **Resolution**: an inference rule that proves statements by deriving a contradiction
- **Bayesian network**: a directed graph encoding conditional dependencies between random variables
- **STRIPS**: a planning language describing actions by preconditions and effects

## Further reading
- Stuart Russell and Peter Norvig, *Artificial Intelligence: A Modern Approach* (Pearson)
- David L. Poole and Alan K. Mackworth, *Artificial Intelligence: Foundations of Computational Agents* (Cambridge University Press)
- Nils J. Nilsson, *The Quest for Artificial Intelligence* (Cambridge University Press)
