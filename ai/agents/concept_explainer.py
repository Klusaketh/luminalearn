"""
LuminaLearn AI — Concept Explainer Agent (VARK Specialist).
Module: ai/agents/concept_explainer.py

Explains a concept in the learner's modality:
  * Visual       -> a Mermaid flowchart plus a walkthrough of it.
  * Auditory     -> narration written for the ear, with a mnemonic.
  * Read/Write   -> structured notes with a worked example.
  * Kinesthetic  -> a predict-observe experiment and an interactive lab on screen.
"""

import re
from dataclasses import dataclass

from ai.agents.base import AgentContext, SpecialistAgent
from ai.agents.guardrails import split_sentences
from ai.agents.schema import AgentDraft, InteractiveWidget
from ai.prompts.templates import CONCEPT_EXPLAINER, MODALITY_LABELS, MODALITY_RULES


@dataclass(frozen=True)
class TopicKit:
    """Curated teaching assets for a frequently tutored concept. `title` reads correctly mid-sentence."""

    key: str
    title: str
    keywords: tuple[str, ...]
    definition: str
    key_ideas: tuple[str, ...]
    nodes: tuple[tuple[str, str], ...]
    edges: tuple[tuple[str, str, str], ...]
    mnemonic: str
    example: str
    experiment: tuple[str, ...]
    check: str
    widget: InteractiveWidget | None = None


TOPIC_KITS: tuple[TopicKit, ...] = (
    TopicKit(
        key="recursion",
        title="recursion",
        keywords=("recursion", "recursive", "base case", "factorial", "fibonacci", "call stack"),
        definition="Recursion solves a problem by solving a smaller copy of the same problem, until a base case is small enough to answer directly.",
        key_ideas=(
            "The base case stops the recursion and returns an answer directly.",
            "The recursive case shrinks the problem and calls the same function on the smaller input.",
            "Each pending call waits on the call stack, and results combine as the stack unwinds.",
        ),
        nodes=(("A", "Call with input n"), ("B", "Is n the base case"), ("C", "Return answer directly"),
               ("D", "Call itself on smaller n"), ("E", "Combine with result"), ("F", "Stack unwinds")),
        edges=(("A", "B", ""), ("B", "C", "yes"), ("B", "D", "no"), ("D", "A", "smaller"), ("D", "E", "returns"), ("E", "F", "")),
        mnemonic="Base, Break, Build: know the base case, break the problem smaller, build the answer back up.",
        example="`factorial(3)` becomes `3 * factorial(2)`, then `3 * 2 * factorial(1)`, and the base case `factorial(1) = 1` lets the stack unwind to `6`.",
        experiment=(
            "Predict how many stack frames `factorial(4)` needs before it starts returning.",
            "Use the call-stack lab below: set the depth slider to 4 and watch frames push, then pop.",
            "Now remove the base case in your head: what would the lab show instead?",
        ),
        check="What would happen to the call stack if the base case could never be reached?",
        widget="recursion",
    ),
    TopicKit(
        key="definite_integral",
        title="the definite integral",
        keywords=("integral", "integrate", "antiderivative", "area under", "fundamental theorem"),
        definition="A definite integral adds up a quantity's accumulated change; by the Fundamental Theorem of Calculus it equals F(b) - F(a) for any antiderivative F.",
        key_ideas=(
            "Integration is the reverse of differentiation: an antiderivative F has F' = f.",
            "The definite integral from a to b measures signed area under f between the limits.",
            "Evaluate it by finding F, then subtracting its value at a from its value at b.",
        ),
        nodes=(("A", "Integrand f of x"), ("B", "Find antiderivative F"), ("C", "Evaluate F at b"),
               ("D", "Evaluate F at a"), ("E", "Subtract F of b minus F of a")),
        edges=(("A", "B", "reverse power rule"), ("B", "C", ""), ("B", "D", ""), ("C", "E", ""), ("D", "E", "")),
        mnemonic="Anti, Plug, Subtract: find the antiderivative, plug in both limits, subtract.",
        example="$\\int_0^1 2x\\,dx$: the antiderivative is $x^2$, so the value is $1^2 - 0^2 = 1$, the area of a triangle with base 1 and height 2.",
        experiment=(
            "Sketch $f(x) = 2x$ from $0$ to $1$ and predict the shaded area before computing anything.",
            "Split the region into 4 rectangles and add their areas; then try 8 rectangles.",
            "Compare both sums with $F(1) - F(0)$. What happens as the rectangles get thinner?",
        ),
        check="Why does it not matter which antiderivative you pick, given that they differ by a constant?",
    ),
    TopicKit(
        key="derivative",
        title="the derivative",
        keywords=("derivative", "differentiate", "slope", "rate of change", "chain rule", "product rule"),
        definition="The derivative measures how fast a function changes at a single point: the slope of its tangent line.",
        key_ideas=(
            "It is the limit of average rates of change over shrinking intervals.",
            "Rules like the power, product and chain rules let you compute it without limits.",
            "A positive derivative means increasing, negative means decreasing, zero flags a possible peak or valley.",
        ),
        nodes=(("A", "Function f of x"), ("B", "Secant slope over h"), ("C", "Let h shrink to 0"),
               ("D", "Tangent slope f prime"), ("E", "Rules shortcut the limit")),
        edges=(("A", "B", ""), ("B", "C", ""), ("C", "D", "limit"), ("E", "D", "faster route")),
        mnemonic="Zoom until it's straight: any smooth curve looks like a line when you zoom in far enough, and that line's slope is the derivative.",
        example="For $f(x) = x^2$, the slope between $x$ and $x + h$ is $2x + h$, which approaches $2x$ as $h \\to 0$.",
        experiment=(
            "Pick two points on $y = x^2$ near $x = 1$ and compute the slope between them.",
            "Move the second point closer three times, recomputing each time.",
            "Predict the value the slopes approach, then check it against $2x$ at $x = 1$.",
        ),
        check="What does a derivative of zero tell you about the shape of a graph at that point?",
    ),
    TopicKit(
        key="eigen",
        title="eigenvalues and eigenvectors",
        keywords=("eigenvalue", "eigenvector", "eigen", "characteristic polynomial", "diagonaliz"),
        definition="An eigenvector of a matrix is a direction the matrix only stretches, never turns; the stretch factor is its eigenvalue.",
        key_ideas=(
            "They satisfy $A\\mathbf{x} = \\lambda \\mathbf{x}$ for a nonzero vector $\\mathbf{x}$.",
            "Eigenvalues are the roots of $\\det(A - \\lambda I) = 0$.",
            "The eigenvalues of a matrix add up to its trace and multiply to its determinant.",
        ),
        nodes=(("A", "Matrix A"), ("B", "Form A minus lambda I"), ("C", "Determinant equals 0"),
               ("D", "Solve for lambda"), ("E", "Null space gives eigenvectors")),
        edges=(("A", "B", ""), ("B", "C", ""), ("C", "D", "characteristic polynomial"), ("D", "E", "each lambda")),
        mnemonic="Shift, Determine, Solve: shift by lambda, take the determinant, solve the polynomial.",
        example="For $A = \\begin{pmatrix} 2 & 0 \\\\ 0 & 3 \\end{pmatrix}$ the axes are eigenvectors, with eigenvalues $2$ and $3$.",
        experiment=(
            "Draw a grid and apply $A = \\begin{pmatrix} 2 & 0 \\\\ 0 & 1 \\end{pmatrix}$ to a few arrows.",
            "Mark which arrows keep their direction and which ones tilt.",
            "Predict the eigenvalues from how much the untilted arrows stretched, then verify with the determinant.",
        ),
        check="Why can't the zero vector count as an eigenvector?",
    ),
    TopicKit(
        key="bayes",
        title="Bayes' theorem",
        keywords=("bayes", "posterior", "prior", "likelihood", "conditional probability", "base rate"),
        definition="Bayes' theorem updates a prior belief with new evidence: $P(A \\mid B) = P(B \\mid A)\\,P(A) / P(B)$.",
        key_ideas=(
            "The prior $P(A)$ is what you believed before the evidence.",
            "The likelihood $P(B \\mid A)$ is how expected the evidence is if $A$ is true.",
            "The evidence $P(B)$ normalizes everything, and the posterior is the updated belief.",
        ),
        nodes=(("A", "Prior belief"), ("B", "Observe evidence"), ("C", "Weigh by likelihood"),
               ("D", "Normalize by evidence"), ("E", "Posterior belief")),
        edges=(("A", "C", ""), ("B", "C", ""), ("C", "D", ""), ("D", "E", ""), ("E", "A", "next update")),
        mnemonic="Prior times Likelihood, over Evidence: P, L, over E.",
        example="If 1% of people have a condition and a test catches 90% of cases with a 5% false-positive rate, a positive result means only about $0.009 / 0.0585 \\approx 15\\%$ chance of having it.",
        experiment=(
            "Open the Bayes lab below and set the prior to 1%.",
            "Predict the posterior after a positive test before moving any slider.",
            "Now raise the prior to 20% and watch how much the same evidence moves the posterior.",
        ),
        check="Why does a rare condition make even an accurate test produce many false alarms?",
        widget="bayes",
    ),
    TopicKit(
        key="gradient_descent",
        title="gradient descent",
        keywords=("gradient descent", "learning rate", "loss", "optimizer", "optimization", "backprop", "converge"),
        definition="Gradient descent minimizes a function by repeatedly stepping in the direction of steepest decrease, the negative gradient.",
        key_ideas=(
            "The gradient points uphill, so the update subtracts it: $\\theta \\leftarrow \\theta - \\eta \\nabla L$.",
            "The learning rate $\\eta$ sets the step size: too small crawls, too large overshoots.",
            "Stochastic variants estimate the gradient from mini-batches to save computation.",
        ),
        nodes=(("A", "Start at theta"), ("B", "Compute gradient"), ("C", "Step against it"),
               ("D", "Loss decreased"), ("E", "Stop at minimum")),
        edges=(("A", "B", ""), ("B", "C", "times eta"), ("C", "D", ""), ("D", "B", "repeat"), ("D", "E", "converged")),
        mnemonic="Slope, Step, Shrink: read the slope, step downhill, watch the loss shrink.",
        example="Minimizing $\\theta^2$ from $\\theta = 4$ with $\\eta = 0.25$ halves $\\theta$ each step: $4 \\to 2 \\to 1 \\to 0.5$.",
        experiment=(
            "In the gradient-descent lab below, predict what happens with a learning rate of 0.1, then run it.",
            "Raise the learning rate to 0.9, then 1.1, predicting each time.",
            "Find the largest rate that still converges. Why does it diverge beyond that?",
        ),
        check="What happens to the steps when the learning rate is larger than the curve can tolerate?",
        widget="gradient_descent",
    ),
    TopicKit(
        key="complexity",
        title="Big-O complexity",
        keywords=("big-o", "big o", "complexity", "asymptotic", "runtime", "o(n"),
        definition="Big-O describes how an algorithm's cost grows with input size, keeping only the dominant term.",
        key_ideas=(
            "Count how many times the busiest line runs as a function of $n$.",
            "Drop constants and lower-order terms: $3n^2 + 5n$ is $O(n^2)$.",
            "Nested loops multiply, sequential loops add, and halving the input gives $\\log n$.",
        ),
        nodes=(("A", "Algorithm"), ("B", "Find busiest line"), ("C", "Count runs in n"),
               ("D", "Keep dominant term"), ("E", "Big-O class")),
        edges=(("A", "B", ""), ("B", "C", ""), ("C", "D", "drop constants"), ("D", "E", "")),
        mnemonic="Count the busiest line, keep the biggest term.",
        example="Checking every pair among $n$ items runs about $n^2 / 2$ comparisons, which is $O(n^2)$.",
        experiment=(
            "Time a loop that checks every pair in a list of 1,000 items, then 2,000.",
            "Predict the ratio of the two times before running it.",
            "Repeat with a single loop. How do the ratios compare?",
        ),
        check="If doubling the input quadruples the runtime, which complexity class are you seeing?",
    ),
    TopicKit(
        key="graph_search",
        title="Dijkstra's shortest paths",
        keywords=("dijkstra", "shortest path", "graph", "bfs", "breadth-first", "vertex", "vertices"),
        definition="Dijkstra's algorithm finds shortest paths from a source by always finalizing the closest unvisited vertex.",
        key_ideas=(
            "Tentative distances start at 0 for the source and infinity elsewhere.",
            "Relaxing an edge asks: is the path through this vertex shorter?",
            "Nonnegative weights guarantee the closest unvisited vertex is final.",
        ),
        nodes=(("A", "Set source to 0"), ("B", "Pick closest unvisited"), ("C", "Relax its edges"),
               ("D", "Mark it final"), ("E", "All vertices final")),
        edges=(("A", "B", ""), ("B", "C", ""), ("C", "D", ""), ("D", "B", "repeat"), ("D", "E", "done")),
        mnemonic="Closest first, then relax.",
        example="With $S \\to A = 4$, $S \\to B = 1$ and $B \\to A = 2$, visiting $B$ first improves $A$ from $4$ to $3$.",
        experiment=(
            "Draw five towns connected by roads labelled with travel times.",
            "Predict the fastest route from one town to the farthest town.",
            "Run Dijkstra by hand, crossing out each town as it is finalized. Did your prediction hold?",
        ),
        check="Why would a negative road length break the 'closest first' guarantee?",
    ),
    TopicKit(
        key="hash_table",
        title="hash tables",
        keywords=("hash table", "hash map", "hashing", "dictionary", "collision"),
        definition="A hash table stores values in an array slot chosen by a hash of the key, giving constant-time lookups on average.",
        key_ideas=(
            "A hash function turns a key into an array index.",
            "Collisions, where two keys share a slot, are handled by chaining or probing.",
            "Keeping the load factor low keeps operations near $O(1)$.",
        ),
        nodes=(("A", "Key"), ("B", "Hash function"), ("C", "Array index"), ("D", "Slot empty"),
               ("E", "Store value"), ("F", "Resolve collision")),
        edges=(("A", "B", ""), ("B", "C", ""), ("C", "D", ""), ("D", "E", "yes"), ("D", "F", "no"), ("F", "E", "")),
        mnemonic="Hash, Bucket, Compare.",
        example="With 8 slots and $h(k) = k \\bmod 8$, the keys $3$ and $11$ both land in slot $3$, so they collide.",
        experiment=(
            "Draw 8 boxes and hash the numbers 5, 13, 21 and 6 with $k \\bmod 8$.",
            "Predict which boxes collide before placing them.",
            "Double the boxes to 16 and repeat. What happened to the collisions?",
        ),
        check="Why does a hash table's worst case degrade to $O(n)$?",
    ),
    TopicKit(
        key="mutex",
        title="mutex locks",
        keywords=("mutex", "lock", "race condition", "critical section", "deadlock", "semaphore", "concurrency"),
        definition="A mutex lock lets only one thread at a time run a critical section, preventing race conditions on shared data.",
        key_ideas=(
            "A thread must acquire the lock before entering the critical section and release it after.",
            "Other threads block or spin until the lock is free.",
            "Acquiring several locks in inconsistent orders can deadlock.",
        ),
        nodes=(("A", "Thread wants shared data"), ("B", "Lock free"), ("C", "Acquire lock"),
               ("D", "Critical section"), ("E", "Release lock"), ("F", "Wait")),
        edges=(("A", "B", ""), ("B", "C", "yes"), ("B", "F", "no"), ("F", "B", "retry"), ("C", "D", ""), ("D", "E", "")),
        mnemonic="Lock, Work, Unlock: never leave the room without returning the key.",
        example="Two threads each running `count += 1` 1,000 times can finish below 2,000 without a lock, because their read-modify-write steps interleave.",
        experiment=(
            "Act it out: two people increment a number on one sheet of paper, reading it, then writing it back.",
            "Interleave the reads and writes on purpose. Predict the final number first.",
            "Add a rule that only the holder of a pen may read or write. What changes?",
        ),
        check="Which of the four Coffman conditions does a consistent lock ordering break?",
    ),
)


def select_kit(text: str) -> TopicKit | None:
    lowered = text.lower()
    best: TopicKit | None = None
    best_hits = 0
    for kit in TOPIC_KITS:
        hits = sum(1 for keyword in kit.keywords if keyword in lowered)
        if hits > best_hits:
            best, best_hits = kit, hits
    return best


def choose_widget(text: str) -> InteractiveWidget | None:
    """Picks the interactive lab that best matches the conversation."""
    kit = select_kit(text)
    if kit and kit.widget:
        return kit.widget
    lowered = text.lower()
    if any(k in lowered for k in ("probab", "evidence", "test result")):
        return "bayes"
    if any(k in lowered for k in ("stack", "loop", "function call")):
        return "recursion"
    return None


_LABEL_UNSAFE = re.compile(r"[()\[\]{}\"'|<>;:`$\\]")


def mermaid_label(text: str, max_words: int = 5) -> str:
    words = _LABEL_UNSAFE.sub(" ", text).split()
    return " ".join(words[:max_words]) or "Idea"


def mermaid_flowchart(nodes: tuple[tuple[str, str], ...], edges: tuple[tuple[str, str, str], ...]) -> str:
    lines = ["flowchart TD"]
    declared: set[str] = set()
    labels = dict(nodes)
    for source, target, label in edges:
        left = source if source in declared else f"{source}[{mermaid_label(labels[source], 6)}]"
        right = target if target in declared else f"{target}[{mermaid_label(labels[target], 6)}]"
        declared.update((source, target))
        arrow = f" -->|{mermaid_label(label, 4)}| " if label else " --> "
        lines.append(f"  {left}{arrow}{right}")
    return "\n".join(lines)


class ConceptExplainerAgent(SpecialistAgent):
    name = "concept_explainer"

    def role_prompt(self, ctx: AgentContext) -> str:
        modality = ctx.request.modality
        return CONCEPT_EXPLAINER.format(modality_label=MODALITY_LABELS[modality], modality_rules=MODALITY_RULES[modality])

    def offline(self, ctx: AgentContext) -> AgentDraft:
        request = ctx.request
        kit = select_kit(f"{request.topic or ''} {request.message}")
        cite = " [1]" if ctx.chunks else ""
        if kit is None:
            return self._from_sources(ctx, cite)

        modality = "auditory" if ctx.is_voice else request.modality
        if modality == "visual":
            diagram = mermaid_flowchart(kit.nodes, kit.edges)
            walkthrough = "\n".join(f"- {idea}" for idea in kit.key_ideas)
            text = (
                f"Here is **{kit.title}** as a flow{cite}:\n\n```mermaid\n{diagram}\n```\n\n"
                f"{walkthrough}\n\n**Check yourself:** {kit.check}"
            )
        elif modality == "auditory":
            ideas = " ".join(kit.key_ideas)
            text = (
                f"Let's talk it through. {kit.definition} {ideas} "
                f"Here's a way to remember it. {kit.mnemonic} Say that back to yourself once. {kit.check}"
            )
        elif modality == "kinesthetic":
            steps = "\n".join(f"{i}. {step}" for i, step in enumerate(kit.experiment, 1))
            text = (
                f"Let's learn **{kit.title}** by doing it{cite}. Try this:\n\n{steps}\n\n"
                f"Write your prediction down before each step: the surprise is where the learning happens.\n\n"
                f"**Check yourself:** {kit.check}"
            )
        else:
            ideas = "\n".join(f"- {idea}" for idea in kit.key_ideas)
            text = (
                f"**{kit.definition}**{cite}\n\n### Key ideas\n{ideas}\n\n### Worked example\n{kit.example}\n\n"
                f"### Check yourself\n{kit.check}"
            )
        widget = (kit.widget or choose_widget(request.message)) if modality == "kinesthetic" else None
        return AgentDraft(text=text, interactive=widget)

    def _from_sources(self, ctx: AgentContext, cite: str) -> AgentDraft:
        """No curated kit: teach from the retrieved curriculum, or say honestly that none matched."""
        topic = ctx.topic
        if not ctx.chunks:
            return AgentDraft(
                text=(
                    f"I don't have verified course material on **{topic}** yet, so here is a general way in. "
                    f"Start by naming what {topic} takes as input, what rule it applies, and what it produces. "
                    "Then find one tiny example you can check by hand.\n\n"
                    f"**Which part of {topic} feels most abstract right now?**"
                )
            )
        sentences = split_sentences(ctx.chunks[0].content)
        definition, ideas = sentences[0], sentences[1:4]
        modality = "auditory" if ctx.is_voice else ctx.request.modality
        if modality == "visual":
            nodes = (("A", topic),) + tuple((chr(66 + i), idea) for i, idea in enumerate(ideas))
            edges = tuple(("A", chr(66 + i), "") for i in range(len(ideas)))
            diagram = mermaid_flowchart(nodes, edges) if edges else f"flowchart TD\n  A[{mermaid_label(topic)}]"
            bullets = "\n".join(f"- {idea}" for idea in ideas)
            text = f"Here is **{topic}** at a glance{cite}:\n\n```mermaid\n{diagram}\n```\n\n{bullets}\n\n**Which branch would you like to zoom into?**"
        elif modality == "auditory":
            text = f"Let's talk it through. {definition} {' '.join(ideas)} Which part should we slow down on?"
        elif modality == "kinesthetic":
            text = (
                f"Let's make **{topic}** concrete{cite}. {definition}\n\n"
                "Try this:\n\n1. Build the smallest example you can, on paper or in code.\n"
                "2. Change one input and predict the result before you check it.\n"
                "3. Write down what surprised you.\n\n**What did your smallest example look like?**"
            )
        else:
            bullets = "\n".join(f"- {idea}" for idea in ideas)
            text = f"**{definition}**{cite}\n\n### Key ideas\n{bullets}\n\n### Check yourself\nCan you explain {topic} in one sentence of your own?"
        interactive = choose_widget(f"{topic} {ctx.request.message}") if modality == "kinesthetic" else None
        return AgentDraft(text=text, interactive=interactive)
