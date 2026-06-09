"""
Property-based tests for history/logs.py.

Property 6: Incident filter correctness
  For any list of incidents and any type filter value ('fire', 'smoke', or 'all'),
  every incident returned by filter_incidents SHALL match the filter predicate,
  and no matching incident SHALL be omitted.
  Validates: Requirements 6.3

Property 7: CSV export completeness
  For any filtered list of incidents, the CSV string produced by export_to_csv
  SHALL contain exactly as many data rows as the input list, and each row SHALL
  contain the type, confidence, timestamp, and screenshot_path fields.
  Validates: Requirements 6.4
"""

import csv
import io

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from history.logs import filter_incidents, export_to_csv


# ---------------------------------------------------------------------------
# Shared strategies
# ---------------------------------------------------------------------------

_TYPES = ["fire", "smoke"]

incident_strategy = st.fixed_dictionaries({
    "id": st.integers(min_value=1, max_value=10_000),
    "type": st.sampled_from(_TYPES),
    "confidence": st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    "timestamp": st.from_regex(
        r"20[2-3][0-9]-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9]",
        fullmatch=True,
    ),
    "screenshot_path": st.one_of(st.just(""), st.just("/screenshots/fire_20240101_120000_000001.jpg")),
})

incidents_list_strategy = st.lists(incident_strategy, min_size=0, max_size=50)

type_filter_strategy = st.sampled_from(["fire", "smoke", "all"])

search_strategy = st.one_of(
    st.just(""),
    st.sampled_from(["fire", "smoke", "2024", "T12"]),
)


# ---------------------------------------------------------------------------
# Property 6: Incident filter correctness
# Validates: Requirements 6.3
# ---------------------------------------------------------------------------

@given(
    incidents=incidents_list_strategy,
    type_filter=type_filter_strategy,
    search=search_strategy,
)
@settings(max_examples=100)
def test_filter_incidents_correctness(
    incidents: list[dict],
    type_filter: str,
    search: str,
):
    """
    # Feature: infernoguard-ai, Property 6: Incident filter correctness
    # Validates: Requirements 6.3

    For any list of incidents and any type filter / search combination:
    1. Every returned incident must satisfy the type predicate.
    2. Every returned incident must satisfy the search predicate.
    3. No incident that satisfies BOTH predicates may be omitted.
    """
    result = filter_incidents(incidents, search=search, type_filter=type_filter)

    type_lower = type_filter.strip().lower()
    search_lower = search.strip().lower()

    # --- Soundness: every returned incident must match both predicates ---
    for inc in result:
        inc_type = inc.get("type", "").lower()
        inc_ts = inc.get("timestamp", "").lower()

        if type_lower not in ("all", ""):
            assert inc_type == type_lower, (
                f"Returned incident has type {inc_type!r} but filter is {type_lower!r}"
            )

        if search_lower:
            assert search_lower in inc_type or search_lower in inc_ts, (
                f"Returned incident does not match search {search_lower!r}: "
                f"type={inc_type!r}, timestamp={inc_ts!r}"
            )

    # --- Completeness: no qualifying incident may be omitted ---
    result_ids = {inc["id"] for inc in result}
    for inc in incidents:
        inc_type = inc.get("type", "").lower()
        inc_ts = inc.get("timestamp", "").lower()

        type_match = type_lower in ("all", "") or inc_type == type_lower
        search_match = not search_lower or (search_lower in inc_type or search_lower in inc_ts)

        if type_match and search_match:
            assert inc["id"] in result_ids, (
                f"Incident id={inc['id']} (type={inc_type!r}, ts={inc_ts!r}) "
                f"should be in results for filter={type_lower!r}, search={search_lower!r} "
                f"but was omitted."
            )


# ---------------------------------------------------------------------------
# Property 7: CSV export completeness
# Validates: Requirements 6.4
# ---------------------------------------------------------------------------

@given(incidents=incidents_list_strategy)
@settings(max_examples=100)
def test_csv_export_completeness(incidents: list[dict]):
    """
    # Feature: infernoguard-ai, Property 7: CSV export completeness
    # Validates: Requirements 6.4

    For any list of incidents, the CSV produced by export_to_csv must:
    1. Contain exactly len(incidents) data rows (excluding the header).
    2. Each row must contain the type, confidence, timestamp, and screenshot_path fields.
    """
    csv_string = export_to_csv(incidents)

    reader = csv.DictReader(io.StringIO(csv_string))
    rows = list(reader)

    # Row count must match input length
    assert len(rows) == len(incidents), (
        f"CSV has {len(rows)} data rows but input had {len(incidents)} incidents."
    )

    # Each row must contain the required fields with non-None values
    required_fields = {"type", "confidence", "timestamp", "screenshot_path"}
    for i, (row, inc) in enumerate(zip(rows, incidents)):
        for field in required_fields:
            assert field in row, f"Row {i} is missing field {field!r}"
            # Values must round-trip correctly for type and timestamp
        assert row["type"] == inc["type"], f"Row {i} type mismatch"
        assert row["timestamp"] == inc["timestamp"], f"Row {i} timestamp mismatch"
        assert float(row["confidence"]) == pytest.approx(inc["confidence"], abs=1e-9), (
            f"Row {i} confidence mismatch"
        )


# ---------------------------------------------------------------------------
# Supporting unit tests
# ---------------------------------------------------------------------------

def test_filter_all_returns_everything():
    incidents = [
        {"id": 1, "type": "fire", "confidence": 0.9, "timestamp": "2024-01-01T12:00:00", "screenshot_path": ""},
        {"id": 2, "type": "smoke", "confidence": 0.7, "timestamp": "2024-01-02T12:00:00", "screenshot_path": ""},
    ]
    result = filter_incidents(incidents, search="", type_filter="all")
    assert len(result) == 2


def test_filter_by_type_fire():
    incidents = [
        {"id": 1, "type": "fire", "confidence": 0.9, "timestamp": "2024-01-01T12:00:00", "screenshot_path": ""},
        {"id": 2, "type": "smoke", "confidence": 0.7, "timestamp": "2024-01-02T12:00:00", "screenshot_path": ""},
    ]
    result = filter_incidents(incidents, search="", type_filter="fire")
    assert len(result) == 1
    assert result[0]["type"] == "fire"


def test_filter_by_search_term():
    incidents = [
        {"id": 1, "type": "fire", "confidence": 0.9, "timestamp": "2024-01-01T12:00:00", "screenshot_path": ""},
        {"id": 2, "type": "smoke", "confidence": 0.7, "timestamp": "2024-02-01T12:00:00", "screenshot_path": ""},
    ]
    result = filter_incidents(incidents, search="2024-02", type_filter="all")
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_export_empty_list():
    csv_string = export_to_csv([])
    reader = csv.DictReader(io.StringIO(csv_string))
    rows = list(reader)
    assert rows == []


def test_export_contains_header():
    csv_string = export_to_csv([])
    assert "type" in csv_string
    assert "confidence" in csv_string
    assert "timestamp" in csv_string
