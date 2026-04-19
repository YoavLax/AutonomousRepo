import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of the given text using TextBlob."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    sentiment = (
        "positive" if polarity > 0.1 else
        "negative" if polarity < -0.1 else
        "neutral"
    )
    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": subjectivity
    }

def new_feature():
    """
    Run a Flask server that exposes a /api/sentiment endpoint.
    Accepts POST requests with JSON: { "text": "..." }
    Returns sentiment analysis.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_api.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment", methods=["POST"])
    def sentiment_api():
        data = request.get_json(force=True)
        text = data.get("text", "")
        if not text or not isinstance(text, str):
            logger.warning("No valid text provided for sentiment analysis.")
            return jsonify({"error": "Missing or invalid 'text' field"}), 400
        try:
            result = analyze_sentiment(text)
            logger.info(f"Sentiment analysis for text: {text[:50]}... Result: {result}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            return jsonify({"error": "Internal server error"}), 500

    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()