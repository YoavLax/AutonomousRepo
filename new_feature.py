import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment using TextBlob and return polarity and subjectivity."""
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity
    }

def create_sentiment_api():
    """Create a Flask app with a /api/sentiment endpoint for sentiment analysis."""
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
        logger.info(f"Analyzing sentiment for text: {text[:100]}...")
        result = analyze_sentiment(text)
        logger.info(f"Sentiment result: {result}")
        return jsonify(result)

    return app

def new_feature():
    """Run the sentiment analysis API server."""
    app = create_sentiment_api()
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()