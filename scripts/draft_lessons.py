"""
Draft lessons for syllabus topics that have no lesson file yet, with the Gemini gateway.

A draft is saved only when it passes the same checks as a hand-written lesson:
- the completeness audit (eight sections in order, worked examples, five or more answered
  questions, objectives, 900+ words, no placeholders), and
- the lesson code check: every runnable example (a code block followed by an `Output:` text
  block) is compiled and run, and the program must print exactly what the lesson says.
Problems are sent back to the model to fix, up to MAX_REPAIRS times; a draft that still fails
is not written. Saved drafts carry `review: ai-draft` in their front matter until a person has
reviewed them. Existing lesson files are never overwritten, so the script can be re-run.

Usage, from the repository root, with GEMINI_API_KEY in backend/.env:
    backend/.venv/bin/python scripts/draft_lessons.py [--subject SLUG ...] [--limit N] [--concurrency N]
"""

from __future__ import annotations

import argparse
import asyncio
import itertools
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
os.chdir(ROOT / "backend")  # settings read backend/.env

from ai.llm import GatewayConfig, GeminiGateway  # noqa: E402
from ai.llm.gemini_gateway import LLMUnavailableError  # noqa: E402
from app.core.config import settings  # noqa: E402
from scripts.subject_content import (  # noqa: E402
    REQUIRED_SECTIONS,
    SUBJECTS_ROOT,
    ContentError,
    audit_lesson,
    h2_sections,
    iter_topics,
    load_lesson,
    load_subject_catalog,
)

MAX_REPAIRS = 3
EXEMPLAR = SUBJECTS_ROOT / "data-structures-and-algorithms" / "lessons" / "amortized-analysis.md"

# Same convention as backend/tests/test_lesson_code.py.
FENCE = re.compile(r"^```([\w+-]*)[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
BETWEEN_OK = re.compile(r"^\s*(?:\*{0,2}output:?\*{0,2}\s*)?$", re.IGNORECASE)
RUNNABLE = {"python", "java", "c", "cpp"}

SYSTEM = (
    "You are an experienced university lecturer and textbook author writing one lesson for LuminaLearn, "
    "a self-study platform for engineering and computer science students. Accuracy comes first: every "
    "definition, formula, derivation, algorithm trace, table value, and program output must be correct and "
    "consistent with standard textbooks. Where sources genuinely differ, say so briefly instead of guessing. "
    "Write clear, friendly, precise English for a motivated second-year student. Output only the lesson file."
)

RULES = """\
Write the complete lesson file in Markdown, following every rule below.

1. Start with this front matter, filling in the summary and objectives:
---
lesson: {slug}
title: {title}
summary: <one sentence of at most 35 words>
minutes: {minutes}
type: theory
objectives:
  - <3 to 5 measurable objectives, each starting with a verb>
---

2. After the front matter, use exactly these eight H2 sections, in this order, and no other H2 headings:
{sections}

3. Introduction: motivate the topic with a concrete situation, say what the lesson covers, and end with a line
   starting "**Before you start:**" that names the prerequisite ideas.
4. Core theory: four to seven "### " subsections. Bold each key term where it is defined. Use KaTeX math:
   $...$ inline and $$...$$ for display equations on their own lines (never \\( \\) or \\[ \\]). Use GitHub
   tables where they help. At most one Mermaid diagram, only if accurate: a ```mermaid block starting with
   "flowchart LR" or "flowchart TD", nodes like A[Plain words] and edges A --> B or A -->|label| B, with no
   parentheses, quotes, colons, or semicolons inside labels.
5. Worked examples: two or three subsections titled "### Example 1: <what it shows>", "### Example 2: ...",
   each solved step by step with the final answer stated clearly. Check every number.
6. Applications: three to five bullets on where this is used in practice.
7. Common mistakes: four to six bullets, each "**The mistake.** Why it is wrong and how to avoid it."
8. Revision notes: six to ten short bullets with the facts and formulas to remember.
9. Practice questions: exactly six questions, two basic, two intermediate, two advanced, each in exactly this
   syntax (the page hides answers until the learner opens them):
:::question basic
The question.
:::answer
The answer, with the reasoning in at least two sentences.
:::
10. Further learning: two to four bullets starting "**Next:**" or "**Related:**" that point to LuminaLearn topics
    from the list below by their exact titles in italics, saying why each is useful. You may add one widely known
    textbook you are certain exists, as author and title only (no edition, chapter, page, or URL).
11. Length: 1,600 to 2,400 words.
12. Code appears only where it teaches something, in fenced blocks with a language: python, c, cpp, java, sql, bash, or
    text. To show what a program prints, put a line "Output:" after its code block, then a ```text block with exactly
    the printed output. Every such program is compiled and run automatically and must print exactly that output:
    Python 3.12 using only the standard library; C11 with int main(void); C++17 with int main(); Java with
    public class Main. Never put a ```text block directly after a code block unless it is that program's exact
    output. Code that reads input, files, or the network, uses randomness without a fixed seed, timing, threads, or
    third-party libraries (such as numpy or PyTorch) may appear, but without an Output block.
13. No H1 headings, HTML, emojis, links, or placeholder text such as TODO, TBD, or "coming soon". No course codes,
    semester or exam references. Do not wrap the whole file in a code fence.
"""

PROMPT = """\
Subject: {subject} — {subject_description}
Course: {course}
Module: {module} — {module_description}
Lesson topic: {title}
Topic summary: {summary}
Level: {difficulty}. Study time: about {minutes} minutes.

Earlier topics in this course (the learner has studied these): {earlier}
Later topics in this course (do not teach these in depth; point to them): {later}
Other LuminaLearn topics you may reference in Further learning: {related}

{rules}

Here is a published LuminaLearn lesson from another subject. Match its depth, tone, and formatting (not its topic):

<example_lesson>
{exemplar}
</example_lesson>
"""


# --------------------------------------------------------------------------- checks


def _normalise(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _run(args: list[str], cwd: Path, timeout: int) -> tuple[bool, str]:
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)  # noqa: S603 - runs a lesson example the script just wrote
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout} s"
    if result.returncode != 0:
        return False, f"exit code {result.returncode}: {(result.stderr or result.stdout)[-1200:]}"
    return True, result.stdout


def run_example(language: str, code: str) -> tuple[bool, str]:
    """(ran successfully, stdout or error) for one runnable example, like test_lesson_code.py."""
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)
        if language == "python":
            return _run([sys.executable, "-I", "-c", code], cwd, timeout=20)
        if language == "java":
            name = re.search(r"public\s+(?:final\s+)?class\s+(\w+)", code)
            main_class = name.group(1) if name else "Main"
            (cwd / f"{main_class}.java").write_text(code, encoding="utf-8")
            ok, out = _run(["javac", f"{main_class}.java"], cwd, timeout=120)
            return _run(["java", "-cp", ".", main_class], cwd, timeout=20) if ok else (False, f"javac failed: {out}")
        compiler = shutil.which("gcc" if language == "c" else "g++")
        if compiler is None:
            return True, ""  # cannot check here; the test skips it too
        source = cwd / ("main.c" if language == "c" else "main.cpp")
        source.write_text(code, encoding="utf-8")
        std = "-std=c11" if language == "c" else "-std=c++17"
        ok, out = _run([compiler, std, "-O0", "-o", "main", source.name, *(["-lm"] if language == "c" else [])], cwd, timeout=120)
        return _run(["./main"], cwd, timeout=20) if ok else (False, f"compile failed: {out}")


def check_lesson(text: str, slug: str) -> list[str]:  # noqa: C901 - a flat list of publishing rules
    """Every problem that would stop this draft from being published (empty when it is ready)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{slug}.md"
        path.write_text(text, encoding="utf-8")
        try:
            lesson = load_lesson(path)
        except ContentError as exc:
            return [f"front matter: {exc}"]
    problems: list[str] = []
    audit = audit_lesson(lesson)
    if audit.missing_sections:
        problems.append(f"missing H2 sections: {', '.join(audit.missing_sections)}")
    extra = [s for s in h2_sections(lesson.content) if s not in REQUIRED_SECTIONS]
    if extra:
        problems.append(f"remove these extra H2 headings (use ### inside a section instead): {', '.join(extra)}")
    if audit.worked_examples < 2:
        problems.append("Worked examples needs at least two '### Example N: ...' subsections")
    if audit.questions < 5:
        problems.append(f"only {audit.questions} correctly formatted practice questions; write six in the exact :::question syntax")
    if audit.unanswered:
        problems.append(f"{audit.unanswered} practice questions have no real answer")
    if audit.words < 1200:
        problems.append(f"the lesson is only {audit.words} words; expand Core theory and the worked examples to 1,600+ words")
    if len(lesson.learning_objectives) < 3:
        problems.append("write three to five learning objectives")
    problems.extend(audit.issues)
    if re.search(r"\\\(|\\\[", lesson.content):
        problems.append("use $...$ and $$...$$ for math, never \\( \\) or \\[ \\]")
    for block in re.finditer(r"^```mermaid[ \t]*\n(.*?)^```", lesson.content, re.MULTILINE | re.DOTALL):
        first = block.group(1).strip().splitlines()[0] if block.group(1).strip() else ""
        if not re.match(r"flowchart (LR|TD)\b", first):
            problems.append("a mermaid diagram must start with 'flowchart LR' or 'flowchart TD'")
    blocks = list(FENCE.finditer(lesson.content))
    for code, output in itertools.pairwise(blocks):
        language = code.group(1)
        if language in RUNNABLE and output.group(1) == "text" and BETWEEN_OK.match(lesson.content[code.end() : output.start()]):
            ok, actual = run_example(language, code.group(2))
            if not ok:
                snippet = code.group(2).strip().splitlines()[0][:80]
                problems.append(
                    f"the {language} program starting `{snippet}` does not run ({actual}). Fix the program, "
                    "or remove its Output block if it cannot run on its own."
                )
            elif _normalise(actual) != _normalise(output.group(2)):
                snippet = code.group(2).strip().splitlines()[0][:80]
                problems.append(
                    f"the {language} program starting `{snippet}` prints:\n```text\n{actual.strip()[:1500]}\n```\n"
                    f"but its Output block says:\n```text\n{output.group(2).strip()[:1500]}\n```\n"
                    "Make the Output block exactly what the program prints, and make the explanation agree with it."
                )
    return problems


# --------------------------------------------------------------------------- drafting


def _strip_wrapper(text: str) -> str:
    text = text.strip()
    wrapped = re.match(r"^```(?:markdown|md)?[ \t]*\n(.*)\n```$", text, re.DOTALL)
    if wrapped:
        text = wrapped.group(1).strip()
    start = text.find("---\n")
    return text[start:] if start > 0 and not text.startswith("---\n") else text


def _with_review_flag(text: str) -> str:
    """Marks the front matter as an AI draft awaiting human review."""
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end == -1 or "\nreview:" in text[:end]:
        return text
    return text[:end] + "\nreview: ai-draft" + text[end:]


def _titles(entries: list[tuple[dict, dict, dict]]) -> str:
    return "; ".join(t["title"] for _, _, t in entries) or "none"


async def draft_topic(gateway: GeminiGateway, job: dict, log) -> bool:
    prompt = PROMPT.format(
        **job,
        rules=RULES.format(
            slug=job["slug"], title=job["title"], minutes=job["minutes"],
            sections="\n".join(f"## {name}" for name in REQUIRED_SECTIONS),
        ),
        exemplar=EXEMPLAR.read_text(encoding="utf-8"),
    )
    contents: list[dict] = [{"role": "user", "parts": [{"text": prompt}]}]
    started = time.monotonic()
    for attempt in range(MAX_REPAIRS + 1):
        text = None
        for wait in (0, 30, 60, 120, 180):
            if wait:
                await asyncio.sleep(wait)
            try:
                result = await gateway.generate_text(
                    contents, system_instruction=SYSTEM, temperature=0.35,
                    max_output_tokens=24000, thinking="medium", timeout_s=420,
                )
                text = _strip_wrapper(result.text)
                break
            except LLMUnavailableError as exc:
                log(f"  {job['key']}: model unavailable ({exc}); retrying")
                for model in gateway.config.text_models:  # all cooling down: clear and retry after the wait
                    gateway.health.mark_healthy(model)
        if text is None:
            log(f"FAILED {job['key']}: no model answered")
            return False
        problems = await asyncio.to_thread(check_lesson, text, job["slug"])
        if not problems:
            job["path"].parent.mkdir(parents=True, exist_ok=True)
            job["path"].write_text(_with_review_flag(text).rstrip() + "\n", encoding="utf-8")
            words = len(text.split())
            log(f"ok {job['key']} ({words} words, {attempt} repairs, {time.monotonic() - started:.0f}s, {result.model})")
            return True
        log(f"  {job['key']}: attempt {attempt + 1} has {len(problems)} problems: {problems[0][:160]}")
        contents += [
            {"role": "model", "parts": [{"text": text}]},
            {"role": "user", "parts": [{"text": (
                "Your lesson cannot be published yet. Fix these problems:\n\n"
                + "\n\n".join(f"- {p}" for p in problems)
                + "\n\nReturn the complete corrected lesson file (front matter and all eight sections). Keep everything "
                "else that is correct, and re-check every number and program output."
            )}]},
        ]
    log(f"FAILED {job['key']}: still has problems after {MAX_REPAIRS} repairs: {problems}")
    return False


def collect_jobs(subjects: list[str] | None) -> list[dict]:
    catalog = load_subject_catalog()
    all_titles = {s["slug"]: [t["title"] for _, _, t in iter_topics(s)] for s in catalog}
    jobs = []
    for subject in catalog:
        if subjects and subject["slug"] not in subjects:
            continue
        triples = iter_topics(subject)
        for index, (course, module, topic) in enumerate(triples):
            path = SUBJECTS_ROOT / subject["slug"] / "lessons" / f"{topic['slug']}.md"
            if path.exists():
                continue
            same_course = [entry for entry in triples if entry[0] is course]
            position = next(i for i, entry in enumerate(same_course) if entry[2] is topic)
            others = [t for slug, titles in all_titles.items() if slug != subject["slug"] for t in titles[:3]]
            jobs.append({
                "key": f"{subject['slug']}/{topic['slug']}",
                "path": path,
                "slug": topic["slug"],
                "title": topic["title"],
                "summary": topic.get("summary", ""),
                "difficulty": topic.get("difficulty", "Intermediate"),
                "minutes": topic.get("estimated_minutes", 45),
                "subject": subject["name"],
                "subject_description": subject.get("short_description") or subject.get("description", ""),
                "course": course["title"],
                "module": module["title"],
                "module_description": module.get("description", ""),
                "earlier": _titles(same_course[max(0, position - 6) : position]),
                "later": _titles(same_course[position + 1 : position + 5]),
                "related": "; ".join(all_titles[subject["slug"]][:index] + all_titles[subject["slug"]][index + 1 :])
                + "; " + "; ".join(others[:20]),
            })
    return jobs


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--subject", action="append", help="only this subject slug (repeatable)")
    parser.add_argument("--limit", type=int, default=0, help="draft at most this many lessons")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    gateway = GeminiGateway(GatewayConfig(
        api_key=settings.GEMINI_API_KEY,
        text_models=tuple(dict.fromkeys([settings.GEMINI_MODEL_FLASH, "gemini-3-flash-preview", "gemini-flash-latest"])),
        temperature=0.35, max_output_tokens=24000, request_timeout_s=420,
    ))
    if not gateway.enabled:
        print("GEMINI_API_KEY is not configured in backend/.env", file=sys.stderr)
        return 1
    jobs = collect_jobs(args.subject)
    if args.limit:
        jobs = jobs[: args.limit]
    print(f"Drafting {len(jobs)} lessons with concurrency {args.concurrency}", flush=True)

    def log(message: str) -> None:
        print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)

    semaphore = asyncio.Semaphore(args.concurrency)

    async def guarded(job: dict) -> bool:
        async with semaphore:
            try:
                return await draft_topic(gateway, job, log)
            except Exception as exc:  # noqa: BLE001 - one bad topic must not stop the batch
                log(f"FAILED {job['key']}: {type(exc).__name__}: {exc}")
                return False

    results = await asyncio.gather(*(guarded(job) for job in jobs))
    print(f"Done: {sum(results)} drafted, {len(results) - sum(results)} failed", flush=True)
    return 0 if all(results) else 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
