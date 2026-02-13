import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_log_stats(db_path: str = "execution_log.db"):
    """Return statistics about the execution log: total entries, last entry timestamp, and error count."""
    if not os.path.exists(db_path):
        return {
            "total_entries": 0,
            "last_entry": None,
            "error_count": 0
        }
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM execution_log")
        total_entries = cursor.fetchone()[0]
        cursor.execute("SELECT timestamp FROM execution_log ORDER BY timestamp DESC LIMIT 1")
        last_entry = cursor.fetchone()
        last_entry = last_entry[0] if last_entry else None
        cursor.execute("SELECT COUNT(*) FROM execution_log WHERE level='ERROR'")
        error_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        # Table does not exist
        total_entries = 0
        last_entry = None
        error_count = 0
    finally:
        conn.close()
    return {
        "total_entries": total_entries,
        "last_entry": last_entry,
        "error_count": error_count
    }

def new_feature():
    '''Adds a Flask API endpoint to report execution log statistics'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
    logger = setup_logger("log_stats_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/log-stats", methods=["GET"])
    def log_stats():
        db_path = os.getenv("EXEC_LOG_DB_PATH", "execution_log.db")
        stats = get_log_stats(db_path)
        logger.info(f"Log stats requested: {stats}")
        return jsonify(stats)

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()