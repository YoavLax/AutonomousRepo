import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "new_feature.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("NEW_FEATURE_LOG_LEVEL", "INFO"))

@app.route("/api/batch-sentiment", methods=["POST"])
def batch_sentiment():
    """
    Accepts a JSON array of texts and returns their sentiment polarity and subjectivity.
    Example input: {"texts": ["I love this!", "This is terrible."]}
    """
    data = request.get_json()
    texts = data.get("texts", [])
    results = []
    for text in texts:
        blob = TextBlob(text)
        sentiment = blob.sentiment
        results.append({
            "text": text,
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity
        })
        logger.info(f"Processed sentiment for text: {text}")
    return jsonify({"results": results})

def new_feature():
    '''Starts a Flask server with a batch sentiment analysis endpoint'''
    logger.info("Starting new_feature Flask server for batch sentiment analysis")
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    new_feature()