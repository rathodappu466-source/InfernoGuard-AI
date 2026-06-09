"""
Live Detection Operations Center — InfernoGuard AI.
Enterprise-grade real-time fire & smoke surveillance UI.
Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3.1–3.7, 9.1–9.4
"""

import os
import tempfile
from datetime import datetime, date

import cv2
import streamlit as st

from auth.session import require_auth
import database.db as db
from detection.detector import FireSmokeDetector
from utils.ui import render_page_footer, render_breadcrumbs
from detection.webcam import stream_webcam
from detection.rtsp import stream_rtsp
from detection.video_detection import stream_video
from alerts.cooldown import should_alert, record_alert
from alerts.sound_alert import play_alarm
from alerts.email_alert import send_email_alert
from alerts.telegram_alert import send_telegram_alert
from utils.config import MODEL_PATH, SCREENSHOTS_DIR
from utils.helpers import get_timestamp, generate_screenshot_filename, resize_frame
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Live Detection — InfernoGuard AI",
    page_icon="🎥",
    layout="wide",
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
_CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "styles.css")
if os.path.isfile(_CSS_PATH):
    with open(_CSS_PATH, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Auth guard ────────────────────────────────────────────────────────────────
require_auth()

render_breadcrumbs([("Home", "🏠"), ("Live Detection", "🎥")])

# ── Session state initialisation ─────────────────────────────────────────────
if "last_detection" not in st.session_state:
    st.session_state["last_detection"] = None
if "live_notifications" not in st.session_state:
    st.session_state["live_notifications"] = []
if "current_fps" not in st.session_state:
    st.session_state["current_fps"] = 0.0
if "threat_level" not in st.session_state:
    st.session_state["threat_level"] = "NORMAL"
if "detection_running" not in st.session_state:
    st.session_state["detection_running"] = False
if "monitoring_active" not in st.session_state:
    st.session_state["monitoring_active"] = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _dispatch_alerts(detection_type: str, confidence: float, screenshot_path: str, settings: dict) -> None:
    """Fire all enabled alert channels if cooldown allows."""
    if not settings.get("alert_enabled", 1):
        return
    if not should_alert(detection_type):
        return
    record_alert(detection_type)
    if settings.get("sound_enabled", 1):
        alarm_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "alarm.mp3")
        play_alarm(alarm_path)
    if settings.get("email_enabled", 0):
        send_email_alert(settings, detection_type, confidence, screenshot_path)
    if settings.get("telegram_enabled", 0):
        send_telegram_alert(
            settings.get("telegram_token", ""),
            settings.get("telegram_chat_id", ""),
            detection_type,
            confidence,
        )


def _save_screenshot(frame, detection_type: str) -> str:
    """Save annotated frame to screenshots dir; return the file path."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    filename = generate_screenshot_filename(detection_type)
    path = os.path.join(SCREENSHOTS_DIR, filename)
    cv2.imwrite(path, frame)
    return path


def _get_severity(confidence: float) -> tuple:
    """Return (level_label, css_class, dot_class) for a confidence score."""
    if confidence >= 0.85:
        return "CRITICAL", "ig-severity-high", "danger"
    elif confidence >= 0.70:
        return "HIGH", "ig-severity-high", "danger"
    elif confidence >= 0.50:
        return "MEDIUM", "ig-severity-medium", "warning"
    else:
        return "LOW", "ig-severity-low", "active"


def _get_ai_recommendation(detection_type) -> str:
    """Return contextual AI response text based on detection type."""
    if detection_type == "fire":
        return (
            "🚒 Initiate evacuation protocol. Contact fire department immediately. "
            "Activate suppression systems."
        )
    elif detection_type == "smoke":
        return (
            "⚠️ Investigate smoke source. Check HVAC systems. "
            "Prepare evacuation if smoke increases."
        )
    else:
        return "✅ All clear. Continue monitoring. No immediate action required."


def _count_today_incidents() -> int:
    """Count incidents logged today."""
    try:
        incidents = db.get_all_incidents()
        today_str = date.today().isoformat()
        return sum(1 for inc in incidents if inc.get("timestamp", "").startswith(today_str))
    except Exception:
        return 0


def _render_side_panel(panel_placeholder) -> None:
    """Render the detection details side panel into the given placeholder."""
    last = st.session_state.get("last_detection")
    with panel_placeholder.container():
        st.markdown(
            '<div class="ig-card ig-card-sm" style="height:100%;">',
            unsafe_allow_html=True,
        )

        # ── Last Detection Details ────────────────────────────────────────────
        st.markdown(
            '<p class="ig-section-title">🎯 Last Detection</p>',
            unsafe_allow_html=True,
        )

        if last:
            det_type = last.get("type", "unknown")
            confidence = last.get("confidence", 0.0)
            ts = last.get("timestamp", "—")
            screenshot_path = last.get("screenshot_path", "")

            badge_class = "fire" if det_type == "fire" else "smoke"
            badge_icon = "🔥" if det_type == "fire" else "💨"

            st.markdown(
                f'<span class="ig-badge {badge_class}">{badge_icon} {det_type.upper()}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p class="ig-caption ig-mt-sm">Confidence: <strong>{confidence:.1%}</strong></p>',
                unsafe_allow_html=True,
            )
            st.progress(confidence)
            st.markdown(
                f'<p class="ig-mono ig-mt-sm">{ts}</p>',
                unsafe_allow_html=True,
            )

            if screenshot_path and os.path.isfile(screenshot_path):
                st.image(screenshot_path, use_container_width=True)

        else:
            st.markdown(
                '<p class="ig-caption">No detection recorded yet.</p>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="ig-divider-subtle"></div>', unsafe_allow_html=True)

        # ── Severity Assessment ───────────────────────────────────────────────
        st.markdown(
            '<p class="ig-section-title">⚡ Severity</p>',
            unsafe_allow_html=True,
        )

        if last:
            confidence = last.get("confidence", 0.0)
            level, sev_class, dot_class = _get_severity(confidence)
            st.markdown(
                f'''
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                  <span class="ig-status-dot {dot_class}"></span>
                  <span class="{sev_class}" style="font-size:1.1rem;">{level}</span>
                </div>
                <p class="ig-caption">Confidence score: <strong>{confidence:.1%}</strong></p>
                ''',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '''
                <div style="display:flex; align-items:center; gap:0.5rem;">
                  <span class="ig-status-dot inactive"></span>
                  <span class="ig-severity-low">NORMAL</span>
                </div>
                ''',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="ig-divider-subtle"></div>', unsafe_allow_html=True)

        # ── AI Response Recommendations ───────────────────────────────────────
        st.markdown(
            '<p class="ig-section-title">🤖 AI Response</p>',
            unsafe_allow_html=True,
        )
        det_type_for_rec = last.get("type") if last else None
        recommendation = _get_ai_recommendation(det_type_for_rec)
        st.markdown(
            f'<p class="ig-caption">{recommendation}</p>',
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ── Main render ───────────────────────────────────────────────────────────────
try:
    is_running = st.session_state.get("detection_running", False)
    now_str = datetime.now().strftime("%H:%M:%S")

    # ── 1. Professional Hero Header ───────────────────────────────────────────
    badge_class = "online" if is_running else "warning"
    badge_label = "● LIVE" if is_running else "○ IDLE"
    st.markdown(
        f'''
        <div class="ig-hero ig-animate-fadeInUp">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
            <div>
              <h1 class="ig-hero-title">🎥 Live Detection Operations Center</h1>
              <p class="ig-hero-subtitle">Real-time AI-powered fire &amp; smoke surveillance</p>
            </div>
            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:0.4rem;">
              <span class="ig-badge {badge_class}">{badge_label}</span>
              <span class="ig-mono" style="font-size:0.72rem; color:var(--text-muted);">
                Last updated: {now_str}
              </span>
            </div>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ig-divider"></div>', unsafe_allow_html=True)

    # ── 2. Status Cards Row ───────────────────────────────────────────────────
    today_count = _count_today_incidents()
    fps_display = f"{st.session_state['current_fps']:.1f}" if is_running else "—"
    threat_level = st.session_state.get("threat_level", "NORMAL")

    det_status_label = "ACTIVE" if is_running else "STANDBY"
    det_dot_class = "active" if is_running else "inactive"

    threat_color_map = {
        "CRITICAL": "var(--fire-red)",
        "ELEVATED": "var(--status-warning)",
        "NORMAL": "var(--status-online)",
    }
    threat_color = threat_color_map.get(threat_level, "var(--status-online)")

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(
            f'''
            <div class="ig-metric-card ig-animate-fadeInUp ig-delay-1">
              <div style="display:flex; align-items:center; justify-content:center; gap:0.5rem; margin-bottom:0.3rem;">
                <span class="ig-status-dot {det_dot_class}"></span>
                <span class="ig-metric-value" style="font-size:1.4rem;">{det_status_label}</span>
              </div>
              <div class="ig-metric-label">Detection Status</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            f'''
            <div class="ig-metric-card ig-animate-fadeInUp ig-delay-2">
              <div class="ig-metric-value">{fps_display}</div>
              <div class="ig-metric-label">Current FPS</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            f'''
            <div class="ig-metric-card ig-animate-fadeInUp ig-delay-3">
              <div class="ig-metric-value">{today_count}</div>
              <div class="ig-metric-label">Detections Today</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with sc4:
        st.markdown(
            f'''
            <div class="ig-metric-card ig-animate-fadeInUp ig-delay-4">
              <div class="ig-metric-value" style="color:{threat_color}; font-size:1.3rem;">{threat_level}</div>
              <div class="ig-metric-label">Threat Level</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3. Source Selector & Controls ─────────────────────────────────────────
    st.markdown('<div class="ig-card ig-card-sm ig-animate-fadeInUp">', unsafe_allow_html=True)

    source = st.selectbox(
        "Video Source",
        ["Webcam", "RTSP Stream", "Upload Video"],
        key="detection_source",
    )

    rtsp_url = ""
    uploaded_file = None

    if source == "RTSP Stream":
        settings_row = db.get_settings()
        default_rtsp = settings_row.get("rtsp_url", "")
        rtsp_url = st.text_input("RTSP URL", value=default_rtsp, key="rtsp_url_input")
    elif source == "Upload Video":
        uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

    col_start, col_stop = st.columns([1, 1])
    with col_start:
        st.markdown('<div class="ig-btn-fire">', unsafe_allow_html=True)
        start = st.button("▶ Start Detection", key="btn_start", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_stop:
        st.markdown('<div class="ig-btn-ghost">', unsafe_allow_html=True)
        stop = st.button("⏹ Stop Detection", key="btn_stop", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if stop:
        st.session_state["detection_running"] = False
        st.session_state["monitoring_active"] = False
        st.session_state["threat_level"] = "NORMAL"
        st.session_state["current_fps"] = 0.0

    if start:
        st.session_state["detection_running"] = True
        st.session_state["monitoring_active"] = True

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4 & 5. Video + Side Panel (2-column layout) ───────────────────────────
    vid_col, panel_col = st.columns([0.65, 0.35])

    with vid_col:
        # Emergency alert placeholder (above video)
        alert_placeholder = st.empty()

        # Scan container wrapper (open) with corner brackets
        st.markdown(
            '''
            <div class="ig-scan-container ig-card"
                 style="padding:0; border:1px solid var(--border-glow);
                        border-radius:var(--radius-lg); overflow:hidden; position:relative;">
              <div class="ig-scan-line"></div>
              <div class="ig-corner-bracket tl"></div>
              <div class="ig-corner-bracket tr"></div>
              <div class="ig-corner-bracket bl"></div>
              <div class="ig-corner-bracket br"></div>
            ''',
            unsafe_allow_html=True,
        )

        frame_placeholder = st.empty()
        fps_placeholder = st.empty()

        # Close scan container
        st.markdown("</div>", unsafe_allow_html=True)

        # Live notification feed
        notifications_placeholder = st.empty()

    with panel_col:
        panel_placeholder = st.empty()
        # Render initial (idle) side panel
        _render_side_panel(panel_placeholder)

    # ── Detection loop ────────────────────────────────────────────────────────
    if st.session_state.get("detection_running", False):
        settings = db.get_settings()
        threshold = settings.get("confidence_threshold", 0.5)

        detector = FireSmokeDetector(MODEL_PATH, confidence_threshold=threshold)

        # Requirement 2.6 — graceful model load failure
        if not detector.is_loaded():
            st.error(
                "⚠️ YOLOv8 model not found. "
                "Please place the model file at: `" + MODEL_PATH + "`"
            )
            st.session_state["detection_running"] = False
            st.stop()

        # Choose stream generator
        if source == "Webcam":
            stream = stream_webcam(detector)
        elif source == "RTSP Stream":
            if not rtsp_url:
                st.warning("Please enter an RTSP URL.")
                st.session_state["detection_running"] = False
                st.stop()
            stream = stream_rtsp(detector, rtsp_url)
        else:  # Upload Video
            if uploaded_file is None:
                st.warning("Please upload a video file.")
                st.session_state["detection_running"] = False
                st.stop()
            suffix = os.path.splitext(uploaded_file.name)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            stream = stream_video(detector, tmp_path)

        for result in stream:
            if not st.session_state.get("detection_running", False):
                break

            # Update FPS in session state
            st.session_state["current_fps"] = result.fps

            # Requirement 2.4 — FPS overlay
            fps_placeholder.markdown(
                f'<span class="ig-mono" style="display:block; padding:4px 8px; '
                f'font-size:0.78rem;">FPS: {result.fps:.1f}</span>',
                unsafe_allow_html=True,
            )

            # Display annotated frame (convert BGR → RGB for Streamlit)
            display_frame = resize_frame(result.annotated_frame, 800)
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)

            # Handle detections
            if result.detections:
                logged_types: set = set()

                for det in result.detections:
                    if det.label in logged_types:
                        continue
                    logged_types.add(det.label)

                    ts = get_timestamp()
                    screenshot_path = _save_screenshot(result.annotated_frame, det.label)

                    # Log incident
                    db.log_incident(det.label, det.confidence, ts, screenshot_path)

                    # Read latest settings
                    current_settings = db.get_settings()

                    # Dispatch alerts
                    _dispatch_alerts(det.label, det.confidence, screenshot_path, current_settings)

                    # Update session state
                    st.session_state["last_detection"] = {
                        "type": det.label,
                        "confidence": det.confidence,
                        "timestamp": ts,
                        "screenshot_path": screenshot_path,
                    }

                    # Update threat level
                    if det.label == "fire":
                        st.session_state["threat_level"] = "CRITICAL"
                    elif det.label == "smoke" and st.session_state["threat_level"] != "CRITICAL":
                        st.session_state["threat_level"] = "ELEVATED"

                    # Update live notifications (keep last 5)
                    notif = {
                        "type": det.label,
                        "confidence": det.confidence,
                        "timestamp": ts,
                    }
                    notifications = st.session_state.get("live_notifications", [])
                    notifications.insert(0, notif)
                    st.session_state["live_notifications"] = notifications[:5]

                # Emergency banner
                detected_types = ", ".join(sorted({d.label.upper() for d in result.detections}))
                max_conf = max(d.confidence for d in result.detections)
                ts_now = datetime.now().strftime("%H:%M:%S")

                alert_placeholder.markdown(
                    f'''
                    <div class="ig-emergency-banner">
                      🚨 EMERGENCY ALERT — {detected_types} DETECTED
                      &nbsp;|&nbsp; Confidence: {max_conf:.1%}
                      &nbsp;|&nbsp; {ts_now}
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

            else:
                # No detection this frame
                if st.session_state.get("threat_level") not in ("CRITICAL", "ELEVATED"):
                    st.session_state["threat_level"] = "NORMAL"
                alert_placeholder.empty()

            # Render side panel with latest detection info
            _render_side_panel(panel_placeholder)

            # Live notification feed
            notifications = st.session_state.get("live_notifications", [])
            if notifications:
                notif_items = ""
                for n in notifications:
                    icon = "🔥" if n["type"] == "fire" else "💨"
                    badge_cls = "fire" if n["type"] == "fire" else "smoke"
                    notif_items += f'''
                    <div class="ig-notification-item">
                      <span class="ig-badge {badge_cls}">{icon} {n["type"].upper()}</span>
                      <span class="ig-caption">{n["confidence"]:.1%}</span>
                      <span class="ig-mono" style="margin-left:auto; font-size:0.70rem;">
                        {n["timestamp"]}
                      </span>
                    </div>
                    '''
                notifications_placeholder.markdown(
                    f'''
                    <div style="margin-top:0.75rem;">
                      <p class="ig-label" style="margin-bottom:0.4rem;">Live Notifications</p>
                      {notif_items}
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

        st.session_state["detection_running"] = False
        st.session_state["monitoring_active"] = False
        st.session_state["threat_level"] = "NORMAL"
        st.session_state["current_fps"] = 0.0
        st.info("Detection stopped.")

    render_page_footer("Live Detection")

except Exception:
    logger.exception("Live Detection page error")
    st.error("An error occurred in the detection pipeline. Please try again.")
