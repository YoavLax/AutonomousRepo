import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import sqlite3
import datetime

def analyze_sentiment_and_log():
    """
    Flask API endpoint to analyze sentiment of user-submitted text,
    log the request and result to the autonomous agent's execution log,
    and return the sentiment analysis.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))
    DB_PATH = os.getenv("EXEC_LOG_DB_PATH", "execution_log.db")

    def log_to_db(input_text: str, polarity: float, subjectivity: float, timestamp: str):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS sentiment_log
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          input_text TEXT,
                          polarity REAL,
                          subjectivity REAL,
                          timestamp TEXT)''')
            c.execute('''INSERT INTO sentiment_log (input_text, polarity, subjectivity, timestamp)
                         VALUES (?, ?, ?, ?)''', (input_text, polarity, subjectivity, timestamp))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log to DB: {e}")

    @app.route("/api/analyze-sentiment", methods=["POST"])
    def analyze_sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "No text provided"}), 400
        text = data["text"]
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        timestamp = datetime.datetime.utcnow().isoformat()
        log_to_db(text, polarity, subjectivity, timestamp)
        logger.info(f"Sentiment analyzed for text: {text[:30]}... Polarity: {polarity}, Subjectivity: {subjectivity}")
        return jsonify({
            "text": text,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "timestamp": timestamp
        })

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    analyze_sentiment_and_log()