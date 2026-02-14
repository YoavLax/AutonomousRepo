import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
from autonomous_agent import ExecutionLog
import datetime

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

DB_PATH = os.getenv("EXEC_LOG_DB_PATH", "execution_log.db")

def get_recent_executions(limit: int = 10):
    """Fetch recent execution logs from the ExecutionLog database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, timestamp, action, status, details FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        executions = [
            {
                "id": row[0],
                "timestamp": row[1],
                "action": row[2],
                "status": row[3],
                "details": row[4]
            }
            for row in rows
        ]
        return executions
    finally:
        conn.close()

@app.route("/api/recent-executions", methods=["GET"])
def recent_executions():
    """
    API endpoint to fetch recent execution logs.
    Query param: limit (optional, default 10)
    """
    try:
        limit = int(request.args.get("limit", 10))
        executions = get_recent_executions(limit)
        logger.info(f"Fetched {len(executions)} recent executions")
        return jsonify({"executions": executions}), 200
    except Exception as e:
        logger.error(f"Error fetching recent executions: {e}")
        return jsonify({"error": str(e)}), 500

def new_feature():
    '''Run the Flask app to serve the recent executions API'''
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()