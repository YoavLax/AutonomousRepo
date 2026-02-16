import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

DB_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "feature_usage.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feature_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_name TEXT NOT NULL,
            used_at TEXT NOT NULL,
            user_ip TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/api/feature-usage", methods=["POST"])
def log_feature_usage():
    """
    Log usage of a feature with timestamp and user IP.
    Expects JSON: { "feature_name": "string" }
    """
    data = request.get_json()
    feature_name = data.get("feature_name")
    user_ip = request.remote_addr
    if not feature_name:
        logger.warning("Feature name missing in request")
        return jsonify({"error": "feature_name required"}), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feature_usage (feature_name, used_at, user_ip) VALUES (?, ?, ?)",
            (feature_name, datetime.datetime.utcnow().isoformat(), user_ip)
        )
        conn.commit()
        conn.close()
        logger.info(f"Logged usage for feature: {feature_name} from IP: {user_ip}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error logging feature usage: {e}")
        return jsonify({"error": "internal error"}), 500

@app.route("/api/feature-usage", methods=["GET"])
def get_feature_usage():
    """
    Retrieve usage logs for all features.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT feature_name, used_at, user_ip FROM feature_usage ORDER BY used_at DESC")
        rows = cursor.fetchall()
        conn.close()
        usage = [
            {"feature_name": row[0], "used_at": row[1], "user_ip": row[2]}
            for row in rows
        ]
        logger.info("Retrieved feature usage logs")
        return jsonify({"usage": usage}), 200
    except Exception as e:
        logger.error(f"Error retrieving feature usage: {e}")
        return jsonify({"error": "internal error"}), 500

def new_feature():
    '''Complete working code that extends existing functionality'''
    init_db()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()