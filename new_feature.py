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
    Accepts a list of texts and returns a summary of their sentiment analysis.
    Example input: { "texts": ["I love this!", "This is terrible."] }
    """
    data = request.get_json(force=True)
    texts = data.get("texts", [])
    if not isinstance(texts, list) or not texts:
        logger.error("Invalid or empty 'texts' provided.")
        return jsonify({"error": "Please provide a non-empty list of texts."}), 400

    results = []
    for text in texts:
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            sentiment = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"
            results.append({
                "text": text,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "sentiment": sentiment
            })
        except Exception as e:
            logger.error(f"Error analyzing text: {text} | {e}")
            results.append({
                "text": text,
                "error": str(e)
            })

    summary = {
        "total": len(results),
        "positive": sum(1 for r in results if r.get("sentiment") == "positive"),
        "negative": sum(1 for r in results if r.get("sentiment") == "negative"),
        "neutral": sum(1 for r in results if r.get("sentiment") == "neutral"),
        "details": results
    }
    logger.info(f"Sentiment summary computed for {len(texts)} texts.")
    return jsonify(summary), 200

def new_feature():
    '''Starts the Flask app for sentiment summary API'''
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()