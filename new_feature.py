import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_execution_stats(db_path: str = "execution_log.db"):
    """Fetch execution statistics from the autonomous agent's log database."""
    if not os.path.exists(db_path):
        return {"error": "Execution log database not found."}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM execution_log")
        total_runs = cursor.fetchone()[0]
        cursor.execute("SELECT status, COUNT(*) FROM execution_log GROUP BY status")
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT MAX(timestamp) FROM execution_log")
        last_run = cursor.fetchone()[0]
        stats = {
            "total_runs": total_runs,
            "status_counts": status_counts,
            "last_run": last_run
        }
        return stats
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

def create_stats_api():
    """Create a Flask API endpoint to serve execution statistics."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/execution-stats", methods=["GET"])
    def execution_stats():
        stats = get_execution_stats()
        if "error" in stats:
            logger.error(f"Error fetching stats: {stats['error']}")
            return jsonify({"error": stats["error"]}), 500
        logger.info("Execution stats served successfully.")
        return jsonify(stats)

    return app

def new_feature():
    '''Run a Flask server exposing an API endpoint for execution statistics.'''
    app = create_stats_api()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()