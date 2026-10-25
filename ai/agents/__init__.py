"""AI Agents Package: the multi-agent Socratic tutoring faculty."""
from ai.agents.code_diagnostic import analyze_code
from ai.agents.orchestrator import SocraticOrchestrator
from ai.agents.schema import (
    AGENT_NAMES,
    AGENT_PROFILES,
    MODALITIES,
    AgentName,
    DialogueTurn,
    Modality,
    RoutingDecision,
    TutorEvent,
    TutorRequest,
)
from ai.agents.supervisor import SupervisorAgent

__all__ = [
    "AGENT_NAMES",
    "AGENT_PROFILES",
    "MODALITIES",
    "AgentName",
    "DialogueTurn",
    "Modality",
    "RoutingDecision",
    "SocraticOrchestrator",
    "SupervisorAgent",
    "TutorEvent",
    "TutorRequest",
    "analyze_code",
]
