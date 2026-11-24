"""
Provider-independent Email Service for LuminaLearn AI.

Supports standard SMTP (Gmail, Brevo, SendGrid, Mailgun, Amazon SES, ...) and an in-memory mock for tests.
Every send reports how the message was delivered, so callers never tell a learner "we emailed you" when
nothing was sent:

- "email":   the SMTP server accepted the message.
- "console": development without SMTP settings; the message was printed to the API console instead.
- "failed":  SMTP is not configured outside development, or the SMTP server refused or could not be reached.

Credentials come from settings only, and codes and links are never logged outside development.
"""

import asyncio
import html
import logging
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid
from typing import Literal

from app.core.config import settings

logger = logging.getLogger(__name__)

EmailDelivery = Literal["email", "console", "failed"]
EmailMode = Literal["email", "console", "disabled"]

SMTP_TIMEOUT_SECONDS = 15


def smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


def email_mode() -> EmailMode:
    """How this server delivers email right now. Server-wide, so it reveals nothing about any account."""
    if smtp_configured():
        return "email"
    return "console" if settings.ENVIRONMENT == "development" else "disabled"


class BaseEmailProvider(ABC):
    """Abstract base class for email providers (SMTP, Mock, ...)."""

    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> EmailDelivery:
        """Send one email and report how it was delivered."""


class SMTPEmailProvider(BaseEmailProvider):
    """Any RFC 5321 SMTP server. Port 465 uses implicit TLS; other ports use STARTTLS when SMTP_TLS is true."""

    def _send_sync(self, to_email: str, subject: str, html_content: str, text_content: str) -> EmailDelivery:
        if not smtp_configured():
            if settings.ENVIRONMENT == "development":
                # Development only: show the message where the developer is looking.
                print("\n" + "=" * 64)
                print("📧 [DEV EMAIL CONSOLE] SMTP is not configured, so this email was not sent.")
                print(f"   To: {to_email}")
                print(f"   Subject: {subject}")
                for line in text_content.strip().splitlines():
                    if line.strip():
                        print(f"   {line.strip()}")
                print("=" * 64 + "\n", flush=True)
                return "console"
            logger.error(
                "Email to %s not sent: SMTP is not configured in the %s environment. Set SMTP_HOST, SMTP_USER and SMTP_PASSWORD.",
                to_email,
                settings.ENVIRONMENT,
            )
            return "failed"

        host = settings.SMTP_HOST or ""
        port = settings.SMTP_PORT
        user = settings.SMTP_USER or ""
        password = settings.SMTP_PASSWORD or ""
        from_email = settings.EMAILS_FROM_EMAIL or user
        from_name = settings.EMAILS_FROM_NAME or "LuminaLearn AI"

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = formataddr((from_name, from_email))
        message["To"] = to_email
        message["Message-ID"] = make_msgid(domain=from_email.split("@")[-1] if "@" in from_email else None)
        message.attach(MIMEText(text_content, "plain", "utf-8"))
        message.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            if port == 465:
                with smtplib.SMTP_SSL(host, port, timeout=SMTP_TIMEOUT_SECONDS) as server:
                    server.login(user, password)
                    server.sendmail(from_email, [to_email], message.as_string())
            else:
                with smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT_SECONDS) as server:
                    if settings.SMTP_TLS:
                        server.starttls()
                    server.login(user, password)
                    server.sendmail(from_email, [to_email], message.as_string())
        except smtplib.SMTPAuthenticationError as exc:
            logger.error(
                "SMTP login failed for %s on %s:%s (%s). For Gmail, SMTP_PASSWORD must be a 16-character App Password.",
                user,
                host,
                port,
                exc.smtp_code,
            )
            return "failed"
        except (smtplib.SMTPException, OSError) as exc:
            # OSError covers DNS, socket, TLS and timeout failures.
            logger.error("Email to %s via %s:%s failed: %s: %s", to_email, host, port, type(exc).__name__, exc)
            return "failed"

        logger.info("Email sent to %s via %s", to_email, host)
        return "email"

    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> EmailDelivery:
        """SMTP is blocking: run it on a worker thread so the event loop keeps serving requests."""
        return await asyncio.to_thread(self._send_sync, to_email, subject, html_content, text_content)


class MockEmailProvider(BaseEmailProvider):
    """In-memory provider for tests. Set `delivery` to simulate console output or failures."""

    def __init__(self) -> None:
        self.sent_emails: list[dict[str, str]] = []
        self.delivery: EmailDelivery = "email"

    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> EmailDelivery:
        self.sent_emails.append(
            {"to_email": to_email, "subject": subject, "html_content": html_content, "text_content": text_content}
        )
        return self.delivery

    def clear(self) -> None:
        self.sent_emails.clear()
        self.delivery = "email"


def _layout(badge: str, heading: str, intro_html: str, body_html: str, footer: str) -> str:
    """Shared dark email layout. Callers must escape any user-supplied text they pass in."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{heading}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0b0f19; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="100%" style="max-width: 560px; background-color: #111827; border: 1px solid #1e293b; border-radius: 16px; padding: 36px 32px;">
          <tr>
            <td align="center" style="padding-bottom: 24px;">
              <span style="display: inline-block; padding: 6px 14px; border-radius: 9999px; background-color: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); color: #818cf8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{badge}</span>
            </td>
          </tr>
          <tr>
            <td style="font-size: 22px; font-weight: 700; color: #ffffff; text-align: center; padding-bottom: 12px;">{heading}</td>
          </tr>
          <tr>
            <td style="font-size: 14px; color: #94a3b8; line-height: 1.6; text-align: center; padding-bottom: 28px;">{intro_html}</td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom: 28px;">{body_html}</td>
          </tr>
          <tr>
            <td style="border-top: 1px solid #1f2937; padding-top: 20px; font-size: 12px; color: #64748b; text-align: center; line-height: 1.6;">
              {footer}<br>&copy; 2026 LuminaLearn AI.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


class EmailService:
    """High-level email service: builds messages and delegates delivery to a provider."""

    def __init__(self, provider: BaseEmailProvider | None = None) -> None:
        self.provider = provider or SMTPEmailProvider()

    def set_provider(self, provider: BaseEmailProvider) -> None:
        """Swap the email provider at runtime (for example in tests)."""
        self.provider = provider

    async def send_otp_email(self, to_email: str, otp: str, user_name: str | None = None) -> EmailDelivery:
        """Send a 6-digit email verification code, valid for 10 minutes."""
        name = user_name or "Learner"
        subject = f"{otp} is your LuminaLearn AI verification code"
        text_content = (
            f"Hello {name},\n\n"
            f"Your LuminaLearn AI verification code is: {otp}\n\n"
            "This code expires in 10 minutes. Do not share it with anyone.\n"
            "If you did not create a LuminaLearn AI account, you can ignore this email.\n\n"
            "The LuminaLearn AI Team"
        )
        html_content = _layout(
            badge="LuminaLearn AI Security",
            heading="Verify your email address",
            intro_html=f'Hello <strong style="color: #f1f5f9;">{html.escape(name)}</strong>, use this code to activate your account.',
            body_html=(
                '<div style="display: inline-block; background-color: #030712; border: 1px solid #312e81; border-radius: 12px; '
                'padding: 18px 36px; letter-spacing: 8px; font-size: 32px; font-weight: 800; color: #a5b4fc; font-family: monospace;">'
                f"{html.escape(otp)}</div>"
            ),
            footer="This code expires in <strong>10 minutes</strong>. If you did not request it, you can ignore this email.",
        )
        return await self.provider.send_email(to_email, subject, html_content, text_content)

    async def send_password_reset_email(self, to_email: str, reset_url: str, user_name: str | None = None) -> EmailDelivery:
        """Send a single-use password reset link, valid for 15 minutes."""
        name = user_name or "Learner"
        subject = "Reset your LuminaLearn AI password"
        text_content = (
            f"Hello {name},\n\n"
            "We received a request to reset your LuminaLearn AI password. Open this link to choose a new one:\n\n"
            f"{reset_url}\n\n"
            "The link works once and expires in 15 minutes.\n"
            "If you did not ask to reset your password, ignore this email: your password stays the same.\n\n"
            "The LuminaLearn AI Team"
        )
        safe_url = html.escape(reset_url, quote=True)
        html_content = _layout(
            badge="LuminaLearn AI Security",
            heading="Reset your password",
            intro_html=(
                f'Hello <strong style="color: #f1f5f9;">{html.escape(name)}</strong>, we received a request to reset your password. '
                "This link works once and expires in 15 minutes."
            ),
            body_html=(
                f'<a href="{safe_url}" style="display: inline-block; background-color: #6366f1; color: #ffffff; text-decoration: none; '
                'font-weight: 700; font-size: 15px; padding: 14px 28px; border-radius: 12px;">Choose a new password</a>'
                f'<p style="margin: 16px 0 0; font-size: 12px; color: #64748b; word-break: break-all;">{safe_url}</p>'
            ),
            footer="If you did not ask to reset your password, ignore this email. Your password stays the same.",
        )
        return await self.provider.send_email(to_email, subject, html_content, text_content)


email_service = EmailService()
