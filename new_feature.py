import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of the given text using TextBlob."""
    blob = TextBlob(text)
    return {
        "polarity": blob.sentiment.polarity,
        "subjectivity": blob.sentiment.subjectivity
    }

def new_feature():
    """
    Adds a standalone Flask API endpoint for advanced sentiment analysis.
    This endpoint accepts POST requests with a 'text' field and returns
    detailed sentiment analysis.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_analysis.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/advanced-sentiment", methods=["POST"])
    def advanced_sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "Missing 'text' field"}), 400
        text = data["text"]
        logger.info(f"Analyzing sentiment for text: {text[:100]}")
        sentiment = analyze_sentiment(text)
        logger.info(f"Sentiment result: {sentiment}")
        return jsonify({"sentiment": sentiment})

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()