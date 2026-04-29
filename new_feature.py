import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import sqlite3
import datetime

def analyze_sentiment_and_log():
    """
    New Feature: Sentiment Analysis API Endpoint with Logging

    - Adds a Flask API endpoint `/api/analyze-sentiment` that accepts POST requests with a 'text' field.
    - Analyzes the sentiment of the provided text using TextBlob.
    - Logs each request and result to a SQLite database with timestamp, input, and sentiment.
    - Returns the sentiment polarity and subjectivity as JSON.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_analysis.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))
    DB_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_requests.db"

    def init_db():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                input_text TEXT NOT NULL,
                polarity REAL NOT NULL,
                subjectivity REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    @app.route("/api/analyze-sentiment", methods=["POST"])
    def analyze_sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided in request")
            return jsonify({"error": "Missing 'text' in request body"}), 400
        text = data["text"]
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Log to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO sentiment_logs (timestamp, input_text, polarity, subjectivity) VALUES (?, ?, ?, ?)",
            (datetime.datetime.utcnow().isoformat(), text, polarity, subjectivity)
        )
        conn.commit()
        conn.close()

        logger.info(f"Sentiment analyzed for text: {text[:50]}... Polarity: {polarity}, Subjectivity: {subjectivity}")
        return jsonify({
            "polarity": polarity,
            "subjectivity": subjectivity
        })

    init_db()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    analyze_sentiment_and_log()