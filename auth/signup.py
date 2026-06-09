"""
InfernoGuard AI — Signup form.
"""

import bcrypt
import streamlit as st

import database.db as db
from utils.logger import get_logger

logger = get_logger(__name__)


def render_signup_form() -> None:
    """Render the signup form."""
    
    with st.form("signup_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("👤 Username", placeholder="Choose a username", key="signup_username")
        with col2:
            email = st.text_input("✉️ Email", placeholder="your@company.com", key="signup_email")
        
        password = st.text_input("🔑 Password", type="password", placeholder="Create a password (min. 6 chars)", key="signup_password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat your password", key="signup_confirm")
        
        submitted = st.form_submit_button("✨ Create Account", use_container_width=True)

    if submitted:
        if not username or not email or not password:
            st.error("⚠️ All fields are required.")
            return

        if len(username) < 3:
            st.error("⚠️ Username must be at least 3 characters.")
            return

        if len(password) < 6:
            st.error("⚠️ Password must be at least 6 characters.")
            return

        if password != confirm_password:
            st.error("❌ Passwords do not match.")
            return

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        success = db.create_user(username, email, password_hash)

        if success:
            logger.info("New user registered: %s", username)
            st.success("✅ Account created successfully! You can now sign in.")
        else:
            st.error("❌ Username or email already exists. Please choose a different one.")
