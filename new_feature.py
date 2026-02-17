import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
from autonomous_agent import ExecutionLog
import datetime

def get_recent_executions(limit: int = 10):
    """Fetch recent execution logs from the database."""
    db_path = "execution_log.db"
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, timestamp, action, status, details FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "action": row[2],
                "status": row[3],
                "details": row[4],
            }
            for row in rows
        ]
    finally:
        conn.close()

def new_feature():
    '''Adds an API endpoint to fetch recent execution logs from the autonomous agent'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-executions", methods=["GET"])
    def recent_executions():
        try:
            limit = int(request.args.get("limit", 10))
            logs = get_recent_executions(limit)
            logger.info(f"Fetched {len(logs)} recent executions")
            return jsonify({"success": True, "executions": logs})
        except Exception as e:
            logger.error(f"Error fetching recent executions: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()