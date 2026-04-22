import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "sentiment_feedback.log"
logger = setup_logger("sentiment_feedback", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

FEEDBACK_FILE = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "user_sentiment_feedback.csv"

def analyze_sentiment(text: str) -> dict:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    sentiment = (
        "positive" if polarity > 0.1 else
        "negative" if polarity < -0.1 else
        "neutral"
    )
    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": subjectivity
    }

def save_feedback(text: str, user_sentiment: str, auto_sentiment: str):
    header = "text,user_sentiment,auto_sentiment\n"
    line = f'"{text.replace("\"", "\"\"")}",{user_sentiment},{auto_sentiment}\n'
    write_header = not FEEDBACK_FILE.exists()
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        if write_header:
            f.write(header)
        f.write(line)

@app.route("/api/sentiment-feedback", methods=["POST"])
def sentiment_feedback():
    """
    Accepts user text and their sentiment feedback, compares with automatic sentiment analysis,
    and logs the result for future model improvement.
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    user_sentiment = data.get("user_sentiment", "").lower()
    if not text or user_sentiment not in {"positive", "neutral", "negative"}:
        logger.warning("Invalid input for sentiment feedback")
        return jsonify({"error": "Invalid input"}), 400

    auto_result = analyze_sentiment(text)
    auto_sentiment = auto_result["sentiment"]

    save_feedback(text, user_sentiment, auto_sentiment)
    logger.info(f"Feedback saved: user={user_sentiment}, auto={auto_sentiment}")

    return jsonify({
        "user_sentiment": user_sentiment,
        "auto_sentiment": auto_sentiment,
        "match": user_sentiment == auto_sentiment
    })

def new_feature():
    """
    Starts a Flask server with a /api/sentiment-feedback endpoint for collecting user sentiment feedback.
    """
    logger.info("Starting Sentiment Feedback API server on http://127.0.0.1:5001")
    app.run(port=5001)

if __name__ == "__main__":
    new_feature()