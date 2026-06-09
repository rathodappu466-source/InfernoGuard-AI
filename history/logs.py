"""
Incident history filtering and CSV export for InfernoGuard AI.
"""

import csv
import io

from utils.logger import get_logger

logger = get_logger(__name__)


def filter_incidents(incidents: list[dict], search: str, type_filter: str) -> list[dict]:
    """
    Filter incidents by a free-text search term and/or detection type.

    Args:
        incidents:   List of incident dicts (keys: id, type, confidence, timestamp, screenshot_path)
        search:      Free-text string; an incident matches if its type or timestamp contains
                     this string (case-insensitive). Empty string matches everything.
        type_filter: One of 'fire', 'smoke', or 'all' (case-insensitive).
                     'all' disables type filtering.

    Returns:
        Filtered list of incident dicts preserving original order.
    """
    search_lower = search.strip().lower()
    type_lower = type_filter.strip().lower()

    result = []
    for incident in incidents:
        inc_type = incident.get("type", "").lower()
        inc_ts = incident.get("timestamp", "").lower()

        # Type filter
        if type_lower not in ("all", "") and inc_type != type_lower:
            continue

        # Search filter
        if search_lower and search_lower not in inc_type and search_lower not in inc_ts:
            continue

        result.append(incident)

    return result


def export_to_csv(incidents: list[dict]) -> str:
    """
    Serialize a list of incident dicts to a CSV string.

    The CSV includes a header row followed by one data row per incident.
    Columns: id, type, confidence, timestamp, screenshot_path

    Args:
        incidents: List of incident dicts

    Returns:
        CSV-formatted string (UTF-8)
    """
    output = io.StringIO()
    fieldnames = ["id", "type", "confidence", "timestamp", "screenshot_path"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for incident in incidents:
        writer.writerow({
            "id": incident.get("id", ""),
            "type": incident.get("type", ""),
            "confidence": incident.get("confidence", ""),
            "timestamp": incident.get("timestamp", ""),
            "screenshot_path": incident.get("screenshot_path", ""),
        })
    return output.getvalue()
