import json
import time
import uuid

import pytest
from httpx import AsyncClient

from app.core.redis import redis_client
from app.core.security import generate_secure_otp, hash_otp, verify_otp_hash
from app.services.email_service import MockEmailProvider


@pytest.mark.asyncio
async def test_otp_generation():
    """Verify exactly 6-digit cryptographically secure numeric format."""
    otps = [generate_secure_otp() for _ in range(50)]
    for code in otps:
        assert len(code) == 6
        assert code.isdigit()
    # Ensure randomness / variance
    assert len(set(otps)) > 40


@pytest.mark.asyncio
async def test_otp_keyed_hmac_hashing():
    """Verify OTP is hashed using keyed HMAC and not plain SHA256 or plaintext."""
    email = "security.test@example.com"
    otp = "123456"
    digest = hash_otp(email, otp)

    assert digest != otp
    assert len(digest) == 64  # SHA256 hex digest length
    # Constant-time verification
    assert verify_otp_hash(email, otp, digest) is True
    assert verify_otp_hash(email, "654321", digest) is False
    assert verify_otp_hash("other@example.com", otp, digest) is False


@pytest.mark.asyncio
async def test_registration_creates_unverified_user(
    async_client: AsyncClient,
    mock_email: MockEmailProvider
):
    """Registration must create an unverified account and not issue tokens."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Unverified Student",
        "preferred_modality": "visual"
    }

    res = await async_client.post("/api/v1/auth/register/student", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["email"] == email.lower()
    assert data["is_verified"] is False
    assert "access_token" not in data
    assert "refresh_token" not in data

    # Verify email was dispatched
    assert len(mock_email.sent_emails) == 1
    assert mock_email.sent_emails[0]["to_email"] == email.lower()


@pytest.mark.asyncio
async def test_otp_not_stored_plaintext(
    async_client: AsyncClient,
    mock_email: MockEmailProvider
):
    """Verify that stored OTP in Redis is a keyed HMAC and never plaintext."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "HMAC Student",
        "preferred_modality": "visual"
    }

    await async_client.post("/api/v1/auth/register/student", json=payload)
    sent_otp = mock_email.sent_emails[-1]["subject"].split()[0]

    raw_state = await redis_client.get(f"otp:{email.lower()}")
    assert raw_state is not None
    assert sent_otp not in raw_state, "Plaintext OTP found in storage!"

    state = json.loads(raw_state)
    assert "otp_hash" in state
    assert state["attempts"] == 0


@pytest.mark.asyncio
async def test_unverified_login_denied(async_client: AsyncClient):
    """Unverified users must be rejected with machine-readable error EMAIL_VERIFICATION_REQUIRED."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    password = "Password123!"
    payload = {
        "email": email,
        "password": password,
        "full_name": "Blocked Login Student",
        "preferred_modality": "visual"
    }

    await async_client.post("/api/v1/auth/register/student", json=payload)

    # Attempt login with unverified account
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_res.status_code == 403
    assert login_res.json()["detail"] == "EMAIL_VERIFICATION_REQUIRED"
    assert "access_token" not in login_res.json()


@pytest.mark.asyncio
async def test_wrong_otp_and_attempt_limit(
    async_client: AsyncClient,
    mock_email: MockEmailProvider
):
    """Test wrong OTP decrements attempts and 5th failed attempt locks verification."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Attempts Student",
        "preferred_modality": "visual"
    }

    await async_client.post("/api/v1/auth/register/student", json=payload)
    real_otp = mock_email.sent_emails[-1]["subject"].split()[0]
    wrong_otp = "000000" if real_otp != "000000" else "111111"

    # Attempt 1 to 4: returns 400 with remaining attempts count
    for i in range(1, 5):
        res = await async_client.post(
            "/api/v1/auth/verify-email",
            json={"email": email, "otp": wrong_otp}
        )
        assert res.status_code == 400
        assert f"{5 - i} attempt" in res.json()["detail"]

    # Attempt 5: triggers maximum attempts reached
    res5 = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": wrong_otp}
    )
    assert res5.status_code == 400
    assert "Maximum verification attempts exceeded" in res5.json()["detail"]

    # Even the correct OTP is now rejected because max attempts was reached
    res_real = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": real_otp}
    )
    assert res_real.status_code == 400
    assert "Maximum verification attempts exceeded" in res_real.json()["detail"]


@pytest.mark.asyncio
async def test_otp_expiry(
    async_client: AsyncClient,
    mock_email: MockEmailProvider
):
    """OTP older than 10 minutes (600s) must be rejected as expired."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Expiry Student",
        "preferred_modality": "visual"
    }

    await async_client.post("/api/v1/auth/register/student", json=payload)
    real_otp = mock_email.sent_emails[-1]["subject"].split()[0]

    # Tamper created_at in Redis to simulate 601 seconds ago
    key = f"otp:{email.lower()}"
    raw = await redis_client.get(key)
    assert raw is not None
    data = json.loads(raw)
    data["created_at"] = time.time() - 601
    await redis_client.setex(key, 600, json.dumps(data))

    # Verify attempt with expired state
    res = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": real_otp}
    )
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_resend_cooldown_and_old_otp_invalidation(
    async_client: AsyncClient,
    mock_email: MockEmailProvider
):
    """Test 60s resend cooldown, and that generating a new OTP invalidates the old one."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Cooldown Student",
        "preferred_modality": "visual"
    }

    await async_client.post("/api/v1/auth/register/student", json=payload)
    old_otp = mock_email.sent_emails[-1]["subject"].split()[0]

    # Immediate resend attempt (< 60s) must return 429
    res_cooldown = await async_client.post(
        "/api/v1/auth/verify-email/resend",
        json={"email": email}
    )
    assert res_cooldown.status_code == 429
    assert "Please wait" in res_cooldown.json()["detail"]

    # Simulate 61 seconds passed for last_sent_at
    key = f"otp:{email.lower()}"
    raw = await redis_client.get(key)
    assert raw is not None
    data = json.loads(raw)
    data["last_sent_at"] = time.time() - 61
    await redis_client.setex(key, 600, json.dumps(data))

    # Now resend succeeds
    res_resend = await async_client.post(
        "/api/v1/auth/verify-email/resend",
        json={"email": email}
    )
    assert res_resend.status_code == 200

    new_otp = mock_email.sent_emails[-1]["subject"].split()[0]
    assert new_otp != old_otp

    # Old OTP is now INVALID
    res_old = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": old_otp}
    )
    assert res_old.status_code == 400
    assert "remaining" in res_old.json()["detail"]

    # New OTP is VALID
    res_new = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": new_otp}
    )
    assert res_new.status_code == 200
    assert "verified successfully" in res_new.json()["message"]


@pytest.mark.asyncio
async def test_successful_verification_invalidates_all_state_and_allows_login(
    async_client: AsyncClient,
    mock_email: MockEmailProvider
):
    """Successful verification sets is_verified=True, deletes OTP from Redis, and allows login."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    password = "Password123!"
    payload = {
        "email": email,
        "password": password,
        "full_name": "Verified Student",
        "preferred_modality": "visual"
    }

    await async_client.post("/api/v1/auth/register/student", json=payload)
    otp = mock_email.sent_emails[-1]["subject"].split()[0]

    # Verify email
    res_verify = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": otp}
    )
    assert res_verify.status_code == 200

    # Ensure Redis OTP state is completely erased
    raw_state = await redis_client.get(f"otp:{email.lower()}")
    assert raw_state is None

    # Verified login succeeds and returns JWT tokens
    res_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert "access_token" in login_data
    assert login_data["user"]["is_verified"] is True

    # Protected route allows verified user
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}
    res_me = await async_client.post if False else await async_client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_protected_route_enforcement_rejects_unverified_token(
    async_client: AsyncClient
):
    """If an unverified user token somehow reached a protected route, it must be rejected with 403."""
    from app.core.database import async_session_factory
    from app.core.security import create_access_token, get_password_hash
    from app.repositories.user_repository import user_repository

    # Create unverified user directly in DB
    email = f"unverified_token_{uuid.uuid4().hex[:6]}@example.com"
    async with async_session_factory() as session:
        user = await user_repository.create(
            session,
            email=email,
            password_hash=get_password_hash("Password123!"),
            full_name="Direct Unverified",
            is_verified=False
        )
        user_id = str(user.id)

    # Forged or legacy token for unverified user
    token = create_access_token(subject=user_id, role="student")
    headers = {"Authorization": f"Bearer {token}"}

    res_me = await async_client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 403
    assert res_me.json()["detail"] == "EMAIL_VERIFICATION_REQUIRED"


@pytest.mark.asyncio
async def test_otp_absent_from_api_responses(
    async_client: AsyncClient,
    mock_email: MockEmailProvider
):
    """Ensure OTP is never exposed in API responses (register, login, resend, verify)."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "No Leak Student",
        "preferred_modality": "visual"
    }

    # Register response
    res_reg = await async_client.post("/api/v1/auth/register/student", json=payload)
    reg_text = res_reg.text
    otp = mock_email.sent_emails[-1]["subject"].split()[0]
    assert otp not in reg_text, "OTP leaked in registration response!"

    # Resend response
    # Advance cooldown
    key = f"otp:{email.lower()}"
    raw = await redis_client.get(key)
    assert raw is not None
    data = json.loads(raw)
    data["last_sent_at"] = time.time() - 65
    await redis_client.setex(key, 600, json.dumps(data))

    res_resend = await async_client.post(
        "/api/v1/auth/verify-email/resend",
        json={"email": email}
    )
    new_otp = mock_email.sent_emails[-1]["subject"].split()[0]
    assert new_otp not in res_resend.text, "OTP leaked in resend response!"

    # Verify response
    res_verify = await async_client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": new_otp}
    )
    assert new_otp not in res_verify.text, "OTP leaked in verify response!"
