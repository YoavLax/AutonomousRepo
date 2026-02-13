import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_sentiment_analysis(text: str, polarity: float, subjectivity: float, db_path: str = "sentiment_log.db"):
    """Log sentiment analysis results to a SQLite database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            polarity REAL,
            subjectivity REAL,
            timestamp TEXT
        )
    """)
    c.execute("""
        INSERT INTO sentiment_log (text, polarity, subjectivity, timestamp)
        VALUES (?, ?, ?, ?)
    """, (text, polarity, subjectivity, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def new_feature():
    '''Adds a Flask API endpoint to analyze sentiment and log results'''
    try:
        from textblob import TextBlob
    except ImportError:
        raise ImportError("textblob is required. Install with 'pip install textblob'.")

    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/analyze-sentiment", methods=["POST"])
    def analyze_sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "Missing 'text' in request body"}), 400
        text = data["text"]
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        log_sentiment_analysis(text, polarity, subjectivity)
        logger.info(f"Sentiment analyzed for text: {text[:30]}... Polarity: {polarity}, Subjectivity: {subjectivity}")
        return jsonify({
            "text": text,
            "polarity": polarity,
            "subjectivity": subjectivity
        })

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()