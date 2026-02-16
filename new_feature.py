import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_db_path():
    # Use the same DB as ExecutionLog in autonomous_agent.py
    return "execution_log.db"

def fetch_recent_logs(limit: int = 10):
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT timestamp, action, status, details FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return [
            {
                "timestamp": row[0],
                "action": row[1],
                "status": row[2],
                "details": row[3]
            }
            for row in rows
        ]
    finally:
        conn.close()

def new_feature():
    """
    Adds a Flask API endpoint to serve recent execution logs from the autonomous agent.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-logs", methods=["GET"])
    def recent_logs():
        try:
            limit = int(request.args.get("limit", 10))
            logs = fetch_recent_logs(limit)
            logger.info(f"Fetched {len(logs)} recent logs")
            return jsonify({"logs": logs}), 200
        except Exception as e:
            logger.error(f"Error fetching logs: {e}")
            return jsonify({"error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()