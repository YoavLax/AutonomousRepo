import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_log_entries(limit: int = 20):
    """Fetch the latest execution log entries from the autonomous agent's log database."""
    db_path = "execution_log.db"
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

def create_log_dashboard_app():
    """Create a Flask app that serves a dashboard of recent autonomous agent execution logs."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature_dashboard.log"
    logger = setup_logger("log_dashboard", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/logs", methods=["GET"])
    def get_logs():
        try:
            limit = int(request.args.get("limit", 20))
            logs = get_log_entries(limit)
            return jsonify({"logs": logs})
        except Exception as e:
            logger.error(f"Failed to fetch logs: {e}")
            return jsonify({"error": "Failed to fetch logs"}), 500

    @app.route("/dashboard/logs", methods=["GET"])
    def dashboard():
        # Simple HTML dashboard for viewing logs
        logs = get_log_entries(50)
        html = "<h2>Autonomous Agent Execution Log</h2><table border='1'><tr><th>Timestamp</th><th>Action</th><th>Status</th><th>Details</th></tr>"
        for log in logs:
            html += f"<tr><td>{log['timestamp']}</td><td>{log['action']}</td><td>{log['status']}</td><td>{log['details']}</td></tr>"
        html += "</table>"
        return html

    return app

def new_feature():
    '''Run a Flask server that provides a dashboard and API for recent autonomous agent execution logs.'''
    app = create_log_dashboard_app()
    app.run(host="0.0.0.0", port=5050, debug=True)

if __name__ == "__main__":
    new_feature()