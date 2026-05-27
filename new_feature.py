import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "feature_sentiment.log"
logger = setup_logger("feature_sentiment", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/batch-sentiment", methods=["POST"])
def batch_sentiment():
    """
    Analyze sentiment for a batch of texts.
    Expects JSON: { "texts": [ ... ] }
    Returns: { "results": [ { "text": ..., "polarity": ..., "subjectivity": ... }, ... ] }
    """
    try:
        data = request.get_json(force=True)
        texts = data.get("texts", [])
        if not isinstance(texts, list) or not texts:
            logger.warning("No texts provided or invalid format.")
            return jsonify({"error": "Please provide a non-empty list of texts."}), 400

        results = []
        for text in texts:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            results.append({
                "text": text,
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity
            })
        logger.info(f"Batch sentiment analysis completed for {len(texts)} texts.")
        return jsonify({"results": results}), 200
    except Exception as e:
        logger.error(f"Error in batch_sentiment: {e}")
        return jsonify({"error": str(e)}), 500

def new_feature():
    '''Run the Flask app for batch sentiment analysis'''
    app.run(host="0.0.0.0", port=5050, debug=True)

if __name__ == "__main__":
    new_feature()