import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
logger = setup_logger("api_server", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/text-analysis", methods=["POST"])
def text_analysis():
    """
    Analyze text for word count, character count, reading time, paragraph count, sentiment, and complexity.
    Expects JSON: { "text": "..." }
    """
    data = request.get_json()
    if not data or "text" not in data:
        logger.warning("No text provided for analysis.")
        return jsonify({"error": "No text provided."}), 400

    text = data["text"]
    words = [w for w in text.split() if w.strip()]
    word_count = len(words)
    char_count = len(text)
    read_time = max(1, round(word_count / 200))
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    para_count = len(paragraphs)

    # Simple sentiment analysis
    positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'happy', 'best', 'awesome', 'brilliant', 'perfect'}
    negative_words = {'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor', 'disappointing', 'sad', 'angry', 'difficult'}
    lower_text = text.lower()
    pos_count = sum(lower_text.count(w) for w in positive_words)
    neg_count = sum(lower_text.count(w) for w in negative_words)
    if pos_count > neg_count * 1.5:
        sentiment = "positive"
    elif neg_count > pos_count * 1.5:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    avg_word_length = sum(len(w) for w in words) / word_count if word_count else 0
    if avg_word_length < 4:
        complexity = "simple"
    elif avg_word_length < 6:
        complexity = "moderate"
    else:
        complexity = "complex"

    logger.info("Text analysis performed.")
    return jsonify({
        "word_count": word_count,
        "char_count": char_count,
        "read_time": read_time,
        "para_count": para_count,
        "sentiment": sentiment,
        "complexity": complexity
    })

if __name__ == "__main__":
    app.run(port=5051, debug=True)

This production-ready Flask API provides a `/api/text-analysis` endpoint for programmatic text analysis, enabling integration with the web UI or external tools.