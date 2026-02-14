import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_db_connection(db_path: str = "execution_log.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_recent_logs(limit: int = 10) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT timestamp, action, status, details FROM execution_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def new_feature():
    """
    Adds a Flask API endpoint to serve recent execution logs from the autonomous agent's log database.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-logs", methods=["GET"])
    def recent_logs():
        try:
            limit = int(request.args.get("limit", 10))
            logs = fetch_recent_logs(limit)
            logger.info(f"Fetched {len(logs)} recent logs.")
            return jsonify({"logs": logs}), 200
        except Exception as e:
            logger.error(f"Error fetching recent logs: {e}")
            return jsonify({"error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()