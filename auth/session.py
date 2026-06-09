"""
Session management for InfernoGuard AI.
Manages Streamlit session state for authentication.
"""

import streamlit as st
from utils.logger import get_logger

logger = get_logger(__name__)

SESSION_KEY = "authenticated_user"


def is_authenticated() -> bool:
    """Return True if a user is currently logged in."""
    return st.session_state.get(SESSION_KEY) is not None


def login_user(username: str) -> None:
    """
    Mark the session as authenticated for the given username.

    Args:
        username: The username of the successfully authenticated user.
    """
    st.session_state[SESSION_KEY] = username
    logger.info(f"User logged in: {username}")


def logout_user() -> None:
    """Clear the authenticated session and redirect to the login page."""
    username = st.session_state.pop(SESSION_KEY, None)
    if username:
        logger.info(f"User logged out: {username}")
    st.switch_page("app.py")


def require_auth() -> None:
    """
    Redirect unauthenticated users to the login page.
    Call this at the top of every protected page.
    """
    if not is_authenticated():
        st.switch_page("app.py")
