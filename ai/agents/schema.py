"""
LuminaLearn AI — Multi-Agent Socratic Faculty: shared contracts.
Module: ai/agents/schema.py
"""

from dataclasses import dataclass, field
from typing import Any, Literal

AgentName = Literal["socratic_tutor", "concept_explainer", "analogy_specialist", "code_diagnostic"]
Modality = Literal["visual", "auditory", "read_write", "kinesthetic"]
Channel = Literal["chat", "voice"]
EventType = Literal["route", "citations", "diagnostics", "delta", "hints", "interactive", "done"]
InteractiveWidget = Literal["recursion", "gradient_descent", "bayes"]

AGENT_NAMES: tuple[AgentName, ...] = ("socratic_tutor", "concept_explainer", "analogy_specialist", "code_diagnostic")
MODALITIES: tuple[Modality, ...] = ("visual", "auditory", "read_write", "kinesthetic")

AGENT_PROFILES: dict[AgentName, dict[str, str]] = {
    "socratic_tutor": {
        "display_name": "Socratic Tutor",
        "summary": "Guides you to the answer with scaffolded questions and a three-tier hint ladder. Never hands the answer over.",
    },
    "concept_explainer": {
        "display_name": "Concept Explainer",
        "summary": "Explains ideas in your learning modality: diagrams, narration, structured notes or hands-on experiments.",
    },
    "analogy_specialist": {
        "display_name": "Analogy Specialist",
        "summary": "Maps abstract ideas onto everyday experiences, and says where each analogy stops working.",
    },
    "code_diagnostic": {
        "display_name": "Code Diagnostic",
        "summary": "Pinpoints syntax bugs, logic bugs and complexity bottlenecks, then asks the question that leads you to the fix.",
    },
}


@dataclass(frozen=True)
class DialogueTurn:
    role: Literal["student", "tutor"]
    text: str


@dataclass
class TutorRequest:
    """Everything the faculty knows about one learner turn."""

    message: str
    topic: str | None = None
    modality: Modality = "read_write"
    mastery: float | None = None  # BKT P(L) for the topic, None when never assessed
    hint_level: int = 0  # extra hints requested in this thread (0-3)
    history: list[DialogueTurn] = field(default_factory=list)
    channel: Channel = "chat"
    requested_agent: AgentName | None = None
    learner_name: str | None = None


@dataclass(frozen=True)
class RoutingDecision:
    agent: AgentName
    confidence: float
    rationale: str
    signals: tuple[str, ...]
    hint_tier: int  # 1 = nudge, 2 = scaffold, 3 = parallel worked example


@dataclass(frozen=True)
class Hint:
    tier: int
    title: str
    text: str


Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class CodeFinding:
    severity: Severity
    line: int | None
    title: str
    detail: str
    question: str


@dataclass(frozen=True)
class CodeAnalysis:
    language: str
    code: str
    findings: tuple[CodeFinding, ...]
    time_complexity: str
    space_complexity: str
    complexity_rationale: str


@dataclass
class AgentDraft:
    """A complete answer from an agent's deterministic (offline) engine."""

    text: str
    hints: list[Hint] = field(default_factory=list)
    interactive: InteractiveWidget | None = None


@dataclass(frozen=True)
class TutorEvent:
    """One frame of the orchestrator's stream (rendered as SSE or WebSocket JSON)."""

    type: EventType
    data: dict[str, Any]


HINT_TITLES = {1: "Nudge", 2: "Scaffold", 3: "Parallel example"}


def retention_label(mastery: float) -> str:
    """Mirrors the quiz engine's competency tiers."""
    if mastery >= 0.85:
        return "Mastered"
    if mastery >= 0.60:
        return "Competent"
    if mastery >= 0.30:
        return "Developing"
    return "Novice"
