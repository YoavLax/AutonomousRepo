import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import sqlite3
import datetime

DB_PATH = "feedback.db"
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "user_feedback.log"
logger = setup_logger("user_feedback", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            feedback TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            polarity REAL NOT NULL
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

def save_feedback(feedback: str, sentiment: str, polarity: float):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO feedback (timestamp, feedback, sentiment, polarity) VALUES (?, ?, ?, ?)",
        (datetime.datetime.utcnow().isoformat(), feedback, sentiment, polarity)
    )
    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__)

    @app.route("/api/submit-feedback", methods=["POST"])
    def submit_feedback():
        data = request.get_json()
        feedback = data.get("feedback", "").strip()
        if not feedback:
            logger.warning("No feedback provided in request.")
            return jsonify({"error": "Feedback is required."}), 400
        sentiment, polarity = analyze_sentiment(feedback)
        save_feedback(feedback, sentiment, polarity)
        logger.info(f"Feedback received: '{feedback}' | Sentiment: {sentiment} ({polarity:.2f})")
        return jsonify({
            "message": "Feedback submitted successfully.",
            "sentiment": sentiment,
            "polarity": polarity
        }), 200

    @app.route("/api/feedback-summary", methods=["GET"])
    def feedback_summary():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT sentiment, COUNT(*) FROM feedback GROUP BY sentiment")
        summary = {row[0]: row[1] for row in c.fetchall()}
        c.execute("SELECT AVG(polarity) FROM feedback")
        avg_polarity = c.fetchone()[0]
        conn.close()
        return jsonify({
            "summary": summary,
            "average_polarity": avg_polarity
        })

    return app

def new_feature():
    """
    Launches a Flask API for collecting user feedback, analyzing sentiment,
    and providing a feedback summary endpoint.
    """
    init_db()
    app = create_app()
    logger.info("Starting User Feedback API server on http://127.0.0.1:5001")
    app.run(host="127.0.0.1", port=5001)

if __name__ == "__main__":
    new_feature()