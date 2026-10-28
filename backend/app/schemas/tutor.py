from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.user import VARKModality

TutorAgentName = Literal["socratic_tutor", "concept_explainer", "analogy_specialist", "code_diagnostic"]


class TutorHistoryTurn(BaseModel):
    """One prior turn of the dialogue, replayed for conversational context."""
    role: Literal["student", "tutor"]
    text: str = Field(..., max_length=6000)


class TutorChatRequest(BaseModel):
    """A learner turn for the multi-agent Socratic faculty."""
    message: str = Field(..., min_length=1, max_length=8000)
    topic: str | None = Field(default=None, max_length=150, description="Topic in focus, used for grounding and BKT lookup")
    modality: VARKModality | None = Field(default=None, description="VARK override; defaults to the learner's profile")
    hint_level: int = Field(default=0, ge=0, le=3, description="Extra hints requested in this thread")
    agent: TutorAgentName | None = Field(default=None, description="Explicitly request one specialist")
    history: list[TutorHistoryTurn] = Field(default_factory=list, max_length=24)


class TutorSpeakRequest(BaseModel):
    """Text to synthesize with the server voice."""
    text: str = Field(..., min_length=1, max_length=1500)


class AgentProfileResponse(BaseModel):
    name: TutorAgentName
    display_name: str
    summary: str


class TutorStatusResponse(BaseModel):
    """Capabilities the tutor workspace adapts to (live model vs. offline engines, voice paths)."""
    llm_enabled: bool
    speech_enabled: bool
    prompt_version: str
    gateway: dict[str, Any]
    agents: list[AgentProfileResponse]
    voice_websocket_path: str
