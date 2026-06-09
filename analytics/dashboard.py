"""
Dashboard analytics module for InfernoGuard AI.
Computes summary statistics and recent activity from incident data.
"""

from utils.logger import get_logger

logger = get_logger(__name__)


def get_summary_stats(incidents: list[dict]) -> dict:
    """
    Compute summary statistics from a list of incident records.

    Args:
        incidents: List of incident dicts with keys: id, type, confidence, timestamp, screenshot_path

    Returns:
        dict with keys:
            total_incidents (int)
            fire_count (int)
            smoke_count (int)
            last_detection (str | None) — ISO timestamp of the most recent incident
            avg_confidence (float) — average confidence score
    """
    if not incidents:
        return {
            "total_incidents": 0,
            "fire_count": 0,
            "smoke_count": 0,
            "last_detection": None,
            "avg_confidence": 0.0,
        }

    fire_count = sum(1 for i in incidents if i.get("type", "").lower() == "fire")
    smoke_count = sum(1 for i in incidents if i.get("type", "").lower() == "smoke")

    # Incidents are expected to be ordered newest-first from the DB layer,
    # but we sort defensively to guarantee correctness.
    sorted_incidents = sorted(incidents, key=lambda i: i.get("timestamp", ""), reverse=True)
    last_detection = sorted_incidents[0].get("timestamp") if sorted_incidents else None
    
    # Calculate average confidence
    confidence_scores = [i.get("confidence", 0.0) for i in incidents]
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

    return {
        "total_incidents": len(incidents),
        "fire_count": fire_count,
        "smoke_count": smoke_count,
        "last_detection": last_detection,
        "avg_confidence": avg_confidence,
    }


def get_recent_activity(incidents: list[dict], n: int) -> list[dict]:
    """
    Return the n most recent incidents sorted by timestamp descending.

    Args:
        incidents: List of incident dicts
        n: Maximum number of incidents to return

    Returns:
        List of up to n incident dicts, newest first
    """
    if n <= 0:
        return []

    sorted_incidents = sorted(incidents, key=lambda i: i.get("timestamp", ""), reverse=True)
    return sorted_incidents[:n]
