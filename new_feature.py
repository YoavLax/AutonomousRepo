import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
from autonomous_agent import ExecutionLog
import datetime

def get_log_stats(db_path: str = "execution_log.db"):
    """Return statistics about the execution log: total entries, last entry timestamp."""
    if not os.path.exists(db_path):
        return {"total_entries": 0, "last_entry": None}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*), MAX(timestamp) FROM execution_log")
        total, last = cursor.fetchone()
        return {"total_entries": total, "last_entry": last}
    finally:
        conn.close()

def new_feature():
    '''Adds a Flask endpoint to report execution log statistics'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
    logger = setup_logger("log_stats_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/log-stats", methods=["GET"])
    def log_stats():
        stats = get_log_stats()
        logger.info(f"Log stats requested: {stats}")
        return jsonify(stats)

    port = int(os.getenv("LOG_STATS_PORT", 5050))
    logger.info(f"Starting log stats API on port {port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    new_feature()