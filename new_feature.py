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
    sentiment = "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"
    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": subjectivity
    }

def create_app():
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_feature.log"
    logger = setup_logger("sentiment_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment", methods=["POST"])
    def sentiment_api():
        data = request.get_json()
        if not data or "text" not in data:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "Missing 'text' in request body"}), 400
        text = data["text"]
        result = analyze_sentiment(text)
        logger.info(f"Sentiment analysis performed: {result}")
        return jsonify(result)

    return app

def new_feature():
    '''Run a Flask server exposing a /api/sentiment endpoint for sentiment analysis'''
    app = create_app()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()