import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_log_stats(db_path: str = "execution_log.db"):
    """Fetch summary statistics from the execution log database."""
    if not os.path.exists(db_path):
        return {"error": "Log database not found."}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM execution_log")
        total_entries = cursor.fetchone()[0]
        cursor.execute("SELECT level, COUNT(*) FROM execution_log GROUP BY level")
        level_counts = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM execution_log")
        min_ts, max_ts = cursor.fetchone()
        conn.close()
        return {
            "total_entries": total_entries,
            "level_counts": level_counts,
            "first_entry": min_ts,
            "last_entry": max_ts
        }
    except Exception as e:
        return {"error": str(e)}

def create_log_stats_api():
    """Create a Flask app exposing an endpoint for log statistics."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "aut