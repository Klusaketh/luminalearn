"""
LuminaLearn AI — Specialist Agent Base.
Module: ai/agents/base.py

Each specialist provides two engines behind one interface:
  * `system_prompt()` instructs Gemini when the gateway is online.
  * `offline()` produces a complete deterministic answer when it is not, so the
    faculty keeps teaching through outages, missing keys, or rate limits.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ai.agents.schema import (
    AgentDraft,
    AgentName,
    CodeAnalysis,
    RoutingDecision,
    TutorRequest,
    retention_label,
)
from ai.llm.gemini_gateway import ThinkingEffort
from ai.prompts.templates import FACULTY_CHARTER, VOICE_RULES
from ai.rag.curriculum_rag import CurriculumChunk


@dataclass
class AgentContext:
    request: TutorRequest
    decision: RoutingDecision
    chunks: list[CurriculumChunk]
    analysis: CodeAnalysis | None = None

    @property
    def topic(self) -> str:
        if self.request.topic:
            return self.request.topic
        if self.chunks:
            return self.chunks[0].topic
        return "this idea"

    @property
    def is_voice(self) -> bool:
        return self.request.channel == "voice"


def format_sources(chunks: list[CurriculumChunk]) -> str:
    if not chunks:
        return "Verified curriculum context: none matched this question."
    lines = ["Verified curriculum context (cite by number):"]
    for index, chunk in enumerate(chunks, 1):
        lines.append(f"[{index}] {chunk.citation}: {chunk.content}")
    return "\n".join(lines)


def format_profile(request: TutorRequest) -> str:
    if request.mastery is None:
        mastery = "unknown (not assessed yet)"
    else:
        mastery = f"{round(request.mastery * 100)}% ({retention_label(request.mastery)})"
    return "\n".join(
        [
            "Learner profile:",
            f"- Name: {request.learner_name or 'not shared'}",
            f"- Topic: {request.topic or 'not specified'}",
            f"- Bayesian mastery P(L): {mastery}",
            f"- Preferred VARK modality: {request.modality.replace('_', '/')}",
        ]
    )


def first_math_expression(message: str) -> str | None:
    """Returns the learner's first $...$ expression so offline replies can point at it."""
    match = re.search(r"\$\$?([^$]+?)\$\$?", message)
    return match.group(0) if match else None


class SpecialistAgent(ABC):
    name: AgentName
    enforces_socratic_rule = False
    emits_hints = False

    @abstractmethod
    def role_prompt(self, ctx: AgentContext) -> str:
        """Role-specific instructions for Gemini."""

    @abstractmethod
    def offline(self, ctx: AgentContext) -> AgentDraft:
        """Deterministic answer used when the gateway is unavailable."""

    def extra_context(self, ctx: AgentContext) -> str:
        return ""

    def output_format(self, ctx: AgentContext) -> str:
        """Trailing output-format rules for the chat channel (voice replies are plain speech)."""
        return ""

    def thinking(self, ctx: AgentContext) -> ThinkingEffort:
        return "minimal" if ctx.is_voice else "low"

    def system_prompt(self, ctx: AgentContext) -> str:
        sections = [FACULTY_CHARTER, self.role_prompt(ctx), format_profile(ctx.request), format_sources(ctx.chunks)]
        extra = self.extra_context(ctx)
        if extra:
            sections.append(extra)
        if ctx.is_voice:
            sections.append(VOICE_RULES)
        elif fmt := self.output_format(ctx):
            sections.append(fmt)
        return "\n\n".join(sections)
