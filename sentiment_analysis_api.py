import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_analysis_api.log"
logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/sentiment-analysis", methods=["POST"])
def sentiment_analysis():
    """
    Analyze the sentiment of the provided text.
    Expects JSON: { "text": "some text" }
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
        logger.info(f"Sentiment analysis performed. Polarity: {polarity}, Subjectivity: {subjectivity}, Sentiment: {sentiment}")
        return jsonify({
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment": sentiment
        })
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {e}")
        return jsonify({"error": "Failed to analyze sentiment."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)