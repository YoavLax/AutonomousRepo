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
        results.append({
            "text": text,
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity
        })
    return results

def register_batch_sentiment_api(app: Flask, logger):
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
        results = analyze_sentiment_batch(data["texts"])
        logger.info(f"Batch sentiment analysis performed on {len(data['texts'])} texts")
        return jsonify({"results": results})

def new_feature():
    '''Adds a batch sentiment analysis API endpoint to the Flask app'''
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "batch_sentiment.log"
    logger = setup_logger("batch_sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))
    register_batch_sentiment_api(app, logger)
    print("Starting Flask app with /api/batch-sentiment endpoint...")
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()