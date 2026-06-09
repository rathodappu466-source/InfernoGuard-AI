"""
Database schema definitions for InfernoGuard AI.
Contains SQL DDL for Users, Incidents, and Settings tables.
"""

USERS_TABLE = """
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

INCIDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS Incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    confidence REAL NOT NULL,
    timestamp TEXT NOT NULL,
    screenshot_path TEXT
)
"""

SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    alert_enabled INTEGER DEFAULT 1,
    sound_enabled INTEGER DEFAULT 1,
    email_enabled INTEGER DEFAULT 0,
    telegram_enabled INTEGER DEFAULT 0,
    confidence_threshold REAL DEFAULT 0.5,
    email_recipient TEXT DEFAULT '',
    email_sender TEXT DEFAULT '',
    email_password TEXT DEFAULT '',
    smtp_host TEXT DEFAULT 'smtp.gmail.com',
    smtp_port INTEGER DEFAULT 587,
    rtsp_url TEXT DEFAULT '',
    telegram_token TEXT DEFAULT '',
    telegram_chat_id TEXT DEFAULT '',
    CHECK (id = 1)
)
"""
