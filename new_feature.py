import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/batch-sentiment", methods=["POST"])
def batch_sentiment():
    """
    Analyze sentiment for a batch of texts.
    Expects JSON: { "texts": [ "text1", "text2", ... ] }
    Returns: { "results": [ { "text": ..., "polarity": ..., "subjectivity": ... }, ... ] }
    """
    data = request.get_json(force=True)
    texts = data.get("texts", [])
    if not isinstance(texts, list) or not texts:
        logger.warning("Invalid or empty 'texts' payload received.")
        return jsonify({"error": "Payload must include a non-empty 'texts' list."}), 400

    results = []
    for text in texts:
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            results.append({
                "text": text,
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity
            })
        except Exception as e:
            logger.error(f"Error analyzing text: {text} | {e}")
            results.append({
                "text": text,
                "error": str(e)
            })

    logger.info(f"Batch sentiment analysis completed for {len(texts)} texts.")
    return jsonify({"results": results})

def new_feature():
    '''Starts the Flask app for batch sentiment analysis'''
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()