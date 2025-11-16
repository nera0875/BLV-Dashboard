"""Vercel serverless entry point for BLV Dashboard"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

# Vercel expects a variable named 'app' or a handler function
# Flask app is already named 'app' so it will be auto-detected
