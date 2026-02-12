import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
from typing import Any, Dict, List

def get_recent_executions(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch recent execution logs from the autonomous agent's SQLite DB."""
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

def create_dashboard_app():
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "dashboard_feature.log"
    logger = setup_logger("dashboard_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-executions", methods=["GET"])
    def recent_executions():
        try:
            limit = int(request.args.get("limit", 10))
            logs = get_recent_executions(limit)
            return jsonify({"success": True, "logs": logs})
        except Exception as e:
            logger.error(f"Error fetching recent executions: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        # Simple HTML dashboard for recent executions
        logs = get_recent_executions(20)
        html = """
        <html>
        <head>
            <title>Autonomous Agent Execution Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                th { background: #f4f4f4; }
                tr:nth-child(even) { background: #fafafa; }
            </style>
        </head>
        <body>
            <h1>Recent Autonomous Agent Executions</h1>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Timestamp</th>
                    <th>Action</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
        """
        for log in logs:
            html += f"""
                <tr>
                    <td>{log['id']}</td>
                    <td>{log['timestamp']}</td>
                    <td>{log['action']}</td>
                    <td>{log['status']}</td>
                    <td>{log['details']}</td>
                </tr>
            """
        html += """
            </table>
        </body>
        </html>
        """
        return html

    return app

def new_feature():
    '''Run a Flask dashboard to view recent autonomous agent executions'''
    app = create_dashboard_app()
    port = int(os.getenv("DASHBOARD_PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    new_feature()