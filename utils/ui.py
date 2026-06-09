"""
Shared UI component utilities for InfernoGuard AI.
Provides reusable HTML components: footer, breadcrumbs, toasts, loading states, empty states.
"""

import streamlit as st


def render_page_footer(page_name: str = "") -> None:
    """Render the enterprise page footer with system info."""
    st.markdown(
        f"""
        <div class="ig-page-footer">
          <div class="ig-footer-left">
            <span class="ig-footer-brand">🔥 InfernoGuard AI</span>
            <span class="ig-footer-sep">·</span>
            <span class="ig-footer-version">Enterprise Edition v2.0</span>
          </div>
          <div class="ig-footer-center">
            <span class="ig-footer-page">{page_name}</span>
          </div>
          <div class="ig-footer-right">
            <span class="ig-footer-copy">© 2025 InfernoGuard AI. All rights reserved.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_breadcrumbs(crumbs: list[tuple[str, str]]) -> None:
    """
    Render a breadcrumb trail.
    crumbs: list of (label, icon) tuples, e.g. [("Dashboard", "🏠"), ("Analytics", "📊")]
    """
    parts = []
    for i, (label, icon) in enumerate(crumbs):
        is_last = i == len(crumbs) - 1
        if is_last:
            parts.append(
                f'<span class="ig-breadcrumb-item ig-breadcrumb-active">{icon} {label}</span>'
            )
        else:
            parts.append(
                f'<span class="ig-breadcrumb-item">{icon} {label}</span>'
                f'<span class="ig-breadcrumb-sep">›</span>'
            )
    st.markdown(
        f'<div class="ig-breadcrumbs">{"".join(parts)}</div>',
        unsafe_allow_html=True,
    )


def render_toast(message: str, toast_type: str = "success") -> None:
    """
    Render an inline toast notification banner.
    toast_type: 'success', 'error', 'warning', 'info'
    """
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    classes = {
        "success": "ig-toast ig-toast-success",
        "error":   "ig-toast ig-toast-error",
        "warning": "ig-toast ig-toast-warning",
        "info":    "ig-toast ig-toast-info",
    }
    icon = icons.get(toast_type, "ℹ️")
    cls  = classes.get(toast_type, "ig-toast ig-toast-info")
    st.markdown(
        f'<div class="{cls}" style="position:relative;bottom:auto;right:auto;'
        f'margin-bottom:1rem;animation:slideInDown 0.35s ease forwards;">'
        f'{icon} {message}</div>',
        unsafe_allow_html=True,
    )


def render_empty_state(
    icon: str = "📭",
    title: str = "No Data Available",
    description: str = "Start the system to begin collecting data.",
    action_hint: str = "",
) -> None:
    """Render a styled empty state card."""
    action_html = (
        f'<div class="ig-empty-state-action">{action_hint}</div>'
        if action_hint
        else ""
    )
    st.markdown(
        f"""
        <div class="ig-empty-state-card">
          <div class="ig-empty-state-icon">{icon}</div>
          <div class="ig-empty-state-title">{title}</div>
          <div class="ig-empty-state-desc">{description}</div>
          {action_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_loading_skeleton(rows: int = 3, card: bool = False) -> None:
    """Render shimmer loading skeleton rows or a card skeleton."""
    if card:
        st.markdown(
            '<div class="ig-skeleton ig-skeleton-card"></div>',
            unsafe_allow_html=True,
        )
        return
    lines = "".join(
        f'<div class="ig-skeleton ig-skeleton-text" style="width:{w}%;"></div>'
        for w in ([100, 85, 70][:rows])
    )
    st.markdown(
        f'<div style="padding:0.5rem 0;">{lines}</div>',
        unsafe_allow_html=True,
    )


def render_section_divider(label: str = "") -> None:
    """Render a styled section divider, optionally with a centered label."""
    if label:
        st.markdown(
            f"""
            <div class="ig-section-divider">
              <div class="ig-section-divider-line"></div>
              <span class="ig-section-divider-label">{label}</span>
              <div class="ig-section-divider-line"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="ig-divider"></div>', unsafe_allow_html=True)


def render_tooltip_badge(text: str, tooltip: str, badge_class: str = "info") -> str:
    """
    Return HTML for a badge with a tooltip on hover.
    Usage: st.markdown(render_tooltip_badge("LIVE", "System is actively monitoring"), unsafe_allow_html=True)
    """
    return (
        f'<span class="ig-badge {badge_class} ig-tooltip-wrap">'
        f'{text}'
        f'<span class="ig-tooltip-text">{tooltip}</span>'
        f'</span>'
    )
