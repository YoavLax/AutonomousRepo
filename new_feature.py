import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment_batch(texts):
    """
    Analyze sentiment for a batch of texts.
    Returns a list of dicts with polarity and subjectivity for each text.
    """
    results = []
    for text in texts:
        blob = TextBlob(text)
        sentiment = blob.sentiment
        results.append({
            "text": text,
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity
        })
    return results

def create_app():
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature_batch_sentiment.log"
    logger = setup_logger("batch_sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/batch-sentiment", methods=["POST"])
    def batch_sentiment():
        """
        Accepts a JSON payload with a list of texts and returns their sentiment analysis.
        Example input: { "texts": ["I love this!", "This is bad."] }
        """
        data = request.get_json()
        if not data or "texts" not in data or not isinstance(data["texts"], list):
            logger.warning("Invalid input for batch sentiment analysis")
            return jsonify({"error": "Invalid input. Provide a JSON with a 'texts' list."}), 400
        try:
            results = analyze_sentiment_batch(data["texts"])
            logger.info(f"Processed batch sentiment for {len(data['texts'])} texts")
            return jsonify({"results": results}), 200
        except Exception as e:
            logger.error(f"Error in batch sentiment analysis: {e}")
            return jsonify({"error": "Internal server error"}), 500

    return app

def new_feature():
    '''Run a Flask server providing a batch sentiment analysis API endpoint'''
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("BATCH_SENTIMENT_PORT", 5050)))

if __name__ == "__main__":
    new_feature()