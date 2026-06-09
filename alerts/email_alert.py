"""
Email alert module for InfernoGuard AI.

Sends SMTP email notifications when fire or smoke is detected.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

from utils.logger import get_logger

logger = get_logger(__name__)


def send_email_alert(
    config: dict,
    detection_type: str,
    confidence: float,
    screenshot_path: str,
) -> bool:
    """
    Send an email notification for a fire/smoke detection event.

    Args:
        config: Dict with keys smtp_host, smtp_port, email_sender,
                email_recipient, email_password.
        detection_type: 'fire' or 'smoke'
        confidence: Detection confidence score (0.0–1.0)
        screenshot_path: Path to the saved screenshot (may be empty string)

    Returns:
        True on success, False on failure.
    """
    try:
        smtp_host = config.get("smtp_host", "smtp.gmail.com")
        smtp_port = int(config.get("smtp_port", 587))
        sender = config.get("email_sender", "")
        recipient = config.get("email_recipient", "")
        password = config.get("email_password", "")

        if not sender or not recipient:
            logger.warning("Email alert skipped: sender or recipient not configured.")
            return False

        subject = f"[InfernoGuard AI] {detection_type.upper()} Detected!"
        body = (
            f"InfernoGuard AI has detected {detection_type} with "
            f"{confidence * 100:.1f}% confidence.\n\n"
            "Please review the attached screenshot and take immediate action."
        )

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach screenshot if it exists
        if screenshot_path and os.path.isfile(screenshot_path):
            with open(screenshot_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(screenshot_path)}"',
            )
            msg.attach(part)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

        logger.info("Email alert sent to %s for %s detection.", recipient, detection_type)
        return True

    except Exception as exc:
        logger.error("Email alert failed: %s", exc, exc_info=True)
        return False
