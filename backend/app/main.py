import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.port_guard import serving_port, warn_if_port_shadowed


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager to handle startup and shutdown events."""
    await init_db()
    # Under pytest there is no listening socket to check.
    shadow_check = None if "pytest" in sys.modules else asyncio.create_task(warn_if_port_shadowed(serving_port()))
    yield
    if shadow_check is not None:
        shadow_check.cancel()


def create_application() -> FastAPI:
    """
    FastAPI Application Factory.
    Configures CORS, middleware stack, routes, and OpenAPI metadata.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-Powered Adaptive Learning Platform API Baseline",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS Middleware
    origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS] if settings.BACKEND_CORS_ORIGINS else []
    if "http://localhost:3000" not in origins:
        origins.append("http://localhost:3000")
    if "http://127.0.0.1:3000" not in origins:
        origins.append("http://127.0.0.1:3000")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Master API V1 Router
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()

