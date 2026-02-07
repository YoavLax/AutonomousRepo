import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_log_stats(db_path: str = "execution_log.db"):
    """Return statistics about the autonomous agent's execution log."""
    if not os.path.exists(db_path):
        return {"error": "Log database not found."}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM execution_log")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT status, COUNT(*) FROM execution_log GROUP BY status")
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM execution_log")
        min_ts, max_ts = cursor.fetchone()
        stats = {
            "total_executions": total,
            "status_counts": status_counts,
            "first_execution": min_ts,
            "last_execution": max_ts
        }
        return stats
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

def create_log_stats_api():
    """Create a Flask API endpoint to serve execution log statistics."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("log_stats_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/log-stats", methods=["GET"])
    def log_stats():
        stats = get_log_stats()
        if "error" in stats:
            logger.error(f"Failed to get log stats: {stats['error']}")
            return jsonify({"error": stats["error"]}), 500
        logger.info("Log stats retrieved successfully")
        return jsonify(stats)

    return app

def new_feature():
    '''Run a Flask API server that provides statistics about the autonomous agent's execution log.'''
    app = create_log_stats_api()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()