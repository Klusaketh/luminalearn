"""
LuminaLearn AI — Subjects module content library.

The academic curriculum lives as plain files under content/ (format: content/README.md):

    content/categories.json                         the four academic categories
    content/subjects/<subject>/syllabus.json        subject metadata and its course -> module -> topic tree
    content/subjects/<subject>/overview.md          long-form overview: objectives, prerequisites, glossary, reading
    content/subjects/<subject>/lessons/<topic>.md   one lesson per topic: front matter + Markdown body

seed_academic_content.py syncs these files into the database, subjects_coverage.py reports on
them, and backend/tests/test_subject_content.py enforces the completeness rules defined here.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"
SUBJECTS_ROOT = CONTENT_ROOT / "subjects"

# Every lesson is a full study unit: these H2 sections, in this order.
REQUIRED_SECTIONS = (
    "Introduction",
    "Core theory",
    "Worked examples",
    "Applications",
    "Common mistakes",
    "Revision notes",
    "Practice questions",
    "Further learning",
)
MIN_PRACTICE_QUESTIONS = 5
MIN_OBJECTIVES = 2
# Below this a lesson is reported as too shallow to count as complete.
MIN_WORDS = 900
QUESTION_LEVELS = ("basic", "intermediate", "advanced")
OVERVIEW_SECTIONS = ("What you will learn", "Prerequisites", "Glossary", "Further reading")

# :::question <level>
# question (Markdown)
# :::answer
# answer and explanation (Markdown)
# :::
QUESTION_BLOCK = re.compile(
    r"^:::question(?:[ \t]+(?P<level>[a-z]+))?[ \t]*\n(?P<question>.*?)\n:::answer[ \t]*\n(?P<answer>.*?)\n:::[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
_PLACEHOLDERS = re.compile(r"\b(TODO|TBD|FIXME|lorem ipsum|coming soon|content pending)\b", re.IGNORECASE)


class ContentError(ValueError):
    """A content file breaks the authoring format."""


@dataclass(frozen=True)
class LessonSource:
    topic_slug: str
    slug: str
    title: str
    summary: str
    estimated_minutes: int
    lesson_type: str
    learning_objectives: list[str]
    content: str
    path: Path


@dataclass
class LessonAudit:
    sections: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    worked_examples: int = 0
    questions: int = 0
    unanswered: int = 0
    levels: dict[str, int] = field(default_factory=dict)
    words: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return (
            not self.missing_sections
            and self.worked_examples >= 1
            and self.questions >= MIN_PRACTICE_QUESTIONS
            and self.unanswered == 0
            and self.words >= MIN_WORDS
            and not self.issues
        )


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """
    Split `---`-fenced front matter from a Markdown body. The format is deliberately small:
    `key: value` lines, and `key:` followed by `  - item` lines for lists of strings.
    """
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ContentError("front matter is not closed with ---")
    meta: dict[str, Any] = {}
    current: list[str] | None = None
    for raw in text[4:end].split("\n"):
        if not raw.strip():
            continue
        stripped = raw.strip()
        if stripped.startswith("- "):
            if current is None:
                raise ContentError(f"list item outside a list: {raw!r}")
            current.append(_unquote(stripped[2:].strip()))
            continue
        key, sep, value = raw.partition(":")
        if not sep or raw[:1].isspace() or not key.strip():
            raise ContentError(f"unreadable front matter line: {raw!r}")
        value = value.strip()
        if value:
            meta[key.strip()] = _unquote(value)
            current = None
        else:
            current = []
            meta[key.strip()] = current
    return meta, text[end + 5 :].lstrip("\n")


def h2_sections(markdown: str) -> list[str]:
    """H2 headings outside fenced code blocks, in order."""
    headings: list[str] = []
    fence: str | None = None
    for line in markdown.split("\n"):
        marker = line.lstrip()[:3]
        if marker in ("```", "~~~"):
            fence = None if fence == marker else (fence or marker)
            continue
        if fence is None and line.startswith("## "):
            headings.append(line[3:].strip())
    return headings


def section_text(markdown: str, heading: str) -> str:
    """The body of one H2 section (up to the next H2), or an empty string."""
    match = re.search(rf"^## {re.escape(heading)}[ \t]*\n(.*?)(?=^## |\Z)", markdown, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def audit_lesson(lesson: LessonSource) -> LessonAudit:
    body = lesson.content
    audit = LessonAudit(sections=h2_sections(body), words=len(body.split()))
    audit.missing_sections = [s for s in REQUIRED_SECTIONS if s not in audit.sections]
    present = [s for s in audit.sections if s in REQUIRED_SECTIONS]
    if not audit.missing_sections and present != list(REQUIRED_SECTIONS):
        audit.issues.append("required sections are out of order")
    audit.worked_examples = len(re.findall(r"^### Example\b", section_text(body, "Worked examples"), re.MULTILINE))
    _audit_questions(body, audit)
    _audit_format(lesson, audit)
    return audit


def _audit_questions(body: str, audit: LessonAudit) -> None:
    for match in QUESTION_BLOCK.finditer(body):
        audit.questions += 1
        level = match.group("level") or "unlabelled"
        audit.levels[level] = audit.levels.get(level, 0) + 1
        if level not in QUESTION_LEVELS:
            audit.issues.append(f"question {audit.questions} has an unknown level {level!r}")
        if len(match.group("answer").split()) < 3:
            audit.unanswered += 1
    if body.count(":::question") != audit.questions:
        audit.issues.append("a :::question block is malformed (missing :::answer or closing :::)")


def _audit_format(lesson: LessonSource, audit: LessonAudit) -> None:
    body = lesson.content
    fences = sum(1 for line in body.split("\n") if line.lstrip().startswith("```"))
    if fences % 2:
        audit.issues.append("unbalanced ``` code fences")
    if body.count("$$") % 2:
        audit.issues.append("unbalanced $$ math delimiters")
    if re.search(r"^# ", body, re.MULTILINE) and not _inside_code(body, r"^# "):
        audit.issues.append("H1 heading in body (the page already shows the lesson title)")
    if _PLACEHOLDERS.search(body):
        audit.issues.append("placeholder text")
    if len(lesson.learning_objectives) < MIN_OBJECTIVES:
        audit.issues.append(f"fewer than {MIN_OBJECTIVES} learning objectives")


def _inside_code(markdown: str, pattern: str) -> bool:
    """True when every match of `pattern` sits inside a fenced code block."""
    fence: str | None = None
    for line in markdown.split("\n"):
        marker = line.lstrip()[:3]
        if marker in ("```", "~~~"):
            fence = None if fence == marker else (fence or marker)
            continue
        if fence is None and re.match(pattern, line):
            return False
    return True


def load_categories() -> list[dict[str, Any]]:
    categories: list[dict[str, Any]] = json.loads((CONTENT_ROOT / "categories.json").read_text(encoding="utf-8"))
    return sorted(categories, key=lambda c: c["display_order"])


def load_subject_catalog() -> list[dict[str, Any]]:
    """Every subject's syllabus, ordered by category and then by the subject's display order."""
    category_order = {c["slug"]: c["display_order"] for c in load_categories()}
    subjects = [json.loads(path.read_text(encoding="utf-8")) for path in SUBJECTS_ROOT.glob("*/syllabus.json")]
    for subject in subjects:
        if subject["category_slug"] not in category_order:
            raise ContentError(f"{subject['slug']}: unknown category {subject['category_slug']!r}")
    return sorted(subjects, key=lambda s: (category_order[s["category_slug"]], s["display_order"]))


def iter_topics(subject: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]:
    """(course, module, topic) triples in syllabus order."""
    return [
        (course, module, topic)
        for course in subject.get("courses", [])
        for module in course.get("modules", [])
        for topic in module.get("topics", [])
    ]


def load_overview(subject_slug: str) -> str | None:
    path = SUBJECTS_ROOT / subject_slug / "overview.md"
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").strip() if path.exists() else None


def load_lesson(path: Path) -> LessonSource:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    missing = [key for key in ("lesson", "title", "summary", "minutes") if not meta.get(key)]
    if missing:
        raise ContentError(f"{path}: front matter is missing {', '.join(missing)}")
    objectives = meta.get("objectives", [])
    if not isinstance(objectives, list):
        raise ContentError(f"{path}: objectives must be a list")
    try:
        minutes = int(meta["minutes"])
    except ValueError as exc:
        raise ContentError(f"{path}: minutes must be a whole number") from exc
    return LessonSource(
        topic_slug=path.stem,
        slug=str(meta["lesson"]),
        title=str(meta["title"]),
        summary=str(meta["summary"]),
        estimated_minutes=minutes,
        lesson_type=str(meta.get("type", "theory")),
        learning_objectives=[str(o) for o in objectives],
        content=body.strip() + "\n",
        path=path,
    )


def load_lessons(subject_slug: str) -> dict[str, LessonSource]:
    """The subject's lessons keyed by topic slug (the file name)."""
    folder = SUBJECTS_ROOT / subject_slug / "lessons"
    return {path.stem: load_lesson(path) for path in sorted(folder.glob("*.md"))} if folder.exists() else {}
