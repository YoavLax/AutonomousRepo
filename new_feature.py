import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of the provided text using TextBlob.
    Returns polarity and subjectivity.
    """
    blob = TextBlob(text)
    return {
        "polarity": blob.sentiment.polarity,
        "subjectivity": blob.sentiment.subjectivity
    }

def new_feature():
    """
    Flask API endpoint for batch sentiment analysis.
    Accepts a JSON payload with a list of texts and returns their sentiment analysis.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "batch_sentiment_analysis.log"
    logger = setup_logger("batch_sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/batch-sentiment", methods=["POST"])
    def batch_sentiment():
        try:
            data = request.get_json(force=True)
            texts = data.get("texts", [])
            if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
                logger.error("Invalid input: 'texts' must be a list of strings.")
                return jsonify({"error": "'texts' must be a list of strings."}), 400

            results = []
            for text in texts:
                sentiment = analyze_sentiment(text)
                results.append({
                    "text": text,
                    "polarity": sentiment["polarity"],
                    "subjectivity": sentiment["subjectivity"]
                })
            logger.info(f"Batch sentiment analysis completed for {len(texts)} texts.")
            return jsonify({"results": results}), 200
        except Exception as e:
            logger.exception("Error in batch sentiment analysis endpoint.")
            return jsonify({"error": str(e)}), 500

    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()