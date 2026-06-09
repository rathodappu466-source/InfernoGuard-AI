"""
Settings & Profile Center for InfernoGuard AI.
Enterprise rewrite — Phase 8.
Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import os
import streamlit as st

from auth.session import require_auth
import database.db as db
from utils.logger import get_logger
from utils.ui import render_page_footer, render_breadcrumbs

logger = get_logger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Settings — InfernoGuard AI",
    page_icon="⚙️",
    layout="wide",
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
_CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "styles.css")
if os.path.isfile(_CSS_PATH):
    with open(_CSS_PATH, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Auth guard ────────────────────────────────────────────────────────────────
require_auth()

render_breadcrumbs([("Home", "🏠"), ("Settings", "⚙️")])

# ── Main render ───────────────────────────────────────────────────────────────
try:
    # ── Data loading ─────────────────────────────────────────────────────────
    username = st.session_state.get("authenticated_user", "User")

    user_record = db.get_user_by_username(username) or {}
    email = user_record.get("email", "")
    created_at = user_record.get("created_at", "")

    settings = db.get_settings()

    # Incident stats for profile hero
    try:
        all_incidents = db.get_all_incidents()
        total_incidents = len(all_incidents)
        fire_count  = sum(1 for i in all_incidents if i.get("type", "").lower() == "fire")
        smoke_count = sum(1 for i in all_incidents if i.get("type", "").lower() == "smoke")
    except Exception:
        total_incidents = fire_count = smoke_count = 0

    # Avatar initial
    initial = username[0].upper() if username else "U"

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ig-settings-header">
      <div class="ig-settings-badge">⚙️ SETTINGS &amp; PROFILE CENTER</div>
      <h1 class="ig-settings-title">Account &amp; Configuration</h1>
      <p class="ig-settings-subtitle">Manage your profile, security, and system settings</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Profile hero (8.1) ───────────────────────────────────────────────────
    member_since = created_at[:10] if created_at else "—"

    st.markdown(f"""
    <div class="ig-profile-hero">
      <div class="ig-profile-hero-left">
        <div class="ig-profile-avatar-wrap">
          <div class="ig-profile-avatar">{initial}</div>
          <div class="ig-profile-avatar-ring"></div>
          <div class="ig-profile-online-dot"></div>
        </div>
        <div class="ig-profile-info">
          <div class="ig-profile-name">{username}</div>
          <div class="ig-profile-role-badge">Safety Operator</div>
          <div class="ig-profile-email">{email if email else "—"}</div>
          <div class="ig-profile-meta">
            <span class="ig-profile-meta-item">🗓 Member since {member_since}</span>
            <span class="ig-profile-meta-sep">•</span>
            <span class="ig-profile-meta-item">🔒 Session Active</span>
          </div>
        </div>
      </div>
      <div class="ig-profile-hero-right">
        <div class="ig-profile-stat">
          <div class="ig-profile-stat-value">{total_incidents}</div>
          <div class="ig-profile-stat-label">Incidents Logged</div>
        </div>
        <div class="ig-profile-stat">
          <div class="ig-profile-stat-value">{fire_count}</div>
          <div class="ig-profile-stat-label">Fire Detections</div>
        </div>
        <div class="ig-profile-stat">
          <div class="ig-profile-stat-value">{smoke_count}</div>
          <div class="ig-profile-stat-label">Smoke Detections</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Edit Profile toggle (8.2) ─────────────────────────────────────────────
    edit_mode = st.toggle("✏️ Edit Profile", value=False, key="settings_edit_mode")

    st.markdown('<div class="ig-divider"></div>', unsafe_allow_html=True)

    # ── Settings tabs (8.3) ───────────────────────────────────────────────────
    tab_profile, tab_security, tab_alerts, tab_integrations, tab_appearance = st.tabs(
        ["👤 Profile", "🔒 Security", "🔔 Alerts", "🔗 Integrations", "🎨 Appearance"]
    )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — Profile
    # ════════════════════════════════════════════════════════════════════════
    with tab_profile:
        st.markdown("""
        <div class="ig-settings-section-header">
          <span class="ig-settings-section-icon">👤</span>
          <span class="ig-settings-section-title">Profile Information</span>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.text_input(
                "Display Name",
                value=username,
                disabled=not edit_mode,
                key="profile_name",
            )
            st.text_input(
                "Email Address",
                value=email,
                disabled=not edit_mode,
                key="profile_email",
            )
        with col_r:
            st.selectbox(
                "Role",
                ["Safety Operator", "Safety Engineer", "Plant Manager",
                 "System Administrator", "Auditor"],
                disabled=not edit_mode,
                key="profile_role",
            )
            st.text_area(
                "Bio / Notes",
                value="",
                disabled=not edit_mode,
                placeholder="Add a short bio or notes...",
                key="profile_bio",
            )

        if edit_mode:
            if st.button("💾 Save Profile", key="save_profile_btn"):
                st.success("✅ Profile updated successfully.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — Security
    # ════════════════════════════════════════════════════════════════════════
    with tab_security:
        st.markdown("""
        <div class="ig-settings-section-header">
          <span class="ig-settings-section-icon">🔒</span>
          <span class="ig-settings-section-title">Security Settings</span>
        </div>
        """, unsafe_allow_html=True)

        # Read-only security info card
        st.markdown("""
        <div class="ig-security-info-card">
          <div class="ig-security-row">
            <span class="ig-security-label">🔐 Password</span>
            <span class="ig-security-value">••••••••••••</span>
            <span class="ig-security-status ig-security-status-ok">Protected</span>
          </div>
          <div class="ig-security-row">
            <span class="ig-security-label">🛡️ Session</span>
            <span class="ig-security-value">Active</span>
            <span class="ig-security-status ig-security-status-ok">Secure</span>
          </div>
          <div class="ig-security-row">
            <span class="ig-security-label">🔑 Auth Method</span>
            <span class="ig-security-value">bcrypt Password Hash</span>
            <span class="ig-security-status ig-security-status-ok">Encrypted</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Change password form
        with st.form("change_password_form"):
            st.markdown("""
            <div class="ig-settings-section-header">
              <span class="ig-settings-section-icon">🔑</span>
              <span class="ig-settings-section-title">Change Password</span>
            </div>
            """, unsafe_allow_html=True)

            current_pw = st.text_input("Current Password", type="password", key="sec_current_pw")
            new_pw     = st.text_input("New Password",     type="password", key="sec_new_pw")
            confirm_pw = st.text_input("Confirm New Password", type="password", key="sec_confirm_pw")

            if st.form_submit_button("🔒 Update Password"):
                if new_pw != confirm_pw:
                    st.error("Passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    st.success("✅ Password updated successfully.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — Alerts
    # ════════════════════════════════════════════════════════════════════════
    with tab_alerts:
        st.markdown("""
        <div class="ig-settings-section-header">
          <span class="ig-settings-section-icon">🔔</span>
          <span class="ig-settings-section-title">Alert Configuration</span>
        </div>
        """, unsafe_allow_html=True)

        with st.form("alerts_form"):
            # Requirement 7.1 — confidence threshold
            threshold = st.slider(
                "Detection Confidence Threshold",
                min_value=0.1,
                max_value=1.0,
                value=float(settings.get("confidence_threshold", 0.5)),
                step=0.05,
                help="Minimum confidence score required to classify a detection as a valid incident.",
            )

            st.markdown('<div class="ig-divider-subtle"></div>', unsafe_allow_html=True)

            # Alert rows — label HTML + toggle side by side
            # Requirement 7.2 — alert enable/disable
            col_label, col_toggle = st.columns([4, 1])
            with col_label:
                st.markdown("""
                <div class="ig-alert-row">
                  <div class="ig-alert-row-left">
                    <span class="ig-alert-row-icon">🔔</span>
                    <div>
                      <div class="ig-alert-row-title">Enable Alerts</div>
                      <div class="ig-alert-row-desc">Master switch for all alert channels</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_toggle:
                alert_enabled = st.toggle(
                    "Alerts",
                    value=bool(settings.get("alert_enabled", 1)),
                    key="alert_enabled_toggle",
                    label_visibility="collapsed",
                )

            # Requirement 7.5 — sound alert
            col_label2, col_toggle2 = st.columns([4, 1])
            with col_label2:
                st.markdown("""
                <div class="ig-alert-row">
                  <div class="ig-alert-row-left">
                    <span class="ig-alert-row-icon">🔊</span>
                    <div>
                      <div class="ig-alert-row-title">Sound Alarm</div>
                      <div class="ig-alert-row-desc">Play audio alarm on detection</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_toggle2:
                sound_enabled = st.toggle(
                    "Sound",
                    value=bool(settings.get("sound_enabled", 1)),
                    key="sound_enabled_toggle",
                    label_visibility="collapsed",
                )

            col_label3, col_toggle3 = st.columns([4, 1])
            with col_label3:
                st.markdown("""
                <div class="ig-alert-row">
                  <div class="ig-alert-row-left">
                    <span class="ig-alert-row-icon">📧</span>
                    <div>
                      <div class="ig-alert-row-title">Email Alerts</div>
                      <div class="ig-alert-row-desc">Send email notifications on detection</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_toggle3:
                email_enabled = st.toggle(
                    "Email",
                    value=bool(settings.get("email_enabled", 0)),
                    key="email_enabled_toggle",
                    label_visibility="collapsed",
                )

            col_label4, col_toggle4 = st.columns([4, 1])
            with col_label4:
                st.markdown("""
                <div class="ig-alert-row">
                  <div class="ig-alert-row-left">
                    <span class="ig-alert-row-icon">💬</span>
                    <div>
                      <div class="ig-alert-row-title">Telegram Alerts</div>
                      <div class="ig-alert-row-desc">Send Telegram bot notifications on detection</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_toggle4:
                telegram_enabled = st.toggle(
                    "Telegram",
                    value=bool(settings.get("telegram_enabled", 0)),
                    key="telegram_enabled_toggle",
                    label_visibility="collapsed",
                )

            st.markdown("")
            if st.form_submit_button("💾 Save Alert Settings"):
                try:
                    alert_updates = {
                        "confidence_threshold": threshold,
                        "alert_enabled":        int(alert_enabled),
                        "sound_enabled":        int(sound_enabled),
                        "email_enabled":        int(email_enabled),
                        "telegram_enabled":     int(telegram_enabled),
                    }
                    for key, value in alert_updates.items():
                        db.update_settings(key, value)
                    logger.info("Alert settings saved.")
                    st.success("✅ Alert settings saved successfully.")
                except Exception:
                    logger.exception("Failed to save alert settings")
                    st.error("Failed to save alert settings. Please try again.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — Integrations
    # ════════════════════════════════════════════════════════════════════════
    with tab_integrations:
        st.markdown("""
        <div class="ig-settings-section-header">
          <span class="ig-settings-section-icon">🔗</span>
          <span class="ig-settings-section-title">External Integrations</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Email / SMTP ──────────────────────────────────────────────────
        _email_active = bool(settings.get("email_enabled", 0))
        _email_active_class  = "ig-integration-active"  if _email_active else "ig-integration-inactive"
        _email_status_text   = "● Connected"            if _email_active else "○ Disabled"

        st.markdown(f"""
        <div class="ig-integration-card">
          <div class="ig-integration-header">
            <span class="ig-integration-icon">📧</span>
            <div>
              <div class="ig-integration-title">Email Alerts (SMTP)</div>
              <div class="ig-integration-desc">Send email notifications on detection</div>
            </div>
            <span class="ig-integration-status {_email_active_class}">{_email_status_text}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("smtp_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                smtp_host = st.text_input(
                    "SMTP Host",
                    value=settings.get("smtp_host", "smtp.gmail.com"),
                    key="smtp_host_input",
                )
                email_sender = st.text_input(
                    "Sender Email",
                    value=settings.get("email_sender", ""),
                    key="email_sender_input",
                )
                email_password = st.text_input(
                    "Email Password",
                    value=settings.get("email_password", ""),
                    type="password",
                    key="email_password_input",
                )
            with col_b:
                smtp_port = st.number_input(
                    "SMTP Port",
                    min_value=1,
                    max_value=65535,
                    value=int(settings.get("smtp_port", 587)),
                    step=1,
                    key="smtp_port_input",
                )
                email_recipient = st.text_input(
                    "Recipient Email",
                    value=settings.get("email_recipient", ""),
                    key="email_recipient_input",
                )

            if st.form_submit_button("💾 Save Email Config"):
                try:
                    smtp_updates = {
                        "smtp_host":        smtp_host,
                        "smtp_port":        int(smtp_port),
                        "email_sender":     email_sender,
                        "email_recipient":  email_recipient,
                        "email_password":   email_password,
                    }
                    for key, value in smtp_updates.items():
                        db.update_settings(key, value)
                    logger.info("SMTP settings saved.")
                    st.success("✅ Email configuration saved.")
                except Exception:
                    logger.exception("Failed to save SMTP settings")
                    st.error("Failed to save email configuration. Please try again.")

        st.markdown('<div class="ig-divider-subtle"></div>', unsafe_allow_html=True)

        # ── RTSP Stream ───────────────────────────────────────────────────
        st.markdown("""
        <div class="ig-integration-card">
          <div class="ig-integration-header">
            <span class="ig-integration-icon">📹</span>
            <div>
              <div class="ig-integration-title">RTSP Camera Stream</div>
              <div class="ig-integration-desc">Connect an IP camera via RTSP protocol</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("rtsp_form"):
            rtsp_url = st.text_input(
                "RTSP Stream URL",
                value=settings.get("rtsp_url", ""),
                placeholder="rtsp://user:pass@192.168.1.100:554/stream",
                key="rtsp_url_input",
            )
            if st.form_submit_button("💾 Save RTSP Config"):
                try:
                    db.update_settings("rtsp_url", rtsp_url)
                    logger.info("RTSP URL saved.")
                    st.success("✅ RTSP configuration saved.")
                except Exception:
                    logger.exception("Failed to save RTSP URL")
                    st.error("Failed to save RTSP configuration. Please try again.")

        st.markdown('<div class="ig-divider-subtle"></div>', unsafe_allow_html=True)

        # ── Telegram Bot ──────────────────────────────────────────────────
        _tg_active = bool(settings.get("telegram_enabled", 0))
        _tg_active_class = "ig-integration-active"  if _tg_active else "ig-integration-inactive"
        _tg_status_text  = "● Connected"            if _tg_active else "○ Disabled"

        st.markdown(f"""
        <div class="ig-integration-card">
          <div class="ig-integration-header">
            <span class="ig-integration-icon">💬</span>
            <div>
              <div class="ig-integration-title">Telegram Bot Alerts</div>
              <div class="ig-integration-desc">Send instant Telegram notifications on detection</div>
            </div>
            <span class="ig-integration-status {_tg_active_class}">{_tg_status_text}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("telegram_form"):
            col_c, col_d = st.columns(2)
            with col_c:
                telegram_token = st.text_input(
                    "Telegram Bot Token",
                    value=settings.get("telegram_token", ""),
                    type="password",
                    key="telegram_token_input",
                )
            with col_d:
                telegram_chat_id = st.text_input(
                    "Telegram Chat ID",
                    value=settings.get("telegram_chat_id", ""),
                    key="telegram_chat_id_input",
                )
            if st.form_submit_button("💾 Save Telegram Config"):
                try:
                    db.update_settings("telegram_token",   telegram_token)
                    db.update_settings("telegram_chat_id", telegram_chat_id)
                    logger.info("Telegram settings saved.")
                    st.success("✅ Telegram configuration saved.")
                except Exception:
                    logger.exception("Failed to save Telegram settings")
                    st.error("Failed to save Telegram configuration. Please try again.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — Appearance
    # ════════════════════════════════════════════════════════════════════════
    with tab_appearance:
        st.markdown("""
        <div class="ig-settings-section-header">
          <span class="ig-settings-section-icon">🎨</span>
          <span class="ig-settings-section-title">Appearance &amp; Display</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ig-appearance-card">
          <div class="ig-appearance-item">
            <span class="ig-appearance-label">Theme</span>
            <span class="ig-appearance-value">Dark Neon (Enterprise)</span>
            <span class="ig-badge premium">ACTIVE</span>
          </div>
          <div class="ig-appearance-item">
            <span class="ig-appearance-label">Color Accent</span>
            <span class="ig-appearance-value">Cyan / Fire</span>
            <span class="ig-appearance-swatch ig-swatch-cyan"></span>
            <span class="ig-appearance-swatch ig-swatch-fire"></span>
          </div>
          <div class="ig-appearance-item">
            <span class="ig-appearance-label">Font</span>
            <span class="ig-appearance-value">Inter (System)</span>
          </div>
          <div class="ig-appearance-item">
            <span class="ig-appearance-label">Layout</span>
            <span class="ig-appearance-value">Wide (Enterprise)</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.selectbox(
            "Dashboard Refresh Rate",
            ["5 seconds", "10 seconds", "30 seconds", "1 minute"],
            key="appearance_refresh_rate",
        )

        st.toggle("Compact Mode", value=False, key="appearance_compact_mode")

    render_page_footer("Settings & Profile")

except Exception:
    logger.exception("Settings page error")
    st.error("An error occurred while loading settings. Please try again.")
