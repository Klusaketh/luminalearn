from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.content import router as content_router
from app.api.v1.onboarding import router as onboarding_router

api_router = APIRouter()

# Register API Sub-Routers
api_router.include_router(auth_router)
api_router.include_router(onboarding_router)
api_router.include_router(content_router)



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
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
