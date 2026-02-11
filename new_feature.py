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

def create_log_viewer_api():
    """Create a Flask app to serve recent execution logs via API."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
    logger = setup_logger("log_viewer_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-executions", methods=["GET"])
    def recent_executions():
        try:
            limit = int(request.args.get("limit", 10))
            logs = get_recent_executions(limit)
            return jsonify({"success": True, "logs": logs})
        except Exception as e:
            logger.error(f"Failed to fetch recent executions: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    return app

def new_feature():
    """
    Run a Flask API server that exposes recent execution logs from the autonomous agent.
    Endpoint: /api/recent-executions?limit=10
    """
    app = create_log_viewer_api()
    port = int(os.getenv("LOG_VIEWER_PORT", 5050))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    new_feature()