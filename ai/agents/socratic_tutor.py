"""
LuminaLearn AI — Socratic Tutor Agent.
Module: ai/agents/socratic_tutor.py

Golden rule: never give the final answer. The tutor scaffolds with a three-tier hint
ladder (nudge -> scaffold -> parallel worked example) and always ends on a question.
"""

from dataclasses import dataclass

from ai.agents.base import AgentContext, SpecialistAgent, first_math_expression
from ai.agents.schema import HINT_TITLES, AgentDraft, Hint
from ai.agents.supervisor import ANSWER_DEMAND_CUES
from ai.prompts.templates import HINTS_MARKER, SOCRATIC_OUTPUT_FORMAT, SOCRATIC_TUTOR


@dataclass(frozen=True)
class Scaffold:
    """One problem family's hint ladder."""

    key: str
    label: str
    keywords: tuple[str, ...]
    nudge: str
    steps: tuple[str, ...]
    parallel: str
    check: str


SCAFFOLDS: tuple[Scaffold, ...] = (
    Scaffold(
        key="definite_integral",
        label="definite integral",
        keywords=("integral", "integrate", "∫", "\\int", "antiderivative", "area under"),
        nudge="Which theorem lets you evaluate a definite integral from an antiderivative, instead of adding up areas?",
        steps=(
            "Find an antiderivative $F(x)$ term by term (the power rule, run backwards).",
            "Evaluate $F$ at the upper limit.",
            "Evaluate $F$ at the lower limit.",
            "Subtract: $F(b) - F(a)$.",
        ),
        parallel=(
            "Parallel example: $\\int_0^1 (2x + 1)\\,dx$. An antiderivative is $F(x) = x^2 + x$, "
            "so the integral is $F(1) - F(0) = 2 - 0 = 2$."
        ),
        check="What antiderivative do you get for the first term of your integrand?",
    ),
    Scaffold(
        key="derivative",
        label="derivative",
        keywords=("derivative", "differentiate", "d/dx", "\\frac{d", "tangent line", "product rule", "chain rule", "quotient rule"),
        nudge="Is your function a product, a quotient, or a composition of simpler functions, and which rule matches that shape?",
        steps=(
            "Identify the structure: a product $u \\cdot v$, a quotient $u / v$, or a composition $f(g(x))$.",
            "Name the simpler pieces and differentiate each one on its own.",
            "Combine the pieces with the matching rule.",
            "Simplify and factor out common terms.",
        ),
        parallel=(
            "Parallel example: for $h(x) = x^2 \\sin x$, take $u = x^2$ and $v = \\sin x$. "
            "The product rule gives $h'(x) = 2x \\sin x + x^2 \\cos x$."
        ),
        check="What simpler functions are hiding inside yours?",
    ),
    Scaffold(
        key="eigen",
        label="eigenvalue",
        keywords=("eigenvalue", "eigenvector", "characteristic polynomial", "characteristic equation", "diagonaliz"),
        nudge="What equation must a scalar $\\lambda$ satisfy for $A - \\lambda I$ to send some nonzero vector to zero?",
        steps=(
            "Write $A - \\lambda I$ by subtracting $\\lambda$ from each diagonal entry.",
            "Take its determinant to get the characteristic polynomial.",
            "Set the polynomial equal to zero and solve for $\\lambda$.",
            "Check that the eigenvalues add up to the trace of $A$.",
        ),
        parallel=(
            "Parallel example: for $A = \\begin{pmatrix} 3 & 0 \\\\ 0 & 5 \\end{pmatrix}$, "
            "$\\det(A - \\lambda I) = (3 - \\lambda)(5 - \\lambda) = 0$, so $\\lambda = 3$ or $\\lambda = 5$, "
            "and $3 + 5$ matches the trace, $8$."
        ),
        check="What do you get when you write out $\\det(A - \\lambda I)$ for your matrix?",
    ),
    Scaffold(
        key="bayes",
        label="Bayes' theorem",
        keywords=("bayes", "posterior", "conditional probability", "p(a|b)", "given that", "false positive", "base rate"),
        nudge="Which quantity is the problem asking for, $P(A \\mid B)$ or $P(B \\mid A)$, and which one were you given?",
        steps=(
            "Label the prior $P(A)$, the likelihood $P(B \\mid A)$, and $P(B \\mid \\neg A)$.",
            "Compute the evidence $P(B)$ with the law of total probability.",
            "Divide: $P(A \\mid B) = P(B \\mid A)\\,P(A) / P(B)$.",
            "Sanity-check that the posterior moves in the direction the evidence suggests.",
        ),
        parallel=(
            "Parallel example: a coin is biased with prior $0.5$; it lands heads with probability $0.9$ if biased "
            "and $0.5$ if fair. After one head, $P(H) = 0.9(0.5) + 0.5(0.5) = 0.7$, so "
            "$P(\\text{biased} \\mid H) = 0.45 / 0.7 \\approx 0.64$."
        ),
        check="What is the total probability of the evidence, $P(B)$, in your problem?",
    ),
    Scaffold(
        key="recursion",
        label="recursion",
        keywords=("recursion", "recursive", "base case", "factorial", "fibonacci", "call stack", "calls itself"),
        nudge="What is the smallest version of this problem you could answer instantly, without another call?",
        steps=(
            "Name the base case and what it returns.",
            "Describe how each call shrinks the problem toward that base case.",
            "Trust the recursive call: assume it solves the smaller problem, then combine its result.",
            "Trace a tiny input by hand to check that the stack unwinds correctly.",
        ),
        parallel=(
            "Parallel example: summing a list. The base case is an empty list, which sums to `0`. "
            "The recursive case is `total(xs) = xs[0] + total(xs[1:])`, so `total([2, 3])` becomes "
            "`2 + total([3])`, then `2 + (3 + total([]))`, then `2 + 3 + 0`."
        ),
        check="What should your function return for the smallest possible input?",
    ),
    Scaffold(
        key="complexity",
        label="complexity",
        keywords=("big-o", "big o", "complexity", "runtime", "o(n", "asymptotic", "how fast", "efficient"),
        nudge="When the input size $n$ doubles, roughly how many more times does the innermost line of work run?",
        steps=(
            "Find the line that runs most often: the innermost loop body or the recursive call.",
            "Count how many times it runs as a function of $n$.",
            "Drop constants and lower-order terms.",
            "Match the result to a familiar class: $O(1)$, $O(\\log n)$, $O(n)$, $O(n \\log n)$, $O(n^2)$.",
        ),
        parallel=(
            "Parallel example: an outer loop over $i = 1 \\dots n$ with an inner loop over $j = 1 \\dots i$ runs "
            "$1 + 2 + \\dots + n = n(n+1)/2$ times, which is $O(n^2)$."
        ),
        check="Which line of your algorithm runs the most times?",
    ),
    Scaffold(
        key="graph_search",
        label="shortest-path",
        keywords=("dijkstra", "shortest path", "bfs", "dfs", "breadth-first", "depth-first", "graph", "vertex", "vertices"),
        nudge="Which vertex should the algorithm commit to next, and why is that choice safe?",
        steps=(
            "Initialize distances: $0$ for the source, $\\infty$ everywhere else.",
            "Pick the unvisited vertex with the smallest tentative distance.",
            "Relax each outgoing edge: is the path through this vertex shorter?",
            "Repeat until every reachable vertex is finalized.",
        ),
        parallel=(
            "Parallel example: edges $S \\to A$ (4), $S \\to B$ (1), $B \\to A$ (2). Start with $d(S) = 0$. "
            "Visit $B$ at distance $1$ and relax $B \\to A$: $1 + 2 = 3 < 4$, so $d(A)$ becomes $3$."
        ),
        check="After the source, which vertex does your graph visit first, and why?",
    ),
    Scaffold(
        key="gradient_descent",
        label="optimization",
        keywords=("gradient descent", "learning rate", "loss function", "optimizer", "converge", "backprop"),
        nudge="If the slope of the loss at your current point is positive, which way should the parameter move?",
        steps=(
            "Compute the gradient of the loss at the current parameter value.",
            "Step against it: $\\theta \\leftarrow \\theta - \\eta \\nabla L(\\theta)$.",
            "Check whether the loss went down.",
            "Adjust the learning rate $\\eta$ if steps overshoot or crawl.",
        ),
        parallel=(
            "Parallel example: minimize $L(\\theta) = \\theta^2$ from $\\theta = 4$ with $\\eta = 0.25$. "
            "The gradient is $2\\theta = 8$, so $\\theta \\leftarrow 4 - 0.25 \\cdot 8 = 2$, then $2 - 0.25 \\cdot 4 = 1$."
        ),
        check="What is the gradient at your starting point?",
    ),
    Scaffold(
        key="probability",
        label="probability",
        keywords=("probability", "dice", "die", "coin", "cards", "independent", "expected value", "variance", "random variable"),
        nudge="What does one outcome look like, and are all outcomes equally likely?",
        steps=(
            "Describe the sample space: every possible outcome.",
            "Mark the outcomes that make the event happen.",
            "Decide whether the events are independent, mutually exclusive, or neither.",
            "Combine with the matching rule: add for 'or' (minus overlap), multiply for independent 'and'.",
        ),
        parallel=(
            "Parallel example: the probability of two heads in two fair flips. The outcomes are HH, HT, TH, TT; "
            "one of the four works, so it is $1/4$, which matches $\\tfrac12 \\cdot \\tfrac12$ for independent flips."
        ),
        check="How many outcomes are in your sample space?",
    ),
    Scaffold(
        key="linear_system",
        label="system of equations",
        keywords=("system of equations", "simultaneous", "solve for x", "linear equation", "two equations"),
        nudge="Can you combine the equations so that one variable disappears?",
        steps=(
            "Choose a variable to eliminate.",
            "Scale one or both equations so that variable's coefficients match.",
            "Add or subtract the equations to eliminate it.",
            "Solve for the remaining variable, then substitute back.",
        ),
        parallel=(
            "Parallel example: $x + y = 5$ and $x - y = 1$. Adding them gives $2x = 6$, so $x = 3$, "
            "and substituting back gives $y = 2$."
        ),
        check="Which variable would be easiest to eliminate in your system?",
    ),
)

GENERAL_SCAFFOLD = Scaffold(
    key="general",
    label="problem",
    keywords=(),
    nudge="What is the problem really asking you to find, and what do you already know that connects to it?",
    steps=(
        "Restate the goal in your own words.",
        "List the facts and definitions you are given.",
        "Pick the principle that links what you know to what you need.",
        "Try the first step and check it before moving on.",
    ),
    parallel=(
        "Parallel example: to find how long a 120 km trip takes at 60 km/h, the linking principle is "
        "time = distance / speed, which gives 2 hours. The same find-the-linking-principle move applies to your question."
    ),
    check="What is the first concrete step you could take?",
)


def select_scaffold(text: str) -> Scaffold:
    lowered = text.lower()
    best, best_hits = GENERAL_SCAFFOLD, 0
    for scaffold in SCAFFOLDS:
        hits = sum(1 for keyword in scaffold.keywords if keyword in lowered)
        if hits > best_hits:
            best, best_hits = scaffold, hits
    return best


def hint_ladder(scaffold: Scaffold) -> list[Hint]:
    steps = " ".join(f"({i}) {step}" for i, step in enumerate(scaffold.steps, 1))
    return [
        Hint(tier=1, title=HINT_TITLES[1], text=scaffold.nudge),
        Hint(tier=2, title=HINT_TITLES[2], text=steps),
        Hint(tier=3, title=HINT_TITLES[3], text=scaffold.parallel),
    ]


class SocraticTutorAgent(SpecialistAgent):
    name = "socratic_tutor"
    enforces_socratic_rule = True
    emits_hints = True

    def role_prompt(self, ctx: AgentContext) -> str:
        return SOCRATIC_TUTOR.format(tier=ctx.decision.hint_tier)

    def output_format(self, ctx: AgentContext) -> str:
        return SOCRATIC_OUTPUT_FORMAT.format(marker=HINTS_MARKER)

    def offline(self, ctx: AgentContext) -> AgentDraft:
        request = ctx.request
        scaffold = select_scaffold(f"{request.topic or ''} {request.message}")
        tier = ctx.decision.hint_tier
        demanded = any(cue in request.message.lower() for cue in ANSWER_DEMAND_CUES)
        expression = first_math_expression(request.message)

        if demanded:
            opening = (
                "I won't hand you the final answer, because finding it yourself is what makes it stick. "
                "I will get you there fast."
            )
        elif scaffold is GENERAL_SCAFFOLD:
            opening = "Let's reason through this together."
        else:
            focus = f" with {expression}" if expression else ""
            opening = f"Good {scaffold.label} problem to work through{focus}."

        if ctx.is_voice:
            body = {1: scaffold.nudge, 2: f"Let's take it one move at a time. First: {scaffold.steps[0]}", 3: scaffold.parallel}[tier]
            text = f"{opening} {body} {scaffold.check}"
        else:
            if tier == 1:
                body = f"Start here: {scaffold.nudge}"
            elif tier == 2:
                moves = "\n".join(f"{i}. {step}" for i, step in enumerate(scaffold.steps, 1))
                body = f"Let's break it into moves:\n\n{moves}\n\nWork on move 1 before anything else."
            else:
                body = f"{scaffold.parallel}\n\nNow apply the same moves to your own problem."
            grounding = "\n\nThe principle behind this is in your course material [1]." if ctx.chunks else ""
            text = f"{opening}\n\n{body}{grounding}\n\n**{scaffold.check}**"
        return AgentDraft(text=text, hints=hint_ladder(scaffold))
