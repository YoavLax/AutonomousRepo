import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("NEW_FEATURE_LOG_LEVEL", "INFO"))

@app.route("/api/sentiment-summary", methods=["POST"])
def sentiment_summary():
    """
    Analyze sentiment of a list of texts and return summary statistics.
    Expects JSON: { "texts": [ ... ] }
    Returns: { "average_polarity": float, "average_subjectivity": float, "details": [ ... ] }
    """
    data = request.get_json()
    texts = data.get("texts", [])
    if not isinstance(texts, list) or not texts:
        logger.error("Invalid or empty 'texts' payload")
        return jsonify({"error": "Provide a non-empty list of texts"}), 400

    details = []
    total_polarity = 0.0
    total_subjectivity = 0.0

    for text in texts:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        details.append({
            "text": text,
            "polarity": polarity,
            "subjectivity": subjectivity
        })
        total_polarity += polarity
        total_subjectivity += subjectivity

    avg_polarity = total_polarity / len(texts)
    avg_subjectivity = total_subjectivity / len(texts)

    logger.info(f"Sentiment summary computed for {len(texts)} texts")
    return jsonify({
        "average_polarity": avg_polarity,
        "average_subjectivity": avg_subjectivity,
        "details": details
    })

def new_feature():
    '''Starts a Flask server with a sentiment summary API endpoint'''
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()