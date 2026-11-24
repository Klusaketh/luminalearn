import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field

Difficulty = Literal["Easy", "Medium", "Hard"]
PracticeLanguage = Literal["python", "javascript"]


class PracticeTestCase(BaseModel):
    args: list[Any]
    expected: Any


class RelatedTopic(BaseModel):
    """The curriculum lesson a problem practises, when it exists in the database."""
    id: uuid.UUID
    title: str


class PracticeProblemSummary(BaseModel):
    slug: str
    title: str
    difficulty: Difficulty
    tags: list[str]
    order: int
    solved: bool = False
    attempts: int = 0
    languages: list[PracticeLanguage] = Field(default_factory=lambda: list[PracticeLanguage](["python"]))


class PracticeProblemDetail(PracticeProblemSummary):
    """Everything the browser needs to run the problem. The reference solution is never included."""
    statement: str
    starter_code: str
    function_name: str
    compare: Literal["exact", "unordered"]
    hints: list[str]
    tests: list[PracticeTestCase]
    harness: str = Field(..., description="Python source of the judging harness, run in the browser with Pyodide")
    starters: dict[PracticeLanguage, str] = Field(default_factory=dict, description="Starter code per language")
    function_names: dict[PracticeLanguage, str] = Field(default_factory=dict, description="Function the tests call, per language")
    harnesses: dict[PracticeLanguage, str] = Field(default_factory=dict, description="Judging harness source per language")
    related_topic: RelatedTopic | None = None
    best_passed: int = 0


class PracticeProblemList(BaseModel):
    problems: list[PracticeProblemSummary]
    solved_count: int
    total_count: int


class PracticeSubmissionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=20_000)
    language: PracticeLanguage = "python"
    passed: int = Field(..., ge=0)
    total: int = Field(..., ge=1)


class PracticeSubmissionResponse(BaseModel):
    solved: bool
    attempts: int
    best_passed: int
    total: int
