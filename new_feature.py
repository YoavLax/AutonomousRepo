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
    Accepts a list of texts and returns a sentiment summary (average polarity, subjectivity, and counts).
    Example input: {"texts": ["I love this!", "This is bad."]}
    """
    data = request.get_json()
    texts = data.get("texts", [])
    if not isinstance(texts, list) or not texts:
        logger.error("Invalid input: texts must be a non-empty list")
        return jsonify({"error": "Invalid input: texts must be a non-empty list"}), 400

    results = []
    for text in texts:
        blob = TextBlob(text)
        sentiment = blob.sentiment
        results.append({
            "text": text,
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity
        })

    avg_polarity = sum(r["polarity"] for r in results) / len(results)
    avg_subjectivity = sum(r["subjectivity"] for r in results) / len(results)
    positive = sum(1 for r in results if r["polarity"] > 0)
    negative = sum(1 for r in results if r["polarity"] < 0)
    neutral = sum(1 for r in results if r["polarity"] == 0)

    summary = {
        "average_polarity": avg_polarity,
        "average_subjectivity": avg_subjectivity,
        "count_positive": positive,
        "count_negative": negative,
        "count_neutral": neutral,
        "details": results
    }
    logger.info(f"Sentiment summary computed for {len(texts)} texts")
    return jsonify(summary), 200

def new_feature():
    '''Starts the Flask app for the sentiment summary API'''
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()