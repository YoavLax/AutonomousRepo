import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_user_feedback(db_path: str, feedback: str, timestamp: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        c.execute('INSERT INTO user_feedback (feedback, timestamp) VALUES (?, ?)', (feedback, timestamp))
        conn.commit()
    finally:
        conn.close()

def new_feature():
    """
    Flask API endpoint to collect user feedback and store it in a local SQLite database.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "user_feedback.log"
    logger = setup_logger("user_feedback_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))
    DB_PATH = str(Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "user_feedback.db")

    @app.route("/api/submit-feedback", methods=["POST"])
    def submit_feedback():
        data = request.get_json()
        feedback = data.get("feedback", "").strip()
        if not feedback:
            logger.warning("No feedback provided in request.")
            return jsonify({"error": "Feedback is required."}), 400
        timestamp = datetime.datetime.utcnow().isoformat()
        try:
            log_user_feedback(DB_PATH, feedback, timestamp)
            logger.info(f"Feedback received at {timestamp}: {feedback}")
            return jsonify({"message": "Feedback submitted successfully."}), 200
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return jsonify({"error": "Failed to save feedback."}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()