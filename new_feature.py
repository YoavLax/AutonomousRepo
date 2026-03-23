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
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            feedback TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            polarity REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def analyze_sentiment(feedback: str):
    blob = TextBlob(feedback)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        sentiment = "positive"
    elif polarity < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return sentiment, polarity

def store_feedback(feedback: str, sentiment: str, polarity: float):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO feedback (timestamp, feedback, sentiment, polarity) VALUES (?, ?, ?, ?)",
        (datetime.datetime.utcnow().isoformat(), feedback, sentiment, polarity)
    )
    conn.commit()
    conn.close()

def get_feedback_summary():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sentiment, COUNT(*) FROM feedback GROUP BY sentiment")
    summary = {row[0]: row[1] for row in c.fetchall()}
    c.execute("SELECT AVG(polarity) FROM feedback")
    avg_polarity = c.fetchone()[0]
    conn.close()
    return summary, avg_polarity

app = Flask(__name__)

@app.route("/api/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    feedback = data.get("feedback", "")
    if not feedback:
        logger.warning("No feedback provided in request")
        return jsonify({"error": "Feedback is required"}), 400
    sentiment, polarity = analyze_sentiment(feedback)
    store_feedback(feedback, sentiment, polarity)
    logger.info(f"Received feedback: '{feedback}' | Sentiment: {sentiment} | Polarity: {polarity}")
    return jsonify({"message": "Feedback received", "sentiment": sentiment, "polarity": polarity})

@app.route("/api/feedback-summary", methods=["GET"])
def feedback_summary():
    summary, avg_polarity = get_feedback_summary()
    return jsonify({"summary": summary, "average_polarity": avg_polarity})

def new_feature():
    '''User Feedback API with Sentiment Analysis and Summary'''
    init_db()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()