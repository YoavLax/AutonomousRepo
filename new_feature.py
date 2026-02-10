import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import sqlite3
import datetime

def log_sentiment_analysis(user_input: str, sentiment: str, polarity: float, db_path: str = "execution_log.db"):
    """Log sentiment analysis results to the execution log database."""
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                sentiment TEXT,
                polarity REAL
            )
        """)
        c.execute("""
            INSERT INTO sentiment_log (timestamp, user_input, sentiment, polarity)
            VALUES (?, ?, ?, ?)
        """, (datetime.datetime.utcnow().isoformat(), user_input, sentiment, polarity))
        conn.commit()
    finally:
        conn.close()

def new_feature():
    '''Adds a Flask API endpoint to log sentiment analysis results'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/log-sentiment", methods=["POST"])
    def log_sentiment():
        data = request.get_json()
        user_input = data.get("user_input")
        sentiment = data.get("sentiment")
        polarity = data.get("polarity")
        if not all([user_input, sentiment, polarity is not None]):
            logger.warning("Missing required fields in request")
            return jsonify({"error": "Missing required fields"}), 400
        try:
            log_sentiment_analysis(user_input, sentiment, float(polarity))
            logger.info(f"Logged sentiment: {sentiment} (polarity: {polarity}) for input: {user_input}")
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logger.error(f"Failed to log sentiment: {e}")
            return jsonify({"error": "Failed to log sentiment"}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()