import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_sentiment_to_db(text: str, sentiment: float, db_path: str = "sentiment_log.db") -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            text TEXT,
            sentiment REAL
        )
    """)
    c.execute(
        "INSERT INTO sentiment_logs (timestamp, text, sentiment) VALUES (?, ?, ?)",
        (datetime.datetime.utcnow().isoformat(), text, sentiment)
    )
    conn.commit()
    conn.close()

def analyze_sentiment(text: str) -> float:
    try:
        from textblob import TextBlob
    except ImportError:
        raise RuntimeError("textblob is required for sentiment analysis")
    blob = TextBlob(text)
    return blob.sentiment.polarity

def new_feature():
    '''Adds a Flask API endpoint to analyze sentiment and log results to a database'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/analyze-sentiment", methods=["POST"])
    def analyze_sentiment_endpoint():
        data = request.get_json()
        if not data or "text" not in data:
            logger.error("No text provided for sentiment analysis")
            return jsonify({"error": "No text provided"}), 400
        text = data["text"]
        try:
            sentiment = analyze_sentiment(text)
            log_sentiment_to_db(text, sentiment)
            logger.info(f"Sentiment analyzed: {sentiment} for text: {text}")
            return jsonify({"sentiment": sentiment})
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return jsonify({"error": str(e)}), 500

    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()