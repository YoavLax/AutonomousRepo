import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

def analyze_sentiment():
    """
    Flask API endpoint for batch sentiment analysis.
    Accepts a JSON array of texts and returns their sentiment polarity and subjectivity.
    """
    app = Flask(__name__)
    LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "batch_sentiment.log"
    logger = setup_logger("batch_sentiment", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

    @app.route("/api/batch-sentiment", methods=["POST"])
    def batch_sentiment():
        try:
            data = request.get_json()
            texts = data.get("texts", [])
            if not isinstance(texts, list) or not texts:
                logger.error("Invalid input: 'texts' must be a non-empty list.")
                return jsonify({"error": "'texts' must be a non-empty list."}), 400

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
            logger.exception("Error in batch sentiment analysis.")
            return jsonify({"error": str(e)}), 500

    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    analyze_sentiment()