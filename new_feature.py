import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_sentiment_analysis(text: str, polarity: float, subjectivity: float, db_path: str = "execution_log.db"):
    """Log sentiment analysis results to the execution log database."""
    conn = sqlite3.connect(db_path)
    try:
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
    finally:
        conn.close()

def new_feature():
    '''Adds a Flask API endpoint for logging sentiment analysis results'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/log-sentiment", methods=["POST"])
    def log_sentiment():
        data = request.get_json()
        if not data or "text" not in data or "polarity" not in data or "subjectivity" not in data:
            logger.warning("Invalid request data: %s", data)
            return jsonify({"error": "Missing required fields: text, polarity, subjectivity"}), 400
        text = data["text"]
        try:
            polarity = float(data["polarity"])
            subjectivity = float(data["subjectivity"])
        except (ValueError, TypeError):
            logger.warning("Invalid polarity/subjectivity values: %s", data)
            return jsonify({"error": "Polarity and subjectivity must be numbers"}), 400
        try:
            log_sentiment_analysis(text, polarity, subjectivity)
            logger.info("Logged sentiment for text: %s", text)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logger.error("Failed to log sentiment: %s", str(e))
            return jsonify({"error": "Failed to log sentiment"}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()