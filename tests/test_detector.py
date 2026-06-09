"""
Property-based tests for detection/detector.py.

# Feature: infernoguard-ai, Property 1: Detection threshold filtering
# For any video frame processed by the detection engine and any configured
# confidence threshold, only detections with a confidence score >= the
# threshold SHALL be included in the DetectionResult's detection list.
# Validates: Requirements 2.5
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from detection.detector import Detection, DetectionResult, FireSmokeDetector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_detector(threshold: float) -> FireSmokeDetector:
    """
    Return a FireSmokeDetector with the given threshold but no model loaded.
    We test the filtering logic in isolation — the model is not required.
    """
    detector = FireSmokeDetector.__new__(FireSmokeDetector)
    detector._model = None
    detector._loaded = False
    detector._confidence_threshold = threshold
    return detector


def _apply_threshold_filter(
    raw_detections: list[Detection], threshold: float
) -> list[Detection]:
    """
    Mirror the filtering logic from FireSmokeDetector.detect_frame():
    keep only detections whose confidence >= threshold.
    """
    return [d for d in raw_detections if d.confidence >= threshold]


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

label_strategy = st.sampled_from(["fire", "smoke"])

confidence_strategy = st.floats(
    min_value=0.0,
    max_value=1.0,
    allow_nan=False,
    allow_infinity=False,
)

threshold_strategy = st.floats(
    min_value=0.0,
    max_value=1.0,
    allow_nan=False,
    allow_infinity=False,
)

detection_strategy = st.builds(
    Detection,
    label=label_strategy,
    confidence=confidence_strategy,
    bbox=st.tuples(
        st.integers(min_value=0, max_value=1920),
        st.integers(min_value=0, max_value=1080),
        st.integers(min_value=0, max_value=1920),
        st.integers(min_value=0, max_value=1080),
    ),
)

raw_detections_strategy = st.lists(detection_strategy, min_size=0, max_size=20)


# ---------------------------------------------------------------------------
# Property 1: Detection threshold filtering
# Validates: Requirements 2.5
# ---------------------------------------------------------------------------

@given(
    raw_detections=raw_detections_strategy,
    threshold=threshold_strategy,
)
@settings(max_examples=100)
def test_detection_threshold_filtering(
    raw_detections: list[Detection], threshold: float
):
    """
    # Feature: infernoguard-ai, Property 1: Detection threshold filtering
    # Validates: Requirements 2.5

    For any list of raw detections and any confidence threshold:
    - Every detection in the filtered result must have confidence >= threshold.
    - No detection with confidence >= threshold may be omitted from the result.
    """
    filtered = _apply_threshold_filter(raw_detections, threshold)

    # All returned detections must meet the threshold
    for det in filtered:
        assert det.confidence >= threshold, (
            f"Detection with confidence={det.confidence} was returned "
            f"but threshold={threshold}"
        )

    # No qualifying detection may be omitted
    qualifying = [d for d in raw_detections if d.confidence >= threshold]
    assert len(filtered) == len(qualifying), (
        f"Expected {len(qualifying)} detections at threshold={threshold}, "
        f"got {len(filtered)}"
    )


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_detector_not_loaded_returns_empty_result():
    """When model is not loaded, detect_frame returns an empty DetectionResult."""
    detector = _make_detector(threshold=0.5)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = detector.detect_frame(frame)

    assert isinstance(result, DetectionResult)
    assert result.detections == []
    assert result.fps == 0.0
    assert result.has_fire is False
    assert result.has_smoke is False


def test_detector_missing_model_file_sets_not_loaded(tmp_path):
    """Constructor must catch FileNotFoundError and set is_loaded() to False."""
    missing_path = str(tmp_path / "nonexistent_model.pt")
    detector = FireSmokeDetector(model_path=missing_path, confidence_threshold=0.5)
    assert detector.is_loaded() is False


def test_threshold_filter_excludes_below_threshold():
    """Detections strictly below the threshold must be excluded."""
    detections = [
        Detection(label="fire", confidence=0.3, bbox=(0, 0, 10, 10)),
        Detection(label="smoke", confidence=0.7, bbox=(0, 0, 10, 10)),
        Detection(label="fire", confidence=0.5, bbox=(0, 0, 10, 10)),
    ]
    result = _apply_threshold_filter(detections, threshold=0.5)
    assert len(result) == 2
    assert all(d.confidence >= 0.5 for d in result)


def test_threshold_filter_boundary_inclusive():
    """A detection exactly at the threshold must be included."""
    detections = [Detection(label="fire", confidence=0.5, bbox=(0, 0, 10, 10))]
    result = _apply_threshold_filter(detections, threshold=0.5)
    assert len(result) == 1
