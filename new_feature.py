import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of the provided text using TextBlob."""
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity,
        "label": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
    }

def create_sentiment_api():
    """Create and run a Flask API for sentiment analysis."""
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_api.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment", methods=["POST"])
    def sentiment_endpoint():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "Missing 'text' in request body."}), 400
        text = data["text"]
        result = analyze_sentiment(text)
        logger.info(f"Sentiment analysis performed for text: {text[:50]}... Result: {result}")
        return jsonify(result)

    app.run(host="0.0.0.0", port=5050)

def new_feature():
    '''Launches a sentiment analysis API endpoint at /api/sentiment'''
    create_sentiment_api()

if __name__ == "__main__":
    new_feature()