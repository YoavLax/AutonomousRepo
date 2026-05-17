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
    Adds a Flask API endpoint for sentiment analysis.
    POST /api/sentiment
    Body: { "text": "some text" }
    Response: { "polarity": float, "subjectivity": float }
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_api.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment", methods=["POST"])
    def sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "Missing 'text' in request body"}), 400
        text = data["text"]
        result = analyze_sentiment(text)
        logger.info(f"Sentiment analysis for text: {text} | Result: {result}")
        return jsonify(result)

    app.run(host="0.0.0.0", port=5002)

if __name__ == "__main__":
    new_feature()