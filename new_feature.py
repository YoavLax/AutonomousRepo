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
    Adds a new Flask endpoint /api/batch-sentiment that accepts a list of texts and returns their sentiment analysis.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "batch_sentiment.log"
    logger = setup_logger("batch_sentiment", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/batch-sentiment", methods=["POST"])
    def batch_sentiment():
        try:
            data = request.get_json(force=True)
            texts = data.get("texts", [])
            if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
                logger.warning("Invalid input for batch sentiment analysis")
                return jsonify({"error": "Input must be a JSON object with a 'texts' list of strings."}), 400
            results = [analyze_sentiment(text) for text in texts]
            logger.info(f"Batch sentiment analysis completed for {len(texts)} texts.")
            return jsonify({"results": results}), 200
        except Exception as e:
            logger.error(f"Error in batch_sentiment: {e}")
            return jsonify({"error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()