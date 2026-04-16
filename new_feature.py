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
    sentiment = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"
    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": subjectivity
    }

def new_feature():
    """
    Flask API endpoint for sentiment analysis.
    POST /api/sentiment-analysis
    JSON body: { "text": "some text" }
    Response: { "sentiment": "...", "polarity": ..., "subjectivity": ... }
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_analysis.log"
    logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment-analysis", methods=["POST"])
    def sentiment_analysis():
        data = request.get_json(force=True)
        text = data.get("text", "")
        if not text or not isinstance(text, str):
            logger.warning("Invalid or missing 'text' in request")
            return jsonify({"error": "Missing or invalid 'text' field"}), 400
        try:
            result = analyze_sentiment(text)
            logger.info(f"Sentiment analysis performed: {result}")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            return jsonify({"error": "Internal server error"}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()