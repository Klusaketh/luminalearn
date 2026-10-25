"""
LuminaLearn AI — Socratic Faculty Orchestrator.
Module: ai/agents/orchestrator.py

An explicit state graph in the LangGraph style, without the framework dependency:

    ground (curriculum RAG)
      -> route (Supervisor: intent + BKT mastery + VARK)
      -> specialist (Gemini stream, or the specialist's offline engine)
      -> guardrail (streaming Socratic answer-leak screen)
      -> finalize (hint ladder, interactive lab, provenance, telemetry)

`stream()` yields TutorEvents that the HTTP layer renders as Server-Sent Events and the
voice layer forwards over its WebSocket.
"""

import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from ai.agents.analogy_specialist import AnalogySpecialistAgent
from ai.agents.base import AgentContext, SpecialistAgent
from ai.agents.code_diagnostic import CodeDiagnosticAgent, analyze_code
from ai.agents.concept_explainer import ConceptExplainerAgent, choose_widget
from ai.agents.guardrails import HintSplitter, SocraticGuardrail, parse_hints
from ai.agents.schema import (
    AGENT_PROFILES,
    AgentDraft,
    AgentName,
    CodeAnalysis,
    Hint,
    RoutingDecision,
    TutorEvent,
    TutorRequest,
)
from ai.agents.socratic_tutor import SocraticTutorAgent, hint_ladder, select_scaffold
from ai.agents.supervisor import SupervisorAgent
from ai.llm.gemini_gateway import (
    GeminiGateway,
    LLMStreamInterruptedError,
    LLMUnavailableError,
)
from ai.prompts.templates import PROMPT_VERSION
from ai.rag.curriculum_rag import CurriculumChunk, CurriculumRAGService

logger = logging.getLogger("luminalearn.ai.orchestrator")

GROUNDING_THRESHOLD = 0.25
_HISTORY_TURNS = 8
_TURN_CHARS = 1500
_INTERRUPTED_NOTE = "\n\n_The model connection dropped here, so the hint ladder below picks up where it stopped._"


def _chunk_for_stream(text: str, size: int = 28) -> list[str]:
    """Splits offline text into small word-aligned pieces so the client typewriter streams it."""
    pieces: list[str] = []
    current = ""
    for word in text.split(" "):
        candidate = f"{current} {word}" if current else word
        if len(candidate) > size and current:
            pieces.append(current + " ")
            current = word
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def build_contents(request: TutorRequest) -> list[dict[str, Any]]:
    """Gemini `contents` from the recent dialogue, merging consecutive turns by the same speaker."""
    contents: list[dict[str, Any]] = []
    turns = [(t.role, t.text) for t in request.history[-_HISTORY_TURNS:]] + [("student", request.message)]
    for role, text in turns:
        gemini_role = "user" if role == "student" else "model"
        part = {"text": text[:_TURN_CHARS]}
        if contents and contents[-1]["role"] == gemini_role:
            contents[-1]["parts"].append(part)
        else:
            contents.append({"role": gemini_role, "parts": [part]})
    if contents and contents[0]["role"] == "model":
        contents.insert(0, {"role": "user", "parts": [{"text": "(continuing our tutoring session)"}]})
    return contents


def citation_payload(chunks: list[CurriculumChunk]) -> list[dict[str, Any]]:
    return [
        {
            "index": index,
            "label": chunk.citation,
            "source": chunk.source_title,
            "section": chunk.section,
            "page": chunk.page,
            "relevance": chunk.score,
            "excerpt": chunk.content[:240] + ("…" if len(chunk.content) > 240 else ""),
        }
        for index, chunk in enumerate(chunks, 1)
    ]


def _route_event(decision: RoutingDecision, request: TutorRequest) -> TutorEvent:
    profile = AGENT_PROFILES[decision.agent]
    return TutorEvent("route", {
        "agent": decision.agent,
        "display_name": profile["display_name"],
        "summary": profile["summary"],
        "confidence": decision.confidence,
        "rationale": decision.rationale,
        "signals": list(decision.signals),
        "hint_tier": decision.hint_tier,
        "modality": request.modality,
    })


def _diagnostics_event(analysis: CodeAnalysis) -> TutorEvent:
    return TutorEvent("diagnostics", {
        "language": analysis.language,
        "time_complexity": analysis.time_complexity,
        "space_complexity": analysis.space_complexity,
        "rationale": analysis.complexity_rationale,
        "findings": [
            {"severity": f.severity, "line": f.line, "title": f.title, "detail": f.detail, "question": f.question}
            for f in analysis.findings
        ],
    })


@dataclass
class _Turn:
    """Mutable state shared by the graph nodes for one learner turn."""

    agent: SpecialistAgent
    ctx: AgentContext
    guard: SocraticGuardrail
    emitted: list[str] = field(default_factory=list)
    hints: list[Hint] = field(default_factory=list)
    engine: str = "offline"
    draft: AgentDraft | None = None

    def delta(self, text: str) -> TutorEvent | None:
        if not text:
            return None
        self.emitted.append(text)
        return TutorEvent("delta", {"text": text})


class SocraticOrchestrator:
    """Runs one learner turn through the faculty graph."""

    def __init__(self, gateway: GeminiGateway | None, rag: CurriculumRAGService, temperature: float = 0.6) -> None:
        self.gateway = gateway
        self.rag = rag
        self.temperature = temperature
        self.supervisor = SupervisorAgent()
        self.agents: dict[AgentName, SpecialistAgent] = {
            "socratic_tutor": SocraticTutorAgent(),
            "concept_explainer": ConceptExplainerAgent(),
            "analogy_specialist": AnalogySpecialistAgent(),
            "code_diagnostic": CodeDiagnosticAgent(),
        }

    @property
    def llm_enabled(self) -> bool:
        return self.gateway is not None and self.gateway.enabled

    async def stream(self, request: TutorRequest) -> AsyncIterator[TutorEvent]:
        started = time.perf_counter()

        # ground
        query = f"{request.topic or ''} {request.message}".strip()
        chunks = self.rag.retrieve(query=query, top_k=3, threshold=GROUNDING_THRESHOLD)
        grounded = self.rag.has_sufficient_grounding(chunks)

        # route
        decision = self.supervisor.route(request)
        agent = self.agents[decision.agent]
        yield _route_event(decision, request)
        yield TutorEvent("citations", {"items": citation_payload(chunks), "grounded": grounded})
        ctx = AgentContext(request=request, decision=decision, chunks=chunks)
        if decision.agent == "code_diagnostic":
            ctx.analysis = analyze_code(request.message)
            yield _diagnostics_event(ctx.analysis)

        # specialist + guardrail
        turn = _Turn(agent=agent, ctx=ctx, guard=SocraticGuardrail(active=agent.enforces_socratic_rule))
        if self.llm_enabled:
            async for event in self._live(turn):
                yield event
        if not turn.emitted:
            async for event in self._offline(turn):
                yield event

        # finalize
        for event in self._finalize(turn):
            yield event
        yield TutorEvent("done", {
            "text": "".join(turn.emitted),
            "agent": decision.agent,
            "engine": turn.engine,
            "grounded": grounded,
            "hint_tier": decision.hint_tier,
            "guardrail_redactions": turn.guard.redactions,
            "prompt_version": PROMPT_VERSION,
            "latency_ms": round((time.perf_counter() - started) * 1000),
        })

    async def _live(self, turn: _Turn) -> AsyncIterator[TutorEvent]:
        """Gemini node: streams through the hint splitter and the Socratic guardrail."""
        if self.gateway is None:
            return
        ctx = turn.ctx
        splitter = HintSplitter()
        committed_model: list[str] = []
        try:
            async for raw in self.gateway.stream_text(
                build_contents(ctx.request),
                system_instruction=turn.agent.system_prompt(ctx),
                temperature=self.temperature,
                max_output_tokens=700 if ctx.is_voice else 2048,
                thinking=turn.agent.thinking(ctx),
                first_token_timeout_s=9.0 if ctx.is_voice else 14.0,
                total_timeout_s=40.0 if ctx.is_voice else 75.0,
                on_model=committed_model.append,
            ):
                event = turn.delta(turn.guard.feed(splitter.feed(raw)))
                if event:
                    yield event
            event = turn.delta(turn.guard.feed(splitter.flush()) + turn.guard.flush())
            if event:
                yield event
            turn.engine = f"gemini:{committed_model[0]}" if committed_model else "gemini"
            if turn.agent.emits_hints and not ctx.is_voice:
                turn.hints = parse_hints(splitter.hint_text)
        except LLMUnavailableError as exc:
            logger.info("Gemini unavailable for this turn (%s); using the %s offline engine.", exc, turn.agent.name)
        except LLMStreamInterruptedError as exc:
            logger.warning("Gemini stream interrupted mid-answer (%s).", exc)
            tail = turn.guard.flush()
            if turn.emitted:
                event = turn.delta(tail + _INTERRUPTED_NOTE)
                if event:
                    yield event
                turn.engine = "gemini (interrupted)"

    async def _offline(self, turn: _Turn) -> AsyncIterator[TutorEvent]:
        """Deterministic node: the specialist's own engine, screened by a fresh guardrail."""
        # A partially buffered model fragment must not leak into the offline answer.
        redacted_online = turn.guard.redactions
        turn.guard = SocraticGuardrail(active=turn.agent.enforces_socratic_rule)
        turn.guard.redactions = redacted_online
        turn.draft = turn.agent.offline(turn.ctx)
        for piece in _chunk_for_stream(turn.draft.text):
            event = turn.delta(turn.guard.feed(piece))
            if event:
                yield event
        event = turn.delta(turn.guard.flush())
        if event:
            yield event
        turn.hints = turn.draft.hints

    def _finalize(self, turn: _Turn) -> list[TutorEvent]:
        """Hint ladder and interactive lab frames (chat channel only)."""
        ctx = turn.ctx
        request = ctx.request
        if ctx.is_voice:
            return []
        events: list[TutorEvent] = []
        if turn.agent.emits_hints:
            hints = turn.hints if len(turn.hints) >= 3 else hint_ladder(select_scaffold(f"{request.topic or ''} {request.message}"))
            events.append(TutorEvent("hints", {
                "start_tier": ctx.decision.hint_tier,
                "items": [{"tier": h.tier, "title": h.title, "text": h.text} for h in hints],
            }))
        widget = turn.draft.interactive if turn.draft else None
        if widget is None and ctx.decision.agent == "concept_explainer" and request.modality == "kinesthetic":
            widget = choose_widget(f"{request.topic or ''} {request.message}")
        if widget is not None:
            events.append(TutorEvent("interactive", {"widget": widget}))
        return events
