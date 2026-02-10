import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_recent_executions(limit: int = 10):
    """Fetch recent execution logs from the autonomous agent's database."""
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

def create_log_viewer_app():
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("log_viewer", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-executions", methods=["GET"])
    def recent_executions():
        """API endpoint to fetch recent execution logs."""
        try:
            limit = int(request.args.get("limit", 10))
            logs = get_recent_executions(limit)
            return jsonify({"success": True, "logs": logs})
        except Exception as e:
            logger.error(f"Failed to fetch recent executions: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/dashboard/logs", methods=["GET"])
    def dashboard_logs():
        """Simple HTML dashboard to view recent execution logs."""
        logs = get_recent_executions(20)
        html = "<h2>Recent Execution Logs</h2><table border='1'><tr><th>ID</th><th>Timestamp</th><th>Action</th><th>Status</th><th>Details</th></tr>"
        for log in logs:
            html += f"<tr><td>{log['id']}</td><td>{log['timestamp']}</td><td>{log['action']}</td><td>{log['status']}</td><td>{log['details']}</td></tr>"
        html += "</table>"
        return html

    return app

def new_feature():
    '''Run a Flask server providing an API and dashboard for recent execution logs.'''
    app = create_log_viewer_app()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()