import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_sentiment_analysis(text: str, sentiment: str, polarity: float, db_path: str = "sentiment_log.db"):
    """Log sentiment analysis results to a SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            sentiment TEXT,
            polarity REAL,
            timestamp TEXT
        )
    """)
    timestamp = datetime.datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO sentiment_logs (text, sentiment, polarity, timestamp) VALUES (?, ?, ?, ?)",
        (text, sentiment, polarity, timestamp)
    )
    conn.commit()
    conn.close()

def new_feature():
    '''Adds a Flask API endpoint to log sentiment analysis results'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/log-sentiment", methods=["POST"])
    def log_sentiment():
        data = request.get_json()
        text = data.get("text")
        sentiment = data.get("sentiment")
        polarity = data.get("polarity")
        if not text or sentiment is None or polarity is None:
            logger.error("Missing required fields in request")
            return jsonify({"error": "Missing required fields"}), 400
        try:
            log_sentiment_analysis(text, sentiment, float(polarity))
            logger.info(f"Logged sentiment for text: {text[:30]}...")
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logger.error(f"Failed to log sentiment: {e}")
            return jsonify({"error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()