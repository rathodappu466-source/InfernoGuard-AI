"""
YOLOv8 fire and smoke detection engine for InfernoGuard AI.

Provides FireSmokeDetector, DetectionResult, and Detection as the core
inference interface consumed by all video-source stream modules.
"""

import time
from dataclasses import dataclass, field

import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Detection:
    """A single detected object within a frame."""
    label: str                          # "fire" or "smoke"
    confidence: float                   # 0.0 – 1.0
    bbox: tuple[int, int, int, int]     # (x1, y1, x2, y2)


@dataclass
class DetectionResult:
    """Aggregated output from processing one video frame."""
    detections: list[Detection]
    annotated_frame: np.ndarray
    fps: float
    has_fire: bool
    has_smoke: bool


class FireSmokeDetector:
    """
    Wraps a YOLOv8 model for fire and smoke inference.

    The model is loaded once at construction time.  If the model file is
    missing the detector degrades gracefully: is_loaded() returns False and
    detect_frame() returns an empty DetectionResult rather than raising.
    """

    def __init__(self, model_path: str, confidence_threshold: float = 0.5) -> None:
        self._model = None
        self._loaded = False
        self._confidence_threshold = confidence_threshold

        try:
            from ultralytics import YOLO  # imported here so the module is
                                          # importable even without ultralytics
            self._model = YOLO(model_path)
            self._loaded = True
            logger.info("YOLOv8 model loaded from %s", model_path)
        except FileNotFoundError:
            logger.error(
                "Model file not found at %s — detection engine disabled.", model_path
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load YOLOv8 model: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_loaded(self) -> bool:
        """Return True if the model was loaded successfully."""
        return self._loaded

    def detect_frame(self, frame: np.ndarray) -> DetectionResult:
        """
        Run inference on a single BGR frame.

        Returns a DetectionResult whose detections list contains only those
        objects whose confidence score is >= the configured threshold.
        FPS is computed from the wall-clock time of this call alone.

        If the model is not loaded, returns an empty DetectionResult with the
        original frame unchanged.
        """
        if not self._loaded or self._model is None:
            return DetectionResult(
                detections=[],
                annotated_frame=frame,
                fps=0.0,
                has_fire=False,
                has_smoke=False,
            )

        t_start = time.perf_counter()

        try:
            results = self._model(frame, verbose=False)
        except Exception as exc:  # noqa: BLE001
            logger.error("Inference error: %s", exc)
            return DetectionResult(
                detections=[],
                annotated_frame=frame,
                fps=0.0,
                has_fire=False,
                has_smoke=False,
            )

        elapsed = time.perf_counter() - t_start
        fps = 1.0 / elapsed if elapsed > 0 else 0.0

        detections: list[Detection] = []
        for result in results:
            annotated_frame = result.plot()  # frame with bounding boxes drawn
            if result.boxes is None:
                continue
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf < self._confidence_threshold:
                    continue  # filter out sub-threshold detections
                cls_id = int(box.cls[0])
                label = (
                    result.names[cls_id].lower()
                    if result.names and cls_id in result.names
                    else str(cls_id)
                )
                x1, y1, x2, y2 = (int(v) for v in box.xyxy[0])
                detections.append(Detection(label=label, confidence=conf, bbox=(x1, y1, x2, y2)))

        has_fire = any(d.label == "fire" for d in detections)
        has_smoke = any(d.label == "smoke" for d in detections)

        # If no results came back (empty list), keep original frame
        if not results:
            annotated_frame = frame

        return DetectionResult(
            detections=detections,
            annotated_frame=annotated_frame,
            fps=fps,
            has_fire=has_fire,
            has_smoke=has_smoke,
        )
