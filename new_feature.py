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
    Flask API endpoint for batch sentiment analysis.
    POST /api/batch-sentiment
    Body: { "texts": [ "text1", "text2", ... ] }
    Response: [{ "sentiment": ..., "polarity": ..., "subjectivity": ... }, ...]
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "batch_sentiment.log"
    logger = setup_logger("batch_sentiment", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/batch-sentiment", methods=["POST"])
    def batch_sentiment():
        data = request.get_json(force=True)
        texts = data.get("texts")
        if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
            logger.error("Invalid input for batch sentiment analysis")
            return jsonify({"error": "Input must be a JSON object with a 'texts' list of strings."}), 400
        logger.info(f"Analyzing sentiment for {len(texts)} texts")
        results = [analyze_sentiment(text) for text in texts]
        return jsonify(results), 200

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()