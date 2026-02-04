import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_log_stats(db_path: str = "execution_log.db"):
    """
    Summarize execution log statistics: total runs, last run time, and error count.
    """
    if not os.path.exists(db_path):
        return {
            "total_runs": 0,
            "last_run": None,
            "error_count": 0
        }
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM execution_log")
        total_runs = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(timestamp) FROM execution_log")
        last_run = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM execution_log WHERE status = 'error'")
        error_count = cursor.fetchone()[0]
    except sqlite3.Error:
        total_runs = 0
        last_run = None
        error_count = 0
    finally:
        conn.close()
    return {
        "total_runs": total_runs,
        "last_run": last_run,
        "error_count": error_count
    }

def create_stats_api():
    """
    Create a Flask API endpoint to serve execution log statistics.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent_stats.log"
    logger = setup_logger("stats_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/execution-log-stats", methods=["GET"])
    def execution_log_stats():
        stats = get_log_stats()
        logger.info(f"Stats requested: {stats}")
        return jsonify(stats)

    return app

def new_feature():
    """
    Run the stats API server for execution log statistics.
    """
    app = create_stats_api()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()