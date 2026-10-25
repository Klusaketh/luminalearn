"""Subjects module content: the authoring format, the auditor, and syllabus completeness."""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.subject_content import (
    MIN_PRACTICE_QUESTIONS,
    OVERVIEW_SECTIONS,
    REQUIRED_SECTIONS,
    SUBJECTS_ROOT,
    ContentError,
    LessonSource,
    audit_lesson,
    h2_sections,
    iter_topics,
    load_lessons,
    load_overview,
    load_subject_catalog,
    parse_front_matter,
)

CATALOG = load_subject_catalog()
EXPECTED_SUBJECTS = {
    "computer-science": [
        "Data Structures & Algorithms", "Operating Systems", "Database Management Systems",
        "Computer Networks", "Digital Logic", "Computer Organization & Architecture",
    ],
    "programming": ["Python", "C Programming", "C++", "Java"],
    "artificial-intelligence": [
        "Artificial Intelligence", "Machine Learning", "Deep Learning",
        "Generative Adversarial Networks (GANs)", "Natural Language Processing", "Computer Vision",
    ],
    "mathematics": ["Discrete Mathematics", "Probability", "Statistics", "Linear Algebra", "Calculus", "Numerical Methods"],
}


def _lesson(body: str, objectives: int = 2) -> LessonSource:
    return LessonSource("t", "t", "T", "S", 10, "theory", [f"objective {i}" for i in range(objectives)], body, Path("t.md"))


def _complete_body(words: int = 950, questions: int = MIN_PRACTICE_QUESTIONS) -> str:
    filler = " ".join(["word"] * words)
    sections = []
    for name in REQUIRED_SECTIONS:
        text = filler if name == "Core theory" else "Text."
        if name == "Worked examples":
            text = "### Example 1: tracing\nSteps."
        if name == "Practice questions":
            text = "\n\n".join(f":::question basic\nQ{i}?\n:::answer\nAn answer that explains why.\n:::" for i in range(questions))
        sections.append(f"## {name}\n\n{text}")
    return "\n\n".join(sections)


# ---------------------------------------------------------------------- format


def test_front_matter_parses_scalars_and_lists():
    meta, body = parse_front_matter("---\nlesson: a-b\ntitle: \"Quoted: title\"\nminutes: 40\nobjectives:\n  - one\n  - two\n---\n\n## Introduction\n")
    assert meta == {"lesson": "a-b", "title": "Quoted: title", "minutes": "40", "objectives": ["one", "two"]}
    assert body.startswith("## Introduction")


@pytest.mark.parametrize("bad", ["---\nlesson: x\n", "---\n  - orphan item\n---\n", "---\njust words\n---\n"])
def test_front_matter_rejects_malformed_headers(bad: str):
    with pytest.raises(ContentError):
        parse_front_matter(bad)


def test_h2_sections_ignore_headings_inside_code():
    assert h2_sections("## Real\n```python\n## not a heading\n```\n## Also real") == ["Real", "Also real"]


def test_audit_accepts_a_complete_lesson():
    audit = audit_lesson(_lesson(_complete_body()))
    assert audit.complete, audit
    assert audit.questions == MIN_PRACTICE_QUESTIONS and audit.levels == {"basic": MIN_PRACTICE_QUESTIONS}


@pytest.mark.parametrize(
    ("body", "reason"),
    [
        (_complete_body(words=200), "too short"),
        (_complete_body(questions=MIN_PRACTICE_QUESTIONS - 1), "too few questions"),
        (_complete_body().replace("## Common mistakes", "## Pitfalls"), "missing section"),
        (_complete_body().replace(":::answer\nAn answer that explains why.", ":::answer\nYes."), "empty answer"),
        (_complete_body() + "\n\n$$ x^2", "unbalanced math"),
        (_complete_body() + "\n\nTODO: write this", "placeholder"),
        (_complete_body().replace("### Example 1", "### Walkthrough"), "no worked example"),
    ],
)
def test_audit_rejects_incomplete_lessons(body: str, reason: str):
    assert not audit_lesson(_lesson(body)).complete, reason


def test_audit_rejects_too_few_objectives():
    assert not audit_lesson(_lesson(_complete_body(), objectives=1)).complete


# ---------------------------------------------------------------------- catalog


def test_all_22_subjects_are_preserved_with_their_categories():
    found: dict[str, list[str]] = {}
    for subject in CATALOG:
        found.setdefault(subject["category_slug"], []).append(subject["name"])
    assert found == EXPECTED_SUBJECTS


def test_slugs_are_unique_where_the_database_requires_it():
    subject_slugs = [s["slug"] for s in CATALOG]
    assert len(subject_slugs) == len(set(subject_slugs))
    for subject in CATALOG:
        for course in subject["courses"]:
            module_slugs = [m["slug"] for m in course["modules"]]
            assert len(module_slugs) == len(set(module_slugs)), subject["slug"]
            for module in course["modules"]:
                topic_slugs = [t["slug"] for t in module["topics"]]
                assert len(topic_slugs) == len(set(topic_slugs)), module["slug"]
        topic_slugs = [t["slug"] for (_, _, t) in iter_topics(subject)]
        assert len(topic_slugs) == len(set(topic_slugs)), f"{subject['slug']}: lesson files are named by topic slug"


@pytest.mark.parametrize("subject", CATALOG, ids=[s["slug"] for s in CATALOG])
def test_every_lesson_file_belongs_to_a_topic(subject: dict):
    topics = {t["slug"] for (_, _, t) in iter_topics(subject)}
    strays = sorted(set(load_lessons(subject["slug"])) - topics)
    assert not strays, f"lesson files without a syllabus topic: {strays}"


# ---------------------------------------------------------------------- completeness


@pytest.mark.parametrize("subject", CATALOG, ids=[s["slug"] for s in CATALOG])
def test_subject_overview_is_complete(subject: dict):
    overview = load_overview(subject["slug"])
    assert overview, f"{SUBJECTS_ROOT / subject['slug'] / 'overview.md'} is missing"
    missing = [s for s in OVERVIEW_SECTIONS if s not in h2_sections(overview)]
    assert not missing, f"overview is missing sections: {missing}"
    assert len(overview.split("## ")[0].split()) >= 80, "the opening overview should explain the subject's scope and purpose"


@pytest.mark.parametrize("subject", CATALOG, ids=[s["slug"] for s in CATALOG])
def test_every_topic_has_a_complete_lesson(subject: dict):
    lessons = load_lessons(subject["slug"])
    problems = []
    for _, _, topic in iter_topics(subject):
        lesson = lessons.get(topic["slug"])
        if lesson is None:
            problems.append(f"{topic['slug']}: no lesson file")
            continue
        audit = audit_lesson(lesson)
        if not audit.complete:
            detail = audit.issues + [f"missing {audit.missing_sections}"] * bool(audit.missing_sections)
            detail += [f"{audit.questions} questions"] * (audit.questions < MIN_PRACTICE_QUESTIONS)
            detail += [f"{audit.words} words"] * (audit.words < 900)
            problems.append(f"{topic['slug']}: {'; '.join(detail) or 'incomplete'}")
    assert not problems, "\n".join(problems)
