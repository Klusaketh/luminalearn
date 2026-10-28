import asyncio
import os
import sys
import uuid
from collections.abc import AsyncGenerator

# Ensure repository root is in sys.path for test execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Hermetic AI: every Gemini-backed feature runs on its deterministic engine during tests,
# even when .env holds a real API key. Must be set before the settings singleton loads.
os.environ["LLM_OFFLINE_MODE"] = "true"

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import create_access_token
from app.main import app
from app.models.user import User, UserRole, VARKModality
from app.services.email_service import MockEmailProvider, email_service


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    await init_db()


@pytest.fixture(autouse=True)
def mock_email():
    provider = MockEmailProvider()
    email_service.set_provider(provider)
    yield provider
    provider.clear()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def create_verified_learner(**overrides) -> User:
    """Persist an active, email-verified student (the minimum the workspace accepts)."""
    fields = {
        "id": uuid.uuid4(),
        "email": f"learner_{uuid.uuid4().hex[:10]}@luminalearn.ai",
        "password_hash": "argon2id_mock_hash",
        "full_name": "Test Learner",
        "role": UserRole.STUDENT,
        "preferred_modality": VARKModality.READ_WRITE,
        "is_active": True,
        "is_verified": True,
    }
    fields.update(overrides)
    async with AsyncSessionLocal() as session:
        user = User(**fields)
        session.add(user)
        await session.commit()
        return user


@pytest_asyncio.fixture
async def auth_headers() -> dict[str, str]:
    """Bearer headers for a fresh verified learner."""
    user = await create_verified_learner()
    return {"Authorization": f"Bearer {create_access_token(subject=str(user.id))}"}


@pytest_asyncio.fixture
async def authed_client(auth_headers: dict[str, str]) -> AsyncGenerator[AsyncClient, None]:
    """An HTTP client signed in as a verified learner."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=auth_headers) as client:
        yield client
