import os
import sqlite3
from flask import Flask, request, jsonify
from typing import Optional, Dict, Any
from datetime import datetime
from logging_utils import setup_logger

def get_db_connection(db_path: str = "execution_log.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_recent_executions(limit: int = 10) -> list:
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

def create_app():
    app = Flask(__name__)
    LOG_PATH = os.path.join(os.getcwd(), "new_feature.log")
    logger = setup_logger("new_feature", LOG_PATH, level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/recent-executions", methods=["GET"])
    def recent_executions():
        """
        API endpoint to fetch recent execution log entries.
        Query param: limit (optional, default 10)
        """
        try:
            limit = int(request.args.get("limit", 10))
            logger.info(f"Fetching {limit} recent executions")
            entries = get_recent_executions(limit)
            return jsonify({"success": True, "executions": entries})
        except Exception as e:
            logger.error(f"Error fetching recent executions: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    return app

def new_feature():
    '''Run a Flask server exposing an endpoint to view recent execution logs'''
    app = create_app()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()