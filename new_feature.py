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

def fetch_recent_logs(limit: int = 10):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT timestamp, action, status, details FROM execution_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        return [
            {
                "timestamp": row["timestamp"],
                "action": row["action"],
                "status": row["status"],
                "details": row["details"]
            }
            for row in rows
        ]
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
            logger.error(f"Failed to fetch logs: {e}")
            return jsonify({"error": "Failed to fetch logs"}), 500

    @app.route("/dashboard/logs", methods=["GET"])
    def logs_dashboard():
        try:
            logs = fetch_recent_logs(20)
            html = "<h2>Recent Execution Logs</h2><table border='1'><tr><th>Timestamp</th><th>Action</th><th>Status</th><th>Details</th></tr>"
            for log in logs:
                html += f"<tr><td>{log['timestamp']}</td><td>{log['action']}</td><td>{log['status']}</td><td>{log['details']}</td></tr>"
            html += "</table>"
            return html
        except Exception as e:
            logger.error(f"Failed to render dashboard: {e}")
            return "<h2>Error loading dashboard</h2>", 500

    return app

def new_feature():
    '''Run a Flask server that provides a dashboard and API for recent execution logs'''
    app = create_log_dashboard_app()
    port = int(os.getenv("LOG_DASHBOARD_PORT", 5050))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    new_feature()