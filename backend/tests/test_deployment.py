"""Production safeguards: unsafe settings refused, password reset by email only, hosted database URLs, Brevo email."""
import json
import re

import httpx
import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from app.api.v1 import voice as voice_api
from app.core import database
from app.core.config import Settings, settings
from app.services.email_service import (
    BrevoEmailProvider,
    EmailService,
    MockEmailProvider,
    SMTPEmailProvider,
)
from tests.conftest import create_verified_learner

STRONG_SECRET = "k3Xv9qTzR7mW2pLs8YdN4bHc6JfG1aQe"


@pytest.mark.asyncio
async def test_production_emails_the_reset_token_and_never_returns_it(
    async_client: AsyncClient, mock_email: MockEmailProvider, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://lumina.example")
    learner = await create_verified_learner()

    res = await async_client.post("/api/v1/auth/forgot-password", json={"email": learner.email})

    assert res.status_code == 200
    assert res.json()["detail"] is None
    [sent] = mock_email.sent_emails
    assert sent["to_email"] == learner.email
    match = re.search(r"https://lumina\.example/reset-password\?token=([\w-]+)", sent["text_content"])
    assert match is not None
    assert match.group(0) in sent["html_content"]

    res = await async_client.post(
        "/api/v1/auth/reset-password", json={"token": match.group(1), "new_password": "BrandNewPass1!"}
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_unknown_email_gets_the_same_answer_and_no_email(
    async_client: AsyncClient, mock_email: MockEmailProvider, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    learner = await create_verified_learner()

    known = await async_client.post("/api/v1/auth/forgot-password", json={"email": learner.email})
    unknown = await async_client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})

    assert unknown.status_code == known.status_code == 200
    assert unknown.json() == known.json()
    assert len(mock_email.sent_emails) == 1


@pytest.mark.asyncio
async def test_reset_emails_are_limited_to_one_a_minute(async_client: AsyncClient, mock_email: MockEmailProvider):
    learner = await create_verified_learner()

    for _ in range(3):
        res = await async_client.post("/api/v1/auth/forgot-password", json={"email": learner.email})
        assert res.status_code == 200

    assert len(mock_email.sent_emails) == 1


@pytest.mark.asyncio
async def test_development_still_shows_the_reset_token(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    learner = await create_verified_learner()

    res = await async_client.post("/api/v1/auth/forgot-password", json={"email": learner.email})

    assert res.json()["detail"]


@pytest.mark.parametrize(
    "secret",
    [
        "DEV_SUPER_SECRET_KEY_CHANGE_IN_PROD_MIN_32_BYTES",
        "CHANGE_THIS_IN_PRODUCTION_SUPER_SECRET_KEY_MIN_32_BYTES",
        "too-short",
    ],
)
def test_production_refuses_a_public_or_short_secret_key(secret: str):
    with pytest.raises(ValidationError) as excinfo:
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=secret)
    assert "SECRET_KEY" in str(excinfo.value)
    assert secret not in str(excinfo.value)


def test_a_private_secret_key_is_accepted_in_production():
    assert Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=STRONG_SECRET).SECRET_KEY == STRONG_SECRET


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        (
            "postgresql://user:p%40ss@ep-x.neon.tech/db?sslmode=require&channel_binding=require",
            "postgresql+asyncpg://user:p%40ss@ep-x.neon.tech/db?ssl=require",
        ),
        ("postgres://user:pw@db.example:5433/db", "postgresql+asyncpg://user:pw@db.example:5433/db"),
    ],
)
def test_hosted_database_urls_are_adapted_for_asyncpg(given: str, expected: str):
    assert Settings(_env_file=None, DATABASE_URL=given).ASYNC_DATABASE_URI == expected


def test_frontend_url_comes_from_the_host_unless_overridden(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("FRONTEND_URL", raising=False)
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://lumina.onrender.com/")
    assert Settings(_env_file=None).FRONTEND_URL == "https://lumina.onrender.com"

    monkeypatch.setenv("FRONTEND_URL", "https://learn.example")
    assert Settings(_env_file=None).FRONTEND_URL == "https://learn.example"


def test_voice_socket_accepts_the_public_site_and_no_other(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://lumina.onrender.com")
    assert voice_api.origin_allowed("https://lumina.onrender.com")
    assert not voice_api.origin_allowed("https://evil.example.com")


@pytest.mark.asyncio
async def test_production_refuses_sqlite(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(database, "use_sqlite", True)
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        await database.init_db()


@pytest.mark.asyncio
async def test_brevo_provider_sends_through_the_api(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "BREVO_API_KEY", "test-api-key")
    monkeypatch.setattr(settings, "EMAILS_FROM_EMAIL", "sender@example.com")
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(url=str(request.url), api_key=request.headers["api-key"], body=json.loads(request.content))
        return httpx.Response(201, json={"messageId": "<id@example.com>"})

    provider = BrevoEmailProvider(transport=httpx.MockTransport(handler))

    assert await provider.send_email("learner@example.com", "Hello", "<p>Hi</p>", "Hi") is True
    assert seen["url"] == "https://api.brevo.com/v3/smtp/email"
    assert seen["api_key"] == "test-api-key"
    assert seen["body"]["sender"]["email"] == "sender@example.com"
    assert seen["body"]["to"] == [{"email": "learner@example.com"}]
    assert seen["body"]["subject"] == "Hello"
    assert seen["body"]["htmlContent"] == "<p>Hi</p>"


@pytest.mark.asyncio
async def test_brevo_failures_are_reported_not_raised():
    refused = BrevoEmailProvider(transport=httpx.MockTransport(lambda _: httpx.Response(401, json={"code": "unauthorized"})))
    assert await refused.send_email("learner@example.com", "Hello", "<p>Hi</p>", "Hi") is False

    def unreachable(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route", request=request)

    down = BrevoEmailProvider(transport=httpx.MockTransport(unreachable))
    assert await down.send_email("learner@example.com", "Hello", "<p>Hi</p>", "Hi") is False


def test_the_email_provider_follows_the_configuration(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "BREVO_API_KEY", "test-api-key")
    assert isinstance(EmailService().provider, BrevoEmailProvider)
    monkeypatch.setattr(settings, "BREVO_API_KEY", None)
    assert isinstance(EmailService().provider, SMTPEmailProvider)


@pytest.mark.asyncio
async def test_names_cannot_inject_html_into_emails():
    provider = MockEmailProvider()
    service = EmailService(provider)
    name = '<a href="https://evil.example.com">Click</a>'

    await service.send_otp_email("learner@example.com", "123456", name)
    await service.send_password_reset_email("learner@example.com", "token", name)

    for sent in provider.sent_emails:
        assert name not in sent["html_content"]
        assert "&lt;a href=" in sent["html_content"]
