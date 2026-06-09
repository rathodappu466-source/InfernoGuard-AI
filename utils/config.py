"""
Central configuration store for InfernoGuard AI.
All file paths, model paths, database paths, default thresholds,
and feature flags are defined here as constants.
"""

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Model configuration
MODEL_PATH: str = os.path.join(BASE_DIR, "models", "best.pt")

# Database configuration
DB_PATH: str = os.path.join(BASE_DIR, "database", "infernoguard.db")

# Screenshots directory
SCREENSHOTS_DIR: str = os.path.join(BASE_DIR, "screenshots")

# Log file path
LOG_FILE: str = os.path.join(BASE_DIR, "infernoguard.log")

# Detection defaults
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5

# Alert cooldown in seconds (suppress duplicate alerts within this window)
ALERT_COOLDOWN_SECONDS: int = 30
