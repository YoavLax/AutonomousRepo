import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment():
    """
    Flask API endpoint for sentiment analysis of user-submitted text.
    Extends the project by providing a new /api/sentiment endpoint.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_analysis.log"
    logger = setup_logger("sentiment_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment", methods=["POST"])
    def sentiment():
        data = request.get_json()
        if not data or "text" not in data:
            logger.error("No text provided for sentiment analysis.")
            return jsonify({"error": "No text provided"}), 400
        text = data["text"]
        try:
            blob = TextBlob(text)
            sentiment_result = {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
                "label": "positive" if blob.sentiment.polarity > 0 else "negative" if blob.sentiment.polarity < 0 else "neutral"
            }
            logger.info(f"Sentiment analysis for text: {text} | Result: {sentiment_result}")
            return jsonify(sentiment_result), 200
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return jsonify({"error": "Sentiment analysis failed"}), 500

    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    analyze_sentiment()