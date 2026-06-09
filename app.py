"""
InfernoGuard AI — Main application entry point.
Enterprise Security Access Portal with professional UI/UX.
"""

import os
import streamlit as st

import database.db as db
from auth.session import is_authenticated, logout_user
from auth.login import render_login_form
from auth.signup import render_signup_form
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InfernoGuard AI — Enterprise Security Portal",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Initialize database ───────────────────────────────────────────────────────
try:
    db.init_db()
except Exception:
    logger.exception("Failed to initialize database")
    st.error("Database initialization failed. Please check the logs.")
    st.stop()

# ── Load CSS ──────────────────────────────────────────────────────────────────
_CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "styles.css")
if os.path.isfile(_CSS_PATH):
    with open(_CSS_PATH, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── HIDE SIDEBAR ON LOGIN/UNAUTHENTICATED PAGES ───────────────────────────────
if not is_authenticated():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ── Premium Sidebar (ONLY FOR AUTHENTICATED USERS) ───────────────────────────
if is_authenticated():
    with st.sidebar:
        # ── 1. Animated Logo Section ──────────────────────────────────────────────
        st.markdown(
            """
            <div class="ig-sidebar-logo">
                <div class="ig-sidebar-logo-ring-wrap">
                    <div class="ig-sidebar-logo-ring"></div>
                    <span class="ig-sidebar-logo-icon">🔥</span>
                </div>
                <div class="ig-sidebar-title">InfernoGuard AI</div>
                <div class="ig-sidebar-subtitle">Industrial Fire &amp; Smoke Detection</div>
                <div class="ig-sidebar-version">v2.0 Enterprise</div>
                <div class="ig-sidebar-logo-shimmer"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="ig-divider"></div>', unsafe_allow_html=True)

        username = st.session_state.get("authenticated_user", "User")
        initials = username[:2].upper()

        # ── 4. User Mini-Profile Section ──────────────────────────────────────
        try:
            incident_count = len(db.get_all_incidents())
        except Exception:
            incident_count = 0

        st.markdown(
            f"""
            <div class="ig-sidebar-user">
                <div class="ig-sidebar-avatar-wrap">
                    <div class="ig-sidebar-avatar-ring"></div>
                    <div class="ig-sidebar-avatar">{initials}</div>
                </div>
                <div style="flex:1;min-width:0;">
                    <div style="display:flex;align-items:center;gap:0.4rem;">
                        <div class="ig-sidebar-username">{username}</div>
                        <span class="ig-online-dot"></span>
                    </div>
                    <div class="ig-sidebar-role-badge">Security Operator</div>
                </div>
            </div>
            <div class="ig-sidebar-stats">
                <div class="ig-sidebar-stat-item">
                    <span class="ig-sidebar-stat-value">{incident_count}</span>
                    <span class="ig-sidebar-stat-label">Incidents Monitored</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── 3. Status Pulse Widget ────────────────────────────────────────────
        monitoring_active = st.session_state.get("monitoring_active", False)
        session_start = st.session_state.get("session_start_time", None)
        uptime_text = str(session_start) if session_start else "Session Active"

        if monitoring_active:
            st.markdown(
                f"""
                <div class="ig-ai-status ig-ai-status-active">
                    <div class="ig-status-radar">
                        <div class="ig-status-radar-ring ig-status-radar-ring-1"></div>
                        <div class="ig-status-radar-ring ig-status-radar-ring-2"></div>
                        <div class="ig-status-radar-ring ig-status-radar-ring-3"></div>
                        <div class="ig-ai-pulse"></div>
                    </div>
                    <div>
                        <div class="ig-ai-status-text">AI ENGINE ACTIVE</div>
                        <div class="ig-ai-uptime">{uptime_text}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="ig-ai-status ig-ai-status-standby">
                    <div class="ig-status-dot-standby"></div>
                    <div>
                        <div style="font-size:0.75rem;color:var(--text-muted);font-weight:600;letter-spacing:0.04em;">SYSTEM STANDBY</div>
                        <div class="ig-ai-uptime">{uptime_text}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── 2. Premium Navigation Links ───────────────────────────────────────
        st.markdown(
            '<div class="ig-nav-section-header">OPERATIONS CENTER</div>',
            unsafe_allow_html=True,
        )

        # Notification dot for Live Detection when monitoring is active
        live_dot = '<span class="ig-nav-item-active-dot"></span>' if monitoring_active else ""

        st.markdown('<div class="ig-nav-item-wrap ig-nav-item-dashboard">', unsafe_allow_html=True)
        st.page_link("pages/1_Dashboard.py", label="🏠  Dashboard")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="ig-nav-item-wrap ig-nav-item-live">{live_dot}', unsafe_allow_html=True)
        st.page_link("pages/2_Live_Detection.py", label="🎥  Live Detection")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="ig-nav-item-wrap ig-nav-item-analytics">', unsafe_allow_html=True)
        st.page_link("pages/3_Analytics.py", label="📊  AI Analytics")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="ig-nav-item-wrap ig-nav-item-history">', unsafe_allow_html=True)
        st.page_link("pages/4_Incident_History.py", label="📜  Incident History")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="ig-nav-item-wrap ig-nav-item-settings">', unsafe_allow_html=True)
        st.page_link("pages/5_Settings.py", label="⚙️  Settings")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── 5. Logout Section ─────────────────────────────────────────────────
        st.markdown('<div class="ig-logout-section">', unsafe_allow_html=True)
        st.markdown('<div class="ig-divider" style="margin:0.75rem 0 0.75rem;"></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="ig-btn-logout">', unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True, key="sidebar_logout"):
            logout_user()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="ig-logout-hint">🔒 Session secured</div>',
            unsafe_allow_html=True,
 
        )

# ── Main content ──────────────────────────────────────────────────────────────
if is_authenticated():
    st.switch_page("pages/1_Dashboard.py")
else:
    # Two-column login layout - single viewport, no scrolling
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="auth-command-center">', unsafe_allow_html=True)
        
        # Branding
        st.markdown("# 🔥 InfernoGuard AI")
        st.markdown("**Enterprise Fire & Smoke Intelligence Platform**")
        st.caption("Real-Time Industrial Threat Detection powered by AI")
        
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
        
        # Live AI Status Grid - Compact 2x2
        st.markdown("#### 🎯 Live AI Status")
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        
        status_col1, status_col2 = st.columns(2, gap="small")
        
        with status_col1:
            st.markdown("""
            <div class="auth-status-card">
                <div class="auth-status-icon">🧠</div>
                <div class="auth-status-label">Detection Engine</div>
                <div class="auth-status-value">Operational</div>
                <div class="auth-status-sub">YOLOv8 Active</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="auth-status-card">
                <div class="auth-status-icon">🚨</div>
                <div class="auth-status-label">Alert System</div>
                <div class="auth-status-value">Active</div>
                <div class="auth-status-sub">Multi-Channel</div>
            </div>
            """, unsafe_allow_html=True)
        
        with status_col2:
            st.markdown("""
            <div class="auth-status-card">
                <div class="auth-status-icon">⚡</div>
                <div class="auth-status-label">Processing</div>
                <div class="auth-status-value">30+ FPS</div>
                <div class="auth-status-sub">Real-Time</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="auth-status-card">
                <div class="auth-status-icon">🎯</div>
                <div class="auth-status-label">AI Confidence</div>
                <div class="auth-status-value">97.3%</div>
                <div class="auth-status-sub">Enterprise Model</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
        
        # AI Features - Compact Grid
        st.markdown("#### 🛡️ AI Monitoring Features")
        st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)
        
        feat_col1, feat_col2 = st.columns(2, gap="small")
        with feat_col1:
            st.markdown("✓ Fire Detection")
            st.markdown("✓ Smoke Detection")
            st.markdown("✓ CCTV Monitoring")
        with feat_col2:
            st.markdown("✓ RTSP Analysis")
            st.markdown("✓ Multi-Channel Alerts")
            st.markdown("✓ Incident Analytics")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="auth-access-card">', unsafe_allow_html=True)
        
        # Auth header
        st.markdown("### 🔐 Secure Operations Access")
        st.markdown("Authenticate to access the InfernoGuard AI monitoring platform")
        
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        
        # Auth tabs
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])
        
        with tab_login:
            render_login_form()
        
        with tab_signup:
            render_signup_form()
        
        st.markdown('</div>', unsafe_allow_html=True)