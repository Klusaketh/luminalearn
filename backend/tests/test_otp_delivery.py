"""
OTP delivery is reported honestly: every endpoint that sends a code says whether it went out by
email, was printed to the console (development without SMTP), or failed, and production refuses
to pretend. Also covers the emailed password-reset code and the SMTP provider itself.
"""

import json
import logging
import smtplib
import time
import uuid
from typing import Any, ClassVar, Self

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.redis import redis_client
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.services import email_service as email_module
from app.services.email_service import MockEmailProvider, SMTPEmailProvider
from tests.conftest import create_verified_learner

PASSWORD = "Password123!"


def _new_email(prefix: str = "delivery") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


async def _register(client: AsyncClient, role: str, email: str) -> Any:
    payload: dict[str, str] = {"email": email, "password": PASSWORD, "full_name": "Delivery Tester"}
    if role == "student":
        payload["preferred_modality"] = "visual"
    return await client.post(f"/api/v1/auth/register/{role}", json=payload)


async def _expire_cooldown(email: str, purpose_prefix: str = "otp") -> None:
    """Pretend the last code was sent 61 seconds ago, so a resend is allowed."""
    key = f"{purpose_prefix}:{email.lower()}"
    raw = await redis_client.get(key)
    assert raw is not None
    state = json.loads(raw)
    state["last_sent_at"] = time.time() - 61
    await redis_client.setex(key, 600, json.dumps(state))


async def _is_verified(email: str) -> bool:
    async with AsyncSessionLocal() as session:
        user = await user_repository.get_by_email(session, email.lower())
        assert user is not None
        return bool(user.is_verified)


# --------------------------------------------------------------------------- register and resend


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["student", "teacher"])
@pytest.mark.parametrize("delivery", ["email", "console", "failed"])
async def test_register_reports_delivery(
    async_client: AsyncClient, mock_email: MockEmailProvider, role: str, delivery: str
):
    mock_email.delivery = delivery  # type: ignore[assignment]
    email = _new_email(role)

    res = await _register(async_client, role, email)

    assert res.status_code == 201
    body = res.json()
    assert body["otp_delivery"] == delivery
    # The existing account fields are still there.
    assert body["email"] == email.lower()
    assert body["is_verified"] is False
    assert len(mock_email.sent_emails) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("delivery", "message_part"),
    [
        ("email", "sent to your email"),
        ("console", "printed in the terminal"),
        ("failed", "couldn't send the email"),
    ],
)
async def test_resend_reports_delivery(
    async_client: AsyncClient, mock_email: MockEmailProvider, delivery: str, message_part: str
):
    email = _new_email("resend")
    assert (await _register(async_client, "student", email)).status_code == 201
    await _expire_cooldown(email)

    mock_email.delivery = delivery  # type: ignore[assignment]
    res = await async_client.post("/api/v1/auth/verify-email/resend", json={"email": email})

    assert res.status_code == 200
    body = res.json()
    assert body["otp_delivery"] == delivery
    assert message_part in body["message"]
    assert len(mock_email.sent_emails) == 2


@pytest.mark.asyncio
async def test_production_send_failure_returns_503_and_keeps_user_unverified(
    async_client: AsyncClient, mock_email: MockEmailProvider, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    mock_email.delivery = "failed"
    email = _new_email("prodfail")

    res = await _register(async_client, "student", email)

    assert res.status_code == 503
    assert res.json()["detail"] == "EMAIL_DELIVERY_FAILED"
    assert await _is_verified(email) is False

    # Resending later fails the same way while email is down, and still verifies nothing...
    await _expire_cooldown(email)
    res = await async_client.post("/api/v1/auth/verify-email/resend", json={"email": email})
    assert res.status_code == 503
    assert res.json()["detail"] == "EMAIL_DELIVERY_FAILED"
    assert await _is_verified(email) is False

    # ...and once email works again, the resent code verifies the account.
    await _expire_cooldown(email)
    mock_email.delivery = "email"
    res = await async_client.post("/api/v1/auth/verify-email/resend", json={"email": email})
    assert res.status_code == 200
    assert res.json()["otp_delivery"] == "email"
    otp = mock_email.sent_emails[-1]["subject"].split()[0]
    res = await async_client.post("/api/v1/auth/verify-email", json={"email": email, "otp": otp})
    assert res.status_code == 200
    assert await _is_verified(email) is True


@pytest.mark.asyncio
async def test_production_success_still_returns_201(
    async_client: AsyncClient, mock_email: MockEmailProvider, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    res = await _register(async_client, "teacher", _new_email("prodok"))
    assert res.status_code == 201
    assert res.json()["otp_delivery"] == "email"


# --------------------------------------------------------------------------- password reset


async def _verified_user_with_password() -> User:
    return await create_verified_learner(
        email=_new_email("reset"), password_hash=get_password_hash(PASSWORD)
    )


@pytest.mark.asyncio
async def test_forgot_password_emails_a_code_that_resets_the_password(
    async_client: AsyncClient, mock_email: MockEmailProvider
):
    user = await _verified_user_with_password()

    res = await async_client.post("/api/v1/auth/forgot-password", json={"email": user.email})

    assert res.status_code == 200
    body = res.json()
    assert body["otp_delivery"] == "email"
    assert len(mock_email.sent_emails) == 1
    sent = mock_email.sent_emails[0]
    assert "password reset code" in sent["subject"]
    code = sent["subject"].split()[0]
    assert code not in json.dumps(body)  # the code only ever goes to the inbox

    new_password = "BrandNewPass456!"
    res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"email": user.email, "otp": code, "new_password": new_password},
    )
    assert res.status_code == 200

    res = await async_client.post("/api/v1/auth/login", json={"email": user.email, "password": new_password})
    assert res.status_code == 200

    # The code is single-use.
    res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"email": user.email, "otp": code, "new_password": "AnotherPass789!"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_verification_code_cannot_reset_a_password(
    async_client: AsyncClient, mock_email: MockEmailProvider
):
    email = _new_email("crossuse")
    await _register(async_client, "student", email)
    verification_code = mock_email.sent_emails[-1]["subject"].split()[0]

    res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"email": email, "otp": verification_code, "new_password": "Hijacked123!"},
    )
    assert res.status_code == 400

    # Asking for a reset code does not cancel the pending verification code either.
    await async_client.post("/api/v1/auth/forgot-password", json={"email": email})
    res = await async_client.post("/api/v1/auth/verify-email", json={"email": email, "otp": verification_code})
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password_for_unknown_email_sends_nothing_and_reveals_nothing(
    async_client: AsyncClient, mock_email: MockEmailProvider, monkeypatch: pytest.MonkeyPatch
):
    # With SMTP configured, a real send would say "email": an unknown address must say the same.
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(settings, "SMTP_USER", "sender@example.com")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "not-a-real-password")

    res = await async_client.post("/api/v1/auth/forgot-password", json={"email": _new_email("nobody")})

    assert res.status_code == 200
    assert res.json()["otp_delivery"] == "email"
    assert mock_email.sent_emails == []


@pytest.mark.asyncio
@pytest.mark.parametrize("delivery", ["console", "failed"])
async def test_forgot_password_reports_delivery(
    async_client: AsyncClient, mock_email: MockEmailProvider, delivery: str
):
    mock_email.delivery = delivery  # type: ignore[assignment]
    user = await _verified_user_with_password()

    res = await async_client.post("/api/v1/auth/forgot-password", json={"email": user.email})

    assert res.status_code == 200
    assert res.json()["otp_delivery"] == delivery


@pytest.mark.asyncio
async def test_forgot_password_production_failure_returns_503(
    async_client: AsyncClient, mock_email: MockEmailProvider, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    mock_email.delivery = "failed"
    user = await _verified_user_with_password()

    res = await async_client.post("/api/v1/auth/forgot-password", json={"email": user.email})

    assert res.status_code == 503
    assert res.json()["detail"] == "EMAIL_DELIVERY_FAILED"


# --------------------------------------------------------------------------- startup check


def _clear_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"):
        monkeypatch.setattr(settings, name, None)


def test_startup_check_fails_fast_in_production_without_smtp(monkeypatch: pytest.MonkeyPatch):
    _clear_smtp(monkeypatch)
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    with pytest.raises(RuntimeError, match="SMTP_HOST"):
        email_module.check_email_configuration()


def test_startup_check_logs_status(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    _clear_smtp(monkeypatch)
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    with caplog.at_level(logging.INFO, logger="uvicorn.error"):
        email_module.check_email_configuration()
    assert "Email: NOT configured" in caplog.text

    caplog.clear()
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(settings, "SMTP_USER", "sender@example.com")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "secret-app-password")
    with caplog.at_level(logging.INFO, logger="uvicorn.error"):
        email_module.check_email_configuration()
    assert "Email: SMTP configured (smtp.example.com:" in caplog.text
    assert "secret-app-password" not in caplog.text


# --------------------------------------------------------------------------- SMTP provider


class _FakeSMTP:
    """Records the SMTP conversation instead of opening a socket."""

    instances: ClassVar[list["_FakeSMTP"]] = []
    fail_with: ClassVar[Exception | None] = None

    def __init__(self, host: str, port: int, timeout: float, **kwargs: Any) -> None:
        self.host, self.port, self.timeout = host, port, timeout
        self.calls: list[str] = []
        self.ssl = False
        _FakeSMTP.instances.append(self)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.calls.append("quit")

    def starttls(self, context: Any = None) -> None:
        self.calls.append("starttls")

    def login(self, user: str, password: str) -> None:
        self.calls.append("login")
        if _FakeSMTP.fail_with is not None:
            raise _FakeSMTP.fail_with

    def sendmail(self, from_addr: str, to_addrs: list[str], msg: str) -> None:
        self.calls.append("sendmail")


class _FakeSMTPSSL(_FakeSMTP):
    def __init__(self, host: str, port: int, timeout: float, **kwargs: Any) -> None:
        super().__init__(host, port, timeout, **kwargs)
        self.ssl = True


@pytest.fixture
def fake_smtp(monkeypatch: pytest.MonkeyPatch) -> type[_FakeSMTP]:
    _FakeSMTP.instances = []
    _FakeSMTP.fail_with = None
    monkeypatch.setattr(email_module.smtplib, "SMTP", _FakeSMTP)
    monkeypatch.setattr(email_module.smtplib, "SMTP_SSL", _FakeSMTPSSL)
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(settings, "SMTP_USER", "sender@example.com")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "secret-app-password")
    monkeypatch.setattr(settings, "SMTP_TLS", True)
    return _FakeSMTP


def _send(provider: SMTPEmailProvider) -> str:
    return provider._send_sync("learner@example.com", "123456 is your code", "<p>123456</p>", "code: 123456")


@pytest.mark.parametrize(("port", "uses_ssl", "uses_starttls"), [(587, False, True), (465, True, False)])
def test_smtp_port_selects_starttls_or_ssl(
    fake_smtp: type[_FakeSMTP], monkeypatch: pytest.MonkeyPatch, port: int, uses_ssl: bool, uses_starttls: bool
):
    monkeypatch.setattr(settings, "SMTP_PORT", port)

    assert _send(SMTPEmailProvider()) == "email"

    server = fake_smtp.instances[-1]
    assert server.ssl is uses_ssl
    assert ("starttls" in server.calls) is uses_starttls
    assert server.timeout == 15
    assert server.calls[-2:] == ["sendmail", "quit"]


def test_smtp_failure_is_logged_without_secrets(
    fake_smtp: type[_FakeSMTP], monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    fake_smtp.fail_with = smtplib.SMTPAuthenticationError(535, b"5.7.8 Username and Password not accepted")

    with caplog.at_level(logging.ERROR):
        assert _send(SMTPEmailProvider()) == "failed"

    assert "SMTPAuthenticationError" in caplog.text
    assert "Username and Password not accepted" in caplog.text
    assert "secret-app-password" not in caplog.text
    assert "123456" not in caplog.text


def test_without_smtp_development_prints_code_and_production_does_not(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    _clear_smtp(monkeypatch)

    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    assert _send(SMTPEmailProvider()) == "console"
    out = capsys.readouterr().out
    assert "[DEV EMAIL CONSOLE] To: learner@example.com" in out
    assert "123456" in out
    out.encode("ascii")  # printable on any console encoding

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    assert _send(SMTPEmailProvider()) == "failed"
    assert "123456" not in capsys.readouterr().out
