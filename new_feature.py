import os
from flask import Flask, request, jsonify
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = os.path.join(os.getcwd(), "new_feature.log")
logger = setup_logger("new_feature", LOG_PATH, level="INFO")

@app.route("/api/batch-sentiment", methods=["POST"])
def batch_sentiment():
    """
    Accepts a JSON array of texts and returns their sentiment analysis.
    Example input: {"texts": ["I love this!", "This is bad."]}
    Example output: {"results": [{"text": "...", "polarity": 0.5, "subjectivity": 0.6}, ...]}
    """
    data = request.get_json(force=True)
    texts = data.get("texts", [])
    if not isinstance(texts, list) or not texts:
        logger.error("Invalid input for batch sentiment analysis.")
        return jsonify({"error": "Input must be a non-empty list of texts."}), 400

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
    '''Runs the Flask app for batch sentiment analysis'''
    app.run(host="0.0.0.0", port=5050, debug=False)

if __name__ == "__main__":
    new_feature()