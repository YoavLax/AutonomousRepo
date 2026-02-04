import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_user_feedback(user_id: str, feedback: str, db_path: str = "user_feedback.db") -> None:
    """Logs user feedback into a SQLite database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            feedback TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    c.execute(
        "INSERT INTO feedback (user_id, feedback, timestamp) VALUES (?, ?, ?)",
        (user_id, feedback, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def create_feedback_api():
    """Creates a Flask API endpoint for collecting user feedback."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "user_feedback.log"
    logger = setup_logger("user_feedback_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/submit-feedback", methods=["POST"])
    def submit_feedback():
        data = request.get_json()
        user_id = data.get("user_id")
        feedback = data.get("feedback")
        if not user_id or not feedback:
            logger.warning("Missing user_id or feedback in request")
            return jsonify({"error": "user_id and feedback are required"}), 400
        try:
            log_user_feedback(user_id, feedback)
            logger.info(f"Feedback received from user {user_id}")
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logger.error(f"Error logging feedback: {e}")
            return jsonify({"error": "Failed to log feedback"}), 500

    return app

def new_feature():
    """Runs the user feedback API server."""
    app = create_feedback_api()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()