import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import sqlite3
import datetime

def analyze_and_log_sentiment():
    """
    Flask API endpoint to analyze sentiment of user-submitted text,
    log the result to a local SQLite database, and return the sentiment.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_analysis.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))
    DB_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_log.db"

    def init_db():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                polarity REAL,
                subjectivity REAL,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    @app.route("/api/analyze-sentiment", methods=["POST"])
    def analyze_sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "Missing 'text' in request."}), 400
        text = data["text"]
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            timestamp = datetime.datetime.utcnow().isoformat()
            # Log to DB
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO sentiment_logs (text, polarity, subjectivity, timestamp) VALUES (?, ?, ?, ?)",
                (text, polarity, subjectivity, timestamp)
            )
            conn.commit()
            conn.close()
            logger.info(f"Analyzed sentiment for text: {text[:30]}... Polarity: {polarity}, Subjectivity: {subjectivity}")
            return jsonify({
                "text": text,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "timestamp": timestamp
            })
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return jsonify({"error": "Failed to analyze sentiment."}), 500

    init_db()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    analyze_and_log_sentiment()