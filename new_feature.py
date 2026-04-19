import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import sqlite3
import datetime

# Feature: User Feedback API Endpoint
# This feature adds an endpoint to collect user feedback, analyze its sentiment, and store it in a feedback log.

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "feedback.log"
logger = setup_logger("feedback_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))
DB_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "feedback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user TEXT,
            feedback TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            polarity REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/api/submit-feedback", methods=["POST"])
def submit_feedback():
    """
    Accepts user feedback, analyzes sentiment, stores it in the database, and logs the event.
    Expects JSON: { "user": "username", "feedback": "text" }
    """
    data = request.get_json(force=True)
    user = data.get("user", "anonymous")
    feedback = data.get("feedback", "")
    if not feedback.strip():
        logger.warning("Empty feedback received")
        return jsonify({"error": "Feedback cannot be empty"}), 400

    analysis = TextBlob(feedback)
    polarity = analysis.sentiment.polarity
    sentiment = (
        "positive" if polarity > 0.1 else
        "negative" if polarity < -0.1 else
        "neutral"
    )

    timestamp = datetime.datetime.utcnow().isoformat()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO feedback (timestamp, user, feedback, sentiment, polarity) VALUES (?, ?, ?, ?, ?)",
            (timestamp, user, feedback, sentiment, polarity)
        )
        conn.commit()
        conn.close()
        logger.info(f"Feedback stored: user={user}, sentiment={sentiment}, polarity={polarity:.2f}")
        return jsonify({
            "message": "Feedback submitted successfully",
            "sentiment": sentiment,
            "polarity": polarity
        }), 200
    except Exception as e:
        logger.error(f"Error storing feedback: {e}")
        return jsonify({"error": "Internal server error"}), 500

def new_feature():
    '''Starts the feedback API server with the new endpoint'''
    init_db()
    logger.info("Starting Feedback API server on http://127.0.0.1:5001")
    app.run(port=5001)

if __name__ == "__main__":
    new_feature()