"""
RTSP/IP-camera video source stream for InfernoGuard AI.

Provides stream_rtsp(), a generator that connects to an RTSP stream URL and
yields DetectionResult objects.
"""

from typing import Generator

import cv2

from detection.detector import DetectionResult, FireSmokeDetector
from utils.logger import get_logger

logger = get_logger(__name__)


def stream_rtsp(
    detector: FireSmokeDetector, url: str
) -> Generator[DetectionResult, None, None]:
    """
    Connect to an RTSP stream and yield DetectionResult objects.

    Opens cv2.VideoCapture(url). If the stream cannot be opened, logs an error
    and returns immediately without yielding. The generator releases the
    capture device when it exits (normally or via GeneratorExit).

    Requirements: 2.2, 2.4
    """
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        logger.error("Failed to open RTSP stream: %s", url)
        return

    logger.info("RTSP stream started: %s", url)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("RTSP stream: failed to read frame — stopping stream.")
                break
            yield detector.detect_frame(frame)
    finally:
        cap.release()
        logger.info("RTSP stream released: %s", url)
