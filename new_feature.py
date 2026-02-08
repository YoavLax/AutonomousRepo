import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import sqlite3
import datetime

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

DB_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_log.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            polarity REAL,
            subjectivity REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/api/analyze-and-log-sentiment", methods=["POST"])
def analyze_and_log_sentiment():
    """
    Analyze sentiment of provided text and log the result to a database.
    """
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        logger.error("No text provided for sentiment analysis.")
        return jsonify({"error": "No text provided"}), 400

    analysis = TextBlob(text)
    polarity = analysis.polarity
    subjectivity = analysis.subjectivity
    timestamp = datetime.datetime.utcnow().isoformat()

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO sentiment_analysis (text, polarity, subjectivity, timestamp) VALUES (?, ?, ?, ?)",
            (text, polarity, subjectivity, timestamp)
        )
        conn.commit()
        conn.close()
        logger.info(f"Logged sentiment for text: {text[:30]}... Polarity: {polarity}, Subjectivity: {subjectivity}")
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

    return jsonify({
        "text": text,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "timestamp": timestamp,
        "status": "logged"
    })

def new_feature():
    '''Adds a sentiment analysis API endpoint that logs results to a database'''
    init_db()
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()