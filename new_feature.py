import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("NEW_FEATURE_LOG_LEVEL", "INFO"))

@app.route("/api/batch-sentiment", methods=["POST"])
def batch_sentiment():
    """
    Accepts a JSON array of texts and returns their sentiment analysis.
    Example input: {"texts": ["I love this!", "This is terrible."]}
    """
    try:
        data = request.get_json()
        texts = data.get("texts", [])
        if not isinstance(texts, list) or not texts:
            logger.warning("Invalid or empty texts array received.")
            return jsonify({"error": "Provide a non-empty 'texts' array."}), 400

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
        logger.error(f"Error in batch_sentiment: {str(e)}")
        return jsonify({"error": "Internal server error."}), 500

def new_feature():
    '''Starts a Flask server with a batch sentiment analysis endpoint'''
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()