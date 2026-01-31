import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
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
    except sqlite3.OperationalError:
        return {"total_entries": 0, "last_entry": None}
    finally:
        conn.close()

def create_stats_api():
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/execution-log-stats", methods=["GET"])
    def execution_log_stats():
        """API endpoint to get execution log statistics."""
        stats = get_log_stats()
        logger.info(f"Fetched execution log stats: {stats}")
        return jsonify(stats)

    return app

def new_feature():
    '''Starts a Flask API to provide execution log statistics'''
    app = create_stats_api()
    port = int(os.getenv("NEW_FEATURE_PORT", 5050))
    print(f"Starting Execution Log Stats API on port {port}...")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    new_feature()