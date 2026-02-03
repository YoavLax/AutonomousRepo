import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def get_log_entries(limit: int = 20):
    """Fetch recent execution log entries from the SQLite database."""
    db_path = "execution_log.db"
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT timestamp, action, status, details FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {
                "timestamp": row[0],
                "action": row[1],
                "status": row[2],
                "details": row[3],
            }
            for row in rows
        ]
    finally:
        conn.close()

def create_log_viewer_api():
    """Create a Flask API endpoint to view recent execution logs."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "log_viewer.log"
    logger = setup_logger("log_viewer", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/logs", methods=["GET"])
    def get_logs():
        try:
            limit = int(request.args.get("limit", 20))
            logs = get_log_entries(limit)
            logger.info(f"Fetched {len(logs)} log entries")
            return jsonify({"logs": logs})
        except Exception as e:
            logger.error(f"Error fetching logs: {e}")
            return jsonify({"error": str(e)}), 500

    return app

def new_feature():
    '''Run a Flask server exposing an endpoint to view recent execution logs.'''
    app = create_log_viewer_api()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()