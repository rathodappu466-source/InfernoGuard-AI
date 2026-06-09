"""
InfernoGuard AI — Login form.
"""

import bcrypt
import streamlit as st

import database.db as db
from auth.session import login_user
from utils.logger import get_logger

logger = get_logger(__name__)


def render_login_form() -> None:
    """Render the login form."""
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_password")
        submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("⚠️ Please enter your username and password.")
            return

        user = db.get_user_by_username(username)

        if user is None:
            logger.warning("Login attempt for unknown user: %s", username)
            st.error("❌ Invalid username or password.")
            return

        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )

        if password_matches:
            login_user(username)
            logger.info("Successful login: %s", username)
            st.success("✅ Authentication successful. Redirecting…")
            st.switch_page("pages/1_Dashboard.py")
        else:
            logger.warning("Failed login attempt for user: %s", username)
            st.error("❌ Invalid username or password.")
