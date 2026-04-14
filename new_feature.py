import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import sqlite3
import datetime

# Feature: User Feedback Sentiment Logging API
# This Flask app endpoint allows users to submit feedback, analyzes sentiment, and logs it to a SQLite DB.

DB_PATH = "user_feedback.db"
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "user_feedback.log"
logger = setup_logger("user_feedback", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            polarity REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def analyze_sentiment(text: str):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return sentiment, polarity

app = Flask(__name__)

@app.route("/api/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    feedback = data.get("feedback", "")
    if not feedback or not isinstance(feedback, str):
        logger.warning("Invalid feedback submission")
        return jsonify({"error": "Feedback must be a non-empty string."}), 400

    sentiment, polarity = analyze_sentiment(feedback)
    timestamp = datetime.datetime.utcnow().isoformat()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO feedback (feedback, sentiment, polarity, timestamp) VALUES (?, ?, ?, ?)",
            (feedback, sentiment, polarity, timestamp)
        )
        conn.commit()
        conn.close()
        logger.info(f"Feedback logged: {feedback} | Sentiment: {sentiment} | Polarity: {polarity}")
        return jsonify({
            "message": "Feedback received.",
            "sentiment": sentiment,
            "polarity": polarity
        }), 200
    except Exception as e:
        logger.error(f"DB error: {e}")
        return jsonify({"error": "Internal server error."}), 500

@app.route("/api/feedback-stats", methods=["GET"])
def feedback_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT sentiment, COUNT(*) FROM feedback GROUP BY sentiment")
        stats = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": "Internal server error."}), 500

def new_feature():
    """
    Starts the Flask app for user feedback sentiment logging.
    """
    init_db()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()