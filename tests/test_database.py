"""
Property-based tests for database/db.py.

# Feature: infernoguard-ai, Property 2: Incident persistence round trip
# For any valid DetectionResult that triggers an incident log, serializing the
# incident to the SQLite database and then reading it back SHALL produce a
# record with equivalent type, confidence, and timestamp values.
# Validates: Requirements 3.2

# Feature: infernoguard-ai, Property 5: Settings persistence round trip
# For any settings value written via update_settings, reading it back via
# get_settings SHALL return the same value.
# Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
"""

import os
import tempfile

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import database.db as db
from utils.helpers import get_timestamp


# ---------------------------------------------------------------------------
# Fixtures — each test gets an isolated in-memory / temp-file database
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """
    Redirect DB_PATH to a fresh temporary file for every test so tests are
    fully isolated and do not touch the real database.
    """
    test_db = str(tmp_path / "test_infernoguard.db")
    monkeypatch.setattr(db, "DB_PATH", test_db)

    # Also patch the import inside db.py's get_connection closure
    import database.db as _db
    original_get_connection = _db.get_connection

    import sqlite3

    def patched_get_connection():
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(_db, "get_connection", patched_get_connection)
    _db.init_db()
    yield


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

incident_type_strategy = st.sampled_from(["fire", "smoke"])

confidence_strategy = st.floats(
    min_value=0.0,
    max_value=1.0,
    allow_nan=False,
    allow_infinity=False,
)

timestamp_strategy = st.from_regex(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
    fullmatch=True,
)

screenshot_strategy = st.one_of(st.just(""), st.text(min_size=1, max_size=100))

# Settings keys and their value strategies
SETTINGS_STRATEGIES = {
    "alert_enabled":        st.integers(min_value=0, max_value=1),
    "sound_enabled":        st.integers(min_value=0, max_value=1),
    "email_enabled":        st.integers(min_value=0, max_value=1),
    "telegram_enabled":     st.integers(min_value=0, max_value=1),
    "confidence_threshold": st.floats(min_value=0.0, max_value=1.0,
                                      allow_nan=False, allow_infinity=False),
    "email_recipient":      st.text(max_size=100),
    "email_sender":         st.text(max_size=100),
    "smtp_host":            st.text(min_size=1, max_size=100),
    "smtp_port":            st.integers(min_value=1, max_value=65535),
    "rtsp_url":             st.text(max_size=200),
    "telegram_token":       st.text(max_size=100),
    "telegram_chat_id":     st.text(max_size=50),
}


# ---------------------------------------------------------------------------
# Property 2: Incident persistence round trip
# Validates: Requirements 3.2
# ---------------------------------------------------------------------------

@given(
    incident_type=incident_type_strategy,
    confidence=confidence_strategy,
    timestamp=timestamp_strategy,
    screenshot_path=screenshot_strategy,
)
@settings(max_examples=100)
def test_incident_persistence_round_trip(incident_type, confidence, timestamp, screenshot_path):
    """
    # Feature: infernoguard-ai, Property 2: Incident persistence round trip
    # Validates: Requirements 3.2

    For any valid incident, writing it to the database and reading it back
    must produce a record with equivalent type, confidence, and timestamp.
    """
    row_id = db.log_incident(incident_type, confidence, timestamp, screenshot_path)
    assert row_id != -1, "log_incident should return a valid row id"

    all_incidents = db.get_all_incidents()
    matching = [i for i in all_incidents if i["id"] == row_id]
    assert len(matching) == 1, "Exactly one incident should match the returned id"

    stored = matching[0]
    assert stored["type"] == incident_type
    assert abs(stored["confidence"] - confidence) < 1e-9
    assert stored["timestamp"] == timestamp


# ---------------------------------------------------------------------------
# Property 5: Settings persistence round trip
# Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
# ---------------------------------------------------------------------------

@given(data=st.data())
@settings(max_examples=100)
def test_settings_persistence_round_trip(data):
    """
    # Feature: infernoguard-ai, Property 5: Settings persistence round trip
    # Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5

    For any settings key and a value drawn from its valid domain, writing the
    value via update_settings and reading it back via get_settings must return
    the same value.
    """
    key = data.draw(st.sampled_from(list(SETTINGS_STRATEGIES.keys())))
    value = data.draw(SETTINGS_STRATEGIES[key])
    
    db.update_settings(key, value)
    stored = db.get_settings()
    assert key in stored, f"Key {key!r} missing from get_settings() result"

    stored_value = stored[key]

    # Floats: allow tiny floating-point rounding from SQLite REAL storage
    if isinstance(value, float):
        assert abs(stored_value - value) < 1e-9, (
            f"Float mismatch for key={key!r}: wrote {value}, got {stored_value}"
        )
    else:
        assert stored_value == value, (
            f"Value mismatch for key={key!r}: wrote {value!r}, got {stored_value!r}"
        )
