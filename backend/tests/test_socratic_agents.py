"""Multi-agent Socratic faculty: routing, guardrails, specialists and the orchestrator graph."""
import os
import sys
from collections.abc import AsyncIterator
from typing import Any

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ai.agents import SocraticOrchestrator, SupervisorAgent, TutorRequest, analyze_code
from ai.agents.analogy_specialist import select_analogy
from ai.agents.concept_explainer import mermaid_flowchart
from ai.agents.guardrails import (
    HintSplitter,
    SocraticGuardrail,
    parse_hints,
    reveals_final_answer,
)
from ai.agents.schema import TutorEvent
from ai.llm import LLMStreamInterruptedError, LLMUnavailableError
from ai.rag.curriculum_rag import curriculum_rag


class FakeGateway:
    """Stands in for GeminiGateway: replays scripted deltas, or fails on demand."""

    def __init__(self, deltas: list[str] | None = None, fail: Exception | None = None, fail_after: int | None = None) -> None:
        self.deltas = deltas or []
        self.fail = fail
        self.fail_after = fail_after
        self.enabled = True
        self.system_prompts: list[str] = []

    async def stream_text(self, contents: Any, **kwargs: Any) -> AsyncIterator[str]:
        self.system_prompts.append(kwargs.get("system_instruction") or "")
        if self.fail is not None and self.fail_after is None:
            raise self.fail
        on_model = kwargs.get("on_model")
        if on_model:
            on_model("fake-model")
        for index, delta in enumerate(self.deltas):
            if self.fail_after is not None and index == self.fail_after:
                raise LLMStreamInterruptedError("connection reset")
            yield delta


async def collect(orchestrator: SocraticOrchestrator, request: TutorRequest) -> list[TutorEvent]:
    return [event async for event in orchestrator.stream(request)]


def text_of(events: list[TutorEvent]) -> str:
    return "".join(e.data["text"] for e in events if e.type == "delta")


# --------------------------------------------------------------------------- supervisor

@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Evaluate $\\int_0^2 3x^2\\,dx$", "socratic_tutor"),
        ("Can you explain what recursion is?", "concept_explainer"),
        ("Give me a real-world analogy for mutex locks", "analogy_specialist"),
        ("Why does this crash?\n```python\ndef f(n):\n    return f(n)\n```", "code_diagnostic"),
        ("just tell me the answer to 2x + 3 = 7", "socratic_tutor"),
    ],
)
def test_supervisor_routes_by_intent(message: str, expected: str) -> None:
    decision = SupervisorAgent().route(TutorRequest(message=message))
    assert decision.agent == expected
    assert 0.34 <= decision.confidence <= 1.0
    assert decision.rationale


def test_supervisor_honours_explicit_agent_request() -> None:
    decision = SupervisorAgent().route(TutorRequest(message="solve x + 1 = 2", requested_agent="analogy_specialist"))
    assert decision.agent == "analogy_specialist"
    assert decision.confidence == 1.0
    assert decision.signals == ("explicit_request",)


def test_hint_tier_policy_uses_mastery_and_answer_demands() -> None:
    supervisor = SupervisorAgent()
    assert supervisor.route(TutorRequest(message="find the derivative of x^2", mastery=0.9)).hint_tier == 1
    assert supervisor.route(TutorRequest(message="find the derivative of x^2", mastery=0.1)).hint_tier == 2
    assert supervisor.route(TutorRequest(message="find the derivative of x^2", mastery=0.5, hint_level=1)).hint_tier == 2
    assert supervisor.route(TutorRequest(message="just give me the answer: d/dx x^2", mastery=0.1)).hint_tier == 3
    assert supervisor.route(TutorRequest(message="find it", hint_level=3)).hint_tier == 3


def test_supervisor_rationale_mentions_mastery_when_known() -> None:
    decision = SupervisorAgent().route(TutorRequest(message="compute the integral of 2x", topic="Calculus", mastery=0.22))
    assert "22%" in decision.rationale
    assert "Novice" in decision.rationale


# --------------------------------------------------------------------------- guardrails

def test_answer_leak_detection() -> None:
    assert reveals_final_answer("So the final answer is $6$.")
    assert reveals_final_answer("The answer is 42.")
    assert reveals_final_answer("Therefore, the result is x = 3.")
    assert not reveals_final_answer("The answer is not 5, so check your signs.")
    assert not reveals_final_answer("What do you get when you evaluate F(2)?")


def test_guardrail_redacts_leaks_but_keeps_parallel_examples_and_code() -> None:
    guard = SocraticGuardrail(active=True)
    streamed = [
        "Nice start. ", "The answer is ", "$6$. ", "What is F(2)?\n\n",
        "Parallel example: for $\\int_0^1 2x\\,dx$ the result is 1. ",
        "```python\nanswer = 6\n```\n",
    ]
    out = "".join(guard.feed(chunk) for chunk in streamed) + guard.flush()
    assert "The answer is $6$" not in out
    assert "hold back the final result" in out
    assert "the result is 1" in out  # labelled parallel example survives
    assert "answer = 6" in out  # code blocks are never rewritten
    assert guard.redactions == 1


def test_guardrail_inactive_passes_text_through_unchanged() -> None:
    guard = SocraticGuardrail(active=False)
    assert guard.feed("The answer is 6.") == "The answer is 6."


def test_hint_splitter_hides_marker_split_across_chunks() -> None:
    splitter = HintSplitter()
    visible = "".join(splitter.feed(c) for c in ["What is F(x)?", "\n\n**[[HI", "NTS]]**\n1) Name the theorem\n", "2) Find F\n3) Parallel: x"])
    visible += splitter.flush()
    assert visible == "What is F(x)?"
    hints = parse_hints(splitter.hint_text)
    assert [h.tier for h in hints] == [1, 2, 3]
    assert hints[0].text == "Name the theorem"
    assert hints[2].title == "Parallel example"


def test_parse_hints_accepts_unnumbered_lines_from_live_models() -> None:
    # Verbatim shape returned by Gemini 3.5 Flash: no 1)/2)/3) labels, step list inlined on line 2.
    section = (
        "\nBased on the characteristic equation, what polynomial do you get?\n"
        "1. Write out the matrix $A - \\lambda I$. 2. Take its determinant. 3. Solve for $\\lambda$.\n"
        "Parallel example: For $B$, the eigenvalues are $3$ and $5$.\n"
    )
    hints = parse_hints(section)
    assert [h.tier for h in hints] == [1, 2, 3]
    assert hints[0].text.startswith("Based on the characteristic equation")
    assert hints[1].text.startswith("1. Write out the matrix")
    assert hints[2].text.startswith("Parallel example")
    assert parse_hints("only one line") == []


def test_hint_splitter_without_marker_emits_everything() -> None:
    splitter = HintSplitter()
    out = splitter.feed("A plain reply [not a marker] ") + splitter.feed("ends here.") + splitter.flush()
    assert out == "A plain reply [not a marker] ends here."
    assert splitter.hint_text == ""


# --------------------------------------------------------------------------- specialists

def test_code_diagnostic_finds_missing_base_case_and_exponential_recursion() -> None:
    analysis = analyze_code("```python\ndef fib(n):\n    return fib(n - 1) + fib(n - 2)\n```")
    titles = {f.title for f in analysis.findings}
    assert analysis.language == "python"
    assert "Recursion without a reachable base case" in titles
    assert "Repeated subproblems" in titles
    assert analysis.time_complexity == "O(2^n)"


def test_code_diagnostic_accepts_correct_recursion_and_tree_walks() -> None:
    factorial = analyze_code("def fact(n):\n    if n == 0:\n        return 1\n    return n * fact(n - 1)\n")
    assert not any("base case" in f.title for f in factorial.findings)
    assert factorial.time_complexity == "O(n)"
    conditional = analyze_code("def fact(n):\n    return 1 if n == 0 else n * fact(n - 1)\n")
    assert not any("base case" in f.title for f in conditional.findings)
    walk = analyze_code("def walk(node):\n    for child in node.children:\n        walk(child)\n")
    assert not any(f.severity == "error" for f in walk.findings)


def test_code_diagnostic_reports_syntax_error_line() -> None:
    analysis = analyze_code("```python\ndef broken(x)\n    return x\n```")
    assert analysis.findings[0].title == "Syntax error"
    assert analysis.findings[0].line == 1


def test_code_diagnostic_classic_python_bugs_and_complexity() -> None:
    code = (
        "def collect(items, seen=[]):\n"
        "    for a in items:\n"
        "        for b in items:\n"
        "            if a == None:\n"
        "                items.remove(a)\n"
        "    while True:\n"
        "        pass\n"
    )
    analysis = analyze_code(code)
    titles = {f.title for f in analysis.findings}
    assert {"Mutable default argument", "Comparing to None with ==", "Mutating a list while iterating over it", "Infinite loop"} <= titles
    assert analysis.time_complexity == "O(n^2)"


def test_code_diagnostic_c_family_heuristics() -> None:
    analysis = analyze_code("```js\nfunction f(arr) {\n  for (let i = 0; i <= arr.length; i++) {\n    if (x = 5) { console.log(i) }\n  }\n```")
    titles = {f.title for f in analysis.findings}
    assert {"Unbalanced brackets", "Possible off-by-one", "Assignment inside a condition"} <= titles
    assert analysis.language == "javascript"


def test_python_with_dict_literal_is_still_detected_as_python() -> None:
    analysis = analyze_code("memo = {}\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n")
    assert analysis.language == "python"


def test_analogy_library_and_mermaid_generation() -> None:
    analogy = select_analogy("give me an analogy for dijkstra")
    assert analogy is not None and "pipes" in analogy.picture
    diagram = mermaid_flowchart((("A", "Start (here)"), ("B", "End")), (("A", "B", "next"),))
    assert diagram.splitlines()[0] == "flowchart TD"
    assert "(" not in diagram.split("\n", 1)[1]  # labels are sanitized for the renderer


# --------------------------------------------------------------------------- orchestrator

@pytest.mark.asyncio
async def test_offline_orchestrator_event_contract() -> None:
    orchestrator = SocraticOrchestrator(gateway=None, rag=curriculum_rag)
    events = await collect(orchestrator, TutorRequest(message="Evaluate $\\int_0^2 (3x^2 - 2x + 1)\\,dx$", topic="Calculus"))
    types = [e.type for e in events]
    assert types[0] == "route" and types[1] == "citations" and types[-1] == "done"
    assert "delta" in types and "hints" in types
    done = events[-1].data
    assert done["engine"] == "offline"
    assert done["agent"] == "socratic_tutor"
    assert done["text"] == text_of(events)
    assert events[1].data["grounded"] is True
    hints = next(e for e in events if e.type == "hints").data["items"]
    assert [h["tier"] for h in hints] == [1, 2, 3]
    # Golden rule: the learner's actual result (6) is never stated.
    assert not reveals_final_answer(done["text"])
    assert "= 6" not in done["text"] and "$6$" not in done["text"]


@pytest.mark.asyncio
async def test_offline_kinesthetic_explainer_emits_interactive_lab() -> None:
    orchestrator = SocraticOrchestrator(gateway=None, rag=curriculum_rag)
    events = await collect(orchestrator, TutorRequest(message="explain gradient descent", modality="kinesthetic"))
    interactive = [e for e in events if e.type == "interactive"]
    assert interactive and interactive[0].data["widget"] == "gradient_descent"


@pytest.mark.asyncio
async def test_code_turn_emits_structured_diagnostics() -> None:
    orchestrator = SocraticOrchestrator(gateway=None, rag=curriculum_rag)
    events = await collect(orchestrator, TutorRequest(message="```python\ndef f(n):\n    return f(n)\n```"))
    diagnostics = next(e for e in events if e.type == "diagnostics").data
    assert diagnostics["language"] == "python"
    assert any(f["title"] == "Recursive call does not shrink the input" for f in diagnostics["findings"])


@pytest.mark.asyncio
async def test_live_stream_is_guarded_and_hints_are_parsed() -> None:
    gateway = FakeGateway(deltas=[
        "Good instinct. ", "The answer is $6$. ", "What antiderivative do you get?",
        "\n[[HINTS]]\n1) Which theorem applies?\n2) Integrate term by term.\n3) Parallel example: ...",
    ])
    orchestrator = SocraticOrchestrator(gateway=gateway, rag=curriculum_rag)  # type: ignore[arg-type]
    events = await collect(orchestrator, TutorRequest(message="Evaluate $\\int_0^2 3x^2\\,dx$", topic="Calculus"))
    text = text_of(events)
    done = events[-1].data
    assert "The answer is $6$" not in text
    assert "[[HINTS]]" not in text
    assert done["engine"] == "gemini:fake-model"
    assert done["guardrail_redactions"] == 1
    hints = next(e for e in events if e.type == "hints").data["items"]
    assert hints[0]["text"] == "Which theorem applies?"
    # The system prompt carries the golden rule, the learner profile and numbered sources.
    prompt = gateway.system_prompts[0]
    assert "Never state the final answer" in prompt and "Learner profile" in prompt and "[1]" in prompt


@pytest.mark.asyncio
async def test_falls_back_to_offline_engine_when_gateway_unavailable() -> None:
    orchestrator = SocraticOrchestrator(gateway=FakeGateway(fail=LLMUnavailableError("down")), rag=curriculum_rag)  # type: ignore[arg-type]
    events = await collect(orchestrator, TutorRequest(message="what is a hash table?"))
    assert events[-1].data["engine"] == "offline"
    assert text_of(events)


@pytest.mark.asyncio
async def test_mid_stream_interruption_keeps_partial_text_and_hint_ladder() -> None:
    gateway = FakeGateway(deltas=["Let's think. ", "What is the base case? ", "never sent"], fail_after=2)
    orchestrator = SocraticOrchestrator(gateway=gateway, rag=curriculum_rag)  # type: ignore[arg-type]
    events = await collect(orchestrator, TutorRequest(message="help me solve this recursion problem"))
    done = events[-1].data
    assert done["engine"] == "gemini (interrupted)"
    assert "What is the base case?" in done["text"]
    assert "never sent" not in done["text"]
    assert any(e.type == "hints" for e in events)


@pytest.mark.asyncio
async def test_voice_channel_has_no_hints_or_markdown_sections() -> None:
    orchestrator = SocraticOrchestrator(gateway=None, rag=curriculum_rag)
    events = await collect(orchestrator, TutorRequest(message="solve 2x + 3 = 7", channel="voice"))
    assert not any(e.type == "hints" for e in events)
    assert "\n" not in events[-1].data["text"]
