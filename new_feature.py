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
    Accepts a JSON array of texts and returns their sentiment analysis.
    Example input: {"texts": ["I love this!", "This is bad."]}
    Example output: {"results": [{"text": "...", "polarity": 0.5, "subjectivity": 0.6}, ...]}
    """
    data = request.get_json(force=True)
    texts = data.get("texts", [])
    if not isinstance(texts, list):
        logger.error("Invalid input: texts must be a list.")
        return jsonify({"error": "Invalid input: texts must be a list."}), 400

    results = []
    for text in texts:
        try:
            blob = TextBlob(text)
            result = {
                "text": text,
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity
            }
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing text '{text}': {e}")
            results.append({
                "text": text,
                "error": str(e)
            })
    logger.info(f"Processed batch sentiment for {len(texts)} texts.")
    return jsonify({"results": results})

def new_feature():
    '''Starts the Flask app for batch sentiment analysis'''
    app.run(host="0.0.0.0", port=5050)

if __name__ == "__main__":
    new_feature()