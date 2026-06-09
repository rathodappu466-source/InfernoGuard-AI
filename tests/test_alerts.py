"""
Property-based tests for alerts/cooldown.py.

# Feature: infernoguard-ai, Property 3: Alert cooldown suppression
# For any sequence of detection events of the same type occurring within the
# cooldown window, only the first event SHALL trigger an alert dispatch;
# all subsequent events within the window SHALL be suppressed.
# Validates: Requirements 3.6
"""

import time

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from alerts.cooldown import should_alert, record_alert, reset_all_cooldowns


# ---------------------------------------------------------------------------
# Property 3: Alert cooldown suppression
# Validates: Requirements 3.6
# ---------------------------------------------------------------------------

detection_type_strategy = st.sampled_from(["fire", "smoke"])

# Number of rapid follow-up events (all within the cooldown window)
followup_count_strategy = st.integers(min_value=1, max_value=20)

# Cooldown window in seconds — large enough that no real time passes through it
cooldown_strategy = st.integers(min_value=5, max_value=300)


@given(
    detection_type=detection_type_strategy,
    followup_count=followup_count_strategy,
    cooldown_seconds=cooldown_strategy,
)
@settings(max_examples=100)
def test_cooldown_suppresses_duplicate_alerts(
    detection_type: str,
    followup_count: int,
    cooldown_seconds: int,
):
    """
    # Feature: infernoguard-ai, Property 3: Alert cooldown suppression
    # Validates: Requirements 3.6

    For any detection type and cooldown window, after the first alert is
    recorded, all subsequent should_alert() calls within the same window
    SHALL return False (suppressed).
    """
    reset_all_cooldowns()

    # First event: should be allowed
    assert should_alert(detection_type, cooldown_seconds=cooldown_seconds), (
        "First alert should always be allowed (no prior record)."
    )
    record_alert(detection_type)

    # All follow-up events within the same cooldown window must be suppressed
    for i in range(followup_count):
        assert not should_alert(detection_type, cooldown_seconds=cooldown_seconds), (
            f"Follow-up alert #{i + 1} should be suppressed within the cooldown window "
            f"(cooldown={cooldown_seconds}s, type={detection_type!r})."
        )


# ---------------------------------------------------------------------------
# Supporting unit tests
# ---------------------------------------------------------------------------

def test_first_alert_always_allowed():
    """With no prior record, should_alert must return True."""
    reset_all_cooldowns()
    assert should_alert("fire", cooldown_seconds=30)
    assert should_alert("smoke", cooldown_seconds=30)


def test_different_types_are_independent():
    """Cooldown for 'fire' must not suppress 'smoke' alerts and vice versa."""
    reset_all_cooldowns()
    record_alert("fire")
    # smoke has no record yet — must be allowed
    assert should_alert("smoke", cooldown_seconds=300)


def test_alert_allowed_after_cooldown_expires():
    """After the cooldown window passes, should_alert must return True again."""
    reset_all_cooldowns()
    record_alert("fire")
    # Use a 0-second cooldown so it expires immediately
    assert should_alert("fire", cooldown_seconds=0)
