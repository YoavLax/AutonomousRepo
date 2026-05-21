import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/sentiment", methods=["POST"])
def analyze_sentiment():
    """
    Analyze the sentiment of the provided text.
    Expects JSON: { "text": "your text here" }
    Returns: { "polarity": float, "subjectivity": float, "sentiment": "positive|neutral|negative" }
    """
    data = request.get_json()
    if not data or "text" not in data:
        logger.warning("No text provided for sentiment analysis.")
        return jsonify({"error": "Missing 'text' in request body."}), 400

    text = data["text"]
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        logger.info(f"Sentiment analyzed: {sentiment} (polarity={polarity}, subjectivity={subjectivity})")
        return jsonify({
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment": sentiment
        })
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {e}")
        return jsonify({"error": "Failed to analyze sentiment."}), 500

def new_feature():
    '''Starts the Flask app to provide sentiment analysis API'''
    app.run(host="0.0.0.0", port=5002, debug=False)

if __name__ == "__main__":
    new_feature()