"""
Provider-independent Email Service for LuminaLearn AI.
Supports standard SMTP (including Gmail SMTP), custom enterprise providers, and testing mocks.
Never hard-codes credentials or sensitive verification data.

Every send reports how the message was delivered (see `OTPDelivery`): "email" when an SMTP
server accepted it, "console" when development without SMTP printed it to the API terminal,
and "failed" otherwise. Callers must never tell a user "we emailed you" unless it was "email".
"""
import asyncio
import logging
import smtplib
import ssl
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.schemas.auth import OTPDelivery
from app.services.otp_service import OTPPurpose

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SECONDS = 15
# Port 465 speaks TLS from the first byte (SMTPS). Every other port (587, 2525, 25) starts in
# plain text and upgrades with STARTTLS when SMTP_TLS is true.
IMPLICIT_TLS_PORT = 465


def smtp_configured() -> bool:
    """True when host, user and password are all set, so codes can really be emailed."""
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


def sender_address() -> str:
    return settings.EMAILS_FROM_EMAIL or settings.SMTP_USER or "noreply@luminalearn.ai"


def fallback_delivery() -> OTPDelivery:
    """How a code is delivered when SMTP is not configured: printed in development, else lost."""
    return "console" if settings.ENVIRONMENT == "development" else "failed"


def expected_delivery() -> OTPDelivery:
    """The delivery a successful send would report, for responses that must not reveal accounts."""
    return "email" if smtp_configured() else fallback_delivery()


def check_email_configuration() -> None:
    """
    Log one line saying whether email works, at API startup. In production, refuse to start
    without SMTP: nobody could register or reset a password.
    """
    # Uvicorn configures only its own loggers, so this line goes through one of them to be seen.
    startup_log = logging.getLogger("uvicorn.error")
    if smtp_configured():
        startup_log.info(
            "Email: SMTP configured (%s:%s, from %s)",
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            sender_address(),
        )
        return
    message = (
        "Email: NOT configured - OTP codes will be printed to the console (development) "
        "or not sent (production). Set SMTP_HOST, SMTP_USER and SMTP_PASSWORD in backend/.env."
    )
    if settings.ENVIRONMENT == "production":
        startup_log.critical(message)
        raise RuntimeError(
            "SMTP_HOST, SMTP_USER and SMTP_PASSWORD are required when ENVIRONMENT=production."
        )
    startup_log.warning(message)


class BaseEmailProvider(ABC):
    """Abstract Base Class for email providers (e.g. SMTP, SendGrid, SES, Mock)."""

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> OTPDelivery:
        """Asynchronously send an email and report how it was delivered."""


class SMTPEmailProvider(BaseEmailProvider):
    """
    Standard SMTP email provider supporting Gmail SMTP, Brevo, SendGrid, Mailgun, AWS SES,
    and any RFC 5321 compliant SMTP server.
    """

    def transmit(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> None:
        """Send one message over SMTP. Raises the SMTP/network error if the server rejects it."""
        host = settings.SMTP_HOST
        user = settings.SMTP_USER
        password = settings.SMTP_PASSWORD
        if not host or not user or not password:
            raise RuntimeError("SMTP is not configured: set SMTP_HOST, SMTP_USER and SMTP_PASSWORD.")
        port = settings.SMTP_PORT
        from_email = sender_address()
        from_name = settings.EMAILS_FROM_NAME or "LuminaLearn AI"

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = to_email
        message.attach(MIMEText(text_content, "plain", "utf-8"))
        message.attach(MIMEText(html_content, "html", "utf-8"))

        context = ssl.create_default_context()
        server: smtplib.SMTP
        if port == IMPLICIT_TLS_PORT:
            server = smtplib.SMTP_SSL(host, port, timeout=SMTP_TIMEOUT_SECONDS, context=context)
        else:
            server = smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT_SECONDS)
        with server:
            if port != IMPLICIT_TLS_PORT and settings.SMTP_TLS:
                server.starttls(context=context)
            server.login(user, password)
            server.sendmail(from_email, [to_email], message.as_string())

    def _send_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> OTPDelivery:
        if not smtp_configured():
            delivery = fallback_delivery()
            if delivery == "console":
                # ASCII only: on Windows a piped stdout may not be able to encode emoji.
                print("\n" + "=" * 64)
                print(f"[DEV EMAIL CONSOLE] To: {to_email}")
                print(f"   Subject: {subject}")
                for line in text_content.strip().split("\n"):
                    if "code is:" in line.lower() or "valid for" in line.lower():
                        print(f"   {line.strip()}")
                print("=" * 64 + "\n", flush=True)
            else:
                logger.error(
                    "SMTP is not configured in the %s environment, so the email to %s was not sent.",
                    settings.ENVIRONMENT,
                    to_email,
                )
            return delivery

        try:
            self.transmit(to_email, subject, html_content, text_content)
        except (smtplib.SMTPException, OSError) as exc:
            # OSError covers DNS, refused connections, TLS and timeouts. The exception text is the
            # server's reply; it never contains the password or the message (so never the code).
            hint = ""
            if isinstance(exc, smtplib.SMTPAuthenticationError):
                hint = " Check SMTP_USER and SMTP_PASSWORD (Gmail needs an App Password)."
            elif not isinstance(exc, smtplib.SMTPException):  # SMTPException is itself an OSError
                hint = (
                    " Could not reach or secure the SMTP server: check SMTP_HOST and SMTP_PORT."
                    " Some hosts block outbound SMTP (Render's free plan blocks 25, 465 and 587)."
                )
            logger.error(
                "Email to %s via %s:%s failed: %s: %s.%s",
                to_email,
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                type(exc).__name__,
                exc,
                hint,
            )
            return "failed"
        logger.info("Email sent to %s via SMTP (%s)", to_email, settings.SMTP_HOST)
        return "email"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> OTPDelivery:
        """Run the blocking SMTP exchange on a worker thread so the event loop keeps serving."""
        return await asyncio.to_thread(
            self._send_sync,
            to_email,
            subject,
            html_content,
            text_content,
        )


class MockEmailProvider(BaseEmailProvider):
    """In-memory mock email provider for testing and offline development."""

    def __init__(self, delivery: OTPDelivery = "email") -> None:
        self.sent_emails: list[dict[str, str]] = []
        # What send_email reports, so tests can simulate a console fallback or a failed send.
        self.delivery: OTPDelivery = delivery

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> OTPDelivery:
        self.sent_emails.append({
            "to_email": to_email,
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content,
        })
        logger.debug("Mock email queued for %s (reporting %s)", to_email, self.delivery)
        return self.delivery

    def clear(self) -> None:
        self.sent_emails.clear()


_OTP_COPY: dict[OTPPurpose, dict[str, str]] = {
    "verify": {
        "subject": "is your LuminaLearn AI verification code",
        "title": "Verify Your Email Address",
        "intro": "use the 6-digit verification code below to activate your account.",
        "ignore": "If you did not create an account on LuminaLearn AI, you can safely ignore this email.",
    },
    "reset": {
        "subject": "is your LuminaLearn AI password reset code",
        "title": "Reset Your Password",
        "intro": "use the 6-digit code below to choose a new password.",
        "ignore": "If you did not ask to reset your password, you can safely ignore this email. Your password has not changed.",
    },
}


class EmailService:
    """High-level email service handling templating and provider delegation."""

    def __init__(self, provider: BaseEmailProvider | None = None) -> None:
        self.provider = provider or SMTPEmailProvider()

    def set_provider(self, provider: BaseEmailProvider) -> None:
        """Swap email provider at runtime (e.g. for testing)."""
        self.provider = provider

    async def send_otp_email(
        self,
        to_email: str,
        otp: str,
        user_name: str | None = None,
        purpose: OTPPurpose = "verify",
    ) -> OTPDelivery:
        """
        Send a 6-digit one-time code (email verification or password reset) with a
        10-minute validity notice, and report how it was delivered.
        """
        copy = _OTP_COPY[purpose]
        display_name = user_name or "Learner"
        subject = f"{otp} {copy['subject']}"

        text_content = (
            f"Hello {display_name},\n\n"
            f"Your LuminaLearn AI code is: {otp}\n\n"
            f"This code is valid for 10 minutes.\n"
            f"{copy['ignore']}\n\n"
            f"Best regards,\n"
            f"The LuminaLearn AI Team"
        )

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{copy['title']}</title>
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
              {copy['title']}
            </td>
          </tr>
          <tr>
            <td style="font-size: 14px; color: #94a3b8; line-height: 1.6; text-align: center; padding-bottom: 28px;">
              Hello <strong style="color: #f1f5f9;">{display_name}</strong>, {copy['intro']}
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
              This code is valid for <strong>10 minutes</strong>. Do not share this code with anyone.
            </td>
          </tr>
          <tr>
            <td style="border-top: 1px solid #1f2937; padding-top: 20px; font-size: 12px; color: #475569; text-align: center;">
              {copy['ignore']}<br>
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


email_service = EmailService()
