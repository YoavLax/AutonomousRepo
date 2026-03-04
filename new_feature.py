import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob
import datetime

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
logger = setup_logger("feature_server", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/sentiment-summary", methods=["POST"])
def sentiment_summary():
    """
    Accepts a list of texts and returns a sentiment summary (average polarity, subjectivity, and counts).
    Expects JSON: { "texts": [ ... ] }
    """
    data = request.get_json()
    if not data or "texts" not in data or not isinstance(data["texts"], list):
        logger.error("Invalid input for sentiment-summary endpoint.")
        return jsonify({"error": "Invalid input. Provide a JSON object with a 'texts' list."}), 400

    texts = data["texts"]
    if not texts:
        logger.warning("Empty texts list received.")
        return jsonify({"error": "The 'texts' list is empty."}), 400

    total_polarity = 0.0
    total_subjectivity = 0.0
    positive, negative, neutral = 0, 0, 0

    for text in texts:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        total_polarity += polarity
        total_subjectivity += subjectivity
        if polarity > 0.1:
            positive += 1
        elif polarity < -0.1:
            negative += 1
        else:
            neutral += 1

    count = len(texts)
    avg_polarity = total_polarity / count
    avg_subjectivity = total_subjectivity / count

    summary = {
        "average_polarity": avg_polarity,
        "average_subjectivity": avg_subjectivity,
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "total_texts": count,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    logger.info(f"Sentiment summary computed: {summary}")
    return jsonify(summary), 200

def new_feature():
    '''Starts a Flask server with a sentiment summary API endpoint'''
    logger.info("Starting feature server for sentiment summary.")
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()