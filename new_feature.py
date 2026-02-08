import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_user_feedback(feedback: str, rating: int, db_path: str = "user_feedback.db") -> None:
    """Store user feedback and rating in a SQLite database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback TEXT NOT NULL,
            rating INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    c.execute(
        "INSERT INTO feedback (feedback, rating, timestamp) VALUES (?, ?, ?)",
        (feedback, rating, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def create_feedback_api():
    """Create a Flask API endpoint for collecting user feedback."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "user_feedback.log"
    logger = setup_logger("user_feedback_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/submit-feedback", methods=["POST"])
    def submit_feedback():
        data = request.get_json()
        feedback = data.get("feedback")
        rating = data.get("rating")
        if not feedback or not isinstance(rating, int) or not (1 <= rating <= 5):
            logger.warning("Invalid feedback submission: %s", data)
            return jsonify({"error": "Invalid input. 'feedback' (str) and 'rating' (1-5 int) required."}), 400
        try:
            log_user_feedback(feedback, rating)
            logger.info("Feedback received: %s | Rating: %d", feedback, rating)
            return jsonify({"message": "Feedback submitted successfully."}), 200
        except Exception as e:
            logger.error("Error saving feedback: %s", str(e))
            return jsonify({"error": "Failed to save feedback."}), 500

    return app

def new_feature():
    '''Run the user feedback API server'''
    app = create_feedback_api()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()