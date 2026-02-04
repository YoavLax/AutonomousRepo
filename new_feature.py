import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
logger = setup_logger("new_feature", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/batch-sentiment", methods=["POST"])
def batch_sentiment():
    """
    Accepts a JSON array of texts and returns their sentiment polarity and subjectivity.
    Example input: {"texts": ["I love this!", "This is bad."]}
    """
    data = request.get_json()
    if not data or "texts" not in data or not isinstance(data["texts"], list):
        logger.error("Invalid input for batch sentiment analysis")
        return jsonify({"error": "Invalid input. Provide a JSON object with a 'texts' list."}), 400

    results = []
    for text in data["texts"]:
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

    logger.info(f"Batch sentiment analysis completed for {len(data['texts'])} texts.")
    return jsonify({"results": results})

def new_feature():
    '''Starts the Flask app to provide batch sentiment analysis API'''
    app.run(host="0.0.0.0", port=5001, debug=False)

if __name__ == "__main__":
    new_feature()