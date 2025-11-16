"""Configuration for BLV Dashboard"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.urandom(24)
    DEBUG = True

    # SQLite
    DB_FILE = os.getenv('DB_FILE', 'blv_dashboard.db')
