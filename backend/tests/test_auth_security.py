import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.user import UserRole
from app.repositories.user_repository import user_repository


@pytest.mark.asyncio
async def test_mock_token_rejected_in_production(async_client: AsyncClient):
    """Ensure dev-google mock tokens are strictly rejected in production environment."""
    original_env = settings.ENVIRONMENT
    original_debug = settings.DEBUG
    try:
        settings.ENVIRONMENT = "production"
        settings.DEBUG = False

        payload = {
            "credential": "dev-google:hacker@example.com:Hacker",
            "role": "student",
        }
        res = await async_client.post("/api/v1/auth/google", json=payload)
        assert res.status_code == 401
        assert "Development mock tokens are strictly forbidden" in res.json()["detail"]
    finally:
        settings.ENVIRONMENT = original_env
        settings.DEBUG = original_debug


@pytest.mark.asyncio
async def test_invalid_real_google_token_rejected(async_client: AsyncClient):
    """Ensure invalid/forged real Google ID tokens fail closed."""
    original_client_id = settings.GOOGLE_CLIENT_ID
    try:
        settings.GOOGLE_CLIENT_ID = "mock-client-id-12345.apps.googleusercontent.com"
        payload = {
            "credential": "forged.jwt.token.string",
            "role": "student",
        }
        res = await async_client.post("/api/v1/auth/google", json=payload)
        assert res.status_code == 401
        assert "Google" in res.json()["detail"] or "Invalid" in res.json()["detail"]
    finally:
        settings.GOOGLE_CLIENT_ID = original_client_id


@pytest.mark.asyncio
async def test_google_token_unverified_email_rejected(async_client: AsyncClient):
    """Ensure Google token with email_verified=False is rejected."""
    original_client_id = settings.GOOGLE_CLIENT_ID
    try:
        settings.GOOGLE_CLIENT_ID = "mock-client-id-12345.apps.googleusercontent.com"

        mock_payload = {
            "iss": "accounts.google.com",
            "aud": settings.GOOGLE_CLIENT_ID,
            "email": "unverified.google@example.com",
            "email_verified": False,
            "name": "Unverified User",
        }

        with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_payload):
            payload = {
                "credential": "valid_looking_token_payload",
                "role": "student",
            }
            res = await async_client.post("/api/v1/auth/google", json=payload)
            assert res.status_code == 400
            assert "not verified by Google" in res.json()["detail"]
    finally:
        settings.GOOGLE_CLIENT_ID = original_client_id


@pytest.mark.asyncio
async def test_google_only_account_password_login_blocked(async_client: AsyncClient):
    """
    Ensure an account created via Google Sign-In gives clear guidance
    if someone attempts password login.
    """
    unique_email = f"google_only_{uuid.uuid4().hex[:6]}@example.com"

    # Register via Google
    payload = {
        "credential": f"dev-google:{unique_email}:Google Learner",
        "role": "student",
    }
    signup_res = await async_client.post("/api/v1/auth/google", json=payload)
    assert signup_res.status_code == 200

    # Attempt to log in with arbitrary password
    login_payload = {
        "email": unique_email,
        "password": "GuessedPassword123!",
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 400
    assert "This account was created via Google Sign-In" in login_res.json()["detail"]


@pytest.mark.asyncio
async def test_google_login_preserves_existing_user_uuid_and_role(async_client: AsyncClient):
    """
    Ensure that when an existing user with role TEACHER signs in with Google,
    the existing UUID and role are preserved, and client-supplied role is ignored.
    """
    unique_email = f"teacher_preserve_{uuid.uuid4().hex[:6]}@example.com"

    async with async_session_factory() as session:
        original_user = await user_repository.create(
            session,
            email=unique_email,
            password_hash=get_password_hash("Password123!"),
            full_name="Prof. Harrison",
            role=UserRole.TEACHER,
            is_verified=False,
        )
        original_id = original_user.id

    # Google login with payload requesting 'student' role
    payload = {
        "credential": f"dev-google:{unique_email}:Prof. Harrison",
        "role": "student",
    }
    res = await async_client.post("/api/v1/auth/google", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["user"]["id"] == str(original_id)
    assert data["user"]["role"] == "teacher"  # Role was NOT overwritten by payload
    assert data["user"]["is_verified"] is True  # Verified by Google login


@pytest.mark.asyncio
async def test_cookie_secure_flag_in_production(async_client: AsyncClient):
    """Ensure access_token cookie has Secure flag when ENVIRONMENT is production."""
    original_env = settings.ENVIRONMENT
    try:
        settings.ENVIRONMENT = "production"

        unique_email = f"secure_cookie_{uuid.uuid4().hex[:6]}@example.com"
        async with async_session_factory() as session:
            await user_repository.create(
                session,
                email=unique_email,
                password_hash=get_password_hash("Password123!"),
                full_name="Secure Cookie User",
                role=UserRole.STUDENT,
                is_verified=True,
            )

        res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "Password123!"}
        )
        assert res.status_code == 200

        # Check Set-Cookie header contains secure and samesite=lax
        cookie_header = res.headers.get("set-cookie", "")
        assert "secure" in cookie_header.lower()
        assert "samesite=lax" in cookie_header.lower()
        assert "httponly" in cookie_header.lower()
    finally:
        settings.ENVIRONMENT = original_env
