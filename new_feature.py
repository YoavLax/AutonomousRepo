import os
import sqlite3
from flask import Flask, request, jsonify
from typing import Optional, Dict, Any
from datetime import datetime
from logging_utils import setup_logger

DB_PATH = os.getenv("EXECUTION_LOG_DB", "execution_log.db")
LOG_PATH = os.getenv("NEW_FEATURE_LOG", "new_feature.log")
logger = setup_logger("new_feature", LOG_PATH, level="INFO")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_recent_executions(limit: int = 10) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, timestamp, action, status, details FROM execution_log ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def add_execution_entry(action: str, status: str, details: str = ""):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO execution_log (timestamp, action, status, details) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), action, status, details),
        )
        conn.commit()
    finally:
        conn.close()

def create_execution_log_table():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

def new_feature():
    """
    Flask API endpoint to view and add execution log entries.
    GET /api/execution-log?limit=5  - returns recent log entries
    POST /api/execution-log {action, status, details} - adds a new log entry
    """
    create_execution_log_table()
    app = Flask(__name__)

    @app.route("/api/execution-log", methods=["GET"])
    def get_log():
        try:
            limit = int(request.args.get("limit", 10))
            logs = get_recent_executions(limit)
            logger.info(f"Fetched {len(logs)} execution log entries")
            return jsonify({"success": True, "logs": logs})
        except Exception as e:
            logger.error(f"Error fetching execution log: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/execution-log", methods=["POST"])
    def add_log():
        try:
            data = request.get_json(force=True)
            action = data.get("action")
            status = data.get("status")
            details = data.get("details", "")
            if not action or not status:
                return jsonify({"success": False, "error": "Missing 'action' or 'status'"}), 400
            add_execution_entry(action, status, details)
            logger.info(f"Added execution log entry: {action}, {status}")
            return jsonify({"success": True})
        except Exception as e:
            logger.error(f"Error adding execution log: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()