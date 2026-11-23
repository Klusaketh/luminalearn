"""
Send one test email with the SMTP settings in backend/.env, to check that OTP emails will arrive:

    cd backend
    python scripts/send_test_email.py you@example.com

Prints "sent", or the exact error the mail server (or network) returned. Never prints the password.
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
os.chdir(BACKEND_DIR)  # settings read .env from the working directory
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.email_service import (
    SMTPEmailProvider,
    sender_address,
    smtp_configured,
)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or "@" not in argv[1]:
        print("usage: python scripts/send_test_email.py <to-address>")
        return 2
    to_email = argv[1]

    if not smtp_configured():
        print(
            "not sent: SMTP is not configured. "
            "Set SMTP_HOST, SMTP_USER and SMTP_PASSWORD in backend/.env."
        )
        return 1

    print(
        f"Sending a test email to {to_email} via {settings.SMTP_HOST}:{settings.SMTP_PORT} "
        f"from {sender_address()} ..."
    )
    try:
        SMTPEmailProvider().transmit(
            to_email,
            subject="LuminaLearn AI test email",
            html_content="<p>Your LuminaLearn AI server can send email. Sign-up codes will arrive like this one.</p>",
            text_content="Your LuminaLearn AI server can send email. Sign-up codes will arrive like this one.",
        )
    except Exception as exc:  # noqa: BLE001 - report every failure verbatim: that is the point of this script
        print(f"error: {type(exc).__name__}: {exc}")
        return 1
    print("sent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
