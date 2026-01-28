import os
from flask import Flask, request, jsonify
from pathlib import Path
from logging_utils import setup_logger
import openai

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
            raise ValueError("OpenAI API key not set