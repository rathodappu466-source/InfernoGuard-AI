"""
Database operations module for InfernoGuard AI.
Provides connection management and CRUD operations for all tables.
"""

import sqlite3
from typing import Optional
from utils.config import DB_PATH
from utils.logger import get_logger
from database.schema import USERS_TABLE, INCIDENTS_TABLE, SETTINGS_TABLE

logger = get_logger(__name__)


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initialize the database by creating all tables and inserting default settings.
    Creates Users, Incidents, and Settings tables if they don't exist.
    Ensures Settings table has exactly one row with default values.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute(USERS_TABLE)
        cursor.execute(INCIDENTS_TABLE)
        cursor.execute(SETTINGS_TABLE)
        
        # Insert default settings row if it doesn't exist
        cursor.execute("SELECT COUNT(*) FROM Settings WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO Settings (id) VALUES (1)
            """)
            logger.info("Created default settings row")
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def create_user(username: str, email: str, password_hash: str) -> bool:
    """
    Create a new user in the database.
    
    Args:
        username: Unique username
        email: Unique email address
        password_hash: Bcrypt-hashed password
    
    Returns:
        bool: True if user created successfully, False if username/email already exists
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO Users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, created_at))
        
        conn.commit()
        conn.close()
        logger.info(f"User created: {username}")
        return True
    except sqlite3.IntegrityError as e:
        logger.warning(f"Failed to create user {username}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise


def get_user_by_username(username: str) -> Optional[dict]:
    """
    Retrieve a user by username.
    
    Args:
        username: Username to look up
    
    Returns:
        dict | None: User record as dict with keys (id, username, email, password_hash, created_at)
                     or None if not found
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, password_hash, created_at
            FROM Users
            WHERE username = ?
        """, (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Error retrieving user {username}: {e}")
        raise


def log_incident(incident_type: str, confidence: float, timestamp: str, screenshot_path: str) -> int:
    """
    Log a detection incident to the database.
    
    Args:
        incident_type: Type of detection ('fire' or 'smoke')
        confidence: Confidence score (0.0-1.0)
        timestamp: ISO format timestamp string
        screenshot_path: Path to saved screenshot
    
    Returns:
        int: ID of the inserted incident record
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Incidents (type, confidence, timestamp, screenshot_path)
            VALUES (?, ?, ?, ?)
        """, (incident_type, confidence, timestamp, screenshot_path))
        
        incident_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Incident logged: {incident_type} at {timestamp} with confidence {confidence}")
        return incident_id
    except Exception as e:
        logger.error(f"Error logging incident: {e}")
        raise


def get_all_incidents() -> list[dict]:
    """
    Retrieve all incidents from the database.
    
    Returns:
        list[dict]: List of incident records, each with keys (id, type, confidence, timestamp, screenshot_path)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, type, confidence, timestamp, screenshot_path
            FROM Incidents
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error retrieving all incidents: {e}")
        raise


def get_recent_incidents(n: int) -> list[dict]:
    """
    Retrieve the n most recent incidents.
    
    Args:
        n: Number of recent incidents to retrieve
    
    Returns:
        list[dict]: List of incident records, each with keys (id, type, confidence, timestamp, screenshot_path)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, type, confidence, timestamp, screenshot_path
            FROM Incidents
            ORDER BY timestamp DESC
            LIMIT ?
        """, (n,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error retrieving recent incidents: {e}")
        raise


def get_settings() -> dict:
    """
    Retrieve the current settings from the database.
    
    Returns:
        dict: Settings record with all configuration values
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM Settings WHERE id = 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        else:
            # Should never happen if init_db() was called
            logger.error("Settings row not found")
            raise ValueError("Settings not initialized")
    except Exception as e:
        logger.error(f"Error retrieving settings: {e}")
        raise


def update_settings(key: str, value) -> None:
    """
    Update a specific setting in the database.
    
    Args:
        key: Setting key (column name)
        value: New value for the setting
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query with column name validation
        valid_columns = {
            'alert_enabled', 'sound_enabled', 'email_enabled', 'telegram_enabled',
            'confidence_threshold', 'email_recipient', 'email_sender', 'email_password',
            'smtp_host', 'smtp_port', 'rtsp_url', 'telegram_token', 'telegram_chat_id'
        }
        
        if key not in valid_columns:
            raise ValueError(f"Invalid settings key: {key}")
        
        query = f"UPDATE Settings SET {key} = ? WHERE id = 1"
        cursor.execute(query, (value,))
        
        conn.commit()
        conn.close()
        logger.info(f"Setting updated: {key} = {value}")
    except Exception as e:
        logger.error(f"Error updating setting {key}: {e}")
        raise
