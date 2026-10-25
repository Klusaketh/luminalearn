"""
Monorepo import bootstrap.

The backend imports the shared `ai/` (agents, RAG, LLM gateway) and `ml/` (BKT, IRT,
retention forecasting) packages that live beside it at the repository root.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def ensure_monorepo_on_path() -> None:
    """Make the repository root importable so `ai.*` and `ml.*` resolve from any working directory."""
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
