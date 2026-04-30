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

def new_feature():
    """
    Launch a minimal Flask API for sentiment analysis.
    POST /api/sentiment
    Body: { "text": "..." }
    Response: { "polarity": float, "subjectivity": float, "label": str }
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_api.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment", methods=["POST"])
    def sentiment_endpoint():
        data = request.get_json(force=True)
        text = data.get("text", "")
        if not text or not isinstance(text, str):
            logger.warning("No valid text provided for sentiment analysis.")
            return jsonify({"error": "Missing or invalid 'text' field."}), 400
        result = analyze_sentiment(text)
        logger.info(f"Sentiment analyzed: {result}")
        return jsonify(result)

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()