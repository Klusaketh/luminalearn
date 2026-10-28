from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.content import router as content_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.quiz import router as quiz_router
from app.api.v1.tutor import router as tutor_router
from app.api.v1.voice import router as voice_router
from app.core.port_guard import INSTANCE_ID

api_router = APIRouter()

# Register API Sub-Routers
api_router.include_router(auth_router)
api_router.include_router(onboarding_router)
api_router.include_router(content_router)
api_router.include_router(quiz_router)
api_router.include_router(tutor_router)
api_router.include_router(voice_router)


@api_router.get("/health", status_code=200)
async def health_check() -> dict[str, Any]:
    """
    Core Health & Readiness Check Endpoint.
    Returns status 200 with system metadata.
    """
    return {
        "status": "healthy",
        "service": "LuminaLearn AI Backend API",
        "version": "1.0.0",
        "instance": INSTANCE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
