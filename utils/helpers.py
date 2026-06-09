"""
Shared utility helpers for InfernoGuard AI.
"""

import os
from datetime import datetime, timezone

import numpy as np


def get_timestamp() -> str:
    """Return the current UTC timestamp as an ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def generate_screenshot_filename(detection_type: str) -> str:
    """
    Generate a unique, timestamped filename for a detection screenshot.

    The filename format is:
        {detection_type}_{YYYYMMDD}_{HHMMSS}_{microseconds}.jpg

    The microsecond component ensures uniqueness even when two detections
    occur within the same second.
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    unique_suffix = f"{now.microsecond:06d}"
    safe_type = detection_type.lower().replace(" ", "_")
    return f"{safe_type}_{timestamp}_{unique_suffix}.jpg"


def resize_frame(frame: np.ndarray, width: int) -> np.ndarray:
    """
    Resize a video frame to the given width while preserving the aspect ratio.
    Returns the original frame unchanged if width is not positive.
    """
    import cv2  # imported here to keep cv2 optional at module load time

    if width <= 0:
        return frame

    h, w = frame.shape[:2]
    if w == 0:
        return frame

    aspect_ratio = h / w
    new_height = int(width * aspect_ratio)
    return cv2.resize(frame, (width, new_height), interpolation=cv2.INTER_AREA)
