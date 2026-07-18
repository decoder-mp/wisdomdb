"""Email delivery helpers."""

import smtplib
from email.message import EmailMessage

from core.config import EMAIL_FROM_ADDRESS
from core.config import SMTP_HOST
from core.config import SMTP_PASSWORD
from core.config import SMTP_PORT
from core.config import SMTP_USE_TLS
from core.config import SMTP_USERNAME


class EmailConfigurationError(RuntimeError):
    """Raised when email transport is not configured."""


def send_password_reset_email(recipient_email: str, reset_link: str) -> None:
    if not SMTP_HOST or not EMAIL_FROM_ADDRESS:
        raise EmailConfigurationError(
            "SMTP_HOST and EMAIL_FROM_ADDRESS must be configured for password reset emails."
        )

    message = EmailMessage()
    message["Subject"] = "Reset your Lore password"
    message["From"] = EMAIL_FROM_ADDRESS
    message["To"] = recipient_email
    message.set_content(
        "\n".join(
            [
                "A password reset was requested for your Lore account.",
                "",
                f"Open this link to set a new password: {reset_link}",
                "",
                "If you did not request this, you can ignore this email.",
            ]
        )
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        if SMTP_USE_TLS:
            smtp.starttls()
        if SMTP_USERNAME:
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(message)
