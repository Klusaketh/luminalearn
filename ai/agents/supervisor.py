"""
LuminaLearn AI — Supervisor Agent.
Module: ai/agents/supervisor.py

Routes each learner turn to the right specialist. Routing is deterministic and explainable
(no LLM round-trip, which keeps voice latency low): it scores intent signals in the message,
then adjusts with the learner's Bayesian mastery and VARK profile. The rationale string is
shown to the learner as the "why this tutor" explanation.
"""

import re

from ai.agents.schema import (
    AGENT_PROFILES,
    AgentName,
    RoutingDecision,
    TutorRequest,
    retention_label,
)

_CODE_FENCE = re.compile(r"```")
_CODE_LINE = re.compile(
    r"^\s*(def |class |for .+:|while .+:|if .+:\s*$|elif |return\b|import |from \w+ import|#include|"
    r"public |private |function\b|const |let |var |console\.|print\(|System\.out|fn |func |int main)",
    re.MULTILINE,
)
_CODE_SYMBOLS = re.compile(r"[{};]\s*$|=>|\+\+|\w+\[\w*\]\s*=", re.MULTILINE)
_MATH = re.compile(
    r"\d\s*[+\-*/^=]\s*\d|[∫∑√π]|\\(int|frac|sum|sqrt|lim|det|begin)|\$[^$]+\$|\b[xyzn]\s*[\^=]|\bd[xy]\b|\bf\(x\)",
    re.IGNORECASE,
)

ANALOGY_CUES = (
    "analogy", "metaphor", "like i'm five", "like im five", "eli5", "real world", "real-world", "real life",
    "everyday", "intuition", "intuitive", "in simple terms", "simple words", "layman", "compare it to",
    "what is it like", "make it relatable",
)
CODE_CUES = (
    "my code", "this code", "bug", "debug", "traceback", "exception", "stack trace", "compile", "syntax error",
    "runtime error", "segfault", "infinite loop", "refactor", "my function", "my program", "my script",
)
EXPLAIN_CUES = (
    "explain", "what is", "what are", "what's", "define", "definition", "describe", "overview", "teach me",
    "help me understand", "how does", "why does", "why do", "difference between", "meaning of", "concept of",
    "introduce", "visualize", "show me",
)
PROBLEM_CUES = (
    "solve", "find", "calculate", "compute", "evaluate", "prove", "derive", "simplify", "determine",
    "integrate", "differentiate", "how many", "value of", "homework", "exercise", "stuck", "hint",
    "check my", "is it correct", "is this right", "my answer", "i got",
)
ANSWER_DEMAND_CUES = (
    "just tell me", "give me the answer", "tell me the answer", "what's the answer", "what is the answer",
    "just give", "final answer", "the solution", "solve it for me", "do it for me", "skip the questions",
)


def _has_any(text: str, cues: tuple[str, ...]) -> bool:
    return any(cue in text for cue in cues)


def looks_like_code(message: str) -> bool:
    """True for fenced code or two or more lines that read as source code."""
    if _CODE_FENCE.search(message):
        return True
    code_lines = len(_CODE_LINE.findall(message))
    return code_lines >= 2 or (code_lines >= 1 and bool(_CODE_SYMBOLS.search(message)))


def hint_tier_for(request: TutorRequest, answer_demand: bool = False) -> int:
    """
    Hint ladder policy: novices (P(L) < 0.30) start with scaffolding, everyone else with a nudge.
    Each extra hint the learner asks for, or a demand for the answer, climbs one rung.
    """
    base = 2 if request.mastery is not None and request.mastery < 0.30 else 1
    return max(1, min(3, base + request.hint_level + (1 if answer_demand else 0)))


class SupervisorAgent:
    """Scores intent signals and dispatches to one specialist with an explainable rationale."""

    def route(self, request: TutorRequest) -> RoutingDecision:
        text = request.message.lower()
        answer_demand = _has_any(text, ANSWER_DEMAND_CUES)
        tier = hint_tier_for(request, answer_demand)

        if request.requested_agent is not None:
            name = AGENT_PROFILES[request.requested_agent]["display_name"]
            return RoutingDecision(
                agent=request.requested_agent,
                confidence=1.0,
                rationale=f"You asked for the {name} directly.",
                signals=("explicit_request",),
                hint_tier=tier,
            )

        scores: dict[AgentName, float] = {
            "socratic_tutor": 0.6,  # the faculty's default teaching stance
            "concept_explainer": 0.0,
            "analogy_specialist": 0.0,
            "code_diagnostic": 0.0,
        }
        signals: list[str] = []

        has_code = looks_like_code(request.message)
        if has_code:
            scores["code_diagnostic"] += 3.0
            signals.append("code_detected")
        if _has_any(text, CODE_CUES):
            scores["code_diagnostic"] += 1.2 if has_code else 0.7
            signals.append("debugging_language")
        if _has_any(text, ANALOGY_CUES):
            scores["analogy_specialist"] += 2.6
            signals.append("analogy_requested")
        if _has_any(text, EXPLAIN_CUES):
            scores["concept_explainer"] += 1.5
            signals.append("explanation_requested")
        if _has_any(text, PROBLEM_CUES):
            scores["socratic_tutor"] += 1.4
            signals.append("problem_solving")
        if _MATH.search(request.message):
            scores["socratic_tutor"] += 1.0
            signals.append("math_expression")
        if answer_demand:
            scores["socratic_tutor"] += 3.0
            signals.append("answer_request")
        if request.mastery is not None and request.mastery < 0.30 and "explanation_requested" in signals:
            scores["concept_explainer"] += 0.5
            signals.append("novice_needs_foundations")

        agent = max(scores, key=lambda name: scores[name])
        total = sum(scores.values())
        confidence = round(max(0.34, min(0.98, scores[agent] / total if total else 0.5)), 2)
        return RoutingDecision(
            agent=agent,
            confidence=confidence,
            rationale=self._rationale(agent, signals, request, tier),
            signals=tuple(signals) or ("default_socratic_stance",),
            hint_tier=tier,
        )

    @staticmethod
    def _rationale(agent: AgentName, signals: list[str], request: TutorRequest, tier: int) -> str:
        topic = request.topic or "this topic"
        mastery_note = ""
        if request.mastery is not None:
            mastery_note = (
                f" Your mastery of {topic} is {round(request.mastery * 100)}% ({retention_label(request.mastery)})."
            )
        if agent == "code_diagnostic":
            reason = "I found code in your message" if "code_detected" in signals else "You described a debugging problem"
            return f"{reason}, so the Code Diagnostic agent will look for bugs and complexity hot-spots."
        if agent == "analogy_specialist":
            return "You asked for an intuitive comparison, so the Analogy Specialist will map this onto everyday experience."
        if agent == "concept_explainer":
            style = request.modality.replace("_", "/")
            return f"You asked to understand a concept, so the Concept Explainer will teach it in your {style} learning style.{mastery_note}"
        if "answer_request" in signals:
            why = "You asked for the answer. The Socratic Tutor won't hand it over, but it will climb the hint ladder faster"
        elif {"problem_solving", "math_expression"} & set(signals):
            why = "This is a problem to work through, so the Socratic Tutor will guide you to the answer instead of giving it"
        else:
            why = "The Socratic Tutor will help you reason it out with guiding questions"
        return f"{why} (hint tier {tier} of 3).{mastery_note}"
