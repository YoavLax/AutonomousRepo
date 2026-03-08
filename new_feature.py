import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/sentiment-summary", methods=["POST"])
def sentiment_summary():
    """
    Accepts a list of texts and returns a sentiment summary (average polarity, subjectivity, and distribution).
    Example input: {"texts": ["I love this!", "This is bad.", "Neutral."]}
    """
    data = request.get_json()
    texts = data.get("texts", [])
    if not isinstance(texts, list) or not texts:
        logger.error("Invalid or empty 'texts' provided.")
        return jsonify({"error": "Provide a non-empty list of texts."}), 400

    sentiments = []
    for text in texts:
        blob = TextBlob(text)
        sentiments.append({
            "text": text,
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity
        })

    avg_polarity = sum(s["polarity"] for s in sentiments) / len(sentiments)
    avg_subjectivity = sum(s["subjectivity"] for s in sentiments) / len(sentiments)
    distribution = {
        "positive": sum(1 for s in sentiments if s["polarity"] > 0),
        "negative": sum(1 for s in sentiments if s["polarity"] < 0),
        "neutral": sum(1 for s in sentiments if s["polarity"] == 0)
    }

    logger.info(f"Sentiment summary calculated for {len(texts)} texts.")
    return jsonify({
        "average_polarity": avg_polarity,
        "average_subjectivity": avg_subjectivity,
        "distribution": distribution,
        "details": sentiments
    })

def new_feature():
    '''Starts the Flask app for the sentiment summary API'''
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()