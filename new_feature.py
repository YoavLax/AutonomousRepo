import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_db_path():
    # Use the same DB path as ExecutionLog in autonomous_agent.py
    return "execution_log.db"

def fetch_recent_logs(limit: int = 10):
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, timestamp, action, status, details FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        logs = [
            {
                "id": row[0],
                "timestamp": row[1],
                "action": row[2],
                "status": row[3],
                "details": row[4]
            }
            for row in rows
        ]
        return logs
    finally:
        conn.close()

def create_log_dashboard_app():
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "log_dashboard.log"
    logger = setup_logger("log_dashboard", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-logs", methods=["GET"])
    def recent_logs():
        try:
            limit = int(request.args.get("limit", 10))
            logs = fetch_recent_logs(limit)
            return jsonify({"logs": logs})
        except Exception as e:
            logger.error(f"Error fetching logs: {e}")
            return jsonify({"error": "Failed to fetch logs"}), 500

    @app.route("/dashboard/logs", methods=["GET"])
    def dashboard():
        # Simple HTML dashboard for recent logs
        logs = fetch_recent_logs(20)
        html = "<h2>Recent Execution Logs</h2><table border='1'><tr><th>ID</th><th>Timestamp</th><th>Action</th><th>Status</th><th>Details</th></tr>"
        for log in logs:
            html += f"<tr><td>{log['id']}</td><td>{log['timestamp']}</td><td>{log['action']}</td><td>{log['status']}</td><td>{log['details']}</td></tr>"
        html += "</table>"
        return html

    return app

def new_feature():
    '''Run a Flask server providing a dashboard and API for recent execution logs'''
    app = create_log_dashboard_app()
    app.run(host="0.0.0.0", port=5050, debug=True)

if __name__ == "__main__":
    new_feature()