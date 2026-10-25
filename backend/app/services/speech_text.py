"""
Converts tutor markdown (with KaTeX math and code) into text that sounds natural when spoken.
"""
import re

_LATEX_WORDS: tuple[tuple[str, str], ...] = (
    (r"\\int_\{?([^}\s^]+)\}?\^\{?([^}\s]+)\}?", r" the integral from \1 to \2 of "),
    (r"\\int", " the integral of "),
    (r"\\sum", " the sum of "),
    (r"\\frac\{([^}]*)\}\{([^}]*)\}", r" \1 over \2 "),
    (r"\\sqrt\{([^}]*)\}", r" the square root of \1 "),
    (r"\\det", " the determinant of "),
    (r"\\lim", " the limit of "),
    (r"\\cdot|\\times", " times "),
    (r"\\leq?", " less than or equal to "),
    (r"\\geq?", " greater than or equal to "),
    (r"\\neq", " not equal to "),
    (r"\\to|\\rightarrow", " goes to "),
    (r"\\leftarrow", " becomes "),
    (r"\\infty", " infinity "),
    (r"\\mid", " given "),
    (r"\\neg\s*", " not "),
    (r"\\(alpha|beta|gamma|delta|epsilon|eta|theta|lambda|mu|pi|sigma|phi|omega)", r" \1 "),
    (r"\\nabla", " the gradient of "),
    (r"\\approx", " approximately "),
    (r"\\(text|mathbf|mathrm|operatorname)\{([^}]*)\}", r" \2 "),
    (r"\^\{?2\}?", " squared "),
    (r"\^\{?3\}?", " cubed "),
    (r"\^\{([^}]*)\}|\^(\w)", r" to the power \1\2 "),
    (r"_\{([^}]*)\}|_(\w)", r" sub \1\2 "),
    (r"\\[,;!]|\\quad|\\left|\\right|\\begin\{\w+\}|\\end\{\w+\}|&|\\\\", " "),
)


def latex_to_words(expression: str) -> str:
    spoken = expression
    for pattern, replacement in _LATEX_WORDS:
        spoken = re.sub(pattern, replacement, spoken)
    spoken = re.sub(r"(?<=\w)\s*=\s*(?=[\w-])", " equals ", spoken)
    spoken = re.sub(r"\s\+\s|(?<=\w)\+(?=\w)", " plus ", spoken)
    spoken = re.sub(r"\s-\s", " minus ", spoken)
    spoken = re.sub(r"[{}\\]", " ", spoken)
    return re.sub(r"\s+", " ", spoken).strip()


def speech_text(markdown: str) -> str:
    """Strips markdown, citations and code for speech synthesis, and reads math aloud."""
    text = re.sub(r"```.*?(```|$)", " I've put a code example on your screen. ", markdown, flags=re.DOTALL)
    text = re.sub(r"\$\$?([^$]+?)\$\$?", lambda m: f" {latex_to_words(m.group(1))} ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[(\d+)\]", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s*(#+|[-*•]|\d+[.)])\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_#>|~]", "", text)
    return re.sub(r"\s+", " ", text).strip()
