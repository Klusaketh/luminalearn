"""
Startup checks: refuse to run production with unsafe settings, and say plainly how email is delivered.
"""

import logging

from app.core.config import DEFAULT_SECRET_KEY, settings
from app.services.email_service import email_mode

logger = logging.getLogger("luminalearn.startup")

MIN_SECRET_KEY_LENGTH = 32


class UnsafeConfigurationError(RuntimeError):
    """Raised when production is configured in a way that would let attackers in."""


def run_startup_checks() -> None:
    production = settings.ENVIRONMENT == "production"

    if production:
        if settings.SECRET_KEY == DEFAULT_SECRET_KEY or len(settings.SECRET_KEY) < MIN_SECRET_KEY_LENGTH:
            # Anyone who knows the development key can forge sign-in tokens for any account.
            raise UnsafeConfigurationError(
                f"SECRET_KEY must be a private random value of at least {MIN_SECRET_KEY_LENGTH} characters in production "
                "(for example the output of `openssl rand -hex 32`)."
            )
        if settings.DEBUG:
            logger.warning("DEBUG is true in production: SQL statements are logged. Set DEBUG=false.")
        if settings.FRONTEND_URL.startswith(("http://localhost", "http://127.0.0.1")):
            logger.warning(
                "FRONTEND_URL is %s in production, so password-reset links will point at localhost. "
                "Set it to the public address of the web app.",
                settings.FRONTEND_URL,
            )

    mode = email_mode()
    if mode == "email":
        logger.info(
            "Email: SMTP configured (%s:%s, from %s).",
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            settings.EMAILS_FROM_EMAIL or settings.SMTP_USER,
        )
    elif mode == "console":
        logger.warning(
            "Email: SMTP is NOT configured. Verification codes and reset links are printed in this console "
            "(development only). Set SMTP_HOST, SMTP_USER and SMTP_PASSWORD to send real emails."
        )
    else:
        logger.error(
            "Email: SMTP is NOT configured in %s, so no verification or reset email can be sent and new users "
            "cannot finish signing up. Set SMTP_HOST, SMTP_USER and SMTP_PASSWORD.",
            settings.ENVIRONMENT,
        )
