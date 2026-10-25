"""
Every lesson code example that shows its output is executed, and the output must match.

Convention (content/README.md): a fenced code block followed by an `Output:` line and a
` ```text ` block is a runnable example. Python always runs; Java, C, and C++ run when a
compiler is available on the machine and are skipped otherwise.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.subject_content import SUBJECTS_ROOT

FENCE = re.compile(r"^```([\w+-]*)[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
BETWEEN_OK = re.compile(r"^\s*(?:\*{0,2}output:?\*{0,2}\s*)?$", re.IGNORECASE)
RUNNABLE = {"python", "java", "c", "cpp"}


def _examples() -> list[tuple[str, str, str, str]]:
    found = []
    for path in sorted(SUBJECTS_ROOT.glob("*/lessons/*.md")):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        blocks = list(FENCE.finditer(text))
        for index, (code, output) in enumerate(zip(blocks, blocks[1:])):
            if code.group(1) in RUNNABLE and output.group(1) == "text" and BETWEEN_OK.match(text[code.end() : output.start()]):
                case_id = f"{path.parent.parent.name}/{path.stem}#{index}"
                found.append((case_id, code.group(1), code.group(2), output.group(2)))
    return found


EXAMPLES = _examples()


def _normalise(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _run(args: list[str], cwd: Path, timeout: int = 30) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    assert result.returncode == 0, f"exit {result.returncode}\n{result.stderr[-2000:]}"
    return result.stdout


def _c_compiler(language: str) -> list[str] | None:
    names = ("gcc", "clang", "cc") if language == "c" else ("g++", "clang++")
    for name in names:
        if shutil.which(name):
            return [name]
    zig = os.environ.get("LESSON_ZIG")  # optional: a zig binary provides a portable C/C++ toolchain
    if zig and Path(zig).exists():
        return [zig, "cc" if language == "c" else "c++"]
    return None


def test_examples_were_found():
    assert len(EXAMPLES) >= 1


@pytest.mark.parametrize(("case_id", "language", "code", "expected"), EXAMPLES, ids=[e[0] for e in EXAMPLES])
def test_example_output_matches(case_id: str, language: str, code: str, expected: str, tmp_path: Path):
    if language == "python":
        actual = _run([sys.executable, "-I", "-c", code], tmp_path)
    elif language == "java":
        if not shutil.which("javac"):
            pytest.skip("javac not installed")
        name = re.search(r"public\s+(?:final\s+)?class\s+(\w+)", code)
        main_class = name.group(1) if name else "Main"
        (tmp_path / f"{main_class}.java").write_text(code, encoding="utf-8")
        _run(["javac", f"{main_class}.java"], tmp_path, timeout=120)
        actual = _run(["java", "-cp", ".", main_class], tmp_path)
    else:
        compiler = _c_compiler(language)
        if compiler is None:
            pytest.skip(f"no {language} compiler installed")
        source = tmp_path / ("main.c" if language == "c" else "main.cpp")
        source.write_text(code, encoding="utf-8")
        std = "-std=c11" if language == "c" else "-std=c++17"
        exe = tmp_path / ("main.exe" if os.name == "nt" else "main")
        _run([*compiler, std, "-O0", "-o", str(exe), str(source), *(["-lm"] if language == "c" and os.name != "nt" else [])], tmp_path, timeout=180)
        actual = _run([str(exe)], tmp_path)
    assert _normalise(actual) == _normalise(expected), f"{case_id}: output differs\n--- expected\n{expected}\n--- actual\n{actual}"
