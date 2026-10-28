import uuid

import pytest
from httpx import AsyncClient

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.user import UserRole
from app.repositories.user_repository import user_repository


@pytest.mark.asyncio
async def test_google_signup_new_student(async_client: AsyncClient):
    """Google sign up creates a new verified student account and returns token pair."""
    unique_email = f"google_student_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "credential": f"dev-google:{unique_email}:Alex Turner",
        "role": "student",
        "preferred_modality": "visual",
    }

    res = await async_client.post("/api/v1/auth/google", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_email.lower()
    assert data["user"]["full_name"] == "Alex Turner"
    assert data["user"]["role"] == "student"
    assert data["user"]["is_verified"] is True


@pytest.mark.asyncio
async def test_google_signup_new_teacher(async_client: AsyncClient):
    """Google sign up can register a teacher account."""
    unique_email = f"google_prof_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "credential": f"dev-google:{unique_email}:Prof. Minerva",
        "role": "teacher",
    }

    res = await async_client.post("/api/v1/auth/google", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["user"]["role"] == "teacher"
    assert data["user"]["is_verified"] is True


@pytest.mark.asyncio
async def test_google_login_existing_unverified_user(async_client: AsyncClient):
    """Signing in with Google marks an existing unverified account as verified."""
    unique_email = f"unverified_signup_{uuid.uuid4().hex[:6]}@example.com"

    # Create unverified user directly in DB
    async with async_session_factory() as session:
        await user_repository.create(
            session,
            email=unique_email,
            password_hash=get_password_hash("InitialPassword123!"),
            full_name="Pending Verification",
            role=UserRole.STUDENT,
            is_verified=False,
        )

    # Google login for that same email
    payload = {
        "credential": f"dev-google:{unique_email}:Pending Verification",
        "role": "student",
    }

    res = await async_client.post("/api/v1/auth/google", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["user"]["email"] == unique_email.lower()
    assert data["user"]["is_verified"] is True
