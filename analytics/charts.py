"""
Plotly chart factory for InfernoGuard AI analytics pages.
All functions accept a list of incident dicts and return a plotly Figure.
"""

from datetime import datetime, timedelta
from collections import defaultdict

import plotly.graph_objects as go
import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)

# ── Enterprise color palette ──────────────────────────────────────────────────
FIRE_COLOR  = "#FF4500"
SMOKE_COLOR = "#00D4FF"
BG_PAPER    = "rgba(0,0,0,0)"
BG_PLOT     = "rgba(5,5,20,0.6)"
GRID_COLOR  = "rgba(0,212,255,0.08)"
ZERO_COLOR  = "rgba(0,212,255,0.15)"
FONT_COLOR  = "#eef0ff"
FONT_FAMILY = "Inter, sans-serif"

_AXIS_STYLE = dict(
    gridcolor=GRID_COLOR,
    zerolinecolor=ZERO_COLOR,
    showgrid=True,
    color=FONT_COLOR,
)

_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=BG_PAPER,
    plot_bgcolor=BG_PLOT,
    font=dict(color=FONT_COLOR, family=FONT_FAMILY),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=_AXIS_STYLE,
    yaxis=_AXIS_STYLE,
    hoverlabel=dict(
        bgcolor="#0a0a1a",
        bordercolor="#00d4ff",
        font_color="#eef0ff",
        font_family=FONT_FAMILY,
    ),
    legend=dict(
        bgcolor="rgba(10,10,28,0.8)",
        bordercolor="rgba(0,212,255,0.2)",
        borderwidth=1,
        font=dict(color=FONT_COLOR),
    ),
    title_font=dict(size=14, color=FONT_COLOR, family=FONT_FAMILY),
)


def _empty_figure(message: str = "No data available") -> go.Figure:
    """Return a blank figure with a centred annotation."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color=FONT_COLOR),
    )
    fig.update_layout(**_LAYOUT_DEFAULTS)
    return fig


def confidence_trend_chart(incidents: list[dict]) -> go.Figure:
    """
    Time-series line chart of detection confidence scores over the most recent incidents.
    Requirements: 4.3
    """
    if not incidents:
        return _empty_figure()

    sorted_inc = sorted(incidents, key=lambda i: i.get("timestamp", ""))
    timestamps  = [i.get("timestamp", "") for i in sorted_inc]
    confidences = [i.get("confidence", 0.0) for i in sorted_inc]
    types       = [i.get("type", "") for i in sorted_inc]

    colors = [FIRE_COLOR if t.lower() == "fire" else SMOKE_COLOR for t in types]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=confidences,
        mode="lines+markers",
        marker=dict(color=colors, size=8),
        line=dict(color=SMOKE_COLOR, width=2),
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.08)",
        name="Confidence",
        hovertemplate="<b>%{x}</b><br>Confidence: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        title="Detection Confidence Trend",
        xaxis_title="Timestamp",
        yaxis_title="Confidence Score",
        yaxis=dict(range=[0, 1], **_AXIS_STYLE),
        **{k: v for k, v in _LAYOUT_DEFAULTS.items() if k not in ("yaxis",)},
    )
    return fig


def incident_frequency_chart(incidents: list[dict]) -> go.Figure:
    """
    Bar chart of incident counts grouped by detection type.
    Requirements: 4.4
    """
    if not incidents:
        return _empty_figure()

    fire_count  = sum(1 for i in incidents if i.get("type", "").lower() == "fire")
    smoke_count = sum(1 for i in incidents if i.get("type", "").lower() == "smoke")

    fig = go.Figure(data=[
        go.Bar(
            name="Fire",
            x=["Fire"],
            y=[fire_count],
            marker_color=FIRE_COLOR,
            marker_line_color="rgba(0,212,255,0.3)",
            marker_line_width=1,
        ),
        go.Bar(
            name="Smoke",
            x=["Smoke"],
            y=[smoke_count],
            marker_color=SMOKE_COLOR,
            marker_line_color="rgba(0,212,255,0.3)",
            marker_line_width=1,
        ),
    ])
    fig.update_layout(
        title="Incident Frequency by Type",
        xaxis_title="Detection Type",
        yaxis_title="Count",
        barmode="group",
        showlegend=False,
        **_LAYOUT_DEFAULTS,
    )
    return fig


def pie_chart(incidents: list[dict]) -> go.Figure:
    """
    Pie chart showing proportion of fire vs smoke incidents.
    Requirements: 5.1
    """
    if not incidents:
        return _empty_figure()

    fire_count  = sum(1 for i in incidents if i.get("type", "").lower() == "fire")
    smoke_count = sum(1 for i in incidents if i.get("type", "").lower() == "smoke")

    if fire_count == 0 and smoke_count == 0:
        return _empty_figure()

    fig = go.Figure(data=[go.Pie(
        labels=["Fire", "Smoke"],
        values=[fire_count, smoke_count],
        marker=dict(
            colors=[FIRE_COLOR, SMOKE_COLOR],
            line=dict(color="#05050f", width=2),
        ),
        hole=0.4,
        textfont=dict(color=FONT_COLOR),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    )])
    fig.update_layout(
        title="Fire vs Smoke Distribution",
        **_LAYOUT_DEFAULTS,
    )
    return fig


def weekly_trend_chart(incidents: list[dict]) -> go.Figure:
    """
    Line chart of weekly incident counts for the past 8 weeks.
    Requirements: 5.2
    """
    if not incidents:
        return _empty_figure()

    now = datetime.utcnow()
    week_counts: dict[str, int] = {}

    for week_offset in range(7, -1, -1):
        week_start = now - timedelta(weeks=week_offset + 1)
        week_end   = now - timedelta(weeks=week_offset)
        label = week_start.strftime("W%W %b %d")
        count = sum(
            1 for i in incidents
            if _parse_ts(i.get("timestamp", "")) is not None
            and week_start <= _parse_ts(i["timestamp"]) < week_end
        )
        week_counts[label] = count

    labels = list(week_counts.keys())
    values = list(week_counts.values())

    fig = go.Figure(data=[go.Scatter(
        x=labels,
        y=values,
        mode="lines+markers",
        line=dict(color=SMOKE_COLOR, width=2),
        marker=dict(color=SMOKE_COLOR, size=8),
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.08)",
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
    )])
    fig.update_layout(
        title="Weekly Incident Trend (Past 8 Weeks)",
        xaxis_title="Week",
        yaxis_title="Incident Count",
        **_LAYOUT_DEFAULTS,
    )
    return fig


def monthly_trend_chart(incidents: list[dict]) -> go.Figure:
    """
    Bar chart of monthly incident counts for the past 12 months.
    Requirements: 5.3
    """
    if not incidents:
        return _empty_figure()

    now = datetime.utcnow()
    month_counts: dict[str, int] = {}

    for month_offset in range(11, -1, -1):
        target = now - timedelta(days=30 * month_offset)
        label  = target.strftime("%b %Y")
        count  = sum(
            1 for i in incidents
            if _parse_ts(i.get("timestamp", "")) is not None
            and _parse_ts(i["timestamp"]).strftime("%b %Y") == label
        )
        month_counts[label] = count

    labels = list(month_counts.keys())
    values = list(month_counts.values())

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker_color=FIRE_COLOR,
        marker_line_color="rgba(0,212,255,0.3)",
        marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
    )])
    fig.update_layout(
        title="Monthly Incident Trend (Past 12 Months)",
        xaxis_title="Month",
        yaxis_title="Incident Count",
        **_LAYOUT_DEFAULTS,
    )
    return fig


def confidence_comparison_chart(incidents: list[dict]) -> go.Figure:
    """
    Bar chart comparing average confidence scores between fire and smoke.
    Requirements: 5.4
    """
    if not incidents:
        return _empty_figure()

    fire_confs  = [i.get("confidence", 0.0) for i in incidents if i.get("type", "").lower() == "fire"]
    smoke_confs = [i.get("confidence", 0.0) for i in incidents if i.get("type", "").lower() == "smoke"]

    fire_avg  = sum(fire_confs)  / len(fire_confs)  if fire_confs  else 0.0
    smoke_avg = sum(smoke_confs) / len(smoke_confs) if smoke_confs else 0.0

    fig = go.Figure(data=[
        go.Bar(
            name="Fire",
            x=["Fire"],
            y=[fire_avg],
            marker_color=FIRE_COLOR,
            marker_line_color="rgba(0,212,255,0.3)",
            marker_line_width=1,
        ),
        go.Bar(
            name="Smoke",
            x=["Smoke"],
            y=[smoke_avg],
            marker_color=SMOKE_COLOR,
            marker_line_color="rgba(0,212,255,0.3)",
            marker_line_width=1,
        ),
    ])
    fig.update_layout(
        title="Average Confidence Score by Detection Type",
        xaxis_title="Detection Type",
        yaxis_title="Average Confidence",
        yaxis=dict(range=[0, 1], **_AXIS_STYLE),
        barmode="group",
        showlegend=False,
        **{k: v for k, v in _LAYOUT_DEFAULTS.items() if k not in ("yaxis",)},
    )
    return fig


# ── New enterprise chart functions ────────────────────────────────────────────

def risk_heatmap_chart(incidents: list[dict]) -> go.Figure:
    """
    Heatmap of incident frequency by hour of day vs day of week.
    Rows = days of week (Mon–Sun), Columns = hours (0–23).
    """
    if not incidents:
        return _empty_figure("No data for risk heatmap")

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = list(range(24))

    # Build a 7×24 matrix (day × hour)
    matrix = [[0] * 24 for _ in range(7)]

    for inc in incidents:
        ts = _parse_ts(inc.get("timestamp", ""))
        if ts is None:
            continue
        day_idx  = ts.weekday()   # 0=Mon … 6=Sun
        hour_idx = ts.hour
        matrix[day_idx][hour_idx] += 1

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[f"{h:02d}:00" for h in hours],
        y=days_of_week,
        colorscale=[
            [0.0,  "rgba(5,5,20,0.6)"],
            [0.33, "rgba(0,85,255,0.5)"],
            [0.66, "rgba(255,106,0,0.7)"],
            [1.0,  "#FF2D2D"],
        ],
        hovertemplate="<b>%{y} %{x}</b><br>Incidents: %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(
            title="Incidents",
            titlefont=dict(color=FONT_COLOR),
            tickfont=dict(color=FONT_COLOR),
            bgcolor="rgba(10,10,28,0.8)",
            bordercolor="rgba(0,212,255,0.2)",
        ),
    ))
    fig.update_layout(
        title="Risk Heatmap — Hour of Day vs Day of Week",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        **_LAYOUT_DEFAULTS,
    )
    return fig


def detection_velocity_chart(incidents: list[dict]) -> go.Figure:
    """
    Area chart showing detection rate (incidents per hour) over the last 24 hours.
    """
    if not incidents:
        return _empty_figure("No data for detection velocity")

    now = datetime.utcnow()
    cutoff = now - timedelta(hours=24)

    # Bucket incidents into 24 hourly slots
    hour_counts = defaultdict(int)
    for inc in incidents:
        ts = _parse_ts(inc.get("timestamp", ""))
        if ts is None or ts < cutoff:
            continue
        # Slot = hours ago (0 = most recent hour)
        hours_ago = int((now - ts).total_seconds() // 3600)
        if 0 <= hours_ago < 24:
            hour_counts[hours_ago] += 1

    # Build ordered series: oldest → newest
    x_labels = []
    y_values = []
    for h in range(23, -1, -1):
        slot_time = now - timedelta(hours=h)
        x_labels.append(slot_time.strftime("%H:%M"))
        y_values.append(hour_counts.get(h, 0))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=y_values,
        mode="lines+markers",
        line=dict(color=FIRE_COLOR, width=2),
        marker=dict(color=FIRE_COLOR, size=6),
        fill="tozeroy",
        fillcolor="rgba(255,69,0,0.12)",
        name="Incidents/hr",
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title="Detection Velocity — Last 24 Hours",
        xaxis_title="Time",
        yaxis_title="Incidents per Hour",
        **_LAYOUT_DEFAULTS,
    )
    return fig


# ── Internal helpers ──────────────────────────────────────────────────────────

def _parse_ts(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp string; return None on failure."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(ts, fmt)
        except (ValueError, TypeError):
            continue
    return None
