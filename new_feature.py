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
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM execution_log")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT level, COUNT(*) FROM execution_log GROUP BY level")
        by_level = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM execution_log")
        min_ts, max_ts = cursor.fetchone()
        conn.close()
        return {
            "total_entries": total,
            "by_level": by_level,
            "first_entry": min_ts,
            "last_entry": max_ts
        }
    except Exception as e:
        return {"error": str(e)}

def create_log_stats_api():
    """Create a Flask app exposing an endpoint for log statistics."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
    logger = setup_logger("log_stats_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/log-stats", methods=["GET"])
    def log_stats():
        db_path = request.args.get("db_path", "execution_log.db")
        stats = get_log_stats(db_path)
        logger.info(f"Log stats requested: {stats}")
        return jsonify(stats)

    return app

def new_feature():
    """
    Run a Flask server exposing /api/log-stats, which returns statistics
    about the autonomous agent's execution log database.
    """
    app = create_log_stats_api()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()