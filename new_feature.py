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
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
    logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/batch-sentiment", methods=["POST"])
    def batch_sentiment():
        """
        Accepts a JSON payload with a list of texts and returns their sentiment analysis.
        Example input: { "texts": ["I love this!", "This is bad."] }
        """
        data = request.get_json(force=True)
        texts = data.get("texts")
        if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
            logger.warning("Invalid input for batch sentiment: %s", data)
            return jsonify({"error": "Invalid input. 'texts' must be a list of strings."}), 400
        logger.info("Processing batch sentiment for %d texts", len(texts))
        results = analyze_sentiment_batch(texts)
        return jsonify({"results": results})

    return app

def new_feature():
    '''Run a Flask server providing a batch sentiment analysis endpoint'''
    app = create_app()
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()