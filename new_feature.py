import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
logger = setup_logger("sentiment_api", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/batch-sentiment", methods=["POST"])
def batch_sentiment():
    """
    Analyze sentiment for a batch of texts.
    Expects JSON: { "texts": ["text1", "text2", ...] }
    Returns: { "results": [ { "text": ..., "polarity": ..., "subjectivity": ... }, ... ] }
    """
    data = request.get_json()
    if not data or "texts" not in data or not isinstance(data["texts"], list):
        logger.error("Invalid input for batch sentiment analysis")
        return jsonify({"error": "Invalid input. Provide a JSON with a 'texts' list."}), 400

    results = []
    for text in data["texts"]:
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            results.append({
                "text": text,
                "polarity": polarity,
                "subjectivity": subjectivity
            })
        except Exception as e:
            logger.error(f"Error analyzing text: {text} | {e}")
            results.append({
                "text": text,
                "error": str(e)
            })

    logger.info(f"Batch sentiment analysis completed for {len(data['texts'])} texts")
    return jsonify({"results": results})

def new_feature():
    '''Starts a Flask server with a batch sentiment analysis endpoint'''
    app.run(host="0.0.0.0", port=5002, debug=False)

if __name__ == "__main__":
    new_feature()