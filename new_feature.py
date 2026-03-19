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
    Adds a minimal Flask API endpoint for sentiment analysis.
    POST /api/sentiment
    Body: { "text": "..." }
    Response: { "polarity": float, "subjectivity": float, "label": str }
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment", methods=["POST"])
    def sentiment_api():
        data = request.get_json(force=True)
        text = data.get("text", "")
        if not text:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "No text provided"}), 400
        result = analyze_sentiment(text)
        logger.info(f"Sentiment analysis for text: {text[:50]}... Result: {result}")
        return jsonify(result)

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()