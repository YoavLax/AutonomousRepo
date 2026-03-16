import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("NEW_FEATURE_LOG_LEVEL", "INFO"))

@app.route("/api/sentiment-summary", methods=["POST"])
def sentiment_summary():
    """
    Analyze sentiment of provided text and return a summary.
    Expects JSON: { "text": "..." }
    """
    data = request.get_json()
    if not data or "text" not in data:
        logger.error("Missing 'text' in request")
        return jsonify({"error": "Missing 'text' in request"}), 400

    text = data["text"]
    blob = TextBlob(text)
    sentiment = blob.sentiment
    summary = {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity,
        "sentiment": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
    }
    logger.info(f"Sentiment summary: {summary}")
    return jsonify(summary), 200

def new_feature():
    '''Starts a Flask server with a sentiment summary endpoint'''
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()