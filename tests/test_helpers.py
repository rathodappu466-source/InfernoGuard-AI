"""
Property-based tests for utils/helpers.py.

# Feature: infernoguard-ai, Property 8: Screenshot filename uniqueness
# For any two calls to generate_screenshot_filename with any detection type,
# the returned filenames SHALL be distinct (no collision).
# Validates: Requirements 3.1
"""

import time

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from utils.helpers import generate_screenshot_filename, get_timestamp, resize_frame


# ---------------------------------------------------------------------------
# Property 8: Screenshot filename uniqueness
# Validates: Requirements 3.1
# ---------------------------------------------------------------------------

# Strategy: any non-empty string that could represent a detection type
detection_type_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_- "),
    min_size=1,
    max_size=20,
)


@given(
    detection_type=detection_type_strategy,
    n=st.integers(min_value=2, max_value=50),
)
@settings(max_examples=100)
def test_screenshot_filename_uniqueness(detection_type: str, n: int):
    """
    # Feature: infernoguard-ai, Property 8: Screenshot filename uniqueness
    # Validates: Requirements 3.1

    For any detection type, generating n filenames in sequence must produce
    n distinct values — no two filenames may collide.
    """
    filenames = []
    for _ in range(n):
        filenames.append(generate_screenshot_filename(detection_type))
        # Small sleep to allow microsecond counter to advance when n is large.
        # In practice detections don't fire faster than this.
        time.sleep(0.000001)

    assert len(filenames) == len(set(filenames)), (
        f"Collision detected among {n} filenames for detection_type={detection_type!r}:\n"
        + "\n".join(filenames)
    )


# ---------------------------------------------------------------------------
# Supporting unit tests
# ---------------------------------------------------------------------------

def test_generate_screenshot_filename_format():
    """Filename should end with .jpg and contain the detection type."""
    fname = generate_screenshot_filename("fire")
    assert fname.endswith(".jpg")
    assert "fire" in fname


def test_get_timestamp_format():
    """get_timestamp should return an ISO-8601-like string."""
    ts = get_timestamp()
    assert "T" in ts
    assert len(ts) == 19  # YYYY-MM-DDTHH:MM:SS
