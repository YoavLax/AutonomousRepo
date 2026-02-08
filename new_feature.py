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

def fetch_recent_executions(limit: int = 10):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, timestamp, action, status, details FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def new_feature():
    """
    Flask API endpoint to fetch the most recent execution logs from the autonomous agent.
    Extends the project by providing visibility into recent agent actions for monitoring/debugging.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-executions", methods=["GET"])
    def recent_executions():
        try:
            limit = int(request.args.get("limit", 10))
            logs = fetch_recent_executions(limit)
            logger.info(f"Fetched {len(logs)} recent executions.")
            return jsonify({"success": True, "logs": logs})
        except Exception as e:
            logger.error(f"Error fetching recent executions: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()