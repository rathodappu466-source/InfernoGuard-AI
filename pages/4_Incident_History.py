"""
Incident History page for InfernoGuard AI — Enterprise Edition.
Modern incident cards with severity badges, filter chips, search,
expandable details, AI-generated summaries, screenshot previews,
and export tools.
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import os
import math
import json

import streamlit as st

from auth.session import require_auth
import database.db as db
from history.logs import filter_incidents, export_to_csv
from utils.logger import get_logger
from utils.ui import render_page_footer, render_breadcrumbs

logger = get_logger(__name__)

PAGE_SIZE = 15

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Incident History — InfernoGuard AI",
    page_icon="📋",
    layout="wide",
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
_CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "styles.css")
if os.path.isfile(_CSS_PATH):
    with open(_CSS_PATH, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Auth guard ────────────────────────────────────────────────────────────────
require_auth()

render_breadcrumbs([("Home", "🏠"), ("Incident History", "📋")])


# ── AI Summary Generator ──────────────────────────────────────────────────────
def _generate_ai_summary(inc: dict) -> str:
    """Generate a deterministic AI-style summary for an incident (no external API)."""
    inc_type = inc.get("type", "unknown").lower()
    conf = inc.get("confidence", 0.0)
    ts = inc.get("timestamp", "unknown")

    severity = (
        "critical" if conf >= 0.85
        else "high" if conf >= 0.70
        else "medium" if conf >= 0.50
        else "low"
    )

    type_desc = "fire hazard" if inc_type == "fire" else "smoke presence"
    action = (
        "Immediate evacuation and emergency services notification recommended."
        if severity == "critical"
        else "Prompt investigation and area isolation advised."
        if severity == "high"
        else "Monitor situation and verify with on-site personnel."
        if severity == "medium"
        else "Low-priority review recommended during next inspection."
    )

    fire_note = (
        "Fire suppression systems should be activated if not already triggered."
        if inc_type == "fire" and severity in ("critical", "high")
        else ""
    )
    smoke_note = (
        "Ventilation systems should be checked and smoke source identified."
        if inc_type == "smoke"
        else ""
    )

    parts = [
        f"AI detected {type_desc} at {ts} with {conf:.1%} confidence ({severity.upper()} severity).",
        action,
    ]
    if fire_note:
        parts.append(fire_note)
    if smoke_note:
        parts.append(smoke_note)

    return " ".join(parts)


# ── Severity helper ───────────────────────────────────────────────────────────
def _severity(conf: float) -> tuple[str, str]:
    """Return (level_label, css_class) for a confidence score."""
    if conf >= 0.85:
        return "CRITICAL", "ig-severity-critical"
    if conf >= 0.70:
        return "HIGH", "ig-severity-high"
    if conf >= 0.50:
        return "MEDIUM", "ig-severity-medium"
    return "LOW", "ig-severity-low"


# ── Main render ───────────────────────────────────────────────────────────────
try:
    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="ig-history-header">
          <div>
            <div class="ig-history-badge">📋 INCIDENT MANAGEMENT CENTER</div>
            <h1 class="ig-history-title">Incident History</h1>
            <p class="ig-history-subtitle">Full audit trail &bull; AI analysis &bull; Export tools</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Load all incidents ────────────────────────────────────────────────────
    all_incidents = db.get_all_incidents()

    # ── Summary stats (computed from ALL incidents before filtering) ──────────
    total_count = len(all_incidents)
    fire_count = sum(1 for i in all_incidents if i.get("type", "").lower() == "fire")
    smoke_count = sum(1 for i in all_incidents if i.get("type", "").lower() == "smoke")
    avg_conf = (
        sum(i.get("confidence", 0.0) for i in all_incidents) / total_count
        if total_count > 0
        else 0.0
    )

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.markdown(
            f"""
            <div class="ig-history-stat-card">
              <div class="ig-history-stat-value">{total_count}</div>
              <div class="ig-history-stat-label">Total Incidents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with stat_col2:
        st.markdown(
            f"""
            <div class="ig-history-stat-card">
              <div class="ig-history-stat-value fire">{fire_count}</div>
              <div class="ig-history-stat-label">🔥 Fire Incidents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with stat_col3:
        st.markdown(
            f"""
            <div class="ig-history-stat-card">
              <div class="ig-history-stat-value">{smoke_count}</div>
              <div class="ig-history-stat-label">💨 Smoke Incidents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with stat_col4:
        st.markdown(
            f"""
            <div class="ig-history-stat-card">
              <div class="ig-history-stat-value">{avg_conf:.1%}</div>
              <div class="ig-history-stat-label">Avg Confidence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ig-divider"></div>', unsafe_allow_html=True)

    # ── Session state defaults ────────────────────────────────────────────────
    if "history_type_filter" not in st.session_state:
        st.session_state["history_type_filter"] = "all"
    if "history_search" not in st.session_state:
        st.session_state["history_search"] = ""

    # ── Search bar ────────────────────────────────────────────────────────────
    search = st.text_input(
        "🔍 Search incidents",
        value=st.session_state["history_search"],
        placeholder="Search incidents by type, timestamp...",
        key="history_search_input",
    )
    st.session_state["history_search"] = search

    # ── Filter chips (3 buttons in columns) ───────────────────────────────────
    active_filter = st.session_state["history_type_filter"]

    chip_col1, chip_col2, chip_col3, _spacer = st.columns([1, 1, 1, 5])
    with chip_col1:
        all_label = "✓ All" if active_filter == "all" else "All"
        if st.button(all_label, key="chip_all", use_container_width=True):
            st.session_state["history_type_filter"] = "all"
            st.rerun()
    with chip_col2:
        fire_label = "✓ 🔥 Fire" if active_filter == "fire" else "🔥 Fire"
        if st.button(fire_label, key="chip_fire", use_container_width=True):
            st.session_state["history_type_filter"] = "fire"
            st.rerun()
    with chip_col3:
        smoke_label = "✓ 💨 Smoke" if active_filter == "smoke" else "💨 Smoke"
        if st.button(smoke_label, key="chip_smoke", use_container_width=True):
            st.session_state["history_type_filter"] = "smoke"
            st.rerun()

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = filter_incidents(
        all_incidents,
        search=st.session_state["history_search"],
        type_filter=st.session_state["history_type_filter"],
    )

    # ── Export tools ──────────────────────────────────────────────────────────
    export_col1, export_col2, _export_spacer = st.columns([1, 1, 4])
    with export_col1:
        csv_data = export_to_csv(filtered)
        st.download_button(
            label="⬇ Export CSV",
            data=csv_data,
            file_name="incidents.csv",
            mime="text/csv",
            key="export_csv_btn",
            use_container_width=True,
        )
    with export_col2:
        json_data = json.dumps(filtered, indent=2, default=str)
        st.download_button(
            label="⬇ Export JSON",
            data=json_data,
            file_name="incidents.json",
            mime="application/json",
            key="export_json_btn",
            use_container_width=True,
        )

    st.markdown('<div class="ig-divider"></div>', unsafe_allow_html=True)

    # ── Empty state ───────────────────────────────────────────────────────────
    if not filtered:
        st.markdown(
            """
            <div class="ig-history-empty">
              <div class="ig-history-empty-icon">📋</div>
              <div class="ig-history-empty-title">No Incidents Found</div>
              <div class="ig-history-empty-desc">
                No incidents match your current filters. Try adjusting the search or filter criteria.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # ── Pagination ────────────────────────────────────────────────────────
        total = len(filtered)
        total_pages = max(1, math.ceil(total / PAGE_SIZE))

        page = st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            key="history_page",
        )
        start = (page - 1) * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)
        page_incidents = filtered[start:end]

        st.markdown(
            f"""
            <div class="ig-pagination-info">
              Showing {start + 1}–{end} of {total} incidents &bull; Page {page} of {total_pages}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Incident cards ────────────────────────────────────────────────────
        for idx, inc in enumerate(page_incidents):
            inc_type = inc.get("type", "unknown").lower()
            badge_class = "fire" if inc_type == "fire" else "smoke"
            type_label = inc_type.upper()
            type_emoji = "🔥" if inc_type == "fire" else "💨"
            conf = inc.get("confidence", 0.0)
            ts = inc.get("timestamp", "—")
            screenshot = inc.get("screenshot_path", "")
            inc_id = inc.get("id", start + idx + 1)

            sev_label, sev_class = _severity(conf)
            ai_summary = _generate_ai_summary(inc)

            # Expander label (always visible)
            expander_label = (
                f"[{type_emoji} {type_label}]  |  {conf:.1%} confidence  |  {ts}"
            )

            with st.expander(expander_label, expanded=False):
                # Card body: details + screenshot side by side
                detail_col, screenshot_col = st.columns([3, 2])

                with detail_col:
                    st.markdown(
                        f"""
                        <div class="ig-incident-details">
                          <div class="ig-incident-detail-row">
                            <span class="ig-incident-detail-label">Detection Type</span>
                            <span class="ig-badge {badge_class}">{type_label}</span>
                          </div>
                          <div class="ig-incident-detail-row">
                            <span class="ig-incident-detail-label">Confidence Score</span>
                            <span class="ig-incident-detail-value">{conf:.1%}</span>
                          </div>
                          <div class="ig-incident-detail-row">
                            <span class="ig-incident-detail-label">Timestamp</span>
                            <span class="ig-incident-detail-value ig-mono">{ts}</span>
                          </div>
                          <div class="ig-incident-detail-row">
                            <span class="ig-incident-detail-label">Severity</span>
                            <span class="ig-severity-badge {sev_class}">{sev_label}</span>
                          </div>
                          <div class="ig-incident-detail-row">
                            <span class="ig-incident-detail-label">Incident ID</span>
                            <span class="ig-incident-detail-value ig-mono">#{inc_id}</span>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with screenshot_col:
                    if screenshot and os.path.isfile(str(screenshot)):
                        st.image(screenshot, use_container_width=True)
                    else:
                        st.markdown(
                            """
                            <div class="ig-screenshot-placeholder">
                              📷<br>No screenshot available
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                # AI summary below the two columns
                st.markdown(
                    f"""
                    <div class="ig-ai-summary">
                      <div class="ig-ai-summary-header">🤖 AI Analysis</div>
                      <div class="ig-ai-summary-text">{ai_summary}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    render_page_footer("Incident History")

except Exception:
    logger.exception("Incident History page error")
    st.error("An error occurred while loading incident history. Please try again.")
