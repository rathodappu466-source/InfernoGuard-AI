"""
Analytics page for InfernoGuard AI — Enterprise Edition.
AI-powered safety analytics with predictive modeling and risk assessment.
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import os
from datetime import datetime, timedelta
from collections import defaultdict

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from auth.session import require_auth
import database.db as db
from analytics.charts import (
    pie_chart,
    weekly_trend_chart,
    monthly_trend_chart,
    confidence_comparison_chart,
    confidence_trend_chart,
    incident_frequency_chart,
    risk_heatmap_chart,
    detection_velocity_chart,
)
from utils.logger import get_logger
from utils.ui import render_page_footer, render_breadcrumbs

logger = get_logger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analytics — InfernoGuard AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def _load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "styles.css")
    if os.path.isfile(css_path):
        with open(css_path, encoding='utf-8') as f:
            return f.read()
    return ""

css_content = _load_css()
if css_content:
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# ── Auth guard ────────────────────────────────────────────────────────────────
require_auth()

render_breadcrumbs([("Home", "🏠"), ("Analytics", "📈")])


# ── SESSION STATE INITIALIZATION ──────────────────────────────────────────────
if "analytics_time_range" not in st.session_state:
    st.session_state["analytics_time_range"] = "7d"

# ── Helper: parse timestamp ───────────────────────────────────────────────────
def _parse_ts(ts: str) -> datetime | None:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(ts, fmt)
        except (ValueError, TypeError):
            continue
    return None

# ── Helper: filter incidents by time range ────────────────────────────────────
def _filter_by_time_range(incidents: list[dict], time_range: str) -> list[dict]:
    now = datetime.utcnow()
    if time_range == "24h":
        cutoff = now - timedelta(hours=24)
    elif time_range == "7d":
        cutoff = now - timedelta(days=7)
    elif time_range == "30d":
        cutoff = now - timedelta(days=30)
    else:  # "all"
        return incidents
    
    return [
        i for i in incidents
        if _parse_ts(i.get("timestamp", "")) is not None
        and _parse_ts(i["timestamp"]) >= cutoff
    ]

# ── Helper: compute safety score ─────────────────────────────────────────────
def _compute_safety_score(incidents: list[dict]) -> int:
    if not incidents:
        return 100
    
    fire_count = sum(1 for i in incidents if i.get("type", "").lower() == "fire")
    smoke_count = sum(1 for i in incidents if i.get("type", "").lower() == "smoke")
    
    score = 100
    score -= fire_count * 5
    score -= smoke_count * 2
    
    return max(0, min(100, score))

# ── Helper: compute comprehensive metrics ──────────────────────────────────────
def _compute_metrics(incidents: list[dict]) -> dict:
    if not incidents:
        return {
            "total": 0,
            "fire": 0,
            "smoke": 0,
            "avg_confidence": 0.0,
            "max_confidence": 0.0,
            "min_confidence": 0.0,
            "today": 0,
            "this_week": 0,
            "detection_rate": 0.0,
        }
    
    fire_count = sum(1 for i in incidents if i.get("type", "").lower() == "fire")
    smoke_count = sum(1 for i in incidents if i.get("type", "").lower() == "smoke")
    confidences = [i.get("confidence", 0.0) for i in incidents]
    
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    
    today_incidents = [
        i for i in incidents
        if _parse_ts(i.get("timestamp", "")) is not None
        and _parse_ts(i["timestamp"]) >= today
    ]
    
    week_incidents = [
        i for i in incidents
        if _parse_ts(i.get("timestamp", "")) is not None
        and _parse_ts(i["timestamp"]) >= week_ago
    ]
    
    return {
        "total": len(incidents),
        "fire": fire_count,
        "smoke": smoke_count,
        "avg_confidence": np.mean(confidences) if confidences else 0.0,
        "max_confidence": np.max(confidences) if confidences else 0.0,
        "min_confidence": np.min(confidences) if confidences else 0.0,
        "today": len(today_incidents),
        "this_week": len(week_incidents),
        "detection_rate": round(len(week_incidents) / 7 if week_incidents else 0, 1),
    }

# ── Helper: get risk level based on metrics ────────────────────────────────────
def _get_risk_level(incidents: list[dict]) -> tuple:
    count_24h = len(_filter_by_time_range(incidents, "24h"))
    if count_24h == 0:
        return "LOW", "#00ffcc", "🟢"
    elif count_24h <= 2:
        return "MEDIUM", "#ff6a00", "🟡"
    else:
        return "HIGH", "#ff2d2d", "🔴"

# ── Helper: create metric card HTML ────────────────────────────────────────────
def _metric_card_html(icon: str, label: str, value: str, subtext: str, color: str = "#00d4ff") -> str:
    return f"""
    <div class="ig-metric-card">
        <div class="ig-metric-icon" style="color: {color}; font-size: 1.8rem;">{icon}</div>
        <div class="ig-metric-label">{label}</div>
        <div class="ig-metric-value" style="color: {color};">{value}</div>
        <div class="ig-metric-sub">{subtext}</div>
    </div>
    """


# ── Helper: safety score gauge ────────────────────────────────────────────────
def _safety_score_gauge(score: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Safety Score", "font": {"color": "#eef0ff", "size": 14, "family": "Inter, sans-serif"}},
        number={"font": {"color": "#eef0ff", "size": 36, "family": "Inter, sans-serif"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#eef0ff",
                "tickfont": {"color": "#eef0ff"},
            },
            "bar": {"color": "#00D4FF"},
            "bgcolor": "rgba(5,5,20,0.6)",
            "borderwidth": 1,
            "bordercolor": "rgba(0,212,255,0.2)",
            "steps": [
                {"range": [0,  40], "color": "rgba(255,45,45,0.25)"},
                {"range": [40, 70], "color": "rgba(255,106,0,0.20)"},
                {"range": [70, 100], "color": "rgba(0,255,204,0.15)"},
            ],
            "threshold": {
                "line": {"color": "#00D4FF", "width": 2},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,5,20,0.6)",
        font=dict(color="#eef0ff", family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=40, b=20),
        height=260,
    )
    return fig

# ── Helper: predictive analytics computations ─────────────────────────────────
def _compute_predictive_metrics(incidents: list[dict]) -> dict:
    now = datetime.utcnow()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d  = now - timedelta(days=7)
    cutoff_14d = now - timedelta(days=14)

    recent_24h = [
        i for i in incidents
        if _parse_ts(i.get("timestamp", "")) is not None
        and _parse_ts(i["timestamp"]) >= cutoff_24h
    ]
    last_7d = [
        i for i in incidents
        if _parse_ts(i.get("timestamp", "")) is not None
        and _parse_ts(i["timestamp"]) >= cutoff_7d
    ]
    prior_7d = [
        i for i in incidents
        if _parse_ts(i.get("timestamp", "")) is not None
        and cutoff_14d <= _parse_ts(i["timestamp"]) < cutoff_7d
    ]

    # Predicted risk level
    count_24h = len(recent_24h)
    if count_24h == 0:
        risk_level = "LOW"
        risk_class = "low"
    elif count_24h <= 2:
        risk_level = "MEDIUM"
        risk_class = "medium"
    else:
        risk_level = "HIGH"
        risk_class = "high"

    # Detection velocity (incidents per hour in last 24h)
    velocity = round(count_24h / 24, 1)

    # Peak risk hour
    hour_counts: dict[int, int] = defaultdict(int)
    for i in incidents:
        ts = _parse_ts(i.get("timestamp", ""))
        if ts:
            hour_counts[ts.hour] += 1
    if hour_counts:
        peak_hour = max(hour_counts, key=lambda h: hour_counts[h])
        peak_hour_str = f"{peak_hour:02d}:00"
    else:
        peak_hour = None
        peak_hour_str = "N/A"

    # 7-day forecast
    if len(last_7d) > len(prior_7d):
        forecast = "↑ Increasing"
    elif len(last_7d) < len(prior_7d):
        forecast = "↓ Decreasing"
    else:
        forecast = "→ Stable"

    return {
        "risk_level": risk_level,
        "risk_class": risk_class,
        "velocity": velocity,
        "peak_hour": peak_hour,
        "peak_hour_str": peak_hour_str,
        "forecast": forecast,
        "count_24h": count_24h,
    }

# ── Helper: AI recommendations ────────────────────────────────────────────────
def _compute_recommendations(incidents: list[dict], metrics: dict) -> list[dict]:
    recs = []

    fire_count  = sum(1 for i in incidents if i.get("type", "").lower() == "fire")
    smoke_count = sum(1 for i in incidents if i.get("type", "").lower() == "smoke")
    confs = [i.get("confidence", 0.0) for i in incidents]
    avg_conf = sum(confs) / len(confs) if confs else 0.0

    if fire_count > smoke_count and fire_count > 0:
        recs.append({
            "text": "🔥 Fire incidents dominate — inspect heat sources and electrical panels",
            "priority": "LOW",
            "priority_class": "low",
        })

    if avg_conf > 0.85:
        recs.append({
            "text": "⚡ High confidence detections — model performing optimally",
            "priority": "LOW",
            "priority_class": "low",
        })

    if avg_conf < 0.6 and incidents:
        recs.append({
            "text": "⚠️ Low confidence scores — consider retraining or adjusting threshold",
            "priority": "MEDIUM",
            "priority_class": "medium",
        })

    if metrics["count_24h"] > 3:
        recs.append({
            "text": "🚨 Elevated activity in last 24h — increase patrol frequency",
            "priority": "HIGH",
            "priority_class": "high",
        })

    peak_hour = metrics.get("peak_hour")
    if peak_hour is not None and (peak_hour >= 22 or peak_hour < 6):
        recs.append({
            "text": "🌙 Incidents peak during night hours — enhance overnight monitoring",
            "priority": "LOW",
            "priority_class": "low",
        })

    if not recs:
        recs.append({
            "text": "✅ System performing well — no immediate action needed",
            "priority": "LOW",
            "priority_class": "low",
        })

    recs.append({
        "text": "📊 Review weekly trends to identify recurring patterns",
        "priority": "LOW",
        "priority_class": "low",
    })

    return recs


# ── NEW SECTION: Rich Metrics Overview ───────────────────────────────────────
@st.cache_data(ttl=300)
def _compute_all_metrics(incidents_list: list) -> dict:
    """Cache computed metrics for 5 minutes."""
    return _compute_metrics(incidents_list)


# ── Main render ───────────────────────────────────────────────────────────────
try:
    # Load incidents
    try:
        incidents = db.get_all_incidents()
    except Exception as e:
        logger.error(f"Failed to load incidents: {e}")
        incidents = []
    
    if not incidents:
        st.markdown("""
        <div style="text-align:center; padding: 4rem 2rem; background: var(--bg-card);
                    border: 1px solid var(--border-subtle); border-radius: 1rem;
                    margin-top: 2rem;">
          <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
          <div style="color: var(--text-primary); font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
            No Incident Data Available
          </div>
          <div style="color: var(--text-secondary); font-size: 0.9rem;">
            Start live detection to begin collecting analytics data.
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Compute all metrics
    metrics = _compute_all_metrics(incidents)
    safety_score = _compute_safety_score(incidents)
    risk_level, risk_color, risk_emoji = _get_risk_level(incidents)
    pred_metrics = _compute_predictive_metrics(incidents)
    
    # ── HERO SECTION ─────────────────────────────────────────────────────────
    score_color = "#ff2d2d" if safety_score < 40 else "#ff6a00" if safety_score < 70 else "#00ffcc"
    
    st.markdown(f"""
    <div class="ig-analytics-header">
      <div>
        <div style="color: #00ffcc; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.5rem;">
          🤖 AI ANALYTICS ENGINE
        </div>
        <h1 style="font-size: 2.8rem; font-weight: 900; margin: 0 0 0.5rem 0; color: #eef0ff;">
          AI-Powered Safety Analytics
        </h1>
        <p style="font-size: 1rem; color: rgba(238, 240, 255, 0.65); margin: 0; font-weight: 400;">
          Real-time intelligence • Predictive modeling • Risk assessment • Historical trends
        </p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
        <div style="text-align: center; background: rgba(5, 5, 20, 0.8); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 1rem; padding: 1rem 1.5rem; backdrop-filter: blur(10px);">
          <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: rgba(238, 240, 255, 0.5); margin-bottom: 0.5rem;">Overall Safety Score</div>
          <div style="font-size: 3rem; font-weight: 900; color: {score_color}; text-shadow: 0 0 20px {score_color}88;">
            {safety_score}
          </div>
          <div style="font-size: 0.75rem; color: rgba(238, 240, 255, 0.5); margin-top: 0.25rem;">/ 100</div>
        </div>
        <div style="text-align: center; background: rgba(5, 5, 20, 0.8); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 1rem; padding: 1rem 1.5rem; backdrop-filter: blur(10px);">
          <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: rgba(238, 240, 255, 0.5); margin-bottom: 0.5rem;">Current Risk</div>
          <div style="font-size: 2rem;">{risk_emoji}</div>
          <div style="font-size: 1rem; font-weight: 700; color: {risk_color};">{risk_level}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # ── TIME RANGE FILTER ────────────────────────────────────────────────────
    col_filter, col_export = st.columns([3, 1])
    with col_filter:
        selected_range = st.selectbox(
            "📅 Analytics Time Range",
            options=["24h", "7d", "30d", "all"],
            format_func=lambda x: {"24h": "Last 24 Hours", "7d": "Last 7 Days", "30d": "Last 30 Days", "all": "All Time"}.get(x, x),
            key="analytics_time_filter"
        )
        filtered_incidents = _filter_by_time_range(incidents, selected_range)
    
    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
    
    # ── KEY METRICS GRID ─────────────────────────────────────────────────────
    st.markdown("<h2 style='color: #eef0ff; font-size: 1.3rem; margin: 0 0 1rem 0;'>📊 Key Metrics</h2>", unsafe_allow_html=True)
    
    metric_cols = st.columns(5)
    metric_cards = [
        ("📈", "Total Incidents", str(metrics["total"]), "All-time count"),
        ("🔥", "Fire Detections", str(metrics["fire"]), f"{metrics['fire'] / max(1, metrics['total']) * 100:.0f}% of total"),
        ("💨", "Smoke Detections", str(metrics["smoke"]), f"{metrics['smoke'] / max(1, metrics['total']) * 100:.0f}% of total"),
        ("📊", "Avg Confidence", f"{metrics['avg_confidence']:.1%}", f"Min: {metrics['min_confidence']:.1%} | Max: {metrics['max_confidence']:.1%}"),
        ("📅", "Today's Incidents", str(metrics["today"]), "24-hour window"),
    ]
    
    for col, (icon, label, value, sub) in zip(metric_cols, metric_cards):
        with col:
            color = "#00ffcc" if "Smoke" not in label and "Fire" not in label else ("#ff4500" if "Fire" in label else "#00d4ff")
            st.markdown(f"""
            <div style="background: rgba(5, 5, 20, 0.8); border: 1px solid rgba(0, 212, 255, 0.15); border-radius: 0.75rem; padding: 1rem; text-align: center; backdrop-filter: blur(10px);">
              <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
              <div style="font-size: 0.75rem; text-transform: uppercase; color: rgba(238, 240, 255, 0.5); margin-bottom: 0.5rem; letter-spacing: 0.05em;">{label}</div>
              <div style="font-size: 1.8rem; font-weight: 900; color: {color}; margin-bottom: 0.5rem;">{value}</div>
              <div style="font-size: 0.7rem; color: rgba(238, 240, 255, 0.5);">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # ── PREDICTIVE INSIGHTS ──────────────────────────────────────────────────
    st.markdown("<h2 style='color: #eef0ff; font-size: 1.3rem; margin: 0 0 1rem 0;'>🔮 Predictive Insights</h2>", unsafe_allow_html=True)
    
    pred_cols = st.columns(4)
    pred_cards = [
        ("🎯", "Risk Level", pred_metrics["risk_level"], "Last 24h activity", pred_metrics["risk_class"]),
        ("⚡", "Detection Rate", f"{pred_metrics['velocity']}/hr", "Incidents per hour", "low" if pred_metrics['velocity'] < 0.1 else "medium"),
        ("🕐", "Peak Hour", pred_metrics["peak_hour_str"], "Highest incident time", "medium"),
        ("📈", "7-Day Trend", pred_metrics["forecast"], "Compared to prior week", "low" if "Decreasing" in pred_metrics["forecast"] else "high"),
    ]
    
    for col, (icon, label, value, sub, risk_cls) in zip(pred_cols, pred_cards):
        with col:
            risk_colors = {"low": "#00ffcc", "medium": "#ff6a00", "high": "#ff2d2d"}
            color = risk_colors.get(risk_cls, "#00d4ff")
            st.markdown(f"""
            <div style="background: rgba(5, 5, 20, 0.8); border: 1px solid rgba(0, 212, 255, 0.15); border-radius: 0.75rem; padding: 1rem; text-align: center; backdrop-filter: blur(10px);">
              <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
              <div style="font-size: 0.75rem; text-transform: uppercase; color: rgba(238, 240, 255, 0.5); margin-bottom: 0.5rem; letter-spacing: 0.05em;">{label}</div>
              <div style="font-size: 1.6rem; font-weight: 900; color: {color}; margin-bottom: 0.5rem;">{value}</div>
              <div style="font-size: 0.7rem; color: rgba(238, 240, 255, 0.5);">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # ── ANALYTICS CHARTS ────────────────────────────────────────────────────
    st.markdown("<h2 style='color: #eef0ff; font-size: 1.3rem; margin: 0 0 1rem 0;'>📊 Detailed Analytics</h2>", unsafe_allow_html=True)
    
    try:
        # Row 1: Safety Score + Heatmap
        col_gauge, col_heatmap = st.columns([1, 1.5])
        with col_gauge:
            st.plotly_chart(_safety_score_gauge(safety_score), use_container_width=True, key="safety_gauge")
        with col_heatmap:
            try:
                st.plotly_chart(risk_heatmap_chart(filtered_incidents), use_container_width=True, key="risk_heatmap")
            except Exception as e:
                logger.warning(f"Heatmap render failed: {e}")
                st.info("Risk heatmap temporarily unavailable")
        
        # Row 2: Confidence + Velocity
        col_conf, col_vel = st.columns(2)
        with col_conf:
            try:
                st.plotly_chart(confidence_trend_chart(filtered_incidents), use_container_width=True, key="conf_trend")
            except Exception as e:
                logger.warning(f"Confidence chart failed: {e}")
                st.info("Confidence trend chart unavailable")
        with col_vel:
            try:
                st.plotly_chart(detection_velocity_chart(filtered_incidents), use_container_width=True, key="velocity_chart")
            except Exception as e:
                logger.warning(f"Velocity chart failed: {e}")
                st.info("Detection velocity chart unavailable")
        
        # Row 3: Distribution + Frequency
        col_pie, col_freq = st.columns(2)
        with col_pie:
            try:
                st.plotly_chart(pie_chart(filtered_incidents), use_container_width=True, key="pie_chart")
            except Exception as e:
                logger.warning(f"Pie chart failed: {e}")
                st.info("Distribution chart unavailable")
        with col_freq:
            try:
                st.plotly_chart(incident_frequency_chart(filtered_incidents), use_container_width=True, key="freq_chart")
            except Exception as e:
                logger.warning(f"Frequency chart failed: {e}")
                st.info("Frequency chart unavailable")
        
        # Row 4: Weekly + Monthly
        col_weekly, col_monthly = st.columns(2)
        with col_weekly:
            try:
                st.plotly_chart(weekly_trend_chart(filtered_incidents), use_container_width=True, key="weekly_chart")
            except Exception as e:
                logger.warning(f"Weekly chart failed: {e}")
                st.info("Weekly trend chart unavailable")
        with col_monthly:
            try:
                st.plotly_chart(monthly_trend_chart(filtered_incidents), use_container_width=True, key="monthly_chart")
            except Exception as e:
                logger.warning(f"Monthly chart failed: {e}")
                st.info("Monthly trend chart unavailable")
        
    except Exception as e:
        logger.error(f"Charts rendering error: {e}")
        st.error("Some charts could not be rendered. Try refreshing the page.")
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # ── AI RECOMMENDATIONS ──────────────────────────────────────────────────
    st.markdown("<h2 style='color: #eef0ff; font-size: 1.3rem; margin: 0 0 1rem 0;'>🤖 AI Recommendations</h2>", unsafe_allow_html=True)
    
    recommendations = _compute_recommendations(incidents, pred_metrics)
    
    for rec in recommendations:
        priority_colors = {"high": "#ff2d2d", "medium": "#ff6a00", "low": "#00ffcc"}
        priority_bg = {"high": "rgba(255, 45, 45, 0.1)", "medium": "rgba(255, 106, 0, 0.1)", "low": "rgba(0, 255, 204, 0.1)"}
        color = priority_colors.get(rec["priority_class"], "#00d4ff")
        bg = priority_bg.get(rec["priority_class"], "rgba(0, 212, 255, 0.08)")
        
        st.markdown(f"""
        <div style="background: {bg}; border: 1px solid {color}22; border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.75rem; backdrop-filter: blur(10px); border-left: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
                <div style="flex: 1; color: #eef0ff; font-size: 0.95rem; line-height: 1.4;">
                    {rec['text']}
                </div>
                <div style="background: {color}22; border: 1px solid {color}44; color: {color}; padding: 0.4rem 0.8rem; border-radius: 0.4rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; white-space: nowrap;">
                    {rec['priority']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # ── INCIDENT TABLE ──────────────────────────────────────────────────────
    st.markdown("<h2 style='color: #eef0ff; font-size: 1.3rem; margin: 0 0 1rem 0;'>📋 Recent Incidents</h2>", unsafe_allow_html=True)
    
    if filtered_incidents:
        # Create dataframe for display
        df_data = []
        for inc in sorted(filtered_incidents, key=lambda x: x.get("timestamp", ""), reverse=True)[:50]:
            df_data.append({
                "⏰ Timestamp": inc.get("timestamp", "N/A"),
                "🎯 Type": inc.get("type", "Unknown").upper(),
                "📊 Confidence": f"{inc.get('confidence', 0.0):.1%}",
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No incidents in selected time range")
    else:
        st.info("No incidents found")
    
    render_page_footer("Analytics")

except Exception as e:
    logger.exception("Analytics page error")
    st.error(f"❌ An error occurred while loading analytics: {str(e)}")
    st.info("Try refreshing the page or contact support if the issue persists.")

