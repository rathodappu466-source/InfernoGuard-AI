"""
Telegram alert module for InfernoGuard AI.

Sends Telegram Bot API messages when fire or smoke is detected.
"""

import requests

from utils.logger import get_logger

logger = get_logger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_alert(
    token: str,
    chat_id: str,
    detection_type: str,
    confidence: float,
) -> bool:
    """
    Send a Telegram message for a fire/smoke detection event.

    Args:
        token: Telegram Bot API token.
        chat_id: Target Telegram chat ID.
        detection_type: 'fire' or 'smoke'
        confidence: Detection confidence score (0.0–1.0)

    Returns:
        True on success, False on failure.
    """
    if not token or not chat_id:
        logger.warning("Telegram alert skipped: token or chat_id not configured.")
        return False

    try:
        text = (
            f"🔥 *InfernoGuard AI Alert*\n\n"
            f"*{detection_type.upper()}* detected with "
            f"*{confidence * 100:.1f}%* confidence.\n\n"
            "Please take immediate action."
        )

        url = TELEGRAM_API_BASE.format(token=token)
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        logger.info(
            "Telegram alert sent to chat_id=%s for %s detection.", chat_id, detection_type
        )
        return True

    except Exception as exc:
        logger.error("Telegram alert failed: %s", exc, exc_info=True)
        return False
