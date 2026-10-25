"""
LuminaLearn AI — Analogy Specialist Agent.
Module: ai/agents/analogy_specialist.py

Translates abstract concepts into everyday metaphors. Every analogy ships with an explicit
mapping and a "where it breaks" note so learners don't over-extend it.
"""

from dataclasses import dataclass

from ai.agents.base import AgentContext, SpecialistAgent
from ai.agents.schema import AgentDraft
from ai.prompts.templates import ANALOGY_SPECIALIST


@dataclass(frozen=True)
class Analogy:
    concept: str
    keywords: tuple[str, ...]
    picture: str
    mapping: tuple[tuple[str, str], ...]
    breaks: str
    question: str


ANALOGIES: tuple[Analogy, ...] = (
    Analogy(
        concept="Dijkstra's algorithm",
        keywords=("dijkstra", "shortest path", "weighted graph"),
        picture=(
            "Pour water into a network of pipes at one junction. The water spreads outward, and the first moment "
            "it reaches any junction tells you that junction's shortest distance from the tap. Junctions that are "
            "already wet never get a faster arrival later."
        ),
        mapping=(("the tap", "the source vertex"), ("pipe length", "edge weight"),
                 ("first arrival time", "shortest distance"), ("a wet junction", "a finalized vertex")),
        breaks="A negative-weight edge would be a pipe that delivers water before it was poured, which is exactly why Dijkstra forbids negative weights.",
        question="In the pipe picture, what would a negative-weight edge mean, and why does it break the 'first arrival is final' rule?",
    ),
    Analogy(
        concept="Mutex locks",
        keywords=("mutex", "lock", "critical section", "race condition", "semaphore"),
        picture=(
            "A café has one restroom and one key on a big wooden paddle. You take the key, use the room, and hang "
            "the key back. Anyone else who needs the room waits at the counter until the key returns."
        ),
        mapping=(("the restroom", "the critical section"), ("the key", "the mutex"),
                 ("taking the key", "acquire()"), ("hanging it back", "release()"), ("waiting customers", "blocked threads")),
        breaks="A real queue is fair, but many mutexes are not: whichever waiting thread grabs the key first wins, so some threads can starve.",
        question="What happens to everyone waiting if a customer leaves with the key in their pocket?",
    ),
    Analogy(
        concept="Linear transformations",
        keywords=("linear transformation", "linear map", "matrix multiplication", "transformation matrix"),
        picture=(
            "Draw a grid on a rubber sheet pinned at its center, then stretch, rotate or shear the sheet. However "
            "you pull it, the grid lines stay straight, parallel and evenly spaced, and the pin never moves."
        ),
        mapping=(("the rubber sheet", "the vector space"), ("the pin", "the origin, which maps to itself"),
                 ("where the two grid arrows land", "the columns of the matrix"), ("straight, even grid lines", "linearity")),
        breaks="Real rubber can bend lines into curves; a linear transformation never can, and it cannot move the pin either.",
        question="If you only know where the two basic grid arrows land, why do you already know where every other point goes?",
    ),
    Analogy(
        concept="Recursion",
        keywords=("recursion", "recursive", "base case", "call stack", "factorial"),
        picture=(
            "You're in a dark cinema queue and want to know your position. You ask the person ahead; they ask the "
            "person ahead of them, and so on, until the first person, who knows they're number one. Each answer "
            "travels back down the line, plus one at every step."
        ),
        mapping=(("asking the person ahead", "the recursive call"), ("the first person", "the base case"),
                 ("everyone waiting for an answer", "frames on the call stack"), ("adding one on the way back", "combining results as the stack unwinds")),
        breaks="People in a queue can each wait as long as needed, but a computer's call stack has a size limit, so very deep recursion overflows.",
        question="What would happen in the queue if the first person also asked someone ahead of them?",
    ),
    Analogy(
        concept="Gradient descent",
        keywords=("gradient descent", "learning rate", "optimizer", "loss function", "minimize"),
        picture=(
            "You're on a mountain in thick fog and want to reach the valley. You can't see far, but you can feel "
            "which way the ground slopes under your boots, so you take a step downhill, feel again, and repeat."
        ),
        mapping=(("your position", "the parameter values"), ("altitude", "the loss"),
                 ("the slope under your boots", "the gradient"), ("stride length", "the learning rate")),
        breaks="Real valleys are obvious once the fog lifts; a loss surface can have many small dips, so gradient descent may settle in a local minimum.",
        question="What would happen if your stride were longer than the valley is wide?",
    ),
    Analogy(
        concept="Eigenvectors",
        keywords=("eigenvector", "eigenvalue", "eigen"),
        picture=(
            "Spin a globe. Every point on its surface swings to a new direction, except the points on the axis: "
            "they stay pointing exactly where they were."
        ),
        mapping=(("spinning the globe", "applying the matrix"), ("the axis", "an eigenvector's direction"),
                 ("how much the axis points stretch", "the eigenvalue (1 for a pure rotation)")),
        breaks="A spinning globe only has one fixed axis and no stretching; general matrices can have several eigen-directions that stretch by different amounts.",
        question="If a transformation doubled the length of the axis arrows without turning them, what would the eigenvalue be?",
    ),
    Analogy(
        concept="Bayes' theorem",
        keywords=("bayes", "posterior", "prior", "likelihood", "conditional probability", "base rate"),
        picture=(
            "Your smoke alarm beeps. That makes a fire more likely than it was a minute ago, but how much depends "
            "on how rare kitchen fires are and how often that alarm beeps at burnt toast."
        ),
        mapping=(("how rare fires are", "the prior P(fire)"), ("the alarm going off", "the evidence"),
                 ("how reliably fires trigger it", "the likelihood P(beep | fire)"), ("your updated worry", "the posterior P(fire | beep)")),
        breaks="Real alarms give you more clues, like the smell of smoke; Bayes' theorem only updates on the evidence you feed it.",
        question="If the alarm went off at burnt toast every morning, how should that change your reaction to a beep?",
    ),
    Analogy(
        concept="Hash tables",
        keywords=("hash table", "hash map", "hashing", "dictionary lookup", "collision"),
        picture=(
            "A library where a book's title, run through a formula, tells you its exact shelf number. You walk "
            "straight to the shelf instead of scanning every aisle. When two titles land on the same shelf, they "
            "share a small basket."
        ),
        mapping=(("the formula", "the hash function"), ("the shelf number", "the array index"),
                 ("the shared basket", "a collision chain")),
        breaks="A library can add shelves overnight; a hash table must rehash everything into a bigger array when it gets too full.",
        question="What happens to lookup time if a bad formula sends almost every title to the same shelf?",
    ),
    Analogy(
        concept="Big-O notation",
        keywords=("big-o", "big o", "complexity", "asymptotic"),
        picture=(
            "At a party, greeting each guest once grows with the guest list, but shaking hands between every pair "
            "of guests grows much faster: double the guests and the handshakes roughly quadruple."
        ),
        mapping=(("guests", "the input size n"), ("greeting each guest", "an O(n) loop"),
                 ("every pair shaking hands", "an O(n^2) nested loop")),
        breaks="At a small party the handshakes might finish first anyway; Big-O only describes growth as the guest list gets huge.",
        question="What party activity would grow like O(log n)?",
    ),
    Analogy(
        concept="Binary search",
        keywords=("binary search", "bisection", "sorted array"),
        picture=(
            "Guessing a number between 1 and 100 when your friend says 'higher' or 'lower'. Start at 50 and every "
            "guess throws away half of what's left."
        ),
        mapping=(("the range of numbers", "the sorted array"), ("guessing the middle", "probing the midpoint"),
                 ("'higher' or 'lower'", "comparing with the target")),
        breaks="Your friend can answer about any number; binary search only works when the data is already sorted.",
        question="How many guesses do you need, at most, for numbers between 1 and 1,000?",
    ),
    Analogy(
        concept="Derivatives",
        keywords=("derivative", "rate of change", "slope", "differentiat"),
        picture=(
            "A car's speedometer shows how fast your position is changing right now, not your average speed for "
            "the whole trip."
        ),
        mapping=(("position on the road", "the function"), ("the speedometer reading", "the derivative"),
                 ("average speed for a stretch", "the slope of a secant line")),
        breaks="A speedometer always has a reading, but functions with sharp corners have no derivative at the corner.",
        question="If the speedometer reads zero for an instant at the top of a hill, what does that suggest about the position graph?",
    ),
    Analogy(
        concept="Integrals",
        keywords=("integral", "integration", "area under", "accumulat"),
        picture=(
            "Filling a bathtub while the faucet's flow keeps changing. The total water in the tub is everything the "
            "faucet delivered, moment by moment, added up."
        ),
        mapping=(("the flow rate over time", "the integrand f(t)"), ("water in the tub", "the integral"),
                 ("opening the drain", "negative values of f")),
        breaks="Water can't be negative, but an integral can be, when the function dips below the axis.",
        question="If the faucet ran at a constant rate, what shape would the area under the flow graph be?",
    ),
    Analogy(
        concept="Deadlock",
        keywords=("deadlock", "circular wait", "coffman"),
        picture=(
            "Four cars arrive at a four-way stop at once, and each driver politely waits for the car on their right. "
            "Nobody moves, forever."
        ),
        mapping=(("each car", "a process"), ("the intersection quadrant it needs", "a resource"),
                 ("waiting for the car on the right", "circular wait")),
        breaks="Drivers eventually wave each other through; processes can't negotiate unless you design a way for them to.",
        question="Which simple traffic rule would break the circular wait?",
    ),
    Analogy(
        concept="Caching",
        keywords=("cache", "caching", "memoiz", "lru"),
        picture=(
            "You keep salt and pepper on the counter instead of in the basement pantry. The counter is small, so "
            "rarely used spices go back downstairs."
        ),
        mapping=(("the counter", "the cache"), ("the basement pantry", "main memory or disk"),
                 ("putting rarely used spices away", "the eviction policy")),
        breaks="You can see your counter at a glance; a cache needs a lookup structure to know what it holds.",
        question="Which spices would an LRU policy move back to the pantry first?",
    ),
    Analogy(
        concept="Dynamic programming",
        keywords=("dynamic programming", "memoization", "overlapping subproblems", "tabulation"),
        picture=(
            "Doing a long homework set where later questions reuse earlier answers. Writing each answer on a sticky "
            "note means you never redo the same calculation twice."
        ),
        mapping=(("each sticky note", "a stored subproblem answer"), ("checking notes first", "the memo lookup"),
                 ("working from question 1 upward", "bottom-up tabulation")),
        breaks="Sticky notes only help if questions really repeat; without overlapping subproblems, dynamic programming saves nothing.",
        question="In a naive Fibonacci, which value would end up on the most-read sticky note?",
    ),
    Analogy(
        concept="Neural networks",
        keywords=("neural network", "neuron", "deep learning", "backprop", "weights"),
        picture=(
            "A stage lit by hundreds of dimmer switches. You want a particular scene, so you nudge each dimmer a "
            "little in whichever direction makes the stage look closer to the target picture, over and over."
        ),
        mapping=(("the dimmer settings", "the weights"), ("the lit stage", "the network's output"),
                 ("how far from the target picture", "the loss"), ("deciding which dimmers to nudge", "back-propagation")),
        breaks="Dimmers each control one light; a network's weights interact, so nudging one changes what every other one should be.",
        question="Why would nudging every dimmer by a huge amount at once make the scene worse?",
    ),
)


def select_analogy(text: str) -> Analogy | None:
    lowered = text.lower()
    best: Analogy | None = None
    best_hits = 0
    for analogy in ANALOGIES:
        hits = sum(1 for keyword in analogy.keywords if keyword in lowered)
        if hits > best_hits:
            best, best_hits = analogy, hits
    return best


class AnalogySpecialistAgent(SpecialistAgent):
    name = "analogy_specialist"

    def role_prompt(self, ctx: AgentContext) -> str:
        return ANALOGY_SPECIALIST

    def offline(self, ctx: AgentContext) -> AgentDraft:
        analogy = select_analogy(f"{ctx.request.topic or ''} {ctx.request.message}")
        if analogy is None:
            topic = ctx.topic
            return AgentDraft(
                text=(
                    f"Here's a lens that works for many abstract ideas: picture **{topic}** as a machine on a workbench. "
                    "It takes something in, applies one rule, and hands something back. Naming those three parts "
                    "usually makes the idea feel physical.\n\n"
                    f"**Which part of {topic} feels most abstract to you?** Tell me and I'll find a sharper analogy."
                )
            )
        if ctx.is_voice:
            return AgentDraft(text=f"{analogy.picture} {analogy.breaks} {analogy.question}")
        mapping = "\n".join(f"- **{left}** is {right}" for left, right in analogy.mapping)
        return AgentDraft(
            text=(
                f"{analogy.picture}\n\n**How it maps**\n{mapping}\n\n**Where it breaks:** {analogy.breaks}\n\n"
                f"**{analogy.question}**"
            )
        )
