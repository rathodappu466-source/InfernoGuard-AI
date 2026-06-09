"""
Uploaded video file source stream for InfernoGuard AI.

Provides stream_video(), a generator that reads frames from a video file and
yields DetectionResult objects.
"""

from typing import Generator

import cv2

from detection.detector import DetectionResult, FireSmokeDetector
from utils.logger import get_logger

logger = get_logger(__name__)


def stream_video(
    detector: FireSmokeDetector, video_path: str
) -> Generator[DetectionResult, None, None]:
    """
    Read frames from a video file and yield DetectionResult objects.

    Opens cv2.VideoCapture(video_path). If the file cannot be opened, logs an
    error and returns immediately without yielding. The generator releases the
    capture device when it exits (normally or via GeneratorExit).

    Requirements: 2.3, 2.4
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        logger.error("Failed to open video file: %s", video_path)
        return

    logger.info("Video file stream started: %s", video_path)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # End of file or read error — either way, stop gracefully
                logger.info("Video file stream ended: %s", video_path)
                break
            yield detector.detect_frame(frame)
    finally:
        cap.release()
        logger.info("Video file stream released: %s", video_path)
