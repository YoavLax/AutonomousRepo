import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment():
    """
    New feature: Sentiment analysis endpoint for submitted text.
    Extends the Flask API with /api/sentiment-analysis.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_analysis.log"
    logger = setup_logger("sentiment_analysis", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment-analysis", methods=["POST"])
    def sentiment_analysis():
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            logger.warning("No text provided for sentiment analysis.")
            return jsonify({"error": "No text provided"}), 400
        analysis = TextBlob(text)
        sentiment = {
            "polarity": analysis.polarity,
            "subjectivity": analysis.subjectivity,
            "label": "positive" if analysis.polarity > 0 else "negative" if analysis.polarity < 0 else "neutral"
        }
        logger.info(f"Sentiment analysis for text: {text} | Result: {sentiment}")
        return jsonify(sentiment), 200

    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    analyze_sentiment()