"""
Alert cooldown tracking for InfernoGuard AI.

Prevents duplicate alert dispatches by enforcing a minimum time interval
between consecutive alerts of the same detection type.
"""

import time
from typing import Dict

from utils.config import ALERT_COOLDOWN_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)

# Maps detection_type -> timestamp of last alert dispatch
_last_alert_times: Dict[str, float] = {}


def should_alert(detection_type: str, cooldown_seconds: int = ALERT_COOLDOWN_SECONDS) -> bool:
    """
    Return True if enough time has elapsed since the last alert for this
    detection type, meaning a new alert should be dispatched.

    Args:
        detection_type: 'fire' or 'smoke'
        cooldown_seconds: minimum seconds between alerts (defaults to config value)
    """
    last = _last_alert_times.get(detection_type)
    if last is None:
        return True
    return (time.monotonic() - last) >= cooldown_seconds


def record_alert(detection_type: str) -> None:
    """
    Record that an alert was dispatched for the given detection type,
    resetting the cooldown window.

    Args:
        detection_type: 'fire' or 'smoke'
    """
    _last_alert_times[detection_type] = time.monotonic()
    logger.debug("Alert recorded for type=%s", detection_type)


def reset_cooldown(detection_type: str) -> None:
    """
    Clear the cooldown record for a detection type (used in tests).
    """
    _last_alert_times.pop(detection_type, None)


def reset_all_cooldowns() -> None:
    """
    Clear all cooldown records (used in tests).
    """
    _last_alert_times.clear()
