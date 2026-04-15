import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_feedback.log"
logger = setup_logger("sentiment_feedback", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

FEEDBACK_FILE = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_feedback.csv"

def analyze_sentiment(text: str) -> str:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def save_feedback(text: str, sentiment: str, user_sentiment: str):
    header_needed = not FEEDBACK_FILE.exists()
    with FEEDBACK_FILE.open("a", encoding="utf-8") as f:
        if header_needed:
            f.write("text,detected_sentiment,user_sentiment\n")
        # Escape quotes and commas for CSV
        safe_text = '"' + text.replace('"', '""') + '"'
        safe_detected = '"' + sentiment.replace('"', '""') + '"'
        safe_user = '"' + user_sentiment.replace('"', '""') + '"'
        f.write(f"{safe_text},{safe_detected},{safe_user}\n")

@app.route("/api/sentiment-feedback", methods=["POST"])
def sentiment_feedback():
    """
    Accepts user text, returns detected sentiment, and allows user to provide feedback on accuracy.
    JSON body: { "text": "...", "user_sentiment": "positive|neutral|negative" }
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    user_sentiment = data.get("user_sentiment", "").lower()
    if not text or user_sentiment not in {"positive", "neutral", "negative"}:
        logger.warning("Invalid input to /api/sentiment-feedback: %s", data)
        return jsonify({"error": "Invalid input"}), 400

    detected_sentiment = analyze_sentiment(text)
    save_feedback(text, detected_sentiment, user_sentiment)
    logger.info("Feedback saved: detected=%s, user=%s", detected_sentiment, user_sentiment)
    return jsonify({
        "detected_sentiment": detected_sentiment,
        "user_sentiment": user_sentiment,
        "match": detected_sentiment == user_sentiment
    })

def new_feature():
    '''Run the Flask app for sentiment feedback collection'''
    app.run(host="0.0.0.0", port=5050, debug=True)

if __name__ == "__main__":
    new_feature()