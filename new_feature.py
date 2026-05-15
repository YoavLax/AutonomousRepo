import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of the given text using TextBlob."""
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity,
        "label": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
    }

def new_feature():
    """
    Flask API endpoint for advanced sentiment analysis.
    Extends the project by providing a /api/advanced-sentiment endpoint.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "advanced_sentiment.log"
    logger = setup_logger("advanced_sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/advanced-sentiment", methods=["POST"])
    def advanced_sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "Missing 'text' in request body"}), 400
        text = data["text"]
        logger.info(f"Analyzing sentiment for text: {text[:100]}")
        result = analyze_sentiment(text)
        logger.info(f"Sentiment result: {result}")
        return jsonify(result)

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()