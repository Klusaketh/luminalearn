"""
LuminaLearn AI — Code Diagnostic Agent.
Module: ai/agents/code_diagnostic.py

Static analysis first, LLM second: Python is parsed with `ast` to pinpoint syntax errors,
recursion without a reachable base case, exponential re-computation, mutation while
iterating, mutable defaults and other classic bugs, and to estimate Big-O from loop
nesting and recursion shape. C-family languages get bracket and condition heuristics.
Findings are framed as questions so the learner makes the fix.
"""

import ast
import re

from ai.agents.base import AgentContext, SpecialistAgent
from ai.agents.schema import AgentDraft, CodeAnalysis, CodeFinding, Severity
from ai.prompts.templates import CODE_DIAGNOSTIC

_FENCE = re.compile(r"```([\w+#-]*)[^\n]*\n(.*?)(?:```|$)", re.DOTALL)
_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
_SHADOWED_BUILTINS = frozenset({"list", "dict", "str", "sum", "max", "min", "id", "input", "type", "len", "set", "map", "filter", "print", "sorted"})
_MUTATORS = frozenset({"append", "remove", "pop", "insert", "extend", "clear", "discard", "add"})
# Anything nested under one of these runs conditionally (or not at all) within its statement.
_CONDITIONAL = (
    ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.BoolOp, ast.Match,
    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef,
)
_C_FAMILY_SIGNAL = re.compile(r"#include|std::|int main\s*\(|public\s+(static\s+)?\w+|System\.out|\bfunction\b|=>|\bconst\b|\blet\b|console\.|;\s*$", re.MULTILINE)
_PYTHON_BLOCK = re.compile(r"^\s*(def|class|for|while|if|elif|else|try|except|finally|with)\b.*:\s*(#.*)?$", re.MULTILINE)


def extract_code(message: str) -> tuple[str, str | None]:
    """Returns (code, language hint). Prefers a fenced block; otherwise the code-looking tail of the message."""
    fence = _FENCE.search(message)
    if fence:
        return fence.group(2).rstrip(), (fence.group(1) or None)
    lines = message.splitlines()
    code_start = re.compile(r"^\s*(def |class |for |while |if |import |from |function |const |let |var |#include|public |int |return )")
    for index, line in enumerate(lines):
        if code_start.match(line):
            return "\n".join(lines[index:]).rstrip(), None
    return message.strip(), None


def detect_language(code: str, hint: str | None) -> str:
    if hint:
        aliases = {"py": "python", "python3": "python", "js": "javascript", "ts": "typescript", "c++": "cpp", "cc": "cpp"}
        return aliases.get(hint.lower(), hint.lower())
    try:
        ast.parse(code)
        if not re.search(r"#include|\bfunction\b|=>|System\.out", code):
            return "python"
    except SyntaxError:
        is_c_family = bool(_C_FAMILY_SIGNAL.search(code))
        if _PYTHON_BLOCK.search(code) and not re.search(r"^\s*(case|default)\b", code, re.MULTILINE) and not is_c_family:
            return "python"  # Python that fails to parse: report its syntax error
    if re.search(r"#include|std::|int main\s*\(", code):
        return "cpp"
    if re.search(r"public\s+(static\s+)?\w+|System\.out", code):
        return "java"
    if re.search(r"\bfunction\b|=>|\bconst\b|\blet\b|console\.", code):
        return "javascript"
    return "unknown"


def _is_self_call(node: ast.AST, name: str) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (isinstance(func, ast.Name) and func.id == name) or (isinstance(func, ast.Attribute) and func.attr == name)


def _always_calls(node: ast.AST, name: str) -> bool:
    """True when executing `node` always reaches a call to `name` (no branch or loop guards it)."""
    if _is_self_call(node, name):
        return True
    if isinstance(node, _CONDITIONAL):
        return False
    return any(_always_calls(child, name) for child in ast.iter_child_nodes(node))


def _can_exit(statement: ast.stmt) -> bool:
    return any(isinstance(n, ast.Return | ast.Raise) for n in ast.walk(statement))


class _PythonAnalyzer:
    """Collects findings and complexity evidence from one parsed module."""

    def __init__(self, tree: ast.Module) -> None:
        self.tree = tree
        self.findings: list[CodeFinding] = []
        self.max_loop_depth = 0
        # "exponential" | "divide_and_conquer" | "logarithmic" | "tree" | "linear"
        self.recursion_shape: str | None = None
        self.grows_collection_in_loop = False

    def run(self) -> None:
        self._walk_loops(self.tree.body, 0)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                self._check_function(node)
            elif isinstance(node, ast.Compare):
                self._check_compare(node)
            elif isinstance(node, ast.ExceptHandler) and node.type is None:
                self._add("warning", node.lineno, "Bare except",
                          "A bare `except:` also swallows KeyboardInterrupt and real bugs, hiding what went wrong.",
                          "Which specific exception do you actually expect this block to handle?")
            elif isinstance(node, ast.For):
                self._check_for(node)
            elif isinstance(node, ast.While):
                self._check_while(node)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id in _SHADOWED_BUILTINS:
                self._add("info", node.lineno, f"Shadows the built-in `{node.id}`",
                          f"Assigning to `{node.id}` hides Python's built-in `{node.id}()` for the rest of this scope.",
                          f"What would happen if you later called `{node.id}(...)` in this scope?")
            for field in ("body", "orelse", "finalbody"):
                block = getattr(node, field, None)
                if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
                    self._check_unreachable_block(block)

    def _add(self, severity: Severity, line: int | None, title: str, detail: str, question: str) -> None:
        if any(f.title == title and f.line == line for f in self.findings):
            return
        self.findings.append(CodeFinding(severity=severity, line=line, title=title, detail=detail, question=question))

    # -- loops ---------------------------------------------------------------

    def _walk_loops(self, body: list[ast.stmt], depth: int) -> None:
        for statement in body:
            is_loop = isinstance(statement, ast.For | ast.While | ast.AsyncFor)
            current = depth + 1 if is_loop else depth
            if is_loop:
                self.max_loop_depth = max(self.max_loop_depth, current)
                if any(
                    isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in {"append", "extend", "add"}
                    for n in ast.walk(statement)
                ):
                    self.grows_collection_in_loop = True
            for node in ast.walk(statement):
                if isinstance(node, ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp):
                    self.max_loop_depth = max(self.max_loop_depth, current + len(node.generators))
            for field in ("body", "orelse", "finalbody"):
                children = getattr(statement, field, None)
                if isinstance(children, list) and children and isinstance(children[0], ast.stmt):
                    self._walk_loops(children, current)
            for handler in getattr(statement, "handlers", []) or []:
                if isinstance(handler, ast.ExceptHandler):
                    self._walk_loops(handler.body, current)

    def _check_for(self, node: ast.For) -> None:
        iterated = node.iter
        if isinstance(iterated, ast.Call) and isinstance(iterated.func, ast.Name) and iterated.func.id == "range" and iterated.args:
            stop = iterated.args[0] if len(iterated.args) == 1 else iterated.args[1]
            if isinstance(stop, ast.Call) and isinstance(stop.func, ast.Name) and stop.func.id == "len":
                self._add("info", node.lineno, "Index loop over `range(len(...))`",
                          "Looping over indices works, but `enumerate()` gives you the index and the item together and avoids indexing mistakes.",
                          "Do you need the index here, or only the items?")
            if (
                isinstance(stop, ast.BinOp)
                and isinstance(stop.op, ast.Add)
                and isinstance(stop.left, ast.Call)
                and isinstance(stop.left.func, ast.Name)
                and stop.left.func.id == "len"
            ):
                self._add("warning", node.lineno, "Possible off-by-one",
                          "`range(len(xs) + 1)` produces one index past the end, so `xs[i]` raises IndexError on the last pass.",
                          "What is the largest valid index of a list with `len(xs)` items?")
        if isinstance(iterated, ast.Name):
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and isinstance(child.func.value, ast.Name)
                    and child.func.value.id == iterated.id
                    and child.func.attr in _MUTATORS
                ):
                    self._add("warning", child.lineno, "Mutating a list while iterating over it",
                              f"Calling `{iterated.id}.{child.func.attr}()` inside `for ... in {iterated.id}` shifts the items under the loop, so elements get skipped or repeated.",
                              "What happens to the next item's position after you remove the current one?")

    def _check_while(self, node: ast.While) -> None:
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            if not any(isinstance(n, ast.Break | ast.Return | ast.Raise) for n in ast.walk(node)):
                self._add("warning", node.lineno, "Infinite loop",
                          "`while True:` has no `break`, `return` or `raise`, so nothing can ever end it.",
                          "Which condition should make this loop stop?")

    # -- functions -----------------------------------------------------------

    def _check_function(self, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._check_mutable_defaults(fn)
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and _is_self_call(n, fn.name)]
        if not calls:
            return
        params = [a.arg for a in fn.args.args if a.arg not in {"self", "cls"}]
        self._check_shrinking_input(fn, calls, params)
        self._check_base_case(fn)
        self._classify_recursion(fn, calls, params)

    def _check_mutable_defaults(self, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for default in [*fn.args.defaults, *(d for d in fn.args.kw_defaults if d is not None)]:
            mutable = isinstance(default, ast.List | ast.Dict | ast.Set) or (
                isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id in {"list", "dict", "set"}
            )
            if mutable:
                self._add("warning", default.lineno, "Mutable default argument",
                          "The default object is created once, when the function is defined, and then shared by every call.",
                          "What would a second call see if the first call appended to that default?")

    def _check_shrinking_input(self, fn: ast.FunctionDef | ast.AsyncFunctionDef, calls: list[ast.Call], params: list[str]) -> None:
        for call in calls:
            passed = [ast.unparse(arg) for arg in call.args]
            if params and passed and passed == params[: len(passed)]:
                self._add("error", call.lineno, "Recursive call does not shrink the input",
                          f"`{fn.name}({', '.join(passed)})` calls itself with the same arguments it received, so it recurses until the stack overflows.",
                          "How should the argument change so each call gets closer to the base case?")

    def _check_base_case(self, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Walk the body in order: an exit-capable guard before the first unconditional
        # self-call is a base case; reaching that call first means recursion never stops.
        for statement in fn.body:
            if isinstance(statement, ast.If | ast.Match | ast.Try | ast.While | ast.For) and _can_exit(statement):
                break
            if isinstance(statement, ast.Return | ast.Raise) and not _always_calls(statement, fn.name):
                break
            if _always_calls(statement, fn.name):
                self._add("error", fn.lineno, "Recursion without a reachable base case",
                          f"`{fn.name}` reaches its recursive call on every path; no branch returns first, so it never stops.",
                          "What should the function return for the smallest possible input?")
                break

    def _classify_recursion(self, fn: ast.FunctionDef | ast.AsyncFunctionDef, calls: list[ast.Call], params: list[str]) -> None:
        memoized = any("cache" in ast.unparse(d) for d in fn.decorator_list) or any(
            p in {"memo", "cache", "dp", "seen", "table"} for p in params
        )
        sites = {(call.lineno, call.col_offset) for call in calls}
        shrinks_by_subtraction = all(
            any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Sub) for n in ast.walk(arg))
            for call in calls for arg in call.args[:1]
        )
        halves = any(
            isinstance(n, ast.BinOp) and isinstance(n.op, ast.FloorDiv | ast.Div | ast.RShift) or isinstance(n, ast.Slice)
            for call in calls for n in ast.walk(call)
        )
        if len(sites) >= 2 and shrinks_by_subtraction and not memoized:
            self.recursion_shape = "exponential"
            self._add("warning", calls[0].lineno, "Repeated subproblems",
                      f"`{fn.name}` branches into {len(sites)} recursive calls on overlapping inputs without caching, so the same values are recomputed and the call count grows exponentially.",
                      f"How many times is the same small input computed when you call `{fn.name}` on a larger one?")
        elif self.recursion_shape != "exponential":
            if len(sites) >= 2:
                self.recursion_shape = "divide_and_conquer" if halves else "tree"
            else:
                self.recursion_shape = "logarithmic" if halves else "linear"

    def _check_compare(self, node: ast.Compare) -> None:
        for op, right in zip(node.ops, node.comparators, strict=True):
            if isinstance(op, ast.Eq | ast.NotEq) and isinstance(right, ast.Constant) and right.value is None:
                self._add("info", node.lineno, "Comparing to None with ==",
                          "`== None` can be overridden by a class's `__eq__`; `is None` checks identity and is the idiomatic test.",
                          "Why might `is None` be more reliable than `== None`?")
            if (
                isinstance(op, ast.Is | ast.IsNot)
                and isinstance(right, ast.Constant)
                and isinstance(right.value, int | float | str)
                and not isinstance(right.value, bool)
            ):
                self._add("warning", node.lineno, "Identity comparison with a literal",
                          "`is` compares object identity, not value, so it can fail for equal numbers or strings.",
                          "Which operator compares values rather than identity?")

    def _check_unreachable_block(self, block: list[ast.stmt]) -> None:
        for statement, following in zip(block, block[1:], strict=False):
            if isinstance(statement, ast.Return | ast.Raise | ast.Break | ast.Continue):
                self._add("info", following.lineno, "Unreachable code",
                          f"Line {following.lineno} comes right after a `{type(statement).__name__.lower()}`, so it can never run.",
                          "Was this line meant to run before the function exits?")
                return

    # -- complexity ----------------------------------------------------------

    def complexity(self) -> tuple[str, str, str]:
        depth = self.max_loop_depth
        loops = {0: "O(1)", 1: "O(n)", 2: "O(n^2)", 3: "O(n^3)"}.get(depth, f"O(n^{depth})")
        shapes = {
            "exponential": ("O(2^n)", "O(n) call stack", "Branching recursion on overlapping inputs, without caching."),
            "divide_and_conquer": ("O(n log n)", "O(n)", "Splits the input in half on each level, with linear work to combine."),
            "logarithmic": ("O(log n)", "O(log n) call stack", "Each recursive call halves the input."),
            "tree": ("O(n)", "O(h) call stack, h = depth", "Visits each node of the structure once."),
            "linear": ("O(n)", "O(n) call stack", "One recursive call per level, n levels deep."),
        }
        if self.recursion_shape in shapes:
            time, space, rationale = shapes[self.recursion_shape]
            if depth:
                rationale += f" It also contains loops nested {depth} deep, which multiply the work per call."
            return time, space, rationale
        space = "O(n)" if self.grows_collection_in_loop else "O(1) extra"
        rationale = f"Deepest loop nesting is {depth}." if depth else "No loops or recursion: straight-line code."
        return loops, space, rationale


def _analyze_python(code: str) -> CodeAnalysis:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        line = exc.lineno
        message = exc.msg[0].upper() + exc.msg[1:] if exc.msg else "Invalid syntax"
        finding = CodeFinding(
            severity="error",
            line=line,
            title="Syntax error",
            detail=f"Python stops parsing at line {line}: {message}.",
            question=f"What does Python expect to see at that point on line {line}?",
        )
        return CodeAnalysis("python", code, (finding,), "unknown", "unknown", "The code must parse before its complexity can be estimated.")
    analyzer = _PythonAnalyzer(tree)
    analyzer.run()
    time, space, rationale = analyzer.complexity()
    findings = tuple(sorted(analyzer.findings, key=lambda f: (_SEVERITY_ORDER[f.severity], f.line or 0)))
    return CodeAnalysis("python", code, findings, time, space, rationale)


def _blank_strings_and_comments(code: str) -> str:
    """Replaces string literals and comments with spaces so bracket counting ignores them."""
    pattern = r"(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|//[^\n]*|/\*.*?\*/)"
    return re.sub(pattern, lambda m: re.sub(r"[^\n]", " ", m.group(0)), code, flags=re.DOTALL)


_CLOSERS = {")": "(", "]": "[", "}": "{"}


def _scan_brackets_and_loops(lines: list[str]) -> tuple[CodeFinding | None, int]:
    """Matches brackets and tracks how many `{` blocks opened by for/while loops are nested."""
    stack: list[tuple[str, int, bool]] = []  # (bracket, line, opened_a_loop_body)
    loop_depth = max_loop_depth = 0
    pending_loop = False
    for line_no, line in enumerate(lines, 1):
        pending_loop = pending_loop or bool(re.search(r"\b(for|while)\s*\(", line))
        for char in line:
            if char in "([{":
                opens_loop = char == "{" and pending_loop
                pending_loop = pending_loop and char != "{"
                stack.append((char, line_no, opens_loop))
                loop_depth += opens_loop
                max_loop_depth = max(max_loop_depth, loop_depth)
            elif char in _CLOSERS:
                if not stack or stack[-1][0] != _CLOSERS[char]:
                    return CodeFinding("error", line_no, "Unbalanced brackets",
                                       f"Line {line_no} closes `{char}` without a matching opener.",
                                       "Which bracket was this meant to close?"), max_loop_depth
                loop_depth -= stack.pop()[2]
    if stack:
        char, line_no, _ = stack[-1]
        return CodeFinding("error", line_no, "Unbalanced brackets",
                           f"The `{char}` opened on line {line_no} is never closed.",
                           "Where should this block end?"), max_loop_depth
    return None, max_loop_depth


def _analyze_c_family(code: str, language: str) -> CodeAnalysis:
    lines = _blank_strings_and_comments(code).splitlines()
    bracket_issue, max_loop_depth = _scan_brackets_and_loops(lines)
    findings: list[CodeFinding] = [bracket_issue] if bracket_issue else []

    for line_no, line in enumerate(lines, 1):
        if re.search(r"\bif\s*\(\s*[\w.\[\]]+\s*=\s*[^=]", line):
            findings.append(CodeFinding("warning", line_no, "Assignment inside a condition",
                                        "`=` assigns instead of comparing, so the condition tests the assigned value.",
                                        "Did you mean to compare the two values?"))
        if re.search(r"\bfor\s*\(.*<=\s*[\w.]+\.(length|size\(\))", line):
            findings.append(CodeFinding("warning", line_no, "Possible off-by-one",
                                        "Looping while `i <= length` visits one index past the last element.",
                                        "What is the last valid index of an array of that length?"))
        if language in {"javascript", "typescript"} and re.search(r"[^=!<>]==[^=]", line):
            findings.append(CodeFinding("info", line_no, "Loose equality",
                                        "`==` coerces types before comparing (`'0' == 0` is true).",
                                        "Would `===` express what you mean more precisely?"))

    time = {0: "O(1)", 1: "O(n)", 2: "O(n^2)"}.get(max_loop_depth, f"O(n^{max_loop_depth})")
    ordered = tuple(sorted(findings, key=lambda f: (_SEVERITY_ORDER[f.severity], f.line or 0)))
    rationale = f"Deepest loop nesting is {max_loop_depth}." if max_loop_depth else "No loops detected."
    return CodeAnalysis(language, code, ordered, time, "O(1) extra", rationale)


def analyze_code(message: str) -> CodeAnalysis:
    code, hint = extract_code(message)
    language = detect_language(code, hint)
    if language == "python":
        return _analyze_python(code)
    return _analyze_c_family(code, language)


def numbered(code: str) -> str:
    return "\n".join(f"{i:>3} | {line}" for i, line in enumerate(code.splitlines(), 1))


class CodeDiagnosticAgent(SpecialistAgent):
    name = "code_diagnostic"

    def role_prompt(self, ctx: AgentContext) -> str:
        return CODE_DIAGNOSTIC

    def extra_context(self, ctx: AgentContext) -> str:
        analysis = ctx.analysis
        if analysis is None:
            return ""
        findings = "\n".join(
            f"- [{f.severity}] line {f.line or '?'}: {f.title}: {f.detail}" for f in analysis.findings
        ) or "- none"
        return (
            f"Static analysis ({analysis.language}):\n{findings}\n"
            f"Estimated complexity: time {analysis.time_complexity}, space {analysis.space_complexity}. "
            f"{analysis.complexity_rationale}\n\nLearner's code with line numbers:\n{numbered(analysis.code)}"
        )

    def offline(self, ctx: AgentContext) -> AgentDraft:
        analysis = ctx.analysis or analyze_code(ctx.request.message)
        language = analysis.language if analysis.language != "unknown" else "code"
        if analysis.time_complexity != "unknown":
            complexity = (
                f"**Complexity:** time {analysis.time_complexity}, space {analysis.space_complexity}. "
                f"{analysis.complexity_rationale}"
            )
        else:
            complexity = f"**Complexity:** {analysis.complexity_rationale}"
        if ctx.is_voice:
            if not analysis.findings:
                return AgentDraft(
                    text=(
                        f"Your {language} parses cleanly and I don't see a classic bug. Its time complexity looks like "
                        f"{analysis.time_complexity}. What does it return for the smallest input?"
                    )
                )
            top = analysis.findings[0]
            where = f"on line {top.line}" if top.line else "in your code"
            return AgentDraft(text=f"I spotted something {where}: {top.title.lower()}. {top.detail} {top.question}")
        if not analysis.findings:
            return AgentDraft(
                text=(
                    f"I read your {language} and ran a static analysis pass: no syntax errors or classic logic traps.\n\n"
                    f"{complexity}\n\nLet's test it mentally. "
                    "**What does it return for the smallest possible input, and for an empty one?**"
                )
            )
        items = []
        for index, finding in enumerate(analysis.findings[:5], 1):
            where = f"Line {finding.line}" if finding.line else "Overall"
            items.append(f"{index}. **{where}: {finding.title}.** {finding.detail} *{finding.question}*")
        lead = analysis.findings[0]
        return AgentDraft(
            text=(
                f"I read your {language} and ran a static analysis pass. Here's what stands out:\n\n"
                + "\n".join(items)
                + f"\n\n{complexity}\n\n**Start with the first one: {lead.question}**"
            )
        )
