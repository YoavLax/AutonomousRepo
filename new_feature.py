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

def create_sentiment_batch_api():
    """
    Create a Flask app with a /api/sentiment-batch endpoint for batch sentiment analysis.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_batch_api.log"
    logger = setup_logger("sentiment_batch_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/sentiment-batch", methods=["POST"])
    def sentiment_batch():
        try:
            data = request.get_json(force=True)
            texts = data.get("texts")
            if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
                logger.warning("Invalid input for batch sentiment analysis")
                return jsonify({"error": "Invalid input. 'texts' must be a list of strings."}), 400
            logger.info(f"Received batch of {len(texts)} texts for sentiment analysis")
            results = analyze_sentiment_batch(texts)
            return jsonify({"results": results}), 200
        except Exception as e:
            logger.error(f"Error in sentiment_batch: {e}")
            return jsonify({"error": "Internal server error"}), 500

    return app

def new_feature():
    '''Run the batch sentiment analysis API server'''
    app = create_sentiment_batch_api()
    app.run(host="0.0.0.0", port=int(os.getenv("SENTIMENT_BATCH_PORT", 5050)))

if __name__ == "__main__":
    new_feature()