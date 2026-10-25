"""
LuminaLearn AI — Socratic Guardrails & Stream Utilities.
Module: ai/agents/guardrails.py

The system prompt is the first line of defense against handing learners the answer.
This module is the second: it screens model output sentence by sentence while it streams,
replacing any sentence that announces a final answer with a Socratic redirect.
Code blocks and explicitly labelled parallel examples are left untouched.
"""

import re

from ai.agents.schema import HINT_TITLES, Hint
from ai.prompts.templates import HINTS_MARKER, SOCRATIC_REDIRECT

# A leak needs an actual value after the verb: "the answer is not 5, check the sign" is a hint.
_VALUE = r"\s*(?:\$|\\\(|\\frac|\\lambda|λ|-?\d|[a-zA-Z]\s*=\s*-?\d)"
_LEAK_PATTERNS = (
    re.compile(
        rf"\b(the|your|final|correct|right)\s+(final\s+)?(answer|solution|result)\s+(is|=|would be|will be|equals){_VALUE}",
        re.IGNORECASE,
    ),
    re.compile(r"^\W*(final\s+)?answer\s*[:=]\s*\S", re.IGNORECASE),
    re.compile(
        rf"\b(so|therefore|thus|hence)\b[^.?!\n]{{0,80}}\b(answer|result|solution)\b[^.?!\n]{{0,40}}\b(is|=|equals){_VALUE}",
        re.IGNORECASE,
    ),
    re.compile(r"\bthe answer you(?:'re| are) looking for\b", re.IGNORECASE),
)
_EXAMPLE_LABEL = re.compile(r"\b(parallel|similar|worked|analogous|different)\s+example\b", re.IGNORECASE)
_BOUNDARY = re.compile(r"(?<=[.!?])[ \t]+|\n")


def reveals_final_answer(sentence: str) -> bool:
    return any(pattern.search(sentence) for pattern in _LEAK_PATTERNS)


class SocraticGuardrail:
    """
    Incremental output screen. `feed()` returns text that is safe to show now; text is held
    only until the end of the current sentence, so the stream still feels live.
    """

    def __init__(self, active: bool = True) -> None:
        self.active = active
        self.redactions = 0
        self._buffer = ""
        self._in_code = False
        self._in_example = False

    def feed(self, text: str) -> str:
        if not self.active:
            return text
        self._buffer += text
        out: list[str] = []
        while self._buffer:
            if self._in_code:
                end = self._buffer.find("```")
                if end == -1:
                    keep = 2  # a fence may be split across chunks
                    if len(self._buffer) > keep:
                        out.append(self._buffer[:-keep])
                        self._buffer = self._buffer[-keep:]
                    break
                out.append(self._buffer[: end + 3])
                self._buffer = self._buffer[end + 3 :]
                self._in_code = False
                continue
            fence = self._buffer.find("```")
            boundary = _BOUNDARY.search(self._buffer)
            if fence != -1 and (boundary is None or fence < boundary.start()):
                out.append(self._screen(self._buffer[:fence]))
                out.append("```")
                self._buffer = self._buffer[fence + 3 :]
                self._in_code = True
                continue
            if boundary is None:
                break
            sentence, self._buffer = self._buffer[: boundary.end()], self._buffer[boundary.end() :]
            out.append(self._screen(sentence))
        return "".join(out)

    def flush(self) -> str:
        remaining, self._buffer = self._buffer, ""
        if not self.active or self._in_code:
            return remaining
        return self._screen(remaining)

    def _screen(self, sentence: str) -> str:
        if not sentence.strip():
            if sentence.count("\n") and self._in_example:
                self._in_example = False  # a blank line closes the example paragraph
            return sentence
        if _EXAMPLE_LABEL.search(sentence):
            self._in_example = True
        if self._in_example or not reveals_final_answer(sentence):
            return sentence
        self.redactions += 1
        trailing = sentence[len(sentence.rstrip()) :]
        return SOCRATIC_REDIRECT.rstrip() + (trailing or " ")


class HintSplitter:
    """
    Separates the visible reply from the trailing `[[HINTS]]` section while streaming.
    Holds back any suffix that could be the start of the marker (plus decoration such as
    `**`) so the marker never leaks into the visible text.
    """

    def __init__(self) -> None:
        self.hint_text = ""
        self._pending = ""
        self._found = False

    def feed(self, text: str) -> str:
        if self._found:
            self.hint_text += text
            return ""
        self._pending += text
        index = self._pending.find(HINTS_MARKER)
        if index != -1:
            visible = self._pending[:index].rstrip(" *#\n")
            self.hint_text += self._pending[index + len(HINTS_MARKER) :]
            self._pending = ""
            self._found = True
            return visible
        keep = 0
        for size in range(min(len(HINTS_MARKER) - 1, len(self._pending)), 0, -1):
            if HINTS_MARKER.startswith(self._pending[-size:]):
                keep = size
                break
        stripped = self._pending[: len(self._pending) - keep]
        decoration = len(stripped) - len(stripped.rstrip(" *#\n"))
        keep += decoration
        emit = self._pending[: len(self._pending) - keep]
        self._pending = self._pending[len(self._pending) - keep :]
        return emit

    def flush(self) -> str:
        if self._found:
            return ""
        remaining, self._pending = self._pending, ""
        return remaining


_HINT_LINE = re.compile(r"^\s*(?:tier\s*)?([1-3])\s*[).:\-]\s*(.+)$", re.IGNORECASE)
_HINT_LABEL = re.compile(r"^\s*(?:(?:tier|hint)\s*[1-3]\s*[:.)\-]|\(?[1-3]\)|nudge\s*:|scaffold\s*:)\s*", re.IGNORECASE)


def parse_hints(text: str) -> list[Hint]:
    """
    Parses the hint section into a three-rung ladder. Prefers explicit `1) 2) 3)` numbering;
    models often drop the numbers (or embed their own step lists), so it falls back to reading
    the first three non-empty lines as tiers 1-3.
    """
    lines = [raw.strip().lstrip("-*• ").replace("**", "") for raw in text.splitlines()]
    lines = [line for line in lines if line]
    numbered: dict[int, str] = {}
    current: int | None = None
    for line in lines:
        match = _HINT_LINE.match(line)
        if match and int(match.group(1)) == len(numbered) + 1:
            current = int(match.group(1))
            numbered[current] = match.group(2).strip()
        elif current is not None:
            numbered[current] = f"{numbered[current]} {line}"
    if len(numbered) == 3:
        texts = [numbered[1], numbered[2], numbered[3]]
    elif len(lines) >= 3:
        texts = [_HINT_LABEL.sub("", line, count=1).strip() for line in lines[:3]]
    else:
        return []
    return [Hint(tier=tier, title=HINT_TITLES[tier], text=body) for tier, body in enumerate(texts, 1) if body]


def split_sentences(text: str) -> list[str]:
    """Splits prose into sentences for speech synthesis and offline composition."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[$*])", text.strip())
    return [p.strip() for p in parts if p.strip()]
