import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import openai
import re
from textblob import TextBlob

app = Flask(__name__)
LOG_PATH = Path(os.getenv("TARGET_REPO_PATH", os.getcwd())) / "autonomous_agent.log"
logger = setup_logger("api_server", str(LOG_PATH), level=os.getenv("API_LOG_LEVEL", "INFO"))

@app.route("/api/generate-content", methods=["POST"])
def generate_content():
    """
    Generate creative content (headline, paragraph, ideas, summary) using OpenAI API.
    Expects JSON: { "type": "headline"|"paragraph"|"ideas"|"summary", "topic": "..." }
    """
    data = request.get_json()
    if not data or "type" not in data or "topic" not in data:
        logger.warning("Invalid request for content generation.")
        return jsonify({"error": "Missing type or topic."}), 400

    content_type = data["type"]
    topic = data["topic"]
    prompt_map = {
        "headline": f"Write a catchy headline about: {topic}",
        "paragraph": f"Write a detailed paragraph about: {topic}",
        "ideas": f"List 5 creative ideas related to: {topic}",
        "summary": f"Write a concise summary of: {topic}",
    }
    prompt = prompt_map.get(content_type)
    if not prompt:
        return jsonify({"error": "Invalid content type."}), 400

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not set.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.7,
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"Generated content for type={content_type}, topic={topic}")
        return jsonify({"result": result})
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    AI chat endpoint. Expects JSON: { "message": "..." }
    Returns: { "response": "..." }
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing message."}), 400
    user_message = data["message"]
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not set")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=256,
            temperature=0.7,
        )
        ai_response = response.choices[0].message.content.strip()
        return jsonify({"response": ai_response})
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze-text", methods=["POST"])
def analyze_text():
    """
    Analyze text for statistics and sentiment.
    Expects JSON: { "text": "..." }
    Returns: { ...stats... }
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing text."}), 400
    text = data["text"]
    try:
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        char_count = len(text)
        para_count = len([p for p in text.split('\n') if p.strip()])
        read_time = round(word_count / 200, 2)  # 200 wpm
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        if sentiment > 0.2:
            sentiment_label = "Positive"
        elif sentiment < -0.2:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
        # Flesch Reading Ease (simple version)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        syllable_count = sum(len(re.findall(r'[aeiouy]+', w, re.I)) for w in words)
        sentence_count = max(len(sentences), 1)
        flesch = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / max(word_count,1))
        if flesch >= 60:
            complexity = "Easy"
        elif flesch >= 30:
            complexity = "Medium"
        else:
            complexity = "Hard"
        return jsonify({
            "word_count": word_count,
            "char_count": char_count,
            "para_count": para_count,
            "read_time": read_time,
            "sentiment": sentiment_label,
            "complexity": complexity
        })
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        return jsonify({"error": str(e)}), 500
