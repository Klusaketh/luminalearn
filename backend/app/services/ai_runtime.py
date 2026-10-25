"""
LuminaLearn AI — AI Runtime Composition Root.
Module: backend/app/services/ai_runtime.py

Builds the process-wide Gemini gateway and the multi-agent Socratic faculty from settings,
so every endpoint (tutor chat, voice, quiz generation) shares one circuit breaker.
"""

from ai.agents import SocraticOrchestrator
from ai.llm import GatewayConfig, GeminiGateway
from ai.rag.curriculum_rag import curriculum_rag
from app.core.config import settings
from app.core.rate_limit import SlidingWindowRateLimiter

gemini_gateway = GeminiGateway(
    GatewayConfig(
        api_key=settings.GEMINI_API_KEY,
        text_models=tuple(dict.fromkeys([settings.GEMINI_MODEL_FLASH, *settings.GEMINI_FALLBACK_MODELS])),
        tts_models=tuple(settings.GEMINI_TTS_MODELS),
        tts_voice=settings.GEMINI_TTS_VOICE,
        temperature=settings.TUTOR_TEMPERATURE,
        max_output_tokens=settings.GEMINI_MAX_TOKENS,
        request_timeout_s=settings.GEMINI_REQUEST_TIMEOUT_SECONDS,
        offline=settings.LLM_OFFLINE_MODE,
    )
)

tutor_orchestrator = SocraticOrchestrator(
    gateway=gemini_gateway,
    rag=curriculum_rag,
    temperature=settings.TUTOR_TEMPERATURE,
)

tutor_rate_limiter = SlidingWindowRateLimiter(window_s=settings.TUTOR_RATE_LIMIT_WINDOW_SECONDS)
