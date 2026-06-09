"""
Webcam video source stream for InfernoGuard AI.

Provides stream_webcam(), a generator that captures frames from the default
webcam (device index 0) and yields DetectionResult objects.
"""

from typing import Generator

import cv2

from detection.detector import DetectionResult, FireSmokeDetector
from utils.logger import get_logger

logger = get_logger(__name__)


def stream_webcam(detector: FireSmokeDetector) -> Generator[DetectionResult, None, None]:
    """
    Capture frames from the default webcam and yield DetectionResult objects.

    Opens cv2.VideoCapture(0). If the device cannot be opened, logs an error
    and returns immediately without yielding. The generator releases the
    capture device when it exits (normally or via GeneratorExit).

    Requirements: 2.1, 2.4
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logger.error("Failed to open webcam (device index 0).")
        return

    logger.info("Webcam stream started.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Webcam: failed to read frame — stopping stream.")
                break
            yield detector.detect_frame(frame)
    finally:
        cap.release()
        logger.info("Webcam stream released.")
