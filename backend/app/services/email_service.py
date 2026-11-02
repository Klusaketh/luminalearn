"""
Provider-independent Email Service for LuminaLearn AI.
Supports standard SMTP (including Gmail SMTP), Brevo's HTTPS API, custom enterprise providers, and testing mocks.
Never hard-codes credentials or sensitive verification data.
"""
import asyncio
import html
import logging
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseEmailProvider(ABC):
    """Abstract Base Class for email providers (e.g. SMTP, SendGrid, SES, Mock)."""

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        """Asynchronously send an email."""


class SMTPEmailProvider(BaseEmailProvider):
    """
    Standard SMTP email provider supporting Gmail SMTP, Mailgun, SendGrid, AWS SES,
    and any RFC 5321 compliant SMTP server.
    """

    def _send_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        host = settings.SMTP_HOST
        port = settings.SMTP_PORT
        user = settings.SMTP_USER
        password = settings.SMTP_PASSWORD
        use_tls = settings.SMTP_TLS
        from_email = settings.EMAILS_FROM_EMAIL or user or "noreply@luminalearn.ai"
        from_name = settings.EMAILS_FROM_NAME or "LuminaLearn AI"

        if not host or not user or not password:
            if settings.ENVIRONMENT == "development":
                logger.warning(
                    "SMTP credentials not fully configured (host=%s, user=%s). Dispatching to dev console.",
                    bool(host),
                    bool(user),
                )
                print("\n" + "=" * 64)
                print(f"📧 [DEV EMAIL CONSOLE] To: {to_email}")
                print(f"   Subject: {subject}")
                for line in text_content.strip().split("\n"):
                    if "code:" in line.lower() or "valid for" in line.lower():
                        print(f"   {line.strip()}")
                print("=" * 64 + "\n", flush=True)
            else:
                logger.error(
                    "SMTP credentials not configured in %s environment. Refusing to print OTP to stdout. Email to %s dropped.",
                    settings.ENVIRONMENT,
                    to_email,
                )
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = to_email

        part_text = MIMEText(text_content, "plain", "utf-8")
        part_html = MIMEText(html_content, "html", "utf-8")
        message.attach(part_text)
        message.attach(part_html)

        try:
            if port == 465:
                with smtplib.SMTP_SSL(host, port, timeout=10) as server:
                    server.login(user, password)
                    server.sendmail(from_email, [to_email], message.as_string())
            else:
                with smtplib.SMTP(host, port, timeout=10) as server:
                    if use_tls:
                        server.starttls()
                    server.login(user, password)
                    server.sendmail(from_email, [to_email], message.as_string())
            logger.info("Email successfully dispatched to %s via SMTP (%s)", to_email, host)
            return True
        except (smtplib.SMTPException, OSError) as exc:
            # OSError covers DNS, socket, TLS and timeout failures.
            logger.error("Failed to send email to %s: %s", to_email, str(exc))
            return False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        """Run blocking SMTP transmission on background worker thread."""
        return await asyncio.to_thread(
            self._send_sync,
            to_email,
            subject,
            html_content,
            text_content,
        )


class BrevoEmailProvider(BaseEmailProvider):
    """Brevo's transactional email API, for hosts that block outbound SMTP (Render's free plan does)."""

    API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._transport = transport

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        payload = {
            "sender": {"name": settings.EMAILS_FROM_NAME, "email": settings.EMAILS_FROM_EMAIL},
            "to": [{"email": to_email}],
            "subject": subject,
            # Brevo documents one body type per request, so the plain-text part is not sent.
            "htmlContent": html_content,
        }
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=10) as client:
                response = await client.post(self.API_URL, json=payload, headers={"api-key": settings.BREVO_API_KEY or ""})
        except httpx.HTTPError as exc:
            logger.error("Failed to reach Brevo for email to %s: %s", to_email, exc)
            return False
        if response.is_error:
            # Brevo's reply names the problem, such as an unverified sender or a bad API key.
            logger.error("Brevo refused email to %s (%s): %s", to_email, response.status_code, response.text[:300])
            return False
        logger.info("Email successfully dispatched to %s via Brevo", to_email)
        return True


class MockEmailProvider(BaseEmailProvider):
    """In-memory mock email provider for testing and offline development."""

    def __init__(self) -> None:
        self.sent_emails: list[dict[str, str]] = []

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        self.sent_emails.append({
            "to_email": to_email,
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content,
        })
        logger.debug("Mock email queued for %s with subject: %s", to_email, subject)
        return True

    def clear(self) -> None:
        self.sent_emails.clear()


class EmailService:
    """High-level email service handling templating and provider delegation."""

    def __init__(self, provider: BaseEmailProvider | None = None) -> None:
        self.provider = provider or (BrevoEmailProvider() if settings.BREVO_API_KEY else SMTPEmailProvider())

    def set_provider(self, provider: BaseEmailProvider) -> None:
        """Swap email provider at runtime (e.g. for testing)."""
        self.provider = provider

    async def send_otp_email(
        self,
        to_email: str,
        otp: str,
        user_name: str | None = None,
    ) -> bool:
        """
        Send a secure 6-digit email verification OTP with 10-minute validity notice.
        """
        display_name = user_name or "Learner"
        subject = f"{otp} is your LuminaLearn AI verification code"

        text_content = (
            f"Hello {display_name},\n\n"
            f"Your LuminaLearn AI verification code is: {otp}\n\n"
            f"This code will expire in exactly 10 minutes.\n"
            f"If you did not create an account on LuminaLearn AI, you can safely ignore this email.\n\n"
            f"Best regards,\n"
            f"The LuminaLearn AI Team"
        )

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Verify Your Email</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0b0f19; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="100%" max-width="560px" style="max-width: 560px; background-color: #111827; border: 1px solid #1e293b; border-radius: 16px; padding: 36px 32px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);">
          <tr>
            <td align="center" style="padding-bottom: 24px;">
              <span style="display: inline-block; padding: 6px 14px; border-radius: 9999px; background-color: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); color: #818cf8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                LuminaLearn AI Security
              </span>
            </td>
          </tr>
          <tr>
            <td style="font-size: 22px; font-weight: 700; color: #ffffff; text-align: center; padding-bottom: 12px;">
              Verify Your Email Address
            </td>
          </tr>
          <tr>
            <td style="font-size: 14px; color: #94a3b8; line-height: 1.6; text-align: center; padding-bottom: 28px;">
              Hello <strong style="color: #f1f5f9;">{html.escape(display_name)}</strong>, use the 6-digit verification code below to activate your account.
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom: 28px;">
              <div style="display: inline-block; background-color: #030712; border: 1px solid #312e81; border-radius: 12px; padding: 18px 36px; letter-spacing: 8px; font-size: 32px; font-weight: 800; color: #a5b4fc; font-family: monospace;">
                {otp}
              </div>
            </td>
          </tr>
          <tr>
            <td style="font-size: 13px; color: #64748b; line-height: 1.5; text-align: center; padding-bottom: 24px;">
              ⏰ This code is valid for <strong>10 minutes</strong>. Do not share this code with anyone.
            </td>
          </tr>
          <tr>
            <td style="border-top: 1px solid #1f2937; padding-top: 20px; font-size: 12px; color: #475569; text-align: center;">
              If you did not request this code, please ignore this email.<br>
              &copy; 2026 LuminaLearn AI. All rights reserved.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        return await self.provider.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    async def send_password_reset_email(
        self,
        to_email: str,
        token: str,
        user_name: str | None = None,
    ) -> bool:
        """
        Send a password reset link, valid for the reset token's 15-minute lifetime.
        """
        display_name = user_name or "Learner"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Reset your LuminaLearn AI password"

        text_content = (
            f"Hello {display_name},\n\n"
            f"Reset your LuminaLearn AI password here (valid for 15 minutes):\n{reset_url}\n\n"
            f"If you did not ask to reset your password, you can safely ignore this email.\n\n"
            f"Best regards,\n"
            f"The LuminaLearn AI Team"
        )

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 40px 20px; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9; text-align: center;">
  <h1 style="font-size: 22px; font-weight: 700; color: #ffffff;">Reset Your Password</h1>
  <p style="font-size: 14px; color: #94a3b8; line-height: 1.6;">
    Hello <strong style="color: #f1f5f9;">{html.escape(display_name)}</strong>, use the button below to choose a new password.
  </p>
  <p style="padding: 16px 0;">
    <a href="{reset_url}" style="display: inline-block; background-color: #4f46e5; border-radius: 12px; padding: 14px 28px; font-size: 14px; font-weight: 700; color: #ffffff; text-decoration: none;">Reset Password</a>
  </p>
  <p style="font-size: 13px; color: #64748b; line-height: 1.5;">
    This link is valid for <strong>15 minutes</strong>. If you did not ask to reset your password, please ignore this email.
  </p>
</body>
</html>"""

        return await self.provider.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )


email_service = EmailService()
