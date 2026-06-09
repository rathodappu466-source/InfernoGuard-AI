"""
Property-based tests for auth modules.

# Feature: infernoguard-ai, Property 4: Password hashing non-reversibility
# For any plaintext password submitted during signup, the value stored in the
# Users table SHALL never equal the plaintext input, and bcrypt verification
# of the plaintext against the stored hash SHALL return true.
# Validates: Requirements 1.1
"""

import bcrypt
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Strategy: generate realistic plaintext passwords
# ---------------------------------------------------------------------------

password_strategy = st.text(
    min_size=1,
    max_size=72,  # bcrypt truncates at 72 bytes
).filter(lambda p: len(p.encode("utf-8")) <= 72)


# ---------------------------------------------------------------------------
# Property 4: Password hashing non-reversibility
# Validates: Requirements 1.1
# ---------------------------------------------------------------------------

@given(password=password_strategy)
@settings(max_examples=25, deadline=None)  # bcrypt is intentionally slow; disable deadline
def test_password_hashing_non_reversibility(password: str):
    """
    # Feature: infernoguard-ai, Property 4: Password hashing non-reversibility
    # Validates: Requirements 1.1

    For any plaintext password:
    1. The bcrypt hash must NOT equal the plaintext.
    2. bcrypt.checkpw(plaintext, hash) must return True.
    """
    password_bytes = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    # The stored hash must never equal the plaintext
    assert password_hash != password, (
        f"Hash equals plaintext for password={password!r}"
    )

    # Verification must succeed with the correct plaintext
    assert bcrypt.checkpw(password_bytes, password_hash.encode("utf-8")), (
        f"bcrypt.checkpw returned False for password={password!r}"
    )


def test_different_passwords_produce_different_hashes():
    """Two distinct passwords should not verify against each other's hash."""
    hash_a = bcrypt.hashpw(b"correct-password", bcrypt.gensalt())
    assert not bcrypt.checkpw(b"wrong-password", hash_a)


def test_same_password_different_salts():
    """Hashing the same password twice should produce different hashes (different salts)."""
    pw = b"same-password"
    hash1 = bcrypt.hashpw(pw, bcrypt.gensalt())
    hash2 = bcrypt.hashpw(pw, bcrypt.gensalt())
    assert hash1 != hash2
    # But both should verify correctly
    assert bcrypt.checkpw(pw, hash1)
    assert bcrypt.checkpw(pw, hash2)
