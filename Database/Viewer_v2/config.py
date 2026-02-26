"""
Configuration file for DB Viewer application.
Defines paths and constants only.
Colors are now in styles/colors.py
"""

import os
from pathlib import Path

# ============== PATHS ==============
# Base directory: E_Zavod/Python/Database/Viewer_v2/
BASE_DIR = Path(__file__).parent
# Go up to Python directory for main app
PYTHON_DIR = BASE_DIR.parent.parent
# Database directory
DATABASE_DIR = PYTHON_DIR / "Database"

# File paths - ABSOLUTE PATHS
DB_PATH = DATABASE_DIR / "Factory.db"
ICON_PATH = PYTHON_DIR / "icone.ico"
LOGS_PATH = DATABASE_DIR / "Logs.txt"
MAIN_APP_PATH = PYTHON_DIR / "main.py"

# ============== CONSTANTS ==============
# UI Dimensions
SIDE_MENU_WIDTH = 300               # Fixed width for side menu
TABLE_ROW_HEIGHT = 30               # Default row height for tables
TABLE_COLUMN_MIN_WIDTH = 100        # Minimum column width
TAB_ARROW_SIZE = 40                 # Size of tab navigation arrows (section 2.2.2)

# Application settings
APP_NAME = "E_Zavod Database Viewer"
APP_VERSION = "2.0"
DEFAULT_WINDOW_WIDTH = 1600
DEFAULT_WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Database settings
MAX_TABLE_ROWS_PREVIEW = 1000       # Limit for initial table load